"""Relationship CRM and outreach drafting.

Hard boundaries enforced in code:
  * Drafts only. This module cannot send email. `record_sent` merely records a
    send the founder performed (or an approved integration performed) elsewhere.
  * A message can only be approved by a named founder, and only to a contact
    that is a VERIFIED_CONTACT or RESEARCHED_ROUTE (never an UNVERIFIED_LEAD).
  * Personalisation uses only facts with a source URL from VERIFIED records.
  * Follow-ups: day 14 and day 28 after a recorded send, max two, stopped by a
    reply, opt-out or a closed relationship.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone

from commerce.db import audit, now_iso, one, rows

FOLLOW_UP_DAYS = (14, 28)
MAX_FOLLOW_UPS = 2
STOP_STATUSES = {"REPLIED", "IN_DISCUSSION", "SUPPLY_AGREED", "DECLINED", "OPTED_OUT", "PAUSED"}


class OutreachError(ValueError):
    pass


def best_contact(conn, org_id):
    order = "CASE tier WHEN 'VERIFIED_CONTACT' THEN 0 WHEN 'RESEARCHED_ROUTE' THEN 1 ELSE 2 END"
    return one(conn, f"SELECT * FROM contacts WHERE organisation_id=? AND opt_out=0 ORDER BY {order}, id LIMIT 1",
               (org_id,))


def verified_facts(conn, org_id) -> list[dict]:
    """Australian connections with sources, from VERIFIED or PARTIAL stints only."""
    facts = []
    for r in rows(conn, """SELECT p.name, p.id pid, s.seasons, s.champion, s.is_current, s.organisation_name, s.verification
                           FROM player_stints s JOIN players p ON p.id = s.player_id
                           WHERE s.organisation_id=? AND p.is_australian=1 AND s.verification IN ('VERIFIED','PARTIAL')
                           ORDER BY CASE s.verification WHEN 'VERIFIED' THEN 0 ELSE 1 END, s.is_current DESC, s.champion DESC""", (org_id,)):
        src = one(conn, "SELECT url FROM sources WHERE entity_type='player' AND entity_id=? LIMIT 1", (r["pid"],))
        if not src:
            continue          # no source, no claim
        yrs = f" ({r['seasons']})" if r["seasons"] and re.search(r"\d{4}", r["seasons"]) else ""
        champ = ", including a championship" if r["champion"] else ""
        if r["is_current"]:
            text = f"{r['name']}, who plays for {r['organisation_name']} this season"
            phrase = f"{r['name']}, who is on the roster this season"
        else:
            text = f"{r['name']}'s years with {r['organisation_name']}{yrs}{champ}"
            phrase = f"{r['name']}'s years there{yrs}{champ}"
        facts.append({"fact": text, "phrase": phrase,
                      "source_url": src["url"], "verification": r["verification"]})
    return facts


def _connection_sentence(org, facts):
    if not facts:
        return None
    f = facts[0].get("phrase") or facts[0]["fact"]
    return (f"Many Australian fans follow {org['name']} because of {f}. "
            "That connection means a great deal to collectors here, and almost none of the genuine "
            "equipment from those seasons ever reaches Australia.")


def draft_initial(conn, org_id, founder_name="[FOUNDER NAME]", actor="outreach_agent") -> dict:
    org = one(conn, "SELECT * FROM organisations WHERE id=?", (org_id,))
    if not org:
        raise OutreachError("Unknown organisation")
    contact = best_contact(conn, org_id)
    if not contact:
        raise OutreachError(f"No contact route recorded for {org['name']}: research one before drafting")
    rel = one(conn, "SELECT * FROM relationships WHERE organisation_id=?", (org_id,)) or {}
    facts = verified_facts(conn, org_id)
    greeting = f"Hello {contact['person']}," if contact["person"] else "Hello,"
    dept = contact["department"] or "team"
    kind = org["kind"]
    if kind == "NBA_TEAM":
        ask = ("whether the organisation has an approved route for purchasing, consigning or being referred to "
               "an official partner for previous-season or surplus team-issued apparel, particularly warmup "
               "tearaway pants, shooting shirts and warmup jackets")
    elif kind in ("NCAA_PROGRAMME", "UNIVERSITY_SURPLUS"):
        ask = ("whether the athletics department or university surplus office releases previous-season team "
               "apparel, and whether remote or bulk purchasers outside the United States can take part, subject "
               "to university policy and any NCAA or name, image and likeness restrictions")
    else:
        ask = ("whether you offer dealer, bulk or consignment terms for older team-issued stock, what provenance "
               "documentation accompanies it, and whether you ship to Australia")
    opp = rel.get("commercial_opportunity")
    parts = [greeting, "",
             "My name is " + founder_name + " and I'm establishing ON COURT ONLY, a new Australian business that "
             "gives local collectors a legitimate way to own genuine team-issued basketball equipment, the "
             "warmups and on-court gear that ordinary retail rarely reaches.", ""]
    conn_sentence = _connection_sentence(org, facts)
    if conn_sentence:
        parts += [conn_sentence, ""]
    parts += [f"I'm writing to your {dept.lower()} team to ask {ask}.", ""]
    if opp:
        parts += [opp, ""]
    parts += ["To be clear, we are an independent reseller, not affiliated with or endorsed by any league, team or "
              "manufacturer, and we only want stock that has been legitimately released with the right to resell. "
              "We document provenance for every item and would follow any conditions you set.", "",
              "If someone else handles this, I'd be grateful for a pointer to the right colleague or official partner.",
              "", "Thank you for your time,", founder_name, "ON COURT ONLY | Australia", "[VERIFIED REPLY-TO ADDRESS]"]
    subject = (f"Australian collector channel for {org['name']} team-issued equipment" if kind != "SUPPLIER"
               else f"Dealer / bulk enquiry from Australia: {org['name']}")
    body = "\n".join(parts)
    cur = conn.execute(
        "INSERT INTO outreach_messages(organisation_id, contact_id, sequence_step, subject, body, personalisation_facts)"
        " VALUES (?,?,?,?,?,?)", (org_id, contact["id"], 0, subject, body, json.dumps(facts)))
    conn.execute("""INSERT INTO relationships(organisation_id, status, updated_at) VALUES (?, 'DRAFT_READY', ?)
                    ON CONFLICT(organisation_id) DO UPDATE SET status=CASE WHEN status='NOT_CONTACTED'
                    THEN 'DRAFT_READY' ELSE status END, updated_at=excluded.updated_at""", (org_id, now_iso()))
    audit(conn, actor, "OUTREACH_DRAFT", "organisation", org_id, {"message_id": cur.lastrowid})
    conn.commit()
    return one(conn, "SELECT * FROM outreach_messages WHERE id=?", (cur.lastrowid,))


def approve(conn, message_id, founder_name):
    if not founder_name or founder_name.startswith("["):
        raise OutreachError("Approval needs the founder's name")
    m = one(conn, "SELECT * FROM outreach_messages WHERE id=?", (message_id,))
    if not m or m["status"] != "DRAFT":
        raise OutreachError("Only drafts can be approved")
    c = one(conn, "SELECT * FROM contacts WHERE id=?", (m["contact_id"],))
    if not c or c["tier"] == "UNVERIFIED_LEAD":
        raise OutreachError("Cannot approve a message to an unverified lead")
    if c["opt_out"]:
        raise OutreachError("Contact has opted out")
    if "[" in m["body"].replace("[VERIFIED REPLY-TO ADDRESS]", ""):
        raise OutreachError("Draft still contains unfilled placeholders")
    conn.execute("UPDATE outreach_messages SET status='APPROVED', approved_by=?, approved_at=? WHERE id=?",
                 (founder_name, now_iso(), message_id))
    audit(conn, founder_name, "OUTREACH_APPROVE", "outreach_message", str(message_id))
    conn.commit()


def record_sent(conn, message_id, sent_via, actor, sent_at=None):
    """Record a send that genuinely happened outside this system."""
    m = one(conn, "SELECT * FROM outreach_messages WHERE id=?", (message_id,))
    if not m or m["status"] != "APPROVED":
        raise OutreachError("Only founder-approved messages can be recorded as sent")
    when = sent_at or now_iso()
    conn.execute("UPDATE outreach_messages SET status='SENT', sent_at=?, sent_via=? WHERE id=?", (when, sent_via, message_id))
    due = (datetime.fromisoformat(when.replace("Z", "+00:00")) + timedelta(days=FOLLOW_UP_DAYS[0])).date().isoformat()
    conn.execute("UPDATE relationships SET status='CONTACTED', follow_up_date=?, updated_at=? WHERE organisation_id=?",
                 (due, now_iso(), m["organisation_id"]))
    audit(conn, actor, "OUTREACH_SENT_RECORDED", "outreach_message", str(message_id), sent_via)
    conn.commit()


def record_reply(conn, org_id, summary, opt_out=False, actor="founder"):
    status = "OPTED_OUT" if opt_out else "REPLIED"
    conn.execute("UPDATE relationships SET status=?, follow_up_date=NULL, updated_at=? WHERE organisation_id=?",
                 (status, now_iso(), org_id))
    conn.execute("UPDATE outreach_messages SET reply_summary=? WHERE organisation_id=? AND status='SENT'",
                 (summary, org_id))
    if opt_out:
        conn.execute("UPDATE contacts SET opt_out=1 WHERE organisation_id=?", (org_id,))
        conn.execute("UPDATE outreach_messages SET status='CANCELLED' WHERE organisation_id=? AND status IN ('DRAFT','APPROVED')",
                     (org_id,))
    audit(conn, actor, "OUTREACH_REPLY", "organisation", org_id, summary)
    conn.commit()


def follow_ups_due(conn, today=None) -> list[dict]:
    """Follow-up drafts that are due, honouring stops and the two-follow-up cap."""
    today = today or datetime.now(timezone.utc).date().isoformat()
    due = []
    for org in rows(conn, "SELECT * FROM relationships WHERE status='CONTACTED' AND follow_up_date <= ?", (today,)):
        sent = rows(conn, "SELECT * FROM outreach_messages WHERE organisation_id=? AND status='SENT' ORDER BY sequence_step",
                    (org["organisation_id"],))
        if not sent or org["status"] in STOP_STATUSES:
            continue
        step = max(m["sequence_step"] for m in sent) + 1
        if step > MAX_FOLLOW_UPS:
            continue
        pending = one(conn, "SELECT id FROM outreach_messages WHERE organisation_id=? AND sequence_step=? AND status IN ('DRAFT','APPROVED')",
                      (org["organisation_id"], step))
        due.append({"organisation_id": org["organisation_id"], "step": step, "draft_exists": bool(pending)})
    return due


def draft_follow_up(conn, org_id, step, founder_name="[FOUNDER NAME]"):
    if step < 1 or step > MAX_FOLLOW_UPS:
        raise OutreachError("Follow-up step must be 1 or 2")
    first = one(conn, "SELECT * FROM outreach_messages WHERE organisation_id=? AND sequence_step=0 AND status='SENT'", (org_id,))
    if not first:
        raise OutreachError("No recorded initial send; follow-ups only follow real sends")
    rel = one(conn, "SELECT status FROM relationships WHERE organisation_id=?", (org_id,))
    if rel and rel["status"] in STOP_STATUSES:
        raise OutreachError(f"Sequence stopped: relationship is {rel['status']}")
    org = one(conn, "SELECT name FROM organisations WHERE id=?", (org_id,))
    if step == 1:
        body = (f"Hello,\n\nJust following up on my note about an approved route for previous-season {org['name']} "
                "team-issued apparel. If another department or an official memorabilia partner handles this, "
                f"a pointer would be much appreciated.\n\nThanks,\n{founder_name}\nON COURT ONLY | Australia")
    else:
        body = (f"Hello,\n\nOne last check on whether {org['name']} has a contact for surplus or historic team-issued "
                "apparel. I won't follow up again after this, and if you'd prefer no further contact just reply "
                f"and I'll note it.\n\nThanks,\n{founder_name}\nON COURT ONLY | Australia")
    cur = conn.execute("INSERT INTO outreach_messages(organisation_id, contact_id, sequence_step, subject, body) VALUES (?,?,?,?,?)",
                       (org_id, first["contact_id"], step, "Re: " + first["subject"], body))
    conn.commit()
    return cur.lastrowid


def pipeline(conn) -> list[dict]:
    return rows(conn, """
      SELECT o.id, o.name, o.kind, o.conference, o.division, r.status, r.priority, r.follow_up_date, r.next_action,
             r.australian_connection, r.commercial_opportunity, r.approved_purchasing_process,
             (SELECT tier FROM contacts c WHERE c.organisation_id=o.id ORDER BY CASE tier WHEN 'VERIFIED_CONTACT' THEN 0
                     WHEN 'RESEARCHED_ROUTE' THEN 1 ELSE 2 END LIMIT 1) AS best_tier,
             (SELECT value FROM contacts c WHERE c.organisation_id=o.id ORDER BY CASE tier WHEN 'VERIFIED_CONTACT' THEN 0
                     WHEN 'RESEARCHED_ROUTE' THEN 1 ELSE 2 END LIMIT 1) AS best_contact,
             (SELECT COUNT(*) FROM outreach_messages m WHERE m.organisation_id=o.id) AS messages,
             (SELECT COUNT(*) FROM outreach_messages m WHERE m.organisation_id=o.id AND m.status='SENT') AS sent
      FROM organisations o LEFT JOIN relationships r ON r.organisation_id=o.id
      WHERE o.kind IN ('NBA_TEAM','NCAA_PROGRAMME','SUPPLIER','AUTHENTICATOR','AUCTION_HOUSE','UNIVERSITY_SURPLUS')
      ORDER BY COALESCE(r.priority, 999), o.name""")

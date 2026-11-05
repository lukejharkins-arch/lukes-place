"""Export registers to CSV for review outside the app.

    python3 -m commerce.export
"""
import csv

from commerce import config as C
from commerce.db import connect, rows


def _w(path, header, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(data)
    return path


def export(conn=None):
    conn = conn or connect()
    out = []
    players = rows(conn, """SELECT p.id, p.name, p.status, p.college, p.achievements, p.verification,
        (SELECT group_concat(organisation_name || COALESCE(' ' || seasons,'') || CASE WHEN is_current THEN ' (current)' ELSE '' END
                             || CASE WHEN champion THEN ' (champion)' ELSE '' END, '; ') FROM player_stints WHERE player_id=p.id) stints,
        (SELECT group_concat(url, ' ') FROM sources WHERE entity_type='player' AND entity_id=p.id) sources
        FROM players p WHERE is_australian=1 ORDER BY p.status, p.name""")
    out.append(_w(C.ROOT / "research" / "australian_player_register.csv",
                  ["id", "name", "status", "teams_and_schools", "college", "achievements", "verification", "source_urls"],
                  [[p["id"], p["name"], p["status"], p["stints"], p["college"], p["achievements"], p["verification"], p["sources"]] for p in players]))
    crm = rows(conn, """SELECT o.id, o.kind, o.name, o.conference, c.department, c.person, c.method, c.value, c.role, c.tier, c.evidence_url,
        c.verified_at, r.australian_connection, r.commercial_opportunity, r.approved_purchasing_process, r.follow_up_date, r.status, r.next_action,
        (SELECT COUNT(*) FROM outreach_messages m WHERE m.organisation_id=o.id AND m.status='SENT') sent,
        (SELECT reply_summary FROM outreach_messages m WHERE m.organisation_id=o.id AND reply_summary IS NOT NULL LIMIT 1) reply
        FROM organisations o LEFT JOIN relationships r ON r.organisation_id=o.id LEFT JOIN contacts c ON c.organisation_id=o.id
        WHERE o.kind != 'OTHER' ORDER BY COALESCE(r.priority, 999), o.kind, o.name""")
    out.append(_w(C.ROOT / "outreach" / "crm_register.csv",
                  ["organisation_id", "type", "organisation", "conference", "department", "contact_name", "method", "verified_email_or_contact_method",
                   "role", "contact_tier", "evidence_source", "verified_at", "australian_player_connection", "previous_contact_count", "response",
                   "commercial_opportunity", "approved_purchasing_process", "follow_up_date", "relationship_status", "next_action"],
                  [[r["id"], r["kind"], r["name"], r["conference"], r["department"], r["person"], r["method"], r["value"], r["role"], r["tier"],
                    r["evidence_url"], r["verified_at"], r["australian_connection"], r["sent"], r["reply"], r["commercial_opportunity"],
                    r["approved_purchasing_process"], r["follow_up_date"], r["status"], r["next_action"]] for r in crm]))
    from sourcing.demand import rank
    out.append(_w(C.ROOT / "research" / "sourcing_priority_ranking.csv", ["rank", "organisation_id", "name", "league", "score", "measured_share_pct", "label"],
                  [[r["rank"], r["organisation_id"], r["name"], r["league"], r["score"], r["measured_share_pct"], r["label"]] for r in rank(conn)]))
    return out




def research_summary(conn=None):
    """Write research/RESEARCH_SUMMARY.md from the database (reproducible)."""
    conn = conn or connect()
    from sourcing.demand import rank
    r = rank(conn)
    nba = [x for x in r if x["league"] == "NBA"][:15]
    ncaa = [x for x in r if x["league"] == "NCAA"][:15]
    chans = rows(conn, "SELECT * FROM channels ORDER BY COALESCE(fit_score,0) DESC, verification, name")
    top = rows(conn, """SELECT o.id, o.name, r.priority, r.commercial_opportunity,
                        (SELECT group_concat(c.method || ': ' || c.value || ' [' || c.tier || ']', '<br>') FROM contacts c WHERE c.organisation_id=o.id) contacts
                        FROM organisations o JOIN relationships r ON r.organisation_id=o.id WHERE o.id LIKE 'SUP-%' ORDER BY r.priority""")
    cur = rows(conn, """SELECT p.name, s.organisation_name, p.verification FROM players p JOIN player_stints s ON s.player_id=p.id
                        WHERE s.is_current=1 ORDER BY p.name""")
    champs = rows(conn, """SELECT DISTINCT p.name, s.organisation_name, s.seasons FROM players p JOIN player_stints s ON s.player_id=p.id
                           WHERE s.champion=1 ORDER BY p.name""")
    tiers = {t["tier"]: t["n"] for t in rows(conn, "SELECT tier, COUNT(*) n FROM contacts GROUP BY tier")}
    L = ["# Research summary | sourcing intelligence (generated from data/oco.db)", "",
         "Method: six research agents on 2026-11-05 using web search. **Direct page loads were blocked by this environment's network "
         "policy for almost every site, and the shared search budget ran out**, so facts come from search-engine extracts of the cited "
         "pages. That is why nothing is marked VERIFIED_CONTACT: a person must confirm each route on the live page.", "",
         f"Contacts: {tiers.get('VERIFIED_CONTACT', 0)} verified · {tiers.get('RESEARCHED_ROUTE', 0)} researched official routes · "
         f"{tiers.get('UNVERIFIED_LEAD', 0)} unverified leads (published emails/phones seen in search extracts).", "",
         "## Ranked NBA sourcing priority (demand model; mostly ESTIMATE, see measured share)", "",
         "| Rank | Team | Score | Measured share |", "|---|---|---|---|"]
    L += [f"| {i} | {x['name']} | {x['score']} | {x['measured_share_pct']}% |" for i, x in enumerate(nba, 1)]
    L += ["", "## Ranked NCAA sourcing priority", "", "| Rank | Programme | Score | Measured share |", "|---|---|---|---|"]
    L += [f"| {i} | {x['name']} | {x['score']} | {x['measured_share_pct']}% |" for i, x in enumerate(ncaa, 1)]
    L += ["", "Ranking caveat: a lower-profile programme with a real surplus route (Purdue, Michigan State, Oregon, Auburn) can outrank a famous one "
          "once access is weighted; access is scored per opportunity by the deal engine, not here.", "",
          "## Australian connections (current 2026-27 NBA)", ""]
    L += [f"- {c['name']}: {c['organisation_name']} ({c['verification']})" for c in cur]
    L += ["", "Australian NBA champions in the register: " + "; ".join(f"{c['name']} ({c['organisation_name']} {c['seasons'] or ''})".replace(" )", ")") for c in champs), "",
          "Metropolitan State University of Denver: NCAA **Division II** (RMAC), not Division I; no verified Australian men's basketball connection.", "",
          f"## Supply channels ({len(chans)})", "", "| Channel | Type | Typical class | Ships to AU | Fit | Verification |", "|---|---|---|---|---|---|"]
    L += [f"| {c['name']} | {c['channel_type']} | {(c['classification_typical'] or '')[:40]} | {(c['ships_to_au'] or 'unknown')[:50]} | {c['fit_score'] or ''} | {c['verification']} |" for c in chans]
    L += ["", "## First 10 sourcing targets and researched contacts", "", "| # | Target | Contacts (tier) | What to ask |", "|---|---|---|---|"]
    L += [f"| {t['priority']} | {t['name']} | {t['contacts'] or 'none found'} | {(t['commercial_opportunity'] or '')[:200]} |" for t in top]
    (C.ROOT / "research" / "RESEARCH_SUMMARY.md").write_text("\n".join(L) + "\n")
    return C.ROOT / "research" / "RESEARCH_SUMMARY.md"


if __name__ == "__main__":
    for p in export():
        print(p)
    print(research_summary())

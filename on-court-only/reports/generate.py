"""Report generator.

    python3 -m reports.generate daily|weekly|fortnightly|monthly [--date YYYY-MM-DD]

Each report is built from the shared database (run the agents first) and
written to reports/<cadence>/<date>.md. Reports state counts as they are,
including zero, and separate measured facts from estimates.
"""
from __future__ import annotations

import argparse
import json
from datetime import date

from commerce import config as C
from commerce.db import connect, jload, one, rows
from operations import budget, launch
from outreach import crm
from sourcing import demand, engine

OUT = C.ROOT / "reports"


def _aud(c):
    return "–" if c is None else f"A${c / 100:,.2f}"


def daily(conn, day):
    res = [dict(r) for r in conn.execute("SELECT * FROM opportunities WHERE is_demo=0 ORDER BY deal_score DESC")]
    s = engine.daily_summary(res)
    L = [f"# Daily sourcing report | {day}", "",
         f"**Qualified purchase opportunities: {s['qualified']} of a {s['target']} target.** "
         f"Shortfall {s['shortfall']} (reported, not filled).", "",
         f"Real leads evaluated: {s['evaluated']} · investigate {s['investigate']} · needs evidence {s['needs_evidence']} · "
         f"watch {s['watch']} · rejected {s['rejected']}", "",
         "Every lead below was seen only through search-engine summaries this session: marketplace pages could not be loaded "
         "from this environment, so none is live-verified and none can qualify until a person opens the listing.", "",
         "| Lead | Item | Team | Listed | Landed (est.) | Class supported | Risk | Score | Recommendation | Main reasons |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in res:
        reasons = jload(r["rejection_reasons"])
        L.append(f"| [{r['id']}]({r['listing_url']}) | {r['title'][:60]} | {r['team_or_school'] or ''} | {r['currency']} "
                 f"{r['listed_price_cents'] / 100:.2f} | {_aud(r['landed_cost_aud_cents'])} | {r['supported_classification']} | "
                 f"{r['risk_grade']} | {r['deal_score']} | {r['recommendation']} | {'; '.join(reasons[:2])} |")
    L += ["", "## Risks", "",
          "- No authentication evidence is visible in any current lead: every one rests on seller wording.",
          "- Sold comparables are search snippets with no confirmed sale, so no resale value can be stated.",
          "- Retail lines branded 'Team Issue' exist (see research/raw/supply_channels.json red flags); titles alone prove nothing.",
          "- Several leads are G League, not NBA; classify by the actual team named on the item.", "",
          "## Next actions", "",
          "1. Open each NEEDS_EVIDENCE listing and request tag, label and size-tag photos plus how the seller acquired it.",
          "2. Record any confirmed sold comparables (URL, price, date) so resale estimates exist.",
          f"3. Work the search plan in sourcing/search_plan_{day}.md.", ""]
    return "\n".join(L)


def weekly(conn, day):
    chans = rows(conn, "SELECT verification, COUNT(*) n FROM channels GROUP BY verification")
    tiers = rows(conn, "SELECT tier, COUNT(*) n FROM contacts GROUP BY tier")
    sup = rows(conn, """SELECT o.name, r.priority, r.status, r.commercial_opportunity FROM organisations o JOIN relationships r ON r.organisation_id=o.id
                        WHERE o.kind NOT IN ('NBA_TEAM','NCAA_PROGRAMME') ORDER BY r.priority""")
    runs = rows(conn, "SELECT agent, ok, summary, started_at FROM agent_runs WHERE id IN (SELECT MAX(id) FROM agent_runs GROUP BY agent) ORDER BY agent")
    L = [f"# Weekly report | week ending {day}", "", "## Supplier relationships", "",
         "Channels by verification: " + ", ".join(f"{c['verification']} {c['n']}" for c in chans),
         "Contacts by tier: " + ", ".join(f"{t['tier']} {t['n']}" for t in tiers), "",
         "| Priority | Supplier | Status | Question to ask |", "|---|---|---|---|"]
    L += [f"| {s['priority'] or ''} | {s['name']} | {s['status']} | {(s['commercial_opportunity'] or '')[:140]} |" for s in sup]
    L += ["", "## Acquisition intelligence", "",
          "- Locker Room Direct (non-profit selling donated team-issued pro and college gear) is the strongest bulk lead found.",
          "- NBA Auctions sells game-issued warmups with NBA & MeiGray registration numbers; shipping to Australia unconfirmed.",
          "- University surplus sales (Duke, Oregon, Auburn, Purdue, Michigan State) are in person; a US buying agent would be needed.",
          "- Budget: " + json.dumps({k: v for k, v in budget.summary(conn).items() if k in ("committed_aud", "proposed_aud", "remaining_aud")}), "",
          "## Technical progress (latest agent runs)", "", "| Agent | OK | Summary | At |", "|---|---|---|---|"]
    L += [f"| {r['agent']} | {'yes' if r['ok'] else 'NO'} | {r['summary']} | {r['started_at']} |" for r in runs]
    return "\n".join(L) + "\n"


def fortnightly(conn, day):
    due = crm.follow_ups_due(conn, day)
    msgs = rows(conn, """SELECT o.name, m.sequence_step, m.status, m.sent_at, m.approved_by FROM outreach_messages m
                         JOIN organisations o ON o.id=m.organisation_id ORDER BY o.name, m.sequence_step""")
    sent = sum(1 for m in msgs if m["status"] == "SENT")
    L = [f"# Fortnightly outreach report | {day}", "",
         f"Messages: {len(msgs)} total · {sent} recorded as sent · approved {sum(m['status'] == 'APPROVED' for m in msgs)} · "
         f"drafts {sum(m['status'] == 'DRAFT' for m in msgs)}.", "",
         "Follow-ups are only scheduled after a real send is recorded (day 14, then day 28, max two), and stop on any reply or opt-out.", "",
         f"**Follow-ups due now: {len(due)}**", ""]
    L += [f"- {d['organisation_id']} step {d['step']} (draft exists: {d['draft_exists']})" for d in due] or ["- None: no outreach has been sent."]
    L += ["", "| Organisation | Step | Status | Approved by | Sent |", "|---|---|---|---|---|"]
    L += [f"| {m['name']} | {m['sequence_step']} | {m['status']} | {m['approved_by'] or ''} | {m['sent_at'] or ''} |" for m in msgs]
    return "\n".join(L) + "\n"


def monthly(conn, day):
    ranked = demand.rank(conn)
    tr = launch.tracker(conn)
    econ_file = sorted((OUT).glob("unit_economics_*.json"))
    econ = json.loads(econ_file[-1].read_text()) if econ_file else {"scenarios": []}
    wait = one(conn, "SELECT COUNT(*) n FROM waitlist WHERE unsubscribed=0")["n"]
    wanted = one(conn, "SELECT COUNT(*) n FROM wanted_posts")["n"]
    wl = one(conn, "SELECT COUNT(*) n FROM wishlist")["n"]
    L = [f"# Monthly report | {day}", "", "## Market demand (ranked)", "",
         "Scores mix MEASURED factors (cited source) and ESTIMATES. The measured share column shows how much is evidence.", "",
         "| Rank | Organisation | Score | Measured share | Label |", "|---|---|---|---|---|"]
    L += [f"| {r['rank']} | {r['name']} | {r['score']} | {r['measured_share_pct']}% | {r['label']} |" for r in ranked[:25]]
    L += ["", "## Margin analysis (scenario estimates, not live deals)", "", f"FX: {econ.get('assumptions_fx', '')}", "",
          "| Scenario | Landed A$ | Sale A$ | Net A$ | Gross profit A$ | Margin |", "|---|---|---|---|---|---|"]
    L += [f"| {s['scenario']} | {s['landed_aud']} | {s['sale_price_aud']} | {s['net_proceeds_aud']} | {s['gross_profit_aud']} | {s['gross_margin_pct']}% |"
          for s in econ["scenarios"]]
    L += ["", "## Collector engagement", "", f"Waitlist {wait} · wanted posts {wanted} · wishlist saves {wl} (pre-launch, local database).", "",
          "## Launch readiness", "", f"Ready: {tr['ready_total']}/30 ({tr['ready']}) against target {tr['target']}. Launch gate passed: {tr['launch_ready']}.",
          "", tr["note"], ""]
    return "\n".join(L)


BUILDERS = {"daily": daily, "weekly": weekly, "fortnightly": fortnightly, "monthly": monthly}


def write(cadence, day, conn=None):
    conn = conn or connect()
    text = BUILDERS[cadence](conn, day)
    path = OUT / cadence / f"{day}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cadence", choices=list(BUILDERS) + ["all"])
    ap.add_argument("--date", default=date.today().isoformat())
    a = ap.parse_args()
    for c in (BUILDERS if a.cadence == "all" else [a.cadence]):
        print(write(c, a.date))

"""Agent team runner. Every agent is a bounded, testable workflow over the shared DB.

    python3 -m agents.run <agent|all> [--date YYYY-MM-DD]

Each run is logged to agent_runs with measurable metrics. No agent can send a
message, spend money, publish a listing or contact a third party: those
actions do not exist in this codebase. Agents draft, score, flag and report.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import traceback
from datetime import date

from authentication.rules import classify, lint_copy, claim_allowed
from commerce import config as C
from commerce.db import connect, jload, now_iso, one, rows
from operations import budget, launch
from outreach import crm
from sourcing import demand, engine, search_framework

ROOT = C.ROOT
AGENTS = {}

FIRST_OUTREACH_TARGETS = ["NCAA-SMC", "NBA-GSW", "SUP-LOCKER-ROOM-DIRECT", "SUP-MEIGRAY-GROUP", "NCAA-PUR"]


def agent(name):
    def deco(fn):
        AGENTS[name] = fn
        return fn
    return deco


def _csv(path, header, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(data)


def _md(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


# ------------------------------------------------------------- 2 NBA Scout
@agent("nba_scout")
def nba_scout(conn, day):
    teams = rows(conn, "SELECT * FROM organisations WHERE kind='NBA_TEAM' ORDER BY name")
    out, gaps = [], []
    for t in teams:
        cs = rows(conn, "SELECT tier, method, value, evidence_url FROM contacts WHERE organisation_id=?", (t["id"],))
        rel = one(conn, "SELECT * FROM relationships WHERE organisation_id=?", (t["id"],)) or {}
        best = next((c for tier in ("VERIFIED_CONTACT", "RESEARCHED_ROUTE", "UNVERIFIED_LEAD") for c in cs if c["tier"] == tier), None)
        aus_now = rows(conn, """SELECT p.name FROM player_stints s JOIN players p ON p.id=s.player_id
                                WHERE s.organisation_id=? AND s.is_current=1""", (t["id"],))
        nsrc = one(conn, "SELECT COUNT(*) n FROM sources WHERE entity_type='organisation' AND entity_id=?", (t["id"],))["n"]
        out.append([t["id"], t["name"], t["conference"], t["division"], t["website"], best["tier"] if best else "NONE",
                    best["value"] if best else "", "; ".join(p["name"] for p in aus_now), rel.get("australian_connection") or "",
                    (rel.get("approved_purchasing_process") or "")[:200], (t["recent_success"] or "")[:200], nsrc, t["verification"]])
        if not best:
            gaps.append(t["name"])
    _csv(ROOT / "research" / "nba_team_register.csv",
         ["id", "team", "conference", "division", "official_site", "best_contact_tier", "best_contact", "current_australians",
          "australian_connection", "official_auction_route", "recent_results", "source_count", "verification"], out)
    return {"teams": len(teams), "with_contact_route": len(teams) - len(gaps), "verified_contacts":
            one(conn, "SELECT COUNT(*) n FROM contacts c JOIN organisations o ON o.id=c.organisation_id WHERE o.kind='NBA_TEAM' AND tier='VERIFIED_CONTACT'")["n"],
            "missing_route": gaps}, f"{len(teams)} franchises; {len(gaps)} still need a contact route"


# ------------------------------------------------------------- 3 NCAA Scout
@agent("ncaa_scout")
def ncaa_scout(conn, day):
    progs = rows(conn, "SELECT * FROM organisations WHERE kind='NCAA_PROGRAMME' ORDER BY name")
    out = []
    surplus = 0
    for p in progs:
        rel = one(conn, "SELECT * FROM relationships WHERE organisation_id=?", (p["id"],)) or {}
        route = one(conn, "SELECT value, tier FROM contacts WHERE organisation_id=? ORDER BY id LIMIT 1", (p["id"],))
        surplus += bool(route)
        out.append([p["id"], p["name"], p["nickname"], p["division"], p["conference"], p["website"] or "",
                    route["value"] if route else "", route["tier"] if route else "NONE",
                    (rel.get("approved_purchasing_process") or "")[:250], rel.get("australian_connection") or "",
                    (p["recent_success"] or "")[:150], p["verification"]])
    _csv(ROOT / "research" / "ncaa_programme_register.csv",
         ["id", "institution", "nickname", "division", "conference_2026_27", "athletics_site", "surplus_route", "route_tier",
          "purchasing_process_notes", "australian_connection", "tournament_2026", "verification"], out)
    non_d1 = [p["name"] for p in progs if p["division"] and "II" in p["division"] and "III" not in p["division"]]
    return {"programmes": len(progs), "with_surplus_route": surplus, "non_division_I": non_d1}, \
        f"{len(progs)} programmes; {surplus} with a researched surplus/property route"


# ------------------------------------------------- 4 Undervalued Gear Hunter
@agent("gear_hunter")
def gear_hunter(conn, day):
    inbox = ROOT / "sourcing" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    ingested = 0
    for f in sorted(inbox.glob("*.json")):
        for c in json.loads(f.read_text()):
            if not (c.get("listing_url") and c.get("title") and c.get("listed_price") and c.get("currency")):
                continue          # never ingest a lead without a real URL and a seen price
            oid = c.get("id") or f"HUNT-{day}-{ingested + 1:02d}"
            conn.execute("""INSERT OR IGNORE INTO opportunities(id, found_at, title, team_or_school, item_type, platform, listing_url,
                            listed_price_cents, currency, shipping_cents, claimed_classification, evidence, red_flags, comps, live_verified)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                         (oid, day, c["title"], c.get("team_or_school"), c.get("item_type") or "OTHER", c.get("platform"), c["listing_url"],
                          int(float(c["listed_price"]) * 100), c["currency"].upper(),
                          int(float(c["shipping"]) * 100) if c.get("shipping") is not None else None, c.get("claimed_classification"),
                          json.dumps(c.get("evidence", [])), json.dumps(c.get("red_flags", [])), json.dumps(c.get("comps", [])),
                          int(bool(c.get("live_verified")))))
            ingested += 1
        f.rename(f.with_suffix(".processed"))
    conn.commit()
    top = demand.rank(conn)[:8]
    plan = search_framework.plan([{"name": t["name"], "era": "OG" if i % 2 == 0 else "CURRENT"} for i, t in enumerate(top)], per_team=6)
    signals = []
    for o in rows(conn, "SELECT id, title, listed_price_cents, currency FROM opportunities WHERE is_demo=0"):
        from sourcing.economics import to_aud
        s = search_framework.misclassification_signal(o["title"], to_aud(o["listed_price_cents"] / 100, o["currency"]))
        signals.append((o["id"], o["title"], s["score"], s["seller_uses_collector_terms"]))
    lines = [f"# Daily search plan | {day}", "",
             "Public search links for a person to review. No scraping, no logins, no messages. Record any real find in "
             "`sourcing/inbox/<date>.json` (url, title, listed_price, currency required).", "",
             f"Priority teams (demand model): {', '.join(t['name'] for t in top)}", ""]
    for p in plan:
        lines.append(f"- **{p['team']}**: `{p['query']}` | " + " · ".join(f"[{k}]({u})" for k, u in p["links"].items()))
    lines += ["", "## Misclassification signals on current leads", "", "| Lead | Title | Signal | Seller already uses collector terms |", "|---|---|---|---|"]
    lines += [f"| {i} | {t[:70]} | {s} | {k} |" for i, t, s, k in sorted(signals, key=lambda x: -x[2])]
    _md(ROOT / "sourcing" / f"search_plan_{day}.md", "\n".join(lines) + "\n")
    return {"queries": len(plan), "ingested": ingested, "leads_scored": len(signals)}, \
        f"{len(plan)} search queries planned; {ingested} new leads ingested"


# --------------------------------------------- 5 Authentication Specialist
@agent("auth_specialist")
def auth_specialist(conn, day):
    findings = []
    for p in rows(conn, "SELECT * FROM products"):
        ev = [r["code"] for r in rows(conn, "SELECT code FROM evidence WHERE product_id=?", (p["id"],))]
        a = classify(ev, p["item_type"], p["season"], player_named=bool(p["player_id"]))
        copy = " ".join(filter(None, [p["title"], p["description"], p["player_connection"], p["story_design"], p["story_vs_retail"]]))
        lint = lint_copy(copy, a.supported)
        ok = claim_allowed(p["claimed_classification"], a.supported) and not lint
        conn.execute("UPDATE products SET supported_classification=?, updated_at=? WHERE id=?", (a.supported, now_iso(), p["id"]))
        conn.execute("INSERT INTO auth_reviews(product_id, reviewed_at, reviewer, supported_classification, claim_ok, findings) VALUES (?,?,?,?,?,?)",
                     (p["id"], now_iso(), "auth_specialist", a.supported, int(ok), json.dumps({"assessment": a.as_dict(), "copy": lint})))
        findings.append((p, a, ok, lint))
    conn.commit()
    bad = [f for f in findings if not f[2]]
    lines = [f"# Authentication review | {day}", "", f"{len(findings)} product records reviewed; {len(bad)} with claim or copy problems.", "",
             "| SKU | Claimed | Supported | Confidence | OK | Issues |", "|---|---|---|---|---|---|"]
    for p, a, ok, lint in findings:
        lines.append(f"| {p['id']} | {p['claimed_classification']} | {a.supported} | {a.confidence} | {'yes' if ok else 'NO'} | "
                     f"{'; '.join(i['phrase'] + ': ' + i['problem'] for i in lint) or ('claim exceeds evidence' if not ok else '')} |")
    _md(ROOT / "authentication" / f"review_{day}.md", "\n".join(lines) + "\n")
    return {"reviewed": len(findings), "problems": len(bad), "blocked_skus": [f[0]["id"] for f in bad]}, \
        f"{len(findings)} reviewed, {len(bad)} blocked"


# ------------------------------------------- 6 Wholesale Partnership Agent
@agent("wholesale_agent")
def wholesale_agent(conn, day):
    chans = rows(conn, "SELECT * FROM channels ORDER BY COALESCE(fit_score,0) DESC, verification, name")
    _csv(ROOT / "sourcing" / "channel_directory.csv",
         ["id", "name", "type", "sells", "typical_class", "ships_to_au", "partner_or_terms", "published_contact", "contact_url", "fit", "fit_reason", "verification"],
         [[c["id"], c["name"], c["channel_type"], c["sells"], c["classification_typical"], c["ships_to_au"], c["partner_programme"],
           c["published_contact"], c["contact_url"], c["fit_score"], c["fit_reason"], c["verification"]] for c in chans])
    targets = rows(conn, """SELECT o.id, o.name, r.priority, r.commercial_opportunity FROM organisations o JOIN relationships r ON r.organisation_id=o.id
                            WHERE o.kind NOT IN ('NBA_TEAM','NCAA_PROGRAMME') ORDER BY r.priority""")
    return {"channels": len(chans), "verified_channels": sum(c["verification"] == "VERIFIED" for c in chans),
            "supplier_targets": len(targets), "ships_to_au_confirmed": sum(bool(c["ships_to_au"]) and "yes" in (c["ships_to_au"] or "").lower() for c in chans)}, \
        f"{len(chans)} channels in directory; {len(targets)} supplier targets in CRM"


# ----------------------------------------------------------- 7 Outreach
@agent("outreach_agent")
def outreach_agent(conn, day):
    made = []
    for oid in FIRST_OUTREACH_TARGETS:
        if not one(conn, "SELECT id FROM organisations WHERE id=?", (oid,)):
            continue
        if one(conn, "SELECT id FROM outreach_messages WHERE organisation_id=? AND sequence_step=0", (oid,)):
            continue
        try:
            made.append(crm.draft_initial(conn, oid, actor="outreach_agent"))
        except crm.OutreachError as e:
            made.append({"organisation_id": oid, "error": str(e)})
    for i, oid in enumerate(FIRST_OUTREACH_TARGETS, 1):
        m = one(conn, "SELECT * FROM outreach_messages WHERE organisation_id=? AND sequence_step=0", (oid,))
        if not m:
            continue
        org = one(conn, "SELECT name FROM organisations WHERE id=?", (oid,))
        c = one(conn, "SELECT * FROM contacts WHERE id=?", (m["contact_id"],))
        facts = jload(m["personalisation_facts"])
        _md(ROOT / "outreach" / "drafts" / f"{i:02d}_{oid}.md",
            f"# DRAFT {i}: {org['name']}\n\nStatus: **{m['status']}** (not sent; founder approval required)\n\n"
            f"Route: {c['method']} · {c['value']} · tier **{c['tier']}**  \nEvidence: {c['evidence_url']}\n\n"
            "Before sending: confirm the route on the live page, replace placeholders, and check each fact below.\n\n"
            + "".join(f"- Fact used: {f['fact']} ({f['verification']}) source: {f['source_url']}\n" for f in facts[:1])
            + f"\n**Subject:** {m['subject']}\n\n```\n{m['body']}\n```\n")
    due = crm.follow_ups_due(conn, day)
    return {"drafts_created": sum(1 for m in made if "error" not in m), "errors": [m for m in made if "error" in m],
            "drafts_total": one(conn, "SELECT COUNT(*) n FROM outreach_messages")["n"], "follow_ups_due": len(due), "sent": 0}, \
        f"{sum(1 for m in made if 'error' not in m)} new drafts; {len(due)} follow-ups due; 0 sent (no send capability)"


# -------------------------------------------------- 8 Commercial Analyst
@agent("commercial_analyst")
def commercial_analyst(conn, day):
    res = engine.evaluate_all(conn)
    summ = engine.daily_summary(res)
    b = budget.summary(conn)
    from sourcing.economics import landed_cost, resale
    scen = []
    for label, price, ship, sale in [("Cheap US pair, eBay-style", 45, 30, 180), ("Mid US pair", 90, 35, 300),
                                     ("Premium US pair", 180, 40, 520), ("Local AU find", 60, 0, 220)]:
        lc = landed_cost(price, "USD" if "AU" not in label else "AUD", ship)
        scen.append({"scenario": label, "landed_aud": lc["total_aud"], **resale(sale, lc["total_aud"])})
    _md(ROOT / "reports" / f"unit_economics_{day}.json", json.dumps({"assumptions_fx": C.FX_AS_OF, "scenarios": scen}, indent=2))
    return {**summ, "budget_committed_aud": b["committed_aud"], "budget_remaining_aud": b["remaining_aud"],
            "scenario_margins": {s["scenario"]: s["gross_margin_pct"] for s in scen}}, \
        f"{summ['qualified']} qualified of {summ['evaluated']} real leads (target {summ['target']})"


# --------------------------------------------------- 9 Ecommerce Developer
@agent("ecommerce_dev")
def ecommerce_dev(conn, day):
    from server import App, ApiError
    app = App(C.DB_PATH)
    checks = {}

    def t(name, fn):
        try:
            checks[name] = bool(fn())
        except Exception as e:  # noqa
            checks[name] = False

    t("health", lambda: app.dispatch("GET", "/api/health", {}, {}, None)["ok"])
    t("catalogue_lists_products", lambda: len(app.dispatch("GET", "/api/products", {}, {}, None)) > 0)
    t("no_demo_is_purchasable", lambda: not any(p["purchasable"] for p in app.dispatch("GET", "/api/products", {}, {}, None)))
    t("all_30_nba_teams", lambda: len(app.dispatch("GET", "/api/teams", {"league": ["NBA"]}, {}, None)) == 30)

    def checkout_blocked():
        try:
            app.dispatch("POST", "/api/checkout", {}, {"product_ids": ["OCO-DEMO-01"]}, None)
        except ApiError as e:
            return e.status == 409
        return False
    t("checkout_refuses_demo", checkout_blocked)

    def admin_guard():
        try:
            app.dispatch("GET", "/api/admin/overview", {}, {}, None)
        except ApiError as e:
            return e.status == 401
        return False
    t("admin_requires_auth", admin_guard)
    passed = sum(checks.values())
    return {"checks": checks, "passed": passed, "total": len(checks)}, f"{passed}/{len(checks)} storefront smoke checks passed"


# --------------------------------------------------- 10 Creative Director
BANNED_BRAND_PHRASES = ["official nba", "our official partner", "an official partner of", "endorsed by", "authorised dealer", "authorized dealer", "nba store", "licensed by the nba"]


@agent("creative_director")
def creative_director(conn, day):
    hits = []
    for f in list((ROOT / "storefront").glob("*.*")) + list((ROOT / "marketing").glob("*.md")) + list((ROOT / "brand").glob("*.md")):
        text = f.read_text(errors="ignore").lower()
        for ph in BANNED_BRAND_PHRASES:
            idx = text.find(ph)
            while idx != -1:
                ctx = text[max(0, idx - 60):idx]
                if not any(n in ctx for n in ("not ", "never", "no ", "avoid", "don't", "banned", "prohibited")):
                    hits.append({"file": str(f.relative_to(ROOT)), "phrase": ph})
                idx = text.find(ph, idx + 1)
    product_issues = []
    for p in rows(conn, "SELECT id, title, description, player_connection, supported_classification FROM products"):
        product_issues += [{"sku": p["id"], **i} for i in lint_copy(" ".join(filter(None, [p["title"], p["description"], p["player_connection"]])),
                                                                     p["supported_classification"] or "UNVERIFIED")]
    required = ["brand/BRAND_IDENTITY.md", "marketing/BRAND_FILM_THE_OTHER_SIDE_OF_THE_GLASS.md", "marketing/SOCIAL_CONTENT_PLAN.md",
                "marketing/LAUNCH_CAMPAIGN_REMEMBER_THE_SOUND.md"]
    missing = [r for r in required if not (ROOT / r).exists()]
    return {"affiliation_phrases": hits, "product_copy_issues": len(product_issues), "missing_assets": missing}, \
        f"{len(hits)} affiliation phrases; {len(product_issues)} product copy issues; {len(missing)} missing brand assets"


# --------------------------------------------------- 11 Community Manager
@agent("community_manager")
def community_manager(conn, day):
    pending = one(conn, "SELECT COUNT(*) n FROM wanted_posts WHERE status='PENDING_MODERATION'")["n"]
    open_posts = rows(conn, "SELECT * FROM wanted_posts WHERE status='OPEN'")
    matches = []
    for w in open_posts:
        if not w["team_or_school"]:
            continue
        hits = rows(conn, "SELECT id, title FROM opportunities WHERE team_or_school LIKE ? AND recommendation IN ('PROPOSE_TO_FOUNDER','INVESTIGATE')",
                    (f"%{w['team_or_school']}%",))
        if hits:
            matches.append({"wanted_id": w["id"], "opportunities": [h["id"] for h in hits]})
    wl = rows(conn, """SELECT p.team_or_school, COUNT(*) n FROM wishlist w JOIN products p ON p.id=w.product_id
                       GROUP BY p.team_or_school ORDER BY n DESC LIMIT 10""")
    wait = one(conn, "SELECT COUNT(*) n FROM waitlist WHERE unsubscribed=0")["n"]
    return {"wanted_pending_moderation": pending, "wanted_open": len(open_posts), "wanted_matches": matches,
            "wishlist_demand": wl, "waitlist": wait}, f"{pending} posts to moderate; {len(matches)} wanted matches; {wait} on waitlist"


# --------------------------------------------------- 12 Operations Manager
@agent("operations_manager")
def operations_manager(conn, day):
    tr = launch.tracker(conn)
    _csv(ROOT / "operations" / "launch_tracker.csv",
         ["slot", "lane", "target", "state", "product_id", "failed_checks"],
         [[s["slot"], s["lane"], s["target_description"], s["state"], s["product_id"] or "",
           ", ".join(s["gate"]["failed"]) if s["gate"] else ""] for s in tr["slots"]])
    cons = rows(conn, "SELECT status, COUNT(*) n FROM consignments GROUP BY status")
    return {"ready": tr["ready"], "ready_total": tr["ready_total"], "launch_ready": tr["launch_ready"], "consignments": cons}, \
        f"{tr['ready_total']}/30 launch products ready"


# ------------------------------------------------------ 1 General Manager
ORDER = ["nba_scout", "ncaa_scout", "wholesale_agent", "gear_hunter", "commercial_analyst", "auth_specialist",
         "outreach_agent", "operations_manager", "community_manager", "creative_director", "ecommerce_dev"]


@agent("general_manager")
def general_manager(conn, day):
    results = {}
    for name in ORDER:
        results[name] = run_one(conn, name, day)
    failures = [n for n, r in results.items() if not r["ok"]]
    quality = {
        "unsourced_players": one(conn, "SELECT COUNT(*) n FROM players p WHERE NOT EXISTS (SELECT 1 FROM sources s WHERE s.entity_type='player' AND s.entity_id=p.id)")["n"],
        "messages_sent_by_system": one(conn, "SELECT COUNT(*) n FROM outreach_messages WHERE status='SENT'")["n"],
        "spend_approved_aud": budget.summary(conn)["committed_aud"],
        "demo_products_purchasable": one(conn, "SELECT COUNT(*) n FROM products WHERE is_demo=1 AND status='LISTED'")["n"],
    }
    return {"agents_run": len(results), "failures": failures, "quality": quality}, \
        f"{len(results) - len(failures)}/{len(results)} agents completed; quality gates: {quality}"


def run_one(conn, name, day):
    started = now_iso()
    try:
        metrics, summary = AGENTS[name](conn, day)
        ok = True
    except Exception as e:  # keep the team running; record failure honestly
        metrics, summary, ok = {"error": repr(e), "trace": traceback.format_exc()[-800:]}, f"FAILED: {e!r}", False
    conn.execute("INSERT INTO agent_runs(agent, started_at, finished_at, ok, summary, metrics) VALUES (?,?,?,?,?,?)",
                 (name, started, now_iso(), int(ok), summary, json.dumps(metrics, default=str)))
    conn.commit()
    return {"ok": ok, "summary": summary, "metrics": metrics}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("agent", choices=sorted(AGENTS) + ["all"])
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--db")
    a = ap.parse_args(argv)
    conn = connect(a.db)
    name = "general_manager" if a.agent == "all" else a.agent
    r = run_one(conn, name, a.date)
    print(json.dumps(r, indent=2, default=str))
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

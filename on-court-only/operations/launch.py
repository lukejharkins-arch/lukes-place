"""30-product launch tracker and per-product launch gate."""
from authentication.rules import check_media, claim_allowed, classify, lint_copy
from commerce import config as C
from commerce.db import jload, one, rows

GATE_CHECKS = [
    "real_inventory", "right_to_sell", "classification_supported", "claim_matches_evidence", "copy_clean",
    "exact_item_photos", "reference_rights_resolved", "condition_recorded", "price_set", "fulfilment_plan",
    "returns_terms",
]


def product_evidence(conn, pid):
    return [r["code"] for r in rows(conn, "SELECT code FROM evidence WHERE product_id=?", (pid,))]


def gate(conn, pid) -> dict:
    p = one(conn, "SELECT * FROM products WHERE id=?", (pid,))
    if not p:
        raise KeyError(pid)
    ev = product_evidence(conn, pid)
    a = classify(ev, p["item_type"], p["season"], player_named=bool(p["player_id"]))
    media = rows(conn, "SELECT * FROM product_media WHERE product_id=?", (pid,))
    copy = " ".join(filter(None, [p["title"], p["description"], p["player_connection"], p["story_design"],
                                  p["story_vs_retail"], p["story_why_collect"]]))
    lint = lint_copy(copy, a.supported)
    media_problems = check_media(media, ev, bool(p["is_demo"]))
    checks = {
        "real_inventory": not p["is_demo"],
        "right_to_sell": bool(p["stock_confirmed"] and p["listing_authority_ref"]),
        "classification_supported": a.listable,
        "claim_matches_evidence": claim_allowed(p["claimed_classification"], a.supported),
        "copy_clean": not lint,
        "exact_item_photos": any(m["side"] == "ITEM" and m["match_level"] == "EXACT_ITEM_PHOTO" for m in media),
        "reference_rights_resolved": not any("Reference" in x or "EXACT_PHOTO_MATCH" in x for x in media_problems),
        "condition_recorded": bool(p["condition_grade"]),
        "price_set": bool(p["price_cents"]),
        "fulfilment_plan": bool(p["fulfilment_plan"]),
        "returns_terms": bool(p["returns_terms"]),
    }
    return {"product_id": pid, "title": p["title"], "ownership": p["ownership"], "ready": all(checks.values()),
            "checks": checks, "failed": [k for k, v in checks.items() if not v], "supported": a.supported,
            "copy_issues": lint, "media_problems": media_problems}


def tracker(conn) -> dict:
    slots = rows(conn, "SELECT * FROM launch_slots ORDER BY slot")
    out, ready = [], {"OWNED": 0, "CONSIGNMENT": 0, "PARTNER": 0}
    for s in slots:
        g = gate(conn, s["product_id"]) if s["product_id"] else None
        state = "EMPTY"
        if g:
            state = "READY" if g["ready"] else ("DEMO_PLACEHOLDER" if not g["checks"]["real_inventory"] else "IN_PROGRESS")
        if s["opportunity_id"] and not g:
            state = "SOURCING_CANDIDATE"
        if s["consignment_id"] and not g:
            state = "CONSIGNMENT_IN_REVIEW"
        if state == "READY":
            ready[s["lane"]] += 1
        out.append({**s, "state": state, "gate": g})
    return {"target": C.LAUNCH_MIX, "ready": ready, "ready_total": sum(ready.values()), "slots": out,
            "launch_ready": all(ready[k] >= v for k, v in C.LAUNCH_MIX.items()),
            "note": "Demo placeholders and wishlist bookmarks never count toward the 30."}


def ensure_slots(conn):
    if one(conn, "SELECT COUNT(*) n FROM launch_slots")["n"]:
        return
    n = 1
    plan = {
        "OWNED": ["Hero tearaway pants (OG era)", "Hero tearaway pants (OG era)", "Hero tearaway pants (current)",
                  "NCAA team-issued warmup pants", "Team-issued shooting shirt", "Team-issued warmup jacket",
                  "NCAA practice gear lot piece", "Australian-connected team-issued piece"],
        "CONSIGNMENT": ["Collector consignment"] * 17,
        "PARTNER": ["Partner-controlled stock with written listing authority"] * 5,
    }
    for lane, items in plan.items():
        for desc in items:
            conn.execute("INSERT INTO launch_slots(slot, lane, target_description) VALUES (?,?,?)", (n, lane, desc))
            n += 1
    conn.commit()

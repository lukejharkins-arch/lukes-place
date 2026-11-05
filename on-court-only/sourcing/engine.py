"""Daily deal opportunity engine.

Takes raw opportunities (from the Undervalued Gear Hunter, founder tips or
supplier lists), authenticates what the evidence supports, prices the landed
cost, values it from VERIFIED sold comparables only, scores and grades it, and
recommends. It never invents an opportunity and never fills the daily target.
"""
from __future__ import annotations

import json

from authentication.rules import classify, claim_allowed, BLOCKING_FLAGS
from commerce import config as C
from commerce.db import jload, now_iso
from sourcing import economics as E

# rarity uplift by supported class (how hard an equivalent is to find)
_RARITY = {"GAME_WORN": 10, "PLAYER_WORN": 9, "PLAYER_ISSUED": 8, "VINTAGE_TEAM_ISSUE": 7,
           "TEAM_ISSUED": 6, "RARE_KICKS": 6, "LICENSED_RETAIL": 2, "UNVERIFIED": 0}
_PROVENANCE = {"HIGH": 30, "MEDIUM": 20, "LOW": 8, "NONE": 0}
_CONDITION = {"DEADSTOCK": 10, "EXCELLENT": 9, "VERY_GOOD": 7, "GOOD": 5, "FAIR": 2}
_SOFT_FLAGS = {"NO_RETURNS": 2, "LOW_SELLER_FEEDBACK": 3, "STOCK_PHOTOS": 4, "NO_INTL_SHIPPING": 3,
               "VAGUE_DESCRIPTION": 1, "PRICE_TOO_GOOD": 3}


def evaluate(opp: dict, demand_score: float | None = None, budget_remaining_aud: float | None = None) -> dict:
    evidence = jload(opp.get("evidence"))
    flags = jload(opp.get("red_flags"))
    comps = jload(opp.get("comps"))
    reasons = []

    a = classify(evidence, opp.get("item_type") or "OTHER", opp.get("season"), flags,
                 player_named=bool(opp.get("player")))
    price = opp["listed_price_cents"] / 100
    ship = None if opp.get("shipping_cents") is None else opp["shipping_cents"] / 100
    lc = E.landed_cost(price, opp["currency"], ship)
    comp = E.comps_estimate(comps)
    resale_aud = comp["median_aud"]
    econ = E.resale(resale_aud, lc["total_aud"]) if resale_aud else None

    # ----- score (100)
    prov = _PROVENANCE[a.confidence] if a.supported not in ("UNVERIFIED", "LICENSED_RETAIL") else (
        5 if a.supported == "LICENSED_RETAIL" else 0)
    if econ:
        m = econ["gross_margin_pct"]
        econ_pts = max(0, min(18, m / 60 * 18)) + min(7, comp["count"] * 2.5)
    else:
        econ_pts = 0
    demand_pts = (demand_score or 0) / 100 * 15
    rarity_pts = _RARITY[a.supported]
    cond_pts = _CONDITION.get((opp.get("condition") or "").upper(), 4)
    soft = sum(_SOFT_FLAGS.get(f, 0) for f in flags)
    seller_pts = max(0, 10 - soft) if opp.get("live_verified") else max(0, 5 - soft)
    total = round(prov + econ_pts + demand_pts + rarity_pts + cond_pts + seller_pts, 1)

    # ----- hard gates
    if a.blocked_by:
        reasons += [f"BLOCKED: {BLOCKING_FLAGS[f]}" for f in a.blocked_by]
    if a.supported == "UNVERIFIED":
        reasons.append("Insufficient provenance: evidence does not support any listable class")
    claimed = opp.get("claimed_classification")
    if claimed and claimed != "UNKNOWN" and not claim_allowed(claimed, a.supported):
        reasons.append(f"Seller claims {claimed} but evidence supports {a.supported}: price must reflect the supported class")
    if comp["count"] < C.MIN_VERIFIED_COMPS_FOR_BUY:
        reasons.append(f"Only {comp['count']} verified sold comparable(s); {C.MIN_VERIFIED_COMPS_FOR_BUY} required")
    if econ and econ["gross_margin_pct"] < C.MIN_GROSS_MARGIN_PCT:
        reasons.append(f"Gross margin {econ['gross_margin_pct']}% below {C.MIN_GROSS_MARGIN_PCT}% floor")
    if not opp.get("live_verified"):
        reasons.append("Listing not loaded directly; re-verify it is live before any decision")
    if budget_remaining_aud is not None and lc["total_aud"] > budget_remaining_aud:
        reasons.append(f"Landed A${lc['total_aud']:.2f} exceeds remaining budget A${budget_remaining_aud:.2f}")
    if a.supported == "LICENSED_RETAIL":
        reasons.append("Licensed retail only: Logo Archive candidate, not core team-issue stock")

    # ----- risk grade A (lowest risk) to E
    risk_pts = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "NONE": 4}[a.confidence]
    risk_pts += 0 if comp["count"] >= 2 else 1
    risk_pts += min(2, soft // 3)
    risk_pts += 0 if opp.get("live_verified") else 1
    risk = "ABCDE"[min(4, risk_pts)] if not a.blocked_by else "E"

    hard_fail = bool(a.blocked_by) or a.supported == "UNVERIFIED"
    econ_fail = (econ is None) or econ["gross_margin_pct"] < C.MIN_GROSS_MARGIN_PCT
    if a.blocked_by or (econ and econ["gross_margin_pct"] < 0):
        rec = "REJECT"
    elif hard_fail:
        rec = "NEEDS_EVIDENCE"      # not qualified: request tag/label photos and provenance before any further work
    elif total >= C.A_GRADE_SCORE and not econ_fail and comp["count"] >= C.MIN_VERIFIED_COMPS_FOR_BUY \
            and opp.get("live_verified") and risk in "AB" and not any(r.startswith("Landed") for r in reasons):
        rec = "PROPOSE_TO_FOUNDER"     # never "buy": every purchase needs founder approval
    elif total >= C.B_GRADE_SCORE:
        rec = "INVESTIGATE"
    elif econ_fail and not hard_fail:
        rec = "WATCH"
    else:
        rec = "REJECT"

    grade = "A" if rec == "PROPOSE_TO_FOUNDER" else ("B" if rec in ("INVESTIGATE", "WATCH") else "C")
    return {
        "supported_classification": a.supported,
        "authentication": a.as_dict(),
        "landed": lc,
        "comps": comp,
        "economics": econ,
        "landed_cost_aud_cents": int(round(lc["total_aud"] * 100)),
        "est_resale_aud_cents": int(round(resale_aud * 100)) if resale_aud else None,
        "gross_margin_pct": econ["gross_margin_pct"] if econ else None,
        "demand_score": demand_score,
        "deal_score": total,
        "score_breakdown": {"provenance": prov, "economics": round(econ_pts, 1), "demand": round(demand_pts, 1),
                            "rarity": rarity_pts, "condition": cond_pts, "seller": seller_pts},
        "risk_grade": risk,
        "grade": grade,
        "recommendation": rec,
        "rejection_reasons": reasons,
    }


def evaluate_all(conn, include_demo: bool = True) -> list[dict]:
    """Evaluate and persist every opportunity. Returns ranked results."""
    from sourcing.demand import rank
    from operations.budget import remaining_aud

    demand = {r["organisation_id"]: r["score"] for r in rank(conn)}
    budget = remaining_aud(conn)
    q = "SELECT * FROM opportunities" + ("" if include_demo else " WHERE is_demo = 0")
    results = []
    for opp in [dict(r) for r in conn.execute(q)]:
        res = evaluate(opp, demand.get(opp.get("organisation_id")), budget)
        conn.execute(
            """UPDATE opportunities SET supported_classification=?, landed_cost_aud_cents=?, est_resale_aud_cents=?,
               gross_margin_pct=?, demand_score=?, deal_score=?, risk_grade=?, recommendation=?,
               rejection_reasons=?, evaluated_at=? WHERE id=?""",
            (res["supported_classification"], res["landed_cost_aud_cents"], res["est_resale_aud_cents"],
             res["gross_margin_pct"], res["demand_score"], res["deal_score"], res["risk_grade"],
             res["recommendation"], json.dumps(res["rejection_reasons"]), now_iso(), opp["id"]))
        results.append({**opp, **res})
    conn.commit()
    results.sort(key=lambda r: r["deal_score"], reverse=True)
    return results


def daily_summary(results: list[dict]) -> dict:
    live = [r for r in results if not r.get("is_demo")]
    qualified = [r for r in live if r["recommendation"] == "PROPOSE_TO_FOUNDER"]
    return {
        "target": C.DAILY_TARGET,
        "evaluated": len(live),
        "qualified": len(qualified),
        "shortfall": max(0, C.DAILY_TARGET - len(qualified)),
        "investigate": sum(1 for r in live if r["recommendation"] == "INVESTIGATE"),
        "watch": sum(1 for r in live if r["recommendation"] == "WATCH"),
        "needs_evidence": sum(1 for r in live if r["recommendation"] == "NEEDS_EVIDENCE"),
        "rejected": sum(1 for r in live if r["recommendation"] == "REJECT"),
        "note": "Shortfall is reported, never filled. Demo rows are excluded from all counts.",
    }

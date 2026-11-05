"""Team / programme demand scoring.

Each factor is scored 0-5 and tagged MEASURED (backed by a cited, dated source)
or ESTIMATE (informed judgement). The output always reports how much of the
score is measured, so estimates are never presented as statistics.
"""
from __future__ import annotations

FACTORS = {
    # factor: (weight, description)
    "popularity": (0.10, "Current NBA/NCAA popularity (attendance, viewership, merchandise rankings)"),
    "championships": (0.08, "Championship success"),
    "historic_players": (0.10, "Historic player significance"),
    "australian_connection": (0.12, "Verified Australian player connection"),
    "international_fanbase": (0.06, "International / Australian fanbase"),
    "collector_resale": (0.12, "Collector resale demand (sell-through, watchers)"),
    "social_engagement": (0.06, "Social engagement"),
    "recent_finals": (0.08, "Recent Finals / Final Four appearances"),
    "iconic_design": (0.10, "Iconic uniforms and warmup designs"),
    "rare_supply": (0.06, "Scarcity of supply (higher = rarer)"),
    "sold_prices": (0.08, "Verified sold price level"),
    "competition": (0.04, "Low market competition (higher = less competition)"),
}
assert abs(sum(w for w, _ in FACTORS.values()) - 1.0) < 1e-9


def score(factors: dict[str, dict]) -> dict:
    """factors: {name: {"score": 0-5, "basis": "MEASURED"|"ESTIMATE"}} -> 0-100 score.

    Missing factors count as 0 and are listed, so gaps lower the score rather than
    being silently assumed.
    """
    total = 0.0
    measured_weight = 0.0
    missing = []
    for name, (weight, _) in FACTORS.items():
        f = factors.get(name)
        if not f:
            missing.append(name)
            continue
        s = max(0.0, min(5.0, float(f["score"])))
        total += weight * s / 5 * 100
        if f.get("basis") == "MEASURED":
            measured_weight += weight
    return {
        "score": round(total, 1),
        "measured_share_pct": round(measured_weight * 100, 1),
        "missing_factors": missing,
        "label": "MEASURED-LED" if measured_weight >= 0.5 else "ESTIMATE-LED",
    }


def rank(conn) -> list[dict]:
    """Rank every organisation that has demand factors recorded."""
    out = []
    org_rows = conn.execute(
        "SELECT DISTINCT o.id, o.name, o.kind, o.league_id FROM organisations o "
        "JOIN demand_factors d ON d.organisation_id = o.id").fetchall()
    for o in org_rows:
        facs = {r["factor"]: {"score": r["score"], "basis": r["basis"]}
                for r in conn.execute("SELECT factor, score, basis FROM demand_factors WHERE organisation_id=?",
                                      (o["id"],))}
        res = score(facs)
        out.append({"organisation_id": o["id"], "name": o["name"], "league": o["league_id"], **res})
    out.sort(key=lambda r: r["score"], reverse=True)
    for i, r in enumerate(out, 1):
        r["rank"] = i
    return out

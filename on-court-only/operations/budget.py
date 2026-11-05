"""Acquisition budget ledger. Enforces the founder's strict sub-A$2,000 ceiling.

Nothing here spends money. A PROPOSED line is a request for founder approval;
only the founder can mark a line APPROVED.
"""
from commerce import config as C
from commerce.db import audit, now_iso, one, rows

LIVE = ("APPROVED", "COMMITTED", "PAID")


class BudgetError(ValueError):
    pass


def committed_cents(conn) -> int:
    r = one(conn, f"SELECT COALESCE(SUM(amount_aud_cents),0) s FROM acquisitions WHERE status IN {LIVE}")
    return r["s"]


def proposed_cents(conn) -> int:
    r = one(conn, "SELECT COALESCE(SUM(amount_aud_cents),0) s FROM acquisitions WHERE status='PROPOSED'")
    return r["s"]


def remaining_aud(conn) -> float:
    return (C.ACQUISITION_CEILING_AUD_CENTS - 1 - committed_cents(conn)) / 100  # strictly under the ceiling


def summary(conn) -> dict:
    by_cat = {r["category"]: r for r in rows(conn, f"""SELECT category,
        SUM(CASE WHEN status IN {LIVE} THEN amount_aud_cents ELSE 0 END) committed,
        SUM(CASE WHEN status='PROPOSED' THEN amount_aud_cents ELSE 0 END) proposed
        FROM acquisitions GROUP BY category""")}
    cats = []
    for cat, env in C.PLANNING_ENVELOPE_AUD_CENTS.items():
        r = by_cat.get(cat, {"committed": 0, "proposed": 0})
        cats.append({"category": cat, "envelope_aud": env / 100, "committed_aud": (r["committed"] or 0) / 100,
                     "proposed_aud": (r["proposed"] or 0) / 100})
    com = committed_cents(conn)
    return {"ceiling_aud": C.ACQUISITION_CEILING_AUD_CENTS / 100, "rule": "Total approved acquisitions must stay strictly under A$2,000",
            "committed_aud": com / 100, "proposed_aud": proposed_cents(conn) / 100,
            "remaining_aud": round(remaining_aud(conn), 2),
            "categories": cats, "spend_authorised": False,
            "note": "No spending is authorised by this system. Every line needs founder approval."}


def propose(conn, description, category, amount_aud, opportunity_id=None, actor="commercial_analyst"):
    if category not in C.PLANNING_ENVELOPE_AUD_CENTS:
        raise BudgetError(f"Unknown category {category}")
    cents = int(round(amount_aud * 100))
    if cents <= 0:
        raise BudgetError("Amount must be positive")
    if committed_cents(conn) + cents >= C.ACQUISITION_CEILING_AUD_CENTS:
        raise BudgetError("Proposal would breach the strict A$2,000 ceiling")
    cur = conn.execute("INSERT INTO acquisitions(opportunity_id, description, category, amount_aud_cents) VALUES (?,?,?,?)",
                       (opportunity_id, description, category, cents))
    audit(conn, actor, "BUDGET_PROPOSE", "acquisition", str(cur.lastrowid), {"amount_aud": amount_aud})
    conn.commit()
    return cur.lastrowid


def approve(conn, acquisition_id, founder_name):
    """Founder-only. Re-checks the ceiling at approval time."""
    a = one(conn, "SELECT * FROM acquisitions WHERE id=?", (acquisition_id,))
    if not a or a["status"] != "PROPOSED":
        raise BudgetError("Only PROPOSED lines can be approved")
    if committed_cents(conn) + a["amount_aud_cents"] >= C.ACQUISITION_CEILING_AUD_CENTS:
        raise BudgetError("Approval would breach the strict A$2,000 ceiling")
    conn.execute("UPDATE acquisitions SET status='APPROVED', approved_by=?, approved_at=? WHERE id=?",
                 (founder_name, now_iso(), acquisition_id))
    audit(conn, founder_name, "BUDGET_APPROVE", "acquisition", str(acquisition_id))
    conn.commit()

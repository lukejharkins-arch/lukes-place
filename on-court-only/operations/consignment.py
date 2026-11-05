"""Consignment lifecycle state machine and seller onboarding framework."""
import json

from authentication.rules import classify
from commerce.db import audit, now_iso, one
from sourcing.economics import consignment_payout

TRANSITIONS = {
    "SUBMITTED": {"EVIDENCE_REVIEW", "DECLINED"},
    "EVIDENCE_REVIEW": {"ACCEPTED", "DECLINED"},
    "ACCEPTED": {"AGREEMENT_SENT", "DECLINED"},
    "AGREEMENT_SENT": {"AGREEMENT_SIGNED", "DECLINED"},
    "AGREEMENT_SIGNED": {"RECEIVED", "RETURNED"},
    "RECEIVED": {"AUTHENTICATED", "RETURNED"},
    "AUTHENTICATED": {"LISTED", "RETURNED"},
    "LISTED": {"SOLD", "RETURNED"},
    "SOLD": {"PAID_OUT"},
    "DECLINED": set(), "PAID_OUT": set(), "RETURNED": set(),
}

SELLER_TIERS = {
    "APPLICANT": {"can": ["submit consignment applications", "post wanted items"], "requires": []},
    "ID_VERIFIED": {"can": ["consign through ON COURT ONLY custody"],
                    "requires": ["identity_verified", "contact_verified", "agreement_terms_accepted"]},
    "VERIFIED_COLLECTOR": {"can": ["list in the Collector Exchange with ON COURT ONLY authentication before sale"],
                           "requires": ["identity_verified", "contact_verified", "agreement_terms_accepted",
                                        "three_successful_consignments", "no_open_disputes", "payout_account_verified"]},
    "APPROVED_PARTNER": {"can": ["supply partner-controlled stock with written listing authority"],
                         "requires": ["identity_verified", "business_verified", "written_listing_authority",
                                      "provenance_documentation_standard", "insurance_or_custody_terms"]},
}


class ConsignmentError(ValueError):
    pass


def submit(conn, data: dict) -> dict:
    required = ["applicant_name", "applicant_email", "item_description"]
    missing = [k for k in required if not (data.get(k) or "").strip()]
    if missing:
        raise ConsignmentError(f"Missing: {', '.join(missing)}")
    if "@" not in data["applicant_email"]:
        raise ConsignmentError("A valid email is required")
    evidence = [e for e in data.get("evidence_offered", []) if isinstance(e, str)]
    pre = classify(evidence, data.get("item_type") or "OTHER", data.get("era"))
    cur = conn.execute(
        """INSERT INTO consignments(applicant_name, applicant_email, item_description, team_or_school, era,
           claimed_classification, provenance_story, evidence_offered, asking_price_cents) VALUES (?,?,?,?,?,?,?,?,?)""",
        (data["applicant_name"].strip()[:120], data["applicant_email"].strip()[:200], data["item_description"][:2000],
         data.get("team_or_school"), data.get("era"), data.get("claimed_classification"),
         (data.get("provenance_story") or "")[:4000], json.dumps(evidence),
         int(float(data["asking_price_aud"]) * 100) if data.get("asking_price_aud") else None))
    audit(conn, data["applicant_email"], "CONSIGNMENT_SUBMIT", "consignment", str(cur.lastrowid))
    conn.commit()
    return {"id": cur.lastrowid, "status": "SUBMITTED", "preliminary_assessment": pre.as_dict(),
            "message": "Received. Nothing is accepted until our authentication review and a signed agreement."}


def advance(conn, cid: int, new_status: str, actor: str, notes: str = None, **fields):
    c = one(conn, "SELECT * FROM consignments WHERE id=?", (cid,))
    if not c:
        raise ConsignmentError("Not found")
    if new_status not in TRANSITIONS[c["status"]]:
        raise ConsignmentError(f"Cannot move {c['status']} -> {new_status}")
    if new_status == "LISTED" and not c["product_id"] and not fields.get("product_id"):
        raise ConsignmentError("Listing requires a linked product record")
    if new_status == "RECEIVED" and not (c["agreement_ref"] or fields.get("agreement_ref")):
        raise ConsignmentError("Receiving stock requires a signed agreement reference")
    sets = {"status": new_status, "updated_at": now_iso(), **{k: v for k, v in fields.items()
                                                                  if k in ("agreement_ref", "product_id", "commission_pct")}}
    if notes:
        sets["decision_notes"] = notes
    conn.execute(f"UPDATE consignments SET {', '.join(k + '=?' for k in sets)} WHERE id=?", (*sets.values(), cid))
    audit(conn, actor, "CONSIGNMENT_" + new_status, "consignment", str(cid), notes)
    conn.commit()
    return one(conn, "SELECT * FROM consignments WHERE id=?", (cid,))


def payout_quote(sale_price_aud: float) -> dict:
    return consignment_payout(sale_price_aud)


def seller_tier_check(checks: dict, tier: str) -> dict:
    req = SELLER_TIERS[tier]["requires"]
    missing = [r for r in req if not checks.get(r)]
    return {"tier": tier, "eligible": not missing, "missing": missing}

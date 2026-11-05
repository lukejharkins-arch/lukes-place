# Consignment management process

State machine in `operations/consignment.py` (illegal jumps are refused in code):

`SUBMITTED → EVIDENCE_REVIEW → ACCEPTED → AGREEMENT_SENT → AGREEMENT_SIGNED → RECEIVED → AUTHENTICATED → LISTED → SOLD → PAID_OUT`
(DECLINED or RETURNED are possible at the allowed points.)

| Step | Owner | What happens | Code guard |
|---|---|---|---|
| Submit | Collector (web form) | Item, provenance story, evidence held; instant preliminary class | Valid email, required fields |
| Evidence review | Authentication Specialist | Photos of tags, snaps, size label; documents checked | |
| Accept or decline | Founder | Decide on fit, price expectations, demand | |
| Agreement | Founder | Written consignment agreement: commission (proposed 25%, 20% over A$1,000), minimum price, term (90 days), insurance in custody, return shipping, payout timing, the consignor's warranty of title | `RECEIVED` refused without `agreement_ref` |
| Receive | Operations | Logged into custody, photographed on arrival | |
| Authenticate | Authentication Specialist | Classification recorded; mismatches go back to the consignor | |
| List | Operations | Product record created and gate passed | `LISTED` refused without a product |
| Sell and pay out | Founder | Payout after the return window | `payout_quote()` |

**Legal notes (from docs/LEGAL_RESEARCH.md):** consignment is a bailment; private collectors are generally outside PPSA "commercial consignment" rules but dealer consignors should be registered on the PPSR; keep consigned stock physically and financially separate; the consignor warrants title, and we never accept items tied to restricted college athlete NIL policies or of unclear origin.

**Seller onboarding tiers** (`SELLER_TIERS`): APPLICANT → ID_VERIFIED → VERIFIED_COLLECTOR (3 successful consignments, no disputes, payout account verified) → APPROVED_PARTNER (business verified, written listing authority, documentation standard, insurance or custody terms).

# Product and inventory model

Source of truth: `data/schema.sql`. Key tables and how they enforce the rules:

| Table | Purpose | Enforced rule |
|---|---|---|
| `products` | One row per physical item (SKU). Title, department, era (OG/CURRENT), team, season, manufacturer, size, condition, **claimed** class, **supported** class, museum story fields, price, ownership lane, status, stock, listing authority | Purchasable only if not demo, `LISTED`, `stock_confirmed`, quantity > 0 and a listing authority reference exists |
| `evidence` | Evidence codes per product with reference IDs, URLs, verifier and date | Supported class is derived from these by `authentication/rules.py`; seller claims are not evidence |
| `custody_events` | Ordered chain of custody, each marked documented or not | Feeds the exhibit timeline |
| `product_media` | ITEM side (exact item photo / illustration placeholder) and REFERENCE side (exact photo-match / same design / era / pending) with rights status | Images without usable rights are never displayed; exact photo-match requires PHOTO_MATCH evidence |
| `auth_reviews` | Every authentication review with findings JSON | Audit of who classified what and when |
| `launch_slots` | 30 slots: 8 OWNED, 17 CONSIGNMENT, 5 PARTNER | A slot counts only when its product passes the gate |
| `acquisitions` | Budget lines (PROPOSED → APPROVED by the founder) | Strictly under A$2,000 total, checked at proposal and approval |
| `consignments`, `sellers` | Consignment lifecycle and seller tiers | Agreement before receipt; product record before listing |
| `opportunities` | Sourcing leads with computed landed cost, margin, score, risk, recommendation | Only verified comparables value an item |

**Ownership lanes:** OWNED (we hold title), CONSIGNMENT (collector holds title, we hold custody under agreement), PARTNER (supplier holds stock, we hold written listing authority), MARKETPLACE (future peer listings), DEMO (illustrative only).

**Status lifecycle:** DRAFT → IN_REVIEW → LISTED → RESERVED → SOLD, or WITHDRAWN. DEMO rows are public but never purchasable; DRAFT and IN_REVIEW are never public.

**Title convention:** `Team | Player or Era | Original Manufacturer + Class + Item`, e.g. "Orlando Magic | Penny Hardaway Era | Team-Issued Tearaway Warmup Pants". The manufacturer is named only when the item's own tags show it.

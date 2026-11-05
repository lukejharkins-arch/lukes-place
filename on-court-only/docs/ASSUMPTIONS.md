# Assumptions register

All are in `commerce/config.py` unless noted. Re-check before any founder decision.

| Assumption | Value | Type | Source or basis |
|---|---|---|---|
| FX USD→AUD | 1.53 | ESTIMATE | Not a live quote; replace with a dated rate |
| FX conversion margin | 3% | ESTIMATE | Typical card or PayPal margin |
| GST on low-value imports | 10%, collected at checkout | Rule (verify) | LVG regime, A$1,000 threshold (`docs/LEGAL_RESEARCH.md`) |
| Apparel duty above A$1,000 | 5% | ESTIMATE | 0-5% by tariff line and origin; some clothing tariffs removed 1 Jul 2026 (unconfirmed) |
| Formal entry and broker charges | A$150 | ESTIMATE | Quote needed |
| International shipping when not shown | A$55 | ESTIMATE | US→AU tracked ~1 kg |
| Consolidated shipping share | ~US$21 per item | ESTIMATE | Forwarder parcel split across 8 items |
| Auth and prep per item | A$15 | ESTIMATE | Materials |
| Card fee | 1.7% + 30c | Researched | Shopify Payments AU domestic (2026-11-05) |
| Outbound domestic shipping | A$12.05 | Researched | Australia Post small satchel (search extract) |
| Returns allowance | 3% | ESTIMATE | |
| GST registered | No | Founder or accountant decision | Under A$75k threshold |
| Consignment commission | 25% (20% over A$1,000) | PROPOSED terms | Not agreed with anyone |
| Gross margin floor | 35% | Business rule | |
| Verified comparables needed | 2 | Business rule | |
| A-grade score | 80/100 | Business rule | |
| OG era cutoff | Season start ≤ 2009 | Business rule | Brief: 1990s through 2000s |
| Demand factor tiers | Build-team judgement | ESTIMATE | Only Australian connection and some finals results are MEASURED |
| Title counts in baseline | Model knowledge | ESTIMATE | Marked "verify" in the register |

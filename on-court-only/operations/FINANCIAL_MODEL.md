# Financial model | launch (ESTIMATES, not authorisations)

Computed with the project's own engine (`sourcing/economics.py`), assumptions in `commerce/config.py` (FX USD→AUD 1.53, 3% FX fee, 10% GST on low-value imports, A$15 prep, 1.7% + 30c card fee, A$12.05 outbound satchel, 3% returns allowance, not GST-registered). Nothing here authorises spending.

## 1. Inventory acquisition (strictly under A$2,000)
| Envelope (founder) | A$ | Plan |
|---|---|---|
| Tearaways | 850 | 5 pairs at about US$70 each |
| Other items | 450 | 3 pieces at about US$45 each |
| Freight and import | 350 | Consolidated via one US forwarder parcel |
| Authentication and prep | 150 | Cleaning, inspection, photography materials |
| Reserve | 150 | Unallocated |
| **Total** | **1,950** | |

**Finding:** buying US items one parcel at a time kills the margin.
| Scenario | Landed per item | Sale | Gross profit | Margin |
|---|---|---|---|---|
| Tearaway, single parcel (US$70 + US$35 ship) | A$196.53 | A$320 | A$96.08 | 30.0% (below 35% floor) |
| Tearaway, consolidated (US$70 + ~US$21 ship share) | A$172.33 | A$320 | A$120.28 | 37.6% |
| Other piece, single parcel (US$45 + US$30) | A$144.67 | A$200 | A$33.58 | 16.8% |
| Other piece, consolidated | A$129.11 | A$200 | A$49.14 | 24.6% |

8 owned items consolidated: about **A$1,249 landed**, leaving about A$700 of headroom. Recommendation: owned stock should be tearaways and higher-value pieces with verified comparables; cheap "other" pieces are better taken on consignment.

## 2. 30-product launch economics (illustrative average prices)
| Lane | Units | Avg sale | GMV | Our gross profit |
|---|---|---|---|---|
| Owned (5 tearaways at A$320, 3 others at A$200) | 8 | | A$2,200 | about A$581 single-parcel, about A$749 consolidated |
| Consignment (25% commission, less fees and shipping) | 17 | A$350 | A$5,950 | A$1,176 (A$69.20 each) |
| Partner (assumed 20% margin to us) | 5 | A$400 | A$2,000 | A$304 |
| **Total** | **30** | | **A$10,150** | **about A$2,062-2,230** |

Consignment carries most of the profit with no inventory cash at risk. That is why the 17-item consignment lane matters most.

## 3. Operating costs (separate from inventory; need separate approval)
| Item | Monthly | Year 1 | Basis |
|---|---|---|---|
| Shopify Basic (annual billing) | A$42 | A$504 | Platform research 2026-11-05 |
| Consignment app (SplitMere) | ~A$29 | ~A$350 | US$19, ESTIMATE FX |
| Domain and email (Google Workspace starter) | ~A$12 | ~A$165 | ESTIMATE |
| Email marketing (free tier to start) | 0 | 0 | ESTIMATE |
| Business name registration (ASIC, 1 yr) | | ~A$45 | ESTIMATE, verify |
| Trade mark application, classes 25 and 35 | | ~A$500-660 | ESTIMATE, verify IP Australia fees |
| Legal review (IP, ACL, consignment agreement) | | A$1,500-3,000 | ESTIMATE, quote needed |
| Photography kit (lightbox, backdrop) | | ~A$150 | ESTIMATE |
| Packaging | | ~A$2 per order | ESTIMATE |
| Launch marketing (organic first) | | A$0-500 | Founder decision |
| **Year 1 operating (excluding legal and marketing)** | | **about A$1,700-1,900** | |

## 4. GST
Below the A$75,000 turnover threshold, registration is optional (confirm with an accountant). If registered: 1/11 of sales is GST payable; Division 66 may give credits on second-hand goods bought from unregistered local sellers (applicability to imports needs advice). The model has a switch, `GST_REGISTERED`.

## 5. Cash requirement before first sale
Inventory up to A$1,950 (founder-approved lines only) + operating set-up about A$700-1,300 (excluding legal) + legal review. About **A$4,200-6,300** all-in with legal, flagged ESTIMATE.

# ON COURT ONLY: Commerce Platform Evaluation

**Prepared:** 5 November 2026
**Purpose:** Choose a platform for:
- **(a) Launch:** about 30 items, hybrid owned stock plus consignment, Australian-based, selling domestically and to some international buyers.
- **(b) Later:** a verified collector marketplace with third-party sellers, authentication and split payouts.

### How prices were verified, and how much to trust them
- **Check date:** every price below was checked on **5 November 2026**.
- **Method:** web search of the vendor's official pricing page. Full page fetching was blocked by the session's network proxy, so most figures come from **search-result extracts** of the official page, not a full page read.
- **Trust labels:**
  - **[OFFICIAL]**: figure taken from the vendor's own page.
  - **[SECONDARY]**: figure taken from a third-party site.
  - **[UNVERIFIED]**: background knowledge only, not checked this session.
- **Search budget:** the web-search budget ran out before Marketplacer, Nautical, Dokan, WCFM, Medusa, Saleor, Hydrogen/Oxygen and hosting prices could be checked. Those rows are **[UNVERIFIED]** and must be re-checked before any decision.
- **Currency:** USD prices are shown as USD. Do not assume AUD conversions.
- **Taxes:** card and gateway fees may or may not include GST. Confirm on each provider's invoice.

### Market changes in 2026 that affect payments and shipping
1. **RBA card reforms from 1 October 2026:**
   - card surcharges are banned;
   - domestic interchange caps are lower (credit cap from about 0.8% to 0.3%; debit cap lower);
   - international-card interchange changes from 1 April 2027.

   Effect: we cannot pass card fees on as a surcharge, so they must be priced into the product.
   Sources: Checkout.com, https://www.checkout.com/blog/australia-card-payment-changes-2026 ; Sprintlaw, https://sprintlaw.com.au/articles/card-surcharge-rules-2026/ ; InvestSmart, https://www.investsmart.com.au/investment-news/the-hidden-catch-in-australias-card-surcharge-ban/155336 ; Shopify Community thread, https://community.shopify.com/t/rba-surcharge-ban-1-oct-2026-what-are-other-au-merchants-actually-doing-besides-raising-prices/664518
2. **Stripe cut its Australian domestic online card rate** from 1.70% + A$0.30 to **1.65% + A$0.30** from 1 October 2026.
   Source: Stripe Support, https://support.stripe.com/questions/updates-to-card-pricing-in-australia-from-october-2026 [OFFICIAL]
3. **Sendle is no longer an option.** It ceased Australian operations on **11 January 2026** and went into liquidation in late February 2026.
   Sources: SmartCompany, https://www.smartcompany.com.au/exclusive/sendle-liquidation-appointment-collapse-after-abrupt-closure/ ; ACS Information Age, https://ia.acs.org.au/article/2026/sendle-shuts-down-after-12-years---100m-in-funding.html ; Shippit (alternatives), https://www.shippit.com/blog/sendle-shut-down-in-australia-shipping-alternatives

---

## 1. Shopify (Australia)

**Source:** https://www.shopify.com/au/pricing, checked 5 Nov 2026 [OFFICIAL, from search extract]

### 1.1 Plans (AUD)

| Plan | Monthly billing | Annual billing (per month) | Notes |
|---|---|---|---|
| Basic | **A$56** | **A$42** | Enough for about 30 items. Includes discounts, gift cards, basic reports. |
| Grow | **A$149** | **A$114** | More staff accounts, better reports, lower card rates |
| Advanced | **A$575** | **A$431** | Custom reports, lower rates |
| Plus | **from A$3,700** | n/a | Enterprise; B2B; checkout extensibility. Shown "from A$3,700/mo" on the AU page. Confirm term length and whether it is a variable platform fee. |

### 1.2 Shopify Payments (online card rates, AUD)
Shown on the AU pricing page as at 5 Nov 2026.

| Plan | Domestic cards | Amex | International cards | Third-party gateway fee (if not using Shopify Payments) |
|---|---|---|---|---|
| Basic | **1.7% + 30c** | 2.9% + 30c | 3.5% + 30c | **2.0%** |
| Grow | **1.55% + 30c** | 2.8% + 30c | 3.4% + 30c | **1.0%** |
| Advanced | **1.35% + 30c** | 2.7% + 30c | 3.3% + 30c | **0.6%** |
| Plus | **1.15% + 30c** | 2.6% + 30c | 3.2% + 30c | **0.2%** |

Source: https://www.shopify.com/au/pricing [OFFICIAL, from search extract]

**Caveats:**
- Some third-party guides list Basic at 1.75%, Grow at 1.6% and Advanced at 1.4%. These look like older rates. Kida Digital, https://www.kidadigital.com.au/blog/how-much-does-shopify-cost-in-australia-2025-2026-pricing-breakdown [SECONDARY]
- Shopify has not been seen announcing a post-1 October 2026 rate cut equivalent to Stripe's. **Re-check in the Shopify admin before launch.**
- In-person (POS) rates are 1.85% on Basic down to 1.45% on Plus, if you ever do pop-ups. [OFFICIAL extract]
- Shopify **Shop Pay Installments** is a US feature. Australian buy-now-pay-later (BNPL) on Shopify is via Afterpay or Zip apps (section 7).

### 1.3 Shopify apps for consignment and multi-vendor
Prices are USD per month, from the Shopify App Store, checked 5 Nov 2026.

| App | Purpose | Price | Source | Notes |
|---|---|---|---|---|
| **Consignify** | Consignment tracking and payouts | from **US$15/mo** | https://apps.shopify.com/consignify [OFFICIAL extract] | Low cost; check AU payout methods |
| **JustConsignIN** | Consignment | from **US$19/mo** | https://apps.shopify.com/justconsignin [OFFICIAL extract] | |
| **SplitMere: Consignment Payouts** | Consignor commissions, statements, consignor portal | **US$19/mo**, 14-day trial | https://apps.shopify.com/splitmere-consignment-payouts [OFFICIAL extract] | Good fit for launch |
| **Consignbook** | Consignor payouts (store credit or manual cash/PayPal records) | **Free** tier (up to 10 consignors), paid tiers above | https://apps.shopify.com/consignbook-consignor-payouts [OFFICIAL extract] | Free tier fits a 30-item launch |
| **What's Their Cut**, **Still Works Consignment**, **ConsignKit** | Consignment | Free plans listed for the first two; ConsignKit not priced | https://apps.shopify.com/whats-their-cut ; https://apps.shopify.com/still-works-consignment ; https://apps.shopify.com/consignkit | |
| **PuppetVendors** | Vendor and consignor management, payouts | from **US$49/mo** (stated on vendor's own blog) | https://puppetvendors.com/best-consignment-software-for-shopify [SECONDARY, vendor-authored] | |
| **"ConsignPro" / "Consignment Partner"** | Named in the brief | **Not found** | n/a | **[UNVERIFIED]**: no Shopify app by these names was found |
| **Webkul MultiVendor Marketplace** | Full multi-vendor marketplace on Shopify (seller sign-up, commissions, seller dashboards) | from **US$15/mo**. Third-party sources give tiers Basic US$15 (3 sellers), Executive US$40 (10), Pro US$60 (unlimited). | https://apps.shopify.com/multi-vendor-marketplace [OFFICIAL "from" price]; tier detail [SECONDARY], https://easysellapp.com/blogs/wiki/best-shopify-multi-vendor-marketplace-apps-2026 | Key features (API, vendor analytics, split payments via Mangopay or Stripe) sit on higher tiers or add-ons |
| **Shipturtle (Multi Vendor Marketplace Pro+)** | Multi-vendor marketplace and dropship sync | from **US$49/mo** on the Shopify listing. GetApp lists US$29 / 49 / 89 / 149 tiers. | https://apps.shopify.com/SHIPTURTLE [OFFICIAL "from" price]; https://www.getapp.com/operations-management-software/a/shipturtle [SECONDARY] | Supports vendor stores syncing products into ours |
| **Marketplacer** (Australian, Melbourne-founded) | Enterprise marketplace platform; can sit alongside Shopify or other front ends | **Quote only [UNVERIFIED]**; enterprise pricing is generally well beyond start-up budgets | https://marketplacer.com | Australian vendor with an AU support time zone, but sized for retailers and brands. Not a launch option. |
| **Nautical Commerce** | Enterprise multi-vendor (headless) | **Quote only [UNVERIFIED]** | https://www.nauticalcommerce.com | Current ownership and status not checked |

**Shopify limitation for a true marketplace:** Shopify Payments does not natively split a single payment between multiple sellers. Marketplace apps either:
- pay sellers out **after** we collect the funds, meaning we become merchant of record and carry the ACL and chargeback exposure; or
- integrate Stripe Connect or Mangopay (more cost and complexity).

Also check Shopify's Acceptable Use Policy and Payments terms on marketplace or "facilitating payments for others" use before building a marketplace on Shopify Payments. **[UNVERIFIED]**

---

## 2. WooCommerce (self-hosted WordPress)

| Item | Price | Source / status |
|---|---|---|
| WooCommerce core | Free (open source) | https://woocommerce.com [OFFICIAL] |
| **WooPayments** (Stripe-powered) | **1.75% + A$0.30** per domestic card; no monthly fee. International card rate not confirmed; one guide shows 3.4% + 30c for AU (other sources differ). Currency conversion may add about 1%. | Official fee table did not render: https://woocommerce.com/document/woopayments/fees-and-debits/fees/ . Domestic rate from a secondary source checked March 2026 [SECONDARY]. Whether WooPayments passes on Stripe's 1 Oct 2026 cut is unknown. |
| Managed WordPress hosting (AU data centre) | Typically about A$20–60/mo for a small store | **[UNVERIFIED]**: hosting prices not checked this session |
| **Dokan** (multi-vendor) | Free core; Pro tiers paid annually | **[UNVERIFIED]**: https://dokan.co/wordpress/pricing/ |
| **WCFM Marketplace** | Free core; paid add-ons ("Ultimate") | **[UNVERIFIED]**: https://wclovers.com |
| Premium theme, security, backups, plugin licences | About A$100–400/yr | **[UNVERIFIED]** |

**Trade-offs:**
- **For:** low software cost, and full control of data and SEO. Dokan and WCFM give a mature marketplace (vendor dashboards, commissions, Stripe Connect split payments via add-ons).
- **Against:** we own security, updates, plugin conflicts and performance. That is significant operational load for a one- to two-person start-up, and a real risk with payment and identity data.

---

## 3. Sharetribe (hosted marketplace software)

| Plan (from October 2026) | Price (USD) | Source |
|---|---|---|
| **Build** (development or test, not live) | **US$39/mo** | Sharetribe Help Centre, "Legacy plans and pricing transition timeline", https://www.sharetribe.com/help/en/articles/17106763-legacy-plans-and-pricing-transition-timeline [OFFICIAL extract] |
| **Live** (includes everything the old "Extend" plan did) | **US$259/mo**, or **US$199/mo** billed annually | Same source; changelog https://sharetribe.com/changelog/ [OFFICIAL extract] |
| Usage-based pricing | Applies to all customers from **1 December 2026**. The first 1 million usage credits per month are included. | https://www.sharetribe.com/docs/introduction/pricing/ [OFFICIAL extract] |
| Legacy four-tier pricing (Build / Lite / Pro / Extend: US$39 / 99 / 199 / 299) | Superseded. Still shown on third-party sites. | https://www.sharetribe.com/pricing.md [OFFICIAL, likely pre-October 2026] |

- **Payments:** Sharetribe uses **Stripe Connect** for split payments, seller onboarding (KYC) and payouts.
  - Stripe Connect supports Australian platforms and Australian connected accounts. **[UNVERIFIED this session]** Confirm at https://stripe.com/au/connect and https://www.sharetribe.com/docs/concepts/payments/
  - Stripe Connect fees apply on top of card fees. **[UNVERIFIED]**
- **Fit:** purpose-built for **peer-to-peer and collector marketplaces** (listings, seller accounts, reviews, transaction workflow, commission). It is weaker as a polished storefront or catalogue for our own stock. The Live plan plus custom code (its "Extend" capability) can add an authentication step in the transaction process.

---

## 4. Headless and custom

| Option | Price | Fit | Status |
|---|---|---|---|
| **Shopify Hydrogen + Oxygen** | Hydrogen (React framework) is free. Oxygen hosting is included with paid Shopify plans (believed to exclude Starter). | Premium custom front end on Shopify's checkout and back office. Good for the "OG Archive / Current Court" brand experience later. | **[UNVERIFIED]**: https://hydrogen.shopify.dev |
| **Medusa** (open-source Node commerce) | Self-host: free plus infrastructure (about A$20–100+/mo). Medusa Cloud is a paid tier. | Flexible; has marketplace recipes (vendors, split orders). Needs a developer. | **[UNVERIFIED]**: https://medusajs.com/pricing/ |
| **Saleor** (open-source GraphQL commerce) | Self-host: free plus infrastructure. Saleor Cloud is paid. | Strong multi-channel and multi-warehouse; marketplace needs custom work. | **[UNVERIFIED]**: https://saleor.io/pricing |
| **Fully custom** (for example Next.js + Supabase/Postgres + Stripe Connect) | Build cost about A$20k–100k+ by agency, or founder time; hosting about A$50–200/mo | Maximum control over authentication workflow and provenance records | Estimate only **[UNVERIFIED]** |

---

## 5. Payment providers (Australia)

| Provider | Domestic online cards | International cards | Other | Source / check date (5 Nov 2026) |
|---|---|---|---|---|
| **Shopify Payments** | 1.7% + 30c (Basic) to 1.15% + 30c (Plus) | 3.5% to 3.2% + 30c | Amex 2.9% to 2.6% + 30c; no third-party fee | https://www.shopify.com/au/pricing [OFFICIAL extract] |
| **Stripe (standard AU)** | **1.65% + A$0.30** from 1 Oct 2026 (was 1.70%) | **Not confirmed.** Sources conflict: 3.5% + 30c (long-standing) vs a reported reduction; international pricing reportedly changes again from 1 Apr 2027. | Connect, Billing and similar extra | Stripe Support, https://support.stripe.com/questions/updates-to-card-pricing-in-australia-from-october-2026 [OFFICIAL]; https://stripe.com/au/pricing (not readable this session); international figures from Wise, https://wise.com/au/blog/stripe-fees [SECONDARY] |
| **PayPal (AU merchant)** | **2.90% + fixed fee** (A$0.30) for domestic commercial transactions | Domestic rate **+ about 1%** cross-border fee [SECONDARY] | QR code transactions 1.20% (official extract). Currency conversion margin extra. | PayPal AU Merchant Fees, https://www.paypal.com/au/webapps/mpp/merchant-fees (page "last updated 9 Feb 2026" in extract; a PDF dated 23 Jul 2026 exists at https://www.paypalobjects.com/marketing/ua/pdf/AU/AU-merchant-fees-23-jul-2026.pdf but could not be read) [OFFICIAL extract]; Wise, https://wise.com/au/blog/paypal-fees-australia [SECONDARY]. If used on Shopify, add Shopify's third-party fee (2% on Basic). |
| **Afterpay** (BNPL) | Merchant fee typically quoted at about **4–6% + 30c** | n/a | Customer pays nothing extra | **Not verifiable.** No current official AU merchant rate published; figures dated. Morningstar, https://www.morningstar.com.au/stocks/new-buy-now-pay-later-rules-to-cut-margins-not-customers-morningstar [SECONDARY, dated]. Get a quote from Afterpay. |
| **Zip** (BNPL) | Merchant fee typically quoted at about **2–4%** (plus possible fixed fee) | n/a | | **Not verifiable.** Same Morningstar source [SECONDARY, dated]. Get a quote from Zip. |

**Implications:**
- With surcharges banned from 1 October 2026, a 4–6% BNPL fee on a A$250 jersey is about A$10–15. That may still pay for itself in conversion. Test it after launch.
- Avoid PayPal as a *gateway* on Shopify Basic (2.9% + 2% third-party fee = 4.9%). Use Shopify Payments, and offer PayPal Express only if the fee stack is acceptable.

---

## 6. Shipping: about 1 kg satchel

| Service | Price | Source / status (checked 5 Nov 2026) |
|---|---|---|
| **Australia Post Parcel Post, Small prepaid satchel** (domestic, up to 5 kg, size-based) | **about A$11.70** postage-only / **A$12.05** with satchel (prices from 1 July 2026) | Calcuris summary, https://calcuris.com/au/postage-calculator/ [SECONDARY]. An earlier official notice listed Small A$10.60 / Medium A$14.50 / Large A$18.25 / XL A$21.95 (older round): https://auspost.com.au/service-updates/pricing-updates/price-changes |
| **Australia Post Parcel Post, Medium prepaid satchel** (a folded warm-up suit may need this) | **about A$16.00** postage-only / A$16.40 with satchel; Express Post Medium about A$20.00 | Same [SECONDARY] |
| **MyPost Business** (discounted contract rates by volume band) | Lower than retail; varies by band | Check at https://auspost.com.au/business/shipping/mypost-business **[UNVERIFIED]** |
| **Australia Post International Standard to USA** (Zone 3), up to 1 kg | **about A$27–40.** The official page shows rows "over 250 g up to 1 kg A$27.25" and "over 500 g up to 1 kg A$39.75" (likely different products or weight steps). | https://auspost.com.au/business/shipping/parcels-international/standard [OFFICIAL extract, date unclear]. Confirm with the AP calculator. |
| **Australia Post International Courier to USA**, 1 kg | about A$100+ (A$106.90 in an older CHOICE comparison) | CHOICE, https://www.choice.com.au/shopping/shopping-for-services/services/articles/best-international-postal-service [SECONDARY, dated] |
| **Sendle** | **Not available.** Ceased Australian operations 11 Jan 2026; in liquidation. | Section "Market changes" sources above |
| Alternatives (aggregators: Shippit, iSend, Starshipit, Interparcel; carriers: CouriersPlease, Aramex) | iSend quotes "from A$7.49" for domestic parcels (weight band not stated) | https://isend.com.au [SECONDARY]; others **[UNVERIFIED]** |

**Notes:**
- For high-value items (A$300+), use tracked and signature-on-delivery service with transit insurance or Extra Cover.
- For US buyers, the US removed its US$800 de minimis exemption in 2025, so buyers may face duties and carrier fees. **[UNVERIFIED]** Disclose this at checkout.

---

## 7. Decision matrix

Scores run from 1 (poor) to 5 (excellent). Weights reflect the founder constraints: a cash ceiling under A$2,000 for acquisitions; a lean team; brand-led storytelling; provenance rigour.

### 7.1 Launch (a): 30 items, hybrid owned plus consignment

| Criterion (weight) | Shopify Basic + consignment app | WooCommerce + WooPayments | Sharetribe Live | Headless (Hydrogen/Medusa) | Custom build |
|---|---|---|---|---|---|
| Time to launch (20%) | **5** | 3 | 3 | 2 | 1 |
| Monthly cost at launch (15%) | **4** (A$42–56 + US$0–19 app) | **4** (hosting about A$20–60 [UNVERIFIED]) | 2 (US$199–259) | 3 | 1 |
| Payment fees (10%) | 4 (1.7% + 30c) | 4 (1.75% + 30c) | 3 (Stripe + Connect) | 4 | 4 |
| Consignment handling (15%) | **4** (apps: SplitMere, Consignbook) | 3 (plugins) | 3 (seller accounts; overkill) | 3 | 4 |
| Storefront and brand quality (15%) | **4** (themes; Hydrogen upgrade path) | 3 | 2 | **5** | **5** |
| Ops and security burden (15%) | **5** (hosted, PCI handled) | 2 | 4 | 2 | 1 |
| Provenance and authentication data (10%) | 3 (metafields, metaobjects) | 3 | 3 | 4 | **5** |
| **Weighted score** | **4.3** | 3.1 | 2.9 | 3.2 | 2.8 |

### 7.2 Later (b): verified collector marketplace

| Criterion (weight) | Shopify + Webkul/Shipturtle | Shopify Plus + Marketplacer | WooCommerce + Dokan/WCFM | Sharetribe Live | Medusa/custom + Stripe Connect |
|---|---|---|---|---|---|
| Native multi-seller and split payouts (20%) | 2 (we collect, then pay out) | **5** | 4 (with Stripe Connect add-on) | **5** (Stripe Connect built in) | **5** |
| Seller KYC and onboarding (10%) | 2 | 4 | 3 | **5** (Stripe hosted onboarding) | 4 |
| Authentication workflow (custom step, hold funds until verified) (20%) | 2 | 3 | 3 | **4** (configurable transaction process) | **5** |
| Cost at modest scale (15%) | **4** | 1 | **4** | 3 | 3 (developer time) |
| Brand storefront continuity with Phase A (15%) | **5** | **5** | 3 | 2 (separate site) | 4 |
| Ops burden (10%) | **4** | 3 | 2 | **4** | 2 |
| AU fit and support (10%) | 4 | **5** (AU vendor) | 3 | 3 | 3 |
| **Weighted score** | 3.2 | 3.7 (cost-prohibitive early) | 3.3 | **3.8** | **4.0** (only if a developer is available) |

---

## 8. Recommendation

### (a) Launch: **Shopify Basic (annual, A$42/mo) + Shopify Payments + a consignment app**
- **Consignment app:** start with Consignbook's free tier, or SplitMere at US$19/mo if you need consignor statements and a portal.
- **Why:** fastest route to a professional, secure store. About A$60–70/mo all-in. PCI-compliant checkout. Strong AU payment methods (Apple Pay, Google Pay, Afterpay app).
- **Provenance:** model each item's authenticity tier, evidence and season with **metafields or metaobjects**. They can be exposed later to a Hydrogen front end.
- **Payments:**
  - Stay on Shopify Payments to avoid the 2% third-party fee.
  - Price card costs into products; surcharging is banned from 1 Oct 2026.
  - Add Afterpay only after a quote.
- **Upgrade trigger:** move to Grow (A$114–149/mo) once monthly sales exceed about A$12–15k. The 0.15% rate saving plus reports pays for the difference at that volume. **[Estimate; re-check with actual rates.]**
- **Shipping:** Australia Post MyPost Business for domestic and international, through Shopify Shipping or an aggregator (Shippit or Starshipit). Do not plan around Sendle.
- **Build the existing demo storefront** (`storefront/`) into a Shopify theme. Defer Hydrogen until brand traffic justifies a developer.

### (b) Later verified collector marketplace: **decide at about 12 months. Default: Sharetribe Live + Stripe Connect as a separate "ON COURT ONLY Exchange", linked from the Shopify store**
- **Why:** native split payments and seller KYC through Stripe Connect. A configurable transaction process supports the core feature: **hold funds, ship to us for authentication, release payout on pass, refund on fail**. Avoids becoming merchant of record for every third-party item through Shopify.
- **Cost:** US$199–259/mo plus usage-based pricing from 1 Dec 2026. Re-check usage-credit costs at our volume.
- **Alternatives:**
  - **Medusa or a custom build with Stripe Connect**, if a capable developer (in-house or partner) is available. It scores highest on control of the authentication workflow and on unifying with the main store.
  - **Shopify + Webkul/Shipturtle** only as a low-cost pilot with a few trusted consignors. It keeps us as merchant of record, with the ACL and chargeback exposure that brings.
  - **Marketplacer**, only if ON COURT ONLY partners with a large retailer or league, given enterprise pricing.
- **Pre-conditions** (see `LEGAL_RESEARCH.md` section 9.1): seller terms, "Verified" definition, IP takedown process, insurance, and lawyer review of payment flows.

---

## 9. Open items to verify before committing

1. Whether Shopify Payments AU rates changed after the RBA reforms of 1 October 2026 (check Settings > Payments in the admin).
2. Stripe AU international card rate (https://stripe.com/au/pricing) and Stripe Connect fees.
3. Afterpay and Zip merchant quotes.
4. Whether Shopify's Payments terms permit Webkul/Shipturtle-style marketplace payouts.
5. Australia Post MyPost Business band rates, and International Standard to USA for 1 kg (calculator).
6. Prices for Dokan, WCFM, Medusa Cloud, Saleor Cloud, Hydrogen/Oxygen, Marketplacer and Nautical, plus AU WordPress hosting. **None were verified this session.**
7. "ConsignPro" and "Consignment Partner" Shopify apps. **Not found.** Confirm the intended products.

*Prepared 5 November 2026. Network restrictions blocked direct page loads and the web-search budget ran out before every price could be checked. Every figure here should be re-checked on the vendor page before purchase.*

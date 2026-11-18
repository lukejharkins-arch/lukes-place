Wren

# 03 Automation and data evidence base

Specialist: Wren, Data and Automation. For: Harbour and the Research Lead. Date: 18 Nov 2026. Status: first pass, model-agnostic (business model not yet chosen).

Sources are in `sources-03.md` and cited here by ID (S, D, L).

## How to read this

- **Observed** = a figure seen in a source on 18 Nov 2026, with source ID. **Observed (secondary)** = seen in a third-party tracker or law firm summary, not on the vendor or regulator page itself.
- **Assumption** = my working figure, logged so it can be challenged.
- **Forecast (2027/28)** = forward estimate, clearly labelled.
- Currency: vendor prices are in USD unless stated. **Assumption A-FX: US$1 = A$1.55, EUR 1 = A$1.75.** All AUD figures are ex GST.
- **Assumption A-GST:** LL Collective is not GST registered in the first 90 days (below the A$75k turnover threshold), so GST on overseas SaaS is a real cost, not a credit. If it registers, roughly 1/11 of local GST-inclusive costs is recoverable.

**Evidence quality warning.** This session's network blocked direct reads of vercel.com, supabase.com and stripe.com. Only the Claude API pricing page (S1) was read in full. Most other prices are "observed (secondary)". They agree across two or more trackers in most cases, but each should be re-checked on the vendor page before any spend. Overall confidence in stack prices: **medium**. Confidence in Claude prices: **high**.

---

## 1. Stack pricing (late 2026)

### 1.1 Claude API (observed, S1, 18 Nov 2026, USD per million tokens)

| Model | Input | Output | Cache hit | Batch (50% off) in / out | Use for |
|---|---|---|---|---|---|
| Haiku 5.5 (prompt up to 100k tokens) | 0.10 | 0.50 | 0.01 | 0.05 / 0.25 | Classification, routing, scoring, support triage |
| Haiku 5.5 (prompt over 100k tokens) | 0.50 | 2.50 | 0.05 | 0.25 / 1.25 | Avoid: keep Haiku prompts under 100k |
| Haiku 4.5 | 1.00 | 5.00 | 0.10 | 0.50 / 2.50 | Legacy, 10x dearer than Haiku 5.5 |
| Sonnet 5.5 | 2.00 | 10.00 | 0.10 | 1.00 / 5.00 | Default for customer-facing writing and delivery |
| Sonnet 5 | 2.00 | 10.00 | 0.20 | 1.00 / 5.00 | Intro price now permanent (no Sep 2026 rise) |
| Sonnet 4.6 / 4.5 | 3.00 | 15.00 | 0.30 | 1.50 / 7.50 | Legacy |
| Opus 5.5 | 4.00 | 20.00 | 0.20 | 2.00 / 10.00 | Hard reasoning, build-time work |
| Opus 5 / 4.8 / 4.7 / 4.6 / 4.5 | 5.00 | 25.00 | 0.50 | 2.50 / 12.50 | Legacy |
| Fable 5.2 / Mythos 5.2 (limited) | 8.00 | 40.00 | 0.20 | 4.00 / 20.00 | Top tier; not needed for production paths |

Other observed modifiers (S1): 5-minute cache writes 1.25x input, 1-hour cache writes 2x input; web search US$10 per 1,000 searches plus tokens; US-only inference (`inference_geo: "us"`) 1.1x; code execution free when used with web search or fetch, otherwise 1,550 free hours per organisation per month; new accounts get free credits; full 1M token context at standard rates on 4.6 and later (except Haiku 5.5, which is tiered at 100k).

**Unit costs (assumption: typical task = 3,000 input + 500 output tokens, no caching):**

| Model | Cost per task | Per 1,000 tasks (AUD) |
|---|---|---|
| Haiku 5.5 | US$0.00055 | A$0.85 |
| Sonnet 5.5 | US$0.011 (0.006 + 0.005) | A$17.05 |
| Opus 5.5 | US$0.022 (0.012 + 0.010) | A$34.10 |

Arithmetic, Sonnet 5.5: 3,000 x $2 / 1M = $0.006; 500 x $10 / 1M = $0.005; total $0.011. With a 2,500-token cached system prompt, input falls to 500 x $2/1M + 2,500 x $0.10/1M = $0.00125, so a cached Sonnet task is about US$0.0063 (43% cheaper).

**Price trend (observed, S1):** generation-on-generation, Haiku fell 90% (4.5 to 5.5), Sonnet input fell 33% (4.6 to 5.5), Opus fell 20% (5 to 5.5). **Forecast (2027/28):** flat to lower list prices; budget at today's prices plus a 50% usage buffer, not on further cuts.

### 1.2 Hosting, database, payments

| Item | Free tier | First paid tier | Key limits and traps | Label |
|---|---|---|---|---|
| Vercel Hobby | A$0 | n/a | **Personal, non-commercial use only**; paused when limits are exceeded; cannot buy extra usage; about 100 GB transfer, 1M edge requests | Observed (secondary), S3, S5 |
| Vercel Pro | n/a | US$20 (A$31) per seat per month incl. US$20 usage credit | About 1 TB transfer; overage pay-as-you-go, no pause | Observed (secondary), S4, S5 |
| Supabase Free | A$0, 2 projects | n/a | 500 MB DB, 50k MAU, 5 GB egress, 1 GB storage; **pauses after 7 days of inactivity** | Observed (secondary), S6, S7 |
| Supabase Pro | n/a | US$25 (A$38.75) per month incl. US$10 compute credit | 8 GB DB, 100k MAU, 250 GB egress; no pausing; next tier (Team) US$599 | Observed (secondary), S6 |
| Stripe AU domestic cards | n/a | **1.65% + A$0.30** from 1 Oct 2026 (was 1.7% + A$0.30) | Surcharging disabled from 1 Oct 2026, so fees must be priced in | Observed (secondary), S8 to S11 |
| Stripe AU international cards | n/a | 3.5% + A$0.30, plus 2% if currency converted | International pricing changes from 1 Apr 2027 (new rate not yet published) | Observed (secondary), S8, S12 |
| Stripe Billing | n/a | 0.7% of billing volume, pay as you go, no monthly fee | Excludes one-off invoices; usage-based billing moved to Metronome (Jul 2026) | Observed (secondary), S12 to S14 |

The deployed site is on the existing Vercel account. If that account is on Hobby, the first paying customer makes it commercial use: budget A$31 a month for Pro from first revenue. This is a fixed cost every model shares unless the storefront is hosted by a merchant of record (see 1.6).

Effective Stripe cost on a A$99 monthly subscription: 1.65% x 99 = A$1.63, + A$0.30, + Billing 0.7% x 99 = A$0.69; total A$2.62 (2.6%). On a A$29 sale: A$0.48 + 0.30 + 0.20 = A$0.98 (3.4%). Small tickets lose proportionally more to the fixed 30c.

### 1.3 Domains

| Item | Cost | Conditions | Label |
|---|---|---|---|
| .com.au / .au wholesale | A$9.50 ex GST per year from 1 Oct 2026 (was A$8.64) | 1 to 5 year terms | Observed, S15, S16 |
| .com.au retail | A$14 to A$25 per year typical | **Needs ABN, ACN or AU trade mark; name must relate to the registrant; renewal blocked if ABN inactive (from May 2026)** | Retail range observed (secondary) S17 to S18; range is assumption |
| .com retail | about A$17 to A$25 per year | No eligibility rules | Assumption |
| ABN | A$0 | Needed before .com.au, Twilio AU numbers (likely) and ABR web services are useful | Assumption (not re-verified this session) |

A pending eligibility proposal for .com.au was not yet law on 3 Oct 2026 (S17). Buying domains needs founder approval (decision rights).

### 1.4 Email

| Item | Free tier | Paid | Label |
|---|---|---|---|
| Resend (transactional) | 3,000 per month, 100 per day | from US$20 (A$31) for 50k | Observed (secondary), S19 |
| Postmark (transactional) | 100 per month | Basic US$15 (A$23) for 10k; Pro US$16.50 | Observed (secondary), S20, S21 |
| Google Workspace extra mailbox (cold sending) | n/a | Business Starter A$9.90 annual or A$11.80 flexible, per user per month ex GST | Observed, S24 |
| Smartlead (cold sequencing) | n/a | Base US$39 (A$60) monthly; US$32 annual; unlimited mailboxes | Observed (secondary), S22 |
| Instantly (cold sequencing) | n/a | Growth US$37.60 per month on annual billing (month-to-month higher, not confirmed) | Observed (secondary), S23 |

**Cold email minimum infrastructure (assumption):** 2 secondary .com domains (A$2.80 a month amortised), 2 Workspace mailboxes on flexible (A$23.60), Smartlead Base (A$60). **Total about A$86 a month.** Warm-up takes 2 to 4 weeks (assumption), so the clock starts before the first send. A zero-tool alternative: Claude drafts, a founder or a Gmail-API job sends 20 to 30 a day from a secondary domain mailbox (A$26 a month). Never send cold email from the primary domain.

### 1.5 Automation platforms

| Option | Cost | Limit that bites | Label |
|---|---|---|---|
| n8n self-host (Community) | A$0 licence, plus hosting | Sustainable Use Licence: fine for our own internal automation and client workflows we run; **not** for offering hosted n8n to customers without a commercial licence | Observed (secondary), S25, S26 |
| n8n Cloud Starter | about EUR 20 annual to 24 monthly (A$35 to A$42) | 2,500 executions per month; a 5-minute poll alone uses about 8,700 | Observed (secondary), S25 |
| Make Free / Core | Free 1,000 credits, 2 scenarios, 15-min interval; Core about US$9 to 10.59 (A$14 to A$16) for 10k credits | Credits replaced operations on 19 Jan 2026 | Observed (secondary), S27, S28 |
| Zapier Free / Professional | Free 100 tasks, 2-step Zaps; Professional US$19.99 annual to 29.99 monthly (A$31 to A$46) for 750 tasks | Poor value at volume | Observed (secondary), S27 |
| Code we own (Vercel functions, Vercel Cron, Supabase Edge Functions, pg_cron, GitHub Actions) with Claude Code as operator | A$0 beyond hosting already counted | Needs Claude Code to write and maintain it; no per-task fees | Assumption (free tiers not re-verified) |

**Recommendation (assumption):** default to code we own in the repo (Supabase plus Vercel functions plus cron) because Claude Code is the operator and there are no per-task fees. Use Make Free only for glue to tools without APIs. Avoid Zapier and n8n Cloud in the first 90 days.

### 1.6 Voice AI and telephony

| Item | Price | Label |
|---|---|---|
| Vapi platform fee | US$0.05 per min, plus pass-through STT, LLM, TTS | Observed (secondary), S31 |
| Vapi all-in | about US$0.08 to 0.13 per min typical; US$0.105 at 20k min per month | Observed (secondary), S31, S32 |
| Retell AI | US$0.07 to 0.31 per min; voice infrastructure US$0.055 per min; add-ons US$0.005 to 0.01 | Observed (secondary), S33 |
| Retell all-in | about US$0.110 per min at 20k min per month | Observed (secondary), S32 |
| ElevenLabs Agents | about US$0.08 to 0.10 per call minute; LLM billed separately; no telephony (bring Twilio or SIP); free 15 min; Creator US$11, Pro US$99 per month | Observed (secondary), S34, S35 |
| Twilio AU local number | US$3.00 per month; inbound US$0.01 per min | Observed, S36 (page date unconfirmed) |
| Twilio AU mobile number | US$20.00 per month; inbound US$0.05 per min | Observed, S36 |
| Twilio outbound to AU mobile | US$0.075 per min (voice); SIP trunk US$0.071 | Observed, S36, S37 |
| Twilio AU SMS number | US$6.50 per month | Observed, S38 |

**Assumption:** Twilio requires an Australian regulatory bundle (business name, address, likely ABN) before AU numbers are issued. Not verified this session; check before promising a go-live date.

Per-minute arithmetic for an inbound AI receptionist, Vapi, Australian local number: US$0.12 (assumption, mid of observed range) + US$0.01 inbound = US$0.13 = **A$0.20 per minute**. A client with 300 minutes a month costs A$60 in usage plus A$4.65 for the number.

### 1.7 Forms, scheduling, digital product checkout

| Item | Price | Label |
|---|---|---|
| Tally Free | Unlimited forms and submissions within fair use; Tally branding; Pro US$29 | Observed (secondary), S29 |
| Cal.com | Individual free tier disputed by sources (may be trial only); Teams US$12 to 15 per user | Observed (secondary), S30 |
| Google Calendar appointment schedules | Included in existing Workspace | Assumption (plan level not checked) |
| Lemon Squeezy (merchant of record) | 5% + 50c, plus about 1.5% international; no monthly fee; handles global sales tax | Observed (secondary), S39 |
| Polar (merchant of record) | 4% + 40c or 5% + 50c (changed May 2026, sources conflict); fees not refunded on refunds | Observed (secondary), S41 |
| Gumroad | 10% + 50c direct; 30% via Discover marketplace | Observed (secondary), S40 |

### 1.8 Minimum viable monthly stack cost (AUD ex GST)

All three assume Google Workspace, GitHub, Notion, Canva and Claude Code are already paid for (given). "Lean" is what to run during the 90-day test. "Ready" is the configuration at about 20 paying customers.

**(a) B2B SaaS**

| Line | Lean | Ready | Basis |
|---|---|---|---|
| Vercel Pro (Hobby is non-commercial) | 31.00 | 31.00 | S4 |
| Supabase | 0.00 (Free, daily cron keeps it awake) | 38.75 (Pro) | S6 |
| Domain (.com.au, A$20 per year) | 1.67 | 1.67 | Assumption |
| Transactional email | 0.00 (Resend Free) | 31.00 (Resend paid) | S19 |
| Claude API | 16.00 | 68.00 | Lean: 20 customers x 200 tasks, 80% Haiku 5.5, 20% Sonnet 5.5 = 20 x (160 x 0.00055 + 40 x 0.011) = US$10.56. Ready: all Sonnet 5.5 = 20 x 200 x 0.011 = US$44 |
| Forms and booking | 0.00 | 0.00 | Tally Free, Workspace calendar |
| **Fixed subtotal** | **48.67** | **170.42** | |
| Payments (variable) | 2.6% on a A$99 plan | same | 1.2 arithmetic |
| Cold email add-on if outbound is the channel | 86.00 | 86.00 | 1.4 |

**(b) AI voice agent service** (inbound receptionist, per client 300 min per month, assumption)

| Line | 1 client | 3 clients | Basis |
|---|---|---|---|
| Vercel Pro (dashboard, webhooks) | 31.00 | 31.00 | S4 |
| Supabase Free | 0.00 | 0.00 | S6 |
| Domain | 1.67 | 1.67 | Assumption |
| Twilio AU local number, per client | 4.65 | 13.95 | S36 |
| Voice platform all-in, US$0.12 x 300 min | 55.80 | 167.40 | S31, S32 (assumed midpoint) |
| Twilio inbound, US$0.01 x 300 min | 4.65 | 13.95 | S36 |
| **Total** | **97.77** | **227.97** | |
| Marginal cost per client | about A$65 a month | | Price must clear A$65 plus support time |

Outbound calling adds US$0.075 per min to mobiles and triggers Do Not Call Register rules (section 4). ElevenLabs at US$0.08 plus LLM may be cheaper; test both on the same script.

**(c) Digital product shop**

| Line | Lean (MoR hosted store) | Own storefront | Basis |
|---|---|---|---|
| Hosting | 0.00 (Lemon Squeezy or Polar store page) | 31.00 (Vercel Pro) | S39, S4 |
| Domain | 1.42 (.com) | 1.42 | Assumption |
| Payments | 5% + 50c (+1.5% intl); MoR handles overseas VAT and GST | 1.65% + 30c domestic, 3.5% + 30c intl, plus our own tax compliance | S39, S9 |
| Delivery and email | 0.00 (MoR file delivery, Resend Free) | 0.00 | S19 |
| Claude API for product creation | 10.00 | 10.00 | Assumption |
| **Fixed subtotal** | **11.42** | **42.42** | |

**Budget fit (arithmetic):** A$500 over 90 days is A$167 a month. SaaS lean plus cold email = 48.67 + 86 = A$134.67 a month, or A$404 over 3 months, leaving A$96 for ads or tests. Voice with one pilot client is A$98 a month (A$294 over 3 months) before any acquisition spend. A digital shop is A$11 to A$42 a month and leaves most of the cap for acquisition. **Rule (assumption):** pay monthly, never annual, in the first 90 days, even where annual is cheaper.

---

## 2. Reusable lead-to-support workflow map

Design rule: every step writes to one Supabase `events` table; anything a rule cannot resolve writes an `exceptions` row with a reason code. A daily Notion digest (built by a cron job with Claude summarising) shows open exceptions. Founders work the queue in two fixed 30-minute windows a week. Nothing else needs a human by default.

| Step | Mode | What runs | Human minutes per customer per month (assumption) | Exceptions and how they are handled |
|---|---|---|---|---|
| 1. Lead capture | Rules | Tally form or site form to Supabase via webhook; ABN Lookup JSON call to validate ABN, entity type, GST status and state (D1, D2); dedupe on ABN and email domain | 0 | Invalid ABN or free-mail domain: auto-tag low priority, no human |
| 2. Qualification | AI plus rules | Haiku 5.5 scores fit against a written rubric (about A$0.001 per lead); hard rules for must-haves (in Australia, sector, size); score over threshold goes to checkout link, under goes to nurture | 0.5 (borderline only, amortised) | Score in a grey band (say 40 to 60): queued for weekly review, batch of 10 takes about 5 min |
| 3. Sales | Rules plus AI, human approval early | Self-serve: pricing page and Stripe Payment Link or Checkout; AI drafts replies to inbound questions; first 20 replies human-approved, then auto-send for known question types | 3 once per new customer, falling to 1 after 20 customers | Custom pricing, procurement forms, contract changes: decline or standard terms only; anything bespoke is queued, not negotiated live |
| 4. Onboarding | Rules plus AI | Stripe webhook creates account; welcome sequence (Resend); intake form; Sonnet 5.5 generates the customer's configuration from intake answers; automated test run before go-live | 3 once (spot-check first 10 customers), then 1 | Intake missing data: auto-chase twice, then pause; failed test run: exception row, customer told "setting up, 2 business days" |
| 5. Delivery | AI with rules-based QA | Sonnet 5.5 (or Haiku for simple jobs) produces the output; rules check schema, length, banned claims list, citations present; outputs failing QA are retried once then queued; 5% random sample logged for review | 2 | QA fail after retry: exception row; regulated-niche outputs (health, finance, legal) always carry a disclaimer and are never auto-sent without passing the banned-claims filter |
| 6. Billing | Rules | Stripe Billing subscriptions, Smart Retries and dunning emails, automatic tax invoices (ABN shown), auto-pause service after final failed retry, auto-cancel after 30 days unpaid | 0.5 | Disputes and chargebacks: queued; respond with evidence pack generated by Claude; refund requests under A$50 within 14 days auto-approved (assumption threshold) |
| 7. Support | AI first line plus rules escalation | Help docs in the repo; Sonnet 5.5 answers support email from docs plus account data; escalate on: refund over threshold, legal or privacy words, complaint, low confidence, 2nd reply on same thread | 3 | Escalations queued with a drafted reply; published support SLA of 2 business days (in terms); outage: status page and templated notice |
| **Total steady state** | | | **about 9 minutes per customer per month, plus about 7 minutes once at onboarding** | |

**Capacity arithmetic.** 5 hours a week x 52 / 12 = 1,300 founder minutes a month. Assume half goes to build, acquisition, admin and the documentary (assumption), leaving 650 minutes for operations. At 9 minutes per customer: 650 / 9 = **about 72 customers** before the hour budget breaks. To serve 200 customers, minutes per customer must fall to about 3 (650 / 200 = 3.25). Levers: remove human approval in sales after 20 customers, raise the auto-refund threshold, move support to docs plus AI with a 5% audit, and choose a model whose delivery needs no human QA.

**Revenue per founder hour check (from brief).** At A$1,000 per founder hour and about 9 minutes per customer per month, each customer must bring in at least A$150 a month of operations-hour value just for their own servicing time, before build and sales hours. Low-ticket models (under A$50 a month) only work if minutes per customer fall below about 1. Flag for the Unit Economics specialist.

**What breaks first, and who fixes it (assumption)**

| Failure | Detection | Fix within 5 hours |
|---|---|---|
| Cold email domain burned (spam rate) | Daily bounce and reply-rate check; pause if bounce over 3% | Automated pause; rotate domain at next window |
| Supabase Free project paused | Daily health cron | Cron keeps it active; upgrade to Pro at first paying customer |
| Anthropic outage or rate limit | Error rate alarm | Queue and retry; fall back from Sonnet to Haiku; customers see "delayed", not "failed" |
| AI output error reaches a customer | Customer reply, QA sample | Kill switch per customer; human reviews within 2 business days; credit note policy |
| Card failures | Stripe dunning | Fully automated |
| Model cost spike | Daily spend report per customer | Hard per-customer token budget; auto-downgrade model when exceeded |
| Founder unavailable 2 weeks | No digest opened | Everything above is automatic; SLA in terms covers 2 business days only, so add a "holiday" banner flag (assumption) |

---

## 3. Lawful Australian data sources

Privacy note that applies to all rows: business-level data (ABN, entity name, licence status) is generally not personal information, but **sole trader names, director names, practitioner names, phone numbers and emails are personal information** under the Privacy Act 1988. Collecting from a public register does not make every use fair (APP 3.5, L5, L6). See 3.2.

### 3.1 Source table

| Source | Access method | Licence | Refresh and cost | Coverage | Reliability | Single-platform dependence | Label |
|---|---|---|---|---|---|---|---|
| ABR ABN Lookup web services | SOAP and JSON API with free GUID after accepting agreement (D1, D2) | Non-exclusive, non-transferable licence; extracts may be given to third parties at own risk; must not be misleading; ABR may suspend; listed CC BY 3.0 AU (D3) | Live; A$0 | Every ABN: entity name, type, status, GST, state, postcode, business names | High; "as is, as available" | High (one government API) but no commercial alternative needed | Observed, D1 to D3 |
| ABN bulk extract (data.gov.au) | Weekly file download | Not confirmed this session | Weekly; A$0 | All ABNs (public fields) | High | Low (files can be mirrored) | Licence unverified, assumption |
| ASIC Company dataset | data.gov.au CSV | CC BY 3.0 AU | Weekly (Tuesdays); A$0 | All companies: name, ACN, type, class, status, deregistration date | High; snapshot lags ASIC Connect | Low | Observed, D4 |
| ASIC Business Names dataset | data.gov.au CSV | CC BY 3.0 AU | Weekly (Wednesdays); A$0 | About 2.7M names, status, registration and cancellation dates, ABN | High | Low | Observed, D5 |
| ASIC AFS licensee, authorised representative, credit licensee, liquidator datasets | data.gov.au CSV | CC BY 3.0 AU (same publisher pattern) | Regular; A$0 | Financial services and credit licensees and reps (rep names are personal information) | High | Low | Observed, D6 (licence per dataset not individually checked) |
| AusTender contract notices | OCDS REST API (D7); auth requirement disputed by sources | Open data (licence not confirmed this session) | Near live; A$0 | Commonwealth contract awards and amendments since 2013; **no open tender (ATM) endpoint** | Medium; API counts lower than front end (D8) | Medium | Observed, D7, D8 |
| AusTender open tenders (ATMs) | Website and email alerts only | Site terms (not checked) | Live; A$0 | Commonwealth open tenders | Medium | High; no API, scraping risk | Observed gap, D7 |
| NSW buy.nsw | Website; Opportunities API is for agencies publishing, not public reading | Not confirmed | Live; all NSW open tenders mandated on buy.nsw from 1 Jan 2026 | NSW Government | Medium | High | Observed, D9 |
| VIC (Buying for Victoria), QLD (QTenders), other states | Portal and email alerts; no public API found | Site terms | Live | Each state | Medium | High; third-party scrapers exist, treat as terms risk | Observed gap |
| GrantConnect | Official RSS of current opportunities (D10); awards report updated daily (D11) | Commonwealth site terms (not checked) | Live; A$0 | Commonwealth grant opportunities, forecasts and awards (awards within 21 days) | High | Medium | Observed, D10, D11 |
| Grants Awarded Data (data.gov.au) | CSV | Not checked | **Stale: last updated 28 Oct 2024** | Awards from 2017 | Low (stale) | Low | Observed, D12 |
| NDIS Commission provider register | Web search; CSV downloads for SIL providers and digital platforms; full register CSV not confirmed (D13) | Site terms (not checked) | Refresh date shown on page; A$0 | Registered NDIS providers (unregistered providers absent) | Medium | High | Observed, D13 |
| NDIS compliance actions | data.gov.au CSV | Not checked | Periodic | Banning orders and compliance actions from Register Part 2 (individual names are personal and sensitive in context) | High | Low | Observed, D14 |
| ACECQA National Registers | CSV export of services and providers, national and by state (D16) | **All rights reserved; no use to compete with or displace ACECQA's market; no sub-licensing without written consent** (D17) | Daily; A$0 | About 18,000 approved education and care services and their providers | High | High | Observed, D16, D17 |
| GEN aged care service list | XLSX by state and national | Free to use subject to attribution; older releases barred sub-licensing and charging for access (D19) | **Annual** (30 June 2025 list released 7 Oct 2025); A$0 | Commonwealth-subsidised aged care services | High but slow | Low | Observed, D18, D19 |
| Aged Care Quality and Safety Commission Provider Register | Excel download (from Nov 2025) | Not checked | Periodic | Registered providers under Aged Care Act 2024 | High | Medium | Observed, D20 |
| AHPRA practitioner register | Public search free; bulk extract under data agreement | Agreement terms; no AHPRA branding | **A$2,000 per board per extract** | All registered health practitioners (personal information) | High | High | Observed, D21 |
| ABS Data API | SDMX REST, no key | Licence not stated on pages read; Indicator API is fee-free licence (D23); ABS data commonly CC BY 4.0 (secondary) | Per release; A$0 | Census, economy, business counts by industry and region | High, but API in Beta "availability not guaranteed" | Low | Observed, D22, D23 |
| NSW Planning Portal Online DA Data API | API, open dataset (D24); subscription key may be required | CC BY | Daily; A$0 | All DAs lodged on the NSW portal since Jan 2019 (incomplete before 1 Jul 2021); no applicant names per secondary source | High; actively maintained (D25) | Medium | Observed, D24, D25 |
| Other council DA data (VIC, QLD, etc.) | Council ePathway portals, varied | Usually site terms; many restrict automated access | Varies | Fragmented, 500+ councils | Low | High | Assumption |
| Google Places API (New) | Paid API with free monthly calls per SKU: Essentials 10k, Pro 5k, Enterprise 1k (D27); Text Search Pro about US$32 per 1,000 beyond free (D29, secondary) | **Google Maps terms: only place_id may be stored indefinitely; lat/lng cached max 30 consecutive days; other content (names, phones, ratings, reviews) not cacheable** (D26, D28) | Per call | Most AU businesses with a Google listing | High | **Very high**; you cannot build a durable owned database from it | Observed, D26 to D29 |
| ACNC Charity Register | data.gov.au weekly file | Believed CC BY | Weekly; A$0 | About 60,000 registered charities | High | Low | Assumption (not verified this session) |
| PlanningAlerts (OpenAustralia Foundation) | API | Believed paid licence for commercial use | Daily | National DA aggregation | Medium | High | Assumption (not verified this session) |

**Where an advantage could come from (assumption).** The open, CC BY, weekly business registers (ABR, ASIC companies, business names, AFS and credit licensees, ACNC) can be joined on ABN and ACN into an owned dataset with no single-platform risk and no licence fee. Combining that join with live triggers (new business name registrations, new AFS authorised representatives, NSW DAs, Commonwealth contract awards, grant openings) gives timely, lawful lead signals for B2B outreach. ACECQA and Google Places data cannot be resold or stored as a database, so they suit lookups inside a service, not a data product.

### 3.2 Privacy Act and scraping risk

- **Small business exemption (observed, L1, L2):** businesses under A$3m turnover stay outside the Privacy Act under the 31 Aug 2026 tranche 2 exposure draft. **But (assumption from Privacy Act s6D, not re-fetched this session):** the exemption does not apply to a small business that discloses personal information to anyone else for a benefit, or collects it from anyone else for a benefit (trading in personal information), or that provides a health service. **Any lead-list or data product that sells or supplies personal information makes LL Collective an APP entity regardless of size.** Plan to comply with all APPs from day one.
- **Scraping (observed, L5, L6):** the OAIC says publicly available is not the same as fair to collect (APP 3.5). In the Property Lovers determination, collecting personal information in breach of a website's terms breached APP 3.5. Treat any scraping against a site's terms as both a terms breach and a privacy breach.
- **ADM transparency (observed, L3, L4):** from **10 Dec 2026**, APP entities must say in their privacy policy when a computer program makes or substantially informs decisions that significantly affect individuals. AI lead scoring of businesses is probably outside this; AI decisions about consumers (eligibility, pricing, service refusal) are inside it.
- **Data minimisation rule (assumption):** store business-level fields; store a person's name and work email only when needed for the service; never store home addresses, personal mobiles or sensitive information from registers.

---

## 4. Risks

### 4.1 AI output liability in regulated niches

| Niche | Rule | Implication | Label |
|---|---|---|---|
| Health (incl. NDIS, aged care clinical) | TGA regulates software by intended medical purpose; chatbots giving diagnostic or treatment recommendations can be medical devices needing ARTG inclusion; SaMD a 2026/27 enforcement priority; 8 of 12 AI scribe products reviewed in Oct 2026 likely devices | Avoid any clinical recommendation function; admin, rostering, compliance paperwork and transcription-only are lower risk | Observed (secondary), L14, L15 |
| Financial services | Personal financial product advice needs AFSL authorisation; AI is not exempt | Avoid personal advice; general information only, with warnings | Observed (secondary), L17 |
| Any consumer or business-facing chatbot | A chatbot's false statements are the deploying business's conduct under the ACL; disclaimers do not fully protect; ACL penalties up to the greater of A$50m or 30% of turnover (secondary) | Keep AI within a narrow, documented scope; log every output; human-review anything that states legal rights, prices or warranties | Observed (secondary), L16, L18 |
| Legal services | Unqualified legal practice rules (state legal profession laws) | Do not offer legal advice; templates and information only | Assumption (not researched this session) |

### 4.2 Australian Consumer Law for digital products and subscriptions

- Consumer guarantees apply to digital products and subscriptions; "no refunds" statements cannot exclude them (observed, secondary, L13). Change-of-mind refunds can be excluded, guarantee failures cannot.
- ACCC v eHarmony [2026] FCA 1208 (25 Aug 2026): misleading pricing, auto-renewal and cancellation practices (observed, secondary, L11). Proposed unfair trading practices laws target subscription traps and drip pricing (L12, status to check).
- Card surcharging is disabled on Stripe from 1 Oct 2026 (S11): display one all-in price.
- **Design rules (assumption):** one-click cancel in the customer portal; renewal reminder email 7 days before annual renewals; price shown GST-inclusive to consumers; refund policy that quotes the consumer guarantees; standard form B2B contracts reviewed for unfair contract terms (small business customers are protected too).

### 4.3 Outreach law (affects every cold-start channel)

- **Spam Act 2003:** commercial email needs consent, sender identification and a working unsubscribe. Inferred consent for B2B relies on an address being conspicuously published, with no "no spam" statement, and the message being relevant to the person's role (observed, secondary, L8, L9). ACMA is actively enforcing: SpinTel paid A$653k (Nov 2026), and over A$11m in spam penalties in 18 months (L7). **Assumption:** only email addresses published by the business itself, role-relevant messages, unsubscribe honoured within 5 business days, full suppression list in Supabase.
- **Do Not Call Register and Telemarketing Industry Standard 2017:** apply to AI voice outbound calls the same as human calls; inbound AI receptionists are outside them (observed, secondary, L10). An AI voice business should be inbound-only unless DNCR washing and calling-hour rules are built in.
- **Call recording (assumption):** state surveillance and listening device laws vary; the AI agent should announce recording and AI use at the start of every call.

### 4.4 APP privacy obligations (if an APP entity)

Assumption list, to verify with the OAIC's APP guidelines before launch: APP 1 privacy policy (plus ADM content from 10 Dec 2026); APP 5 collection notices on every form; APP 6 use only for the purpose collected; APP 7 direct marketing opt-out; APP 8 cross-border disclosure (Anthropic, Vercel, Supabase, Stripe all process data overseas unless regions are set: choose Supabase Sydney region, note Claude's global routing); APP 11 security and deletion; Notifiable Data Breaches scheme (30 days to assess). Statutory tort for serious invasions of privacy is in force (assumption, from 2025).

### 4.5 AI model cost blowouts

| Risk | Control | Label |
|---|---|---|
| Runaway loops or agent retries | Per-request max tokens; max 2 retries; per-customer daily token budget held in Supabase and checked before each call | Assumption |
| Long prompts tip Haiku 5.5 into higher tier | Keep Haiku prompts under 100k tokens: over that, prices jump 5x (0.10 to 0.50 input) | Observed, S1 |
| Web search inside agents | US$10 per 1,000 searches plus result tokens re-billed on every later turn | Observed, S1 |
| Unpriced heavy users | Fair-use cap in terms; usage-based tier above it | Assumption |
| Voice minutes | Max call duration (say 10 minutes), silence timeout, per-client monthly minute cap with alert at 80% | Assumption |
| Using a top model by default | Route by task: Haiku 5.5 for classify and triage, Sonnet 5.5 for writing, Opus 5.5 only at build time; prompt caching (0.05x on Sonnet 5.5 cache hits) and Batch API (50% off) for non-urgent jobs | Observed prices S1; routing is assumption |
| Account-level surprise | Spend limit in the Anthropic console, daily cost report in the Notion digest, alert if any day exceeds 3x the 7-day average | Assumption |

**Cost to margin rule (assumption):** model plus voice costs must stay under 15% of the customer's price. Example: a A$99 SaaS plan allows A$14.85 a month of AI cost, which is about 870 cached Sonnet 5.5 tasks (14.85 / 1.55 / 0.011 = 871 uncached). A voice agent at A$0.20 a minute needs a price of at least A$400 a month at 300 minutes (A$60 / 0.15).

---

## 5. Open questions (for Harbour, tagged with the decision they affect)

1. Is the existing Vercel account on Hobby or Pro? (Fixed cost line for every model; A$31 a month.)
2. Is there an ABN yet, and in which structure? (.com.au domain, Twilio AU numbers, invoices, privacy exemption analysis.)
3. Will the business supply any personal information (lead lists, contact data) to customers? (If yes, full Privacy Act compliance applies from day one regardless of turnover.)
4. Can this session's network be widened to vercel.com, supabase.com, stripe.com and the voice vendors' sites, so secondary prices can be confirmed from primary pages? (Confidence in section 1.)
5. Is founder approval likely for about A$86 a month of cold email infrastructure in the 90-day window? (Channel choice and validation budget.)

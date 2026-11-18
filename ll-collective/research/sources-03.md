# Sources 03: Automation, data and stack evidence

Compiled by Wren (Data and Automation specialist), 18 Nov 2026. All accessed 18 Nov 2026 unless noted.

**Method note.** This session's network blocked direct page fetches for vercel.com, supabase.com, stripe.com and support.stripe.com. Only platform.claude.com was read in full. All other figures come from web search result summaries, which mostly quote third-party pricing trackers and law firm commentary. Where a vendor's own page was not read, the entry is marked **(secondary)**. Before any spend, each secondary price should be re-checked on the vendor page (a 10-minute job once network access allows).

## Claude API

| ID | Source | URL | Notes |
|---|---|---|---|
| S1 | Anthropic, Pricing (developer docs), read in full | https://platform.claude.com/docs/en/about-claude/pricing | Primary. All model token prices, batch 50%, cache multipliers, web search US$10 per 1,000, US-only inference 1.1x, Haiku 5.5 over-100k pricing, free credits for new users |
| S2 | Claude pricing page (consumer and API tabs) | https://claude.com/pricing | Fetched; API table truncated, used only to confirm model families |

## Hosting, database, payments

| ID | Source | URL | Notes |
|---|---|---|---|
| S3 | Vercel docs, Hobby plan (secondary, via search) | https://vercel.com/docs/plans/hobby | Hobby free for personal, non-commercial use; paused on exceeding limits |
| S4 | Vercel docs, Pro plan (secondary, via search) | https://vercel.com/docs/plans/pro | US$20 per seat per month incl. US$20 usage credit |
| S5 | Modelence, Vercel pricing 2026 (secondary) | https://modelence.com/compare/vercel-pricing | 100 GB transfer and 1M edge requests on Hobby; 1 TB on Pro |
| S6 | Toolradar, Supabase pricing 2026 (secondary) | https://toolradar.com/blog/supabase-pricing-2026 | Free 500 MB DB, 50k MAU, 5 GB egress, 2 projects, pause after 7 days idle; Pro US$25 incl. US$10 compute credit, 100k MAU |
| S7 | Automation Atlas, Supabase free tier limits 2026 (secondary) | https://automationatlas.io/answers/supabase-free-tier-limits-2026/ | Corroborates S6 |
| S8 | Stripe support, Updates to card pricing in Australia from October 2026 (snippet only) | https://support.stripe.com/questions/updates-to-card-pricing-in-australia-from-october-2026 | Domestic fee cut from 1 Oct 2026; international changes from 1 Apr 2027 |
| S9 | Studio Ninja help, changes to card surcharges in Australia (secondary) | https://help.studioninja.co/en/articles/16651258-changes-to-card-surcharges-in-australia | Domestic 1.65% + A$0.30 from 1 Oct 2026 |
| S10 | Kajabi help, updates to card pricing in Australia (secondary) | https://help.kajabi.com/updates-to-card-pricing-in-australia-from-october-2026 | 0.05 percentage point domestic cut |
| S11 | Stripe support, Australia is removing card surcharges (snippet) | https://support.stripe.com/questions/australia-is-removing-card-surcharges-what-stripe-users-need-to-know | Surcharging disabled from 1 Oct 2026 |
| S12 | Wise AU, Stripe fees guide 2026 (secondary) | https://wise.com/au/blog/stripe-fees | International cards, currency conversion 2%, Billing 0.7% |
| S13 | Orb, Stripe Billing pricing (secondary) | https://www.withorb.com/blog/stripe-billing-pricing | Billing pay as you go 0.7% of billing volume |
| S14 | UsagePricing, Stripe Billing activity July 2026 (secondary) | https://usagepricing.com/blueprint/stripe-billing | Billing stays 0.7%; advanced usage billing moved to Metronome |

## Domains and email

| ID | Source | URL | Notes |
|---|---|---|---|
| S15 | auDA, Wholesale .au domain pricing | https://auda.org.au/registrar-resources/wholesale-au-domain-pricing | Wholesale A$9.50 ex GST from 1 Oct 2026 (was A$8.64) |
| S16 | auDA, Statement on .au wholesale price and quality program (Aug 2026) | https://files.auda.org.au/documents/Statement-.au-wholesale-price-and-quality-program.pdf | As above |
| S17 | Sprintlaw, new .com.au eligibility rules | https://sprintlaw.com.au/articles/new-com-au-domain-eligibility-rules-what-australian-businesses-need-to-know/ | ABN/ACN/trade mark connection required |
| S18 | Register.Domains, .com.au eligibility change | https://register.domains/en/blog/com-au-domain-eligibility-rules-change | Renewal blocked if linked ABN/ACN inactive (from May 2026) |
| S19 | Automation Atlas, Resend pricing 2026 (secondary) | https://automationatlas.io/answers/resend-pricing-explained-2026/ | Free 3,000 per month, 100 per day; paid from US$20 for 50k |
| S20 | Automation Atlas, Postmark pricing 2026 (secondary) | https://automationatlas.io/answers/postmark-pricing-explained-2026/ | Free 100 per month; Basic US$15 for 10k |
| S21 | Costbench, Postmark vs Resend (secondary) | https://costbench.com/compare/postmark-vs-resend/ | Corroborates |
| S22 | Cleanlist, Smartlead pricing guide (1 Sep 2026, secondary) | https://www.cleanlist.ai/blog/2026-09-01-smartlead-pricing-guide | Base US$39, Pro US$94 monthly |
| S23 | Leadhaste, Instantly pricing 2026 (secondary) | https://leadhaste.com/blog/instantly-pricing-2026 | Growth US$37.60 per month on annual billing |
| S24 | Google Workspace AU business pricing | https://workspace.google.com/intl/en_au/business/ | Business Starter A$9.90 annual, A$11.80 flexible, ex GST |

## Automation, forms, scheduling

| ID | Source | URL | Notes |
|---|---|---|---|
| S25 | Toolradar, n8n pricing 2026 (secondary) | https://toolradar.com/blog/n8n-pricing-2026 | Cloud Starter about EUR 20 to 24, 2,500 executions |
| S26 | Sliplane, n8n pricing 2026 (secondary) | https://sliplane.io/blog/n8n-pricing | Self-host Community Edition free; Sustainable Use Licence limits hosting for others |
| S27 | Automation Atlas, Make vs Zapier 2026 (secondary) | https://automationatlas.io/answers/make-pricing-vs-zapier-cost/ | Make free 1,000 credits; Core about US$9 to 10.59; Zapier free 100 tasks; Professional US$19.99 to 29.99 for 750 tasks |
| S28 | Activepieces, Make pricing 2026 (secondary) | https://www.activepieces.com/blog/comparing-make-com-pricing-2026-plans-and-real-costs.md | Credits replaced operations 19 Jan 2026 |
| S29 | Jetadmin, Tally pricing (26 Sep 2026, secondary) | https://www.jetadmin.io/blog/tally-pricing/ | Free unlimited forms and submissions (fair use); Pro US$29 |
| S30 | Costbench, Cal.com free plan 2026 (secondary) | https://costbench.com/software/scheduling/cal-com/free-plan/ | Free individual tier disputed; Teams US$12 to 15 per user |

## Voice AI and telephony

| ID | Source | URL | Notes |
|---|---|---|---|
| S31 | Fora Soft, Vapi vs Retell vs custom (secondary, cites vapi.ai/pricing) | https://www.forasoft.com/blog/article/vapi-vs-retell-vs-custom | Vapi platform US$0.05 per min plus pass-through |
| S32 | Betonai, Vapi vs Retell vs Bland at 20,000 calls (Sep 2026, secondary) | https://betonai.net/?p=1872 | All-in about US$0.105 (Vapi) and US$0.110 (Retell) per min |
| S33 | Dupple, Retell AI pricing 2026 (secondary) | https://dupple.com/learn/retell-ai-pricing | US$0.07 to 0.31 per min; infra US$0.055 per min |
| S34 | Stork, ElevenLabs Agents pricing 2026 (secondary) | https://www.stork.ai/blog/elevenlabs-agents-pricing-2026 | About US$0.08 per call minute on paid plans; free 15 min; LLM billed separately; bring own telephony |
| S35 | Costbench, ElevenLabs plans (secondary) | https://costbench.com/software/ai-voice-tools/elevenlabs/ | Starter US$6, Creator US$11, Pro US$99 |
| S36 | Twilio Voice pricing, Australia | https://www.twilio.com/voice/pricing/au | Local number US$3.00 per month, inbound US$0.01 per min; mobile number US$20.00 per month, inbound US$0.05 per min; outbound to AU mobile US$0.075 per min. Date of page not confirmed |
| S37 | Twilio Elastic SIP Trunking pricing, Australia | https://twilio.com/en-us/sip-trunking/pricing/au | Different number rentals (local US$2.50); outbound AU US$0.0212, to mobile US$0.071 |
| S38 | Twilio SMS pricing, Australia | https://www.twilio.com/en-us/sms/pricing/au | SMS number US$6.50 per month |

## Digital product commerce

| ID | Source | URL | Notes |
|---|---|---|---|
| S39 | Dodo Payments, Lemon Squeezy review 2026 (secondary, competitor) | https://dodopayments.com/blogs/lemonsqueezy-review | 5% + 50c, international surcharge about 1.5% |
| S40 | Checkoutpage, Gumroad fees 2026 (secondary) | https://checkoutpage.com/blog/gumroad-fees | 10% + 50c direct; 30% via Discover |
| S41 | Polar docs, fees | https://polar.sh/docs/fees | Conflicting 4% + 40c vs 5% + 50c after May 2026 change |

## Australian data sources

| ID | Source | URL | Notes |
|---|---|---|---|
| D1 | ABR, Web Services Agreement | https://abr.business.gov.au/Tools/WebServicesAgreement | Free, GUID registration, non-exclusive licence, extracts to third parties at own risk, may be suspended |
| D2 | ABR, Web services and JSON services | https://abr.business.gov.au/Tools/WebServices ; https://abr.business.gov.au/json/ | SOAP and JSON methods |
| D3 | researchdata.edu.au listing of ABN Lookup web services | https://researchdata.edu.au/abn-lookup-web-services/3805072 | CC BY 3.0 AU |
| D4 | data.gov.au, ASIC Company Dataset | https://www.data.gov.au/data/dataset/asic-companies | CC BY 3.0 AU, weekly (Tuesdays) |
| D5 | data.gov.au, ASIC Business Names Dataset | https://data.gov.au/data/dataset/asic-business-names | CC BY 3.0 AU, weekly (Wednesdays), about 2.7M records |
| D6 | data.gov.au, ASIC AFS Licensee, AFS Authorised Representative, Credit Licensee, Liquidator datasets | https://data.gov.au/data/dataset/asic-afs-licensee | Same publisher pattern |
| D7 | AusTender OCDS API (GitHub) | https://github.com/austender/austender-ocds-api | Contract notices since 1 Jan 2013 in OCDS; no approach-to-market (open tender) endpoint |
| D8 | Open Contracting Partnership, Australia's open contracting data | https://www.open-contracting.org/2020/02/11/what-does-australias-open-contracting-data-look-like/ | Record count gap API vs front end (2020) |
| D9 | NSW Procurement Board Direction PBD-2025-04 | https://arp.nsw.gov.au/pbd-2025-04-procurement-board-direction-2025-04-mandate-for-the-publication-of-nsw-government-open-tender-opportunities-on-buy-nsw | All NSW open tenders on buy.nsw from 1 Jan 2026; Opportunities API is for agency publishing |
| D10 | GrantConnect RSS, current grant opportunity list | https://www.grants.gov.au/public_data/rss/rss.xml | Official live feed |
| D11 | GrantConnect help, awards by financial year | https://help.grants.gov.au//getting-started-with-grantconnect/information-made-easy/awards-by-financial-year/ | Updated daily |
| D12 | data.gov.au, Grants Awarded Data | https://data.gov.au/data/dataset/grants-awarded-data | Last updated 28 Oct 2024 (stale) |
| D13 | NDIS Commission, Find a registered provider | https://www.ndiscommission.gov.au/provider-registration/find-registered-provider | Search plus CSVs (SIL providers, digital platforms) |
| D14 | data.gov.au, NDIS Commission Compliance Actions | https://data.gov.au/data/en/dataset/ndis-commission-compliance-actions-23-02-2026/resource/2f39f38f-35d7-4ebf-8ba8-35ae97be75e8 | CSV derived from Provider Register Part 2 |
| D15 | NDIS data research, provider datasets | https://dataresearch.ndis.gov.au/datasets/provider-datasets | Aggregated counts only |
| D16 | ACECQA, National registers | https://www.acecqa.gov.au/resources/national-registers | CSV export of services and providers, updated daily |
| D17 | ACECQA, Terms of use | https://acecqa.gov.au/terms-of-use | All rights reserved; no use to compete with or displace; no sub-licensing without consent |
| D18 | GEN, Aged care service list 30 June 2025 | https://www.gen-agedcaredata.gov.au/resources/access-data/2025/october/aged-care-service-list-30-june-2025 | Annual XLSX, released 7 Oct 2025 |
| D19 | GEN, Aged care service information June 2019 (licence wording) | https://www.gen-agedcaredata.gov.au/resources/access-data/2019/july/aged-care-service-information-june-2019 | No sub-licensing or charging for access (older release) |
| D20 | ACQSC, Provider registration policy and register | https://www.agedcarequality.gov.au/resource-library/provider-registration-policy | Provider Register (Aged Care Act 2024) as Excel from Nov 2025 |
| D21 | AHPRA, National Register extract or copy | https://www.ahpra.gov.au/Registration/Employer-Services/External-data-exchange-services/National-Register-Copy-or-Extract.aspx | Extract fee A$2,000 per board per point in time; data agreement |
| D22 | ABS, Data API user guide | https://www.abs.gov.au/about/data-services/data-explorer/data-api-user-guide | SDMX API, Beta, availability not guaranteed |
| D23 | ABS, Indicator API terms of use | https://www.abs.gov.au/about/data-services/application-programming-interfaces-apis/indicator-api/terms-use | Fee-free licence |
| D24 | NSW Planning Portal, Online DA Data API | https://www.planningportal.nsw.gov.au/opendata/dataset/online-da-data-api | CC BY, daily, DAs lodged since Jan 2019 |
| D25 | NSW Planning Portal API release notes 25 Sep 2026 | https://www.planningportal.nsw.gov.au/sites/default/files/documents/2026/NSW%20Planning%20Portal%20-%20API%20release%20notes_25%20September%202026.pdf | API actively maintained |
| D26 | Google Maps Platform service specific terms (archive 10 Jun 2026) | https://cloud.google.com/archive/maps-platform/terms/maps-service-terms-20260610 | place_id cacheable; lat/lng max 30 days |
| D27 | Google Maps Platform pricing overview | https://developers.google.com/maps/billing/overview/ | Free calls per SKU per month: Essentials 10k, Pro 5k, Enterprise 1k |
| D28 | Open Places API blog, can you store Places results (secondary) | https://openplacesapi.com/blog/can-you-store-places-api-results | Only place_id indefinitely |
| D29 | Woosmap, Google Places API pricing 2026 (secondary) | https://www.woosmap.com/blog/google-places-api-pricing | Text Search Pro US$32 per 1,000 beyond free |

## Law and risk

| ID | Source | URL | Notes |
|---|---|---|---|
| L1 | Clayton Utz, Privacy Act tranche 2 exposure draft (Sep 2026) | https://www.cbp.com.au/insights/publications/privacy-amendment-(personal-data-protection)-bill-2026-exposure-draft-released-for-second-tranche-o | Exposure draft 31 Aug 2026; submissions closed 18 Sep 2026 |
| L2 | HSF Kramer, draft tranche 2 reforms (Sep 2026) | https://www.hsfkramer.com/en_US/insights/2026-09/the-draft-tranche-2-privacy-act-reforms-whats-there-whats-new-and-whats-missing | Small business exemption not removed |
| L3 | OAIC, new resources on ADM transparency (30 Sep 2026) | https://www.oaic.gov.au/news/media-centre/new-resources-on-transparency-for-use-of-ai-and-automated-decision-making | ADM privacy policy obligation from 10 Dec 2026 |
| L4 | Allens, ADM transparency APP 1 amendments (Jun 2026) | https://www.allens.com.au/insights-news/insights/2026/06/automated-decision-making-transparency-what-app-entities-need-to-know-about-the-app-1-amendments/ | APP 1.7 to 1.9 |
| L5 | FPF, OAIC dual AI guidelines (Oct 2024) | https://fpf.org/blog/oaics-dual-ai-guidelines-set-new-standards-for-privacy-protection-in-australia/ | Public availability is not permission; APP 3.5 fairness |
| L6 | DLA Piper, when data scraping breaches the Privacy Act (Sep 2025) | https://privacymatters.dlapiper.com/2025/09/australia-scraping-the-barrel-when-data-scraping-breaches-the-privacy-act/ | Property Lovers determination: collection in breach of site terms breached APP 3.5 |
| L7 | ACMA, SpinTel pays $653K penalty (Nov 2026) | https://www.acma.gov.au/articles/2026-11/spintel-pays-653k-penalty-spamming-former-customers | Active Spam Act enforcement |
| L8 | Sparke Helmore, ACMA raises stakes for business messaging | https://www.sparke.com.au/insights/spam-in-the-spotlight-acma-raises-the-stakes-for-business-messaging/ | Express consent preferred |
| L9 | Spam Act 2003 (legislation.gov.au) | https://www.legislation.gov.au/C2004A01214/2016-03-10/2016-03-10/text/original/epub/OEBPS/document_1/document_1.html | Consent, identify, unsubscribe |
| L10 | Do Not Call Register, industry overview | https://www.donotcall.gov.au/industry/industry-overview | DNCR Act and Telemarketing Industry Standard 2017 |
| L11 | Clayton Utz, ACCC v eHarmony [2026] FCA 1208 (Sep 2026) | https://www.claytonutz.com/insights/2026/september/subscription-traps-under-the-spotlight-federal-court-finds-eharmony-misled-consumers-on-pricing-auto-renewal-and-cancellation | Subscription pricing, renewal and cancellation misleading |
| L12 | Clayton Utz, draft unfair trading practices laws (Feb 2026) | https://claytonutz.com/insights/2026/february/dark-patterns-online-traps-and-confirm-shaming-new-draft-consumer-laws-on-subscription-practices-and-drip-pricing | Subscription cancellation and drip pricing reforms |
| L13 | Sprintlaw, digital product refund policy | https://sprintlaw.com.au/articles/digital-product-refund-policy/ | Consumer guarantees apply to digital products |
| L14 | Clayton Utz, TGA clarifies when AI is a medical device (Jul 2026) | https://www.claytonutz.com/insights/2026/july/healthcare-software-tga-clarifies-when-ai-will-be-regulated-as-a-medical-device | Intended purpose test; SaMD a 2026/27 enforcement priority |
| L15 | Pure Global, TGA digital scribes review (Oct 2026) | https://www.pureglobal.com/news/australia-tga-digital-scribes-review-guidance-2026 | 8 of 12 scribe products likely devices |
| L16 | Lander and Rogers, chatbots and consumer law risks | https://landers.com.au/legal-insights-news/chatbots-on-the-front-line-consumer-law-risks-businesses-cant-ignore | Chatbot hallucinations can be the business's misleading conduct |
| L17 | Mills Oakley, AI and financial advice chatbots | https://www.millsoakley.com.au/insights/advice-and-ai-in-the-age-of-aging-part-2-ai-and-financial-advice-live-chatbots-virtual-call-centres-and-virtual-advisers/ | Personal advice needs AFSL authorisation |
| L18 | ACS Information Age, businesses liable for AI chatbot mistakes (2024) | https://ia.acs.org.au/article/2024/businesses-liable-for-ai-chatbot-mistakes.html | Air Canada chatbot ruling |

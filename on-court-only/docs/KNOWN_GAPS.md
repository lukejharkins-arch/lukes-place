# Known gaps and blockers (honest status, 2026-11-05)

## Environment blockers (this build session)
- **Network policy:** direct page loads were refused for marketplaces (eBay, Grailed, Depop, Vinted, Mercari, Poshmark, Etsy, Gumtree, Facebook), nba.com, university athletics sites, Wikipedia, IP Australia, ABF and legislation.gov.au. Research used search-engine extracts only. To fix: allow those domains in the environment's network settings, or run the hunter from the founder's own machine.
- **Search budget:** the shared limit of about 200 web searches per turn was exhausted. NCAA current Australian rosters, 12 NBA team contact routes, staff directories and licensing offices were not reached.

## Therefore
- 0 VERIFIED_CONTACT records (77 researched official routes, 53 unverified leads).
- 0 qualified daily opportunities: the 9 priced real leads (plus 11 unpriced) were seen only in search extracts and show no authentication evidence.
- Sold comparables are unconfirmed, so no resale value is asserted for any real lead.
- Demand scores are about 12-20% measured; the rest is estimate.

## Product gaps
- No Shopify adapter yet (needs a store and API credentials).
- No email sending (by design) and no email verification or password reset.
- No rate limiting or admin 2FA; run behind a reverse proxy before any public deployment.
- No image upload pipeline for real item photos (media rows accept URLs).
- Collector Exchange peer listings are not open; only the consignment intake and seller tiers are live.
- Automated schedule written (GitHub Actions) but not active until merged to the default branch.

## Founder decisions needed
1. Approve or adjust the 5 outreach drafts and confirm each route on the live page.
2. Allow marketplace domains or run the hunter locally; then approve any purchase line.
3. Choose the trade mark filing and legal review (questions in `docs/LEGAL_RESEARCH.md`).
4. Shopify account and Payments onboarding when ready.

# Claude vs Codex | objective comparison framework

**Status of the comparison:** only the Claude column is filled. I have **not** inspected a Codex implementation. The supplied zip (`reference/codex_pack/`) is the business handoff pack prepared *for* Codex (brief, agent scopes, research templates and a 6.6 KB static HTML prototype marked "not a commerce backend"). It is not Codex's output, so no Codex scores are recorded and no winner is declared.

To complete it: run `tests/COMPARISON_TEST_PLAN.md` against both repositories at the same date and fill the Codex column from that evidence.

## Scoring
Each criterion is scored 0-5 against the evidence listed, by a reviewer who did not build either project. 0 = absent, 1 = claimed but not demonstrable, 3 = working with clear gaps, 5 = working, tested and verified against primary sources. Weighted total out of 100.

| # | Criterion | Weight | Evidence to inspect | Claude delivered (2026-11-05) | Claude self-score (to be re-scored independently) | Codex |
|---|---|---|---|---|---|---|
| 1 | Research accuracy | 6 | Spot-check 20 random facts against primary pages | 595 cited source rows; every player row sourced; facts graded VERIFIED/PARTIAL/UNVERIFIED; page loads blocked, so extracts only | 3 | – |
| 2 | Verified NBA contacts | 6 | Contacts confirmed on the live official page with date | 0 verified; 18/30 teams with a researched official route; 12 teams with none | 1 | – |
| 3 | Verified NCAA contacts | 4 | Same, for programmes | 0 verified; 21/50 with a researched surplus or property route | 1 | – |
| 4 | Australian player connections | 5 | Count, sourcing, correctness of current vs former | 39 players, 94 stints; 9 current 2026-27 NBA Australians cross-sourced; 8 Australian NBA champions recorded, each with a source and graded verification; NCAA current rosters not reached; MSU Denver correctly Division II | 3 | – |
| 5 | Actual wholesale opportunities | 6 | Named suppliers with real access and published routes | 37 channels; 10 deep-dive targets with routes and specific questions; no terms obtained (no outreach sent) | 2 | – |
| 6 | Genuine qualified daily opportunities | 6 | Live URLs, seen prices, evidence, verified comps | **0 qualified**; 20 real leads found (9 priced) from search extracts; none live-verified; shortfall reported, not filled | 1 | – |
| 7 | Functioning features | 8 | Click through every storefront and admin feature | All brief §11 features working except checkout (blocked by design until credentials) | 4 | – |
| 8 | Website design quality | 5 | Desktop and 390 px screenshots, accessibility basics | Two complete visual systems; responsive with no horizontal scroll at 390 px; original illustrations | 4 | – |
| 9 | Era switching | 4 | Toggle changes identity without breaking navigation; per-product era skin | Header switch, persisted; tokens swap; products keep their own era skin | 5 | – |
| 10 | Product storytelling | 4 | Left/right comparison, three reference levels, museum plaque | Exhibit pages with team, era, player connection, design, rarity, value, provenance, custody, "claims / does not claim" | 4 | – |
| 11 | Authentication standards | 6 | Rules enforced in code; over-claims blocked | Evidence-derived classes, blocking flags, copy linter, media rules; 15 unit tests | 5 | – |
| 12 | Database structure | 4 | Schema covers all registers with integrity | 29-table SQLite schema, single source of truth, audit log | 4 | – |
| 13 | Agent automation | 6 | Agents run, log metrics, do real work | 12 agents (11 + General Manager) run end to end, metrics in `agent_runs`; Claude Code subagent definitions | 4 | – |
| 14 | Ecommerce readiness | 5 | Path to real checkout | Shopify-first decision with an integration design; adapter not built (no credentials) | 2 | – |
| 15 | Marketplace capabilities | 3 | Seller onboarding, consignment, moderation | Consignment state machine, seller tiers, moderated wanted board; peer listings deliberately not open | 3 | – |
| 16 | Running costs | 3 | Monthly cost to operate | About A$71/month (Shopify Basic + consignment app) plus hosting for the app; zero dependencies | 4 | – |
| 17 | Deployment complexity | 3 | Steps from clone to running | 3 commands, no installs | 5 | – |
| 18 | Security | 4 | Auth, CSRF, CSP, traversal, secrets | PBKDF2, HttpOnly SameSite cookies, CSRF header, CSP, body cap, no secrets; no rate limit or 2FA yet | 3 | – |
| 19 | Code quality | 3 | Tests, structure, readability | 63 automated tests passing; domain modules separated | 4 | – |
| 20 | Maintainability | 3 | Docs, ADRs, assumptions register | ADRs, assumptions, gaps, requirement traceability | 4 | – |
| 21 | Launch readiness | 6 | 30 gate-passed products | 0/30 (no stock, no agreements, by design) | 1 | – |

## What Claude actually delivered
- Working app: `server.py` + `storefront/` (two eras), 29-table database, 12-agent runner, 4 report cadences, 63 tests.
- Research registers: 30 NBA franchises, 50 NCAA programmes, 39 Australian players, 37 channels, 130 contact records (0 verified, 77 researched routes, 53 unverified leads), demand ranking of 80 organisations.
- 5 outreach drafts (unsent), legal research, platform evaluation, financial model, brand film, campaign, social plan.

## What Claude did not deliver
Verified contacts, live-verified opportunities, supplier terms, any purchase, any outreach sent, a deployed store, or an active schedule. Blockers are in `docs/KNOWN_GAPS.md`.

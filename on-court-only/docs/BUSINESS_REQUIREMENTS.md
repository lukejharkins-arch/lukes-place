# Business requirements and traceability

Source: the founder's brief (this session) plus the supplied pack (`reference/codex_pack/`), treated as **business requirements only**. Technical design is independent (see `ARCHITECTURE_DECISIONS.md`).

Status key: **DONE** working and tested · **PARTIAL** built but limited by evidence or access · **BLOCKED** needs a founder action or external access · **PLANNED** documented, not built.

## Non-negotiables
| # | Requirement | Where | Status |
|---|---|---|---|
| N1 | No purchasing, costs, external messages, contracts or public launch without founder approval | No send, buy or publish functions exist; budget lines need a named founder approval; outreach approval needs a founder name | DONE |
| N2 | Inventory acquisition strictly under A$2,000 including freight | `operations/budget.py` (checked at proposal and approval) + tests | DONE |
| N3 | 30 launch products: 8 owned, 17 consignment, 5 partner | `launch_slots`, `operations/launch.py` gate; 0/30 ready (no stock yet) | DONE (tracker) / BLOCKED (stock) |
| N4 | Authentic on court = verified team issue; six classes; never confuse issued and worn | `authentication/rules.py`, 15 unit tests | DONE |
| N5 | Every product has a transparent provenance record | `evidence`, `custody_events`, exhibit page | DONE |
| N6 | Never fabricate opportunities, contacts, demand statistics or results | Engine never fills the target; contacts tiered; demand factors tagged MEASURED or ESTIMATE | DONE |
| N7 | Demo data clearly identified; nothing shown as for sale without stock or authority | Site banner, DEMO badges, `can_purchase()`, checkout refuses | DONE |

## Workstreams
| Brief § | Requirement | Implementation | Status |
|---|---|---|---|
| 3 | Two-era design system with working switcher; products keep their own era styling | `storefront/styles.css` tokens; `.skin-og` / `.skin-current`; header toggle (persisted) | DONE |
| 3 | Accurate team, player and manufacturer naming; no copied logos | Title convention; original SVG illustrations; brand rules | DONE |
| 3 | Research nominative use, parallel imports, IP | `docs/LEGAL_RESEARCH.md` (s122A, ACL, copyright, imports, GST, PPSA, Spam Act) | PARTIAL (search extracts; lawyer questions listed) |
| 4 | Tearaway Vault, construction guide, comparisons, archive, campaign | `#/vault` page with synthesised snap sound; `marketing/LAUNCH_CAMPAIGN_REMEMBER_THE_SOUND.md` | DONE |
| 5 | Global sourcing intelligence; MeiGray and comparable businesses | 37 channels, 10 deep-dive targets (`research/RESEARCH_SUMMARY.md`) | PARTIAL |
| 5 | Undervalued search system, terminology, misspellings | `sourcing/search_framework.py`, daily `search_plan_<date>.md` | DONE |
| 6 | Demand-scoring model; ranked NBA and NCAA list; measured vs estimate | `sourcing/demand.py`; `research/sourcing_priority_ranking.csv` | DONE (model) / PARTIAL (mostly estimates) |
| 7 | Australian connection database | 39 players, 94 stints, all with sources (`research/australian_player_register.csv`) | PARTIAL (NCAA current rosters not reached) |
| 7 | Saint Mary's and MSU Denver verified | SMC alumni sourced; MSU Denver confirmed Division II with no verified Australian link | DONE |
| 7 | Individually researched outreach drafts | 5 drafts in `outreach/drafts/` using sourced facts only | DONE |
| 8 | 12 agents with instruction files, objectives, shared DB, boundaries; real workflows | `agents/*.md`, `agents/run.py`, `.claude/agents/` | DONE |
| 9 | 20 qualified opportunities daily with all fields; report actual count | `sourcing/engine.py`; daily report: **0 qualified** of 9 real leads | DONE (engine) / BLOCKED (marketplace access) |
| 10 | Persistent CRM covering 30 NBA and NCAA programmes, all fields, fortnightly follow-ups | `contacts`, `relationships`, `outreach_messages`, `outreach/crm.py`, `outreach/crm_register.csv` | DONE |
| 11 | Platform evaluation and recommendation | `docs/PLATFORM_EVALUATION.md`, `commerce/ECOMMERCE_ARCHITECTURE.md` | DONE |
| 11 | Storefront features (full list) | See ecommerce architecture "What is built" | DONE (checkout BLOCKED on credentials) |
| 12 | Left/right storytelling with three reference levels | Exhibit page; `check_media()` rules | DONE |
| 13 | 12 departments | `commerce/catalogue.py` DEPARTMENTS + Locker Room | DONE |
| 14 | Brand film: screenplay, storyboard, production, social cuts | `marketing/BRAND_FILM_THE_OTHER_SIDE_OF_THE_GLASS.md` | DONE |
| 15 | Finances: software, marketing, operations, GST, cash | `operations/FINANCIAL_MODEL.md` | DONE (estimates flagged) |
| 16 | Repository structure and 18 artefacts | This repo (`README.md` maps each) | DONE |
| 17 | Daily, weekly, fortnightly, monthly reports; scheduling only when real | `reports/generate.py`; GitHub Actions workflow written but **not active** until merged | PARTIAL |
| 18 | Claude vs Codex comparison framework and test plan | `CLAUDE_VS_CODEX_COMPARISON.md`, `tests/COMPARISON_TEST_PLAN.md` | DONE |

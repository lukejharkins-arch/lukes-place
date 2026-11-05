# ON COURT ONLY

**Where basketball love meets authentic on-court wear.** Genuine team-issued NBA and NCAA equipment for Australian collectors, with the evidence behind every claim.

This is Claude Code's independent build: a working storefront with two design eras, a provenance-first database, a sourcing and authentication engine, a supplier CRM, a 12-agent team and reports. The supplied Codex pack is kept in `reference/codex_pack/` as business requirements only.

> **Pre-launch.** Every product is a labelled demo exhibit. Nothing is for sale, nothing has been bought, no one has been contacted, and nothing is deployed.

## Run it (Python 3.11+, nothing to install)
```bash
cd on-court-only
python3 -m commerce.seed --reset        # build data/oco.db (admin password -> data/ADMIN_CREDENTIALS.local)
python3 -m agents.run all               # 12-agent cycle
python3 -m reports.generate all         # daily / weekly / fortnightly / monthly
python3 server.py --port 8080           # http://127.0.0.1:8080, admin at #/admin
python3 -m unittest discover -s tests -t .   # 63 tests
```

## Where the 18 required artefacts are
| # | Artefact | Location |
|---|---|---|
| 1 | Full business requirements | `docs/BUSINESS_REQUIREMENTS.md` (with traceability) |
| 2 | NBA team register | `research/nba_team_register.csv` (30 franchises) |
| 3 | NCAA programme register | `research/ncaa_programme_register.csv` (50 programmes) |
| 4 | Australian player register | `research/australian_player_register.csv` (39 players) |
| 5 | Sourcing channel directory | `sourcing/channel_directory.csv` (37 channels) |
| 6 | Supplier contact CRM | `outreach/crm_register.csv`, admin CRM tab, `outreach/crm.py` |
| 7 | Daily deal opportunity engine | `sourcing/engine.py`, `reports/daily/` |
| 8 | Authentication schema | `authentication/AUTHENTICATION_SCHEMA.md`, `authentication/rules.py` |
| 9 | Product and inventory model | `commerce/PRODUCT_INVENTORY_MODEL.md`, `data/schema.sql` |
| 10 | Consignment management process | `operations/CONSIGNMENT_PROCESS.md`, `operations/consignment.py` |
| 11 | Ecommerce architecture | `commerce/ECOMMERCE_ARCHITECTURE.md`, `docs/PLATFORM_EVALUATION.md` |
| 12 | Functioning storefront | `storefront/` + `server.py` |
| 13 | Brand identity system | `brand/BRAND_IDENTITY.md`, `storefront/styles.css` |
| 14 | Social content plan | `marketing/SOCIAL_CONTENT_PLAN.md` |
| 15 | Launch dashboard | Admin → Launch 30; `operations/launch_tracker.csv` |
| 16 | Operations dashboard | Admin → Overview, Sourcing, Budget, Consignments |
| 17 | Automated testing | `tests/` (63 tests) |
| 18 | Deployment instructions | `docs/DEPLOYMENT.md` |

Also: `agents/` (12 instruction files + runner), `research/RESEARCH_SUMMARY.md`, `docs/LEGAL_RESEARCH.md`, `operations/FINANCIAL_MODEL.md`, `marketing/BRAND_FILM_THE_OTHER_SIDE_OF_THE_GLASS.md`, `marketing/LAUNCH_CAMPAIGN_REMEMBER_THE_SOUND.md`, `outreach/drafts/` (5 drafts), `CLAUDE_VS_CODEX_COMPARISON.md`, `docs/ASSUMPTIONS.md`, `docs/KNOWN_GAPS.md`, `docs/ARCHITECTURE_DECISIONS.md`, `WORK_LOG.md`.

## Layout
```
agents/  research/  data/  sourcing/  authentication/  outreach/  commerce/  storefront/
marketing/  brand/  operations/  reports/  tests/  docs/  reference/codex_pack/
```

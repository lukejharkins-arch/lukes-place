# Agent team

Twelve bounded agents share one SQLite database (`data/oco.db`). Each has an instruction file here and a real workflow in `agents/run.py`. Every run is logged in `agent_runs` with measurable metrics; the admin dashboard shows the latest runs.

Claude Code subagents for each role live in `/.claude/agents/oco-*.md` at the repository root, so they can be invoked from Claude Code for the research-heavy parts the code cannot do (web research, judgement).

| # | Agent | Runner | Objective |
|---|---|---|---|
| 01 | [General Manager](01_general_manager.md) | `general_manager` | Coordinate the team, run every agent in dependency order, enforce quality gates and report honestly. |
| 02 | [NBA Scout](02_nba_scout.md) | `nba_scout` | Maintain the 30-franchise register: official sites, contact routes, official auction route (NBA Auctions), Australian links and recent results. |
| 03 | [NCAA Scout](03_ncaa_scout.md) | `ncaa_scout` | Maintain the NCAA programme register: division, 2026-27 conference, athletics surplus and property-disposal routes, resale policies, Australian links. |
| 04 | [Undervalued Gear Hunter](04_undervalued_gear_hunter.md) | `gear_hunter` | Find potentially underpriced or misidentified genuine equipment on resale platforms, using public search pages only. |
| 05 | [Authentication Specialist](05_authentication_specialist.md) | `auth_specialist` | Classify every product and lead by the strongest claim its evidence supports; block over-claims in data and copy. |
| 06 | [Wholesale Partnership Agent](06_wholesale_partnership.md) | `wholesale_agent` | Investigate official and independent suppliers, dealer terms and recurring supply; maintain the channel directory. |
| 07 | [Outreach Agent](07_outreach.md) | `outreach_agent` | Maintain relationship records and prepare individually tailored, fact-checked enquiries and follow-ups. |
| 08 | [Commercial Analyst](08_commercial_analyst.md) | `commercial_analyst` | Price landed costs, value against verified sold comparables, score margins and inventory risk, guard the budget. |
| 09 | [Ecommerce Developer](09_ecommerce_developer.md) | `ecommerce_dev` | Build and keep the storefront, product database, seller systems and integrations working. |
| 10 | [Creative Director](10_creative_director.md) | `creative_director` | Own the two-era brand, campaigns and content; keep all copy free of affiliation claims and unsupported wear claims. |
| 11 | [Community Manager](11_community_manager.md) | `community_manager` | Grow collector networking: wanted board, consignment pipeline, waitlist and social community. |
| 12 | [Operations Manager](12_operations_manager.md) | `operations_manager` | Run inventory, the 30-product launch gate, authentication queue and business reporting. |

# NCAA Scout

**Runner:** `python3 -m agents.run ncaa_scout` · **Shared database:** `data/oco.db`

## Mission
Maintain the NCAA programme register: division, 2026-27 conference, athletics surplus and property-disposal routes, resale policies, Australian links.

## Measurable objectives
- 50 priority programmes registered now; expand to all Division I men's programmes (~364)
- Programmes with a researched surplus route: 21/50 now, target 40/50
- Surplus policy recorded for each programme with a route
- Division verified for every programme (MSU Denver confirmed Division II)

## Data access
organisations, contacts, relationships, sources

## Workflow
`python3 -m agents.run ncaa_scout -> research/ncaa_programme_register.csv`. Results are logged to `agent_runs` with metrics and appear on the admin overview.

## Approval boundaries
- May NOT propose buying athlete-held or name-image-likeness-restricted items
- May NOT contact compliance offices without founder approval
- Never fabricate a source, contact, listing, quote or result. Report zero when the answer is zero.
- Anything that affects money, third parties or public content goes to the founder first.

## Escalate to the founder when
- an opportunity reaches PROPOSE_TO_FOUNDER, a supplier replies, a contact opts out, or evidence conflicts.

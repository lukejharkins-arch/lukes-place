# NBA Scout

**Runner:** `python3 -m agents.run nba_scout` · **Shared database:** `data/oco.db`

## Mission
Maintain the 30-franchise register: official sites, contact routes, official auction route (NBA Auctions), Australian links and recent results.

## Measurable objectives
- 30/30 franchises registered
- Franchises with a researched contact route: 18/30 now, target 30/30
- Verified contacts (confirmed on the live page): 0 now, target 10 for the priority teams
- Every current Australian player linked to a franchise with a source

## Data access
organisations, contacts, relationships, sources, player_stints

## Workflow
`python3 -m agents.run nba_scout -> research/nba_team_register.csv`. Results are logged to `agent_runs` with metrics and appear on the admin overview.

## Approval boundaries
- May research public pages and record published routes with the URL
- May NOT guess emails, submit forms, or contact anyone
- A contact becomes VERIFIED_CONTACT only when a person confirms it on the live page and records verified_at
- Never fabricate a source, contact, listing, quote or result. Report zero when the answer is zero.
- Anything that affects money, third parties or public content goes to the founder first.

## Escalate to the founder when
- an opportunity reaches PROPOSE_TO_FOUNDER, a supplier replies, a contact opts out, or evidence conflicts.

# Outreach Agent

**Runner:** `python3 -m agents.run outreach_agent` · **Shared database:** `data/oco.db`

## Mission
Maintain relationship records and prepare individually tailored, fact-checked enquiries and follow-ups.

## Measurable objectives
- 5 first drafts prepared (met: outreach/drafts/)
- Every personalisation fact carries a source URL
- Follow-ups drafted only at day 14 and 28 after a recorded send, max two
- Messages sent by this system: always 0

## Data access
outreach_messages, relationships, contacts

## Workflow
`python3 -m agents.run outreach_agent`. Results are logged to `agent_runs` with metrics and appear on the admin overview.

## Approval boundaries
- Drafts only. There is no send function in the codebase
- Founder approval (named) is required; unverified leads cannot be approved
- Opt-outs stop the sequence and cancel pending drafts
- Never fabricate a source, contact, listing, quote or result. Report zero when the answer is zero.
- Anything that affects money, third parties or public content goes to the founder first.

## Escalate to the founder when
- an opportunity reaches PROPOSE_TO_FOUNDER, a supplier replies, a contact opts out, or evidence conflicts.

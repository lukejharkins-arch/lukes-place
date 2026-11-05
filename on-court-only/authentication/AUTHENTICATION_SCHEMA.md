# Authentication schema

**AUTHENTIC ON COURT = VERIFIED TEAM ISSUE.** Implemented in `authentication/rules.py`, tested in `tests/test_core.py`.

## Classes (strongest supportable claim wins; under-claiming is always allowed)
| Class | Minimum evidence | Never implies |
|---|---|---|
| UNVERIFIED | none, or seller claim only | Not listable |
| LICENSED_RETAIL | GENUINE_MANUFACTURER (legit check) | Team issue |
| RARE_KICKS | Shoes with PE_MARKINGS or SAMPLE_TAG plus a legit check (PE or sample), or RARE_RELEASE plus a legit check (rare retail) | Player provenance |
| TEAM_ISSUED | Tier A (official purchase, team or partner LOA, or independent certificate) **or** chain of custody + one construction marker **or** team-issue tag + two construction markers (MEDIUM) | Any player link |
| VINTAGE_TEAM_ISSUE | Team-issued, season starting 2009 or earlier | Any player link |
| PLAYER_ISSUED | Team-issued + sewn name/number tag, an allocation document, or an institutional LOA naming the player | Wear |
| PLAYER_WORN | Player-issued + WEAR_LOA | A specific game |
| GAME_WORN | Team-issued + independent PHOTO_MATCH or GAME_USE_LOA | Nothing beyond the documented event |

**Blocking flags** override everything: COUNTERFEIT_INDICATORS, OWNERSHIP_DISPUTE, STOLEN_RISK (possible unauthorised equipment-room disposal), NIL_RESTRICTED (college athlete item restricted by policy).

**Design-match photos** (same design shown in use) are storytelling only and never upgrade a class.

## Evidence tiers
A institutional · B construction/custody · P player allocation · C use · D design reference · K kicks · G genuine · X not evidence. The full table is served at `/api/standards` and rendered on the Standards page.

## Copy linter
`lint_copy()` refuses "game-worn/used", "worn by", "player-issued", "team-issued", "pro cut", "equipment room" and "photo-matched" when the supported class doesn't allow them, ignores negated uses ("not game-worn"), and always flags affiliation language ("official partner of", "endorsed by", "authorised dealer").

## Reference media
EXACT_PHOTO_MATCH needs PHOTO_MATCH evidence; reference images display only with OWNED, LICENSED, PUBLIC_DOMAIN or CC rights (LINK_ONLY shows a link); live listings need an EXACT_ITEM_PHOTO.

## Collector red flags (from research, `research/raw/supply_channels.json`)
Retail lines named "Team Issue" or "Locker Issued" exist; "Authentic" on retail on-court apparel is not team issue; "game-issued" is not "worn"; check MeiGray registration tags by phone; auction descriptions are seller claims; college gear sold by athletes can breach NCAA rules.

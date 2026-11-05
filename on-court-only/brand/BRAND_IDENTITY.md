# ON COURT ONLY | Brand identity system

**Promise:** Where basketball love meets authentic on-court wear.
**Line:** Remember the sound? · Gear you saw. Gear you couldn't get. · Wear the game, not just the logo.
**Character:** bold, nostalgic, knowledgeable, original, unmistakably basketball. Speaks like a collector who has done the homework, never like a hype account.

Implemented in `storefront/styles.css` as tokens on `<html data-era>`; switch live with the OG / Current toggle in the header.

## 1. One house, two eras

| | ERA ONE: ON COURT OG | ERA TWO: CURRENT COURT |
|---|---|---|
| Period | 1996 to 2009 (seasons starting 2009 or earlier) | 2010 to now |
| Mood | 1990s basketball magazine, warmup culture, arena concourse | City Edition-era fashion, premium product photography, tunnel walks |
| Ground | Paper cream `#F1E6CC` with an original SVG grain | Ink `#11151B` |
| Ink | Charcoal `#1F1A17` | Chalk `#F8F5EB` |
| Accents | Electric purple `#5B2A86`, teal `#00838F`, burnt orange `#E2611B` | Court-lime `#C1ED57`, ice `#8FD3FF`, signal `#FF6B4A` |
| Display type | Bowlby One SC (Google Fonts, OFL), heavy and oversized | Barlow Condensed 800 (OFL), tight and technical |
| Body | Inter | Inter |
| Utility | IBM Plex Mono: equipment-room tags, SKU and season labels | Same |
| Cards | 3px ink border, hard offset shadow, rotated season tag | 1px hairline, no shadow, flat lime season tag |
| Motif | Snap-dot rows and dashed seam stitches (tearaway side seam) | Snap dots in lime, precise grid |

**What stays constant:** navigation, the logo lock-up, classification badges, purchase box, the left/right exhibit comparison, and all trust language. A shopper switching eras never loses their place.

**Per-product skin:** every product card and exhibit panel carries its own era (`.skin-og` / `.skin-current`) regardless of the site mode. A 1996 Bulls jacket looks like an archive piece even on the Current Court homepage.

## 2. Logo
Word mark "ON COURT ONLY" set in the active display face with "ONLY" in the accent colour, plus the micro-line "VERIFIED TEAM ISSUE · AUSTRALIA". No ball, crest, shield or silhouette that could read as a league, team or manufacturer mark. Trade mark clearance pending (see `docs/LEGAL_RESEARCH.md` section 10).

## 3. Illustration system
Until we hold photographs of real stock, the site shows original flat garment illustrations (pants, jacket, shirt, jersey, shoe) drawn in code from colourways (`storefront/app.js`, `art()`). They are always captioned "Original illustration, not a photo of the item". Team colourways describe the item and are not logos. Never trace or reproduce team artwork, wordmarks or manufacturer logos.

## 4. Photography rules
- **Left panel (item):** our own photographs of the exact item: front, back, tags, snaps, size label, flaws.
- **Right panel (reference):** only images we own, have licensed, or that are public domain or CC licensed. Otherwise the panel shows "Reference pending rights clearance" and at most a link.
- Labels: Exact item photo-match · Verified same-design reference · General era reference · Reference pending.
- Getty / AP / team photography is editorial-licensed at best; commercial use on a shop page needs a commercial licence (see legal research).

## 5. Voice
- Say exactly what we know: "Team-issued, documented by team letter ref. 1234." Not "100% authentic game gear!!!"
- Name players, teams and seasons factually for genuine goods. Never imply a player wore an item without evidence.
- Every listing carries: "Independent reseller. Not affiliated with or endorsed by the NBA, NCAA, any team, player or manufacturer."
- Australian English (colour, authorised, programme). No em dashes in copy.

## 6. Don'ts
No league, team or manufacturer logos in our identity, ads or social avatars. No "official", "authorised dealer" or "partner" language. No fake scarcity. No mocking ordinary fans or retail buyers.

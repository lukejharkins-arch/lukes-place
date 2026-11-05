"""Undervalued resale search framework.

Generates human-reviewable search links (public search pages only, no scraping)
across resale platforms, built from:
  * the vocabulary ordinary sellers use for older team equipment,
  * deliberate misspellings and vague descriptions,
  * team / school priority from the demand model.
It also scores a raw listing title for "possible misclassification" so the
hunter knows where to look harder. A high score is a reason to inspect, never
authentication evidence.
"""
from __future__ import annotations

import re
from urllib.parse import quote_plus

PLATFORMS = {
    "ebay_us": "https://www.ebay.com/sch/i.html?_nkw={q}&_sop=10",
    "ebay_us_sold": "https://www.ebay.com/sch/i.html?_nkw={q}&LH_Sold=1&LH_Complete=1",
    "ebay_au": "https://www.ebay.com.au/sch/i.html?_nkw={q}&_sop=10",
    "grailed": "https://www.grailed.com/shop?query={q}",
    "depop": "https://www.depop.com/search/?q={q}",
    "vinted": "https://www.vinted.com/catalog?search_text={q}",
    "mercari": "https://www.mercari.com/search/?keyword={q}",
    "poshmark": "https://poshmark.com/search?query={q}",
    "etsy": "https://www.etsy.com/search?q={q}",
    "gumtree_au": "https://www.gumtree.com.au/s-{q_dash}/k0",
    "facebook_marketplace": "https://www.facebook.com/marketplace/search/?query={q}",
    "govdeals": "https://www.govdeals.com/en/search?kWord={q}",
    "publicsurplus": "https://www.publicsurplus.com/sms/browse/search?posting=y&keyWord={q}",
}

# core terms ordinary sellers use (see research/raw/supply_channels.json for evidence)
BASE_TERMS = [
    "warm up pants", "warmup pants", "tearaway pants", "tear away pants", "snap pants", "snap away pants",
    "breakaway pants", "rip away pants", "popper pants", "basketball track pants", "basketball tracksuit",
    "warm up jacket", "shooting shirt", "practice shirt", "practice jersey", "player equipment bag",
]
TEAM_ISSUE_TERMS = ["team issued", "team issue", "pro cut", "player issued", "game issued", "TI",
                    "4XL+3", "3XLT", "XL+2", "tall", "length +2", "made in usa"]
VAGUE_TERMS = ["vintage athletic pants", "oversized nike pants", "90s basketball pants", "old school track pants",
               "college athletic pants", "university team clothing", "basketball warmup lot", "sports clothing lot",
               "big and tall nike pants", "mens 4xl track pants"]
MISSPELLINGS = {
    "tearaway": ["tear-a-way", "tareaway", "tearaways", "tear awy"],
    "warmup": ["warm-up", "wram up", "warmp up", "warm ups"],
    "basketball": ["basket ball", "bball", "baskeball"],
    "lakers": ["laker", "la lakers"], "celtics": ["celtic"], "cavaliers": ["cavs", "cavaliar"],
    "warriors": ["warrior", "gsw"], "spurs": ["san antonio spur"], "magic": ["orlando majic"],
    "thunder": ["okc"], "bulls": ["chicago bull"], "gonzaga": ["gonzega", "zags"],
    "saint mary's": ["st marys", "st. mary's", "saint marys gaels"],
}
MANUFACTURER_ERA = {
    "OG": ["champion", "starter", "nike team", "reebok", "logo athletic", "puma", "russell", "majestic"],
    "CURRENT": ["nike", "nike team", "jordan", "adidas", "under armour"],
}


def queries_for(team: str, era: str = "OG", limit: int = 30) -> list[str]:
    """Build search queries for one team/school: precise first, then vague and misspelt."""
    t = team.lower()
    out = []
    for term in ["team issued warm up pants", "pro cut warm up", "tearaway pants", "snap pants",
                 "warm up jacket", "shooting shirt", "player issued"]:
        out.append(f"{t} {term}")
    for mfr in MANUFACTURER_ERA.get(era, []):
        out.append(f"{mfr} {t} warm up")
    nick = t.split()[-1]
    for alt in MISSPELLINGS.get(nick, []) + MISSPELLINGS.get(t, []):
        out.append(f"{alt} warmup pants")
        out.append(f"{alt} tear away")
    out.append(f"{t} basketball lot")
    # dedupe preserving order
    seen, uniq = set(), []
    for q in out:
        if q not in seen:
            seen.add(q)
            uniq.append(q)
    return uniq[:limit]


def generic_queries() -> list[str]:
    qs = [f"{v}" for v in VAGUE_TERMS]
    qs += [f"nba {t}" for t in ["team issued pants", "tearaway", "warm up pants", "pro cut"]]
    qs += [f"ncaa {t}" for t in ["team issued warm up", "team gear lot", "player issue"]]
    for word, alts in MISSPELLINGS.items():
        if word in ("tearaway", "warmup", "basketball"):
            qs += [f"{a} pants" for a in alts]
    return qs


def links(query: str, platforms=None) -> dict[str, str]:
    platforms = platforms or PLATFORMS.keys()
    q = quote_plus(query)
    q_dash = re.sub(r"[^a-z0-9]+", "-", query.lower()).strip("-")
    return {p: PLATFORMS[p].format(q=q, q_dash=q_dash) for p in platforms}


_STRONG = re.compile(r"\b(\d?xl\s?\+\s?\d|[2-5]xlt|xl\s?tall|\+\s?2 length|pro cut|team issued?|player issued?|"
                     r"game issued?|made in usa|sewn|stitched name|equipment room)\b", re.I)
_ERA = re.compile(r"\b(19[89]\d|200\d|90s|80s|vintage|og)\b", re.I)
_UNDERSOLD = re.compile(r"\b(old|used|pants|track ?pants|joggers|lot|bundle|mens|unknown|misc|clean out)\b", re.I)
_TERMS_SELLERS_KNOW = re.compile(r"\b(team issued?|pro cut|game (worn|used|issued)|player issued?|loa|coa)\b", re.I)


def misclassification_signal(title: str, price_aud: float | None = None) -> dict:
    """Score 0-100 how likely a listing is under-described relative to what it may be.

    High when the title carries pro-sizing / construction hints or era cues but
    the seller has NOT used collector vocabulary, and the price is low.
    """
    strong = len(_STRONG.findall(title))
    era = bool(_ERA.search(title))
    vague = len(_UNDERSOLD.findall(title))
    knows = bool(_TERMS_SELLERS_KNOW.search(title))
    s = strong * 25 + (15 if era else 0) + min(20, vague * 5)
    if knows:
        s -= 30        # seller already markets it as team issue: priced accordingly
    if price_aud is not None:
        s += 20 if price_aud < 60 else (10 if price_aud < 120 else 0)
    s = max(0, min(100, s))
    return {"score": s, "seller_uses_collector_terms": knows, "pro_sizing_or_construction_hints": strong,
            "era_cue": era, "note": "Signal for inspection only; not authentication evidence"}


def plan(priority_teams: list[dict], per_team: int = 8, platforms=("ebay_us", "ebay_us_sold", "grailed", "depop",
                                                                      "vinted", "mercari", "gumtree_au")) -> list[dict]:
    """Daily search plan: top teams by demand x precise and vague queries x platforms."""
    out = []
    for t in priority_teams:
        for q in queries_for(t["name"], t.get("era", "OG"))[:per_team]:
            out.append({"team": t["name"], "query": q, "links": links(q, platforms)})
    for q in generic_queries()[:12]:
        out.append({"team": "(generic)", "query": q, "links": links(q, platforms)})
    return out

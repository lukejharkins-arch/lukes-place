"""Authentication engine: evidence in, the strongest *supportable* classification out.

Core principle: AUTHENTIC ON COURT = VERIFIED TEAM ISSUE.
The engine never upgrades on a seller's word. It derives the highest class the
recorded evidence supports, explains why, and lists what would be needed next.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# --------------------------------------------------------------- vocabulary
CLASSES = {
    "TEAM_ISSUED": "Team-Issued",
    "PLAYER_ISSUED": "Player-Issued",
    "PLAYER_WORN": "Player-Worn Premium",
    "GAME_WORN": "Player-Worn Premium (Game-Worn)",
    "VINTAGE_TEAM_ISSUE": "Vintage Team Issue",
    "RARE_KICKS": "Rare Kicks",
    "LICENSED_RETAIL": "Licensed Retail",
    "UNVERIFIED": "Unverified (not listable)",
}

# Evidence codes. tier: A institutional, B construction/custody, C use, K kicks, G genuine, X negative
EVIDENCE = {
    "OFFICIAL_SOURCE_PURCHASE": ("A", "Acquired directly from a team, university or league-run sale (receipt held)"),
    "TEAM_LOA": ("A", "Letter of authenticity from the team or its official memorabilia partner, with reference ID"),
    "AUTHENTICATOR_CERT": ("A", "Independent authenticator certificate with an independently verifiable reference ID"),
    "CHAIN_OF_CUSTODY": ("B", "Documented chain of custody back to team, staff or player"),
    "TEAM_ISSUE_TAG": ("B", "Manufacturer team-issue / pro tag not used on retail product"),
    "TALL_OR_PRO_SIZING": ("B", "Pro sizing such as XL+2 / 3XLT length tags"),
    "INTERNAL_CODE": ("B", "Internal style or production code matching documented team-issue product"),
    "CONSTRUCTION_MATCH": ("B", "Construction documented against verified team-issue examples"),
    "PLAYER_NAME_TAG": ("P", "Sewn player name / number tag"),
    "PLAYER_ALLOCATION_DOC": ("P", "Document allocating the item to a named player"),
    "DESIGN_MATCH_PHOTO": ("D", "Photo shows the same design in use (does NOT prove this physical item)"),
    "WEAR_LOA": ("C", "LOA stating the named player wore/used this item (practice or warmup)"),
    "GAME_USE_LOA": ("C", "LOA stating use in a specific, named game"),
    "PHOTO_MATCH": ("C", "Independent photo-match of this exact item to a specific event"),
    "PE_MARKINGS": ("K", "Player-exclusive markings, PE codes or player-specific build"),
    "SAMPLE_TAG": ("K", "Manufacturer sample / pre-release tag"),
    "RARE_RELEASE": ("K", "Documented limited or historic retail release"),
    "GENUINE_MANUFACTURER": ("G", "Genuine manufacturer product (legit check passed)"),
    "SELLER_CLAIM_ONLY": ("X", "Seller statement only, not evidence"),
}

BLOCKING_FLAGS = {
    "COUNTERFEIT_INDICATORS": "Counterfeit indicators present",
    "OWNERSHIP_DISPUTE": "Title or right to sell is unclear",
    "STOLEN_RISK": "Possible unauthorised equipment-room disposal or theft",
    "NIL_RESTRICTED": "Item tied to a college athlete's name/image/likeness under a restricting policy",
}

# claims each supported class permits (conservative under-claiming is always allowed)
_ALLOWED = {
    "UNVERIFIED": set(),
    "LICENSED_RETAIL": {"LICENSED_RETAIL"},
    "RARE_KICKS": {"RARE_KICKS", "LICENSED_RETAIL"},
    "TEAM_ISSUED": {"TEAM_ISSUED", "LICENSED_RETAIL"},
    "VINTAGE_TEAM_ISSUE": {"VINTAGE_TEAM_ISSUE", "TEAM_ISSUED", "LICENSED_RETAIL"},
    "PLAYER_ISSUED": {"PLAYER_ISSUED", "TEAM_ISSUED", "VINTAGE_TEAM_ISSUE", "LICENSED_RETAIL"},
    "PLAYER_WORN": {"PLAYER_WORN", "PLAYER_ISSUED", "TEAM_ISSUED", "VINTAGE_TEAM_ISSUE", "LICENSED_RETAIL"},
    "GAME_WORN": {"GAME_WORN", "PLAYER_WORN", "PLAYER_ISSUED", "TEAM_ISSUED", "VINTAGE_TEAM_ISSUE", "LICENSED_RETAIL"},
}
# shoes may also carry RARE_KICKS when player-issued/worn evidence exists
for _c in ("PLAYER_ISSUED", "PLAYER_WORN", "GAME_WORN", "TEAM_ISSUED", "VINTAGE_TEAM_ISSUE"):
    _ALLOWED[_c] = _ALLOWED[_c] | {"RARE_KICKS"}


@dataclass
class Assessment:
    supported: str
    confidence: str                       # HIGH | MEDIUM | LOW | NONE
    reasons: list = field(default_factory=list)
    next_evidence: list = field(default_factory=list)
    blocked_by: list = field(default_factory=list)
    kicks_subtype: str | None = None

    @property
    def listable(self) -> bool:
        return self.supported != "UNVERIFIED" and not self.blocked_by

    def as_dict(self):
        return {
            "supported": self.supported,
            "label": CLASSES[self.supported],
            "confidence": self.confidence,
            "reasons": self.reasons,
            "next_evidence": self.next_evidence,
            "blocked_by": self.blocked_by,
            "kicks_subtype": self.kicks_subtype,
            "listable": self.listable,
        }


def season_start(season: str | None) -> int | None:
    if not season:
        return None
    m = re.search(r"(19|20)\d{2}", str(season))
    return int(m.group(0)) if m else None


def classify(evidence_codes, item_type: str = "OTHER", season: str | None = None,
             red_flags=(), og_cutoff: int = 2009, player_named: bool = False) -> Assessment:
    """Derive the strongest supportable classification from evidence codes."""
    ev = {c for c in evidence_codes if c in EVIDENCE and c != "SELLER_CLAIM_ONLY"}
    unknown = [c for c in evidence_codes if c not in EVIDENCE]
    flags = [f for f in red_flags if f in BLOCKING_FLAGS]

    if flags:
        return Assessment("UNVERIFIED", "NONE",
                          reasons=[BLOCKING_FLAGS[f] for f in flags],
                          next_evidence=["Resolve blocking issue before any listing"],
                          blocked_by=flags)

    tier = lambda t: {c for c in ev if EVIDENCE[c][0] == t}
    a, b, c_use = tier("A"), tier("B"), tier("C")
    construction = b - {"CHAIN_OF_CUSTODY"}
    reasons = [EVIDENCE[c][1] for c in sorted(ev)]
    if unknown:
        reasons.append(f"Ignored unrecognised evidence codes: {', '.join(unknown)}")

    # ---- team-issue proof and its confidence
    team_conf = None
    if a:
        team_conf = "HIGH"
    elif "CHAIN_OF_CUSTODY" in ev and construction:
        team_conf = "MEDIUM"
    elif "TEAM_ISSUE_TAG" in ev and len(construction) >= 2:
        team_conf = "MEDIUM"

    player_alloc = bool(ev & {"PLAYER_NAME_TAG", "PLAYER_ALLOCATION_DOC"})
    # an institutional LOA that names the player counts as allocation evidence
    if player_named and ev & {"TEAM_LOA", "AUTHENTICATOR_CERT"}:
        player_alloc = True

    is_shoe = item_type == "SHOES"
    start = season_start(season)

    if team_conf:
        if "PHOTO_MATCH" in c_use or "GAME_USE_LOA" in c_use:
            result = Assessment("GAME_WORN", "HIGH" if a else "MEDIUM", reasons)
        elif "WEAR_LOA" in c_use and player_alloc:
            result = Assessment("PLAYER_WORN", "HIGH" if a else "MEDIUM", reasons)
        elif player_alloc:
            result = Assessment("PLAYER_ISSUED", team_conf, reasons)
            result.next_evidence.append("Wear claims need a wear LOA or an independent photo-match (PLAYER_WORN)")
        else:
            cls = "VINTAGE_TEAM_ISSUE" if (start is not None and start <= og_cutoff) else "TEAM_ISSUED"
            result = Assessment(cls, team_conf, reasons)
            result.next_evidence.append("Player allocation needs a sewn name tag or allocation document (PLAYER_ISSUED)")
        if "DESIGN_MATCH_PHOTO" in ev:
            result.reasons.append("Same-design photo is a storytelling reference only, not proof this item was used")
        if is_shoe and ev & {"PE_MARKINGS", "SAMPLE_TAG"}:
            result.kicks_subtype = "PLAYER_EXCLUSIVE" if "PE_MARKINGS" in ev else "SAMPLE"
        if team_conf != "HIGH":
            result.next_evidence.append("An official LOA or independent certificate would raise confidence to HIGH")
        return result

    if is_shoe:
        if ev & {"PE_MARKINGS", "SAMPLE_TAG"} and "GENUINE_MANUFACTURER" in ev:
            r = Assessment("RARE_KICKS", "MEDIUM", reasons,
                           kicks_subtype="PLAYER_EXCLUSIVE" if "PE_MARKINGS" in ev else "SAMPLE")
            r.next_evidence.append("Team/player provenance needed before any player-issued or worn claim")
            return r
        if "RARE_RELEASE" in ev and "GENUINE_MANUFACTURER" in ev:
            return Assessment("RARE_KICKS", "MEDIUM", reasons, kicks_subtype="RARE_RETAIL",
                              next_evidence=["Retail release: never describe as player-issued"])

    if "GENUINE_MANUFACTURER" in ev:
        nxt = ["Team-issue needs official provenance, an authenticator, or custody plus construction evidence"]
        if construction:
            nxt.insert(0, "Construction clues alone are insufficient; add chain of custody or a second independent marker")
        return Assessment("LICENSED_RETAIL", "MEDIUM", reasons, next_evidence=nxt)

    return Assessment("UNVERIFIED", "NONE", reasons or ["No authenticity evidence recorded"],
                      next_evidence=["Legit check (GENUINE_MANUFACTURER) is the minimum for any listing"])


def claim_allowed(claimed: str, supported: str) -> bool:
    return claimed in _ALLOWED.get(supported, set())


# ------------------------------------------------------------- copy linter
_NEG = re.compile(r"\b(not|never|no|without|isn't|is not|cannot|can't|nor)\b[\w\s,'-]{0,40}$", re.I)

COPY_RULES = [
    # (pattern, minimum classes that permit it, message)
    (re.compile(r"\bgame[- ]?(worn|used)\b", re.I), {"GAME_WORN"}, "Game-worn/used language needs GAME_WORN evidence"),
    (re.compile(r"\b(player[- ]worn|worn by|wore (this|these|it)|match[- ]worn)\b", re.I),
     {"PLAYER_WORN", "GAME_WORN"}, "Wear language needs PLAYER_WORN evidence"),
    (re.compile(r"\b(player[- ]issued|issued to)\b", re.I),
     {"PLAYER_ISSUED", "PLAYER_WORN", "GAME_WORN"}, "Player-issued language needs player allocation evidence"),
    (re.compile(r"\b(team[- ]issued?|pro[- ]cut|equipment[- ]room|on[- ]court issue)\b", re.I),
     {"TEAM_ISSUED", "VINTAGE_TEAM_ISSUE", "PLAYER_ISSUED", "PLAYER_WORN", "GAME_WORN"},
     "Team-issue language needs team-issue evidence"),
    (re.compile(r"\bphoto[- ]?match(ed)?\b", re.I), {"GAME_WORN"}, "Photo-match language needs an independent photo-match"),
]
AFFILIATION = re.compile(
    r"\b(official(ly)? (licensed|partner|retailer|distributor|store)|endorsed by|authori[sz]ed (by|dealer|reseller)|"
    r"in partnership with the (nba|ncaa))\b", re.I)


def lint_copy(text: str, supported: str) -> list[dict]:
    """Return problems where marketing copy over-claims versus the supported class."""
    issues = []
    if not text:
        return issues
    for pattern, permitted, msg in COPY_RULES:
        for m in pattern.finditer(text):
            before = text[max(0, m.start() - 45):m.start()]
            if _NEG.search(before):
                continue                      # "not game-worn", "no evidence it was worn by"
            if supported not in permitted:
                issues.append({"phrase": m.group(0), "problem": msg, "supported": supported})
    for m in AFFILIATION.finditer(text):
        before = text[max(0, m.start() - 45):m.start()]
        if _NEG.search(before):
            continue
        issues.append({"phrase": m.group(0),
                       "problem": "Affiliation/endorsement claim: ON COURT ONLY is independent", "supported": supported})
    return issues


# ------------------------------------------------------ storytelling media
REFERENCE_LEVELS = {
    "EXACT_PHOTO_MATCH": "Exact item photo-match",
    "SAME_DESIGN_REFERENCE": "Verified same-design reference (not necessarily this item)",
    "ERA_REFERENCE": "General era reference",
    "REFERENCE_PENDING": "Reference pending rights clearance",
}
DISPLAYABLE_RIGHTS = {"OWNED", "LICENSED", "PUBLIC_DOMAIN", "CC_LICENCE"}


def check_media(media: list[dict], evidence_codes, is_demo: bool) -> list[str]:
    problems = []
    items = [m for m in media if m["side"] == "ITEM"]
    refs = [m for m in media if m["side"] == "REFERENCE"]
    if not items:
        problems.append("No item image recorded")
    for m in items:
        if m["match_level"] != "EXACT_ITEM_PHOTO" and not is_demo:
            problems.append("Live listings need a photo of the exact item being sold")
        if m["rights_status"] not in DISPLAYABLE_RIGHTS:
            problems.append("Item image has no usable rights")
    if not refs:
        problems.append("No reference panel recorded (use REFERENCE_PENDING if rights are absent)")
    for m in refs:
        if m["match_level"] == "EXACT_PHOTO_MATCH" and "PHOTO_MATCH" not in set(evidence_codes):
            problems.append("EXACT_PHOTO_MATCH reference requires PHOTO_MATCH evidence")
        if m["match_level"] != "REFERENCE_PENDING" and m["rights_status"] not in DISPLAYABLE_RIGHTS | {"LINK_ONLY"}:
            problems.append(f"Reference image rights '{m['rights_status']}' do not permit display")
    return problems

"""Departments, catalogue queries and product presentation."""
import json

from authentication.rules import CLASSES, REFERENCE_LEVELS, classify
from commerce.db import jload, one, rows

DEPARTMENTS = {
    "OG_ONCOURT": {"name": "ON COURT OGs", "era": "OG", "blurb": "Vintage team-issued gear and warmups, 1996 onward."},
    "OG_JERSEYS": {"name": "OG Jerseys", "era": "OG", "blurb": "Historical jerseys and distinctive early-era apparel."},
    "CURRENT_COURT": {"name": "Current Court", "era": "CURRENT", "blurb": "Modern team-issued equipment."},
    "CURRENT_JERSEYS": {"name": "Current Jerseys", "era": "CURRENT", "blurb": "Current-era jerseys, correctly classified."},
    "COLLEGE_LIFE": {"name": "College Life", "era": None, "blurb": "NCAA warmups, jerseys, Final Four gear and programmes."},
    "TEARAWAY_VAULT": {"name": "The Tearaway Vault", "era": None, "blurb": "The signature snap-away collection."},
    "KICKS_PES": {"name": "Kicks & PEs", "era": None, "blurb": "Rare original shoes and player exclusives."},
    "FINALS_VAULT": {"name": "The Finals Vault", "era": None, "blurb": "Championship and tournament-connected equipment."},
    "LOGO_ARCHIVE": {"name": "The Logo Archive", "era": None, "blurb": "Historic basketball branding and licensed apparel, labelled as retail."},
    "PLAYER_WORN": {"name": "Player-Worn Premium", "era": None, "blurb": "Evidence-backed player-worn and game-worn pieces."},
    "COLLECTOR_EXCHANGE": {"name": "The Collector Exchange", "era": None, "blurb": "Approved resale and consignment marketplace."},
}

PURCHASABLE_STATUSES = {"LISTED"}


def evidence_codes(conn, pid):
    return [r["code"] for r in rows(conn, "SELECT code FROM evidence WHERE product_id=?", (pid,))]


def can_purchase(p: dict) -> tuple[bool, str]:
    if p["is_demo"]:
        return False, "Demo exhibit: not for sale"
    if p["status"] not in PURCHASABLE_STATUSES:
        return False, f"Not available ({p['status'].lower()})"
    if not (p["stock_confirmed"] and p["stock_qty"] > 0 and p["listing_authority_ref"]):
        return False, "Stock or listing authority not confirmed"
    return True, "Available"


def present(conn, p: dict, full=False) -> dict:
    ev = evidence_codes(conn, p["id"])
    a = classify(ev, p["item_type"], p["season"], player_named=bool(p["player_id"]))
    ok, why = can_purchase(p)
    out = {
        "id": p["id"], "slug": p["slug"], "title": p["title"], "department": p["department"],
        "department_name": DEPARTMENTS.get(p["department"], {}).get("name"), "era": p["era"],
        "league": p["league_id"], "organisation_id": p["organisation_id"], "team_or_school": p["team_or_school"],
        "player_id": p["player_id"], "season": p["season"], "manufacturer": p["manufacturer"], "item_type": p["item_type"],
        "size": p["size"], "condition_grade": p["condition_grade"],
        "classification": a.supported, "classification_label": CLASSES[a.supported], "confidence": a.confidence,
        "price_aud": p["price_cents"] / 100 if p["price_cents"] else None, "ownership": p["ownership"],
        "status": p["status"], "is_demo": bool(p["is_demo"]), "purchasable": ok, "availability": why,
        "collections": jload(p.get("collections")), "art": jload(p.get("art"), {}),
    }
    if full:
        media = rows(conn, "SELECT side, match_level, url, caption, rights_status, credit FROM product_media WHERE product_id=?",
                     (p["id"],))
        for m in media:
            m["match_label"] = REFERENCE_LEVELS.get(m["match_level"], m["match_level"].replace("_", " ").title())
            m["displayable"] = m["rights_status"] in {"OWNED", "LICENSED", "PUBLIC_DOMAIN", "CC_LICENCE"}
            if not m["displayable"]:
                m["url_link_only"] = m["url"]
                m["url"] = None
        out.update({
            "condition_notes": p["condition_notes"], "player_connection": p["player_connection"],
            "claimed_classification": p["claimed_classification"], "description": p["description"],
            "story": {"team": p["story_team"], "era": p["story_era"], "design": p["story_design"],
                      "rarity": p["story_rarity"], "why_collect": p["story_why_collect"], "vs_retail": p["story_vs_retail"]},
            "authentication": a.as_dict(),
            "evidence": rows(conn, "SELECT code, detail, reference_id, url, verified_by, verified_at FROM evidence WHERE product_id=?",
                             (p["id"],)),
            "custody": rows(conn, "SELECT happened_on, holder, event, documented, note FROM custody_events WHERE product_id=? ORDER BY id",
                            (p["id"],)),
            "media": media,
            "player": one(conn, "SELECT id, name, achievements, verification FROM players WHERE id=?", (p["player_id"],))
            if p["player_id"] else None,
        })
    return out


def search(conn, q=None, department=None, era=None, league=None, team=None, item_type=None, classification=None,
           sort="featured", limit=60, public=True):
    sql = ("SELECT * FROM products WHERE status IN ('DEMO','LISTED','RESERVED','SOLD')" if public
           else "SELECT * FROM products WHERE 1=1")
    params = []
    if q:
        sql += " AND (title LIKE ? OR team_or_school LIKE ? OR description LIKE ? OR season LIKE ? OR manufacturer LIKE ?)"
        params += [f"%{q}%"] * 5
    if department:
        sql += " AND (department = ? OR collections LIKE ?)"
        params += [department, f'%"{department}"%']
    if era:
        sql += " AND era = ?"
        params.append(era)
    if league:
        sql += " AND league_id = ?"
        params.append(league)
    if team:
        sql += " AND organisation_id = ?"
        params.append(team)
    if item_type:
        sql += " AND item_type = ?"
        params.append(item_type)
    order = {"price_asc": "price_cents ASC", "price_desc": "price_cents DESC", "newest": "created_at DESC",
             "season": "season ASC"}.get(sort, "is_demo ASC, id ASC")
    sql += f" ORDER BY {order} LIMIT ?"
    params.append(int(limit))
    items = [present(conn, dict(r)) for r in conn.execute(sql, params)]
    if classification:
        items = [i for i in items if i["classification"] == classification]
    return items

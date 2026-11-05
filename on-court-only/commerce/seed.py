"""Build the database: baseline registers + agent research overlays + clearly-flagged demo data.

    python3 -m commerce.seed --reset

Research files in research/raw/ are optional; the seed degrades gracefully.
"""
from __future__ import annotations

import argparse
import json
import re
import secrets
from pathlib import Path

from commerce import config as C
from commerce.auth import hash_password
from commerce.db import connect, init, now_iso
from data.baseline import NBA_TEAMS, NCAA_PROGRAMMES, SCHOOL_ALIASES, TEAM_ALIASES
from operations.launch import ensure_slots

RAW = C.ROOT / "research" / "raw"
TODAY = "2026-11-05"


def _load(name):
    p = RAW / name
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except ValueError:
        return None


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _team_id(name: str | None):
    if not name:
        return None
    n = name.lower()
    for full in (t[1].lower() for t in NBA_TEAMS):
        if full in n:
            return "NBA-" + next(t[0] for t in NBA_TEAMS if t[1].lower() == full)
    for alias in sorted(TEAM_ALIASES, key=len, reverse=True):
        if alias in n:
            return TEAM_ALIASES[alias]
    return None


def _school_id(name: str | None):
    if not name:
        return None
    n = name.lower()
    for pid, inst, *_ in NCAA_PROGRAMMES:
        if inst.lower() in n or n in inst.lower():
            return "NCAA-" + pid
    for alias, oid in SCHOOL_ALIASES.items():
        if alias in n:
            return oid
    return None


def _src(conn, etype, eid, url, supports, checked=TODAY):
    if url:
        conn.execute("INSERT INTO sources(entity_type, entity_id, url, supports, checked_at) VALUES (?,?,?,?,?)",
                     (etype, eid, url, supports, checked))


def _verification(v):
    v = (v or "").upper()
    return "VERIFIED" if v.startswith("VERIFIED") else ("PARTIAL" if v.startswith("PARTIAL") else "UNVERIFIED")


# ------------------------------------------------------------------ NBA
def seed_nba(conn):
    for tid, name, city, conf, div, slug, titles, era in NBA_TEAMS:
        conn.execute("""INSERT INTO organisations(id, kind, name, league_id, conference, division, city, website, iconic_era,
                        notes, verification, researched_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                     (f"NBA-{tid}", "NBA_TEAM", name, "NBA", conf, div, city, f"https://www.nba.com/{slug}", era,
                      f"Titles (baseline knowledge, verify): {titles}", "PARTIAL", TODAY))
        conn.execute("INSERT INTO relationships(organisation_id, updated_at, next_action) VALUES (?,?,?)",
                     (f"NBA-{tid}", now_iso(), "Confirm official contact route on the live page; identify equipment/memorabilia department"))
    research = _load("nba_teams_research.json") or []
    for t in research:
        oid = _team_id(t.get("team"))
        if not oid:
            continue
        conn.execute("UPDATE organisations SET recent_success=?, notes=COALESCE(notes,'') || ? WHERE id=?",
                     (t.get("recent_success"), f" | Arena: {t.get('arena') or 'n/a'}", oid))
        route = t.get("official_contact_route") or {}
        if isinstance(route, dict) and route.get("url"):
            conn.execute("""INSERT INTO contacts(organisation_id, department, method, value, tier, evidence_url, notes)
                            VALUES (?,?,?,?,?,?,?)""",
                         (oid, "Front office / fan relations", "CONTACT_PAGE", route["url"], "RESEARCHED_ROUTE", route["url"],
                          "Official team page URL; contents seen via search index only. Confirm live before use."))
            for d in route.get("published_details") or []:
                method = {"email": "EMAIL", "phone": "PHONE", "mail": "POSTAL"}.get((d.get("type") or "").lower())
                if not method:
                    continue
                conn.execute("""INSERT INTO contacts(organisation_id, department, method, value, tier, evidence_url, notes)
                                VALUES (?,?,?,?,?,?,?)""",
                             (oid, "General", method, d.get("value"), "UNVERIFIED_LEAD", d.get("source"),
                              "Seen in search-index snippet of an official page on 2026-11-05; not loaded live. "
                              "Promote to VERIFIED_CONTACT only after a person confirms it on the page."))
        auction = t.get("official_auction_route") or {}
        if isinstance(auction, dict):
            conn.execute("UPDATE relationships SET approved_purchasing_process=? WHERE organisation_id=?",
                         ((auction.get("programme") or "")[:500], oid))
            for e in auction.get("evidence") or []:
                _src(conn, "organisation", oid, e.get("url"), "Auction route: " + (e.get("supports") or "")[:200])
        for s in t.get("sources") or []:
            if isinstance(s, dict):
                _src(conn, "organisation", oid, s.get("url"), (s.get("supports") or "")[:300])
            elif isinstance(s, str):
                _src(conn, "organisation", oid, s, "NBA Scout research")


# ------------------------------------------------------------------ NCAA
def seed_ncaa(conn):
    for pid, inst, nick, div, conf, reason in NCAA_PROGRAMMES:
        conn.execute("""INSERT INTO organisations(id, kind, name, league_id, conference, division, nickname, notes,
                        verification, researched_at) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                     (f"NCAA-{pid}", "NCAA_PROGRAMME", inst, "NCAA", conf, f"Division {div}", nick, reason, "UNVERIFIED", TODAY))
        conn.execute("INSERT INTO relationships(organisation_id, updated_at, next_action) VALUES (?,?,?)",
                     (f"NCAA-{pid}", now_iso(), "Confirm athletics equipment room / university surplus route"))
    data = _load("ncaa_programmes.json") or {}
    for p in data.get("programmes", []):
        oid = _school_id(p.get("institution"))
        if not oid:
            continue
        div = p.get("division") or ""
        conn.execute("""UPDATE organisations SET conference=COALESCE(?, conference), division=COALESCE(?, division),
                        website=?, recent_success=?, verification=? WHERE id=?""",
                     (p.get("conference_2026_27"), div.replace("NCAA ", "") or None, p.get("official_athletics_site"),
                      p.get("tournament_2026_result"), _verification(p.get("verification")), oid))
        route = p.get("surplus_or_property_disposal_route")
        if route:
            conn.execute("UPDATE relationships SET approved_purchasing_process=? WHERE organisation_id=?", (route[:600], oid))
        for u in p.get("surplus_route_urls") or []:
            conn.execute("""INSERT INTO contacts(organisation_id, department, method, value, tier, evidence_url, notes)
                            VALUES (?,?,?,?,?,?,?)""",
                         (oid, "University surplus / property disposition", "CONTACT_PAGE", u, "RESEARCHED_ROUTE", u,
                          f"Surplus route ({p.get('surplus_route_status')}); seen via search index. Confirm live."))
        for s in p.get("sources") or []:
            url = s.get("url") if isinstance(s, dict) else s
            _src(conn, "organisation", oid, url, (s.get("supports") if isinstance(s, dict) else "NCAA Scout research"))
    for ev in data.get("surplus_sale_evidence", []):
        oid = _school_id(ev.get("institution"))
        if oid:
            _src(conn, "organisation", oid, ev.get("url"), f"Surplus sale {ev.get('date')}: {ev.get('event')}"[:300])


# -------------------------------------------------------- Australians
def seed_australians(conn):
    data = _load("australian_connections.json") or {}
    seen = {}

    def player(rec, status):
        pid = "P-" + _slug(rec["name"])
        if pid not in seen:
            ach = rec.get("notable_achievements") or rec.get("contract_note") or rec.get("status")
            conn.execute("""INSERT INTO players(id, name, nationality, is_australian, status, position, college, achievements,
                            verification, notes) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                         (pid, rec["name"], "Australia", 1, status, rec.get("position"), rec.get("college"),
                          "; ".join(ach) if isinstance(ach, list) else ach, _verification(rec.get("verification")),
                          rec.get("verification_note")))
            for u in rec.get("source_urls") or []:
                _src(conn, "player", pid, u, f"{rec['name']} record")
            seen[pid] = True
        return pid

    for rec in data.get("current_nba", []):
        pid = player(rec, "CURRENT_NBA")
        conn.execute("""INSERT INTO player_stints(player_id, organisation_id, organisation_name, seasons, is_current, verification)
                        VALUES (?,?,?,?,1,?)""", (pid, _team_id(rec.get("team")), rec.get("team"), rec.get("season"),
                                                   _verification(rec.get("verification"))))
    champs = {}
    for rec in data.get("nba_champions", []):
        champs.setdefault(rec["name"], set()).add(_team_id(rec.get("team")))
    for rec in data.get("former_nba", []):
        pid = player(rec, "FORMER_NBA")
        for stint in rec.get("nba_teams") or []:
            m = re.match(r"(.+?)\s+((?:19|20)\d{2}.*)$", stint)
            team, seasons = (m.group(1), m.group(2)) if m else (stint, None)
            oid = _team_id(team)
            conn.execute("""INSERT INTO player_stints(player_id, organisation_id, organisation_name, seasons, champion, verification)
                            VALUES (?,?,?,?,?,?)""",
                         (pid, oid, team, seasons, int(oid in champs.get(rec["name"], set())), _verification(rec.get("verification"))))
    for rec in data.get("nba_champions", []):
        pid = player(rec, "FORMER_NBA")
        for u in rec.get("source_urls") or []:
            _src(conn, "player", pid, u, f"{rec['name']} NBA champion {rec.get('years')}")
    for prog in data.get("ncaa_programmes_with_aussie_alumni", []):
        oid = _school_id(prog.get("school"))
        for name in prog.get("notable_aussie_alumni") or []:
            clean = re.sub(r"\s*\(.*\)", "", name).strip()
            unverified = "unverified" in name.lower()
            pid = "P-" + _slug(clean)
            if pid not in seen:
                player({"name": clean, "verification": "UNVERIFIED" if unverified else prog.get("verification"),
                        "source_urls": prog.get("source_urls")}, "FORMER_NCAA")
            conn.execute("""INSERT INTO player_stints(player_id, organisation_id, organisation_name, verification)
                            VALUES (?,?,?,?)""", (pid, oid, prog.get("school"),
                                                  "UNVERIFIED" if unverified else _verification(prog.get("verification"))))
    msu = data.get("msu_denver_check")
    ncaa = _load("ncaa_programmes.json") or {}
    for p in ncaa.get("programmes", []):
        if "Metropolitan" in (p.get("institution") or ""):
            conn.execute("UPDATE organisations SET division=?, conference=?, notes=? WHERE id='NCAA-MSUD'",
                         ("Division II", p.get("conference_2026_27") or "RMAC",
                          "NCAA Division II (not Division I). No verified Australian men's basketball connection. "
                          + (json.dumps(msu)[:300] if msu else "")))
    # relationship australian_connection summary
    for r in conn.execute("""SELECT s.organisation_id oid, group_concat(p.name || CASE WHEN s.is_current THEN ' (current)'
                             ELSE COALESCE(' (' || s.seasons || ')','') END, '; ') names
                             FROM player_stints s JOIN players p ON p.id=s.player_id
                             WHERE s.organisation_id IS NOT NULL AND s.verification != 'UNVERIFIED'
                             GROUP BY s.organisation_id""").fetchall():
        conn.execute("UPDATE relationships SET australian_connection=? WHERE organisation_id=?", (r["names"], r["oid"]))


# ------------------------------------------------------------ channels
_KIND = [("authent", "AUTHENTICATOR"), ("auction", "AUCTION_HOUSE"), ("surplus", "UNIVERSITY_SURPLUS"),
         ("marketplace", "MARKETPLACE"), ("government", "MARKETPLACE")]


def seed_channels(conn):
    data = _load("supply_channels.json") or {}
    def _key(n):
        return " ".join(re.sub(r"\(.*?\)", "", n.lower()).split()[:2])
    top = {_key(t["name"]): t for t in data.get("top10_deep_dive", [])}
    for i, ch in enumerate(data.get("channels", []), 1):
        if not ch.get("name"):
            continue
        cid = f"CH-{i:02d}"
        contact = ch.get("contact") or {}
        pub = "; ".join(x for x in [contact.get("email"), contact.get("phone")] if x)
        conn.execute("""INSERT INTO channels(id, name, channel_type, sells, classification_typical, ships_to_au, partner_programme,
                        published_contact, contact_url, fit_score, fit_reason, verification, checked_at) VALUES
                        (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                     (cid, ch["name"], ch.get("channel_type") or "unknown", ch.get("sells"), ch.get("item_class"),
                      ch.get("ships_to_au") or (top.get(_key(ch["name"]), {}).get("international_shipping")),
                      ch.get("partner_programme") or top.get(_key(ch["name"]), {}).get("seller_terms"), pub or None,
                      contact.get("form_url") or contact.get("contact_source_url"),
                      ch.get("fit_score") if isinstance(ch.get("fit_score"), int) else None, ch.get("fit_reason"),
                      _verification(ch.get("verification")), TODAY))
        for u in ch.get("source_urls") or []:
            _src(conn, "channel", cid, u, ch["name"])
        if _key(ch["name"]) in top and not top[_key(ch["name"])].get("_used"):
            ctype = (ch.get("channel_type") or "").lower()
            kind = next((k for key, k in _KIND if key in ctype), "SUPPLIER")
            oid = "SUP-" + _slug(re.sub(r"\(.*?\)", "", ch["name"]))[:30].upper().strip("-")
            t = top[_key(ch["name"])]
            t["_used"] = True
            conn.execute("""INSERT OR IGNORE INTO organisations(id, kind, name, website, notes, verification, researched_at)
                            VALUES (?,?,?,?,?,?,?)""", (oid, kind, ch["name"], t.get("contact_page"), ch.get("sells"),
                                                        _verification(ch.get("verification")), TODAY))
            conn.execute("""INSERT OR IGNORE INTO relationships(organisation_id, commercial_opportunity, approved_purchasing_process,
                            priority, next_action, updated_at) VALUES (?,?,?,?,?,?)""",
                         (oid, t.get("question_to_ask"), t.get("seller_terms"), t.get("rank"),
                          "Confirm contact on live page; founder approval before any enquiry", now_iso()))
            if t.get("contact_page"):
                conn.execute("""INSERT INTO contacts(organisation_id, department, method, value, tier, evidence_url, notes)
                                VALUES (?,?,?,?,?,?,?)""", (oid, "Sales / consignments", "CONTACT_PAGE", t["contact_page"],
                                                            "RESEARCHED_ROUTE", t["contact_page"], "Official site page (seen via search index)"))
            for method, val in (("EMAIL", t.get("published_email")), ("PHONE", t.get("published_phone"))):
                if val and "none" not in str(val).lower() and "not " not in str(val).lower():
                    conn.execute("""INSERT INTO contacts(organisation_id, department, method, value, tier, evidence_url, notes)
                                    VALUES (?,?,?,?,?,?,?)""", (oid, "Sales / consignments", method, val, "UNVERIFIED_LEAD",
                                                                t.get("contact_page"), "Published per search index; confirm live"))


# ------------------------------------------------------------- demand
ESTIMATE_TIERS = {  # popularity, historic_players, international_fanbase, collector_resale, social, iconic_design, rare_supply
    "NBA-LAL": (5, 5, 5, 5, 5, 4, 3), "NBA-GSW": (5, 4, 5, 4, 5, 3, 3), "NBA-CHI": (4, 5, 5, 5, 4, 5, 4),
    "NBA-ORL": (3, 4, 3, 4, 3, 5, 4), "NBA-OKC": (4, 3, 3, 3, 4, 3, 3), "NBA-SAS": (4, 4, 4, 3, 4, 3, 3),
    "NBA-CLE": (3, 4, 3, 3, 3, 3, 3), "NBA-NYK": (5, 4, 4, 4, 5, 4, 3), "NBA-BOS": (5, 5, 4, 4, 5, 3, 3),
    "NBA-ATL": (3, 3, 3, 2, 3, 3, 3), "NBA-TOR": (3, 3, 4, 4, 3, 5, 4), "NBA-UTA": (2, 4, 3, 3, 2, 4, 3),
    "NBA-MIA": (4, 4, 4, 3, 4, 4, 3), "NBA-PHI": (4, 4, 3, 3, 4, 3, 3), "NBA-CHA": (2, 3, 2, 4, 2, 5, 4),
    "NCAA-SMC": (2, 3, 4, 2, 2, 2, 5), "NCAA-DUKE": (5, 5, 4, 4, 4, 3, 3), "NCAA-UNC": (4, 5, 4, 4, 3, 4, 3),
    "NCAA-UK": (4, 4, 3, 4, 3, 3, 3), "NCAA-MICH": (4, 4, 3, 4, 3, 5, 4), "NCAA-GONZ": (3, 3, 3, 2, 3, 2, 4),
}


def seed_demand(conn):
    org_titles = {f"NBA-{t[0]}": t[6] for t in NBA_TEAMS}
    finals_2026 = {"NBA-NYK": 5, "NBA-SAS": 4, "NBA-OKC": 4, "NCAA-MICH": 5, "NCAA-UCONN": 4, "NCAA-ILL": 3, "NCAA-ARIZ": 3}
    finals_src = {"NBA-NYK": "https://www.basketball.com.au/news/jalen-brunson-knicks-spurs-nba-finals-2026-championship",
                  "NBA-SAS": "https://www.basketball.com.au/news/jalen-brunson-knicks-spurs-nba-finals-2026-championship"}
    orgs = [r["id"] for r in conn.execute("SELECT id FROM organisations WHERE kind IN ('NBA_TEAM','NCAA_PROGRAMME')")]
    for oid in orgs:
        f = {}
        if oid in org_titles:
            t = org_titles[oid]
            f["championships"] = (min(5, round(t / 3.6, 1)) if t else 0, "ESTIMATE", f"{t} titles (baseline knowledge, verify)", None)
        conn_row = conn.execute("""SELECT COUNT(DISTINCT s.player_id) n, MAX(s.is_current) cur, MAX(s.champion) ch
                                   FROM player_stints s JOIN players p ON p.id=s.player_id
                                   WHERE s.organisation_id=? AND s.verification!='UNVERIFIED'""", (oid,)).fetchone()
        if conn_row["n"]:
            sc = min(5, conn_row["n"] * 1.5 + (1 if conn_row["cur"] else 0) + (1 if conn_row["ch"] else 0))
            f["australian_connection"] = (sc, "MEASURED", f"{conn_row['n']} sourced Australian player link(s)", None)
        else:
            f["australian_connection"] = (0, "MEASURED", "No sourced Australian link recorded", None)
        if oid in finals_2026:
            f["recent_finals"] = (finals_2026[oid], "MEASURED" if oid in finals_src else "ESTIMATE",
                                  "2025-26 postseason outcome (research agents)", finals_src.get(oid))
        tiers = ESTIMATE_TIERS.get(oid, (2, 2, 2, 2, 2, 2, 2))
        for name, val in zip(["popularity", "historic_players", "international_fanbase", "collector_resale",
                              "social_engagement", "iconic_design", "rare_supply"], tiers):
            f[name] = (val, "ESTIMATE", "Build-team judgement pending measured data", None)
        f["competition"] = (3, "ESTIMATE", "Few Australian sellers specialise in team-issue (unmeasured)", None)
        for name, (score, basis, evidence, url) in f.items():
            conn.execute("""INSERT OR REPLACE INTO demand_factors(organisation_id, factor, score, basis, evidence, source_url, assessed_at)
                            VALUES (?,?,?,?,?,?,?)""", (oid, name, score, basis, evidence, url, TODAY))


# ------------------------------------------------------- opportunities
def _currency(s):
    m = re.search(r"\b(USD|AUD|GBP|EUR|CAD|NZD|JPY)\b", (s or "").upper())
    return m.group(1) if m else ("USD" if "$" in (s or "") else None)


def seed_opportunities(conn):
    data = _load("live_listings_2026-11-05.json") or {}
    skipped = []
    for i, c in enumerate(data.get("candidates", []), 1):
        cur = _currency(c.get("currency"))
        if c.get("listed_price") is None or not cur:
            skipped.append({"title": c.get("title"), "url": c.get("url"), "reason": "No price seen"})
            continue
        ev = []
        size = (c.get("size") or "") + " " + (c.get("title") or "")
        if re.search(r"\b(tall|\dXLT|XLT|LT|\+\s?\d)\b", size, re.I):
            ev.append("TALL_OR_PRO_SIZING")
        ev.append("SELLER_CLAIM_ONLY")
        flags = []
        if "barcode" in (c.get("red_flags") or "").lower() or "retail" in (c.get("red_flags") or "").lower():
            flags.append("VAGUE_DESCRIPTION")
        if not c.get("loaded_directly"):
            flags.append("STOCK_PHOTOS") if False else None
        comps = [{"url": s.get("url"), "price": s.get("price"), "currency": _currency(s.get("currency")) or "USD",
                  "date": s.get("date"), "verified": False, "note": "search snippet; unconfirmed"}
                 for s in c.get("sold_comparables") or [] if s.get("price")]
        ship = c.get("shipping_to_au_if_shown")
        team = c.get("team_or_school")
        conn.execute("""INSERT INTO opportunities(id, found_at, title, organisation_id, team_or_school, player, era, item_type, seller,
                        platform, listing_url, listed_price_cents, currency, shipping_cents, claimed_classification, condition, size,
                        evidence, red_flags, comps, live_verified, is_demo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0)""",
                     (f"LIVE-20261105-{i:02d}", c.get("date_seen") or TODAY, c["title"], _team_id(team) or _school_id(team), team,
                      None, c.get("player_and_era_if_supported"), _item_type(c), c.get("seller"), c.get("platform"), c["url"],
                      int(round(float(c["listed_price"]) * 100)), cur,
                      int(round(float(ship) * 100)) if isinstance(ship, (int, float)) else None,
                      _claim(c.get("claimed_classification")), (c.get("condition") or "").upper() or None, c.get("size"),
                      json.dumps(ev), json.dumps([f for f in flags if f]), json.dumps(comps), int(bool(c.get("loaded_directly")))))
    (C.ROOT / "sourcing" / "unpriced_leads_2026-11-05.json").write_text(json.dumps(skipped, indent=2))
    # one clearly-labelled demo opportunity to exercise the full A-grade path in the UI
    conn.execute("""INSERT INTO opportunities(id, found_at, title, organisation_id, team_or_school, era, season, item_type, seller, platform,
                    listing_url, listed_price_cents, currency, shipping_cents, claimed_classification, condition, size, evidence, red_flags,
                    comps, live_verified, is_demo) VALUES ('DEMO-OPP-01', ?, 'DEMO: 1996-97 team-issued tearaway pants with team LOA',
                    'NBA-CHI', 'Chicago Bulls', 'OG', '1996-97', 'TEARAWAY_PANTS', 'Demo Seller', 'demo', 'https://example.invalid/demo-listing',
                    9000, 'USD', 3500, 'TEAM_ISSUED', 'VERY_GOOD', '2XL+2', ?, '[]', ?, 1, 1)""",
                 (TODAY, json.dumps(["TEAM_LOA", "TEAM_ISSUE_TAG", "TALL_OR_PRO_SIZING"]),
                  json.dumps([{"url": "https://example.invalid/comp1", "price": 240, "currency": "USD", "verified": True},
                              {"url": "https://example.invalid/comp2", "price": 275, "currency": "USD", "verified": True},
                              {"url": "https://example.invalid/comp3", "price": 310, "currency": "USD", "verified": True}])))


def _item_type(c):
    t = ((c.get("item_type") or "") + " " + (c.get("title") or "")).lower()
    for key, val in (("tear", "TEARAWAY_PANTS"), ("snap", "TEARAWAY_PANTS"), ("pant", "TEARAWAY_PANTS"),
                     ("jacket", "WARMUP_JACKET"), ("shooting", "SHOOTING_SHIRT"), ("practice", "PRACTICE"),
                     ("jersey", "JERSEY"), ("shoe", "SHOES"), ("sneaker", "SHOES"), ("suit", "WARMUP_JACKET")):
        if key in t:
            return val
    return "OTHER"


def _claim(s):
    s = (s or "").lower()
    if "game used" in s or "game worn" in s or "game-worn" in s:
        return "GAME_WORN"
    if "player" in s and "worn" in s:
        return "PLAYER_WORN"
    if "player" in s and "issue" in s:
        return "PLAYER_ISSUED"
    if "team" in s or "pro cut" in s or "game issued" in s:
        return "TEAM_ISSUED"
    return "UNKNOWN"


# ----------------------------------------------------------- demo products
DEMO_PRODUCTS = [
    # id, title, dept, collections, era, league, org, season, mfr, item_type, size, cond, claim, evidence, player, player_connection, price, art, story
    ("OCO-DEMO-01", "Orlando Magic | Penny Hardaway Era | Team-Issued Tearaway Warmup Pants",
     "TEARAWAY_VAULT", ["OG_ONCOURT", "TEARAWAY_VAULT"], "OG", "NBA", "NBA-ORL", "1995-96", None, "TEARAWAY_PANTS", "XL+2",
     "VERY_GOOD", "VINTAGE_TEAM_ISSUE", ["CHAIN_OF_CUSTODY", "TEAM_ISSUE_TAG", "TALL_OR_PRO_SIZING"], None,
     "Same era as Penny Hardaway's Orlando tenure. Not linked to any individual player.", 420,
     {"g": "pants", "c1": "#0b0b0b", "c2": "#1d63c7", "c3": "#e8e8e8", "pin": True},
     ("The Magic were the league's newest sensation, reaching the 1995 Finals.",
      "Mid-1990s pinstripe-era Orlando, the peak of Penny Hardaway's popularity.",
      "Full-length side snaps, pro length sizing and team-issue labelling (demo record).",
      "Team-issued warmup pants from this era rarely leave the US.",
      "Pinstripes and full side snaps are the definitive 1990s warmup silhouette.",
      "Pro length sizing (XL+2) is not a standard retail size. Further differences are documented only where verified.")),
    ("OCO-DEMO-02", "Chicago Bulls | 1997-98 Dynasty Season | Team-Issued Warmup Jacket",
     "OG_ONCOURT", ["OG_ONCOURT", "FINALS_VAULT"], "OG", "NBA", "NBA-CHI", "1997-98", None, "WARMUP_JACKET", "2XL",
     "EXCELLENT", "VINTAGE_TEAM_ISSUE", ["TEAM_LOA", "TEAM_ISSUE_TAG"], None,
     "Season of the Bulls' sixth title. Australian Luc Longley started at centre for the 1996-98 champions. "
     "This jacket is not linked to any individual player.", 680,
     {"g": "jacket", "c1": "#c8102e", "c2": "#0b0b0b", "c3": "#ffffff"},
     ("The 1990s Bulls dynasty, six titles in eight seasons.", "1997-98, the final title season.",
      "Full-zip warmup jacket with team-issue tag (demo record).", "Finals-season team issue is heavily collected.",
      "The dynasty is the most collected era in basketball.", None)),
    ("OCO-DEMO-03", "Los Angeles Lakers | Kobe Era 2009-10 | Team-Issued Shooting Shirt",
     "OG_ONCOURT", ["OG_ONCOURT", "FINALS_VAULT"], "OG", "NBA", "NBA-LAL", "2009-10", None, "SHOOTING_SHIRT", "XL",
     "VERY_GOOD", "TEAM_ISSUED", ["CHAIN_OF_CUSTODY", "CONSTRUCTION_MATCH"], None,
     "Championship season of the Kobe Bryant era. Not linked to any individual player; no wear is claimed.", 360,
     {"g": "shirt", "c1": "#552583", "c2": "#fdb927", "c3": "#ffffff"},
     ("Back-to-back champions in 2009 and 2010.", "The late Kobe Bryant era.", "Long-sleeve pre-game shooting shirt (demo).",
      "Season-specific shooting shirts change yearly, so each one is finite.", "Kobe-era Lakers drive global demand.", None)),
    ("OCO-DEMO-04", "Golden State Warriors | 2015 Championship Season | Team-Issued Tearaway Pants",
     "TEARAWAY_VAULT", ["CURRENT_COURT", "TEARAWAY_VAULT", "FINALS_VAULT"], "CURRENT", "NBA", "NBA-GSW", "2014-15", None,
     "TEARAWAY_PANTS", "2XL+2", "EXCELLENT", "TEAM_ISSUED", ["AUTHENTICATOR_CERT", "TALL_OR_PRO_SIZING"], None,
     "The first title of the Stephen Curry era, with Australian Andrew Bogut at centre. Not linked to any individual player.", 520,
     {"g": "pants", "c1": "#1d428a", "c2": "#ffc72c", "c3": "#ffffff"},
     ("The Warriors' 2015 title began a dynasty.", "Curry era, 2014-15.", "Side-snap warmup pants with certificate (demo).",
      "Championship-season issue.", "Bogut's role makes this season special for Australian fans.", None)),
    ("OCO-DEMO-05", "Cleveland Cavaliers | 2016 Championship Season | Team-Issued Shooting Shirt",
     "FINALS_VAULT", ["CURRENT_COURT", "FINALS_VAULT"], "CURRENT", "NBA", "NBA-CLE", "2015-16", None, "SHOOTING_SHIRT", "L",
     "EXCELLENT", "TEAM_ISSUED", ["TEAM_LOA"], None,
     "The 2016 comeback title, won with Australian Matthew Dellavedova on the roster. Not linked to any individual player.", 380,
     {"g": "shirt", "c1": "#860038", "c2": "#fdbb30", "c3": "#041e42"},
     ("Cleveland's first championship.", "2015-16.", "Shooting shirt (demo).", "Finals-season issue.", "Dellavedova connection.", None)),
    ("OCO-DEMO-06", "San Antonio Spurs | 2014 Championship Season | Team-Issued Practice Shirt",
     "FINALS_VAULT", ["CURRENT_COURT", "FINALS_VAULT"], "CURRENT", "NBA", "NBA-SAS", "2013-14", None, "PRACTICE", "XL",
     "VERY_GOOD", "TEAM_ISSUED", ["CHAIN_OF_CUSTODY", "TEAM_ISSUE_TAG"], None,
     "The 2014 title team featured Australians Patty Mills and Aron Baynes. Not linked to any individual player.", 260,
     {"g": "shirt", "c1": "#c4ced4", "c2": "#000000", "c3": "#ffffff"},
     ("Spurs 'beautiful game' champions.", "2013-14.", "Practice shirt (demo).", "Practice gear rarely reaches retail.",
      "Two Australians on one title team.", None)),
    ("OCO-DEMO-07", "Oklahoma City Thunder | 2025 Championship Season | Team-Issued Tearaway Pants",
     "TEARAWAY_VAULT", ["CURRENT_COURT", "TEARAWAY_VAULT", "FINALS_VAULT"], "CURRENT", "NBA", "NBA-OKC", "2024-25", None,
     "TEARAWAY_PANTS", "XL+2", "DEADSTOCK", "TEAM_ISSUED", ["OFFICIAL_SOURCE_PURCHASE"], None,
     "Thunder's 2025 championship season. Australian Josh Giddey played for OKC from 2021 to 2024, before this season.", 450,
     {"g": "pants", "c1": "#007ac1", "c2": "#ef3b24", "c3": "#002d62"},
     ("OKC's first title as the Thunder.", "2024-25.", "Warmup pants bought at an official sale (demo).", "Recent title-season issue.",
      "Modern Finals demand.", None)),
    ("OCO-DEMO-08", "Saint Mary's Gaels | West Coast Conference | Team-Issued Warmup Jacket",
     "COLLEGE_LIFE", ["COLLEGE_LIFE", "CURRENT_COURT"], "CURRENT", "NCAA", "NCAA-SMC", "2023-24", None, "WARMUP_JACKET", "L",
     "VERY_GOOD", "TEAM_ISSUED", ["CHAIN_OF_CUSTODY", "TEAM_ISSUE_TAG", "INTERNAL_CODE"], None,
     "Saint Mary's has a long Australian pipeline including Patty Mills, Matthew Dellavedova and Jock Landale. "
     "This jacket is not linked to any individual player.", 240,
     {"g": "jacket", "c1": "#06315b", "c2": "#d80024", "c3": "#ffffff"},
     ("The Gaels from Moraga, California.", "Modern WCC era.", "Team warmup jacket (demo).",
      "College team issue almost never reaches Australia.", "The Australian connection.", None)),
    ("OCO-DEMO-09", "Duke Blue Devils | Athletics Surplus Sale | Team-Issued Warmup Pants",
     "COLLEGE_LIFE", ["COLLEGE_LIFE", "TEARAWAY_VAULT"], "CURRENT", "NCAA", "NCAA-DUKE", "2022-23", None, "TEARAWAY_PANTS", "XL",
     "GOOD", "TEAM_ISSUED", ["OFFICIAL_SOURCE_PURCHASE"], None,
     "Format demonstration of stock bought at an official university athletics surplus sale. Not linked to any player.", 190,
     {"g": "pants", "c1": "#003087", "c2": "#ffffff", "c3": "#000000"},
     ("Duke men's basketball.", "Recent seasons.", "Warmup pants, official surplus sale receipt (demo).",
      "Public surplus sales are the cleanest provenance route.", "Blue-blood programme.", None)),
    ("OCO-DEMO-10", "Michigan Wolverines | 2025-26 Season | Team-Issued Shooting Shirt",
     "FINALS_VAULT", ["COLLEGE_LIFE", "FINALS_VAULT"], "CURRENT", "NCAA", "NCAA-MICH", "2025-26", None, "SHOOTING_SHIRT", "XL",
     "EXCELLENT", "TEAM_ISSUED", ["OFFICIAL_SOURCE_PURCHASE", "TEAM_ISSUE_TAG"], None,
     "Michigan's 2025-26 season (2026 national champion per research agent sources; verify before publishing).", 260,
     {"g": "shirt", "c1": "#00274c", "c2": "#ffcb05", "c3": "#ffffff"},
     ("Michigan basketball.", "2025-26.", "Shooting shirt (demo).", "Title-season college issue.", "Fab Five heritage brand.", None)),
    ("OCO-DEMO-11", "Atlanta Hawks | 2025-26 Season | Player-Issued Warmup Jacket (Format Demonstration)",
     "CURRENT_COURT", ["CURRENT_COURT"], "CURRENT", "NBA", "NBA-ATL", "2025-26", None, "WARMUP_JACKET", "L+2",
     "EXCELLENT", "PLAYER_ISSUED", ["TEAM_LOA", "PLAYER_NAME_TAG"], None,
     "Shows how a player-issued record is presented. Player-issued means allocated to a player; it does NOT mean worn.", 480,
     {"g": "jacket", "c1": "#e03a3e", "c2": "#26282a", "c3": "#c1d32f"},
     ("Atlanta, home of Australians Dyson Daniels and Jock Landale this season.", "2025-26.",
      "Warmup jacket with sewn name tag (demo, no real player named).", "Player-issued pieces are individually allocated.",
      "Shows the player-issued standard.", None)),
    ("OCO-DEMO-12", "NCAA Programme | Player-Worn Practice Jersey | Exhibit Format Demonstration",
     "PLAYER_WORN", ["PLAYER_WORN"], "CURRENT", "NCAA", None, "2024-25", None, "JERSEY", "XL",
     "GOOD", "PLAYER_WORN", ["TEAM_LOA", "PLAYER_ALLOCATION_DOC", "WEAR_LOA"], None,
     "Format demonstration only: a player-worn piece requires a wear LOA plus allocation evidence. No real player is named.", 900,
     {"g": "jersey", "c1": "#222222", "c2": "#c1ed57", "c3": "#ffffff"},
     ("Format demonstration.", "Format demonstration.", "Practice jersey (demo).",
      "Worn pieces are one of one.", "Shows the evidence premium tier requires.", None)),
    ("OCO-DEMO-13", "Basketball Player Exclusive | Sample Shoe | Kicks Format Demonstration",
     "KICKS_PES", ["KICKS_PES"], "CURRENT", None, None, "2019", None, "SHOES", "US 15",
     "VERY_GOOD", "RARE_KICKS", ["PE_MARKINGS", "GENUINE_MANUFACTURER"], None,
     "Player-exclusive markings with a legit check. No team or player provenance, so no player claim is made.", 650,
     {"g": "shoe", "c1": "#f8f5eb", "c2": "#11151b", "c3": "#c1ed57"},
     ("Format demonstration.", "Modern PE culture.", "PE build markings (demo).", "PEs are made in tiny runs.",
      "Large-size PEs are a collecting niche.", None)),
    ("OCO-DEMO-14", "Toronto Raptors | 1995-99 Expansion Era | Licensed Retail Jacket",
     "LOGO_ARCHIVE", ["LOGO_ARCHIVE"], "OG", "NBA", "NBA-TOR", "1996-97", None, "WARMUP_JACKET", "XL",
     "GOOD", "LICENSED_RETAIL", ["GENUINE_MANUFACTURER"], None,
     "Licensed retail fan apparel from the expansion era. Not team-issued.", 140,
     {"g": "jacket", "c1": "#753bbd", "c2": "#ce1141", "c3": "#000000"},
     ("Toronto's expansion years.", "1995-99.", "Retail fan jacket (demo).", "Era retail jackets are common but loved.",
      "Nostalgia for the original Raptors look.", "This is retail product, sold as retail.")),
    ("OCO-DEMO-15", "Charlotte Hornets | 1990s Pinstripe Era | Licensed Retail Replica Jersey",
     "OG_JERSEYS", ["OG_JERSEYS", "LOGO_ARCHIVE"], "OG", "NBA", "NBA-CHA", "1994-95", None, "JERSEY", "L",
     "VERY_GOOD", "LICENSED_RETAIL", ["GENUINE_MANUFACTURER"], None,
     "Licensed replica jersey from the 1990s teal era. Not team-issued.", 160,
     {"g": "jersey", "c1": "#00788c", "c2": "#1d1160", "c3": "#ffffff", "pin": True},
     ("Charlotte's 1990s popularity peak.", "Mid-1990s.", "Retail replica jersey (demo).", "Common at retail at the time.",
      "One of the most recognisable 1990s looks.", "Replica retail cut, sold as retail.")),
    ("OCO-DEMO-16", "Chicago Bulls | 2025-26 Season | Licensed Retail Swingman Jersey",
     "CURRENT_JERSEYS", ["CURRENT_JERSEYS"], "CURRENT", "NBA", "NBA-CHI", "2025-26", None, "JERSEY", "L",
     "DEADSTOCK", "LICENSED_RETAIL", ["GENUINE_MANUFACTURER"], None,
     "Licensed retail jersey. Australian Josh Giddey plays for Chicago this season. Not team-issued.", 180,
     {"g": "jersey", "c1": "#ce1141", "c2": "#000000", "c3": "#ffffff"},
     ("Chicago's current era.", "2025-26.", "Retail swingman (demo).", "Retail.", "Giddey connection for Australian fans.", "Retail cut.")),
    ("OCO-DEMO-17", "Houston Rockets | 1994-95 Back-to-Back Era | Team-Issued Warmup Pants (Consignment Format)",
     "COLLECTOR_EXCHANGE", ["COLLECTOR_EXCHANGE", "OG_ONCOURT", "TEARAWAY_VAULT"], "OG", "NBA", "NBA-HOU", "1994-95", None,
     "TEARAWAY_PANTS", "2XL+2", "GOOD", "VINTAGE_TEAM_ISSUE", ["AUTHENTICATOR_CERT", "TEAM_ISSUE_TAG"], None,
     "Demonstrates a consigned piece in the Collector Exchange. Not linked to any individual player.", 390,
     {"g": "pants", "c1": "#ce1141", "c2": "#c4ced4", "c3": "#000000"},
     ("Back-to-back champions 1994 and 1995.", "Mid-1990s.", "Warmup pants (demo consignment).",
      "Back-to-back title era pieces are scarce.", "Olajuwon-era nostalgia.", None)),
]


def seed_demo_products(conn):
    for (pid, title, dept, cols, era, league, org, season, mfr, itype, size, cond, claim, ev, player, conn_text, price,
         art, story) in DEMO_PRODUCTS:
        st_team, st_era, st_design, st_rarity, st_why, st_retail = story
        org_name = None
        if org:
            r = conn.execute("SELECT name FROM organisations WHERE id=?", (org,)).fetchone()
            org_name = r["name"] if r else None
        conn.execute("""INSERT INTO products(id, slug, title, department, era, league_id, organisation_id, team_or_school, player_id,
                        player_connection, season, manufacturer, item_type, size, condition_grade, condition_notes,
                        claimed_classification, story_team, story_era, story_design, story_rarity, story_why_collect, story_vs_retail,
                        description, price_cents, ownership, status, stock_qty, stock_confirmed, is_demo, collections, art)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'DEMO','DEMO',0,0,1,?,?)""",
                     (pid, _slug(title), title, dept, era, league, org, org_name, player, conn_text, season, mfr, itype, size, cond,
                      "Demo condition record.", claim, st_team, st_era, st_design, st_rarity, st_why, st_retail,
                      "DEMO EXHIBIT. This record demonstrates how a verified listing will be presented. It is not an item in stock "
                      "and is not for sale. Illustration only; no photograph of a real item is shown.",
                      int(price * 100), json.dumps(cols), json.dumps(art)))
        for code in ev:
            conn.execute("INSERT INTO evidence(product_id, code, detail, reference_id, verified_by) VALUES (?,?,?,?,?)",
                         (pid, code, "Demo evidence record", "DEMO-" + code[:6], "demo"))
        conn.execute("INSERT INTO custody_events(product_id, happened_on, holder, event, documented, note) VALUES (?,?,?,?,?,?)",
                     (pid, season, "Team equipment room (demo)", "ISSUED", 1 if "CHAIN_OF_CUSTODY" in ev else 0, "Demo custody record"))
        conn.execute("INSERT INTO custody_events(product_id, happened_on, holder, event, documented, note) VALUES (?,?,?,?,?,?)",
                     (pid, None, "ON COURT ONLY (demo)", "AUTHENTICATED", 1, "Demo record"))
        conn.execute("""INSERT INTO product_media(product_id, side, match_level, caption, rights_status, credit)
                        VALUES (?, 'ITEM', 'ILLUSTRATION_PLACEHOLDER', 'Original ON COURT ONLY illustration, not a photo of a real item', 'OWNED', 'ON COURT ONLY')""",
                     (pid,))
        conn.execute("""INSERT INTO product_media(product_id, side, match_level, caption, rights_status)
                        VALUES (?, 'REFERENCE', 'REFERENCE_PENDING', ?, 'NONE')""",
                     (pid, f"Reference pending: a licensed archive image of {org_name or 'this design'} {season} equipment in use "
                           "will appear here once rights are cleared."))
    # a non-public draft that fails the gate, to demonstrate the authentication block in admin
    conn.execute("""INSERT INTO products(id, slug, title, department, era, league_id, organisation_id, team_or_school, season, item_type,
                    condition_grade, claimed_classification, description, price_cents, ownership, status, is_demo, collections, art)
                    VALUES ('OCO-DEMO-99', 'demo-blocked-claim', 'DEMO: Seller says game-worn warmup pants (no evidence)', 'PLAYER_WORN',
                    'OG', 'NBA', 'NBA-LAL', 'Los Angeles Lakers', '2001-02', 'TEARAWAY_PANTS', 'GOOD', 'GAME_WORN',
                    'Game-worn by a star, trust me.', 150000, 'DEMO', 'DRAFT', 1, '["PLAYER_WORN"]', '{"g":"pants","c1":"#552583","c2":"#fdb927","c3":"#fff"}')""")
    conn.execute("INSERT INTO evidence(product_id, code, detail) VALUES ('OCO-DEMO-99', 'SELLER_CLAIM_ONLY', 'Seller statement')")


def seed_admin(conn):
    import os
    email = os.environ.get("OCO_ADMIN_EMAIL", "founder@oncourtonly.local")
    pw = os.environ.get("OCO_ADMIN_PASSWORD") or secrets.token_urlsafe(12)
    conn.execute("INSERT INTO users(email, display_name, password_hash, role) VALUES (?,?,?, 'ADMIN')",
                 (email, "Founder", hash_password(pw)))
    if not os.environ.get("OCO_ADMIN_PASSWORD"):
        cred = C.ROOT / "data" / "ADMIN_CREDENTIALS.local"
        cred.write_text(f"email={email}\npassword={pw}\n")
        return email, str(cred)
    return email, "(from environment)"


def _normalise_dashes(conn):
    """House style: no long dashes in any text that reaches reports or the site."""
    for table in ("channels", "organisations", "relationships", "contacts", "sources", "players", "player_stints", "opportunities"):
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})") if r[2] == "TEXT"]
        for col in cols:
            conn.execute(f"UPDATE {table} SET {col} = replace(replace({col}, ' \u2014 ', ', '), '\u2014', '-') WHERE {col} LIKE ?",
                         ("%\u2014%",))


def build(path=None, quiet=False):
    path = Path(path or C.DB_PATH)
    if path.exists():
        path.unlink()
    conn = connect(path)
    init(conn)
    conn.executemany("INSERT INTO leagues(id, name) VALUES (?,?)", [("NBA", "National Basketball Association"),
                                                                    ("NCAA", "NCAA Men's Basketball")])
    seed_nba(conn)
    seed_ncaa(conn)
    seed_australians(conn)
    seed_channels(conn)
    seed_demand(conn)
    seed_opportunities(conn)
    seed_demo_products(conn)
    ensure_slots(conn)
    admin = seed_admin(conn)
    _normalise_dashes(conn)
    conn.commit()
    from sourcing.engine import evaluate_all
    evaluate_all(conn)
    if not quiet:
        counts = {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in
                  ("organisations", "players", "player_stints", "contacts", "channels", "opportunities", "products", "sources")}
        print(json.dumps({"db": str(path), "counts": counts, "admin": admin[0], "admin_credentials": admin[1]}, indent=2))
    return conn


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true")
    ap.add_argument("--db")
    a = ap.parse_args()
    build(a.db)

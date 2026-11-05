"""ON COURT ONLY | local application server (Python 3.11+ standard library only).

    python3 -m commerce.seed --reset     # build the database
    python3 server.py --port 8080        # storefront at /, admin at /#/admin

JSON API under /api, static storefront from ./storefront.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import re
import threading
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from authentication.rules import CLASSES, EVIDENCE, BLOCKING_FLAGS, REFERENCE_LEVELS
from commerce import auth, catalogue, config as C
from commerce.db import audit, connect, jload, one, rows
from operations import budget, consignment, launch
from outreach import crm
from sourcing import demand, engine, search_framework

STATIC = Path(__file__).resolve().parent / "storefront"
MAX_BODY = 64 * 1024
EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,190}\.[a-z]{2,}$", re.I)


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status, self.message = status, message


class App:
    def __init__(self, db_path=None):
        self.conn = connect(db_path)
        self.lock = threading.Lock()
        self.routes = []
        r = self.route
        r("GET", r"/api/health", self.health)
        r("GET", r"/api/departments", self.departments)
        r("GET", r"/api/standards", self.standards)
        r("GET", r"/api/products", self.products)
        r("GET", r"/api/products/(?P<slug>[\w-]+)", self.product)
        r("GET", r"/api/teams", self.teams)
        r("GET", r"/api/teams/(?P<oid>[\w-]+)", self.team)
        r("GET", r"/api/players", self.players)
        r("GET", r"/api/players/(?P<pid>[\w-]+)", self.player)
        r("GET", r"/api/wanted", self.wanted_list)
        r("POST", r"/api/wanted", self.wanted_post)
        r("POST", r"/api/waitlist", self.waitlist)
        r("POST", r"/api/consignments", self.consign)
        r("GET", r"/api/seller-tiers", self.seller_tiers)
        r("POST", r"/api/auth/register", self.register)
        r("POST", r"/api/auth/login", self.login)
        r("POST", r"/api/auth/logout", self.logout)
        r("GET", r"/api/me", self.me)
        r("GET", r"/api/wishlist", self.wishlist)
        r("POST", r"/api/wishlist/(?P<pid>[\w-]+)", self.wishlist_add)
        r("DELETE", r"/api/wishlist/(?P<pid>[\w-]+)", self.wishlist_remove)
        r("POST", r"/api/checkout", self.checkout)
        # admin
        r("GET", r"/api/admin/overview", self.admin_overview, admin=True)
        r("GET", r"/api/admin/opportunities", self.admin_opps, admin=True)
        r("POST", r"/api/admin/opportunities", self.admin_opp_add, admin=True)
        r("POST", r"/api/admin/evaluate", self.admin_evaluate, admin=True)
        r("GET", r"/api/admin/search-plan", self.admin_search_plan, admin=True)
        r("GET", r"/api/admin/crm", self.admin_crm, admin=True)
        r("GET", r"/api/admin/crm/(?P<oid>[\w-]+)", self.admin_crm_org, admin=True)
        r("POST", r"/api/admin/crm/(?P<oid>[\w-]+)/draft", self.admin_draft, admin=True)
        r("POST", r"/api/admin/outreach/(?P<mid>\d+)/approve", self.admin_approve, admin=True)
        r("GET", r"/api/admin/outreach", self.admin_outreach, admin=True)
        r("GET", r"/api/admin/launch", self.admin_launch, admin=True)
        r("GET", r"/api/admin/budget", self.admin_budget, admin=True)
        r("GET", r"/api/admin/products", self.admin_products, admin=True)
        r("GET", r"/api/admin/consignments", self.admin_consignments, admin=True)
        r("POST", r"/api/admin/consignments/(?P<cid>\d+)/advance", self.admin_consign_advance, admin=True)
        r("GET", r"/api/admin/wanted", self.admin_wanted, admin=True)
        r("POST", r"/api/admin/wanted/(?P<wid>\d+)", self.admin_wanted_moderate, admin=True)
        r("GET", r"/api/admin/demand", self.admin_demand, admin=True)
        r("GET", r"/api/admin/channels", self.admin_channels, admin=True)
        r("GET", r"/api/admin/players", self.admin_players, admin=True)
        r("GET", r"/api/admin/waitlist", self.admin_waitlist, admin=True)
        r("GET", r"/api/admin/audit", self.admin_audit, admin=True)

    def route(self, method, pattern, fn, admin=False):
        self.routes.append((method, re.compile("^" + pattern + "$"), fn, admin))

    def dispatch(self, method, path, query, body, user):
        for m, rx, fn, admin in self.routes:
            match = rx.match(path)
            if match and m == method:
                if admin and (not user or user["role"] != "ADMIN"):
                    raise ApiError(401 if not user else 403, "Admin sign-in required")
                with self.lock:
                    return fn(query=query, body=body, user=user, **match.groupdict())
        raise ApiError(404, "Not found")

    # ------------------------------------------------------------- public
    def health(self, **_):
        return {"ok": True, "products": one(self.conn, "SELECT COUNT(*) n FROM products")["n"],
                "checkout": "DISABLED (no payment provider configured)"}

    def departments(self, **_):
        out = []
        for code, d in catalogue.DEPARTMENTS.items():
            n = one(self.conn, """SELECT COUNT(*) n FROM products WHERE status IN ('DEMO','LISTED','RESERVED','SOLD')
                                  AND (department=? OR collections LIKE ?)""", (code, f'%"{code}"%'))["n"]
            out.append({"code": code, **d, "count": n})
        return out

    def standards(self, **_):
        return {"classes": CLASSES, "evidence": {k: {"tier": v[0], "meaning": v[1]} for k, v in EVIDENCE.items()},
                "blocking_flags": BLOCKING_FLAGS, "reference_levels": REFERENCE_LEVELS}

    def products(self, query, **_):
        q = {k: v[0] for k, v in query.items()}
        return catalogue.search(self.conn, q=q.get("q"), department=q.get("department"), era=q.get("era"),
                                league=q.get("league"), team=q.get("team"), item_type=q.get("item_type"),
                                classification=q.get("classification"), sort=q.get("sort", "featured"))

    def product(self, slug, **_):
        p = one(self.conn, "SELECT * FROM products WHERE slug=? AND status IN ('DEMO','LISTED','RESERVED','SOLD')", (slug,))
        if not p:
            raise ApiError(404, "Product not found")
        return catalogue.present(self.conn, p, full=True)

    def teams(self, query, **_):
        league = (query.get("league") or [None])[0]
        sql = """SELECT o.id, o.name, o.kind, o.league_id, o.conference, o.division, o.city, o.nickname, o.iconic_era,
                 o.recent_success, r.australian_connection,
                 (SELECT COUNT(*) FROM products p WHERE p.organisation_id=o.id AND p.status IN ('DEMO','LISTED')) products
                 FROM organisations o LEFT JOIN relationships r ON r.organisation_id=o.id
                 WHERE o.kind IN ('NBA_TEAM','NCAA_PROGRAMME')"""
        params = []
        if league:
            sql += " AND o.league_id=?"
            params.append(league)
        return rows(self.conn, sql + " ORDER BY o.league_id DESC, o.name", params)

    def team(self, oid, **_):
        o = one(self.conn, """SELECT o.*, r.australian_connection FROM organisations o
                              LEFT JOIN relationships r ON r.organisation_id=o.id WHERE o.id=?""", (oid,))
        if not o or o["kind"] not in ("NBA_TEAM", "NCAA_PROGRAMME"):
            raise ApiError(404, "Team not found")
        o["products"] = catalogue.search(self.conn, team=oid)
        o["players"] = rows(self.conn, """SELECT p.id, p.name, p.status, s.seasons, s.is_current, s.champion, s.verification
                                         FROM player_stints s JOIN players p ON p.id=s.player_id WHERE s.organisation_id=?
                                         ORDER BY s.is_current DESC, s.champion DESC""", (oid,))
        o["sources"] = rows(self.conn, "SELECT url, supports, checked_at FROM sources WHERE entity_type='organisation' AND entity_id=? LIMIT 12", (oid,))
        o.pop("notes", None)
        return o

    def players(self, **_):
        return rows(self.conn, """SELECT p.id, p.name, p.status, p.college, p.achievements, p.verification,
                                  group_concat(s.organisation_name || COALESCE(' ' || s.seasons, ''), '; ') stints
                                  FROM players p LEFT JOIN player_stints s ON s.player_id=p.id
                                  WHERE p.is_australian=1 GROUP BY p.id ORDER BY p.status, p.name""")

    def player(self, pid, **_):
        p = one(self.conn, "SELECT * FROM players WHERE id=?", (pid,))
        if not p:
            raise ApiError(404, "Player not found")
        p["stints"] = rows(self.conn, "SELECT organisation_id, organisation_name, seasons, is_current, champion, verification FROM player_stints WHERE player_id=?", (pid,))
        p["sources"] = rows(self.conn, "SELECT url, supports FROM sources WHERE entity_type='player' AND entity_id=?", (pid,))
        p["products"] = [catalogue.present(self.conn, dict(r)) for r in self.conn.execute(
            "SELECT * FROM products WHERE status IN ('DEMO','LISTED') AND organisation_id IN (SELECT organisation_id FROM player_stints WHERE player_id=?)", (pid,))]
        return p

    def wanted_list(self, **_):
        return rows(self.conn, "SELECT id, display_name, team_or_school, era, item_type, description, budget_aud_cents, status, created_at "
                               "FROM wanted_posts WHERE status IN ('OPEN','MATCHED') ORDER BY id DESC LIMIT 100")

    def wanted_post(self, body, user, **_):
        desc = _text(body, "description", 1000, required=True)
        name = _text(body, "display_name", 60) or (user["display_name"] if user else None)
        if not name:
            raise ApiError(400, "Display name required")
        b = body.get("budget_aud")
        cur = self.conn.execute("""INSERT INTO wanted_posts(user_id, display_name, team_or_school, era, item_type, description, budget_aud_cents)
                                   VALUES (?,?,?,?,?,?,?)""",
                                (user["id"] if user else None, name, _text(body, "team_or_school", 80), _text(body, "era", 10),
                                 _text(body, "item_type", 40), desc, int(float(b) * 100) if b else None))
        self.conn.commit()
        return {"id": cur.lastrowid, "status": "PENDING_MODERATION",
                "message": "Thanks. Wanted posts appear once a moderator approves them."}

    def waitlist(self, body, **_):
        email = _text(body, "email", 200, required=True).lower()
        if not EMAIL_RE.match(email):
            raise ApiError(400, "Please enter a valid email")
        if not body.get("consent"):
            raise ApiError(400, "Please tick the consent box so we can email you")
        consent_text = "I agree to receive ON COURT ONLY launch and drop emails. I can unsubscribe at any time."
        self.conn.execute("""INSERT INTO waitlist(email, era_preference, teams, consent_marketing, consent_text, source)
                             VALUES (?,?,?,?,?,?) ON CONFLICT(email) DO UPDATE SET era_preference=excluded.era_preference,
                             teams=excluded.teams, unsubscribed=0""",
                          (email, _text(body, "era", 10), _text(body, "teams", 200), 1, consent_text, _text(body, "source", 40)))
        self.conn.commit()
        return {"ok": True, "message": "You're on the list. We only email when there is something real to show you."}

    def consign(self, body, **_):
        try:
            return consignment.submit(self.conn, body)
        except consignment.ConsignmentError as e:
            raise ApiError(400, str(e))

    def seller_tiers(self, **_):
        return consignment.SELLER_TIERS

    def register(self, body, **_):
        email = _text(body, "email", 200, required=True).lower()
        if not EMAIL_RE.match(email):
            raise ApiError(400, "Valid email required")
        if one(self.conn, "SELECT id FROM users WHERE email=?", (email,)):
            raise ApiError(409, "An account with that email exists")
        try:
            ph = auth.hash_password(body.get("password") or "")
        except ValueError as e:
            raise ApiError(400, str(e))
        cur = self.conn.execute("INSERT INTO users(email, display_name, password_hash) VALUES (?,?,?)",
                                (email, _text(body, "display_name", 60) or email.split("@")[0], ph))
        self.conn.commit()
        return {"_session": auth.create_session(self.conn, cur.lastrowid), "ok": True}

    def login(self, body, **_):
        email = (body.get("email") or "").strip().lower()
        u = one(self.conn, "SELECT * FROM users WHERE email=?", (email,))
        if not u or not auth.verify_password(body.get("password") or "", u["password_hash"]):
            raise ApiError(401, "Email or password is incorrect")
        return {"_session": auth.create_session(self.conn, u["id"]), "ok": True, "role": u["role"]}

    def logout(self, user, body, **kw):
        return {"_logout": True, "ok": True}

    def me(self, user, **_):
        return user or {"anonymous": True}

    def _need_user(self, user):
        if not user:
            raise ApiError(401, "Sign in required")

    def wishlist(self, user, **_):
        self._need_user(user)
        return [catalogue.present(self.conn, dict(r)) for r in self.conn.execute(
            "SELECT p.* FROM wishlist w JOIN products p ON p.id=w.product_id WHERE w.user_id=? ORDER BY w.added_at DESC", (user["id"],))]

    def wishlist_add(self, user, pid, **_):
        self._need_user(user)
        if not one(self.conn, "SELECT id FROM products WHERE id=? AND status IN ('DEMO','LISTED','RESERVED','SOLD')", (pid,)):
            raise ApiError(404, "Product not found")
        self.conn.execute("INSERT OR IGNORE INTO wishlist(user_id, product_id) VALUES (?,?)", (user["id"], pid))
        self.conn.commit()
        return {"ok": True}

    def wishlist_remove(self, user, pid, **_):
        self._need_user(user)
        self.conn.execute("DELETE FROM wishlist WHERE user_id=? AND product_id=?", (user["id"], pid))
        self.conn.commit()
        return {"ok": True}

    def checkout(self, body, user, **_):
        ids = body.get("product_ids") or []
        if not ids:
            raise ApiError(400, "Cart is empty")
        problems = []
        for pid in ids:
            p = one(self.conn, "SELECT * FROM products WHERE id=?", (pid,))
            ok, why = catalogue.can_purchase(p) if p else (False, "Unknown product")
            if not ok:
                problems.append({"product_id": pid, "reason": why})
        if problems:
            raise ApiError(409, "Some items cannot be purchased: " + "; ".join(f"{x['product_id']}: {x['reason']}" for x in problems))
        raise ApiError(503, "Checkout is not enabled: no payment provider is configured. See commerce/CHECKOUT_ARCHITECTURE.md")

    # -------------------------------------------------------------- admin
    def admin_overview(self, **_):
        res = [dict(r) for r in self.conn.execute("SELECT * FROM opportunities")]
        summ = engine.daily_summary([{**r, "recommendation": r["recommendation"]} for r in res])
        tr = launch.tracker(self.conn)
        return {
            "sourcing": summ,
            "launch": {"ready_total": tr["ready_total"], "ready": tr["ready"], "target": tr["target"], "launch_ready": tr["launch_ready"]},
            "budget": budget.summary(self.conn),
            "crm": rows(self.conn, "SELECT COALESCE(r.status,'NOT_CONTACTED') status, COUNT(*) n FROM organisations o LEFT JOIN relationships r "
                                   "ON r.organisation_id=o.id WHERE o.kind IN ('NBA_TEAM','NCAA_PROGRAMME') OR r.priority IS NOT NULL GROUP BY 1"),
            "contacts": rows(self.conn, "SELECT tier, COUNT(*) n FROM contacts GROUP BY tier"),
            "registers": {t: one(self.conn, f"SELECT COUNT(*) n FROM {t}")["n"] for t in
                          ("organisations", "players", "player_stints", "channels", "contacts", "sources", "products", "consignments",
                           "wanted_posts", "waitlist", "users")},
            "outreach": rows(self.conn, "SELECT status, COUNT(*) n FROM outreach_messages GROUP BY status"),
            "agent_runs": rows(self.conn, "SELECT agent, started_at, ok, summary FROM agent_runs ORDER BY id DESC LIMIT 15"),
        }

    def admin_opps(self, query, **_):
        q = {k: v[0] for k, v in query.items()}
        sql, params = "SELECT * FROM opportunities WHERE 1=1", []
        for key, col in (("recommendation", "recommendation"), ("risk", "risk_grade"), ("classification", "supported_classification")):
            if q.get(key):
                sql += f" AND {col}=?"
                params.append(q[key])
        if q.get("live") == "1":
            sql += " AND is_demo=0"
        if q.get("q"):
            sql += " AND (title LIKE ? OR team_or_school LIKE ?)"
            params += [f"%{q['q']}%"] * 2
        if q.get("max_landed"):
            sql += " AND landed_cost_aud_cents <= ?"
            params.append(int(float(q["max_landed"]) * 100))
        sort = {"score": "deal_score DESC", "margin": "gross_margin_pct DESC", "landed": "landed_cost_aud_cents ASC",
                "demand": "demand_score DESC"}.get(q.get("sort", "score"), "deal_score DESC")
        out = rows(self.conn, sql + f" ORDER BY {sort}", params)
        for o in out:
            for k in ("evidence", "red_flags", "comps", "rejection_reasons"):
                o[k] = jload(o[k])
        return out

    def admin_opp_add(self, body, user, **_):
        need = ["title", "listing_url", "listed_price", "currency"]
        miss = [k for k in need if not body.get(k)]
        if miss:
            raise ApiError(400, "Missing " + ", ".join(miss))
        if not re.match(r"^https?://", body["listing_url"]):
            raise ApiError(400, "listing_url must be a real http(s) URL")
        if body["currency"].upper() not in C.FX_TO_AUD:
            raise ApiError(400, "Unsupported currency")
        oid = "MAN-" + re.sub(r"\D", "", engine.now_iso())[:14]
        self.conn.execute("""INSERT INTO opportunities(id, found_at, title, organisation_id, team_or_school, player, era, season, item_type,
                             seller, platform, listing_url, listed_price_cents, currency, shipping_cents, claimed_classification, condition,
                             size, evidence, red_flags, comps, live_verified) VALUES (?,date('now'),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                          (oid, body["title"][:300], body.get("organisation_id"), body.get("team_or_school"), body.get("player"),
                           body.get("era"), body.get("season"), body.get("item_type") or "OTHER", body.get("seller"), body.get("platform"),
                           body["listing_url"], int(float(body["listed_price"]) * 100), body["currency"].upper(),
                           int(float(body["shipping"]) * 100) if body.get("shipping") not in (None, "") else None,
                           body.get("claimed_classification"), (body.get("condition") or "").upper() or None, body.get("size"),
                           json.dumps(body.get("evidence") or []), json.dumps(body.get("red_flags") or []),
                           json.dumps(body.get("comps") or []), int(bool(body.get("live_verified")))))
        audit(self.conn, user["email"], "OPPORTUNITY_ADD", "opportunity", oid)
        self.conn.commit()
        engine.evaluate_all(self.conn)
        return one(self.conn, "SELECT * FROM opportunities WHERE id=?", (oid,))

    def admin_evaluate(self, **_):
        res = engine.evaluate_all(self.conn)
        return engine.daily_summary(res)

    def admin_search_plan(self, **_):
        top = [r for r in demand.rank(self.conn)][:8]
        teams = [{"name": t["name"], "era": "OG" if i % 2 == 0 else "CURRENT"} for i, t in enumerate(top)]
        return {"generated_for": [t["name"] for t in teams], "plan": search_framework.plan(teams, per_team=5),
                "note": "Human-reviewed public search links. No scraping; follow each platform's terms."}

    def admin_crm(self, query, **_):
        kind = (query.get("kind") or [None])[0]
        data = crm.pipeline(self.conn)
        return [d for d in data if not kind or d["kind"] == kind]

    def admin_crm_org(self, oid, **_):
        o = one(self.conn, "SELECT * FROM organisations WHERE id=?", (oid,))
        if not o:
            raise ApiError(404, "Not found")
        o["relationship"] = one(self.conn, "SELECT * FROM relationships WHERE organisation_id=?", (oid,))
        o["contacts"] = rows(self.conn, "SELECT * FROM contacts WHERE organisation_id=?", (oid,))
        o["messages"] = rows(self.conn, "SELECT * FROM outreach_messages WHERE organisation_id=? ORDER BY id", (oid,))
        o["facts"] = crm.verified_facts(self.conn, oid)
        o["sources"] = rows(self.conn, "SELECT url, supports, checked_at FROM sources WHERE entity_type='organisation' AND entity_id=?", (oid,))
        return o

    def admin_draft(self, oid, body, user, **_):
        try:
            return crm.draft_initial(self.conn, oid, body.get("founder_name") or "[FOUNDER NAME]", actor=user["email"])
        except crm.OutreachError as e:
            raise ApiError(400, str(e))

    def admin_approve(self, mid, body, **_):
        try:
            crm.approve(self.conn, int(mid), body.get("founder_name"))
        except crm.OutreachError as e:
            raise ApiError(400, str(e))
        return {"ok": True, "note": "Approved. Nothing has been sent: this system cannot send email."}

    def admin_outreach(self, **_):
        return rows(self.conn, """SELECT m.id, m.organisation_id, o.name, m.sequence_step, m.subject, m.status, m.created_at, m.approved_by,
                                  m.sent_at FROM outreach_messages m JOIN organisations o ON o.id=m.organisation_id ORDER BY m.id DESC""")

    def admin_launch(self, **_):
        return launch.tracker(self.conn)

    def admin_budget(self, **_):
        s = budget.summary(self.conn)
        s["lines"] = rows(self.conn, "SELECT * FROM acquisitions ORDER BY id DESC")
        return s

    def admin_products(self, **_):
        return [{**catalogue.present(self.conn, dict(p)), "gate": launch.gate(self.conn, p["id"])}
                for p in self.conn.execute("SELECT * FROM products ORDER BY id")]

    def admin_consignments(self, **_):
        return rows(self.conn, "SELECT * FROM consignments ORDER BY id DESC")

    def admin_consign_advance(self, cid, body, user, **_):
        try:
            return consignment.advance(self.conn, int(cid), body.get("status"), user["email"], body.get("notes"),
                                       **{k: body[k] for k in ("agreement_ref", "product_id", "commission_pct") if k in body})
        except consignment.ConsignmentError as e:
            raise ApiError(400, str(e))

    def admin_wanted(self, **_):
        return rows(self.conn, "SELECT * FROM wanted_posts ORDER BY id DESC")

    def admin_wanted_moderate(self, wid, body, user, **_):
        st = body.get("status")
        if st not in ("OPEN", "REJECTED", "CLOSED", "MATCHED"):
            raise ApiError(400, "Bad status")
        self.conn.execute("UPDATE wanted_posts SET status=? WHERE id=?", (st, int(wid)))
        audit(self.conn, user["email"], "WANTED_" + st, "wanted_post", wid)
        self.conn.commit()
        return {"ok": True}

    def admin_demand(self, **_):
        out = demand.rank(self.conn)
        for r in out:
            r["factors"] = rows(self.conn, "SELECT factor, score, basis, evidence, source_url FROM demand_factors WHERE organisation_id=?",
                                (r["organisation_id"],))
        return out

    def admin_channels(self, **_):
        return rows(self.conn, "SELECT * FROM channels ORDER BY COALESCE(fit_score,0) DESC, name")

    def admin_players(self, **_):
        return self.players()

    def admin_waitlist(self, **_):
        return {"count": one(self.conn, "SELECT COUNT(*) n FROM waitlist WHERE unsubscribed=0")["n"],
                "rows": rows(self.conn, "SELECT email, era_preference, teams, created_at FROM waitlist ORDER BY id DESC LIMIT 200")}

    def admin_audit(self, **_):
        return rows(self.conn, "SELECT * FROM audit_log ORDER BY id DESC LIMIT 200")


def _text(body, key, maxlen, required=False):
    v = body.get(key)
    v = v.strip() if isinstance(v, str) else None
    if required and not v:
        raise ApiError(400, f"{key.replace('_', ' ').capitalize()} is required")
    return v[:maxlen] if v else None


SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                               "font-src https://fonts.gstatic.com; script-src 'self'; connect-src 'self'; frame-ancestors 'none'",
}


def make_handler(app: App):
    class Handler(BaseHTTPRequestHandler):
        server_version = "OnCourtOnly/1.0"

        def log_message(self, fmt, *args):
            if getattr(self.server, "verbose", True):
                super().log_message(fmt, *args)

        def _user(self):
            c = cookies.SimpleCookie(self.headers.get("Cookie", ""))
            tok = c["oco_session"].value if "oco_session" in c else None
            return auth.user_for_token(app.conn, tok), tok

        def _send(self, status, payload, extra_headers=None):
            data = json.dumps(payload, default=str).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            for k, v in {**SECURITY_HEADERS, **(extra_headers or {})}.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(data)

        def _api(self, method):
            url = urlparse(self.path)
            body = {}
            if method in ("POST", "DELETE"):
                if self.headers.get("X-Requested-With") != "oco":
                    return self._send(403, {"error": "Missing X-Requested-With header"})
                n = int(self.headers.get("Content-Length") or 0)
                if n > MAX_BODY:
                    return self._send(413, {"error": "Request too large"})
                if n:
                    try:
                        body = json.loads(self.rfile.read(n) or b"{}")
                    except ValueError:
                        return self._send(400, {"error": "Invalid JSON"})
                    if not isinstance(body, dict):
                        return self._send(400, {"error": "JSON object expected"})
            user, tok = self._user()
            try:
                res = app.dispatch(method, url.path, parse_qs(url.query), body, user)
            except ApiError as e:
                return self._send(e.status, {"error": e.message})
            except Exception as e:  # pragma: no cover
                self.log_error("API error: %r", e)
                return self._send(500, {"error": "Internal error"})
            headers = {}
            if isinstance(res, dict) and "_session" in res:
                headers["Set-Cookie"] = (f"oco_session={res.pop('_session')}; Path=/; HttpOnly; SameSite=Strict; "
                                         f"Max-Age={auth.SESSION_DAYS * 86400}")
            if isinstance(res, dict) and res.pop("_logout", False):
                if tok:
                    auth.destroy_session(app.conn, tok)
                headers["Set-Cookie"] = "oco_session=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0"
            self._send(200, res, headers)

        def _static(self):
            path = urlparse(self.path).path
            rel = "index.html" if path in ("/", "") else path.lstrip("/")
            target = (STATIC / rel).resolve()
            inside = STATIC.resolve() in target.parents
            if not inside or not target.is_file():
                target = STATIC / "index.html"
            data = target.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mimetypes.guess_type(str(target))[0] or "application/octet-stream")
            self.send_header("Content-Length", str(len(data)))
            for k, v in SECURITY_HEADERS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path.startswith("/api/"):
                return self._api("GET")
            return self._static()

        def do_POST(self):
            return self._api("POST")

        def do_DELETE(self):
            return self._api("DELETE")

    return Handler


def serve(port=8080, host="127.0.0.1", db=None, verbose=True):
    app = App(db)
    srv = ThreadingHTTPServer((host, port), make_handler(app))
    srv.verbose = verbose
    return srv, app


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--db")
    a = ap.parse_args()
    if not (a.db or C.DB_PATH.exists()):
        raise SystemExit("No database. Run: python3 -m commerce.seed --reset")
    srv, _ = serve(a.port, a.host, a.db)
    print(f"ON COURT ONLY running at http://{a.host}:{a.port}")
    srv.serve_forever()

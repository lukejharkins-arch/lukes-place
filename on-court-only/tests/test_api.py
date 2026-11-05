"""HTTP-level tests against a real server on a temporary database."""
import json
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.cookiejar import CookieJar

os.environ["OCO_ADMIN_PASSWORD"] = "test-password-123"
os.environ["OCO_ADMIN_EMAIL"] = "founder@oncourtonly.local"

from commerce import seed
import server


class Api(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        path = os.path.join(cls.tmp.name, "api.db")
        seed.build(path, quiet=True).close()
        cls.srv, _ = server.serve(0, "127.0.0.1", path, verbose=False)
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.tmp.cleanup()

    def req(self, path, method="GET", body=None, opener=None, csrf=True):
        data = json.dumps(body).encode() if body is not None else (b"{}" if method != "GET" else None)
        r = urllib.request.Request(self.base + path, data=data, method=method)
        r.add_header("Content-Type", "application/json")
        if csrf and method != "GET":
            r.add_header("X-Requested-With", "oco")
        try:
            resp = (opener or urllib.request.build_opener()).open(r)
            return resp.status, json.loads(resp.read() or b"null"), resp.headers
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"null"), e.headers

    def session(self):
        return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))

    def test_health_and_security_headers(self):
        s, d, h = self.req("/api/health")
        self.assertEqual(s, 200)
        self.assertIn("DISABLED", d["checkout"])
        self.assertEqual(h["X-Frame-Options"], "DENY")
        self.assertIn("default-src 'self'", h["Content-Security-Policy"])

    def test_catalogue_and_filters(self):
        _, all_, _ = self.req("/api/products")
        _, og, _ = self.req("/api/products?era=OG")
        self.assertTrue(all(p["era"] == "OG" for p in og))
        self.assertLess(len(og), len(all_))
        _, vault, _ = self.req("/api/products?department=TEARAWAY_VAULT")
        self.assertTrue(all(p["item_type"] == "TEARAWAY_PANTS" for p in vault))
        self.assertFalse(any(p["purchasable"] for p in all_))
        self.assertFalse(any(p["id"] == "OCO-DEMO-99" for p in all_))  # drafts stay private

    def test_product_detail_storytelling(self):
        _, items, _ = self.req("/api/products?department=TEARAWAY_VAULT")
        s, p, _ = self.req("/api/products/" + items[0]["slug"])
        self.assertEqual(s, 200)
        sides = {m["side"] for m in p["media"]}
        self.assertEqual(sides, {"ITEM", "REFERENCE"})
        ref = next(m for m in p["media"] if m["side"] == "REFERENCE")
        self.assertIsNone(ref["url"])            # no rights -> nothing displayed
        self.assertIn("authentication", p)

    def test_draft_product_hidden(self):
        self.assertEqual(self.req("/api/products/demo-blocked-claim")[0], 404)

    def test_teams(self):
        _, nba, _ = self.req("/api/teams?league=NBA")
        self.assertEqual(len(nba), 30)
        s, t, _ = self.req("/api/teams/NBA-GSW")
        self.assertEqual(s, 200)
        self.assertTrue(any("Bogut" in p["name"] for p in t["players"]))

    def test_checkout_refuses_demo(self):
        s, d, _ = self.req("/api/checkout", "POST", {"product_ids": ["OCO-DEMO-01"]})
        self.assertEqual(s, 409)
        self.assertIn("Demo", d["error"])

    def test_csrf_header_required(self):
        self.assertEqual(self.req("/api/waitlist", "POST", {"email": "a@b.com", "consent": True}, csrf=False)[0], 403)

    def test_waitlist_requires_consent(self):
        self.assertEqual(self.req("/api/waitlist", "POST", {"email": "fan@example.com"})[0], 400)
        self.assertEqual(self.req("/api/waitlist", "POST", {"email": "fan@example.com", "consent": True})[0], 200)
        self.assertEqual(self.req("/api/waitlist", "POST", {"email": "not-an-email", "consent": True})[0], 400)

    def test_admin_requires_admin(self):
        self.assertEqual(self.req("/api/admin/overview")[0], 401)
        op = self.session()
        self.req("/api/auth/register", "POST", {"email": "cust@example.com", "password": "longenough1"}, opener=op)
        self.assertEqual(self.req("/api/admin/overview", opener=op)[0], 403)

    def test_admin_flow(self):
        op = self.session()
        s, _, _ = self.req("/api/auth/login", "POST", {"email": "founder@oncourtonly.local", "password": "test-password-123"}, opener=op)
        self.assertEqual(s, 200)
        s, ov, _ = self.req("/api/admin/overview", opener=op)
        self.assertEqual(s, 200)
        self.assertEqual(ov["sourcing"]["target"], 20)
        self.assertEqual(self.req("/api/admin/launch", opener=op)[1]["ready_total"], 0)
        s, opps, _ = self.req("/api/admin/opportunities?live=1", opener=op)
        self.assertTrue(all(not o["is_demo"] for o in opps))
        s, new, _ = self.req("/api/admin/opportunities", "POST", {"title": "x", "listing_url": "ftp://bad", "listed_price": 5, "currency": "USD"}, opener=op)
        self.assertEqual(s, 400)

    def test_login_wrong_password(self):
        self.assertEqual(self.req("/api/auth/login", "POST", {"email": "founder@oncourtonly.local", "password": "nope"})[0], 401)

    def test_wishlist(self):
        op = self.session()
        self.assertEqual(self.req("/api/wishlist", opener=op)[0], 401)
        self.req("/api/auth/register", "POST", {"email": "wish@example.com", "password": "longenough1"}, opener=op)
        self.assertEqual(self.req("/api/wishlist/OCO-DEMO-01", "POST", opener=op)[0], 200)
        self.assertEqual(len(self.req("/api/wishlist", opener=op)[1]), 1)
        self.assertEqual(self.req("/api/wishlist/OCO-DEMO-99", "POST", opener=op)[0], 404)

    def test_wanted_is_moderated(self):
        s, d, _ = self.req("/api/wanted", "POST", {"display_name": "Kim", "description": "1996 Bulls warmup pants XL"})
        self.assertEqual(d["status"], "PENDING_MODERATION")
        self.assertFalse(any(p["id"] == d["id"] for p in self.req("/api/wanted")[1]))

    def test_consignment_endpoint(self):
        s, d, _ = self.req("/api/consignments", "POST", {"applicant_name": "Jo", "applicant_email": "jo@example.com",
                                                          "item_description": "Spurs practice shirt", "evidence_offered": ["SELLER_CLAIM_ONLY"]})
        self.assertEqual(s, 200)
        self.assertEqual(d["preliminary_assessment"]["supported"], "UNVERIFIED")

    def test_static_and_traversal(self):
        r = urllib.request.urlopen(self.base + "/")
        self.assertIn(b"ON COURT ONLY", r.read())
        r = urllib.request.urlopen(self.base + "/..%2f..%2fserver.py")
        self.assertNotIn(b"ThreadingHTTPServer", r.read())

    def test_body_limit(self):
        s, _, _ = self.req("/api/wanted", "POST", {"display_name": "x", "description": "y" * 70000})
        self.assertEqual(s, 413)


if __name__ == "__main__":
    unittest.main()

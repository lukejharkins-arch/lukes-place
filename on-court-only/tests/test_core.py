"""Unit tests for the business rules. Run: python3 -m unittest discover -s tests -v"""
import json
import os
import tempfile
import unittest

os.environ["OCO_ADMIN_PASSWORD"] = "test-password-123"

from authentication.rules import classify, claim_allowed, lint_copy, check_media
from sourcing import economics as E, engine, search_framework, demand
from commerce import seed
from operations import budget, consignment, launch
from outreach import crm


class Authentication(unittest.TestCase):
    def test_seller_claim_alone_is_unverified(self):
        a = classify(["SELLER_CLAIM_ONLY"], "TEARAWAY_PANTS", "1996-97")
        self.assertEqual(a.supported, "UNVERIFIED")
        self.assertFalse(a.listable)

    def test_genuine_only_is_retail(self):
        self.assertEqual(classify(["GENUINE_MANUFACTURER"]).supported, "LICENSED_RETAIL")

    def test_construction_alone_is_not_team_issue(self):
        a = classify(["GENUINE_MANUFACTURER", "TALL_OR_PRO_SIZING"], "TEARAWAY_PANTS", "2001-02")
        self.assertEqual(a.supported, "LICENSED_RETAIL")

    def test_team_loa_vintage(self):
        a = classify(["TEAM_LOA"], "TEARAWAY_PANTS", "1997-98")
        self.assertEqual((a.supported, a.confidence), ("VINTAGE_TEAM_ISSUE", "HIGH"))

    def test_modern_team_issue(self):
        self.assertEqual(classify(["AUTHENTICATOR_CERT"], "JERSEY", "2024-25").supported, "TEAM_ISSUED")

    def test_custody_plus_construction_medium(self):
        a = classify(["CHAIN_OF_CUSTODY", "TEAM_ISSUE_TAG"], "PRACTICE", "2015-16")
        self.assertEqual((a.supported, a.confidence), ("TEAM_ISSUED", "MEDIUM"))

    def test_player_issued_is_not_player_worn(self):
        a = classify(["TEAM_LOA", "PLAYER_NAME_TAG"], "WARMUP_JACKET", "2020-21")
        self.assertEqual(a.supported, "PLAYER_ISSUED")
        self.assertFalse(claim_allowed("PLAYER_WORN", a.supported))
        self.assertFalse(claim_allowed("GAME_WORN", a.supported))

    def test_wear_needs_allocation_and_wear_loa(self):
        self.assertEqual(classify(["TEAM_LOA", "WEAR_LOA"], "JERSEY", "2020").supported, "TEAM_ISSUED")
        self.assertEqual(classify(["TEAM_LOA", "PLAYER_NAME_TAG", "WEAR_LOA"], "JERSEY", "2020").supported, "PLAYER_WORN")

    def test_game_worn_needs_photo_match_or_game_loa(self):
        self.assertEqual(classify(["TEAM_LOA", "PHOTO_MATCH"], "JERSEY", "2020").supported, "GAME_WORN")
        self.assertNotEqual(classify(["TEAM_LOA", "DESIGN_MATCH_PHOTO"], "JERSEY", "2020").supported, "GAME_WORN")

    def test_design_photo_is_not_evidence_of_use(self):
        a = classify(["DESIGN_MATCH_PHOTO", "GENUINE_MANUFACTURER"], "JERSEY", "1996")
        self.assertEqual(a.supported, "LICENSED_RETAIL")

    def test_blocking_flags_override_everything(self):
        a = classify(["TEAM_LOA", "PHOTO_MATCH"], "JERSEY", "2020", red_flags=["STOLEN_RISK"])
        self.assertEqual(a.supported, "UNVERIFIED")
        self.assertIn("STOLEN_RISK", a.blocked_by)

    def test_kicks(self):
        self.assertEqual(classify(["PE_MARKINGS", "GENUINE_MANUFACTURER"], "SHOES").kicks_subtype, "PLAYER_EXCLUSIVE")
        self.assertEqual(classify(["RARE_RELEASE", "GENUINE_MANUFACTURER"], "SHOES").kicks_subtype, "RARE_RETAIL")
        self.assertEqual(classify(["PE_MARKINGS"], "SHOES").supported, "UNVERIFIED")

    def test_under_claiming_allowed(self):
        self.assertTrue(claim_allowed("TEAM_ISSUED", "GAME_WORN"))
        self.assertFalse(claim_allowed("TEAM_ISSUED", "LICENSED_RETAIL"))

    def test_copy_linter(self):
        self.assertTrue(lint_copy("Game-worn by the star", "TEAM_ISSUED"))
        self.assertFalse(lint_copy("This is not game-worn and was never worn by any player", "TEAM_ISSUED"))
        self.assertTrue(lint_copy("Team-issued warmup pants", "LICENSED_RETAIL"))
        self.assertFalse(lint_copy("Team-issued warmup pants", "VINTAGE_TEAM_ISSUE"))
        self.assertTrue(lint_copy("An official partner of the NBA", "GAME_WORN"))
        self.assertFalse(lint_copy("We are not an official partner of any league", "GAME_WORN"))

    def test_media_rules(self):
        media = [{"side": "ITEM", "match_level": "ILLUSTRATION_PLACEHOLDER", "rights_status": "OWNED"},
                 {"side": "REFERENCE", "match_level": "EXACT_PHOTO_MATCH", "rights_status": "LICENSED"}]
        probs = check_media(media, ["TEAM_LOA"], is_demo=False)
        self.assertTrue(any("exact item" in p for p in probs))
        self.assertTrue(any("PHOTO_MATCH" in p for p in probs))
        media[1]["rights_status"] = "NONE"
        self.assertTrue(any("do not permit" in p for p in check_media(media, ["PHOTO_MATCH"], True)))


class Economics(unittest.TestCase):
    def test_low_value_import(self):
        lc = E.landed_cost(100, "USD", 30)
        self.assertEqual(lc["duty_aud"], 0)
        self.assertGreater(lc["gst_aud"], 0)
        self.assertAlmostEqual(lc["item_aud"], 153.0)

    def test_high_value_import_attracts_duty_and_entry(self):
        lc = E.landed_cost(900, "USD", 40)
        self.assertGreater(lc["duty_aud"], 0)
        self.assertGreater(lc["entry_charges_aud"], 0)

    def test_unknown_shipping_is_flagged(self):
        self.assertTrue(any("ESTIMATE" in f for f in E.landed_cost(50, "USD")["flags"]))

    def test_domestic_has_no_import_costs(self):
        lc = E.landed_cost(80, "AUD", 10)
        self.assertEqual((lc["gst_aud"], lc["fx_fee_aud"]), (0, 0))

    def test_comps_exclude_unverified(self):
        c = E.comps_estimate([{"price": 100, "currency": "USD", "verified": True}, {"price": 900, "currency": "USD", "verified": False}])
        self.assertEqual(c["count"], 1)
        self.assertEqual(c["excluded"], 1)

    def test_unknown_currency_raises(self):
        with self.assertRaises(ValueError):
            E.to_aud(10, "XYZ")

    def test_consignment_payout(self):
        p = E.consignment_payout(400)
        self.assertEqual(p["commission_pct"], 25.0)
        self.assertEqual(p["consignor_payout_aud"], 300.0)
        self.assertEqual(E.consignment_payout(1500)["commission_pct"], 20.0)


def _opp(**kw):
    base = dict(id="T", title="t", listing_url="https://x", listed_price_cents=9000, currency="USD", shipping_cents=3500,
                item_type="TEARAWAY_PANTS", season="1996-97", condition="VERY_GOOD", claimed_classification="TEAM_ISSUED",
                evidence=json.dumps(["TEAM_LOA", "TEAM_ISSUE_TAG"]), red_flags="[]", live_verified=1,
                comps=json.dumps([{"price": p, "currency": "USD", "verified": True} for p in (240, 275, 310)]))
    base.update(kw)
    return base


class Engine(unittest.TestCase):
    def test_a_grade_path(self):
        r = engine.evaluate(_opp(), demand_score=70)
        self.assertEqual(r["recommendation"], "PROPOSE_TO_FOUNDER")
        self.assertEqual(r["grade"], "A")

    def test_never_buy_without_comps(self):
        r = engine.evaluate(_opp(comps="[]"), demand_score=90)
        self.assertNotEqual(r["recommendation"], "PROPOSE_TO_FOUNDER")

    def test_unverified_needs_evidence(self):
        r = engine.evaluate(_opp(evidence=json.dumps(["SELLER_CLAIM_ONLY"])), demand_score=90)
        self.assertEqual(r["recommendation"], "NEEDS_EVIDENCE")

    def test_blocked_rejected(self):
        r = engine.evaluate(_opp(red_flags=json.dumps(["COUNTERFEIT_INDICATORS"])), demand_score=90)
        self.assertEqual(r["recommendation"], "REJECT")

    def test_not_live_cannot_be_proposed(self):
        self.assertNotEqual(engine.evaluate(_opp(live_verified=0), 90)["recommendation"], "PROPOSE_TO_FOUNDER")

    def test_budget_breach_blocks_proposal(self):
        r = engine.evaluate(_opp(), 70, budget_remaining_aud=50)
        self.assertNotEqual(r["recommendation"], "PROPOSE_TO_FOUNDER")

    def test_overclaim_flagged(self):
        r = engine.evaluate(_opp(claimed_classification="GAME_WORN"), 70)
        self.assertTrue(any("Seller claims GAME_WORN" in x for x in r["rejection_reasons"]))

    def test_summary_reports_shortfall_and_ignores_demo(self):
        res = [{"is_demo": 1, "recommendation": "PROPOSE_TO_FOUNDER"}, {"is_demo": 0, "recommendation": "REJECT"}]
        s = engine.daily_summary(res)
        self.assertEqual((s["qualified"], s["shortfall"], s["evaluated"]), (0, 20, 1))


class Demand(unittest.TestCase):
    def test_missing_factors_lower_score(self):
        full = {k: {"score": 5, "basis": "MEASURED"} for k in demand.FACTORS}
        self.assertEqual(demand.score(full)["score"], 100.0)
        part = demand.score({"popularity": {"score": 5, "basis": "ESTIMATE"}})
        self.assertLess(part["score"], 20)
        self.assertEqual(part["measured_share_pct"], 0)
        self.assertEqual(part["label"], "ESTIMATE-LED")


class SearchFramework(unittest.TestCase):
    def test_queries_and_links(self):
        q = search_framework.queries_for("Orlando Magic")
        self.assertTrue(any("majic" in x for x in q))
        links = search_framework.links("tear away pants")
        self.assertIn("tear+away+pants", links["ebay_us"])
        self.assertTrue(links["gumtree_au"].endswith("/s-tear-away-pants/k0"))

    def test_misclassification_signal(self):
        hi = search_framework.misclassification_signal("old nike track pants 3XLT 90s", 30)
        lo = search_framework.misclassification_signal("Team issued game worn LOA pants", 30)
        self.assertGreater(hi["score"], lo["score"])


class DbBacked(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = os.path.join(cls.tmp.name, "t.db")
        cls.conn = seed.build(cls.path, quiet=True)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        cls.tmp.cleanup()

    # ---- registers
    def test_thirty_nba_franchises(self):
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM organisations WHERE kind='NBA_TEAM'").fetchone()[0], 30)

    def test_msu_denver_is_not_division_one(self):
        d = self.conn.execute("SELECT division FROM organisations WHERE id='NCAA-MSUD'").fetchone()[0]
        self.assertIn("II", d)
        self.assertNotEqual(d.strip(), "Division I")

    def test_current_australians_are_sourced(self):
        bad = self.conn.execute("""SELECT p.name FROM players p WHERE p.status='CURRENT_NBA' AND NOT EXISTS
                                   (SELECT 1 FROM sources s WHERE s.entity_type='player' AND s.entity_id=p.id)""").fetchall()
        self.assertEqual(bad, [])

    def test_no_contact_marked_verified_without_date(self):
        n = self.conn.execute("SELECT COUNT(*) FROM contacts WHERE tier='VERIFIED_CONTACT' AND verified_at IS NULL").fetchone()[0]
        self.assertEqual(n, 0)

    def test_no_demo_product_is_purchasable(self):
        from commerce.catalogue import can_purchase
        for p in self.conn.execute("SELECT * FROM products WHERE is_demo=1"):
            self.assertFalse(can_purchase(dict(p))[0])

    def test_real_listings_never_fill_target(self):
        n = self.conn.execute("SELECT COUNT(*) FROM opportunities WHERE is_demo=0 AND recommendation='PROPOSE_TO_FOUNDER'").fetchone()[0]
        self.assertEqual(n, 0)  # snippet-only leads can never qualify

    # ---- launch gate
    def test_demo_never_launch_ready(self):
        self.assertEqual(launch.tracker(self.conn)["ready_total"], 0)

    def test_real_product_can_pass_gate(self):
        c = self.conn
        c.execute("""INSERT INTO products(id, slug, title, department, era, item_type, season, condition_grade, claimed_classification,
                     description, price_cents, ownership, status, stock_qty, stock_confirmed, listing_authority_ref, fulfilment_plan, returns_terms)
                     VALUES ('T-1','t-1','Chicago Bulls | 1997-98 | Team-Issued Warmup Pants','TEARAWAY_VAULT','OG','TEARAWAY_PANTS','1997-98',
                     'GOOD','VINTAGE_TEAM_ISSUE','Team-issued pants.',30000,'OWNED','IN_REVIEW',1,1,'PO-1','AusPost tracked','14 days')""")
        c.execute("INSERT INTO evidence(product_id, code) VALUES ('T-1','TEAM_LOA')")
        c.execute("INSERT INTO product_media(product_id, side, match_level, rights_status) VALUES ('T-1','ITEM','EXACT_ITEM_PHOTO','OWNED')")
        c.execute("INSERT INTO product_media(product_id, side, match_level, rights_status) VALUES ('T-1','REFERENCE','REFERENCE_PENDING','NONE')")
        g = launch.gate(c, "T-1")
        self.assertTrue(g["ready"], g["failed"])
        c.execute("UPDATE products SET description='Game-worn by a star' WHERE id='T-1'")
        self.assertFalse(launch.gate(c, "T-1")["ready"])
        c.execute("DELETE FROM product_media WHERE product_id='T-1'")
        c.execute("DELETE FROM evidence WHERE product_id='T-1'")
        c.execute("DELETE FROM products WHERE id='T-1'")

    # ---- budget
    def test_budget_ceiling_strict(self):
        with self.assertRaises(budget.BudgetError):
            budget.propose(self.conn, "too much", "TEARAWAYS", 2000.00)
        aid = budget.propose(self.conn, "pair", "TEARAWAYS", 1999.00)
        budget.approve(self.conn, aid, "Founder")
        with self.assertRaises(budget.BudgetError):
            budget.propose(self.conn, "one more", "RESERVE", 1.00)
        self.conn.execute("DELETE FROM acquisitions")
        self.conn.commit()

    # ---- CRM
    def test_outreach_rules(self):
        c = self.conn
        org = c.execute("SELECT organisation_id FROM contacts WHERE tier='RESEARCHED_ROUTE' LIMIT 1").fetchone()[0]
        m = crm.draft_initial(c, org, "Alex Founder")
        self.assertEqual(m["status"], "DRAFT")
        with self.assertRaises(crm.OutreachError):
            crm.approve(c, m["id"], "")
        with self.assertRaises(crm.OutreachError):
            crm.record_sent(c, m["id"], "gmail", "x")          # not approved
        with self.assertRaises(crm.OutreachError):
            crm.draft_follow_up(c, org, 1)                     # no real send yet
        crm.approve(c, m["id"], "Alex Founder")
        crm.record_sent(c, m["id"], "founder's own mailbox", "Alex Founder", sent_at="2026-11-01T00:00:00Z")
        due = crm.follow_ups_due(c, "2026-11-20")
        self.assertTrue(any(d["organisation_id"] == org and d["step"] == 1 for d in due))
        self.assertFalse(any(d["organisation_id"] == org for d in crm.follow_ups_due(c, "2026-11-10")))
        with self.assertRaises(crm.OutreachError):
            crm.draft_follow_up(c, org, 3)
        crm.record_reply(c, org, "Please do not contact us", opt_out=True)
        with self.assertRaises(crm.OutreachError):
            crm.draft_follow_up(c, org, 1)
        self.assertFalse(any(d["organisation_id"] == org for d in crm.follow_ups_due(c, "2027-01-01")))

    def test_cannot_approve_unverified_lead(self):
        c = self.conn
        c.execute("INSERT INTO organisations(id, kind, name) VALUES ('X-LEAD','SUPPLIER','Lead Co')")
        c.execute("INSERT INTO contacts(organisation_id, method, value, tier) VALUES ('X-LEAD','EMAIL','a@b.example','UNVERIFIED_LEAD')")
        m = crm.draft_initial(c, "X-LEAD", "Alex Founder")
        with self.assertRaises(crm.OutreachError):
            crm.approve(c, m["id"], "Alex Founder")

    def test_draft_requires_contact(self):
        self.conn.execute("INSERT OR IGNORE INTO organisations(id, kind, name) VALUES ('X-NONE','SUPPLIER','No Route')")
        with self.assertRaises(crm.OutreachError):
            crm.draft_initial(self.conn, "X-NONE")

    def test_draft_uses_only_sourced_facts(self):
        m = crm.draft_initial(self.conn, "NBA-GSW", "Alex Founder")
        facts = json.loads(m["personalisation_facts"])
        self.assertTrue(all(f["source_url"].startswith("http") for f in facts))
        self.assertIn("not affiliated", m["body"])

    # ---- consignment
    def test_consignment_flow(self):
        c = self.conn
        r = consignment.submit(c, {"applicant_name": "Sam", "applicant_email": "sam@example.com",
                                   "item_description": "1998 warmup", "evidence_offered": ["TEAM_LOA"], "era": "1997-98"})
        self.assertEqual(r["preliminary_assessment"]["supported"], "VINTAGE_TEAM_ISSUE")
        cid = r["id"]
        with self.assertRaises(consignment.ConsignmentError):
            consignment.advance(c, cid, "LISTED", "admin")
        for st in ("EVIDENCE_REVIEW", "ACCEPTED", "AGREEMENT_SENT", "AGREEMENT_SIGNED"):
            consignment.advance(c, cid, st, "admin")
        with self.assertRaises(consignment.ConsignmentError):
            consignment.advance(c, cid, "RECEIVED", "admin")      # no agreement ref
        consignment.advance(c, cid, "RECEIVED", "admin", agreement_ref="AGR-1")
        with self.assertRaises(consignment.ConsignmentError):
            consignment.submit(c, {"applicant_name": "x", "applicant_email": "nope", "item_description": "y"})


if __name__ == "__main__":
    unittest.main()

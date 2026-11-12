"""Unit tests for canonical/model.py. Run: python3 -m unittest discover -s canonical/tests -v"""
import json
import os
import statistics
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import model  # noqa: E402


class Building(unittest.TestCase):
    def setUp(self):
        self.doc = model.load_assumptions()
        self.s = model.base_settings(self.doc)

    def test_premium_is_zero_at_ten_years_and_full_at_zero(self):
        self.assertEqual(model.premium(10, self.s), 0.0)
        self.assertEqual(model.premium(25, self.s), 0.0)
        self.assertAlmostEqual(model.premium(0, self.s), self.s["short_premium"])
        self.assertAlmostEqual(model.premium(5, self.s), self.s["short_premium"] / 2)

    def test_value_is_rent_over_yield(self):
        self.assertAlmostEqual(model.leased_value(100.0, 6.8, 20, self.s), 100.0 / 0.068)
        self.assertAlmostEqual(model.leased_value(100.0, 6.8, 0, self.s), 100.0 / ((6.8 + self.s["short_premium"]) / 100))

    def test_cash_sale_closed_form(self):
        s, e, H = self.s, 2032 - 2026, 2040 - 2026
        price = 100.0 / ((s["cap_long"] + s["short_premium"] * (10 - e) / 10) / 100)
        expect = price * (1 - s["sell_cost"] / 100) * (1 + s["reinvest_rate"] / 100) ** H
        self.assertAlmostEqual(model.expected(s, 2032)["sell_cash"], expect, places=6)

    def test_anchors_match_the_ledger(self):
        self.assertEqual(model.check_anchors(self.doc, model.load_rows()), [])

    def test_a_wrong_anchor_is_caught(self):
        doc = json.loads(json.dumps(self.doc))
        doc["settings"]["reinvest_rate"]["value"] = 9.99
        self.assertTrue(model.check_anchors(doc, model.load_rows()))


class Behaviour(unittest.TestCase):
    def setUp(self):
        self.s = model.base_settings(model.load_assumptions())

    def test_holding_improves_with_renewal_chance_and_cash_sale_does_not_move(self):
        lo = model.expected(dict(self.s, p_renew=40.0), 2032)
        hi = model.expected(dict(self.s, p_renew=90.0), 2032)
        self.assertGreater(hi["do_nothing"], lo["do_nothing"])
        self.assertAlmostEqual(hi["sell_cash"], lo["sell_cash"])
        self.assertAlmostEqual(hi["sell_exchange"], lo["sell_exchange"])

    def test_asking_first_never_hurts_a_seller(self):
        for year in (2030, 2033, 2035):
            ev = model.expected(self.s, year)
            self.assertGreaterEqual(ev["extend_then_sell"], ev["sell_exchange"] - 1e-9)

    def test_tax_only_touches_the_cash_sale(self):
        a = model.expected(dict(self.s, tax_drag=0.0), 2031)
        b = model.expected(dict(self.s, tax_drag=20.0), 2031)
        self.assertAlmostEqual(b["sell_cash"], a["sell_cash"] * 0.8)
        for key in ("sell_exchange", "do_nothing", "extend_and_hold", "test_then_decide", "extend_then_sell"):
            self.assertAlmostEqual(a[key], b[key])

    def test_breakeven_renewal_chance_really_is_a_breakeven(self):
        x = model.breakeven(self.s, 2031, "p_renew", 0.0, 100.0)
        self.assertIsNotNone(x)
        ev = model.expected(dict(self.s, p_renew=x), 2031)
        self.assertAlmostEqual(ev["do_nothing"], ev["sell_exchange"], delta=0.5)

    def test_with_no_change_of_intent_an_extension_adds_no_expected_value_to_a_holder_beyond_the_rent_terms(self):
        # tenants who agree today are those who would have renewed anyway
        s = dict(self.s, intent_change=0.0, extend_rent=self.s["renew_rent"], p_extend_now=50.0, p_renew=80.0)
        ev = model.expected(s, 2035)
        self.assertLess(abs(ev["extend_and_hold"] - ev["do_nothing"]) / ev["do_nothing"], 0.05)

    def test_a_signed_extension_protects_against_a_change_of_intent(self):
        calm = model.expected(dict(self.s, intent_change=0.0), 2032)
        risky = model.expected(dict(self.s, intent_change=60.0), 2032)
        gain_calm = calm["extend_and_hold"] - calm["do_nothing"]
        gain_risky = risky["extend_and_hold"] - risky["do_nothing"]
        self.assertGreater(gain_risky, gain_calm)


class Simulation(unittest.TestCase):
    def setUp(self):
        self.s = model.base_settings(model.load_assumptions())

    def test_simulation_without_noise_or_disasters_reproduces_the_expected_value(self):
        s = dict(self.s, cap_sigma=0.0, p_credit=0.0, repl_p_credit=0.0, p_regional_event=0.0)
        ev = model.expected(s, 2032)
        res = model.simulate(s, 2032, 20000, 7)
        for key, _, _ in model.STRATEGIES:
            self.assertAlmostEqual(statistics.fmean(res[key]) / ev[key], 1.0, delta=0.01, msg=key)

    def test_same_seed_same_answer(self):
        a = model.simulate(self.s, 2031, 500, 11)
        b = model.simulate(self.s, 2031, 500, 11)
        self.assertEqual(a, b)

    def test_disasters_only_hurt_the_local_property(self):
        calm = dict(self.s, p_regional_event=0.0)
        rough = dict(self.s, p_regional_event=5.0, p_site_damage=40.0, damage_loss=70.0)
        a = model.summarise(model.simulate(calm, 2032, 4000, 3), 0.5)
        b = model.summarise(model.simulate(rough, 2032, 4000, 3), 0.5)
        self.assertLess(b["do_nothing"]["p05"], a["do_nothing"]["p05"])
        self.assertAlmostEqual(b["sell_cash"]["median"], a["sell_cash"]["median"])

    def test_published_output_is_what_the_model_produces_now(self):
        with open(model.OUT, encoding="utf-8") as fh:
            published = json.load(fh)
        self.assertEqual(json.loads(json.dumps(model.build())), published)


if __name__ == "__main__":
    unittest.main()

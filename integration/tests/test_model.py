"""Unit tests for integration/model.py. Run: python3 -m unittest discover -s integration/tests -v"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import model  # noqa: E402


class Formulas(unittest.TestCase):
    def test_annuity_matches_closed_form(self):
        for rate in (0.0498, 0.066, 0.073):
            for years in range(1, 12):
                closed = 100 * (1 - (1 + rate) ** -years) / rate
                self.assertAlmostEqual(model.annuity(100, 0.0, rate, years), closed, places=9)

    def test_growing_annuity_matches_closed_form(self):
        rate, growth, years = 0.0498, 0.02, 7
        closed = 100 / (rate - growth) * (1 - ((1 + growth) / (1 + rate)) ** years)
        self.assertAlmostEqual(model.annuity(100, growth, rate, years), closed, places=9)

    def test_hold_value_rises_with_renewal_probability(self):
        values = [model.hold_value(6, 0.0498, 0.073, p / 10, 1.031, 0.63) for p in range(11)]
        self.assertEqual(values, sorted(values))
        self.assertLess(values[0], values[-1])

    def test_breakeven_probability_solves_hold_equals_sale(self):
        for years in range(4, 10):
            for sale_yield in (0.055, 0.065, 0.075):
                p = model.breakeven_p(sale_yield, years, 0.0498, 0.073, 1.031, 0.63)
                hold = model.hold_value(years, 0.0498, 0.073, p, 1.031, 0.63)
                self.assertAlmostEqual(hold, 100 / sale_yield, places=8)

    def test_certain_renewal_at_the_walk_away_rent_equals_the_gamble(self):
        p, rec, vac = 0.6, 1.031, 0.63
        gamble = model.hold_value(6, 0.0498, 0.073, p, rec, vac)
        certain = model.hold_value(6, 0.0498, 0.073, 1.0, model.mix(p, rec, vac), vac)
        self.assertAlmostEqual(gamble, certain, places=9)

    def test_event_probability_over_the_full_horizon_is_the_published_figure(self):
        self.assertAlmostEqual(model.prob_within(0.60, 30), 0.60, places=12)
        self.assertLess(model.prob_within(0.60, 4), model.prob_within(0.60, 9))

    def test_transfer_tax_bands(self):
        v = {"county_cents": 0.55, "county_per": 500, "city_base": 0.45, "ula_t1": 5_400_000, "ula_t2": 10_900_000, "ula_r1": 4, "ula_r2": 5.5}
        self.assertAlmostEqual(model.transfer_tax_rate(5_400_000, v), 0.0056, places=12)
        self.assertAlmostEqual(model.transfer_tax_rate(5_400_001, v), 0.0456, places=12)
        self.assertAlmostEqual(model.transfer_tax_rate(10_899_999, v), 0.0456, places=12)
        self.assertAlmostEqual(model.transfer_tax_rate(10_900_000, v), 0.0606, places=12)

    def test_cliff_price_nets_the_same_as_the_threshold(self):
        v = {"county_cents": 0.55, "county_per": 500, "city_base": 0.45, "ula_t1": 5_400_000, "ula_t2": 10_900_000, "ula_r1": 4, "ula_r2": 5.5}
        cliff = 5_400_000 * (1 - 0.0056) / (1 - 0.0456)
        self.assertAlmostEqual(cliff * (1 - model.transfer_tax_rate(cliff, v)), 5_400_000 * (1 - 0.0056), places=4)

    def test_number_tokens(self):
        self.assertIn("9,853,435", model.number_tokens(9853435))
        self.assertIn("4.98", model.number_tokens(4.98))
        self.assertIn("12.30", model.number_tokens(12.30))


class Reproducibility(unittest.TestCase):
    def test_two_runs_are_identical(self):
        self.assertEqual(model.render(), model.render())

    def test_committed_output_matches_a_fresh_run(self):
        with open(model.OUT, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), model.render())

    def test_inputs_must_appear_in_their_quotes(self):
        facts = [{"id": "Z-1", "status": "verified", "quote": "the rate was 4.98 percent", "n": {"x": 5.98}}]
        with self.assertRaises(SystemExit):
            model.collect_inputs(facts)

    def test_base_case_uses_only_published_figures(self):
        doc = json.loads(model.render())
        base = doc["base_case"]
        self.assertEqual(base["discount_rate_pct"], 4.98)
        self.assertEqual(base["buyer_yield_at_renewal_pct"], 7.3)
        self.assertEqual(base["renewal_rent_pct_of_old"], 103.1)
        self.assertEqual(base["renewal_probability_pct"], 76.2)
        self.assertEqual(base["vacant_price_pct_of_leased"], 62.8)

    def test_simulation_percentiles_are_ordered(self):
        doc = json.loads(model.render())
        for row in doc["simulation"]["rows"]:
            self.assertLessEqual(row["p05"], row["p25"])
            self.assertLessEqual(row["p25"], row["p50"])
            self.assertLessEqual(row["p50"], row["p75"])
            self.assertLessEqual(row["p75"], row["p95"])


if __name__ == "__main__":
    unittest.main()

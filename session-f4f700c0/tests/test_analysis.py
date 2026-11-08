import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import analyze

class TestModel(unittest.TestCase):
    def test_ula_boundaries(self):
        self.assertEqual(analyze.ula_rate(5_400_000), 0.0)
        self.assertEqual(analyze.ula_rate(5_400_001), 0.04)
        self.assertEqual(analyze.ula_rate(10_899_999), 0.04)
        self.assertEqual(analyze.ula_rate(10_900_000), 0.055)
        self.assertEqual(analyze.ula_rate(20_000_000, in_city=False), 0.0)

    def test_base_transfer_tax_rounding(self):
        self.assertEqual(analyze.city_base_transfer_tax(5_400_000), 24300.0)
        self.assertEqual(analyze.city_base_transfer_tax(5_400_001), 24302.25)

    def test_noi_path_and_cost(self):
        p = analyze.DEFAULTS
        flows = analyze.noi_path(p["expiry"], p["escalation"], p["reset"], p["extension_cost"], p["downtime"], p["retenant_cost"], p["reuse_factor"], "renew")
        self.assertAlmostEqual(flows[2027], 102.0)
        self.assertAlmostEqual(flows[p["expiry"]], 100 * 1.02 ** (p["expiry"] - 2026) - p["extension_cost"])
        self.assertAlmostEqual(flows[p["expiry"] + 1], 100 * 1.02 ** (p["expiry"] - 2026) * p["reset"])

    def test_vacate_branch(self):
        p = analyze.DEFAULTS
        flows = analyze.noi_path(p["expiry"], p["escalation"], p["reset"], 0, 1, p["retenant_cost"], p["reuse_factor"], "vacate")
        self.assertEqual(flows[p["expiry"] + 1], -p["retenant_cost"])
        self.assertAlmostEqual(flows[p["expiry"] + 2], 100 * 1.02 ** (p["expiry"] - 2026) * p["reuse_factor"])

    def test_breakevens(self):
        p = analyze.DEFAULTS
        res = analyze.evaluate(p)
        be = analyze.breakevens(p, res)
        cap = 100 / be["required_gross_sale_now_to_match_extend_hold"]
        self.assertAlmostEqual(analyze.evaluate(dict(p, entry_cap=cap))["sell_now"]["fv"], res["extend_hold"]["fv"], places=6)
        self.assertAlmostEqual(analyze.evaluate(dict(p, reset=be["required_renewal_reset_to_match_sell_now"]))["extend_hold"]["fv"], res["sell_now"]["fv"], places=6)

class TestLedgers(unittest.TestCase):
    def test_unknowns_blank(self):
        rows = json.loads((ROOT / "data" / "metrics.json").read_text())["rows"]
        for r in rows:
            if r["status"] != "verified":
                self.assertIn(r["value"], ("", None))
        reqs = json.loads((ROOT / "data" / "requirements.json").read_text())["rows"]
        self.assertTrue(all(r["value"] == "" for r in reqs))

    def test_projection_math(self):
        rows = json.loads((ROOT / "model" / "projections.json").read_text())["rows"]
        for r in rows:
            years = int(r["end"].split(",")[-1].strip()) - int(r["start"].split(",")[-1].strip()) if "," in r["end"] else int(r["end"]) - int(r["start"])
            cagr = ((r["end_value"] / r["start_value"]) ** (1 / years) - 1) * 100
            self.assertAlmostEqual(cagr, r["cagr_pct"], places=3)

if __name__ == "__main__":
    unittest.main()

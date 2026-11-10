import json, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TestBuild(unittest.TestCase):
    def test_verify_passes(self):
        r = subprocess.run([sys.executable, str(ROOT/"scripts"/"verify.py")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_blanks_stay_blank(self):
        rows = json.loads((ROOT/"data"/"metrics.json").read_text())["rows"]
        for r in rows:
            if r["status"] != "verified":
                self.assertEqual(str(r["value"]).strip(), "", r["id"])

    def test_pages_exist(self):
        for p in ["index.html","executive-summary.html","market-economics.html","decision.html","risks.html","sources.html","flagged.html","verification.html"]:
            self.assertTrue((ROOT/p).exists(), p)

if __name__ == "__main__":
    unittest.main()

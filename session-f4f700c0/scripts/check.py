#!/usr/bin/env python3
"""Build, data, model, privacy and internal-link verification for the dashboard."""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, urljoin

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "scripts"))
import analyze  # noqa: E402

ALLOWED_SUFFIXES = (
    "census.gov", "bls.gov", "bea.gov", "treasury.gov", "federalreserve.gov",
    "sec.gov", "irs.gov", "usgs.gov", "fema.gov", "huduser.gov",
    "ca.gov", "lacity.org", "lacity.gov", "lacounty.gov", "metro.net", "portoflosangeles.org",
    "caschooldashboard.org", "discoverlosangeles.com", "waterboards.ca.gov",
)
PII_RES = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}"),
    re.compile(r"\b\d{1,6}\s+(?:[A-Z][a-z]+\s){1,3}(Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Way|Lane|Ln)\b"),
    re.compile(r"\bAPN[:\s#]*\d{3,}"),
]

checks = []
def check(name, ok, detail=""):
    checks.append(dict(name=name, passed=bool(ok), detail=detail))
    if not ok:
        print("FAIL:", name, detail)
    return ok

def load(name):
    return json.loads((DATA / f"{name}.json").read_text())["rows"]

sources = {r["id"]: r for r in load("sources")}
metrics = load("metrics")
reqs = load("requirements")
risks = load("risks")
decisions = load("decisions")
flags = load("flags")

# Source registry and row linkage.
ids = [r["id"] for r in sources.values()]
check("source IDs unique", len(ids) == len(set(ids)))
bad_hosts = []
for s in sources.values():
    host = urlparse(s["url"]).hostname or ""
    if not s["url"].startswith("https://") or not any(host == d or host.endswith("." + d) for d in ALLOWED_SUFFIXES):
        bad_hosts.append(s["id"] + ":" + host)
check("official source domains", not bad_hosts, ",".join(bad_hosts))

for name, rows in [("metrics", metrics), ("requirements", reqs), ("risks", risks), ("decisions", decisions), ("flags", flags)]:
    missing = [r["id"] for r in rows if not r.get("source") or r["source"] not in sources]
    extra_missing = [r["id"] for r in rows for sid in r.get("extra_sources", []) if sid not in sources]
    check(f"{name} row source links", not missing and not extra_missing, ",".join(missing + extra_missing))
    rid = [r["id"] for r in rows]
    check(f"{name} IDs unique", len(rid) == len(set(rid)))

bad_values = []
for r in metrics:
    if r["status"] == "verified" and (r["value"] == "" or r["value"] is None):
        bad_values.append(r["id"])
    if r["status"] != "verified" and r["value"] not in ("", None):
        bad_values.append(r["id"] + ":nonblank")
check("verified/unknown value discipline", not bad_values, ",".join(bad_values))
check("requirements remain blank", all(r["value"] == "" for r in reqs))
check("risk probabilities remain blank", all(r["probability"] == "" for r in risks))

# Model arithmetic and tax boundaries.
check("ULA equality at lower threshold", analyze.ula_rate(5_400_000) == 0.0)
check("ULA just above lower threshold", analyze.ula_rate(5_400_001) == 0.04)
check("ULA equality at upper threshold", analyze.ula_rate(10_900_000) == 0.055)
check("ULA outside city", analyze.ula_rate(20_000_000, in_city=False) == 0.0)
check("city base transfer tax rounding", analyze.city_base_transfer_tax(5_400_001) == 24302.25)
p = analyze.DEFAULTS
res = analyze.evaluate(p)
flows = res["extend_hold"]["annual_flows"]
check("first forecast year NOI", abs(flows[2027] - 102.0) < 1e-9)
check("expiry-year extension cost", abs(flows[p["expiry"]] - (100 * 1.02 ** (p["expiry"] - 2026) - p["extension_cost"])) < 1e-9)
be = analyze.breakevens(p, res)
required_cap = 100 / be["required_gross_sale_now_to_match_extend_hold"]
res2 = analyze.evaluate(dict(p, entry_cap=required_cap))
check("sale-now breakeven consistency", abs(res2["sell_now"]["fv"] - res["extend_hold"]["fv"]) < 1e-6)
res3 = analyze.evaluate(dict(p, reset=be["required_renewal_reset_to_match_sell_now"]))
check("renewal-reset breakeven consistency", abs(res3["extend_hold"]["fv"] - res["sell_now"]["fv"]) < 1e-6)

proj = json.loads((ROOT / "model" / "projections.json").read_text())["rows"]
bad_proj = []
for r in proj:
    years = int(r["end"].split(",")[-1].strip()) - int(r["start"].split(",")[-1].strip()) if "," in r["end"] else int(r["end"]) - int(r["start"])
    cagr = ((r["end_value"] / r["start_value"]) ** (1 / years) - 1) * 100
    if abs(cagr - r["cagr_pct"]) > 0.001:
        bad_proj.append(r["series"])
check("projection CAGR arithmetic", not bad_proj, ",".join(bad_proj))

# Privacy scan of current-session files.
privacy_hits = []
for f in ROOT.rglob("*"):
    if not f.is_file() or f.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip"}:
        continue
    text = f.read_text(errors="replace")
    for rx in PII_RES:
        if rx.search(text):
            privacy_hits.append(str(f.relative_to(ROOT)))
            break
check("current-session privacy scan", not privacy_hits, ",".join(sorted(set(privacy_hits))))

# HTML internal links and table-row source links.
if not (ROOT / "verification.json").exists():
    (ROOT / "verification.json").write_text('{"pending": true}\n')
class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.in_tbody = False
        self.in_row = False
        self.row_has_external = False
        self.rows = 0
        self.rows_missing_source = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("a", "link") and a.get("href"):
            self.links.append(a["href"])
        if tag == "script" and a.get("src"):
            self.links.append(a["src"])
        if tag == "tbody":
            self.in_tbody = True
        if self.in_tbody and tag == "tr":
            self.in_row = True
            self.row_has_external = False
            self.rows += 1
        if self.in_row and tag == "a" and a.get("href", "").startswith("http"):
            self.row_has_external = True
    def handle_endtag(self, tag):
        if tag == "tbody":
            self.in_tbody = False
        if self.in_tbody and tag == "tr":
            if not self.row_has_external:
                self.rows_missing_source += 1
            self.in_row = False

broken = []
table_rows = 0
table_missing = 0
for f in sorted(ROOT.glob("*.html")):
    parser = LinkParser()
    parser.feed(f.read_text())
    table_rows += parser.rows
    table_missing += parser.rows_missing_source
    for href in parser.links:
        if href.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = urljoin(f.as_uri(), href).split("#")[0].split("?")[0]
        path = Path(target.replace("file://", ""))
        if not path.exists():
            broken.append(f.name + " -> " + href)
check("internal links resolve", not broken, ",".join(broken[:10]))
check("every table row has an external source link", table_missing == 0, f"rows={table_rows}, missing={table_missing}")

audit = json.loads((ROOT / "audit" / "summary.json").read_text())
check("audit structural errors zero", audit["structural_errors"] == 0)
check("audit current-session privacy zero", audit["current_session_privacy_hits"] == 0)

payload = dict(
    as_of="2026-11-08",
    passed=all(c["passed"] for c in checks),
    checks=checks,
    counts=dict(sources=len(sources), metrics=len(metrics), verified=sum(r["status"]=="verified" for r in metrics),
                unknown=sum(r["status"]!="verified" for r in metrics), requirements=len(reqs),
                risks=len(risks), decisions=len(decisions), flags=len(flags),
                html_table_rows=table_rows, audit_files=audit["files"], audit_lines=audit["lines"]),
)
(ROOT / "verification.json").write_text(json.dumps(payload, indent=2) + "\n")
print(json.dumps(dict(passed=payload["passed"], checks=len(checks), counts=payload["counts"]), indent=2))
sys.exit(0 if payload["passed"] else 1)

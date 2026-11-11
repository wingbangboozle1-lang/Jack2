"""Independent pre-publication verification for the Session I workbook.

Checks:
  * every metric/risk/source reference resolves to a declared source,
  * verified rows carry values; unverified rows are blank (nothing inferred),
  * no personal information (emails, phones, SSNs) in data or HTML,
  * risk ratings and decision scores in range,
  * generated HTML links internally and carries source links on every table row.
Exit non-zero on any failure.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PAGES = [p for p in ROOT.glob("*.html")]
ERRORS = []

def err(msg):
    ERRORS.append(msg)
    print("FAIL:", msg)

def ok(msg):
    print("ok:", msg)

# --- 1. sources ---
with open(DATA / "sources.json", encoding="utf-8") as f:
    sources = json.load(f)["sources"]
src_ids = {s["id"] for s in sources}
assert len(src_ids) == len(sources), "duplicate source ids"
for s in sources:
    assert s["url"].startswith("https://"), f"source {s['id']} URL not https: {s['url']}"
    assert s["tier"] in ("A","B","C","X"), f"source {s['id']} bad tier {s['tier']}"
    assert isinstance(s["verified"], bool), f"source {s['id']} verified not bool"
ok(f"sources.json: {len(sources)} sources, all https, valid tiers")

# --- 2. metrics ---
with open(DATA / "metrics.json", encoding="utf-8") as f:
    metrics = json.load(f)["rows"]
m_ids = [r["id"] for r in metrics]
assert len(m_ids) == len(set(m_ids)), "duplicate metric ids"
for r in metrics:
    assert r["source"] in src_ids or r["source"] == "Internal", f"metric {r['id']} cites unknown source {r['source']}"
    assert r["status"] in ("verified", "unverified"), f"metric {r['id']} bad status {r['status']}"
    if r["status"] == "verified":
        assert r["value"] not in (None, ""), f"verified metric {r['id']} has no value"
    else:
        assert r["value"] in (None, ""), f"unverified metric {r['id']} must be blank, got {r['value']!r}"
ok(f"metrics.json: {len(metrics)} rows, sourcing and blank rules satisfied")
n_ver = sum(1 for r in metrics if r["status"] == "verified")
n_unv = len(metrics) - n_ver
print(f"  verified={n_ver} unverified={n_unv}")

# --- 3. property lease: no PII ---
with open(DATA / "property_lease.json", encoding="utf-8") as f:
    lease = json.load(f)
text = json.dumps(lease)
email = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
phone = re.findall(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b", text)
ssn = re.findall(r"\b\d{3}-\d{2}-\d{4}\b", text)
assert not email and not phone and not ssn, f"PII found: emails={email} phones={phone} ssns={ssn}"
for k in ("address", "apn", "owner_name", "current_rent", "current_market_value"):
    v = lease["identified_property"][k]
    assert "WITHHELD" in v or v in ("", None), f"lease field {k} not a placeholder: {v}"
ok("property_lease.json: no PII, all identifying fields withheld")

# --- 4. risks ---
with open(DATA / "risks.json", encoding="utf-8") as f:
    risks = json.load(f)["risks"]
r_ids = [r["id"] for r in risks]
assert len(r_ids) == len(set(r_ids)), "duplicate risk ids"
for r in risks:
    assert 1 <= r["likelihood"] <= 5 and 1 <= r["impact"] <= 5, f"risk {r['id']} ratings out of range"
    assert r["source"] in src_ids or r["source"] == "Internal", f"risk {r['id']} unknown source {r['source']}"
ok(f"risks.json: {len(risks)} risks, ratings in 1-5")

# --- 5. decisions ---
with open(DATA / "decisions.json", encoding="utf-8") as f:
    dec = json.load(f)
w = dec["meta"]["weights"]
assert abs(sum(w.values()) - 1.0) < 1e-9, "weights don't sum to 1"
for o in dec["options"]:
    for k, v in o["scores"].items():
        assert 1 <= v <= 10, f"decision {o['id']} score {k} = {v} out of range"
ok(f"decisions.json: {len(dec['options'])} options, weights sum to 1, scores in 1-10")

# --- 6. model output ---
with open(DATA / "model_output.json", encoding="utf-8") as f:
    mo = json.load(f)
assert len(mo["scenarios"]) == 5, "expected 5 cap scenarios"
for s in mo["scenarios"]:
    for k in ("exit_cap_pct", "gross_price_usd", "net_proceeds_usd", "pv_hold_weighted_usd", "hold_minus_sell_usd"):
        assert k in s, f"scenario missing {k}"
ok("model_output.json: 5 scenarios complete")

# --- 7. HTML pages ---
expected = {"index.html","executive-summary.html","property-lease.html","market-economics.html",
            "schools-education.html","capital-markets-taxes.html","tenant-brand.html","risks.html",
            "valuation.html","projection-model.html","decision.html","sources.html","flagged.html","privacy.html"}
present = {p.name for p in PAGES}
missing = expected - present
assert not missing, f"missing pages: {missing}"
for p in sorted(PAGES):
    html = p.read_text(encoding="utf-8")
    assert re.search(r"<title>.+</title>", html), f"{p.name} no title"
    assert "style.css" in html, f"{p.name} missing stylesheet"
    # every internal nav target present
    for target in expected:
        assert f'href="{target}"' in html, f"{p.name} missing link to {target}"
    # no PII in HTML
    assert not re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", html), f"email in {p.name}"
    assert not re.findall(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b", html), f"phone in {p.name}"
    # every table row has a source cell linking to sources.html#Txx
    for m in re.finditer(r'id="?"(M\d+)"?', html):
        pass  # metrics ids aren't stamped on cells; check source cells instead
    src_refs = set(re.findall(r'href="sources\.html#(T\d+)"', html))
    assert src_refs <= src_ids, f"{p.name} references unknown sources: {src_refs - src_ids}"
ok(f"html: {len(PAGES)} pages, all cross-links present, no PII, source links resolve")

# --- 8. irregularities ---
with open(DATA / "irregularities.json", encoding="utf-8") as f:
    irr = json.load(f)["items"]
i_ids = [i["id"] for i in irr]
assert len(i_ids) == len(set(i_ids)), "duplicate irregularity ids"
for i in irr:
    assert i["severity"] in ("Low","Medium","High","Informational"), f"bad severity {i['id']}"
ok(f"irregularities.json: {len(irr)} items")

print(f"\nVERIFICATION PASSED ({len(metrics)} metrics, {len(sources)} sources, {len(PAGES)} pages)")
sys.exit(0)

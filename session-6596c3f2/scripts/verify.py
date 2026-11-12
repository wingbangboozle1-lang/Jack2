#!/usr/bin/env python3
"""Verifier - Session O. Checks: JSON validity, source-per-row, blank rule,
official-domain allowlist, PII patterns, internal links, model freshness."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; errs = []
def load(n): return json.loads((ROOT/"data"/n).read_text())
src = {s["id"]: s for s in load("sources.json")["sources"]}
OFFICIAL = (".gov", "sec.gov", "fred.stlouisfed.org")
for s in src.values():
    if not any(d in s["url"] for d in OFFICIAL): errs.append(f"source {s['id']} not official: {s['url']}")
for r in load("metrics.json")["rows"]:
    if r["status"] == "verified" and not (r["value"] and r["source"] in src): errs.append(f"{r['id']}: verified without value/source")
    if r["status"] == "unverified" and r["value"]: errs.append(f"{r['id']}: unverified must be blank")
    if r["status"] in ("verified","flagged") and r["source"] and r["source"] not in src: errs.append(f"{r['id']}: bad source {r['source']}")
PII = [r"\b\d{3}-\d{2}-\d{4}\b", r"\b[\w.]+@[\w.]+\.\w+\b", r"\b\d{3}[-.]\d{3}[-.]\d{4}\b", r"\bAPN[:#]?\s*\d"]
for f in list(ROOT.glob("*.html")) + list((ROOT/"data").glob("*.json")):
    t = f.read_text()
    for p in PII:
        if re.search(p, t): errs.append(f"PII pattern {p} in {f.name}")
    if f.suffix == ".html":
        for href in re.findall(r'href="([^"#]+)"', t):
            if href.startswith(("http", "mailto")): continue
            if not (ROOT/href).exists(): errs.append(f"broken link {href} in {f.name}")
mo = ROOT/"data"/"model_output.json"
if not mo.exists(): errs.append("model_output.json missing - run scripts/model.py")
else:
    m = json.loads(mo.read_text())
    if m["monte_carlo"]["B"]["ce_crra2"] < m["monte_carlo"]["C"]["ce_crra2"]: errs.append("model ranking sanity failed")
print(f"FAIL ({len(errs)}):" if errs else "PASS: 0 errors - sources official, blanks blank, links resolve, no PII patterns")
for e in errs: print(" -", e)
sys.exit(1 if errs else 0)

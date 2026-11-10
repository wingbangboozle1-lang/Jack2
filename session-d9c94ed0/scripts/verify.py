#!/usr/bin/env python3
"""Verify Session M dashboard: source links, blanks, PII, internal links, IDs. Stdlib only."""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
errors, warnings = [], []

sources = json.loads((DATA/"sources.json").read_text())["sources"]
sids = {s["id"] for s in sources}
metrics = json.loads((DATA/"metrics.json").read_text())["rows"]
risks = json.loads((DATA/"risks.json").read_text())["rows"]

# 1. source IDs unique + official domains
seen = set()
for s in sources:
    if s["id"] in seen: errors.append(f"dup source {s['id']}")
    seen.add(s["id"])
    if s["tier"] == "D": errors.append(f"source {s['id']} is Tier D")
    if not s["url"].startswith("https://"): errors.append(f"source {s['id']} not https")

# 2. metrics: every row has source; verified non-empty; unverified blank; IDs unique
seen = set()
for r in metrics:
    if r["id"] in seen: errors.append(f"dup metric {r['id']}")
    seen.add(r["id"])
    if r["source"] not in sids: errors.append(f"metric {r['id']} bad source {r['source']}")
    if r["status"] == "verified" and not str(r["value"]).strip():
        errors.append(f"metric {r['id']} verified but empty")
    if r["status"] != "verified" and str(r["value"]).strip():
        errors.append(f"metric {r['id']} unverified but has value")

# 3. risks: source present, IDs unique
seen = set()
for r in risks:
    if r["id"] in seen: errors.append(f"dup risk {r['id']}")
    seen.add(r["id"])
    if r["source"] not in sids: errors.append(f"risk {r['id']} bad source {r['source']}")

# 4. PII scan on published HTML + data
email = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
phone = re.compile(r"\b\d{3}[-. ]\d{3}[-. ]\d{4}\b")
apn = re.compile(r"\bAPN\s*[:#]?\s*\d{4,}\b", re.I)
for p in list(ROOT.glob("*.html")) + list(DATA.glob("*.json")):
    t = p.read_text(errors="ignore")
    for m in email.finditer(t): errors.append(f"PII email in {p.name}: {m.group(0)[:30]}")
    for m in phone.finditer(t): errors.append(f"PII phone in {p.name}: {m.group(0)}")
    for m in apn.finditer(t): errors.append(f"PII APN in {p.name}: {m.group(0)}")

# 5. internal links resolve
pages = {p.name for p in ROOT.glob("*.html")}
for p in ROOT.glob("*.html"):
    t = p.read_text(errors="ignore")
    for m in re.finditer(r'href="([^"#]+)(#[^"]*)?"', t):
        href = m.group(1)
        if href.startswith(("http://","https://","mailto:")): continue
        if href.startswith("../"): continue  # root landing link
        if href.startswith("assets/"):
            if not (ROOT/href).exists(): errors.append(f"missing asset {href} in {p.name}")
            continue
        if href not in pages: errors.append(f"broken internal link {href} in {p.name}")

# 6. every metric ID appears in at least one page (spot check via market/index)
all_html = "".join(p.read_text(errors="ignore") for p in ROOT.glob("*.html"))
for r in metrics:
    if r["id"] not in all_html: warnings.append(f"metric {r['id']} not rendered")

print(f"pages: {len(pages)} | sources: {len(sources)} | metrics: {len(metrics)} ({sum(1 for r in metrics if r['status']=='verified')} verified) | risks: {len(risks)}")
if warnings:
    print("warnings:"); [print(" -", w) for w in warnings]
if errors:
    print(f"FAILED ({len(errors)} errors):"); [print(" -", e) for e in errors]; sys.exit(1)
print("all checks passed")

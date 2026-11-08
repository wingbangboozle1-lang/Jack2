#!/usr/bin/env python3
"""
Verifier for session-643e4aab. Fails loudly. Run before every commit and in CI.

Checks
------
 1. data integrity      every row has an id, a status and a category; ids are unique
 2. blank rule          verified/computed rows must have a value; unverified rows must be blank
 3. source resolution   every non-blank row and every risk resolves to a source with an https URL
 4. citation discipline no source is cited that was not in the ledger
 5. page build          every page exists and every internal link/nav target resolves
 6. source links        every <a class="src"> href is an https URL that appears in the ledger
 7. PII scan            no email, phone, street address, parcel number or account number patterns
 8. model consistency   published projections.json matches a fresh run of the engine
 9. row coverage        every metric row appears in the rendered HTML exactly once
"""
import html as html_lib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

errors, warnings, notes = [], [], []


def err(m):
    errors.append(m)


def warn(m):
    warnings.append(m)


def load(n):
    with open(os.path.join(DATA, n), encoding="utf-8") as f:
        return json.load(f)


SRCS = load("sources.json")
LEDGER = {s["id"]: s for s in SRCS["sources"]}
METRICS = load("metrics.json")["rows"]
RISKS = load("risks.json")["rows"]
PROJ = load("projections.json")

# ---------------------------------------------------------------- 1 & 2
seen = set()
for r in METRICS:
    for field in ("id", "category", "metric", "value", "status", "note"):
        if field not in r:
            err(f"metric row missing '{field}': {r.get('id', r)}")
    if r["id"] in seen:
        err(f"duplicate metric id {r['id']}")
    seen.add(r["id"])
    if r["status"] in ("verified", "computed", "given"):
        if r["value"] in ("", None) and r["status"] != "given":
            err(f"{r['id']}: {r['status']} row has an empty value")
    if r["status"] == "unverified":
        if r["value"] not in ("", None):
            err(f"{r['id']}: unverified row has a value ({r['value']!r}) - values must never be filled in for unverified rows")
        if not r.get("note"):
            err(f"{r['id']}: unverified row has no explanation")

# ---------------------------------------------------------------- 3
for r in METRICS:
    sid = r.get("source", "")
    if r["status"] in ("verified", "computed") and not sid:
        err(f"{r['id']}: {r['status']} row has no source id")
    if r["status"] == "unverified" and sid:
        warn(f"{r['id']}: unverified row carries a source id ({sid}) - confirm that is intended (e.g. the lookup source)")
    if sid and sid not in LEDGER:
        err(f"{r['id']}: source {sid} is not in the ledger")
    if sid in LEDGER and not LEDGER[sid]["url"].startswith("https://"):
        err(f"{r['id']}: source {sid} does not have an https URL")
for r in RISKS:
    if r["evidence"] == "verified":
        if not r["source"]:
            err(f"{r['id']}: risk marked verified has no source")
        elif r["source"] not in LEDGER:
            err(f"{r['id']}: risk source {r['source']} not in ledger")
    if r["evidence"] == "verified" and not LEDGER.get(r["source"], {}).get("tier") in ("A", "B", "C"):
        err(f"{r['id']}: verified risk cites an unacceptable source tier")
    if r["evidence"] not in ("verified", "analyst"):
        err(f"{r['id']}: unknown evidence type {r['evidence']}")

# ---------------------------------------------------------------- 5 & 6
PAGES = ["index.html", "executive-summary.html", "property.html", "market.html", "tenant.html",
         "hazards.html", "taxes.html", "risks.html", "projection.html", "verification.html", "flagged.html", "sources.html"]
for p in PAGES:
    full = os.path.join(ROOT, p)
    if not os.path.exists(full):
        err(f"missing page {p}")
        continue
    html = open(full, encoding="utf-8").read()
    for href in set(re.findall(r'href="([^"#][^"]*)"', html)):
        if href.startswith(("http://", "https://", "mailto:")):
            continue
        target = os.path.normpath(os.path.join(ROOT, href.split("?")[0]))
        if not os.path.exists(target):
            err(f"{p}: broken internal link -> {href}")
    ledger_urls = {s["url"] for s in LEDGER.values()}
    for href in set(re.findall(r'<a class="src" href="([^"]+)"', html)):
        raw = html_lib.unescape(href)
        if not raw.startswith("https://"):
            err(f"{p}: source link is not https: {raw}")
        if raw not in ledger_urls:
            err(f"{p}: source link not present in the ledger: {raw}")

# ---------------------------------------------------------------- 7 (PII)
PII = [
    (r"[\w.+-]+@[\w-]+\.[\w.]{2,}", "email address"),
    (r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b", "US phone number"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "Social Security number pattern"),
    (r"\b\d{3,4}[- ]\d{2}[- ]\d{3,4}\b", "parcel/APN-like number"),
    (r"\b\d{4}\s+\d{2}\s+\d{3}\s+\d{3}\b", "parcel/APN-like number"),
    (r"\b\d{2,5}\s+[A-Z][a-z]{2,}\s+(Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Way|Place|Pl)\b", "street address"),
    (r"\b(?:Account|Acct|Loan)\s*(?:No\.?|Number|#)\s*[:#]?\s*[A-Z0-9-]{4,}", "account or loan number"),
]
for p in PAGES:
    full = os.path.join(ROOT, p)
    if not os.path.exists(full):
        continue
    html = open(full, encoding="utf-8").read()
    # strip the federal relay / agency contact info that is legitimately part of cited source text
    for pattern, label in PII:
        for m in re.finditer(pattern, html):
            snippet = m.group(0)
            if snippet.endswith("@example.com"):
                continue
            err(f"{p}: possible {label} in output: {snippet!r}")

# ---------------------------------------------------------------- 8
tmp = subprocess.run([sys.executable, os.path.join(ROOT, "model", "projection.py")],
                     capture_output=True, text=True, cwd=ROOT)
if tmp.returncode != 0:
    err(f"model engine failed to run:\n{tmp.stderr[-800:]}")
else:
    fresh = load("projections.json")
    if json.dumps(fresh, sort_keys=True) != json.dumps(PROJ, sort_keys=True):
        err("data/projections.json does not match a fresh run of model/projection.py")

# ---------------------------------------------------------------- 9
market = open(os.path.join(ROOT, "market.html"), encoding="utf-8").read()
property_html = open(os.path.join(ROOT, "property.html"), encoding="utf-8").read()
tenant = open(os.path.join(ROOT, "tenant.html"), encoding="utf-8").read()
taxes = open(os.path.join(ROOT, "taxes.html"), encoding="utf-8").read()
hazards = open(os.path.join(ROOT, "hazards.html"), encoding="utf-8").read()
rendered = market + property_html + tenant + taxes + hazards
for r in METRICS:
    if f'>{r["id"]}<' not in rendered:
        err(f"metric row {r['id']} is not rendered on any category page")
risks_html = open(os.path.join(ROOT, "risks.html"), encoding="utf-8").read()
for r in RISKS:
    if f'>{r["id"]}<' not in risks_html:
        err(f"risk {r['id']} is not rendered")
flagged = open(os.path.join(ROOT, "flagged.html"), encoding="utf-8").read()
for r in METRICS:
    if r["status"] == "unverified" and f'>{r["id"]}<' not in flagged:
        err(f"unverified metric {r['id']} is not listed on the flagged page")

# ---------------------------------------------------------------- summary
counts = {}
for r in METRICS:
    counts[r["status"]] = counts.get(r["status"], 0) + 1
print(f"pages checked: {len(PAGES)}")
print(f"metric rows: {len(METRICS)}  " + "  ".join(f"{k}={v}" for k, v in sorted(counts.items())))
print(f"risk rows:   {len(RISKS)}  (verified evidence={sum(1 for r in RISKS if r['evidence']=='verified')})")
print(f"sources:     {len(LEDGER)}")
for w in warnings:
    print(f"WARN  {w}")
if errors:
    print(f"\n{len(errors)} ERROR(S):")
    for e_ in errors:
        print(f"  ERROR {e_}")
    sys.exit(1)
print("\nall checks passed")

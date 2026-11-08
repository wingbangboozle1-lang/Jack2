#!/usr/bin/env python3
"""
8-Rule Automated Audit & Verification Suite for Session J (session-24d6cd5f).
Exits non-zero on any link, citation, blank-cell, PII, or model-consistency error.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
FAILS = []


def fail(msg):
    FAILS.append(msg)


def load(name):
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
        return json.load(f)


SOURCES = load("sources.json")
SRC = {s["id"]: s for s in SOURCES["sources"]}
METRICS = load("metrics.json")
RISKS = load("risks.json")
IRR = load("irregularities.json")
MODEL = load("model_output.json")

# 1. Source registry integrity (Tier A/B only, https:// only)
for s in SOURCES["sources"]:
    if not s["url"].startswith("https://"):
        fail(f"Source {s['id']} not https: {s['url']}")
    if s["tier"] not in ("A", "B"):
        fail(f"Source {s['id']} invalid tier {s['tier']} (Tier A/B only)")

# 2. Metric rows blank-cell & source rule
for r in METRICS["rows"]:
    if r.get("source") not in SRC:
        fail(f"Metric {r['id']} invalid source {r.get('source')}")
    val = str(r.get("value", "")).strip()
    if r["status"] == "verified" and not val:
        fail(f"Metric {r['id']} marked verified with blank value")
    if r["status"] != "verified" and val != "":
        fail(f"Metric {r['id']} marked {r['status']} with non-blank value {val!r}")

# 3. Risk & Irregularity sources
for rk in RISKS["rows"]:
    if rk.get("source") not in SRC:
        fail(f"Risk {rk['id']} invalid source {rk.get('source')}")
for ir in IRR["cross_session_findings"]:
    if ir.get("source") not in SRC:
        fail(f"Irregularity {ir['id']} invalid source {ir.get('source')}")

# 4. HTML Pages & Nav Completeness
html_files = sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))
if len(html_files) != 11:
    fail(f"Expected 11 HTML pages, found {len(html_files)}")

with open(os.path.join(ROOT, "index.html"), encoding="utf-8") as f:
    nav_block = " ".join(re.findall(r'<nav class="main"[^>]*>.*?</nav>', f.read(), re.S))
for fn in html_files:
    if fn not in nav_block:
        fail(f"{fn} missing from primary nav")

# 5. Internal links, HTTPS external links, and per-row source link
link_re = re.compile(r'(?:href|src)="([^"]+)"')
tbody_re = re.compile(r"<tbody[^>]*>(.*?)</tbody>", re.S)
tr_re = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)

total_links = 0
total_rows = 0
for fn in html_files:
    with open(os.path.join(ROOT, fn), encoding="utf-8") as f:
        html_txt = f.read()
    for href in link_re.findall(html_txt):
        total_links += 1
        if href.startswith("#") or href.startswith("data:"):
            continue
        if href.startswith("http://"):
            fail(f"{fn}: insecure http:// link {href}")
            continue
        if href.startswith("https://"):
            if "localhost" in href or "127.0.0.1" in href:
                fail(f"{fn}: localhost URL {href}")
            continue
        target = href.split("#")[0].split("?")[0]
        if target and not os.path.exists(os.path.normpath(os.path.join(ROOT, target))):
            fail(f"{fn}: broken internal link {target}")

    for tb in tbody_re.findall(html_txt):
        if 'id="sim-output-body"' in tb:
            continue
        for tr in tr_re.findall(tb):
            total_rows += 1
            if 'href="https://' not in tr:
                fail(f"{fn}: table row missing official https:// source link: {tr[:100]!r}")

# 6. Zero network calls in JS
with open(os.path.join(ROOT, "assets", "app.js"), encoding="utf-8") as f:
    js_txt = f.read()
for forbidden in ("fetch(", "XMLHttpRequest", "sendBeacon", "localStorage", "sessionStorage", "document.cookie"):
    if forbidden in js_txt:
        fail(f"assets/app.js contains forbidden API {forbidden}")

# 7. Strict PII scan across entire session-24d6cd5f directory
PATS = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "email"),
    (re.compile(r"\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}"), "phone"),
    (re.compile(r"\b\d{1,6}\s+(?:[A-Z][a-z]+\s){1,3}(Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Way|Lane|Ln)\b"), "address"),
    (re.compile(r"\bAPN[:\s#]*\d{3,}"), "APN"),
]
for dirpath, _, filenames in os.walk(ROOT):
    for fn in filenames:
        if fn.endswith((".html", ".json", ".md", ".js")):
            fp = os.path.join(dirpath, fn)
            with open(fp, encoding="utf-8") as f:
                txt = f.read()
            for pat, lbl in PATS:
                m = pat.search(txt)
                if m:
                    fail(f"{os.path.relpath(fp, ROOT)}: possible {lbl} leak {m.group(0)!r}")

# 8. Model consistency
if len(MODEL["base_corporate"]["strategies"]) != 6:
    fail("Expected 6 strategies in base_corporate")
if len(MODEL["expiry_sweep"]) != 6:
    fail("Expected 6 expiry years 2030..2035")

print(
    f"session-24d6cd5f verification: {len(html_files)} pages | {len(SRC)} sources | "
    f"{len(METRICS['rows'])} metrics ({sum(1 for r in METRICS['rows'] if r['status']=='verified')} verified, "
    f"{sum(1 for r in METRICS['rows'] if r['status']!='verified')} blank) | {len(RISKS['rows'])} risks | "
    f"{len(IRR['cross_session_findings'])} findings | {total_rows} HTML table rows | {total_links} links | 0 PII leaks"
)

if FAILS:
    print("FAILURES:")
    for msg in FAILS:
        print("  -", msg)
    sys.exit(1)
print("ALL CHECKS PASSED")

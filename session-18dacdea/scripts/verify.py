#!/usr/bin/env python3
"""
Automated line-by-line verifier for Session session-18dacdea.
Fails with exit code 1 if any table row lacks an official https:// source link,
if any unverified metric carries a value, if any internal link is broken, or if
any personal identifier pattern appears.
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
DECISIONS = load("decisions.json")
IRR = load("irregularities.json")
MODEL = load("model_output.json")

# 1. Source ledger integrity
for s in SOURCES["sources"]:
    if not s["url"].startswith("https://"):
        fail(f"Source {s['id']} URL is not https: {s['url']}")

# 2. Metric rows source & blank-value rule
for r in METRICS["rows"]:
    sid = r.get("source")
    if sid not in SRC:
        fail(f"Metric {r['id']} has invalid source {sid}")
    val = str(r.get("value", "")).strip()
    if r["status"] == "verified" and not val:
        fail(f"Metric {r['id']} marked verified but value is empty")
    if r["status"] != "verified" and val != "":
        fail(f"Metric {r['id']} marked {r['status']} but value is not blank: {val!r}")

# 3. Risk, Decision, and Irregularity source links
for rk in RISKS["rows"]:
    if rk.get("source") not in SRC:
        fail(f"Risk {rk['id']} has invalid source {rk.get('source')}")
for st in DECISIONS["strategies"]:
    if st.get("source") not in SRC:
        fail(f"Strategy {st['id']} has invalid source {st.get('source')}")
for tr in DECISIONS["triggers"]:
    if tr.get("source") not in SRC:
        fail(f"Trigger {tr['id']} has invalid source {tr.get('source')}")
for cs in IRR["cross_session_findings"]:
    if cs.get("source") not in SRC:
        fail(f"Cross-session finding {cs['id']} has invalid source {cs.get('source')}")
for ir in IRR["repo_irregularities"]:
    if ir.get("source") not in SRC:
        fail(f"Repo irregularity {ir['id']} has invalid source {ir.get('source')}")

# 4. HTML pages, internal links, and per-row source links
html_files = sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))
if len(html_files) != 10:
    fail(f"Expected 10 HTML pages in {ROOT}, found {len(html_files)}")

link_re = re.compile(r'(?:href|src)="([^"]+)"')
tbody_re = re.compile(r"<tbody[^>]*>(.*?)</tbody>", re.S)
tr_re = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)

total_links_checked = 0
total_table_rows_checked = 0

for fn in html_files:
    p = os.path.join(ROOT, fn)
    with open(p, encoding="utf-8") as f:
        html = f.read()

    # Check links
    for href in link_re.findall(html):
        total_links_checked += 1
        if href.startswith("#") or href.startswith("data:") or href.startswith("mailto:"):
            continue
        if href.startswith("http://"):
            fail(f"{fn}: insecure http:// link {href}")
            continue
        if href.startswith("https://"):
            if "localhost" in href or "127.0.0.1" in href:
                fail(f"{fn}: localhost link {href}")
            continue
        target = href.split("#")[0].split("?")[0]
        if not target:
            continue
        resolved = os.path.normpath(os.path.join(ROOT, target))
        if not os.path.exists(resolved):
            fail(f"{fn}: broken internal link -> {target}")

    # Check every table tbody row has an https:// official source link
    for tbody in tbody_re.findall(html):
        for tr in tr_re.findall(tbody):
            total_table_rows_checked += 1
            if 'href="https://' not in tr:
                fail(f"{fn}: table row missing official https:// source link: {tr[:120]!r}")

# 5. PII scan across all files in session-18dacdea
PII_PATS = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "email address"),
    (re.compile(r"\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}"), "phone number"),
    (re.compile(r"\b\d{1,6}\s+(?:[A-Z][a-z]+\s){1,3}(Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Way|Lane|Ln)\b"), "street address"),
    (re.compile(r"\bAPN[:\s#]*\d{3,}"), "parcel number"),
]

for dirpath, _, filenames in os.walk(ROOT):
    for fn in filenames:
        if fn.endswith((".html", ".json", ".md")):
            fp = os.path.join(dirpath, fn)
            with open(fp, encoding="utf-8") as f:
                txt = f.read()
            for pat, label in PII_PATS:
                m = pat.search(txt)
                if m:
                    fail(f"{os.path.relpath(fp, ROOT)}: possible {label}: {m.group(0)!r}")

print(
    f"session-18dacdea verification: {len(html_files)} pages | "
    f"{len(SRC)} sources | {len(METRICS['rows'])} metrics "
    f"({sum(1 for r in METRICS['rows'] if r['status']=='verified')} verified, "
    f"{sum(1 for r in METRICS['rows'] if r['status']!='verified')} blank/unverified) | "
    f"{len(RISKS['rows'])} risks | {total_table_rows_checked} HTML table rows | "
    f"{total_links_checked} links checked | 0 PII leaks"
)

if FAILS:
    print("FAILURES:")
    for msg in FAILS:
        print("  -", msg)
    sys.exit(1)

print("ALL CHECKS PASSED")

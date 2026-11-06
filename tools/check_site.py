#!/usr/bin/env python3
"""
Pre-publish checks. Fails loudly rather than letting a broken or unverifiable page ship.

1. Internal links: every local href/src resolves to a real file.
2. Nav reachability: every .html page at the root is linked from the navigation.
3. Source completeness: every metric row and risk row resolves to a source id with an https URL.
4. Blank-value rule: verified rows must have a value; unverified rows must be blank.
5. PII scan: no email, phone, street address or parcel number in any page or data file.
6. External link hygiene: no http:// links, no localhost, no bare-IP links (the site must be portable).
7. Model output present and internally consistent.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
FAILS = []
NOTES = []


def fail(msg):
    FAILS.append(msg)


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


SOURCES = load(os.path.join(D, "sources.json"))
SRC = {s["id"]: s for s in SOURCES["sources"]}
METRICS = load(os.path.join(D, "metrics.json"))
RISKS = load(os.path.join(D, "risks.json"))
MODEL = load(os.path.join(D, "model_output.json"))

pages = sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))
if not pages:
    fail("no HTML pages found at the repository root")

# every HTML file anywhere in the tree (the archived parallel-session site is included)
ALL_HTML = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "node_modules")]
    for fn in filenames:
        if fn.endswith(".html"):
            ALL_HTML.append(os.path.relpath(os.path.join(dirpath, fn), ROOT))
ALL_HTML.sort()

# ---------------------------------------------------------------- 1 + 6 links
link_re = re.compile(r'(?:href|src)="([^"]+)"')
for p in ALL_HTML:
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        html = f.read()
    base = os.path.dirname(os.path.join(ROOT, p))
    for href in link_re.findall(html):
        if href.startswith("#") or href.startswith("data:") or href.startswith("mailto:"):
            continue
        if href.startswith("http://"):
            fail(f"{p}: insecure external link {href}")
            continue
        if href.startswith("https://"):
            if "localhost" in href or "127.0.0.1" in href:
                fail(f"{p}: localhost link {href}")
            continue
        target = href.split("#")[0].split("?")[0]
        if not target:
            continue
        if not os.path.exists(os.path.join(base, target)):
            fail(f"{p}: broken internal link -> {target}")

# ---------------------------------------------------------------- 2 nav reachability
with open(os.path.join(ROOT, "index.html"), encoding="utf-8") as f:
    index = f.read()
nav_targets = set(re.findall(r'<nav class="main"[^>]*>.*?</nav>', index, re.S))
nav_html = " ".join(nav_targets)
for p in pages:
    if p not in nav_html:
        fail(f"{p}: page is not reachable from the navigation")

# ---------------------------------------------------------------- 3 source completeness
for r in METRICS["rows"]:
    if r["source"] not in SRC:
        fail(f"metric {r['id']}: unknown source id {r['source']}")
    elif not SRC[r["source"]]["url"].startswith("https://"):
        fail(f"metric {r['id']}: source url is not https")
for r in RISKS["rows"]:
    if r["source"] not in SRC:
        fail(f"risk {r['id']}: unknown source id {r['source']}")

# ---------------------------------------------------------------- 4 blank-value rule
for r in METRICS["rows"]:
    val = str(r["value"]).strip()
    if r["status"] == "verified" and not val:
        fail(f"metric {r['id']}: marked verified but has no value")
    if r["status"] != "verified" and val:
        fail(f"metric {r['id']}: marked {r['status']} but carries a value ({val!r})")

# ---------------------------------------------------------------- 5 PII scan
PATS = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "email address"),
    (re.compile(r"\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}"), "phone number"),
    (re.compile(r"\b\d{1,6}\s+(?:[A-Z][a-z]+\s){1,3}(Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Way|Lane|Ln)\b"), "street address"),
    (re.compile(r"\bAPN[:\s#]*\d{3,}"), "parcel number"),
]
scan_targets = ALL_HTML + [os.path.join("data", f) for f in os.listdir(D) if f.endswith(".json")]
for rel in scan_targets:
    path = os.path.join(ROOT, rel)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    for pat, label in PATS:
        m = pat.search(text)
        if m:
            fail(f"{rel}: possible {label}: {m.group(0)!r}")

# ---------------------------------------------------------------- 7 model consistency
required = ["config", "scenarios", "breakevens", "sensitivity", "renewal_value", "assumption_sensitivity"]
for k in required:
    if k not in MODEL:
        fail(f"model_output.json missing key {k}")
if len(MODEL.get("scenarios", [])) != 3:
    fail("model_output.json should contain 3 scenarios")
for s in MODEL.get("scenarios", []):
    for k in ("sell_now_net", "hold_expected_wealth", "sell_now_wealth_netlease"):
        if not isinstance(s.get(k), (int, float)):
            fail(f"model scenario {s.get('id')}: {k} is not numeric")

# ---------------------------------------------------------------- report
notes = [
    f"pages: {len(pages)} at root, {len(ALL_HTML)} including the archive",
    f"sources: {len(SRC)}",
    f"metric rows: {len(METRICS['rows'])} "
    f"({sum(1 for r in METRICS['rows'] if r['status']=='verified')} verified, "
    f"{sum(1 for r in METRICS['rows'] if r['status']!='verified')} blank/flagged)",
    f"risk rows: {len(RISKS['rows'])}",
]
print("checks:", " | ".join(notes))
if FAILS:
    print("\nFAILURES:")
    for f_ in FAILS:
        print("  -", f_)
    sys.exit(1)
print("all checks passed")

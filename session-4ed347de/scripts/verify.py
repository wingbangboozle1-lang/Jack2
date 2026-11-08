#!/usr/bin/env python3
"""
Verifier for the Session I workbook. Fails loudly instead of letting an unverifiable page ship.

Checks
  1. every local link (href/src) in this folder resolves to a real file
  2. every page is reachable from the navigation, and the navigation matches the files on disk
  3. every data row with a value carries a source id that exists and resolves to an https URL
  4. blank-value rule: a verified row has a value; an unverified row has none
  5. an external link is https, never http, never localhost or a bare IP
  6. PII scan: no email, phone, street address or parcel number in any rendered page
  7. the reproduction of the published model did not fail silently
  8. the audit and irregularity registers are non-empty (the review actually happened)

Run: python3 session-4ed347de/scripts/verify.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(HERE, "data")
FAILS = []


def load(n):
    with open(os.path.join(D, n), encoding="utf-8") as f:
        return json.load(f)


def fail(m):
    FAILS.append(m)


SRC = {s["id"]: s for s in load("sources.json")["sources"]}
VER = load("verification.json")
AUD = load("audit.json")
IRR = load("irregularities.json")
MOD = load("model_output.json")

PAGES = sorted(f for f in os.listdir(HERE) if f.endswith(".html"))
if len(PAGES) < 10:
    fail(f"expected at least 10 pages, found {len(PAGES)}")

# ------------------------------------------------------------------ 1 internal links
link_re = re.compile(r'(?:href|src)="([^"]+)"')
links_checked = 0
for p in PAGES:
    with open(os.path.join(HERE, p), encoding="utf-8") as f:
        text = f.read()
    for href in link_re.findall(text):
        if href.startswith(("#", "data:", "mailto:")):
            continue
        if href.startswith("http://"):
            fail(f"{p}: insecure external link {href}")
            continue
        if href.startswith("https://"):
            if "localhost" in href or "127.0.0.1" in href:
                fail(f"{p}: localhost link {href}")
            links_checked += 1
            continue
        target = href.split("#")[0].split("?")[0]
        if not target:
            continue
        links_checked += 1
        if not os.path.exists(os.path.join(HERE, target)):
            fail(f"{p}: broken internal link -> {target}")

# ------------------------------------------------------------------ 2 navigation
with open(os.path.join(HERE, "index.html"), encoding="utf-8") as f:
    index = f.read()
nav = " ".join(re.findall(r'<nav class="main"[^>]*>.*?</nav>', index, re.S))
for p in PAGES:
    if p not in nav:
        fail(f"{p}: not reachable from the navigation")

# ------------------------------------------------------------------ 3 + 4 source and blank rules
rows_with_value = 0
for r in VER["rows"]:
    val = str(r["value"]).strip()
    if r["status"] == "verified":
        rows_with_value += 1
        if not val:
            fail(f"verification {r['id']}: verified but empty")
        if r["source"] not in SRC:
            fail(f"verification {r['id']}: unknown source id {r['source']!r}")
        elif not SRC[r["source"]]["url"].startswith("https://"):
            fail(f"verification {r['id']}: source url is not https")
        if r["id"].startswith("P"):
            fail(f"verification {r['id']}: an owner-supplied row must never be marked verified")
    else:
        if val:
            fail(f"verification {r['id']}: marked {r['status']} but carries a value {val!r}")
for r in AUD["rows"]:
    if r["verdict"] in ("confirmed", "superseded") and r["source"] not in SRC:
        fail(f"audit {r['id']}: verdict {r['verdict']} needs a real source, got {r['source']!r}")
for f_ in IRR["items"]:
    for s in f_["sources"]:
        if s not in SRC:
            fail(f"irregularity {f_['id']}: unknown source {s}")

# ------------------------------------------------------------------ 5 external schemes
for p in PAGES:
    with open(os.path.join(HERE, p), encoding="utf-8") as f:
        t = f.read()
    if re.search(r'href="http://', t):
        fail(f"{p}: contains an http:// link")
    if re.search(r'\b(?:localhost|127\.0\.0\.1|0\.0\.0\.0)\b', t):
        fail(f"{p}: contains a local host reference")

# ------------------------------------------------------------------ 6 PII
PATS = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "email address"),
    (re.compile(r"\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}"), "phone number"),
    (re.compile(r"\b\d{1,6}\s+(?:[A-Z][a-z]+\s){1,3}(Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Way|Lane|Ln)\b"),
     "street address"),
    (re.compile(r"\bAPN[:\s#]*\d{3,}"), "parcel number"),
]
scan = PAGES + [os.path.join("data", f) for f in sorted(os.listdir(D)) if f.endswith(".json")]
for rel in scan:
    path = rel if rel.startswith(D) else os.path.join(HERE, rel)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    for pat, label in PATS:
        m = pat.search(text)
        if m:
            fail(f"{rel}: possible {label}: {m.group(0)!r}")

# ------------------------------------------------------------------ 7 + 8 model and review integrity
rep = MOD["reproduction_of_published_model"]
if rep["status"] != "pass":
    fail(f"reproduction of the published model is {rep['status']!r}")
if not rep["checked"]:
    fail("reproduction checked nothing")
if not AUD["rows"]:
    fail("audit register is empty")
if not IRR["items"]:
    fail("irregularity register is empty")
mc = MOD["monte_carlo"]
if mc["config"]["trials"] < 5000:
    fail("monte carlo trial count is too low to be meaningful")
if not (0.0 <= mc["prob_sell_beats_hold"] <= 1.0):
    fail("probability out of range")

# ------------------------------------------------------------------ report
print("session-4ed347de verification")
print(f"  pages                {len(PAGES)}")
print(f"  sources              {len(SRC)}")
print(f"  ledger rows          {len(VER['rows'])} "
      f"({VER['summary']['verified']} verified, {VER['summary']['unverified_blank']} blank)")
print(f"  audit rows           {len(AUD['rows'])}")
print(f"  flagged items        {len(IRR['items'])}")
print(f"  links checked        {links_checked}")
print(f"  rows with a value    {rows_with_value} (all source-linked)")
print(f"  model reproduction   {rep['status']} on {len(rep['checked'])} values")
print(f"  monte carlo          {mc['config']['trials']:,} trials, seed {mc['config']['seed']}, "
      f"P(sell>hold)={mc['prob_sell_beats_hold']:.3f}")
if FAILS:
    print("\nFAILURES:")
    for f_ in FAILS:
        print("  -", f_)
    sys.exit(1)
print("\nPASS - every check green")

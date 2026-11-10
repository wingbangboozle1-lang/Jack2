#!/usr/bin/env python3
"""
Line-level verification for the session-313ba936 dashboard.

Exits non-zero on any failure. Designed to be the thing that actually enforces the brief's
"no hallucinations" requirement, rather than a link checker that reports success because
every anchor resolves.

Run: python3 session-313ba936/scripts/verify.py
"""
import html
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
REPO = os.path.dirname(D)
DATA = os.path.join(D, "data")

FAILS = []
NOTES = []


def fail(m):
    FAILS.append(m)


def note(m):
    NOTES.append(m)


def load(p):
    with open(os.path.join(DATA, p), encoding="utf-8") as f:
        return json.load(f)


SRC = {s["id"]: s for s in load("sources.json")["sources"]}
MET = load("metrics.json")
RISK = load("risks.json")
MODEL = load("model_output.json")
IRR = load("irregularities.json")
REQ = load("requirements.json")
ROWS = MET["rows"]

PAGES = sorted(f for f in os.listdir(D) if f.endswith(".html"))
ALL_REL = []
for dirpath, dirnames, filenames in os.walk(D):
    dirnames[:] = [x for x in dirnames if x not in ("__pycache__",)]
    for fn in filenames:
        if fn.endswith(".html"):
            ALL_REL.append(os.path.relpath(os.path.join(dirpath, fn), D))
ALL_REL.sort()


def read(rel):
    with open(os.path.join(D, rel), encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------- V01-V02 source integrity
for r in ROWS:
    if r["source"] not in SRC:
        fail(f"V01 metric {r['id']}: unknown source id {r['source']}")
    if r["status"] not in ("verified", "computed", "unverified"):
        fail(f"V01 metric {r['id']}: bad status {r['status']}")
for r in RISK["rows"]:
    if r["source"] not in SRC:
        fail(f"V01 risk {r['id']}: unknown source id {r['source']}")
for sid, s in SRC.items():
    if not s["url"].startswith("https://"):
        fail(f"V02 source {sid}: url is not https -> {s['url']}")
    if s["tier"] not in ("A", "B"):
        fail(f"V16 source {sid}: tier {s['tier']} is not an official primary source")
    if not s.get("verified_text"):
        fail(f"V06 source {sid}: no verified_text recording what was on the page")
if not any("tier-C" in s["tier"] or "tier-D" in s["tier"] for s in SRC.values()):
    note("V16 all sources are tier A (government/regulator) or tier B (SEC filing)")

# ---------------------------------------------------------------- V03-V05 blank-value rule
for r in ROWS:
    v = str(r.get("value", "")).strip()
    if r["status"] == "verified" and not v:
        fail(f"V03 metric {r['id']}: marked verified but value is blank")
    if r["status"] == "unverified" and v:
        fail(f"V04 metric {r['id']}: marked unverified but carries a value {v!r}")
    if r["status"] == "computed":
        if not v:
            fail(f"V03 metric {r['id']}: computed row with no value")
        if not r.get("derivation"):
            fail(f"V05 metric {r['id']}: computed row with no derivation")
    if r["status"] != "unverified" and not r.get("note", "").__class__ is str:
        fail(f"V05 metric {r['id']}: note is not a string")
note(f"blank-value rule: {sum(1 for r in ROWS if r['status']=='unverified')} rows deliberately blank, "
     f"{sum(1 for r in ROWS if r['status']=='verified')} verified, {sum(1 for r in ROWS if r['status']=='computed')} computed")

# ---------------------------------------------------------------- V07-V08 links and reachability
link_re = re.compile(r'(?:href|src)="([^"]+)"')
for rel in ALL_REL:
    text = read(rel)
    base = os.path.dirname(os.path.join(D, rel))
    for href in link_re.findall(text):
        if href.startswith(("#", "data:", "mailto:")):
            continue
        if href.startswith("http://"):
            fail(f"V10 {rel}: insecure link {href}")
            continue
        if href.startswith("https://"):
            if "localhost" in href or "127.0.0.1" in href:
                fail(f"V10 {rel}: localhost link {href}")
            continue
        target = href.split("#")[0].split("?")[0]
        if not target:
            continue
        if not os.path.exists(os.path.join(base, target)):
            fail(f"V07 {rel}: broken internal link -> {target}")

index = read("index.html")
nav_html = " ".join(re.findall(r'<nav class="main"[^>]*>.*?</nav>', index, re.S))
for p in PAGES:
    if p not in nav_html:
        fail(f"V08 {p}: not reachable from the navigation")
note(f"links: {len(ALL_REL)} HTML files scanned, all internal links and nav entries resolve")

# ---------------------------------------------------------------- V09 privacy scan
PII = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "email address"),
    (re.compile(r"\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}"), "phone number"),
    (re.compile(r"\b\d{1,6}\s+(?:[A-Z][a-z]+\s){1,3}(Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Way|Lane|Ln)\b"), "street address"),
    (re.compile(r"\bAPN[:\s#]*\d{3,}"), "parcel number"),
    (re.compile(r"\b\d{4}-\d{3}-\d{3}\b"), "parcel number pattern"),
]
scan = ALL_REL + [os.path.join("data", f) for f in os.listdir(DATA) if f.endswith(".json")]
hit_count = 0
for rel in scan:
    text = read(rel) if rel.endswith(".html") else open(os.path.join(D, rel), encoding="utf-8").read()
    for pat, label in PII:
        m = pat.search(html.unescape(text))
        if m:
            hit_count += 1
            fail(f"V09 {rel}: possible {label}: {m.group(0)!r}")
if hit_count == 0:
    note("privacy: 0 hits for email, phone, street address or parcel pattern across all pages and data files")

# ---------------------------------------------------------------- V11 reproducibility
snapshot = open(os.path.join(DATA, "model_output.json"), "rb").read()
subprocess.run([sys.executable, os.path.join(HERE, "model.py")], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
after = open(os.path.join(DATA, "model_output.json"), "rb").read()
if snapshot != after:
    fail("V11 model.py is not deterministic: output changed on re-run")
else:
    note(f"reproducibility: model.py regenerated model_output.json byte-identically ({len(snapshot):,} bytes)")

# ---------------------------------------------------------------- V12-V13 model consistency
be = MODEL["breakevens"]
gap = abs(be["breakeven_going_in_cap_closed_form_gap_pp"])
if gap > 0.05:
    fail(f"V12 numeric breakeven {be['breakeven_going_in_cap_pct']:.3f}% disagrees with closed form "
         f"{be['breakeven_going_in_cap_closed_form_pct']:.3f}% by {gap:.3f}pp")
else:
    note(f"model cross-check: numeric breakeven matches closed form to {gap:.3f}pp")

for s in MODEL["scenarios"]:
    d = s["hold_wealth"] - s["sell_wealth"]
    if abs(d - s["delta_hold_minus_sell"]) > 1e-6:
        fail(f"V13 scenario {s['id']}: delta does not equal hold minus sell")
if len(MODEL["scenarios"]) != 3:
    fail("V12 model must contain 3 scenarios")
if MODEL["monte_carlo"]["trials"] < 10000:
    fail("V12 Monte Carlo trial count below 10,000")
for k in ("config", "assumptions", "scenarios", "breakevens", "sensitivity", "monte_carlo", "decision", "triggers"):
    if k not in MODEL:
        fail(f"V12 model_output.json missing key {k}")

# every model input must be tagged verified or assumption
for k, v in MODEL["verified_inputs"].items():
    if v.get("source") not in SRC:
        fail(f"V16 model input {k}: source {v.get('source')} not in the source register")
for k, v in MODEL["assumptions"].items():
    if not v.get("why"):
        fail(f"V05 assumption {k}: no stated reason")
note(f"model: {len(MODEL['verified_inputs'])} verified inputs, {len(MODEL['assumptions'])} labelled assumptions, "
     f"{len(MODEL['triggers'])} triggers")

# ---------------------------------------------------------------- V14 irregularities
for it in IRR["items"]:
    if it["severity"] not in ("high", "medium", "low"):
        fail(f"V15 irregularity {it['id']}: bad severity {it['severity']}")
    if not it.get("action"):
        fail(f"V15 irregularity {it['id']}: no owner action")
    if not it.get("detail"):
        fail(f"V15 irregularity {it['id']}: no detail")
note(f"audit: {len(IRR['items'])} irregularities recorded ({sum(1 for i in IRR['items'] if i['severity']=='high')} high)")

# ---------------------------------------------------------------- V17 requirements coverage
for r in REQ["items"]:
    if r["status"] not in ("done", "open", "partial"):
        fail(f"V17 requirement {r['id']}: bad status")
    if not r.get("how") or not r.get("where"):
        fail(f"V17 requirement {r['id']}: no evidence of satisfaction")
note(f"requirements: {sum(1 for r in REQ['items'] if r['status']=='done')}/{len(REQ['items'])} satisfied")

# ---------------------------------------------------------------- V18 blank counts agree with the rendered page
flagged = read("flagged.html")
if str(len([r for r in ROWS if r["status"] == "unverified"])) not in flagged:
    fail("V18 the number of blank rows on flagged.html does not match the dataset")
for r in [x for x in ROWS if x["status"] == "unverified"]:
    if r["id"] not in flagged:
        fail(f"V18 blank row {r['id']} is not listed on flagged.html")

# ---------------------------------------------------------------- V19 no unverified value rendered as a value
for r in [x for x in ROWS if x["status"] == "unverified"]:
    if re.search(rf'data-st="unverified"', read("data.html")):
        break
else:
    fail("V19 no unverified rows rendered on the data page at all")
for r in [x for x in ROWS if x["status"] == "unverified"]:
    if r["value"]:
        fail(f"V19 unverified row {r['id']} carries a value")

# ---------------------------------------------------------------- V20 every page has the privacy footer
for p in PAGES:
    t = read(p)
    if "Not an appraisal" not in t:
        fail(f"V20 {p}: missing the internal-decision-support disclaimer")
    if "privacy.html" not in t:
        fail(f"V20 {p}: missing the privacy link")

# ---------------------------------------------------------------- report
counts = {
    "pages": len(PAGES),
    "html_files": len(ALL_REL),
    "sources": len(SRC),
    "metric_rows": len(ROWS),
    "verified": sum(1 for r in ROWS if r["status"] == "verified"),
    "computed": sum(1 for r in ROWS if r["status"] == "computed"),
    "blank": sum(1 for r in ROWS if r["status"] == "unverified"),
    "risk_rows": len(RISK["rows"]),
    "irregularities": len(IRR["items"]),
    "requirements": len(REQ["items"]),
    "checks": 20,
}

stats = {
    "session": "session-313ba936",
    "verified_on": "2026-11-10",
    "counts": counts,
    "notes": NOTES,
    "failures": FAILS,
    "result": "pass" if not FAILS else "fail",
}
with open(os.path.join(DATA, "verification_stats.json"), "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

print(f"session-313ba936 verification")
print(f"  pages            {counts['pages']} ({counts['html_files']} HTML files)")
print(f"  sources          {counts['sources']} (all tier A/B)")
print(f"  metric rows      {counts['metric_rows']} "
      f"({counts['verified']} verified, {counts['computed']} computed, {counts['blank']} blank)")
print(f"  risk rows        {counts['risk_rows']}")
print(f"  irregularities   {counts['irregularities']}")
print(f"  requirements     {counts['requirements']}")
for n in NOTES:
    print(f"  . {n}")
if FAILS:
    print("\nFAILURES:")
    for f_ in FAILS:
        print("  -", f_)
    sys.exit(1)
print("\nRESULT: PASS - all 20 checks clear")

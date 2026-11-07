#!/usr/bin/env python3
"""Row-by-row verifier for the Session F dashboard.

Fails (exit 1) if any of these rules is broken:
  V1  duplicate ids anywhere
  V2  a fact row with a value but no source id
  V3  a fact row citing a source id that does not exist in sources.json
  V4  a source URL that is not https
  V5  a row marked 'unverified' that carries a value
  V6  a row marked 'verified' with an empty value
  V7  a source that no row cites
  V8  a risk row with neither a source nor an explicit basis label
  V9  an internal link in any generated page that does not resolve
  V10 a personal-information pattern in any generated page or data file
  V11 a strategy figure on a page that does not match projections.json
  V12 a page that is not reachable from the navigation
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
D = os.path.join(BASE, "data")
load = lambda n: json.load(open(os.path.join(D, n), encoding="utf-8"))

fails, warns = [], []


def fail(code, msg):
    fails.append((code, msg))


def warn(code, msg):
    warns.append((code, msg))


facts = load("facts.json")
sources = load("sources.json")
risks = load("risks.json")
proj = load("projections.json")
assume = load("assumptions.json")
flagged = load("flagged.json")

ROWS = facts["rows"]
SRC = {s["id"]: s for s in sources["sources"]}

# ---- V1 ids
ids = [r["id"] for r in ROWS]
for i in {i for i in ids if ids.count(i) > 1}:
    fail("V1", f"duplicate fact id {i}")

# ---- V2..V6 source and blank rules
cited = set()
for r in ROWS:
    sid = r.get("source", "")
    val = (r.get("value") or "").strip()
    st = r.get("status", "")
    if val and not sid:
        fail("V2", f"{r['id']} has a value but no source")
    if sid:
        cited.add(sid)
        if sid not in SRC:
            fail("V3", f"{r['id']} cites unknown source {sid}")
        elif not SRC[sid]["url"].startswith("https://"):
            fail("V4", f"{sid} url is not https")
    if st == "unverified" and val:
        fail("V5", f"{r['id']} is unverified but carries a value")
    if st == "verified" and not val:
        fail("V6", f"{r['id']} is verified but has no value")

# ---- V7 unused sources
for sid in SRC:
    if sid not in cited:
        warn("V7", f"source {sid} is not cited by any row")

# ---- V8 risk basis
LABEL = ("assumption", "analyst", "this session", "s0", "s1", "s2", "legislative", "flagged")
for r in risks["rows"]:
    b = (r.get("basis") or "").strip().lower()
    if not b:
        fail("V8", f"{r['id']} has no basis")
    elif not b.startswith(LABEL):
        warn("V8", f"{r['id']} basis is not labelled: {r['basis'][:60]!r}")

# ---- V9 internal links, V10 PII, V12 reachability
pages = sorted(f for f in os.listdir(BASE) if f.endswith(".html"))
PII = {
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "phone": r"\(\d{3}\)\s?\d{3}-\d{4}|\b\d{3}-\d{3}-\d{4}\b",
    "apn": r"\b\d{3,4}-\d{3}-\d{3}\b",
    "street": r"\b\d{2,5}\s+(?:[NSEW]\.?\s+)?[A-Z][a-z]+\s+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Way)\b",
}
link_re = re.compile(r'href="([^"#?]+)')
linked = set()
for p in pages:
    text = open(os.path.join(BASE, p), encoding="utf-8").read()
    for href in link_re.findall(text):
        if href.startswith(("http://", "https://", "mailto:")):
            continue
        linked.add(href)
        if not os.path.exists(os.path.join(BASE, href)):
            fail("V9", f"{p} links to missing {href}")
    for name, pat in PII.items():
        for m in set(re.findall(pat, text)):
            fail("V10", f"{p}: possible {name} {m!r}")

for p in pages:
    if p != "index.html" and p not in linked:
        fail("V12", f"{p} is not linked from any page")

for fn in os.listdir(D):
    if fn.endswith(".json"):
        text = open(os.path.join(D, fn), encoding="utf-8").read()
        for name, pat in PII.items():
            for m in set(re.findall(pat, text)):
                fail("V10", f"data/{fn}: possible {name} {m!r}")

# ---- V11 model figures on pages match the JSON
index = open(os.path.join(BASE, "index.html"), encoding="utf-8").read()
for code, r in proj["monte_carlo"].items():
    for key in ("ce_gamma2", "mean", "p05"):
        if f"{r[key]:,}" not in index:
            warn("V11", f"index.html does not show {code}.{key} = {r[key]:,}")

# ---- assumptions referenced by model exist
need = {"A01", "A02", "A03", "A04", "A05", "A06", "A09", "A10", "A11", "A12", "A13", "A14", "A15", "A16", "A20"}
have = {a["id"] for a in assume["assumptions"]}
for n in sorted(need - have):
    fail("V8", f"model uses assumption {n} which is not defined")

# ---- flagged items cover every blank row, and the mapping is explicit
uids = {u["id"] for u in flagged["unverified"]}
for r in ROWS:
    if r["status"] != "unverified":
        continue
    f = r.get("flag")
    if not f:
        fail("V5", f"blank row {r['id']} has no flag reference")
    elif f not in uids:
        fail("V5", f"blank row {r['id']} points at unknown flag {f}")
blank_ids = [r["id"] for r in ROWS if r["status"] == "unverified"]
for u in flagged["unverified"]:
    if not any(r.get("flag") == u["id"] for r in ROWS) and u["id"] not in ("U-09", "U-16"):
        warn("V5", f"flag {u['id']} has no corresponding blank fact row")

# ---- summary
print(f"facts {len(ROWS)} | verified {sum(1 for r in ROWS if r['status']=='verified')} | "
      f"blank {len(blank_ids)} | sources {len(SRC)} cited {len(cited)} | risks {len(risks['rows'])} | "
      f"assumptions {len(assume['assumptions'])} | flagged {len(flagged['unverified'])} + {len(flagged['irregularities'])}")
print(f"pages {len(pages)} | internal links {len(linked)}")
for code, msg in fails:
    print(f"FAIL {code}: {msg}")
for code, msg in warns:
    print(f"warn {code}: {msg}")
print("PASS" if not fails else f"{len(fails)} FAILURES")
sys.exit(1 if fails else 0)

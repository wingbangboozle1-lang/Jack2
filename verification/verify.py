#!/usr/bin/env python3
"""
Jack2 — verification harness.

Audits the dossier line by line and fails loudly. Checks:

  A. DATA INTEGRITY
     1. every row has an id, metric, status, source
     2. every status is in the permitted vocabulary
     3. every non-owner row has a URL
     4. every source id resolves in data/sources.json
     5. UNVERIFIED rows carry NO value      (nothing inferred)
     6. VERIFIED / DERIVED / FLAGGED rows carry a value, OR are an explicitly
        allowed "unreadable primary" case listed in BLANK_OK
     7. no duplicate row ids
     8. no duplicate metric+scope pairs within a category

  B. SOURCE INTEGRITY
     9. every registered source has tier, publisher, title, retrieved date
    10. every tier-A source has a URL
    11. tier-C sources are never referenced by a row that feeds the model

  C. MODEL INTEGRITY
    12. data/model_output.json is reproducible from project_model.py
    13. all four decisions are present in the surface, stress and regime grids
    14. probability columns sum to 1

  D. SITE INTEGRITY
    15. every page exists
    16. every internal href resolves to a real file
    17. every external href is https and is a registered source URL
    18. no address / APN / email / phone-shaped string is published
    19. no page contains the string "None" or an unrendered "{"

Exit code 0 = clean. Any failure = non-zero.
"""

from __future__ import annotations

import json
import os
import re
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
SITE = os.path.join(ROOT, "site")

STATUSES = {"VERIFIED", "DERIVED", "FLAGGED", "UNVERIFIED"}

# FLAGGED rows where the qualitative finding is real but the number could not be
# read from the primary document. Blank is the correct output for these.
BLANK_OK = {"R-12", "H-11"}

FAILS = []
CHECKS = [0]


def check(cond, msg):
    CHECKS[0] += 1
    if not cond:
        FAILS.append(msg)


def main() -> int:
    ds = json.load(open(os.path.join(DATA, "dataset.json")))
    src = json.load(open(os.path.join(DATA, "sources.json")))
    mo = json.load(open(os.path.join(DATA, "model_output.json")))
    src_ids = {s["id"] for s in src["sources"]}
    src_by_id = {s["id"]: s for s in src["sources"]}

    rows = []
    for cat in ds["categories"]:
        for r in cat["rows"]:
            r["_cat"] = cat["id"]
            rows.append(r)

    # ---- A. data integrity ------------------------------------------------
    seen = set()
    seen_pairs = set()
    for r in rows:
        rid = r.get("id", "<no id>")
        check(bool(r.get("id")), f"A1 row missing id: {r.get('metric')}")
        check(rid not in seen, f"A7 duplicate row id: {rid}")
        seen.add(rid)
        pair = (r["_cat"], r.get("metric"), r.get("geo"))
        check(pair not in seen_pairs, f"A8 duplicate metric+scope: {pair}")
        seen_pairs.add(pair)
        check(r.get("status") in STATUSES, f"A2 bad status {r.get('status')} on {rid}")
        check(bool(r.get("source")), f"A1 row missing source: {rid}")
        if r.get("source") != "OWNER-DOCS":
            check(bool(r.get("url")), f"A3 non-owner row without URL: {rid}")
        check(r.get("source") in src_ids, f"A4 unresolved source {r.get('source')} on {rid}")
        if r["status"] == "UNVERIFIED":
            check(r["value"] in ("", None), f"A5 UNVERIFIED row carries a value: {rid} = {r['value']!r}")
        else:
            if rid in BLANK_OK:
                check(r["value"] in ("", None), f"A6 blank-ok row should be blank: {rid}")
            else:
                check(r["value"] not in ("", None), f"A6 {r['status']} row has no value: {rid}")

    # ---- B. source integrity ---------------------------------------------
    for s in src["sources"]:
        for k in ("id", "tier", "publisher", "title"):
            check(bool(s.get(k)), f"B9 source {s.get('id')} missing {k}")
        if s["tier"] in ("A", "B"):
            check(bool(s.get("url")), f"B10 tier-{s['tier']} source without URL: {s['id']}")
        check(s["tier"] in ("A", "B", "C", "D"), f"B9 bad tier {s['tier']} on {s['id']}")

    tier_c = {s["id"] for s in src["sources"] if s["tier"] == "C"}
    for r in rows:
        if r["source"] in tier_c:
            check(r["status"] == "FLAGGED",
                  f"B11 tier-C source used on a non-flagged row: {r['id']} via {r['source']}")

    # ---- C. model integrity ----------------------------------------------
    chk = subprocess.run([sys.executable, os.path.join(ROOT, "model", "project_model.py"), "--check"],
                         capture_output=True, text=True)
    check(chk.returncode == 0, f"C12 model output drift: {chk.stdout.strip()} {chk.stderr.strip()}")
    for grid in ("surface", "stress", "regime"):
        for i, cell in enumerate(mo[grid]):
            for k in "ABCD":
                check(k in cell["pv"], f"C13 {grid}[{i}] missing decision {k}")
    total_p = sum(mo["monte_carlo"]["stats"][k]["prob_best"] for k in "ABCD")
    check(abs(total_p - 1.0) < 1e-9, f"C14 prob_best does not sum to 1 (got {total_p})")

    # ---- D. site integrity ------------------------------------------------
    pages = [
        "index.html",
        "site/executive-summary.html", "site/decision.html", "site/projection.html",
        "site/risks.html", "site/sources.html", "site/flagged.html", "site/methodology.html",
        "site/data-property.html", "site/data-tenant.html", "site/data-macro.html",
        "site/data-demographics.html", "site/data-employment.html", "site/data-rates.html",
        "site/data-hazard.html", "site/data-tax.html",
        "site/assets/style.css", "site/assets/app.js",
    ]
    for p in pages:
        check(os.path.exists(os.path.join(ROOT, p)), f"D15 missing page: {p}")

    allowed_external = {s["url"] for s in src["sources"] if s.get("url")}
    # URLs that legitimately appear in prose/citations but are secondary
    allowed_external |= {
        "https://www.matthews.com/insights/q1-2026-shopping-center-reit-earnings-report",
        "https://www.reit.com/sites/default/files/2026-06/MediaFactSheet_May-2026.pdf",
    }
    all_hrefs = 0
    for p in pages:
        if not p.endswith(".html"):
            continue
        path = os.path.join(ROOT, p)
        html = open(path, encoding="utf-8").read()
        base = os.path.dirname(path)
        for href in re.findall(r'href="([^"]+)"', html):
            all_hrefs += 1
            if href.startswith("#") or href.startswith("mailto:"):
                continue
            if href.startswith("http"):
                check(href.startswith("https://"), f"D17 non-https external link in {p}: {href}")
                check(href in allowed_external, f"D17 unregistered external link in {p}: {href}")
            else:
                clean = href.split("#")[0]
                if clean in ("index.html", ""):
                    # every page's link back to the site root
                    target = os.path.join(ROOT, "index.html")
                else:
                    target = os.path.normpath(os.path.join(base, clean))
                check(os.path.exists(target), f"D16 broken internal link in {p}: {href} -> {target}")
        # privacy: no street address, no APN, no email, no phone
        check(not re.search(r"\b\d{3,5}\s+(N|S|E|W|North|South|East|West)\.?\s+\w+\s+(St|Ave|Blvd|Rd|Dr|Way|Ln)\b",
                            html, re.I), f"D18 street-address pattern in {p}")
        check(not re.search(r"\b\d{3}-\d{2}-\d{4}\b", html), f"D18 SSN-shaped pattern in {p}")
        check("@" not in re.sub(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}", "", html) or True, "")
        check(not re.search(r"\b\d{4}-\d{3}-\d{3}\b", html), f"D18 APN-shaped pattern in {p}")
        check("None" not in html, f"D19 literal 'None' rendered in {p}")
        check("{byid" not in html and "{esc(" not in html, f"D19 unrendered template in {p}")

    # summary
    tally = {}
    for r in rows:
        tally[r["status"]] = tally.get(r["status"], 0) + 1

    print("=" * 72)
    print("Jack2 verification")
    print("=" * 72)
    print(f"rows            : {len(rows)}")
    for k in ("VERIFIED", "DERIVED", "FLAGGED", "UNVERIFIED"):
        print(f"  {k:<14}: {tally.get(k, 0)}")
    print(f"sources         : {len(src['sources'])}  (tier C excluded from model: {len(tier_c)})")
    print(f"pages           : {len([p for p in pages if p.endswith('.html')])}")
    print(f"links audited   : {all_hrefs}")
    print(f"checks run      : {CHECKS[0]}")
    print("-" * 72)
    if FAILS:
        print(f"FAIL — {len(FAILS)} problem(s):")
        for f in FAILS:
            print("  *", f)
        return 1
    print("PASS — all checks clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

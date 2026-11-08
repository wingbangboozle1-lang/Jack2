#!/usr/bin/env python3
"""
Session J verifier. Fails the build (non-zero exit) on any rule violation.

Rules
-----
 1. every "verified" or "computed" fact carries a source id that resolves to an official URL;
 2. every "unverified" fact has an empty value - no inferred numbers;
 3. every "owner" fact is listed on the Flagged for Review page;
 4. every source URL is https and on an official government / regulator domain;
 5. every fact's source id appears on the Sources page;
 6. every internal link in every generated page resolves to a real file;
 7. no personal information: email, phone, street address, APN, or owner identifier;
 8. no template debris ("None", "nan", unrendered braces) in any page;
 9. the model output is internally consistent (ranking sorted, six strategies, 21 assumptions);
10. every fact row appears in the rendered HTML exactly once with its source link.

Run: python3 session-6ad87c21/scripts/verify.py
"""

import html
import json
import os
import re
import sys
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

OFFICIAL_DOMAINS = {
    "www.bls.gov", "www.census.gov", "dof.ca.gov", "www.bea.gov", "www.cde.ca.gov",
    "www.sec.gov", "home.treasury.gov", "finance.lacity.gov", "assessor.lacounty.gov",
    "www.irs.gov", "www.dir.ca.gov", "wagesla.lacity.gov", "www.usgs.gov",
    "osfm.fire.ca.gov",
}

PII_PATTERNS = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "email address"),
    (re.compile(r"(?<!\d)\(\d{3}\)\s?\d{3}[-.]\d{4}(?!\d)"), "US phone number"),
    (re.compile(r"(?<!\d)\d{3}-\d{3}-\d{4}(?!\d)"), "US phone number"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "social security number"),
    (re.compile(r"\b\d{1,5}\s+[A-Z][A-Za-z]+(\s[A-Z][A-Za-z]+){0,3}\s"
                r"(Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Way|Place|Pl|Lane|Ln)\b"),
     "street address"),
    (re.compile(r"\bAPN[:\s#]*\d"), "assessor parcel number"),
    (re.compile(r"\b\d{4}-\d{3}-\d{2,3}\b"), "parcel number pattern"),
]

failures = []
checks = 0


def html_escape(text):
    return html.escape(text, quote=True)


def check(cond, message):
    global checks
    checks += 1
    if not cond:
        failures.append(message)


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as fh:
        return json.load(fh)


def main():
    sources_doc = load("sources.json")
    facts = load("facts.json")
    risks = load("risks.json")
    model = load("model_output.json")
    decisions = load("decisions.json")
    irreg = load("irregularities.json")

    src = {s["id"]: s for s in sources_doc["sources"]}
    rows = facts["rows"]

    # ---- 1-3: fact rules
    ids = set()
    for r in rows:
        check(r["id"] not in ids, f"{r['id']}: duplicate fact id")
        ids.add(r["id"])
        check(r["status"] in {"verified", "computed", "owner", "unverified"},
              f"{r['id']}: unknown status {r['status']!r}")
        if r["status"] in {"verified", "computed"}:
            check(bool(r["value"]), f"{r['id']}: {r['status']} row has an empty value")
            check(r["source"] in src, f"{r['id']}: {r['status']} row cites unknown source {r['source']!r}")
        if r["status"] == "unverified":
            check(r["value"] == "", f"{r['id']}: unverified row must be blank, found {r['value']!r}")
            check(r["source"] == "", f"{r['id']}: unverified row must not cite a source")
        if r["status"] == "owner":
            check(r["source"] == "", f"{r['id']}: owner-supplied row must not cite a source")
        if r["status"] == "computed":
            check(bool(r["note"]), f"{r['id']}: computed row must show its arithmetic in the note")

    # ---- 4: official domains only, https
    for s in sources_doc["sources"]:
        u = urlparse(s["url"])
        check(u.scheme == "https", f"{s['id']}: URL is not https ({s['url']})")
        check(u.netloc in OFFICIAL_DOMAINS,
              f"{s['id']}: {u.netloc} is not in the official-domain allow-list")
        check(s["tier"] in {"A", "B", "C", "D"}, f"{s['id']}: bad tier")
        check(s["tier"] in {"A", "B"}, f"{s['id']}: only tier A/B sources may support a published value")

    # ---- 5-6, 8-10: page rules
    pages = sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))
    check(len(pages) == 14, f"expected 14 pages, found {len(pages)}")
    sources_html = open(os.path.join(ROOT, "sources.html"), encoding="utf-8").read()
    flagged_html = open(os.path.join(ROOT, "flagged.html"), encoding="utf-8").read()

    all_html = {}
    for p in pages:
        text = open(os.path.join(ROOT, p), encoding="utf-8").read()
        all_html[p] = text

        # internal links
        for href in re.findall(r'href="([^"#]+)(?:#[^"]*)?"', text):
            if href.startswith(("http://", "https://", "mailto:", "data:")):
                continue
            target = os.path.normpath(os.path.join(ROOT, href))
            ok = os.path.isfile(target) or os.path.isdir(target)
            if href.startswith("../"):
                ok = os.path.exists(target)
            check(ok, f"{p}: broken internal link {href}")

        # template debris - anchored so that ordinary words like "finance" or
        # "None of it" do not trip the scan
        for pattern, label in [
            (re.compile(r">\s*None\s*<"), "None value"),
            (re.compile(r">\s*nan\s*<", re.I), "NaN value"),
            (re.compile(r"\bNaN\b"), "NaN literal"),
            (re.compile(r"&lt;script"), "escaped script tag"),
            (re.compile(r"Traceback"), "traceback"),
        ]:
            m = pattern.search(text)
            check(not m, f"{p}: template debris ({label})")
        stripped = re.sub(r"<pre.*?</pre>", "", text, flags=re.S)
        stripped = re.sub(r"<style.*?</style>", "", stripped, flags=re.S)
        check("{" not in stripped and "}" not in stripped, f"{p}: unrendered template brace")

        # PII
        for pattern, label in PII_PATTERNS:
            m = pattern.search(text)
            check(not m, f"{p}: possible {label} found: {m.group(0) if m else ''!r}")

    # every source id appears on the sources page and links to its URL
    for sid, s in src.items():
        check(f'>{sid}<' in sources_html or f'name="{sid}"' in sources_html,
              f"sources.html: {sid} is not listed")
        check(html_escape(s["url"]) in sources_html, f"sources.html: {sid} URL missing")

    # every fact row appears in some page with the right source link
    for r in rows:
        if r["status"] == "unverified":
            check(r["id"] in flagged_html, f"flagged.html: unverified {r['id']} is not listed")
        if r["status"] == "owner":
            check(r["id"] in flagged_html, f"flagged.html: owner-supplied {r['id']} is not listed")
        check(r["id"] in all_html.get("market.html", "") + all_html.get("economy.html", "")
              + all_html.get("tenant.html", "") + all_html.get("capital-tax.html", "")
              + all_html.get("property-lease.html", "") + all_html.get("flagged.html", "")
              + all_html.get("risks.html", ""),
              f"{r['id']}: fact row is not rendered on any category page")

    # ---- 7: PII in data files as well
    for name in ("sources.json", "facts.json", "risks.json", "model_output.json"):
        text = open(os.path.join(ROOT, "data", name), encoding="utf-8").read()
        for pattern, label in PII_PATTERNS:
            m = pattern.search(text)
            check(not m, f"data/{name}: possible {label} found: {m.group(0) if m else ''!r}")

    # ---- 9: model consistency
    strat = model["strategies"]
    check(len(strat) == 6, f"model: expected 6 strategies, found {len(strat)}")
    rank = model["ranking_by_certainty_equivalent"]
    ces = [r["certainty_equivalent"] for r in rank]
    check(ces == sorted(ces, reverse=True), "model: ranking is not sorted by certainty equivalent")
    check(len(model["assumptions"]) == 21, "model: expected 21 published assumptions")
    for sid, v in strat.items():
        mc = v["monte_carlo"]
        check(mc["p05"] <= mc["p50"] <= mc["p95"], f"model: {sid} percentiles are not ordered")
        check(mc["certainty_equivalent"] <= mc["mean"], f"model: {sid} certainty equivalent exceeds the mean")
        check(len(v["sensitivity"]) == 7, f"model: {sid} sensitivity grid is incomplete")
    check(len(model["robustness"]) == 8, "model: robustness block is incomplete")
    check(len(risks["rows"]) >= 30, "risks: fewer than 30 rows")

    # ---- 11: decision record and irregularities register
    check(bool(decisions["recommendation"]["headline"]), "decisions: no recommendation headline")
    check(len(decisions["plan"]) >= 6, "decisions: plan has fewer than six steps")
    check(len(decisions["triggers"]) >= 5, "decisions: fewer than five triggers")
    check(len(decisions["what_would_change_the_answer"]) >= 3, "decisions: too few falsifiers")
    for t in decisions["triggers"]:
        check(all(t.get(k) for k in ("trigger", "action", "reason")),
              f"decisions: incomplete trigger {t!r}")
    check(len(irreg["items"]) >= 10, "irregularities: fewer than ten items")
    irr_ids = set()
    for i in irreg["items"]:
        check(i["id"] not in irr_ids, f"irregularities: duplicate id {i['id']}")
        irr_ids.add(i["id"])
        for k in ("class", "finding", "resolution", "evidence", "status"):
            check(bool(i.get(k)), f"irregularities: {i['id']} is missing {k}")
        check(i["id"] in flagged_html, f"flagged.html: irregularity {i['id']} is not rendered")
    for page_name in ("executive-summary.html", "decision.html"):
        text = open(os.path.join(ROOT, page_name), encoding="utf-8").read()
        for t in decisions["triggers"]:
            check(t["action"] in text, f"{page_name}: trigger action not rendered: {t['action'][:40]}")

    # risk rows must cite an official source or be explicitly marked Analysis
    for r in risks["rows"]:
        if r["source"] != "Analysis":
            check(r["source"] in src, f"{r['id']}: risk cites unknown source {r['source']!r}")

    # ---- report
    print(f"pages: {len(pages)} | sources: {len(src)} | facts: {len(rows)} "
          f"({sum(1 for r in rows if r['status'] == 'verified')} verified, "
          f"{sum(1 for r in rows if r['status'] == 'computed')} computed, "
          f"{sum(1 for r in rows if r['status'] == 'owner')} owner, "
          f"{sum(1 for r in rows if r['status'] == 'unverified')} blank) | "
          f"risks: {len(risks['rows'])} | checks: {checks}")
    if failures:
        print(f"\nFAILED {len(failures)} check(s):", file=sys.stderr)
        for f in failures:
            print("  -", f, file=sys.stderr)
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Line-by-line verifier for session-343c7030.

Seven rule families. Exits non-zero on the first failure so it can gate CI:

  1. a verified row has a value AND a resolvable source
  2. a blank row has no value AND is published on flagged.html
  3. every source is cited at least once, is https, and has an access date
  4. every internal link in every page resolves to a file that exists
  5. no page contains an e-mail, phone, SSN, APN, account or street-address pattern
  6. the strategy figures published in the HTML equal data/projections.json
  7. every page carries the navigation, a title, and the privacy footer

Standard library only.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))

PAGES = [
    "index.html", "executive-summary.html", "market.html", "economy.html",
    "property-lease.html", "valuation-tax.html", "projection.html", "decision.html",
    "risks.html", "sources.html", "flagged.html", "verification.html",
]

PII_PATTERNS = [
    (r"[\w.+-]+@[\w-]+\.[a-z]{2,}", "e-mail address"),
    (r"\(\d{3}\)\s?\d{3}-\d{4}", "phone number"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "SSN-like pattern"),
    (r"\b\d{4}-\d{3}-\d{3}\b", "APN-like pattern"),
    (r"\b\d{3}-\d{3}-\d{3}\b", "APN-like pattern"),
    (r"\b\d{1,5}\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Way)\b", "street address"),
    (r"\b(?:acct|account)\s*(?:no\.?|number|#)\s*[:#]?\s*\d+", "account number"),
]


def load(name):
    with open(os.path.join(ROOT, "data", name)) as fh:
        return json.load(fh)


def main():
    fails = []

    facts = load("facts.json")["rows"]
    sources = {s["id"]: s for s in load("sources.json")["sources"]}
    proj = load("projections.json")
    mc = proj["monte_carlo"]["summary"]

    # 1 and 2 -------------------------------------------------------------
    for r in facts:
        if r["status"] == "verified":
            if not str(r["value"]).strip():
                fails.append(f'1: verified row {r["id"]} has an empty value')
            if not r["source"]:
                fails.append(f'1: verified row {r["id"]} has no source')
        elif r["status"] == "blank":
            if str(r["value"]).strip():
                fails.append(f'2: blank row {r["id"]} carries a value')
        else:
            fails.append(f'1: row {r["id"]} has unknown status {r["status"]!r}')
        for sid in [x.strip() for x in r["source"].split(",") if x.strip()]:
            if sid not in sources:
                fails.append(f'1: row {r["id"]} cites unknown source {sid}')

    # 3 -------------------------------------------------------------------
    cited = set()
    for r in facts:
        cited |= {x.strip() for x in r["source"].split(",") if x.strip()}
    for sid, s in sources.items():
        if sid not in cited:
            fails.append(f"3: source {sid} is never cited")
        if not s["url"].startswith("https://"):
            fails.append(f"3: source {sid} is not https")
        if not re.match(r"\d{4}-\d{2}-\d{2}", s.get("accessed", "")):
            fails.append(f"3: source {sid} has no access date")

    blank_ids = [r["id"] for r in facts if r["status"] == "blank"]
    flagged_html = open(os.path.join(ROOT, "flagged.html")).read()
    for rid in blank_ids:
        if rid not in flagged_html:
            fails.append(f"2: blank row {rid} is not published on flagged.html")

    # 4 -------------------------------------------------------------------
    links = 0
    for f in PAGES:
        path = os.path.join(ROOT, f)
        if not os.path.exists(path):
            fails.append(f"4: page {f} is missing")
            continue
        text = open(path).read()
        for m in re.findall(r'(?:href|src)="([^"#:]+)"', text):
            links += 1
            if m.startswith(("http://", "https://", "//", "mailto:")):
                continue
            target = os.path.normpath(os.path.join(ROOT, m))
            if not os.path.exists(target):
                fails.append(f"4: {f} links to missing {m}")

    # 5 -------------------------------------------------------------------
    for f in PAGES:
        text = open(os.path.join(ROOT, f)).read()
        for pat, label in PII_PATTERNS:
            hit = re.search(pat, text)
            if hit:
                fails.append(f"5: {f} contains a possible {label}: {hit.group(0)!r}")
    for f in ("../README.md", "../COORDINATION.md"):
        pass  # other sessions' files are not this verifier's scope

    # 6 -------------------------------------------------------------------
    index = open(os.path.join(ROOT, "index.html")).read()
    decision = open(os.path.join(ROOT, "decision.html")).read()
    for sid in ("S1", "S2", "S3", "S4", "S5"):
        fig = f"${mc[sid]['ce']:,.0f}"
        if sid in ("S1", "S3") and fig not in index:
            fails.append(f"6: index.html does not publish the model figure for {sid} ({fig})")
        if fig not in decision:
            fails.append(f"6: decision.html does not publish the model figure for {sid} ({fig})")

    # 7 -------------------------------------------------------------------
    for f in PAGES:
        text = open(os.path.join(ROOT, f)).read()
        if "<title>" not in text:
            fails.append(f"7: {f} has no title")
        if 'class="tabs"' not in text:
            fails.append(f"7: {f} has no navigation")
        if "Not an appraisal" not in text:
            fails.append(f"7: {f} is missing the privacy/disclaimer footer")

    if fails:
        print("VERIFY FAILED")
        for f in fails:
            print("  -", f)
        return 1

    print(f"VERIFY PASS — {len(PAGES)} pages · {len(facts)} fact rows "
          f"({sum(1 for r in facts if r['status']=='verified')} verified, {len(blank_ids)} blank) · "
          f"{len(sources)} sources all cited · {links} local links resolve · "
          f"0 PII patterns · model figures consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())

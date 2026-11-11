#!/usr/bin/env python3
"""Session N4 independent verifier.

Re-checks the published workbook without trusting the build script:
  V1 schema + blank/verified rules on data/*.json
  V2 every source exists, is https, and was read on the access date
  V3 all 12 pages present; every internal link resolves; nav reaches all pages
  V4 every metric row appears in data.html with a source link or blank badge
  V5 PII scan (email, phone, SSN, street address) over pages AND data files
  V6 model reproducibility: scripts/model.py regenerates model_output.json
  V7 counts quoted on verification.html match the data files

Usage: python3 scripts/verify.py   (exit 0 = PASS)
"""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = os.path.dirname(ROOT)
ACCESS = "2026-11-11"

PAGES = ["index.html", "executive-summary.html", "questions.html", "decision.html",
         "projection.html", "risks.html", "data.html", "reconciliation.html",
         "sources.html", "verification.html", "flagged.html", "privacy.html"]

PII = [
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "email"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "ssn"),
    (re.compile(r"(?<![\d-])(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}(?![\d-])"), "phone"),
    (re.compile(r"\b\d{1,5}\s+[A-Z][a-z]+\s+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Way|Lane|Ln)\b"), "street-address"),
]

errors = []
checks = []


def ok(name, detail=""):
    checks.append((name, detail))


def fail(name, detail):
    errors.append(f"{name}: {detail}")


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def v1_v2_data_layer():
    sources = load("sources.json")
    metrics = load("metrics.json")
    questions = load("questions.json")
    risks = load("risks.json")
    decisions = load("decisions.json")
    recon = load("reconciliation.json")
    flags = load("irregularities.json")
    s_ids = {s["id"] for s in sources["sources"]}

    v = b = 0
    for r in metrics["rows"]:
        if r["status"] == "verified":
            v += 1
            if not r["value"]:
                fail("V1", f"{r['id']} verified with empty value")
            if r["source"] not in s_ids:
                fail("V1", f"{r['id']} unknown source {r['source']!r}")
        elif r["status"] == "blank":
            b += 1
            if r["value"]:
                fail("V1", f"{r['id']} blank but carries a value")
        else:
            fail("V1", f"{r['id']} bad status {r['status']!r}")
    for s in sources["sources"]:
        if not s["url"].startswith("https://"):
            fail("V2", f"{s['id']} not https")
        if s["read_on"] != ACCESS:
            fail("V2", f"{s['id']} read_on {s['read_on']}")
    for q in questions["questions"]:
        if q["status"] == "answered" and not q["answer"]:
            fail("V1", f"{q['id']} answered without answer")
        if q["status"] != "answered" and q["answer"]:
            fail("V1", f"{q['id']} open but carries an answer")
    for r in risks["risks"]:
        if not r["affects"]:
            fail("V1", f"{r['id']} affects nothing")
        if r["source"] and r["source"] not in s_ids:
            fail("V1", f"{r['id']} unknown source {r['source']}")
    for row in recon["rows"]:
        if not row["url"] or not row["recommendation"]:
            fail("V1", f"reconciliation row incomplete: {row.get('workbook')}")
    for it in flags["items"]:
        if it["severity"] not in ("high", "medium", "low"):
            fail("V1", f"{it['id']} bad severity")
    ok("V1 data layer", f"{v} verified / {b} blank metrics; "
                        f"{len(questions['questions'])} questions; {len(risks['risks'])} risks; "
                        f"{len(flags['items'])} flags")
    ok("V2 sources", f"{len(sources['sources'])} https sources, all read {ACCESS}")
    return sources, metrics, questions, risks, decisions, recon, flags, s_ids


def v3_v4_pages(s_by_id, metrics):
    contents = {}
    for p in PAGES:
        path = os.path.join(ROOT, p)
        if not os.path.exists(path):
            fail("V3", f"missing page {p}")
            continue
        with open(path, encoding="utf-8") as f:
            contents[p] = f.read()
    # internal links
    n_links = 0
    for p, txt in contents.items():
        for href in re.findall(r'href="([^"]+)"', txt):
            if href.startswith(("http", "#")):
                continue
            n_links += 1
            target = href.split("#")[0]
            if target.startswith("../"):
                if not os.path.exists(os.path.join(REPO, target[3:])):
                    fail("V3", f"{p} -> broken {target}")
            elif target.endswith(".html"):
                if target not in contents:
                    fail("V3", f"{p} -> broken {target}")
            elif not os.path.exists(os.path.join(ROOT, target)):
                fail("V3", f"{p} -> missing asset {target}")
    # nav reachability: index must link every page
    idx = contents.get("index.html", "")
    for p in PAGES:
        if p != "index.html" and f'href="{p}"' not in idx:
            fail("V3", f"index.html does not link {p}")
    # every metric row present in data.html with source or blank badge
    data = contents.get("data.html", "")
    n_ok = 0
    for r in metrics["rows"]:
        if f"<td>{r['id']}</td>" not in data:
            fail("V4", f"{r['id']} missing from data.html")
            continue
        if r["status"] == "verified":
            sid = r["source"]
            if f">{sid} " not in data and f">{sid}</a>" not in data:
                # link rendered as "Sxx ↗"
                if f"{sid} &#8599;" not in data:
                    fail("V4", f"{r['id']} has no visible source link in data.html")
        else:
            if "(blank)" not in data:
                fail("V4", "blank badge missing")
        n_ok += 1
    ok("V3 pages/links", f"{len(contents)} pages, {n_links} internal links, nav complete")
    ok("V4 row coverage", f"{n_ok}/{len(metrics['rows'])} metric rows rendered with source/blank")


def v5_pii():
    hits = 0
    scanned = 0
    for p in PAGES:
        path = os.path.join(ROOT, p)
        if not os.path.exists(path):
            continue
        txt = open(path, encoding="utf-8").read()
        scanned += 1
        for rx, label in PII:
            m = rx.search(txt)
            if m:
                fail("V5", f"PII {label} in {p}: {m.group(0)[:40]!r}")
                hits += 1
    for name in ("sources.json", "metrics.json", "questions.json", "risks.json",
                 "decisions.json", "reconciliation.json", "irregularities.json",
                 "model_output.json"):
        txt = open(os.path.join(ROOT, "data", name), encoding="utf-8").read()
        scanned += 1
        for rx, label in PII:
            m = rx.search(txt)
            if m:
                fail("V5", f"PII {label} in data/{name}: {m.group(0)[:40]!r}")
                hits += 1
    ok("V5 PII scan", f"{scanned} files scanned, {hits} hits")


def v6_model():
    target = os.path.join(ROOT, "data", "model_output.json")
    before = open(target, encoding="utf-8").read()
    with tempfile.TemporaryDirectory() as td:
        # run model in a copy of the session dir to avoid touching the real file
        import shutil
        dest = os.path.join(td, "session-3090b9ed")
        shutil.copytree(ROOT, dest)
        env = dict(os.environ)
        r = subprocess.run([sys.executable, os.path.join(dest, "scripts", "model.py")],
                           capture_output=True, text=True, env=env, cwd=td)
        if r.returncode != 0:
            fail("V6", f"model.py failed: {r.stderr[-300:]}")
            return
        after = open(os.path.join(dest, "data", "model_output.json"), encoding="utf-8").read()
    if before != after:
        fail("V6", "model_output.json not reproducible from scripts/model.py")
    else:
        mc = json.loads(before)["monte_carlo"]
        ok("V6 model", f"deterministic regeneration identical (seed {mc['seed']}, {mc['trials']} trials)")


def v7_counts(sources, metrics, questions, risks, flags, decisions):
    txt = open(os.path.join(ROOT, "verification.html"), encoding="utf-8").read()
    v = sum(1 for r in metrics["rows"] if r["status"] == "verified")
    b = sum(1 for r in metrics["rows"] if r["status"] == "blank")
    must = [str(len(sources["sources"])), str(v), str(b),
            str(len(risks["risks"])), str(len(questions["questions"]))]
    for m in must:
        if m not in txt:
            fail("V7", f"verification.html missing count {m}")
    # decision options exist for every strategy named in the model
    strat = json.load(open(os.path.join(ROOT, "data", "model_output.json")))["monte_carlo"]["strategy_stats"]
    names = {o["name"] for o in decisions["options"]}
    if set(strat) != names:
        fail("V7", f"decision options {names} != model strategies {set(strat)}")
    ok("V7 counts", f"verification.html counts match; {len(decisions['options'])} options == {len(strat)} strategies")


def main():
    sources, metrics, questions, risks, decisions, recon, flags, s_ids = v1_v2_data_layer()
    v3_v4_pages(s_ids, metrics)
    v5_pii()
    v6_model()
    v7_counts(sources, metrics, questions, risks, flags, decisions)

    print("=" * 70)
    for name, detail in checks:
        print(f"  PASS  {name:24s} {detail}")
    if errors:
        print("-" * 70)
        for e in errors:
            print(f"  FAIL  {e}")
        print(f"RESULT: FAIL ({len(errors)} errors)")
        sys.exit(1)
    print("RESULT: PASS (0 errors)")


if __name__ == "__main__":
    main()

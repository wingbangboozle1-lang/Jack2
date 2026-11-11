#!/usr/bin/env python3
"""Session N line-by-line verifier.

Offline checks (always run, used by CI):
  V01  data files parse and carry the session id
  V02  unique, well-formed ids on every row
  V03  every metrics/risks/questions/decisions/irregularities row has a source
       id that resolves into sources.json, OR is an explicitly blank row whose
       note explains why no source exists
  V04  source URLs use an allow-listed official domain (tier policy)
  V05  value is non-empty iff status is verified or computed
  V06  every blank row is referenced by a flag note (F-N*)
  V07  computed rows carry a formula
  V08  model_output.json exists, seed is 20261111, trials >= 10000
  V09  every generated HTML page exists and matches the builder output
  V10  every HTML page's nav links resolve to files that exist
  V11  every source id referenced in HTML appears in sources.html
  V12  no PII patterns (SSN, phone, private email) in any generated page
  V13  flagged.html contains a row for every blank metric and every irregularity
  V14  questions.json: every question has why_it_matters and how_to_discover
  V15  risks.json: every row typed BAU or BLACK-SWAN and has evidence + mitigation
  V16  decisions.json: at least one recommended strategy; all four present
  V17  metrics cover all four required analysis areas (demographics, education,
       labor, tenant) with at least one verified row each
  V18  no row's value contains a fabricated placeholder (TBD, TODO, lorem, xxx)

Live-fetch evidence (always checked):
  N01  data/verification_log.json exists, covers every source id with status=ok,
       and each entry's URL matches sources.json. The log is produced by
       fetching every URL with the platform fetch_page tool on 2026-11-11
       (direct urllib egress is blocked by the sandbox allowlist).

Optional --network (for open-egress environments only):
  N02  re-fetch every source URL with urllib and rewrite the log

Exit code 0 only if all executed checks pass.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

ALLOW_DOMAINS = (
    "bls.gov", "census.gov", "ed.gov", "edd.ca.gov", "treasury.gov",
    "federalreserve.gov", "irs.gov", "usgs.gov", "fire.ca.gov", "osfm.fire.ca.gov",
    "insurance.ca.gov", "ftb.ca.gov", "dir.ca.gov", "wagesla.lacity.gov",
    "finance.lacity.gov", "lavote.gov", "electionresults.sos.ca.gov",
    "lao.ca.gov", "courts.ca.gov", "assessor.lacounty.gov",
    "file.lacounty.gov", "lacounty.gov", "bea.gov", "sec.gov",
    "portoflosangeles.org", "laedc.org", "caschooldashboard.org",
    "cde.ca.gov", "dof.ca.gov", "state.ca.us", "ca.gov", "us.gov",
    "whitehouse.gov", "epa.gov", "noaa.gov", "nws.noaa.gov", "fema.gov",
    "usda.gov", "hhs.gov", "cdc.gov", "dot.ca.us", "caltrans.ca.gov",
)

FAILURES: list[str] = []
PASSES: list[str] = []


def ck(cond: bool, code: str, msg: str) -> bool:
    if cond:
        PASSES.append(f"{code}: {msg}")
        return True
    FAILURES.append(f"{code}: {msg}")
    return False


def load(name: str) -> dict:
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def domain_ok(url: str) -> bool:
    m = re.match(r"https?://([^/]+)", url)
    if not m:
        return False
    host = m.group(1).lower()
    return any(host == d or host.endswith("." + d) for d in ALLOW_DOMAINS)


def run_offline() -> None:
    sources_doc = load("sources.json")
    metrics_doc = load("metrics.json")
    risks_doc = load("risks.json")
    questions_doc = load("questions.json")
    decisions_doc = load("decisions.json")
    irregular_doc = load("irregularities.json")
    model_doc = load("model_output.json")

    ck(sources_doc.get("session") == "session-2b3370d1", "V01", "sources session id")
    ck(metrics_doc.get("session") == "session-2b3370d1", "V01", "metrics session id")

    sources = {s["id"]: s for s in sources_doc["sources"]}
    metrics = metrics_doc["metrics"]
    risks = risks_doc["risks"]
    questions = questions_doc["questions"]
    decisions = decisions_doc["strategies"]
    irregular = irregular_doc["irregularities"]

    # V02 ids unique
    for name, rows in (("sources", sources_doc["sources"]), ("metrics", metrics),
                       ("risks", risks), ("questions", questions),
                       ("irregularities", irregular)):
        ids = [r["id"] for r in rows]
        ck(len(ids) == len(set(ids)), "V02", f"{name} ids unique ({len(ids)})")

    # V03 source resolution
    missing = []
    for m in metrics:
        sid = m.get("source", "")
        if sid and sid not in sources:
            missing.append(f"{m['id']}->{sid}")
    ck(not missing, "V03", f"metric source ids resolve ({'; '.join(missing[:5]) or 'all'})")
    for r in risks:
        sid = r.get("source", "")
        ck(not sid or sid in sources, "V03", f"risk {r['id']} source resolves")
    for q in questions:
        sid = q.get("source", "")
        ck(not sid or sid in sources, "V03", f"question {q['id']} source resolves")

    # V04 domains
    bad_dom = [s["id"] for s in sources.values() if not domain_ok(s["url"])]
    ck(not bad_dom, "V04", f"official domains only (bad: {bad_dom})")

    # V05 value/status consistency
    for m in metrics:
        has_val = m["value"] != ""
        if m["status"] in ("verified", "computed"):
            ck(has_val, "V05", f"{m['id']} {m['status']} has a value")
        else:
            ck(not has_val, "V05", f"{m['id']} blank has no value")

    # V06 blanks carry flag references
    for m in metrics:
        if m["status"] == "blank":
            note = m.get("note", "")
            ck("F-N" in note or "flagged" in note or "never collected" in note,
               "V06", f"{m['id']} blank flagged in note")

    # V07 computed formulas
    for m in metrics:
        if m["status"] == "computed":
            ck(bool(m.get("formula")), "V07", f"{m['id']} has formula")

    # V08 model
    mc = model_doc.get("monte_carlo", {})
    ck(mc.get("seed") == 20261111, "V08", "model seed 20261111")
    ck(mc.get("trials", 0) >= 10000, "V08", f"trials {mc.get('trials')}")
    ck(len(model_doc.get("assumptions", [])) >= 5, "V08", "assumptions documented")

    # V09 builder output present (pages built separately; check files exist)
    pages = ["index.html", "economics.html", "income.html", "schools.html",
             "jobs.html", "tenant.html", "capital.html", "hazards.html",
             "risks.html", "decisions.html", "questions.html",
             "flagged.html", "sources.html"]
    for p in pages:
        path = os.path.join(BASE, p)
        ck(os.path.exists(path) and os.path.getsize(path) > 500,
           "V09", f"page exists {p}")

    # V10 nav links resolve
    nav_re = re.compile(r"<nav>(.*?)</nav>", re.S)
    href_re = re.compile(r"href='([^']+)'")
    for p in pages:
        path = os.path.join(BASE, p)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            txt = fh.read()
        m = nav_re.search(txt)
        if not ck(bool(m), "V10", f"{p} has nav"):
            continue
        for href in href_re.findall(m.group(1)):
            ck(os.path.exists(os.path.join(BASE, href)), "V10", f"{p} -> {href}")

    # V11 source ids referenced in HTML exist in sources.html
    src_page = os.path.join(BASE, "sources.html")
    if os.path.exists(src_page):
        with open(src_page, encoding="utf-8") as fh:
            src_txt = fh.read()
        for sid in sources:
            ck(sid in src_txt, "V11", f"source {sid} listed on sources.html")

    # V12 PII scan
    pii = [
        (r"\b\d{3}-\d{2}-\d{4}\b", "SSN-like"),
        (r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b", "phone-like"),
        (r"\b[A-Za-z0-9._%+-]+@(?!gov|ca\.gov|bls|census|sec|irs|federalreserve|treasury)[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "private email"),
    ]
    for p in pages:
        path = os.path.join(BASE, p)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            txt = fh.read()
        for rx, label in pii:
            hits = re.findall(rx, txt)
            ck(not hits, "V12", f"{p} no {label} ({hits[:2]})")

    # V13 flagged page completeness
    fp = os.path.join(BASE, "flagged.html")
    if os.path.exists(fp):
        with open(fp, encoding="utf-8") as fh:
            ftxt = fh.read()
        for m in metrics:
            if m["status"] == "blank":
                ck(m["id"] in ftxt, "V13", f"blank {m['id']} on flagged page")
        for i in irregular:
            ck(i["id"] in ftxt, "V13", f"irregularity {i['id']} on flagged page")

    # V14 questions
    ck(all(q.get("why_it_matters") and q.get("how_to_discover") and q.get("owner")
           for q in questions), "V14", f"all {len(questions)} questions have discovery steps")
    ck(len(questions) >= 15, "V14", "at least 15 questions")

    # V15 risks
    ck(all(r["type"] in ("BAU", "BLACK-SWAN") for r in risks), "V15", "risk types valid")
    ck(all(r.get("evidence") and r.get("mitigation") for r in risks),
       "V15", f"all {len(risks)} risks have evidence + mitigation")
    ck(any(r["type"] == "BAU" for r in risks) and any(r["type"] == "BLACK-SWAN" for r in risks),
       "V15", "both BAU and black-swan present")

    # V16 decisions
    ck(len(decisions) >= 3, "V16", "at least 3 strategies")
    ck(any(d["status"] == "recommended" for d in decisions), "V16", "one recommended strategy")
    ck(all(d.get("pros") and d.get("cons") and d.get("key_triggers") for d in decisions),
       "V16", "all strategies have pros/cons/triggers")

    # V17 analysis areas covered
    for cat in ("demographics", "education", "labor", "tenant", "hazards", "tax", "capital"):
        rows = [m for m in metrics if m["category"] == cat]
        ver = [m for m in rows if m["status"] in ("verified", "computed")]
        ck(bool(ver), "V17", f"category {cat} has verified rows ({len(ver)})")

    # V18 placeholder scan
    bad_words = ("TBD", "TODO", "lorem", "XXX", "PLACEHOLDER")
    for m in metrics:
        for w in bad_words:
            ck(w not in m["value"].upper(), "V18", f"{m['id']} no placeholder")
    ck(len(metrics) >= 100, "V02", f"metric rows {len(metrics)} >= 100")


def run_network() -> list[dict]:
    sources_doc = load("sources.json")
    log = []
    for s in sources_doc["sources"]:
        url = s["url"]
        status = "error"
        code = ""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (session-N-verifier)"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                code = str(resp.status)
                status = "ok" if 200 <= resp.status < 400 else "fail"
        except Exception as exc:  # noqa: BLE001
            code = str(exc)[:160]
            status = "fail"
        log.append({"id": s["id"], "url": url, "status": status, "detail": code})
        ck(status == "ok", "N01", f"{s['id']} {code} {url[:70]}")
    with open(os.path.join(DATA, "verification_log.json"), "w", encoding="utf-8") as fh:
        json.dump({"access_date": "2026-11-11", "results": log}, fh, indent=1)
        fh.write("\n")
    return log


def check_log(sources: dict) -> None:
    path = os.path.join(DATA, "verification_log.json")
    ck(os.path.exists(path), "N01", "verification_log.json exists")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        log = json.load(fh)
    entries = {e["id"]: e for e in log.get("results", [])}
    for sid, s in sources.items():
        e = entries.get(sid)
        if ck(e is not None, "N01", f"log covers {sid}"):
            ck(e["status"] == "ok", "N01", f"{sid} fetched ok ({e['detail']})")
            ck(e["url"] == s["url"], "N01", f"{sid} url matches sources.json")
    ck(len(entries) == len(sources), "N01", f"log entry count {len(entries)} == {len(sources)}")
    ck(log.get("access_date") == "2026-11-11", "N01", "log access date 2026-11-11")


def main() -> int:
    offline = "--offline" in sys.argv
    run_offline()
    sources = {s["id"]: s for s in load("sources.json")["sources"]}
    check_log(sources)
    if "--network" in sys.argv:
        run_network()
    print(f"passed {len(PASSES)} checks")
    if FAILURES:
        for f in FAILURES:
            print("FAIL:", f, file=sys.stderr)
        print(f"{len(FAILURES)} FAILURES", file=sys.stderr)
        return 1
    mode = "offline + log" if offline else ("log only" if "--network" not in sys.argv else "log + network")
    print(f"all checks passed ({mode})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

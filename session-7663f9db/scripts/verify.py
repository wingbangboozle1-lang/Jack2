#!/usr/bin/env python3
"""
Session P (session-7663f9db) Comprehensive Self-Verification Suite (V1-V7).
Exits non-zero if any check fails.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXPECTED_PAGES = [
    "index.html",
    "demographics.html",
    "economy.html",
    "schools.html",
    "market.html",
    "taxes.html",
    "hazards.html",
    "projections.html",
    "risks.html",
    "questions.html",
    "decisions.html",
    "suggestions.html",
    "flagged.html",
    "requirements.html",
    "sources.html",
]

EXPECTED_JSON = [
    "sources.json",
    "metrics.json",
    "irregularities.json",
    "questions.json",
    "risks.json",
    "decisions.json",
    "suggestions.json",
    "requirements.json",
    "model_output.json",
]

BROKEN_URL_SUBSTRINGS = [
    "fire-hazard-severity-zones-maps-2022",
    "lacountycalifornia",
    "losangelesNICITYcalifornia",
    "/AB1253",
]

PII_PATTERNS = {
    "street_address": re.compile(
        r"\b\d{1,5}\s+(?:[NSWE]\.?\s+)?(?:South|North|East|West\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\s+(?:Ave|Avenue|St|Street|Blvd|Boulevard|Rd|Road|Dr|Drive|Ln|Lane|Way|Pkwy|Parkway)\b"
    ),
    "apn_parcel": re.compile(r"\b\d{4}-\d{3}-\d{3}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "phone": re.compile(r"\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
}


def load_json(name: str) -> dict:
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []

    # V1: Required files
    for p in EXPECTED_PAGES:
        if not (ROOT / p).is_file():
            errors.append(f"V1 missing HTML page: {p}")
    for j in EXPECTED_JSON:
        p = ROOT / "data" / j
        if not p.is_file():
            errors.append(f"V1 missing JSON: data/{j}")
        else:
            try:
                json.loads(p.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"V1 invalid JSON data/{j}: {exc}")
    for rel in ["PRIVACY_POLICY.md", "EXECUTIVE_SUMMARY.md", "assets/style.css", "assets/app.js", "scripts/model.py", "scripts/build_site.py"]:
        if not (ROOT / rel).is_file():
            errors.append(f"V1 missing artifact: {rel}")

    if errors:
        for err in errors:
            print("FAIL:", err)
        return 1

    # V2: Sources integrity
    sources = load_json("sources.json")["sources"]
    src_ids = {s["id"] for s in sources}
    for s in sources:
        if not s.get("verified"):
            errors.append(f"V2 unverified source: {s['id']}")
        if s.get("read_on") != "2026-11-12":
            errors.append(f"V2 stale read_on on {s['id']}: {s.get('read_on')}")
        url = s.get("url", "")
        if not url.startswith("https://"):
            errors.append(f"V2 non-HTTPS url on {s['id']}: {url}")
        for bad in BROKEN_URL_SUBSTRINGS:
            if bad in url:
                errors.append(f"V2 legacy broken URL pattern {bad} on {s['id']}")

    # V3: Blank-vs-Verified discipline across metrics, questions, risks, irregularities
    metrics = load_json("metrics.json")["rows"]
    blank_count = 0
    verified_count = 0
    for m in metrics:
        st = m.get("status")
        val = m.get("value", "")
        src = m.get("source", "")
        if st == "verified":
            verified_count += 1
            if not val:
                errors.append(f"V3 verified metric has empty value: {m['id']}")
            if src not in src_ids:
                errors.append(f"V3 verified metric {m['id']} cites missing source '{src}'")
        elif st == "blank":
            blank_count += 1
            if val != "" or src != "":
                errors.append(f"V3 blank metric {m['id']} must have empty value & source")
        else:
            errors.append(f"V3 unknown metric status on {m['id']}: {st}")

    for q in load_json("questions.json")["questions"]:
        src = q.get("source", "")
        if src and src not in src_ids:
            errors.append(f"V3 question {q['id']} cites invalid source '{src}'")
        if q["status"] == "known-verified" and not q.get("answer"):
            errors.append(f"V3 known-verified question {q['id']} missing answer")
        if q["status"] != "known-verified" and q.get("answer"):
            errors.append(f"V3 non-verified question {q['id']} should leave answer blank")

    for rk in load_json("risks.json")["risks"]:
        src = rk.get("source", "")
        if src and src not in src_ids:
            errors.append(f"V3 risk {rk['id']} cites invalid source '{src}'")

    # V4: Zero PII across all workspace files
    for fpath in sorted(ROOT.rglob("*")):
        if not fpath.is_file():
            continue
        if fpath.suffix.lower() not in {".html", ".json", ".md", ".py", ".js", ".css"}:
            continue
        txt = fpath.read_text(encoding="utf-8")
        # Strip valid external URLs before checking patterns like emails/paths
        for pname, pat in PII_PATTERNS.items():
            for match in pat.finditer(txt):
                snippet = match.group(0)
                errors.append(f"V4 PII regex ({pname}) matched '{snippet}' in {fpath.relative_to(ROOT)}")

    # V5: HTML link, fragment, nav & dependency checks
    href_re = re.compile(r'(?:href|src)="([^"]+)"')
    for page in EXPECTED_PAGES:
        txt = (ROOT / page).read_text(encoding="utf-8")
        if "<!DOCTYPE html>" not in txt:
            errors.append(f"V5 {page} missing DOCTYPE")
        for target_page in EXPECTED_PAGES:
            if f'href="{target_page}"' not in txt:
                errors.append(f"V5 {page} missing nav link to {target_page}")
        if "http://" in txt:
            errors.append(f"V5 insecure http:// found in {page}")
        for m in href_re.finditer(txt):
            target = m.group(1)
            if target.startswith("https://"):
                continue
            if target.startswith("../"):
                # Allow ../favicon.svg pointing to repo root favicon.svg
                rel_up = (ROOT.parent / target[3:])
                if not rel_up.exists():
                    errors.append(f"V5 broken parent link {target} in {page}")
                continue
            path_part, _, frag = target.partition("#")
            if path_part:
                if not (ROOT / path_part).exists():
                    errors.append(f"V5 broken local href {target} in {page}")
                elif path_part == "sources.html" and frag:
                    if frag not in src_ids:
                        errors.append(f"V5 broken source anchor #{frag} in {page}")

    # V6: Deterministic model check & numbers reconciliation
    pre_model = (ROOT / "data" / "model_output.json").read_text(encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "model.py")], check=True, stdout=subprocess.DEVNULL)
    post_model = (ROOT / "data" / "model_output.json").read_text(encoding="utf-8")
    if pre_model != post_model:
        errors.append("V6 model.py output is non-deterministic!")

    model = json.loads(post_model)
    if model["meta"]["seed"] != 20261112 or model["meta"]["trials_per_regime"] != 15000:
        errors.append("V6 unexpected model seed or trial count")

    idx_html = (ROOT / "index.html").read_text(encoding="utf-8")
    for token in ["4.98%", "6.80%", "2,115", "87.6%", "+3.7%", "4.8%"]:
        if token not in idx_html:
            errors.append(f"V6 index.html missing verified live KPI token: {token}")

    proj_html = (ROOT / "projections.html").read_text(encoding="utf-8")
    for token in ['id="owner-calc"', "6.59%", "6.32%", "8.06%", "7.27%"]:
        if token not in proj_html:
            errors.append(f"V6 projections.html missing expected model token: {token}")

    # V7: JS interactive DOM IDs match HTML
    sug_html = (ROOT / "suggestions.html").read_text(encoding="utf-8")
    for dom_id in ["ps-walt", "ps-ula", "ps-sales", "ps-gain", "ps-cap", "ps-tod", "path-selector"]:
        if f'id="{dom_id}"' not in sug_html:
            errors.append(f"V7 suggestions.html missing DOM id={dom_id}")
    for calc_id in ["calc-noi", "calc-cap", "calc-yrs", "calc-ula", "calc-gain", "calc-debt", "calc-esc", "calc-rep",
                    "out-gross", "out-dtt", "out-equity", "out-hold-npv", "out-1031-npv", "out-be-npv", "out-tax-npv"]:
        if f'id="{calc_id}"' not in proj_html:
            errors.append(f"V7 projections.html missing DOM id={calc_id}")

    if errors:
        print(f"VERIFICATION FAILED ({len(errors)} error(s)):")
        for err in errors:
            print(" -", err)
        return 1

    print(
        f"PASS: All V1-V7 checks clean! ({len(EXPECTED_PAGES)} HTML pages, {len(sources)} HTTPS sources, "
        f"{verified_count} verified metrics + {blank_count} strictly blank fields, 0 PII hits, deterministic 15k MC)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

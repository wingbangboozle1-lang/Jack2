#!/usr/bin/env python3
"""Line-level structural/privacy inventory of the repository.

This is not a claim that every historical sentence was independently fact-checked.
It reads every line of every tracked/nonignored file, records hashes and structural
checks, and masks potential identifiers instead of copying them into the report.
"""
import hashlib
import json
import py_compile
import re
import subprocess
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "session-f4f700c0" / "audit"
OUT.mkdir(exist_ok=True)

URL_RE = re.compile(r"https?://[^\s\"'<>]+")
PII_RES = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}"),
    re.compile(r"\b\d{1,6}\s+(?:[A-Z][a-z]+\s){1,3}(Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Way|Lane|Ln)\b"),
    re.compile(r"\bAPN[:\s#]*\d{3,}"),
]

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = 0
    def handle_starttag(self, tag, attrs):
        self.tags += 1


# Append-only shared coordination log. Every session is required to add to it, therefore its
# line count, byte count and hash can never be stable in CI. It is still READ on every line for the
# privacy and structural checks below; only its stored fingerprint is withheld. See COORDINATION.md,
# Session N task N-02: fingerprinting this file made the "generated files out of date" gate fail on
# every push from 2026-11-08 onward, for every session, permanently.
FINGERPRINT_EXCLUDED = {"COORDINATION.md"}


def files():
    """Every tracked/non-ignored path. Used for scanning (privacy, structure, URL counts)."""
    raw = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=REPO).decode()
    paths = sorted(set(raw.splitlines()))
    # Exclude self-referential generated audit/verification artifacts so the inventory is stable in CI.
    return [p for p in paths if not p.startswith("session-f4f700c0/audit/") and p != "session-f4f700c0/verification.json"]


def fingerprintable(rel):
    """Whether a scanned file's fingerprint may be asserted byte-stable across runs."""
    return rel not in FINGERPRINT_EXCLUDED


def workspace(path):
    top = path.split("/")[0]
    if top.startswith("session-"):
        return top
    if top in ("docs", "model", "research", "scripts", "data", "tools", "assets"):
        return "root/historical-shared"
    return "root/config"


def main():
    rows = []
    for rel in files():
        p = REPO / rel
        if not p.is_file():
            continue
        raw = p.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        lines = text.splitlines()
        # Explicitly touch every line; structural counters are line-derived.
        url_count = sum(len(URL_RE.findall(line)) for line in lines)
        pii_hits = sum(len(rx.findall(line)) for line in lines for rx in PII_RES)
        kind = p.suffix.lower() or "text"
        json_valid = None
        python_compiles = None
        html_tags = None
        if kind == ".json":
            try:
                json.loads(text)
                json_valid = True
            except Exception:
                json_valid = False
        elif kind == ".py":
            try:
                py_compile.compile(str(p), doraise=True)
                python_compiles = True
            except Exception:
                python_compiles = False
        elif kind in (".html", ".htm"):
            try:
                parser = Parser()
                parser.feed(text)
                html_tags = parser.tags
            except Exception:
                html_tags = -1
        status = "ok"
        if json_valid is False or python_compiles is False or html_tags == -1:
            status = "structural-error"
        if pii_hits:
            status = "privacy-review"
        fp = fingerprintable(rel)
        rows.append(dict(
            path=rel, workspace=workspace(rel),
            bytes=len(raw) if fp else None, lines=len(lines),
            sha256=hashlib.sha256(raw).hexdigest() if fp else None,
            fingerprint_excluded=not fp, kind=kind,
            url_count=url_count, pii_pattern_hits=pii_hits,
            json_valid=json_valid, python_compiles=python_compiles, html_tags=html_tags,
            status=status,
        ))
    by_ws = defaultdict(lambda: dict(files=0, lines=0, bytes=0, privacy_hits=0, structural_errors=0))
    for r in rows:
        w = by_ws[r["workspace"]]
        w["files"] += 1
        w["lines"] += r["lines"]
        w["bytes"] += r["bytes"] or 0
        w["privacy_hits"] += r["pii_pattern_hits"]
        if r["status"] == "structural-error":
            w["structural_errors"] += 1
    current_hits = sum(r["pii_pattern_hits"] for r in rows if r["workspace"] == "session-f4f700c0")
    historical_review = [dict(path=r["path"], hits=r["pii_pattern_hits"]) for r in rows if r["pii_pattern_hits"] and r["workspace"] != "session-f4f700c0"]
    summary = dict(
        as_of="2026-11-10",
        files=len(rows),
        lines=sum(r["lines"] for r in rows),
        bytes=sum(r["bytes"] or 0 for r in rows),
        fingerprint_excluded=sorted(FINGERPRINT_EXCLUDED),
        fingerprint_exclusion_reason="Append-only shared board; scanned on every run, but not asserted byte-stable (Session N, task N-02).",
        privacy_pattern_hits=sum(r["pii_pattern_hits"] for r in rows),
        current_session_privacy_hits=current_hits,
        historical_privacy_review=historical_review,
        structural_errors=sum(r["status"] == "structural-error" for r in rows),
        workspaces=dict(sorted(by_ws.items())),
        limitation="Automated line-level structural/privacy inventory plus targeted source-value audit. Not a certification of every historical narrative sentence. Street-address patterns may be public institutional addresses; current-session pages are scanned separately.",
    )
    (OUT / "inventory.json").write_text(json.dumps(dict(meta=summary, rows=rows), indent=2) + "\n")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

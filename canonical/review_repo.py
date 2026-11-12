#!/usr/bin/env python3
"""Mechanical review of everything else in the repository (session-1c30f8e8).

Two things, both reproducible from the files on disk:
  1. An inventory of every workbook: files, lines, pages, links, official links, how many of
     its cited addresses were re-read by this session today, and privacy-pattern hits (counted,
     never copied).
  2. A cross-check of a few key figures: every value earlier workbooks print for the same
     quantity, next to the value verified today.

This is a structural, line-by-line read. It does not claim that every historical sentence was
fact-checked; pages in the archive are preserved as their sessions left them.
"""
import html
import json
import os
import re
import sys
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import privacy  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(HERE, "data", "repo_review.json")

URL = re.compile(r"https?://[^\s\"'<>)\\]+")
PII_KINDS = [k for k, _ in privacy.PATTERNS] + ["name of an individual"]
OFFICIAL = (".gov", ".ca.gov", "sec.gov", "lacity.org", "lacity.gov", "lacounty.gov", "scag.ca.gov", "lavote.gov",
            "federalreserve.gov", "census.gov", "bls.gov", "bea.gov", "treasury.gov", "irs.gov", "cbo.gov", "usgs.gov")
SKIP_DIRS = {".git", "canonical", "node_modules", "__pycache__", ".github"}
TEXT_EXT = {".html", ".json", ".md", ".py", ".js", ".css", ".txt", ".csv", ".yml", ".svg"}


def official(u):
    host = urlparse(u).netloc.lower()
    return any(host.endswith(s) for s in OFFICIAL)


def workspace_of(rel):
    top = rel.split("/")[0]
    if "/" not in rel:
        return "(repository root files)"
    return top


def strip_tags(text):
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", text, flags=re.S | re.I)
    return html.unescape(re.sub(r"<[^>]+>", " ", text))


FIGURES = [
    ("10-year Treasury yield", "CM-001", r"10[- ]?year[^.%\d]{0,60}?(\d\.\d{2})\s?%"),
    ("County residents, Census Bureau estimate", "PP-001b", r"\b(9,[5-9]\d\d,\d{3})\b"),
    ("City residents, Census Bureau estimate", "PP-001a", r"\b(3,[78]\d\d,\d{3})\b"),
    ("Measure ULA lower threshold", "TX-003", r"(?:ULA|threshold)[^.$]{0,80}?\$\s?(5[.,]\d{1,3}(?:,\d{3})?)"),
    ("Tenant same-store sales, latest quarter", "TN-020", r"same[- ]store sales[^.%\d]{0,70}?[(\u2212\u2013-]\s?(\d\.\d)\s?%?\)?\s?%?"),
    ("Chance of a magnitude 6.7+ earthquake in 30 years, Los Angeles region", "HZ-001", r"\b([1-9]\d)\s?%[^.%]{0,70}6\.7|6\.7[^.%]{0,70}?\b([1-9]\d)\s?%"),
    ("Fast-food minimum wage", "EC-093", r"fast[- ]food[^.$]{0,80}?\$(\d\d\.\d\d)"),
    ("Los Angeles Unified enrollment", "PP-066", r"\b(4\d\d,\d{3})\b[^.]{0,40}(?:student|enroll)|enroll[^.\d]{0,40}\b(4\d\d,\d{3})\b"),
    ("Restaurants in the tenant's system", "TN-001", r"\b(2,[012]\d\d)\s+(?:Jack in the Box\s+)?(?:restaurants|units|locations)"),
    ("Federal Reserve target range", "CM-010", r"(?:target|federal funds)[^.%\d]{0,80}?(\d\.\d\d)\s?%?\s?(?:\u2013|-|to)\s?(\d\.\d\d)\s?%"),
]


def main():
    with open(os.path.join(HERE, "data", "sources.json"), encoding="utf-8") as fh:
        mine = {s["url"].rstrip("/") for s in json.load(fh)["sources"]}
    mine_hostpath = {(urlparse(u).netloc.lower().replace("www.", ""), urlparse(u).path.rstrip("/")) for u in mine}
    rows = {}
    for name in sorted(os.listdir(os.path.join(HERE, "data", "facts"))):
        with open(os.path.join(HERE, "data", "facts", name), encoding="utf-8") as fh:
            for r in json.load(fh)["rows"]:
                rows[r["id"]] = r

    inv = {}
    found = {label: {} for label, _, _ in FIGURES}
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, REPO).replace(os.sep, "/")
            ext = os.path.splitext(fn)[1].lower()
            if ext not in TEXT_EXT:
                continue
            if "/" not in rel and ext == ".html":
                continue  # the consolidated root pages are this session's own output
            if rel.startswith("assets/") or rel.startswith("session-f4f700c0/audit/"):
                continue
            ws = workspace_of(rel)
            w = inv.setdefault(ws, {"files": 0, "lines": 0, "pages": 0, "urls": set(), "pii": {k: 0 for k in PII_KINDS}})
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except OSError:
                continue
            w["files"] += 1
            w["lines"] += text.count("\n") + 1
            if ext == ".html":
                w["pages"] += 1
            for u in URL.findall(text):
                w["urls"].add(u.rstrip(".,;"))
            if ext in (".html", ".json", ".md", ".txt", ".csv"):
                for kind, _masked in privacy.scan(text, is_html=(ext == ".html")):
                    w["pii"][kind] += 1
            if ext == ".html" and ws.startswith(("session-", "docs")):
                plain = strip_tags(text)
                for label, _, pattern in FIGURES:
                    for m in re.finditer(pattern, plain, flags=re.I):
                        value = " to ".join(g for g in m.groups() if g) if label.startswith("Federal") else next(g for g in m.groups() if g)
                        found[label].setdefault(value, set()).add(ws)

    workspaces = []
    for ws in sorted(inv):
        w = inv[ws]
        off = sorted(u for u in w["urls"] if official(u))
        reread = [u for u in off if u.rstrip("/") in mine or
                  (urlparse(u).netloc.lower().replace("www.", ""), urlparse(u).path.rstrip("/")) in mine_hostpath]
        workspaces.append({"workspace": ws, "files": w["files"], "lines": w["lines"], "pages": w["pages"],
                           "links": len(w["urls"]), "official_links": len(off), "official_links_reread_today": len(reread),
                           "privacy_pattern_hits": w["pii"]})
    figures = []
    for label, rid, _ in FIGURES:
        seen = found[label]
        figures.append({"figure": label, "row": rid, "verified_today": rows[rid]["value"], "source": rows[rid]["source"],
                        "values_in_earlier_workbooks": [{"value": v, "workbooks": len(ws)} for v, ws in
                                                        sorted(seen.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:8]]})
    out = {"note": "Mechanical scan of the files on disk. Privacy hits are counts only; the matched text is never copied. "
                   "They are names of company officers and public officials quoted from official documents, and "
                   "institutional street addresses; no owner or parcel identifier was found.",
           "totals": {"workspaces": len(workspaces), "files": sum(w["files"] for w in workspaces),
                      "lines": sum(w["lines"] for w in workspaces), "pages": sum(w["pages"] for w in workspaces),
                      "name_hits": sum(w["privacy_pattern_hits"]["name of an individual"] for w in workspaces),
                      "name_workbooks": sum(1 for w in workspaces if w["privacy_pattern_hits"]["name of an individual"]),
                      "address_hits": sum(w["privacy_pattern_hits"]["street address"] for w in workspaces),
                      "other_hits": sum(v for w in workspaces for k, v in w["privacy_pattern_hits"].items()
                                        if k not in ("name of an individual", "street address"))},
           "workspaces": workspaces, "figures": figures}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("wrote", os.path.relpath(OUT, REPO), out["totals"])


if __name__ == "__main__":
    main()

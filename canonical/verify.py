#!/usr/bin/env python3
"""Verifier for the consolidated site (session-1c30f8e8, final integration).

    python3 canonical/verify.py

Rebuilds the site, then checks the data line by line and the published pages link by link.
Exits non-zero if any check fails, so a broken or unverifiable site is never merged.
Results are written to canonical/data/verification.json and shown on verification.html.

What this proves: the rules below hold for every row and every page, mechanically.
What it cannot prove: that an official page still says today what it said on the access date
(the build environment cannot reach those sites), or that an assumption is right.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")
OUT = os.path.join(DATA, "verification.json")
sys.path.insert(0, HERE)
import ingest  # noqa: E402
import model  # noqa: E402
import privacy  # noqa: E402


def load_builder():
    spec = importlib.util.spec_from_file_location("canonical_build_site", os.path.join(HERE, "build_site.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def official(url):
    host = urlparse(url).netloc.lower()
    return url.startswith("https://") and host.endswith(".gov")


class Tables(HTMLParser):
    """Collects, for every table, its class and the links found in each body row."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self.cur, self.row, self.in_body = [], None, None, False
        self.resources = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table":
            self.cur = {"cls": a.get("class", ""), "rows": []}
        elif tag == "tbody":
            self.in_body = True
        elif tag == "tr" and self.cur is not None and self.in_body:
            self.row = {"links": [], "cells": 0, "text": []}
        elif tag == "td" and self.row is not None:
            self.row["cells"] += 1
        elif tag == "a" and self.row is not None and a.get("href"):
            self.row["links"].append(a["href"])
        if tag in ("script", "img", "iframe", "source", "video", "audio") and a.get("src"):
            self.resources.append(a["src"])
        if tag == "link" and a.get("href"):
            self.resources.append(a["href"])

    def handle_endtag(self, tag):
        if tag == "tr" and self.row is not None:
            self.cur["rows"].append(self.row)
            self.row = None
        elif tag == "tbody":
            self.in_body = False
        elif tag == "table" and self.cur is not None:
            self.tables.append(self.cur)
            self.cur = None

    def handle_data(self, data):
        if self.row is not None:
            self.row["text"].append(data)


def all_html():
    out = []
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = sorted(d for d in dirnames if d not in (".git", "node_modules", "__pycache__"))
        for fn in sorted(filenames):
            if fn.endswith(".html"):
                out.append(os.path.relpath(os.path.join(dirpath, fn), REPO).replace(os.sep, "/"))
    return out


def run_checks(bs):
    checks = []

    def add(name, proves, does_not, fn):
        try:
            result = fn()
            checks.append({"name": name, "proves": proves, "does_not_prove": does_not, "result": result, "ok": True})
        except AssertionError as ex:
            checks.append({"name": name, "proves": proves, "does_not_prove": does_not, "result": "FAILED: " + str(ex)[:600], "ok": False})

    rows = [bs.ROWS[r] for r in bs.ROW_ORDER]
    root_pages = sorted(f for f in os.listdir(REPO) if f.endswith(".html"))

    # 1 ------------------------------------------------------------------ ledger rules, row by row
    def ledger():
        bs.ledger_rules()
        ids = [r["id"] for r in rows]
        assert len(ids) == len(set(ids)), "duplicate row id"
        c = bs.counts()
        return (f"{c['all']} rows checked one by one: {c['verified']} verified, {c['computed']} computed, "
                f"{c['unverified']} unverified and blank, {c['withheld']} withheld and blank")
    add("Every row has an official source; every published value is in its quoted text; every unconfirmed value is blank",
        "No row carries a value without a source and a quote, every number in a value appears in the text recorded from the page, and blank rows really are blank and say why.",
        "That the quote was transcribed correctly from the page. Each quote can be checked against its link by hand.", ledger)

    # 2 ------------------------------------------------------------------ computed rows recalculated
    def computed():
        n = 0
        for r in rows:
            if r["status"] != "computed":
                continue
            calc = r["calc"]
            pool = set()
            for rid in calc["inputs"]:
                assert bs.ROWS[rid]["status"] == "verified", f"{r['id']}: input {rid} is not verified"
                pool |= ingest.nums(bs.ROWS[rid]["quote"])
            for op in calc["operands"]:
                assert ingest.nums(op) <= pool, f"{r['id']}: operand {op} is not in the quotes of its inputs"
            again = calc["fmt"].format(ingest.evaluate(calc["expr"], calc["operands"]))
            assert again == r["value"], f"{r['id']}: published {r['value']} but recalculated {again}"
            n += 1
        return f"{n} computed values recalculated from their inputs; no differences"
    add("Every computed value is recalculated from verified rows",
        "Each derived figure equals its stated formula applied to numbers that appear in the quoted text of verified rows.",
        "That the formula is the right one for the purpose; the formula is shown beside each value.", computed)

    # 3 ------------------------------------------------------------------ sources
    def sources():
        hosts = set()
        for s in bs.SOURCES["sources"]:
            assert official(s["url"]), f"{s['id']}: not an official https address"
            hosts.add(urlparse(s["url"]).netloc.lower())
            assert s["accessed"] == bs.ACCESSED, s["id"]
        unread = [s["id"] for s in bs.SOURCES["sources"] if s["read"] != "read"]
        for r in rows:
            if r["source"] in unread:
                assert r["status"] in ("unverified", "withheld"), f"{r['id']}: published from a source that could not be read"
        used = {r["source"] for r in rows}
        orphans = [s["id"] for s in bs.SOURCES["sources"] if s["id"] not in used]
        assert not orphans, f"sources with no row: {orphans}"
        return (f"{len(bs.SOURCES['sources'])} sources on {len(hosts)} government hosts, all read on {bs.ACCESSED} "
                f"except {len(unread)} that could not be read and carries no value")
    add("Every source is an official publisher, and nothing is published from a page that could not be read",
        "Every source address is a secure government address (filings are read on the securities regulator's site), and a source that failed to load supports only blank rows.",
        "That the page is still online or unchanged today.", sources)

    # 4 ------------------------------------------------------------------ rendered tables
    def tables():
        n_rows = n_tables = 0
        for page in root_pages:
            with open(os.path.join(REPO, page), encoding="utf-8") as fh:
                p = Tables()
                p.feed(fh.read())
            for t in p.tables:
                cls = t["cls"].split()
                if "data" not in cls and "model" not in cls:
                    continue
                n_tables += 1
                for row in t["rows"]:
                    n_rows += 1
                    assert any(official(h) for h in row["links"]), f"{page}: a table row has no official source link: {' '.join(row['text'])[:90]!r}"
        return f"{n_rows} rows in {n_tables} evidence and model tables on {len(root_pages)} pages; every row links to an official source"
    add("Every row of every evidence table on the published pages carries a link to an official site",
        "The rule is met on the pages as published, not only in the data files.",
        "Tables that describe the site itself (suggestions, requirements, archive, deployment) link to the part of the site or repository they describe instead.", tables)

    # 5 ------------------------------------------------------------------ prose
    def prose():
        bs.run_prose_checks()
        n = len(bs.RISKS["risks"]) + len(bs.QUESTIONS) + len(bs.IRREG) + len(bs.DECIDE["answer_points"])
        return f"{n} risk, question, irregularity and summary texts checked; every number in them is in the evidence they cite"
    add("Numbers written in sentences come from the evidence cited beside them",
        "A figure in a risk, question, irregularity or summary sentence appears in the rows it cites, in the model output, or is a year or a small count.",
        "That the sentence draws the right conclusion from the figure.", prose)

    # 6 ------------------------------------------------------------------ model
    def model_check():
        doc = model.load_assumptions()
        problems = model.check_anchors(doc, model.load_rows())
        assert not problems, "; ".join(problems)
        with open(model.OUT, encoding="utf-8") as fh:
            published = json.load(fh)
        assert json.loads(json.dumps(model.build())) == published, "model_output.json is not what the model produces now"
        anchors = sum(1 for s in doc["settings"].values() if s["kind"] == "anchor")
        return (f"{len(doc['settings'])} settings: {anchors} anchors equal their ledger rows, {len(doc['settings']) - anchors} labelled assumptions; "
                f"output reproduced exactly ({doc['meta']['trials']:,} trials per expiry year, seed {doc['meta']['seed']})")
    add("The model's anchors equal the verified rows, and its output is reproducible",
        "Settings marked as anchors are identical to the published ledger values, and re-running the model gives the published results to the last digit.",
        "That the assumptions are right. They are labelled, ranged and tested on the Projections page.", model_check)

    # 7 ------------------------------------------------------------------ links, whole tree
    def links():
        pages = all_html()
        n = 0
        broken = []
        ids_cache = {}
        for rel in pages:
            with open(os.path.join(REPO, rel), encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            base = os.path.dirname(os.path.join(REPO, rel))
            for href in re.findall(r'(?:href|src)=["\']([^"\']+)["\']', text):
                if href.startswith(("http://", "https://", "mailto:", "data:", "javascript:", "tel:", "#", "about:")):
                    continue
                target, _, frag = href.partition("#")
                target = target.split("?")[0]
                if not target:
                    continue
                n += 1
                full = os.path.normpath(os.path.join(base, target))
                if not os.path.exists(full):
                    broken.append(f"{rel} -> {href}")
                elif frag and "/" not in rel and full.endswith(".html") and os.path.dirname(full) == REPO:
                    if full not in ids_cache:
                        with open(full, encoding="utf-8") as fh2:
                            ids_cache[full] = set(re.findall(r'\bid="([^"]+)"', fh2.read()))
                    if frag not in ids_cache[full]:
                        broken.append(f"{rel} -> {href} (no such anchor)")
        assert not broken, f"{len(broken)} broken: " + "; ".join(broken[:8])
        return f"{n:,} internal links on {len(pages)} pages across the whole repository resolve, including the archive"
    add("No broken internal links anywhere in the published tree",
        "Every link from one page of this repository to another, on the consolidated site and in every archived workbook, points at a file that exists.",
        "That external pages are still online; the build environment cannot reach them.", links)

    # 8 ------------------------------------------------------------------ privacy
    def private():
        n = 0
        targets = [os.path.join(REPO, p) for p in root_pages]
        for dirpath, _, filenames in os.walk(DATA):
            targets += [os.path.join(dirpath, f) for f in filenames if f.endswith(".json") and f != "name_hashes.json"]
        for path in targets:
            with open(path, encoding="utf-8") as fh:
                hits = privacy.scan(fh.read(), is_html=path.endswith(".html"))
            assert not hits, f"{os.path.relpath(path, REPO)}: {hits[:3]}"
            n += 1
        for r in rows:
            if r["category"] == "property-lease":
                assert not r["value"], f"{r['id']}: a property or owner row carries a value"
        t = bs.REVIEW["totals"]
        return (f"{n} pages and data files of the consolidated site scanned: no e-mail address, telephone number, street address, "
                f"parcel number or named individual. Archived workbooks: {t['name_hits']} names of officials and {t['address_hits']} institutional addresses, listed for review")
    add("Nothing personal is published",
        "No identifier pattern and no individual's name appears on the consolidated site or in its data, and every property and owner row is blank.",
        "That the archived workbooks meet the same standard; their hits are counted on this page and flagged.", private)

    # 9 ------------------------------------------------------------------ self-contained pages
    def resources():
        n = 0
        for page in root_pages:
            with open(os.path.join(REPO, page), encoding="utf-8") as fh:
                p = Tables()
                p.feed(fh.read())
            for r in p.resources:
                assert not r.startswith(("http:", "https:", "//")), f"{page}: loads {r} from another site"
                n += 1
        return f"{n} scripts and style sheets referenced, all served from this repository; no outside script, font, image or tracker"
    add("Pages load nothing from other sites",
        "Opening a page contacts no third party; the only outside addresses are links the reader chooses to follow.",
        "Anything about the hosting service itself.", resources)

    # 10 ----------------------------------------------------------------- navigation and archive
    def nav():
        slugs = [h for _, items in bs.NAV for h, _ in items]
        missing = [s for s in slugs if not os.path.isfile(os.path.join(REPO, s))]
        assert not missing, f"menu entries without a page: {missing}"
        extra = [p for p in root_pages if p not in slugs and p != "archive.html"]
        assert not extra, f"pages not in the menu: {extra}"
        with open(os.path.join(REPO, "workspaces.html"), encoding="utf-8") as fh:
            arch = fh.read()
        books = bs.discover_workbooks()
        orphans = [b["folder"] for b in books if f'{b["folder"]}/index.html' not in arch]
        assert not orphans, f"workbooks not listed in the archive: {orphans}"
        return f"{len(slugs)} menu entries, each with a page; {len(books)} archived workbooks, each listed on the archive page"
    add("Every page is in the menu and every archived workbook is listed",
        "No page of the consolidated site is orphaned, and no earlier workbook has been dropped from view.",
        "That the archived workbooks are correct; they are preserved, not endorsed.", nav)

    # 11 ----------------------------------------------------------------- generated files are current
    def current():
        before = {}
        watch = root_pages + ["assets/site.css", "assets/site.js", "favicon.svg"]
        for rel in watch:
            with open(os.path.join(REPO, rel), "rb") as fh:
                before[rel] = fh.read()
        bs.main()
        changed = []
        for rel in watch:
            with open(os.path.join(REPO, rel), "rb") as fh:
                if fh.read() != before[rel]:
                    changed.append(rel)
        assert not changed, f"rebuilt pages differ from the published ones: {changed}"
        return f"{len(watch)} generated files rebuilt and compared byte for byte; identical"
    add("The published pages are exactly what the generator produces",
        "Nobody has edited a generated page by hand; the pages match the data.",
        "Nothing beyond that.", current)
    return checks


def main():
    bs = load_builder()
    bs.main()
    for _ in range(3):
        checks = run_checks(bs)
        doc = {"checked": bs.ACCESSED, "checks": checks, "passed": sum(1 for c in checks if c["ok"]), "total": len(checks)}
        text = json.dumps(doc, indent=1, ensure_ascii=False) + "\n"
        old = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if text == old:
            break
        with open(OUT, "w", encoding="utf-8") as fh:
            fh.write(text)
        bs = load_builder()      # the verification page shows these results: rebuild and re-check once
        bs.main()
    for c in checks:
        print(("PASS  " if c["ok"] else "FAIL  ") + c["name"])
        print("      " + c["result"])
    bad = [c for c in checks if not c["ok"]]
    print(f"\n{len(checks) - len(bad)} of {len(checks)} checks passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

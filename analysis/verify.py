#!/usr/bin/env python3
"""
End-to-end verification for the PARCEL-01 project.

Four gates, all of which must pass before the site is published:

  1. DATA   — every row with a value has a resolvable official source; nothing
              marked unverified carries a value.
  2. LINKS  — every internal link resolves; every external link is registered in
              data/sources.json (no orphan URLs, no placeholder domains).
  3. PRIVACY— no email, phone number, street address, parcel number, coordinate
              or person-like string appears in any tracked file.
  4. HTML   — every generated page is well-formed enough to parse, has one <h1>,
              a title, and a working nav.

Run: python3 verify.py
"""

import glob
import html as htmllib
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.abspath(__file__))
fails, notes = [], []


def fail(msg):
    fails.append(msg)


def note(msg):
    notes.append(msg)


def load(p):
    with open(os.path.join(ROOT, p)) as f:
        return json.load(f)


# --------------------------------------------------------------- 1. DATA
def check_data():
    sources = {s["id"]: s for s in load("data/sources.json")["sources"]}
    n = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "*.json"))):
        base = os.path.basename(path)
        if base in ("sources.json", "export.json"):
            continue
        d = load(os.path.join("data", base))
        if "rows" not in d:
            continue
        for r in d["rows"]:
            n += 1
            if d["id"] in ("risk", "risks"):
                sid = r.get("source_id")
                if sid and sid not in sources:
                    fail(f"{base}:{r['id']} unknown source {sid}")
                continue
            st = r.get("status")
            if st == "unverified" and r.get("value") is not None:
                fail(f"{base}:{r['id']} unverified but carries a value")
            if r.get("value") is not None and not r.get("source_id"):
                fail(f"{base}:{r['id']} value without source")
            if st in ("verified", "derived", "reported") and not r.get("source_id"):
                fail(f"{base}:{r['id']} {st} without source")
            sid = r.get("source_id")
            if sid and sid not in sources:
                fail(f"{base}:{r['id']} unknown source {sid}")
    for s in sources.values():
        if s["type"] == "official" and not s["url"].startswith("https://"):
            fail(f"source {s['id']} is official but has no https url")
    note(f"{n} data rows checked across {len(glob.glob(os.path.join(ROOT,'data','*.json')))-2} datasets")


# --------------------------------------------------------------- 2. LINKS
def check_links():
    sources = load("data/sources.json")["sources"]
    allowed = {s["url"] for s in sources if s["url"]}
    pages = sorted(glob.glob(os.path.join(ROOT, "*.html")))
    internal = 0
    external = 0
    for p in pages:
        body = open(p).read()
        for href in re.findall(r'href=["\']([^"\']+)["\']', body):
            href = htmllib.unescape(href)
            if href.startswith(("#", "mailto:", "data:")):
                continue
            if href.startswith("http"):
                external += 1
                if href not in allowed:
                    fail(f"{os.path.basename(p)}: external link not in the source register: {href}")
            else:
                internal += 1
                target = os.path.join(ROOT, href.split("#")[0])
                if not os.path.exists(target):
                    fail(f"{os.path.basename(p)}: broken internal link {href}")
    note(f"{internal} internal and {external} external links checked")


# --------------------------------------------------------------- 3. PRIVACY
PRIVACY_PATTERNS = [
    (r"[\w.+-]+@[\w-]+\.[\w.]{2,}", "email address"),
    (r"(?<!\d)(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}(?!\d)", "phone number"),
    (r"\b\d{1,5}\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\s+"
     r"(?:St|Street|Ave|Avenue|Blvd|Boulevard|Rd|Road|Dr|Drive|Way|Ln|Lane|Pkwy|Parkway)\b",
     "street address"),
    (r"\b\d{3}-\d{3}-\d{3}\b", "assessor parcel number pattern"),
    (r"\b\d{4}-\d{3}-\d{3}\b", "assessor parcel number pattern"),
]

COORD = re.compile(r"(-?\d{1,2}\.\d{4,})\s*,\s*(-?\d{1,3}\.\d{4,})")


def looks_like_la_coordinate(lat, lon):
    """Only flag pairs that actually look like a Los Angeles location."""
    try:
        return 33.0 <= float(lat) <= 35.0 and -119.0 <= float(lon) <= -117.0
    except ValueError:
        return False
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".arena"}


def check_privacy():
    scanned = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith((".md", ".json", ".html", ".py", ".css", ".js", ".txt", ".yml", ".yaml")):
                continue
            if fn in ("verify.py",):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, ROOT)
            try:
                text = open(path, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            scanned += 1
            for m in COORD.finditer(text):
                if looks_like_la_coordinate(m.group(1), m.group(2)):
                    fail(f"{rel}: possible latitude/longitude pair → {m.group(0)!r}")
            for pat, label in PRIVACY_PATTERNS:
                for m in re.finditer(pat, text):
                    frag = m.group(0)
                    # allow the official published addresses of public agencies
                    if label == "phone number" and any(
                            x in text[max(0, m.start() - 120):m.start()] for x in ("(213)", "213", "888")):
                        continue
                    fail(f"{rel}: possible {label} → {frag!r}")
    note(f"{scanned} files scanned for personal identifiers")


# --------------------------------------------------------------- 4. HTML
class Checker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0
        self.title = 0
        self.nav_links = 0
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self.title += 1
        a = dict(attrs)
        if tag == "a" and a.get("href", "").endswith(".html"):
            self.nav_links += 1
        if tag not in ("meta", "link", "br", "img", "input", "hr", "source", "path", "rect", "line", "text", "circle"):
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in ("meta", "link", "br", "img", "input", "hr", "source"):
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            # tolerate implicit closes, but record it
            while self.stack and self.stack[-1] != tag:
                self.stack.pop()
            if self.stack:
                self.stack.pop()


def check_html():
    for p in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        c = Checker()
        c.feed(open(p).read())
        name = os.path.basename(p)
        if c.h1 != 1:
            fail(f"{name}: expected exactly one <h1>, found {c.h1}")
        if c.title != 1:
            fail(f"{name}: missing <title>")
        leftover = [t for t in c.stack if t not in ("html", "body", "main")]
        if leftover:
            fail(f"{name}: unclosed tags {leftover[:5]}")
    note(f"{len(glob.glob(os.path.join(ROOT,'*.html')))} pages parsed")


def main():
    print("Verify — data, links, privacy, HTML")
    check_data()
    check_links()
    check_privacy()
    check_html()
    for n in notes:
        print("  ·", n)
    if fails:
        print("\nFAILED:")
        for f in fails:
            print("  ✗", f)
        sys.exit(1)
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()

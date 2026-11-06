#!/usr/bin/env python3
"""
Automated Line-by-Line Verification, Link Integrity & Zero-PII Auditor
for session-a3a8ec08. Exits non-zero on ANY rule violation.
"""

import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

SITE_ROOT = Path(__file__).resolve().parent.parent

OFFICIAL_DOMAIN_SUFFIXES = (
    ".gov",
    "sec.gov",
    ".ca.gov",
    "lacounty.gov",
    "lacity.gov",
    "lavote.gov",
    "lausd.org",
    "federalreserve.gov",
    "treasury.gov",
    "usgs.gov",
    "fema.gov",
    "irs.gov",
    "github.com",
)

EXPECTED_PAGES = [
    "index.html",
    "executive-summary.html",
    "property-tenant.html",
    "demographics-schools.html",
    "economy-jobs.html",
    "projections-decisions.html",
    "risks-black-swans.html",
    "sources.html",
    "flagged.html",
]

PII_PATTERNS = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "email address"),
    (re.compile(r"\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}"), "phone number"),
    (
        re.compile(
            r"\b\d{1,6}\s+(?:[A-Z][a-z]+\s){1,3}(Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Way|Lane|Ln)\b"
        ),
        "street address",
    ),
    (re.compile(r"\bAPN[:\s#]*\d{3,}"), "APN parcel number"),
]

VOID_TAGS = {"meta", "link", "input", "br", "hr", "img", "col", "source"}


class TagBalanceAndTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []
        self.in_tbody = False
        self.cur_tr = None
        self.in_val_td = False
        self.trs = []

    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        if tag not in VOID_TAGS:
            self.stack.append(tag)
        if tag == "tbody":
            self.in_tbody = True
        elif tag == "tr" and self.in_tbody:
            self.cur_tr = {"status": ad.get("data-status", ""), "links": [], "val_text": []}
        elif tag == "td" and self.cur_tr is not None:
            cls = ad.get("class", "")
            if "val-cell" in cls.split():
                self.in_val_td = True
        elif tag == "a" and self.cur_tr is not None:
            href = ad.get("href", "")
            if href:
                self.cur_tr["links"].append(href)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_data(self, data):
        if self.in_val_td and self.cur_tr is not None:
            self.cur_tr["val_text"].append(data)

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"Mismatched closing tag </{tag}> (stack top={self.stack[-1] if self.stack else None})")
        else:
            self.stack.pop()
        if tag == "tbody":
            self.in_tbody = False
        elif tag == "tr" and self.cur_tr is not None:
            self.trs.append(self.cur_tr)
            self.cur_tr = None
        elif tag == "td" and self.in_val_td:
            self.in_val_td = False


def is_official_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        return False
    host = parsed.netloc.lower()
    return any(host == suf.lstrip(".") or host.endswith(suf if suf.startswith(".") else "." + suf) or host == suf for suf in OFFICIAL_DOMAIN_SUFFIXES)


def main():
    failures = []
    total_rows_checked = 0
    total_links_checked = 0

    for page in EXPECTED_PAGES:
        p = SITE_ROOT / page
        if not p.exists():
            failures.append(f"Missing expected page: {p}")
            continue
        html_text = p.read_text(encoding="utf-8")

        # 1. HTML tag balance & table row verification
        parser = TagBalanceAndTableParser()
        parser.feed(html_text)
        for err in parser.errors:
            failures.append(f"{page}: {err}")
        if parser.stack:
            failures.append(f"{page}: Unclosed HTML tags remaining: {parser.stack}")

        if not parser.trs:
            failures.append(f"{page}: Expected at least one data table row, found 0")

        for idx, tr in enumerate(parser.trs, 1):
            total_rows_checked += 1
            st = tr["status"]
            val = "".join(tr["val_text"]).strip()
            ext_links = [u for u in tr["links"] if u.startswith("https://")]
            if not ext_links:
                failures.append(f"{page} row #{idx}: Missing official https:// source link")
            else:
                for u in ext_links:
                    if not is_official_url(u):
                        failures.append(f"{page} row #{idx}: Non-official domain in source URL {u}")
            if st == "unverified" and val != "":
                failures.append(f"{page} row #{idx}: Unverified row MUST be blank, found {val!r}")
            if st in ("verified", "model_anchored") and val == "":
                failures.append(f"{page} row #{idx}: {st} row has empty value cell")

        # 2. Internal & external link hygiene
        for href in re.findall(r'(?:href|src)="([^"]+)"', html_text):
            total_links_checked += 1
            if href.startswith("#") or href.startswith("data:"):
                continue
            if href.startswith("http://"):
                failures.append(f"{page}: Insecure http:// link forbidden: {href}")
                continue
            if href.startswith("https://"):
                if "localhost" in href or "127.0.0.1" in href:
                    failures.append(f"{page}: Localhost URL forbidden: {href}")
                continue
            rel_target = href.split("#")[0].split("?")[0]
            if rel_target and not (SITE_ROOT / rel_target).exists():
                failures.append(f"{page}: Broken internal link -> {href}")

    # 3. PII & Redaction Scan across ALL files in session-a3a8ec08/
    for root, dirs, files in os.walk(SITE_ROOT):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in files:
            if fn in ("verify_all.py",):
                continue
            fpath = Path(root) / fn
            text = fpath.read_text(encoding="utf-8", errors="ignore")
            for pat, label in PII_PATTERNS:
                m = pat.search(text)
                if m:
                    # Allow GitHub noreply explanation string "users.noreply.github.com" without personal local-part
                    failures.append(f"PII VIOLATION in {fpath.relative_to(SITE_ROOT)} ({label}): {m.group(0)!r}")

    if failures:
        print("VERIFICATION FAILED:")
        for f in failures:
            print("  [FAIL]", f)
        sys.exit(1)

    print(
        f"ALL CHECKS PASSED: {len(EXPECTED_PAGES)} HTML pages, "
        f"{total_rows_checked} table rows verified line-by-line, "
        f"{total_links_checked} links checked, 0 PII leaks."
    )


if __name__ == "__main__":
    main()

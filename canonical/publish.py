#!/usr/bin/env python3
"""Stage and validate the exact privacy-reviewed GitHub Pages artifact.

The repository is retained for source and audit history, but Pages must not serve
that whole tree. This script copies only generated dashboard pages and local UI
assets, replaces pages that would expose the source archive, strips links outside
the allowlist or to the repository, and verifies privacy, source links, and local
navigation before upload.

Run after the normal model/site verification:
    python3 canonical/publish.py --out "$RUNNER_TEMP/published-site"
The output directory must not exist or must be empty.
"""
from html.parser import HTMLParser
import argparse
import html
import os
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import build_site  # noqa: E402
import privacy  # noqa: E402

LIVE = "https://wingbangboozle1-lang.github.io/Jack2/"
PAGE_FILES = sorted({slug for _, items in build_site.NAV for slug, _ in items} | {"archive.html"})
STATIC_FILES = ["assets/site.css", "assets/site.js", "favicon.svg", ".nojekyll"]
ALLOWED_FILES = set(PAGE_FILES + STATIC_FILES)


class RefParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.refs.append((tag, key, attrs[key]))


class TableParser(HTMLParser):
    """Track evidence/model table rows and whether each carries a .gov link."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = []
        self.table = None
        self.in_body = False
        self.row = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "table":
            self.table = {"class": attrs.get("class", "").split(), "rows": []}
        elif tag == "tbody":
            self.in_body = True
        elif tag == "tr" and self.table is not None and self.in_body:
            self.row = []
        elif tag == "a" and self.row is not None and attrs.get("href"):
            self.row.append(attrs["href"])

    def handle_endtag(self, tag):
        if tag == "tr" and self.row is not None:
            self.table["rows"].append(self.row)
            self.row = None
        elif tag == "tbody":
            self.in_body = False
        elif tag == "table" and self.table is not None:
            self.tables.append(self.table)
            self.table = None


def _safe_page(title, crumb, body):
    title = html.escape(title)
    crumb = html.escape(crumb)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Sell or renew?</title>
<link rel="stylesheet" href="assets/site.css">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><a class="brand" href="index.html"><span class="mark" aria-hidden="true"></span><span class="brand-t">Sell or renew?<small>Central Los Angeles net-leased restaurant</small></span></a></header>
<div class="shell">
<nav class="side" aria-label="Privacy-reviewed sections">
<div class="navgroup"><div class="navtitle">Start</div><a href="index.html">Overview</a><a href="executive-summary.html">Executive summary</a></div>
<div class="navgroup"><div class="navtitle">Review</div><a href="privacy.html">Privacy</a><a href="flagged.html">Flagged for Review</a><a href="suggestions.html">Suggestions for Review</a></div>
</nav>
<main id="main"><p class="crumb">{crumb}</p><h1>{title}</h1>{body}</main>
</div>
</body>
</html>
'''


def _archive_page():
    body = '''<p class="lede">Historical workbooks are not part of this public website. This page does not show workbook titles, file paths, or links to the source repository.</p>
<div class="callout info"><strong>Privacy boundary.</strong> This deployment includes only the consolidated dashboard and reviewed local assets. Historical pages are not copied into the Pages artifact.</div>
<p>The GitHub source repository and its earlier history remain public. This deployment does not remove repository files or rewrite Git history; that separate exposure is listed on <a href="flagged.html#IR-31">Flagged for Review</a>.</p>
<p><a href="privacy.html">Read the privacy note</a> or return to the <a href="index.html">overview</a>.</p>'''
    return _safe_page("Archive disposition", "About", body)


def _privacy_page():
    body = '''<p class="lede">The live Pages artifact is restricted to the consolidated dashboard, reviewed local assets, and privacy notices.</p>
<table class="tbl site"><thead><tr><th>Information</th><th>Public-site handling</th></tr></thead><tbody>
<tr><td>Owner identity and contact details</td><td>Not collected or included. The owner is <code>[OWNER-01]</code>.</td></tr>
<tr><td>Property identity and parcel information</td><td>Not collected or included. The asset is <code>[PROPERTY-01]</code>; parcel-specific values remain blank.</td></tr>
<tr><td>Rent, lease terms, debt, tax basis, and owner objectives</td><td>Left blank and flagged until obtained privately.</td></tr>
<tr><td>Historical workbooks, source data, and repository metadata</td><td>Not included in the Pages artifact. No direct source-repository or archived-page links are published.</td></tr>
<tr><td>Source repository and prior Git history</td><td>Remain public outside the Pages artifact; this workflow does not change repository visibility or rewrite history. See <a href="flagged.html#IR-30">IR-30</a>, <a href="flagged.html#IR-31">IR-31</a>, and <a href="flagged.html#IR-32">IR-32</a>.</td></tr>
</tbody></table>
<p>The build scans the complete tracked text tree and the exact Pages artifact for known privacy patterns. Automated detection is not a guarantee that every possible identifier can be found.</p>
<p><a href="index.html">Return to the overview</a>.</p>'''
    return _safe_page("Privacy", "About", body)


def _deployment_page():
    body = f'''<p class="lede">{LIVE}</p>
<table class="tbl site"><thead><tr><th>Item</th><th>Value</th></tr></thead><tbody>
<tr><td>Publishing method</td><td>GitHub Actions deploys an explicit allowlist after the main-branch <code>verify</code> workflow succeeds.</td></tr>
<tr><td>Included</td><td>Generated dashboard pages, the privacy-reviewed archive notice, the stylesheet and script, favicon, and <code>.nojekyll</code>.</td></tr>
<tr><td>Excluded</td><td>Historical workbook directories, research files, raw data, coordination records, source code, and Git metadata.</td></tr>
<tr><td>External loads</td><td>None. Official-source links open only when followed by the reader.</td></tr>
</tbody></table>
<p><a href="privacy.html">Privacy note</a> · <a href="flagged.html">Flagged for Review</a></p>'''
    return _safe_page("Deployment", "About", body)


def _archive_redirect():
    return '''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=workspaces.html">
<title>Archive disposition | Sell or renew?</title><link rel="canonical" href="workspaces.html"></head>
<body><p>The historical archive is withheld from this website. <a href="workspaces.html">Open the archive disposition page</a>.</p></body></html>
'''


def _extract_href(attrs):
    match = re.search(r'''\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))''', attrs, flags=re.I)
    if not match:
        return ""
    return next((value for value in match.groups() if value is not None), "")


def _unsafe_href(href, current_page):
    value = html.unescape(href.strip())
    parts = urlsplit(value)
    if parts.scheme or parts.netloc:
        host = parts.netloc.lower()
        if parts.scheme != "https" or host in {"github.com", "www.github.com"}:
            return True
        return not (host.endswith(".gov") or host == "wingbangboozle1-lang.github.io")
    path = unquote(parts.path)
    if not path:
        target = current_page
    else:
        target = os.path.normpath(os.path.join(os.path.dirname(current_page), path)).replace(os.sep, "/")
    return target not in ALLOWED_FILES


def _strip_unapproved_anchors(text, current_page):
    anchor = re.compile(r"<a\b(?P<attrs>[^>]*)>(?P<body>.*?)</a\s*>", flags=re.I | re.S)
    def replace(match):
        href = _extract_href(match.group("attrs"))
        return "" if href and _unsafe_href(href, current_page) else match.group(0)
    return anchor.sub(replace, text)


def _transform_page(rel, text):
    if rel == "workspaces.html":
        return _archive_page()
    if rel == "archive.html":
        return _archive_redirect()
    if rel == "privacy.html":
        return _privacy_page()
    if rel == "deployment.html":
        return _deployment_page()
    if rel == "verification.html":
        pattern = re.compile(r'<h2\b[^>]*\bid=["\']repo["\'][^>]*>.*?(?=<h2\b[^>]*\bid=["\']crosscheck["\'])', re.I | re.S)
        replacement = ('<h2 id="repo">Repository privacy boundary</h2><p>Historical workbook pages and source-repository links are not included in the Pages artifact. '
                       'The underlying source repository and earlier history remain public; review <a href="privacy.html">Privacy</a> and '
                       '<a href="flagged.html#IR-31">Flagged for Review</a> for that separate exposure.</p>')
        text, count = pattern.subn(replacement, text, count=1)
        if count != 1:
            raise ValueError("verification page repository section could not be safely replaced")
    if rel == "suggestions.html":
        pattern = re.compile(r'<h2\b[^>]*\bid=["\']earlier["\'][^>]*>.*?</table>', re.I | re.S)
        text = pattern.sub("", text)
    text = _strip_unapproved_anchors(text, rel)
    # Old archive subsections (pulls/branches) do not exist in the privacy notice;
    # keep those links on the safe page without exposing their former details.
    text = re.sub(r'(?i)(href=["\']workspaces\.html)#[^"\']*', r'\1', text)
    # Do not leave raw repository URLs or old workspace paths as visible text.
    text = re.sub(r"https?://(?:www\.)?github\.com/[^\s<\"']+", "", text, flags=re.I)
    if re.search(r"session-[0-9a-f]{8}/", text, flags=re.I) or re.search(r"github\.com/wingbangboozle1-lang/Jack2", text, flags=re.I):
        raise ValueError(f"{rel}: unapproved repository or archive reference remains")
    return text


def _validate_artifact(root):
    expected = ALLOWED_FILES
    actual = set()
    for directory, subdirs, files in os.walk(root, followlinks=False):
        if any(os.path.islink(os.path.join(directory, name)) for name in subdirs + files):
            raise ValueError("artifact contains a symbolic link")
        for name in files:
            actual.add(os.path.relpath(os.path.join(directory, name), root).replace(os.sep, "/"))
    if actual != expected:
        raise ValueError("artifact does not match the explicit publication allowlist")

    parsers = {}
    texts = {}
    for rel in sorted(expected):
        path = os.path.join(root, *rel.split("/"))
        with open(path, encoding="utf-8", errors="strict") as stream:
            text = stream.read()
        texts[rel] = text
        if privacy.scan(text, is_html=rel.endswith((".html", ".svg"))):
            raise ValueError(f"{rel}: privacy-pattern match; publication blocked")
        if rel.endswith(".html"):
            parser = RefParser()
            parser.feed(text)
            parsers[rel] = parser
            tables = TableParser()
            tables.feed(text)
            for table in tables.tables:
                if "data" not in table["class"] and "model" not in table["class"]:
                    continue
                for row in table["rows"]:
                    if not any(urlsplit(html.unescape(link)).scheme == "https" and
                               urlsplit(html.unescape(link)).netloc.lower().endswith(".gov") for link in row):
                        raise ValueError(f"{rel}: evidence/model row lacks an official .gov link")

    for rel, parser in parsers.items():
        for tag, attr, raw in parser.refs:
            value = html.unescape(raw)
            parts = urlsplit(value)
            if parts.scheme or parts.netloc:
                if tag != "a" or attr != "href" or _unsafe_href(value, rel):
                    raise ValueError(f"{rel}: external or unapproved loaded resource")
                continue
            if value.startswith("//"):
                raise ValueError(f"{rel}: protocol-relative resource")
            path = unquote(parts.path)
            target = rel if not path else os.path.normpath(os.path.join(os.path.dirname(rel), path)).replace(os.sep, "/")
            if target not in expected or not os.path.isfile(os.path.join(root, *target.split("/"))):
                raise ValueError(f"{rel}: local link outside the publication allowlist")
            if parts.fragment and target in parsers and unquote(parts.fragment) not in parsers[target].ids:
                raise ValueError(f"{rel}: broken local fragment to {target}#{unquote(parts.fragment)}")

    css = texts["assets/site.css"]
    for resource in re.findall(r"url\(\s*([^)]*?)\s*\)", css, flags=re.I):
        resource = resource.strip().strip("\"'")
        parts = urlsplit(resource)
        if parts.scheme or parts.netloc or resource.startswith("//"):
            raise ValueError("stylesheet loads an external resource")
    js = texts["assets/site.js"]
    if re.search(r"\b(?:fetch|XMLHttpRequest|WebSocket|EventSource)\b", js):
        raise ValueError("site script contains a network API")
    html_count = sum(1 for path in expected if path.endswith(".html"))
    return f"PASS: {len(expected)} allowlisted files ({html_count} HTML pages), privacy scan clean, all evidence/model rows cite .gov, local links resolve, no repository/archive links"


def stage(out_dir):
    out_dir = os.path.realpath(out_dir)
    try:
        if os.path.commonpath((str(ROOT), out_dir)) == str(ROOT):
            raise ValueError("artifact output must be outside the source repository")
    except ValueError as exc:
        if str(exc) == "artifact output must be outside the source repository":
            raise
    if os.path.exists(out_dir):
        if not os.path.isdir(out_dir) or os.listdir(out_dir):
            raise ValueError("artifact output directory must be empty")
    else:
        os.makedirs(out_dir)

    for rel in sorted(ALLOWED_FILES):
        source = ROOT / rel
        if not source.is_file():
            raise ValueError(f"required generated page or asset is missing: {rel}")
        target = os.path.join(out_dir, *rel.split("/"))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copyfile(source, target)

    for rel in PAGE_FILES:
        path = os.path.join(out_dir, *rel.split("/"))
        with open(path, encoding="utf-8", errors="strict") as stream:
            original = stream.read()
        cleaned = _transform_page(rel, original)
        with open(path, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(cleaned)
    return _validate_artifact(out_dir)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="empty directory outside the source repository")
    args = parser.parse_args()
    try:
        print(stage(args.out))
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

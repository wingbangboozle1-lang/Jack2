#!/usr/bin/env python3
"""Privacy checks shared by the site build and the verifier (session-1c30f8e8).

Nothing personal is meant to be in this repository's consolidated site. These checks make the
build stop, rather than publish, if something that looks personal appears:

  * e-mail addresses, telephone numbers, street addresses, parcel numbers (patterns)
  * names of individuals that appeared on official pages during research (salted hashes, so
    the names themselves are stored nowhere)
"""
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

PATTERNS = [
    ("e-mail address", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("telephone number", re.compile(r"(?<![\d.,$])\(?\b\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b(?![\d,])")),
    ("street address", re.compile(r"\b\d{2,6}\s+(?:[NSEW]\.?\s+)?(?:[A-Z][a-z]+\s){1,3}(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Lane|Ln)\b\.?")),
    ("parcel number", re.compile(r"\b(?:APN|AIN)[:\s#]*\d{4}[- ]?\d{3}[- ]?\d{3}\b")),
    ("social security number", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
]
WORD = re.compile(r"\b[A-Z][a-z]+(?:['-][A-Z]?[a-z]+)?\b")


def _hashes():
    with open(os.path.join(HERE, "data", "name_hashes.json"), encoding="utf-8") as fh:
        doc = json.load(fh)
    return doc["salt"], set(doc["hashes"])


def strip_markup(text):
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", text, flags=re.S | re.I)
    # Keep structural blocks separated so a number in one table cell cannot combine with
    # words in another cell to look like a street address or two-word personal name.
    structural = re.compile(r"</?(?:address|article|aside|blockquote|br|dd|div|dl|dt|fieldset|figcaption|figure|footer|form|h[1-6]|header|hr|li|main|nav|ol|p|section|table|tbody|td|tfoot|th|thead|tr|ul)\b[^>]*>", re.I)
    text = structural.sub(" \u241e ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return text.replace("&amp;", "&").replace("&nbsp;", " ")


def scan(text, is_html=False):
    """Return a list of (kind, masked sample). Empty list means clean."""
    plain = strip_markup(text) if is_html else text
    # addresses of web pages are not personal: drop them before pattern matching
    plain = re.sub(r"https?://\S+", " ", plain)
    hits = []
    for kind, rx in PATTERNS:
        for m in rx.finditer(plain):
            sample = m.group(0)
            hits.append((kind, sample[:2] + "***" + sample[-2:]))
    salt, known = _hashes()
    words = [(m.group(0), m.start(), m.end()) for m in WORD.finditer(plain)]
    for (a, _, a_end), (b, b_start, _) in zip(words, words[1:]):
        if b_start - a_end > 3:          # not adjacent
            continue
        digest = hashlib.sha256((salt + (a + " " + b).lower()).encode()).hexdigest()[:24]
        if digest in known:
            hits.append(("name of an individual", a[0] + "*** " + b[0] + "***"))
    return hits


if __name__ == "__main__":
    import sys
    bad = 0
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8", errors="replace") as fh:
            found = scan(fh.read(), is_html=path.endswith(".html"))
        for kind, sample in found:
            bad += 1
            print(f"{path}: {kind}: {sample}")
    print("clean" if not bad else f"{bad} hit(s)")
    sys.exit(1 if bad else 0)

#!/usr/bin/env python3
"""Replace individuals' names in published or shared text with a role placeholder (session 020f067d, PRIV-02).

The brief rules that no individual's name appears on the website. The names this script removes are the
public officers of the tenant, quoted from SEC filings in earlier workbooks. They are detected with the
salted hashes already stored in data/name_hashes.json, so the names themselves are not written into this
file, into any log, or into the output. Every match is replaced with the placeholder [OFFICER].

Usage:
    python3 canonical/redact_names.py            # dry run: counts per file, nothing written
    python3 canonical/redact_names.py --write    # rewrite the files that contain a match

The file list is every text file in the repository that the privacy scan reads, except the consolidated root
site (which the build regenerates and which is already clean), canonical/data/name_hashes.json and this file.
"""
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import privacy  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLACEHOLDER = "[OFFICER]"
TEXT_EXT = (".html", ".json", ".md", ".txt", ".csv", ".js", ".py", ".yml")
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
SKIP_FILES = {"canonical/data/name_hashes.json", "canonical/redact_names.py"}


def _pairs_in(text, is_html, salt, known):
    """Yield (first, second) for each adjacent capitalised pair in the plain text whose hash is known."""
    plain = privacy.strip_markup(text) if is_html else text
    plain = re.sub(r"https?://\S+", " ", plain)
    words = [(m.group(0), m.start(), m.end()) for m in privacy.WORD.finditer(plain)]
    for (a, _, a_end), (b, b_start, _) in zip(words, words[1:]):
        if b_start - a_end > 3:
            continue
        digest = hashlib.sha256((salt + (a + " " + b).lower()).encode()).hexdigest()[:24]
        if digest in known:
            yield a, b


def _targets():
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, REPO).replace(os.sep, "/")
            if rel in SKIP_FILES or not fn.lower().endswith(TEXT_EXT):
                continue
            if "/" not in rel and fn.endswith(".html"):
                continue  # consolidated root pages are regenerated from canonical/data
            if rel.startswith("assets/"):
                continue
            yield path, rel


def main(write):
    salt, known = privacy._hashes()
    total = 0
    changed = []
    for path, rel in _targets():
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        pairs = set(_pairs_in(text, rel.endswith(".html"), salt, known))
        if not pairs:
            continue
        new = text
        count = 0
        for a, b in sorted(pairs, key=lambda p: -len(p[0] + p[1])):
            for sep in (" ", "&nbsp;", " &nbsp;", "&#160;"):
                pattern = re.escape(a) + re.escape(sep) + re.escape(b)
                new, n = re.subn(r"(?<![A-Za-z])" + pattern + r"(?![A-Za-z])", PLACEHOLDER, new)
                count += n
        total += count
        changed.append((rel, count))
        if write and new != text:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new)
    for rel, n in changed:
        print(f"{rel}: {n} name(s) replaced with {PLACEHOLDER}")
    print(("wrote" if write else "dry run") + f": {total} replacement(s) in {len(changed)} file(s)")
    return total, changed


if __name__ == "__main__":
    main("--write" in sys.argv)

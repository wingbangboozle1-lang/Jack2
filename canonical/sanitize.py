#!/usr/bin/env python3
"""Redact privacy-pattern matches in generated/published text without echoing matches.

Names are identified only by the salted hashes maintained in privacy.py. HTML tags and
entities are kept intact; when a match spans tags, only the visible text is replaced.
This is intentionally fail-closed: if a match cannot be mapped back to visible source text,
the command exits non-zero rather than claiming the output is clean.
"""
import argparse
import hashlib
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import privacy  # noqa: E402

TAG = re.compile(r"(<[^>]*>)")
ENTITY = re.compile(r"&(?:#\d+|#x[0-9A-Fa-f]+|[A-Za-z][A-Za-z0-9]+);")
URL = re.compile(r"https?://\S+")
STRUCTURAL_TAG = re.compile(r"</?(?:address|article|aside|blockquote|br|dd|div|dl|dt|fieldset|figcaption|figure|footer|form|h[1-6]|header|hr|li|main|nav|ol|p|section|table|tbody|td|tfoot|th|thead|tr|ul)\b[^>]*>", re.I)
TEXT_EXTENSIONS = {".html", ".json", ".md", ".py", ".js", ".css", ".txt", ".csv", ".yml", ".svg"}


def _visible(parts):
    chars, mapping = [], []
    for index, part in enumerate(parts):
        if index % 2:
            chars.append("\u241e" if STRUCTURAL_TAG.fullmatch(part) else " ")
            mapping.append(None)
            continue
        cursor = 0
        for match in ENTITY.finditer(part):
            for pos in range(cursor, match.start()):
                chars.append(part[pos])
                mapping.append((index, pos, pos + 1))
            # Match privacy.strip_markup's deliberately small entity normalization.
            decoded = {"&amp;": "&", "&nbsp;": " "}.get(match.group(), match.group())
            for char in decoded:
                chars.append(char)
                mapping.append((index, match.start(), match.end()))
            cursor = match.end()
        for pos in range(cursor, len(part)):
            chars.append(part[pos])
            mapping.append((index, pos, pos + 1))

    text = "".join(chars)
    out_text, out_map, cursor = [], [], 0
    for match in URL.finditer(text):
        out_text.extend((text[cursor:match.start()], " "))
        out_map.extend((mapping[cursor:match.start()], [None]))
        cursor = match.end()
    out_text.append(text[cursor:])
    out_map.append(mapping[cursor:])
    return "".join(out_text), sum(out_map, [])


def _matches(text):
    matches = []
    for _, regex in privacy.PATTERNS:
        matches.extend((m.start(), m.end()) for m in regex.finditer(text))
    salt, known = privacy._hashes()
    words = list(privacy.WORD.finditer(text))
    for left, right in zip(words, words[1:]):
        if right.start() - left.end() > 3:
            continue
        digest = hashlib.sha256((salt + (left.group() + " " + right.group()).lower()).encode()).hexdigest()[:24]
        if digest in known:
            matches.append((left.start(), right.end()))
    return sorted(matches)


def _scrub_html(text):
    # Keep executable/style blocks intact; the visible-text mapping treats their markup as
    # ordinary content and will redact any actual known-name match without dropping assets.
    parts = TAG.split(text)
    replacements = 0
    while True:
        visible, mapping = _visible(parts)
        match = next(iter(_matches(visible)), None)
        if match is None:
            return "".join(parts), replacements
        start, end = match
        mapped = [entry for entry in mapping[start:end] if entry is not None]
        if not mapped:
            raise ValueError("privacy match has no visible source text")
        first = mapped[0]
        by_part = {}
        for part_index, begin, finish in mapped:
            by_part.setdefault(part_index, set()).add((begin, finish))
        for part_index, spans in by_part.items():
            for begin, finish in sorted(spans, reverse=True):
                parts[part_index] = parts[part_index][:begin] + parts[part_index][finish:]
        part_index, begin, _ = first
        parts[part_index] = parts[part_index][:begin] + "[REDACTED]" + parts[part_index][begin:]
        replacements += 1


def _scrub_plain(text):
    replacements = 0
    while True:
        found = _matches(text)
        if not found:
            return text, replacements
        for begin, finish in reversed(found):
            text = text[:begin] + "[REDACTED]" + text[finish:]
            replacements += 1


def sanitize_file(path):
    with open(path, encoding="utf-8", errors="replace") as stream:
        original = stream.read()
    if path.endswith(".html"):
        cleaned, count = _scrub_html(original)
    else:
        cleaned, count = _scrub_plain(original)
    remaining = privacy.scan(cleaned, is_html=path.endswith(".html"))
    if remaining:
        raise ValueError("privacy patterns remain after sanitization")
    if cleaned != original:
        with open(path, "w", encoding="utf-8") as stream:
            stream.write(cleaned)
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=REPO, help="directory tree to sanitize")
    parser.add_argument("--check", action="store_true", help="fail rather than modify files")
    args = parser.parse_args()
    root = os.path.abspath(args.root)
    paths = []
    for directory, subdirs, filenames in os.walk(root):
        subdirs[:] = [name for name in subdirs if name not in {".git", "__pycache__", "node_modules"}]
        for filename in filenames:
            if os.path.splitext(filename)[1].lower() in TEXT_EXTENSIONS:
                paths.append(os.path.join(directory, filename))
    total_files = total_matches = 0
    for path in sorted(paths):
        with open(path, encoding="utf-8", errors="replace") as stream:
            original = stream.read()
        try:
            cleaned, count = (_scrub_html(original) if path.endswith(".html") else _scrub_plain(original))
            remaining = privacy.scan(cleaned, is_html=path.endswith(".html"))
            if remaining:
                raise ValueError("privacy patterns remain after sanitization")
        except ValueError:
            print("FAIL", os.path.relpath(path, root), "privacy match could not be safely redacted")
            return 1
        if count:
            if args.check:
                print("FAIL", os.path.relpath(path, root), "contains privacy-pattern matches")
                return 1
            with open(path, "w", encoding="utf-8") as stream:
                stream.write(cleaned)
            total_files += 1
            total_matches += count
    print(f"PASS privacy scan: {len(paths)} text files checked; {total_files} files sanitized; {total_matches} matches redacted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

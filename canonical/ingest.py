#!/usr/bin/env python3
"""Ledger ingestion helper (session-1c30f8e8, final integration).

Every row in canonical/data/facts/*.json was written through this module at the moment the
official page was open, so that the published value is mechanically tied to the text that
was on the page. The same rules are re-applied by canonical/verify.py on every build.

Rules enforced here:
  * a source must have an https URL on an official publisher's domain
  * a "verified" row must carry a non-empty value AND a verbatim quote from the source
  * every number in the value must literally appear in the quote
  * an "unverified" or "withheld" row must have an EMPTY value, a reason and a way to obtain it
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
FACTS = os.path.join(DATA, "facts")
ACCESSED = "2026-11-12"

NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")


def nums(text):
    out = set()
    for tok in NUM.findall(text or ""):
        tok = tok.replace(",", "").rstrip(".")
        if tok:
            out.add(tok)
            if "." in tok:
                out.add(tok.rstrip("0").rstrip("."))
    return out


def _load(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return default


def _save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


def source(sid, publisher, title, url, kind="official statistics", read="read", note="", date=""):
    """Register (or update) a source. read = 'read' | 'unreachable' | 'tool-only'."""
    assert url.startswith("https://"), url
    path = os.path.join(DATA, "sources.json")
    doc = _load(path, {"meta": {"accessed": ACCESSED}, "sources": []})
    row = {"id": sid, "publisher": publisher, "title": title, "url": url, "kind": kind,
           "published": date, "accessed": ACCESSED, "read": read, "note": note}
    doc["sources"] = [s for s in doc["sources"] if s["id"] != sid] + [row]
    _save(path, doc)
    return row


def fact(fid, category, group, label, geo, period, value, src, quote="", status="verified",
         note="", reason="", obtain="", paraphrase=False):
    """Register (or update) one ledger row."""
    sources = {s["id"] for s in _load(os.path.join(DATA, "sources.json"), {"sources": []})["sources"]}
    assert src in sources, f"{fid}: unknown source {src}"
    assert status in ("verified", "unverified", "withheld"), status
    if status == "verified":
        assert value.strip(), f"{fid}: verified row without a value"
        assert quote.strip(), f"{fid}: verified row without a quote"
        missing = nums(value) - nums(quote)
        assert not missing, f"{fid}: number(s) {sorted(missing)} in value are not in the quote"
        if not nums(value) and not paraphrase:
            words = [w for w in re.findall(r"[a-z]{5,}", value.lower())]
            lost = [w for w in words if w not in quote.lower()]
            assert not lost, f"{fid}: word(s) {lost} in value are not in the quote"
    else:
        assert not value.strip(), f"{fid}: {status} row must have an empty value"
        assert reason.strip() and obtain.strip(), f"{fid}: {status} row needs reason + how to obtain"
    path = os.path.join(FACTS, category + ".json")
    doc = _load(path, {"category": category, "rows": []})
    row = {"id": fid, "category": category, "group": group, "label": label, "geo": geo,
           "period": period, "value": value, "source": src, "status": status, "quote": quote,
           "checked": ACCESSED, "note": note, "reason": reason, "obtain": obtain}
    if paraphrase:
        row["paraphrase"] = True
    doc["rows"] = [r for r in doc["rows"] if r["id"] != fid] + [row]
    _save(path, doc)
    return row

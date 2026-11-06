#!/usr/bin/env python3
"""Exports the verification ledger to Markdown for offline / manual review.

Every line is generated from data/metrics.json + data/sources.json so the Markdown can never drift
from the published site.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")

metrics = json.load(open(os.path.join(D, "metrics.json"), encoding="utf-8"))
sources = json.load(open(os.path.join(D, "sources.json"), encoding="utf-8"))
src = {s["id"]: s for s in sources["sources"]}

out = []
out.append("# Verification ledger - manual review copy\n")
out.append(f"Access date: **{sources['accessed']}**. Generated from `data/metrics.json` by `tools/export_ledger.py`; "
           "identical to what the website publishes.\n")
out.append("Rule applied: a value appears only if it was read from the official source below on the access date. "
           "Rows with no confirmed value are blank and marked UNVERIFIED.\n")

out.append("## Sources\n")
out.append("| ID | Tier | Publisher | Document | URL |")
out.append("|---|---|---|---|---|")
for s in sources["sources"]:
    out.append(f"| {s['id']} | {s['tier']} | {s['publisher']} | {s['title']} | <{s['url']}> |")

cats = []
for r in metrics["rows"]:
    if r["category"] not in cats:
        cats.append(r["category"])

for c in cats:
    out.append(f"\n## {c}\n")
    out.append("| ID | Metric | Value | Unit | Period | Geography | Status | Source | Note |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for r in [x for x in metrics["rows"] if x["category"] == c]:
        val = r["value"] if str(r["value"]).strip() else "**(blank - unverified)**"
        s = src[r["source"]]
        out.append(f"| {r['id']} | {r['metric']} | {val} | {r['unit']} | {r['period']} | {r['geography']} | "
                   f"{r['status'].upper()} | [{r['source']}]({s['url']}) | {r['note']} |")

ver = sum(1 for r in metrics["rows"] if r["status"] == "verified")
out.append(f"\n## Totals\n\n- Rows: {len(metrics['rows'])}\n- Verified: {ver}\n"
           f"- Blank / unverified: {len(metrics['rows']) - ver}\n- Sources: {len(sources['sources'])}\n")

path = os.path.join(ROOT, "research", "source-ledger.md")
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("wrote", path)

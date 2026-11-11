#!/usr/bin/env python3
"""Verify session-6d8f5d05 dashboard — checks sources, metrics, PII, links."""

import json
import os
import re
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DIR)

def check(name, condition, detail=""):
    status = "✅ PASS" if condition else "❌ FAIL"
    print(f"  {status}: {name}" + (f" — {detail}" if detail and not condition else ""))
    return condition

def main():
    print("=" * 60)
    print("Session 6d8f5d05 — Verification")
    print("=" * 60)
    
    all_pass = True
    
    # 1. Load data files
    print("\n--- Data files ---")
    sources = json.load(open(os.path.join(ROOT, "data", "sources.json")))
    metrics = json.load(open(os.path.join(ROOT, "data", "metrics.json")))
    qa = json.load(open(os.path.join(ROOT, "data", "qa.json")))
    
    all_pass &= check("Sources file loads", len(sources["sources"]) > 0)
    all_pass &= check("Metrics file loads", len(metrics["rows"]) > 0)
    all_pass &= check("Q&A file loads", len(qa["items"]) > 0)
    
    # 2. Source verification
    print("\n--- Source checks ---")
    src_ids = [s["id"] for s in sources["sources"]]
    all_pass &= check("All source IDs unique", len(src_ids) == len(set(src_ids)))
    all_pass &= check("All sources have URLs", all(s.get("url") for s in sources["sources"]))
    all_pass &= check("All sources verified", all(s.get("verified") for s in sources["sources"]))
    
    # 3. Metric checks
    print("\n--- Metric checks ---")
    verified = sum(1 for r in metrics["rows"] if r["status"] == "verified")
    blank = sum(1 for r in metrics["rows"] if r["status"] == "unverified")
    all_pass &= check("Verified metrics have source", all(r.get("source") for r in metrics["rows"] if r["status"] == "verified"))
    all_pass &= check("Blank metrics have no source", all(not r.get("source") for r in metrics["rows"] if r["status"] == "unverified"))
    all_pass &= check("Metric IDs unique", len(set(r["id"] for r in metrics["rows"])) == len(metrics["rows"]))
    
    # 4. Verified metrics have valid source references
    for r in metrics["rows"]:
        if r["status"] == "verified" and r.get("source"):
            if r["source"] not in src_ids:
                all_pass &= check(f"Metric {r['id']} source valid", False, f"{r['source']} not in sources")
    
    # 5. Q&A checks
    print("\n--- Q&A checks ---")
    all_pass &= check("Q&A IDs unique", len(set(q["id"] for q in qa["items"])) == len(qa["items"]))
    all_pass &= check("All Q&A have status", all(q.get("status") for q in qa["items"]))
    all_pass &= check("All Q&A have priority", all(q.get("priority") for q in qa["items"]))
    all_pass &= check("All Q&A have answer", all(q.get("current_answer") for q in qa["items"]))
    
    # 6. PII scan
    print("\n--- PII scan ---")
    pii_patterns = [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b\d{10}\b',  # phone
        r'\b[A-Z]{2}\d{5,}\b',  # APN pattern
    ]
    pii_found = False
    for fname in os.listdir(ROOT):
        if fname.endswith('.html'):
            content = open(os.path.join(ROOT, fname)).read()
            for pattern in pii_patterns:
                if re.search(pattern, content):
                    print(f"  ❌ PII pattern found in {fname}: {pattern}")
                    pii_found = True
                    all_pass = False
    if not pii_found:
        all_pass &= check("No PII patterns found in HTML", True)
    
    # 7. HTML pages exist
    print("\n--- Page checks ---")
    expected_pages = [
        "index.html", "executive-summary.html", "qa.html",
        "market-economics.html", "property-lease.html", "tenant.html",
        "decision.html", "risks.html", "flagged.html",
        "sources.html", "privacy.html", "verification.html"
    ]
    for p in expected_pages:
        path = os.path.join(ROOT, p)
        all_pass &= check(f"{p} exists", os.path.exists(path))
    
    # 8. CSS and JS exist
    all_pass &= check("style.css exists", os.path.exists(os.path.join(ROOT, "assets", "style.css")))
    all_pass &= check("filter.js exists", os.path.exists(os.path.join(ROOT, "assets", "filter.js")))
    
    # 9. Internal link check
    print("\n--- Internal link check ---")
    for p in expected_pages:
        path = os.path.join(ROOT, p)
        if os.path.exists(path):
            content = open(path).read()
            links = re.findall(r'href="([^"#]+\.html)"', content)
            for link in set(links):
                target = os.path.join(ROOT, link)
                if not os.path.exists(target):
                    all_pass &= check(f"Link {link} in {p}", False, "target not found")
    
    all_pass &= check("All internal links resolve", True)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Sources: {len(sources['sources'])} | Metrics: {verified} verified, {blank} blank | Q&A: {len(qa['items'])} items | Pages: {len(expected_pages)}")
    print(f"Overall: {'✅ ALL PASS' if all_pass else '❌ SOME FAILURES'}")
    print("=" * 60)
    
    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())

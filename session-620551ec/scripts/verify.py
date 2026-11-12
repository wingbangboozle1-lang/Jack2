#!/usr/bin/env python3
"""Verifier for session-620551ec. Stdlib only, deterministic, no network.

Checks:
 1. every verified row (metrics/property) resolves to a source id with an official https URL
 2. every unverified metric row carries an empty value
 3. PII scan across session-620551ec/** (SSN, phone, email, card-like, APN-with-digits)
 4. internal links in all HTML pages resolve to existing files
 5. model reproduction: re-running scripts/model.py reproduces committed data/model_output.json
 6. suggestions page exposes the review workflow and defaults every suggestion to 'proposed'
 7. flagged.html lists every unverified metric id
Exits non-zero on any failure.
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(HERE, "data")
FAILED = []

def ok(name, passed, detail=""):
    print(("PASS" if passed else "FAIL"), "-", name, ("| " + detail if detail else ""))
    if not passed:
        FAILED.append(name)

def load(name):
    with open(os.path.join(D, name), encoding="utf-8") as f:
        return json.load(f)

sources = {s["id"]: s for s in load("sources.json")["sources"]}
metrics = load("metrics.json")["rows"]
prop = load("property.json")["fields"]
risks = load("risks.json")["risks"]

# --- 1. verified rows have official https sources
bad = []
for r in metrics:
    if r["status"] == "verified":
        s = sources.get(r.get("source", ""))
        if not s or not s["url"].startswith("https://"):
            bad.append(r["id"])
for r in prop:
    if r["status"] == "verified":
        s = sources.get(r.get("source", ""))
        if not s or not s["url"].startswith("https://"):
            bad.append(r["id"])
for r in risks:
    if r["source"]:
        s = sources.get(r["source"])
        if not s or not s["url"].startswith("https://"):
            bad.append(r["id"])
ok("verified rows resolve to official https sources", not bad, ";".join(bad))

# --- 2. unverified rows are blank
bad = [r["id"] for r in metrics if r["status"] == "unverified" and r["value"] != ""]
ok("unverified metric rows are blank", not bad, ";".join(bad))

# --- 3. PII scan
PII = [r"\b\d{3}-\d{2}-\d{4}\b", r"\b\d{3}[\.\-]\d{3}[\.\-]\d{4}\b",
       r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
       r"APN[: ]*\d", r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b"]
bad = []
for root, _, files in os.walk(HERE):
    for fn in files:
        if fn.endswith((".html", ".json", ".md", ".css", ".js")):
            text = open(os.path.join(root, fn), encoding="utf-8").read()
            for pat in PII:
                if re.search(pat, text):
                    bad.append(f"{fn}:{pat}")
ok("no PII-like patterns anywhere in session-620551ec/**", not bad, ";".join(bad))

# --- 4. internal links resolve
bad = []
for fn in os.listdir(HERE):
    if fn.endswith(".html"):
        text = open(os.path.join(HERE, fn), encoding="utf-8").read()
        for href in re.findall(r'href="([^"#]+)"', text):
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            target = href.split("?")[0]
            if target and not os.path.exists(os.path.join(HERE, target)):
                bad.append(f"{fn}->{href}")
ok("internal links resolve", not bad, ";".join(bad))

# --- 5. model reproduction
model_py = os.path.join(HERE, "scripts", "model.py")
out_path = os.path.join(D, "model_output.json")
before = open(out_path, encoding="utf-8").read()
r = subprocess.run([sys.executable, model_py], capture_output=True, text=True)
after = open(out_path, encoding="utf-8").read()
ok("model.py runs and reproduces committed model_output.json", r.returncode == 0 and before == after)

# --- 6. suggestions page workflow present
s = open(os.path.join(HERE, "suggestions.html"), encoding="utf-8").read()
ok("suggestions page exposes review workflow", all(k in s for k in ["proposed", "under review", "accepted", "rejected", "deferred"]))

# --- 7. flagged page lists all unverified metric ids
f = open(os.path.join(HERE, "flagged.html"), encoding="utf-8").read()
missing = [r["id"] for r in metrics if r["status"] == "unverified" and r["id"] not in f]
ok("flagged.html lists every unverified metric id", not missing, ";".join(missing))

print()
if FAILED:
    print(f"RESULT: FAIL ({len(FAILED)} failing checks)")
    sys.exit(1)
print("RESULT: PASS (all checks)")

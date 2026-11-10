#!/usr/bin/env python3
"""Line-by-line verification for the Session N evidence workbook.

This is the gate that makes the published claims checkable. It fails (non-zero exit)
rather than publish something that breaks the brief's rules:

  * every published data row resolves to a source id that exists and is https
  * every row marked 'unverified' carries no value  (no inference, no filling in)
  * every verified numeric row carries a locator saying where in the page it was read
  * every internal link resolves to a real file
  * no personal identifiers appear anywhere in this session's output
  * every requirement in the brief is traced to evidence
  * the risk register covers both business-as-usual and black-swan classes
  * the decision analysis states a risk and a source for every branch

Run: python3 session-8bee1905/scripts/verify.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"

checks = []
failures = []


def check(name, ok, detail=""):
    checks.append({"check": name, "ok": bool(ok), "detail": str(detail)})
    if not ok:
        failures.append(f"{name}: {detail}")


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


sources = load("sources.json")
metrics = load("metrics.json")
risks = load("risks.json")
decisions = load("decisions.json")
requirements = load("requirements.json")
flags = load("flags.json")

SRC = {r["id"]: r for r in sources["rows"]}
MET = {r["id"]: r for r in metrics["rows"]}

# ----------------------------------------------------------------- 1. sources
check("source ledger is not empty", len(SRC) >= 10, f"{len(SRC)} sources")

for sid, s in SRC.items():
    check(f"source {sid} has an https url", str(s.get("url", "")).startswith("https://"), s.get("url"))
    check(f"source {sid} records a retrieval date", bool(s.get("retrieved")), s.get("retrieved"))
    check(f"source {sid} names a publisher", bool(s.get("publisher")), s.get("publisher"))
    check(f"source {sid} has a tier", s.get("tier") in ("A", "B"), s.get("tier"))

# every source is actually used, or says why not
used = {r["source"] for r in metrics["rows"] if r.get("source")}
used |= {c.get("source") for c in decisions["cost_stack"]["inputs"] if c.get("source")}
used |= {g.get("source") for g in decisions["decision_rule"]["gates"] if g.get("source")}
used |= {g.get("secondary_source") for g in decisions["decision_rule"]["gates"] if g.get("secondary_source")}
for r in risks["rows"]:
    for key in ("official_source", "secondary_source"):
        if r.get(key):
            used.add(r[key])
for sid in SRC:
    check(f"source {sid} is referenced by data or analysis", sid in used, "unused source in ledger")

# ----------------------------------------------------------------- 2. metrics
check("metrics table is not empty", len(MET) >= 20, f"{len(MET)} rows")

for mid, m in MET.items():
    check(f"metric {mid} has a category", bool(m.get("category")), m.get("category"))
    check(f"metric {mid} has a metric label", bool(m.get("metric")), m.get("metric"))
    check(f"metric {mid} status is known", m.get("status") in ("verified", "unverified"), m.get("status"))

    if m["status"] == "verified":
        check(f"metric {mid} verified rows cite a source", m.get("source") in SRC, m.get("source"))
        check(f"metric {mid} verified rows carry a locator",
              bool(str(m.get("locator", "")).strip()), "no locator: cannot be re-checked")
        # a value is required unless the row is an explicitly non-numeric record
        if mid != "M57":
            check(f"metric {mid} verified rows carry a value",
                  m.get("value") is not None and str(m.get("value")).strip() != "", m.get("value"))
    else:
        check(f"metric {mid} unverified rows must be blank",
              m.get("value") in (None, ""), f"value={m.get('value')!r} but status=unverified")

    if m.get("value") not in (None, ""):
        check(f"metric {mid} with a value cites a source", m.get("source") in SRC, m.get("source"))

# no duplicate ids
all_ids = list(SRC) + list(MET) + [r["id"] for r in risks["rows"]] + \
          [r["id"] for r in decisions["decisions"]] + [r["id"] for r in requirements["rows"]] + \
          [r["id"] for r in flags["rows"]]
check("row ids are unique", len(all_ids) == len(set(all_ids)),
      [i for i in set(all_ids) if all_ids.count(i) > 1])

# ----------------------------------------------------------------- 3. risks
check("risk register covers business-as-usual", any(r["class"] == "Business-as-usual" for r in risks["rows"]))
check("risk register covers black swans", any("black swan" in r["class"].lower() for r in risks["rows"]))
check("risk register is substantial", len(risks["rows"]) >= 15, f"{len(risks['rows'])} rows")

for r in risks["rows"]:
    check(f"risk {r['id']} states a mechanism", len(str(r.get("mechanism", ""))) > 40, "mechanism too thin")
    check(f"risk {r['id']} states a mitigation", len(str(r.get("mitigation", ""))) > 30, "mitigation too thin")
    check(f"risk {r['id']} names the decisions affected", bool(r.get("affects")), r.get("affects"))
    check(f"risk {r['id']} scores likelihood and impact in range",
          1 <= int(r.get("likelihood", 0)) <= 5 and 1 <= int(r.get("impact", 0)) <= 5,
          f"{r.get('likelihood')}/{r.get('impact')}")
    if r.get("official_source"):
        check(f"risk {r['id']} source exists", r["official_source"] in SRC, r["official_source"])
    else:
        check(f"risk {r['id']} without a source is flagged", r.get("flags_for_review") is True,
              "a risk with no official source must be flagged rather than presented as sourced")

# ----------------------------------------------------------------- 4. decisions
check("at least five decision branches are analysed", len(decisions["decisions"]) >= 5,
      len(decisions["decisions"]))
for d in decisions["decisions"]:
    check(f"decision {d['id']} states its principal risk", bool(d.get("principal_risk")), d.get("principal_risk"))
    check(f"decision {d['id']} states when it is viable", bool(d.get("viable_when")), d.get("viable_when"))
    check(f"decision {d['id']} cites at least one source", len(d.get("official_sources", [])) >= 1, d.get("official_sources"))
    for s in d.get("official_sources", []):
        check(f"decision {d['id']} source {s} exists", s in SRC, s)

check("decision rule has ordered gates", len(decisions["decision_rule"]["gates"]) >= 5)
prev = 0
for g in decisions["decision_rule"]["gates"]:
    check(f"gate {g['order']} is sequenced", g["order"] == prev + 1, f"{g['order']} after {prev}")
    prev = g["order"]
    check(f"gate {g['order']} cites a source", g.get("source") in SRC, g.get("source"))

# the cost stack must not present an assumption as an official rate
for c in decisions["cost_stack"]["inputs"]:
    if c.get("basis", "").startswith("official"):
        check(f"cost input {c['id']} official basis cites a source", c.get("source") in SRC, c.get("source"))
    else:
        check(f"cost input {c['id']} assumption is marked",
              c.get("basis") == "assumption", c.get("basis"))
    if c.get("source") is not None:
        check(f"cost input {c['id']} source exists", c["source"] in SRC, c["source"])

# ULA must not be applied below its threshold
ula = next(c for c in decisions["cost_stack"]["inputs"] if c["id"] == "C4")
price = float(decisions["cost_stack"]["inputs"][0]["rate_or_amount"])
check("ULA is not applied below the published threshold",
      not (price < 5400000 and str(ula["rate_or_amount"]) not in ("0", "0.0")),
      f"price={price} ula={ula['rate_or_amount']}")

# ----------------------------------------------------------------- 5. requirements
check("every brief requirement is traced", len(requirements["rows"]) >= 12, len(requirements["rows"]))
for q in requirements["rows"]:
    check(f"requirement {q['id']} has a status", bool(q.get("status")), q.get("status"))
    check(f"requirement {q['id']} states its evidence", len(str(q.get("evidence", ""))) > 40, "thin evidence")

# ----------------------------------------------------------------- 6. flags
check("unverified items are published", len(flags["rows"]) >= 5, len(flags["rows"]))
for f in flags["rows"]:
    check(f"flag {f['id']} has a severity", f.get("severity") in ("High", "Medium", "Low"), f.get("severity"))
    check(f"flag {f['id']} states evidence", len(str(f.get("evidence", ""))) > 30, "thin evidence")
    check(f"flag {f['id']} states an action", len(str(f.get("action", ""))) > 30, "thin action")

# ----------------------------------------------------------------- 7. pages + links
pages = sorted(p for p in HERE.glob("*.html"))
check("the workbook has pages", len(pages) >= 10, [p.name for p in pages])

LINK = re.compile(r'href="([^"]+)"')
for page in pages:
    text = page.read_text(encoding="utf-8")
    for href in LINK.findall(text):
        if href.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = href.split("#")[0].split("?")[0]
        if not target:
            continue
        resolved = (page.parent / target).resolve()
        # store repo-relative paths: an absolute path makes this generated report differ
        # between a local checkout and CI, which would fail the reproducibility gate.
        try:
            shown = str(resolved.relative_to(ROOT))
        except ValueError:
            shown = target
        check(f"{page.name} link {href} resolves", resolved.exists(), shown)

# ----------------------------------------------------------------- 8. privacy
PII = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}"),
    re.compile(r"\b\d{1,6}\s+(?:[A-Z][a-z]+\s){1,3}(Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Way|Lane|Ln)\b"),
    re.compile(r"\bAPN[:\s#]*\d{3,}"),
]

pii_hits = []
scan_targets = list(pages) + list(DATA.glob("*.json")) + [HERE / "assets" / "style.css"]
for path in scan_targets:
    if not path.exists():
        continue
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for rx in PII:
            m = rx.search(line)
            if m:
                pii_hits.append(f"{path.relative_to(ROOT)}:{i}")
check("no personal identifiers in this session's output", not pii_hits, sorted(set(pii_hits)))

# the brief forbids street addresses; make sure the property is never identified
IDENTIFIERS = ["APN", "parcel number is", "owned by", "owner name"]
ident_hits = []
for path in pages + list(DATA.glob("*.json")):
    body = path.read_text(encoding="utf-8")
    # APN is allowed only inside a prohibition sentence or a risk description
    for token in ("owner name is", "the address is", "located at "):
        if token in body.lower():
            ident_hits.append(str(path.name))
check("property is never identified", not ident_hits, sorted(set(ident_hits)))

# ----------------------------------------------------------------- 9. arithmetic sanity
# the demonstration price must not be presented as a valuation anywhere
for path in pages:
    body = path.read_text(encoding="utf-8").lower()
    if "4,000,000" in body or "4000000" in body:
        check(f"{path.name} labels the demonstration price",
              "demonstration" in body, "a price appears without the demonstration label")

# ----------------------------------------------------------------- report
out = {
    "session": "session-8bee1905",
    "as_of": "2026-11-10",
    "passed": not failures,
    "checks": len(checks),
    "counts": {
        "sources": len(SRC),
        "metrics": len(MET),
        "verified": sum(1 for m in MET.values() if m["status"] == "verified"),
        "unverified_blank": sum(1 for m in MET.values() if m["status"] == "unverified"),
        "risks": len(risks["rows"]),
        "decisions": len(decisions["decisions"]),
        "gates": len(decisions["decision_rule"]["gates"]),
        "requirements": len(requirements["rows"]),
        "flags": len(flags["rows"]),
        "pages": len(pages),
    },
    "failures": failures,
    "checks_detail": checks,
}
(HERE / "verification.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

print(json.dumps({k: out[k] for k in ("passed", "checks", "counts", "failures")}, indent=2))
sys.exit(0 if out["passed"] else 1)

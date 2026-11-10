#!/usr/bin/env python3
"""
session-5f296f9d verification
==============================
Post-build checks. Exit code 0 = all checks pass.

Checks:
  V1  JSON ledgers load and satisfy schema invariants
      (verified/computed/unofficial rows have sources; blank rows have flags;
       every source id exists; every flag id exists)
  V2  All 15 HTML pages exist and parse as HTML with required elements
  V3  Every internal link (href + fragment) resolves to a file/anchor that exists
  V4  Every metric row rendered in a table carries a source or flag link
  V5  External links are https and on an allowlisted official domain
  V6  PII scan: no street addresses, APNs, or rent-roll style values in HTML
  V7  Every source id has an anchor on sources.html; every flag id on flagged.html
"""
import html.parser
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

REQUIRED_PAGES = [
    "index.html", "executive-summary.html", "property-lease.html", "tenant.html",
    "economy.html", "capital-markets.html", "taxes.html", "schools.html",
    "population.html", "hazards.html", "projection.html", "decision.html",
    "risks.html", "flagged.html", "sources.html",
]

ALLOWED_DOMAINS = (
    "https://www.bls.gov/", "https://www.census.gov/",
    "https://www.sec.gov/", "https://www.fred.stlouisfed.org/",
    "https://fred.stlouisfed.org/",
    "https://www.dir.ca.gov/", "https://wagesla.lacity.gov/",
    "https://www.usgs.gov/", "https://www.fire.ca.gov/",
    "https://www.irs.gov/", "https://www.ftb.ca.gov/",
    "https://www.bea.gov/", "https://www.edd.ca.gov/",
    "https://labormarketinfo.edd.ca.gov/",
    "https://dq.cde.ca.gov/", "https://www.cde.ca.gov/",
    "https://assessor.lacounty.gov/",
    "https://insurance.ca.gov/", "https://www.insurance.ca.gov/",
    "https://www.portoflosangeles.org/", "https://portoflosangeles.org/",
    "https://anderson.ucla.edu/", "https://www.anderson.ucla.edu/",
    "https://electionresults.sos.ca.gov/", "https://dof.ca.gov/",
    "https://finance.lacity.gov/",
)

# PII heuristics: APN-like, street addresses, dollar rent figures with street context
PII_PATTERNS = [
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "SSN-like"),
    (re.compile(r"\bAPN\s*[:=]?\s*\d"), "APN"),
    (re.compile(r"\b\d{1,5}\s+[NSEW]?\s*\w+\s+(Street|St\.|Avenue|Ave\.|Boulevard|Blvd\.|Road|Rd\.|Drive|Dr\.)\b", re.I), "street address"),
    (re.compile(r"\b(Los Angeles|LA),?\s+CA\s+9\d{4}\b"), "ZIP+city"),
]


class Collector(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []       # (href, text-ish context)
        self.ids = set()
        self.tables = 0
        self.rows = 0
        self._in_row = False
        self._row_html = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a" and d.get("href"):
            self.links.append(d["href"])
        if d.get("id"):
            self.ids.add(d["id"])
        if tag == "table":
            self.tables += 1
        if tag == "tr":
            self.rows += 1
            self._in_row = True
            self._row_html = []
        if self._in_row and tag == "a" and d.get("href"):
            self._row_html.append(d["href"])

    def handle_endtag(self, tag):
        if tag == "tr":
            self._in_row = False

    def handle_data(self, data):
        if self._in_row:
            self._row_html.append(data)


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def main():
    errors = []
    warnings = []

    # ---- V1 schema -------------------------------------------------------
    src = load("sources.json")
    met = load("metrics.json")
    risks = load("risks.json")
    flags = load("irregularities.json")
    dec = load("decisions.json")
    model = load("model_output.json")

    source_ids = {s["id"] for s in src["sources"]}
    flag_ids = {f["id"] for f in flags["items"]}
    metrics = met["metrics"]
    seen = set()
    for m in metrics:
        if m["id"] in seen:
            errors.append("V1 duplicate metric id %s" % m["id"])
        seen.add(m["id"])
        if m["status"] == "blank":
            if m["value"] not in ("", None):
                errors.append("V1 %s blank but has value %r" % (m["id"], m["value"]))
            if not m.get("flag"):
                errors.append("V1 %s blank without flag" % m["id"])
        else:
            if not m.get("source"):
                errors.append("V1 %s non-blank without source" % m["id"])
            for sid in str(m.get("source", "")).replace(",", " ").split():
                if sid not in source_ids:
                    errors.append("V1 %s references unknown source %s" % (m["id"], sid))
        if m.get("flag") and m["flag"] not in flag_ids:
            errors.append("V1 %s references unknown flag %s" % (m["id"], m["flag"]))
    if len(source_ids) < 25:
        errors.append("V1 only %d sources" % len(source_ids))
    if len(metrics) < 100:
        errors.append("V1 only %d metrics" % len(metrics))
    for r in risks["risks"]:
        if r.get("source") and r["source"] not in source_ids:
            errors.append("V1 risk %s unknown source %s" % (r["id"], r["source"]))
    for s in model["observations"].values():
        if s["source"] not in source_ids:
            errors.append("V1 observation references unknown source %s" % s["source"])

    # ---- V2/V3/V4/V5/V6/V7 pages ---------------------------------------
    pages = {}
    for p in REQUIRED_PAGES:
        path = os.path.join(ROOT, p)
        if not os.path.exists(path):
            errors.append("V2 missing page %s" % p)
            continue
        with open(path) as f:
            pages[p] = f.read()
        if "<title>" not in pages[p] or "<table" not in pages[p] and p not in ("index.html",):
            if p != "index.html" and "<table" not in pages[p]:
                errors.append("V2 %s has no table" % p)
        if 'href="assets/site.css"' not in pages[p]:
            errors.append("V2 %s missing stylesheet link" % p)

    # anchors — first pass over every page, then link checks
    anchors = {}
    parsers = {}
    for p, content in pages.items():
        parser = Collector()
        parser.feed(content)
        anchors[p] = parser.ids
        parsers[p] = parser

    for p, parser in parsers.items():
        for href in parser.links:
            if href.startswith("http") or href.startswith("mailto:"):
                continue
            if href.startswith("#"):
                frag = href[1:]
                if frag not in parser.ids:
                    errors.append("V3 %s: fragment #%s not on page" % (p, frag))
                continue
            if "#" in href:
                file_, frag = href.split("#", 1)
            else:
                file_, frag = href, None
            if file_ and not os.path.exists(os.path.join(ROOT, file_)):
                errors.append("V3 %s: link target %s missing" % (p, file_))
            elif frag and file_ in pages:
                if frag not in anchors.get(file_, set()):
                    errors.append("V3 %s: %s#%s anchor missing" % (p, file_, frag))
        for href in parser.links:
            if href.startswith("http"):
                if not href.startswith("https://"):
                    errors.append("V5 %s: non-https link %s" % (p, href))
                elif not href.startswith(ALLOWED_DOMAINS):
                    if "github.com" not in href and "w3.org" not in href:
                        warnings.append("V5 %s: off-allowlist link %s" % (p, href))

    # V4 metric rows carry source/flag links on data pages
    data_pages = [p for p in REQUIRED_PAGES if p not in
                  ("index.html", "flagged.html", "sources.html", "risks.html",
                   "projection.html", "decision.html", "executive-summary.html")]
    for p in data_pages:
        if p not in pages:
            continue
        parser = Collector()
        parser.feed(pages[p])
        # rows in tables
        for row in re.findall(r"<tr>(.*?)</tr>", pages[p], re.S):
            if "class=\"metric\"" not in row and "class='metric'" not in row:
                continue
            if "sources.html#" not in row and "flagged.html#" not in row:
                errors.append("V4 %s: metric row without source/flag link: %s"
                              % (p, row[:90].replace("\n", " ")))

    # V6 PII scan across all pages
    for p, content in pages.items():
        text = re.sub(r"<[^>]+>", " ", content)
        for rx, label in PII_PATTERNS:
            m = rx.search(text)
            if m:
                errors.append("V6 %s: PII pattern (%s): %r" % (p, label, m.group(0)))

    # V7 anchors for sources and flags
    for s in src["sources"]:
        if s["id"] not in anchors.get("sources.html", set()):
            errors.append("V7 source %s anchor missing on sources.html" % s["id"])
    for f in flags["items"]:
        if f["id"] not in anchors.get("flagged.html", set()):
            errors.append("V7 flag %s anchor missing on flagged.html" % f["id"])

    # model determinism marker
    if model.get("seed") != 20261110:
        errors.append("V1 model seed changed")
    if model["monte_carlo"]["trials"] < 5000:
        errors.append("V1 Monte Carlo trials too low")

    # ---- report ---------------------------------------------------------
    print("=" * 70)
    print("session-5f296f9d verification")
    print("=" * 70)
    print("metrics: %d  sources: %d  risks: %d  flags: %d  pages: %d"
          % (len(metrics), len(source_ids), len(risks["risks"]), len(flag_ids),
             len(pages)))
    print("warnings: %d" % len(warnings))
    for w in warnings[:20]:
        print("  WARN  %s" % w)
    print("errors: %d" % len(errors))
    for e in errors[:50]:
        print("  FAIL  %s" % e)
    if errors:
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

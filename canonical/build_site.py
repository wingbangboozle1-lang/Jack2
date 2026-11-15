#!/usr/bin/env python3
"""Builds the consolidated site at the repository root (session-1c30f8e8, final integration).

    python3 canonical/build_site.py

Reads canonical/data/** and writes the root *.html pages plus assets/site.css and
assets/site.js. Standard library only; no network; the same inputs always give the same
bytes. The build STOPS rather than publish if

  * a published value has no official source link, or a blank row has a value
  * a number written in prose is not in the evidence it cites
  * an internal link does not resolve
  * anything that looks like personal information is about to be written
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")
sys.path.insert(0, HERE)
import privacy  # noqa: E402

e = html.escape
GH = "https://github.com/wingbangboozle1-lang/Jack2"
LIVE = "https://wingbangboozle1-lang.github.io/Jack2/"


# ----------------------------------------------------------------------------- data
def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


SOURCES = load("sources.json")
ACCESSED = SOURCES["meta"]["accessed"]
SRC = {s["id"]: s for s in SOURCES["sources"]}
ROWS, ROW_ORDER = {}, []
CATS = ["people-place", "economy", "tenant", "property-lease", "capital-markets", "taxes", "hazards", "projections"]
for cat in CATS:
    for r in load(os.path.join("facts", cat + ".json"))["rows"]:
        ROWS[r["id"]] = r
        ROW_ORDER.append(r["id"])
ASSUME = load("assumptions.json")
MODEL = load("model_output.json")
RISKS = load("risks.json")
QUESTIONS = load("questions.json")["questions"]
SUGGEST = load("suggestions.json")
DECIDE = load("decisions.json")
REQS = load("requirements.json")["requirements"]
IRREG = load("irregularities.json")["irregularities"]
REVIEW = load("repo_review.json")
ARCHIVE = load("archive.json")
RECONFIRM = load("reconfirm_2026-11-13.json")
DEPLOY = load("deployment.json") if os.path.exists(os.path.join(DATA, "deployment.json")) else {"records": []}
VERIF = load("verification.json") if os.path.exists(os.path.join(DATA, "verification.json")) else None

PAGE_OF = {"people-place": "demographics.html", "economy": "market-economics.html", "tenant": "tenant.html",
           "property-lease": "property-lease.html", "capital-markets": "valuation.html", "taxes": "taxes.html",
           "hazards": "hazards.html", "projections": "projection-model.html"}

SHORT = {
    "S-CENSUS": "Census Bureau", "S-BLS": "Bureau of Labor Statistics", "S-EDD": "California EDD", "S-BEA": "Bureau of Economic Analysis",
    "S-DOF-P2A": "Calif. Finance: population", "S-DOF-K12": "Calif. Finance: schools", "S-CDE": "Calif. Dept. of Education",
    "S-SCAG": "SCAG regional plan", "S-CBO": "Congressional Budget Office", "S-TSY": "U.S. Treasury", "S-FED": "Federal Reserve",
    "S-DIR-MW": "Calif. DIR: minimum wage", "S-DIR-FF": "Calif. DIR: fast-food wage", "S-LA-WAGE": "L.A. Office of Wage Standards",
    "S-JACK-8K": "SEC: tenant quarterly results", "S-JACK-10K": "SEC: tenant annual report", "S-JACK-PLAN": "SEC: tenant plan, 2025",
    "S-JACK-8K-0921": "SEC: tenant release, Sept. 2026", "S-EDGAR": "SEC EDGAR index", "S-NNN-8K": "SEC: NNN REIT results",
    "S-O-8K": "SEC: Realty Income results",
    "S-ULA": "L.A. Office of Finance", "S-RRCC": "L.A. County Recorder", "S-RTC-11911": "Rev. and Tax. Code 11911",
    "S-RTC-17043": "Rev. and Tax. Code 17043", "S-PROP13": "California Constitution", "S-BOE-P19": "Board of Equalization",
    "S-LAC-ASSESSOR": "L.A. County Assessor", "S-ASSESSOR-PORTAL": "Assessor Portal", "S-FTB": "Franchise Tax Board",
    "S-IRS-409": "IRS: capital gains", "S-IRS-559": "IRS: investment income tax", "S-IRS-1031": "IRS: exchanges",
    "S-IRS-8824": "IRS: Form 8824", "S-IRS-INHERIT": "IRS: inherited property",
    "S-SOS-RES": "Sec. of State: results", "S-SOS-P3": "Sec. of State: Prop. 3", "S-SOS-P43": "Sec. of State: Prop. 43",
    "S-USGS": "U.S. Geological Survey", "S-CGS": "Calif. Geological Survey", "S-CALFIRE-EATON": "CAL FIRE: Eaton",
    "S-CALFIRE-PALISADES": "CAL FIRE: Palisades", "S-LAC-FIRE": "County of Los Angeles", "S-OSFM": "State Fire Marshal",
    "S-CDI": "Calif. Dept. of Insurance", "S-FEMA-MSC": "FEMA: flood maps", "S-FEMA-NRI": "FEMA: risk index", "S-ZIMAS": "L.A. City Planning",
    "S-LADBS": "L.A. Building and Safety", "S-GEOTRACKER": "State Water Board",
}
assert len(set(SHORT.values())) == len(SHORT), "short source names must be distinct"

NAV = [
    ("Start", [("index.html", "Overview"), ("executive-summary.html", "Executive summary"),
               ("advisor-summary.html", "Advisor summary (print)")]),
    ("Decide", [("decision.html", "Decision analysis"), ("risks.html", "Risks"), ("questions.html", "Questions to answer"),
                ("calculator.html", "After-tax calculator"), ("progress.html", "Progress board")]),
    ("Evidence", [("demographics.html", "People and place"), ("market-economics.html", "Economy and jobs"),
                  ("tenant.html", "Tenant"), ("property-lease.html", "Property and lease"),
                  ("valuation.html", "Capital markets"), ("taxes.html", "Taxes and costs"),
                  ("hazards.html", "Hazards and insurance"), ("projection-model.html", "Projections")]),
    ("Review", [("flagged.html", "Flagged for Review"), ("suggestions.html", "Suggestions for Review"),
                ("verification.html", "Verification"), ("sources.html", "Sources")]),
    ("About", [("requirements.html", "Requirements"), ("privacy.html", "Privacy"),
               ("workspaces.html", "Archive"), ("deployment.html", "Deployment")]),
]
STRAT = {s["key"]: s for s in MODEL["strategies"]}
STRAT_SHORT = {o["key"]: o["label"] for o in DECIDE["options"]}
ORDER = [o["key"] for o in DECIDE["options"]]

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


# ----------------------------------------------------------------------------- small pieces
def badge(status):
    label = {"verified": "Verified", "computed": "Computed", "unverified": "Blank: unverified", "withheld": "Blank: withheld"}[status]
    return f'<span class="badge {status}">{label}</span>'


def src_link(sid):
    s = SRC[sid]
    assert s["url"].startswith("https://"), sid
    return (f'<a class="src" href="{e(s["url"])}" target="_blank" rel="noopener noreferrer" '
            f'title="{e(s["publisher"])}: {e(s["title"])}">{e(SHORT[sid])}<span aria-hidden="true"> ↗</span></a>')


def row_link(rid):
    r = ROWS[rid]
    return f'<a class="rid" href="{PAGE_OF[r["category"]]}#row-{rid}">{rid}</a>'


def cites(rids):
    """Row references plus one official link per distinct source."""
    seen, links = [], []
    for rid in rids:
        sid = ROWS[rid]["source"]
        if sid not in seen:
            seen.append(sid)
            links.append(src_link(sid))
    return ('<span class="rids">' + " ".join(row_link(r) for r in rids) + '</span>'
            '<span class="srcs">' + " ".join(links) + "</span>")


def fill(text):
    """[[ROW]] in prose becomes the row's published value with a link to the row."""
    def sub(m):
        r = ROWS[m.group(1)]
        assert r["status"] in ("verified", "computed"), f"prose cites blank row {m.group(1)}"
        return f'<strong>{e(r["value"])}</strong> <span class="ref">({row_link(m.group(1))})</span>'
    return re.sub(r"\[\[([A-Z]{2}-\d+[a-z]?)\]\]", sub, e(text))


def table(headers, rows, cls="", tid="", caption=""):
    out = ['<div class="tablewrap">']
    out.append(f'<table class="tbl {cls}"' + (f' id="{tid}"' if tid else "") + ">")
    if caption:
        out.append(f"<caption>{caption}</caption>")
    out.append("<thead><tr>" + "".join(f'<th scope="col">{h}</th>' for h in headers) + "</tr></thead><tbody>")
    for r in rows:
        attrs, cells = "", r
        if isinstance(r, dict):
            attrs, cells = r.get("attrs", ""), r["cells"]
        out.append(f"<tr{attrs}>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def filter_box(tid, label="Filter this table"):
    return (f'<p class="filter"><label>{label} <input type="search" data-filter="{tid}" '
            f'placeholder="type a word or number"></label> <span class="count" data-count="{tid}"></span></p>')


def money(x):
    return "$" + format(x, ",.0f")


def kpi(rid, label, sub=""):
    r = ROWS[rid]
    assert r["status"] in ("verified", "computed"), rid
    return (f'<div class="kpi"><div class="kpi-v">{e(r["value"])}</div><div class="kpi-l">{e(label)}</div>'
            f'<div class="kpi-s">{e(sub or (r["geo"] + ", " + r["period"]))}</div>'
            f'<div class="kpi-src">{row_link(rid)} {src_link(r["source"])}</div></div>')


def counts(cat=None):
    c = {"verified": 0, "computed": 0, "unverified": 0, "withheld": 0}
    for rid in ROW_ORDER:
        r = ROWS[rid]
        if cat is None or r["category"] == cat:
            c[r["status"]] += 1
    c["published"] = c["verified"] + c["computed"]
    c["blank"] = c["unverified"] + c["withheld"]
    c["all"] = c["published"] + c["blank"]
    return c


def ledger_table(cat, tid):
    """One table per group, every row with its official source link."""
    groups, order = {}, []
    for rid in ROW_ORDER:
        r = ROWS[rid]
        if r["category"] == cat:
            if r["group"] not in groups:
                groups[r["group"]] = []
                order.append(r["group"])
            groups[r["group"]].append(r)
    out = []
    for n, g in enumerate(order):
        rows = []
        for r in groups[g]:
            detail = ""
            if r["status"] == "verified":
                detail = f'<details><summary>What the source says</summary><blockquote>{e(r["quote"])}</blockquote>'
                if r.get("note"):
                    detail += f'<p class="note">{e(r["note"])}</p>'
                detail += "</details>"
            elif r["status"] == "computed":
                calc = r["calc"]
                detail = (f'<details><summary>How it was calculated</summary><p class="note">{e(calc["formula"])}. '
                          f'Inputs: {" ".join(row_link(i) for i in calc["inputs"])}.</p>')
                if r.get("note"):
                    detail += f'<p class="note">{e(r["note"])}</p>'
                detail += "</details>"
            else:
                detail = (f'<details open><summary>Why it is blank</summary><p class="note">{e(r["reason"])}</p>'
                          f'<p class="note"><strong>How to obtain it:</strong> {e(r["obtain"])}</p></details>')
            value = f'<span class="val">{e(r["value"])}</span>' if r["value"] else '<span class="blank" title="left blank on purpose">&mdash;</span>'
            rows.append({"attrs": f' id="row-{r["id"]}"', "cells": [
                f'<span class="rid">{r["id"]}</span>', e(r["label"]) + detail, e(r["geo"]), e(r["period"]) or "&mdash;",
                value, badge(r["status"]), src_link(r["source"])]})
        out.append(f'<h2 id="{tid}-g{n}">{e(g)}</h2>')
        out.append(table(["Row", "Item", "Place or entity", "Period", "Value", "Status", "Official source"], rows, "data", f"{tid}-{n}"))
    return "".join(out)


# ----------------------------------------------------------------------------- page shell
def page(slug, title, lede, body, group=""):
    nav = []
    for gname, items in NAV:
        nav.append(f'<div class="navgroup"><div class="navtitle">{gname}</div>')
        for href, label in items:
            cur = ' aria-current="page"' if href == slug else ""
            nav.append(f'<a href="{href}"{cur}>{label}</a>')
        nav.append("</div>")
    c = counts()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} | Sell or renew: a central Los Angeles net-leased restaurant</title>
<meta name="description" content="{e(lede)[:300]}">
<link rel="stylesheet" href="assets/site.css">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <a class="brand" href="index.html"><span class="mark" aria-hidden="true"></span><span class="brand-t">Sell or renew?<small>Central Los Angeles net-leased restaurant &middot; lease expires 2030 to 2035</small></span></a>
  <span class="asof">Official sources read {ACCESSED}</span>
  <button class="menu" type="button" aria-controls="side" aria-expanded="false">Menu</button>
</header>
<div class="shell">
<nav class="side" id="side" aria-label="Sections">{''.join(nav)}</nav>
<main id="main">
<p class="crumb">{e(group)}</p>
<h1>{e(title)}</h1>
<p class="lede">{lede}</p>
{body}
</main>
</div>
<footer class="foot">
  <p><strong>Decision support only.</strong> Not an appraisal, not tax advice, not investment advice. Every published value links to the official page it was read from on {ACCESSED}. {c['blank']} values that could not be confirmed, or are withheld for privacy, are blank and listed on <a href="flagged.html">Flagged for Review</a>. No personal or parcel-identifying information is published; the owner is <code>[OWNER-01]</code> and the property <code>[PROPERTY-01]</code>.</p>
  <p><a href="sources.html">{len(SRC)} sources</a> &middot; <a href="verification.html">how it was verified</a> &middot; <a href="workspaces.html">archive of earlier workbooks</a> &middot; rebuild: <code>python3 canonical/build_site.py</code></p>
</footer>
<script src="assets/site.js" defer></script>
</body>
</html>
"""


CSS = """:root{--bg:#f5f6f8;--panel:#fff;--ink:#17212f;--muted:#5a6676;--line:#dde2ea;--accent:#0b5cab;--accent-bg:#eaf2fb;
--ok:#17794a;--ok-bg:#e6f4ec;--calc:#5a3fb0;--calc-bg:#eeeafa;--warn:#8f5200;--warn-bg:#fdf1dd;--mute-bg:#eceff3;--bad:#a8261d;--bad-bg:#fbe9e7}
*{box-sizing:border-box}
html{font-size:16px}
body{margin:0;background:var(--bg);color:var(--ink);font:400 1rem/1.5 system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
a{color:var(--accent)}
a:focus-visible,button:focus-visible,input:focus-visible,summary:focus-visible{outline:3px solid #f0a020;outline-offset:2px}
.skip{position:absolute;left:-999px;top:0;background:#fff;padding:.5rem 1rem;z-index:20}
.skip:focus{left:.5rem;top:.5rem}
.top{position:sticky;top:0;z-index:10;display:flex;align-items:center;gap:1rem;background:#102a43;color:#fff;padding:.6rem 1.1rem}
.brand{display:flex;align-items:center;gap:.7rem;color:#fff;text-decoration:none;font-weight:650;font-size:1.05rem}
.brand small{display:block;font-weight:400;font-size:.78rem;opacity:.85}
.mark{width:1.5rem;height:1.5rem;border-radius:.35rem;background:linear-gradient(135deg,#f0a020,#e2542a);flex:none}
.asof{margin-left:auto;font-size:.8rem;opacity:.9;white-space:nowrap}
.menu{display:none;background:transparent;color:#fff;border:1px solid rgba(255,255,255,.5);border-radius:.4rem;padding:.3rem .7rem;font:inherit}
.shell{display:grid;grid-template-columns:15rem minmax(0,1fr);max-width:92rem;margin:0 auto}
.side{position:sticky;top:3.4rem;align-self:start;height:calc(100vh - 3.4rem);overflow:auto;padding:1rem .8rem 2rem;border-right:1px solid var(--line);background:var(--panel)}
.navgroup{margin-bottom:1rem}
.navtitle{font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);padding:0 .6rem .25rem}
.side a{display:block;padding:.32rem .6rem;border-radius:.4rem;color:var(--ink);text-decoration:none;font-size:.93rem}
.side a:hover{background:var(--mute-bg)}
.side a[aria-current=page]{background:var(--accent-bg);color:var(--accent);font-weight:650}
main{padding:1.4rem 1.6rem 3rem;min-width:0}
.crumb{margin:0;color:var(--muted);font-size:.78rem;letter-spacing:.06em;text-transform:uppercase}
h1{font-size:1.75rem;line-height:1.2;margin:.2rem 0 .5rem}
h2{font-size:1.15rem;margin:2rem 0 .6rem;padding-top:.4rem;border-top:1px solid var(--line)}
h3{font-size:1rem;margin:1.2rem 0 .4rem}
.lede{font-size:1.05rem;color:#2c3a4d;max-width:62rem;margin:.2rem 0 1.1rem}
p,li{max-width:62rem}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(13.5rem,1fr));gap:.8rem;margin:1rem 0}
.kpi,.card{background:var(--panel);border:1px solid var(--line);border-radius:.6rem;padding:.8rem .9rem}
.kpi-v{font-size:1.5rem;font-weight:700;line-height:1.15;overflow-wrap:anywhere}
.kpi-l{font-weight:600;margin-top:.15rem}
.kpi-s{color:var(--muted);font-size:.82rem}
.kpi-src{margin-top:.4rem;font-size:.8rem}
.card h3{margin:.1rem 0 .3rem;font-size:1rem}
.card p{margin:.2rem 0;font-size:.9rem;color:#33415a}
.card .meta{color:var(--muted);font-size:.8rem}
.answer{background:var(--panel);border:1px solid var(--line);border-left:.35rem solid var(--accent);border-radius:.6rem;padding:1rem 1.1rem;margin:1rem 0;max-width:62rem}
.answer p{margin:.3rem 0}
.callout{background:var(--warn-bg);border:1px solid #efd9ae;border-radius:.6rem;padding:.7rem .9rem;margin:1rem 0;max-width:62rem}
.callout.info{background:var(--accent-bg);border-color:#cfe0f3}
.tablewrap{overflow-x:auto;background:var(--panel);border:1px solid var(--line);border-radius:.6rem;margin:.6rem 0 1rem}
.tbl{border-collapse:collapse;width:100%;font-size:.9rem}
.tbl caption{caption-side:top;text-align:left;padding:.6rem .7rem;color:var(--muted);font-size:.85rem}
.tbl th{position:sticky;top:0;text-align:left;background:#eef1f5;color:#2c3a4d;font-weight:650;padding:.5rem .7rem;border-bottom:1px solid var(--line);white-space:nowrap}
.tbl td{padding:.5rem .7rem;border-bottom:1px solid #edf0f4;vertical-align:top}
.tbl tr:last-child td{border-bottom:0}
.tbl tr:target td{background:#fff8e1}
.tbl tr.hide{display:none}
.val{font-weight:650;white-space:normal}
.blank{color:var(--muted);font-weight:700}
.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.rid{font:600 .78rem ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:#44506a;text-decoration:none;white-space:nowrap}
a.rid{color:var(--accent);text-decoration:underline}
.rids{display:block;margin-bottom:.2rem}
.rids .rid{margin-right:.35rem}
.srcs a{margin-right:.5rem}
.srcs.compact a{font-size:.78rem;white-space:nowrap}
.src{white-space:nowrap;font-size:.86rem}
.ref{font-size:.85em}
.badge{display:inline-block;border-radius:1rem;padding:.08rem .55rem;font-size:.75rem;font-weight:650;white-space:nowrap}
.badge.verified{background:var(--ok-bg);color:var(--ok)}
.badge.computed{background:var(--calc-bg);color:var(--calc)}
.badge.unverified{background:var(--warn-bg);color:var(--warn)}
.badge.withheld{background:var(--mute-bg);color:#44506a}
.badge.assumption{background:var(--warn-bg);color:var(--warn)}
.badge.anchor{background:var(--ok-bg);color:var(--ok)}
.badge.review{background:var(--bad-bg);color:var(--bad)}
.badge.na{background:var(--mute-bg);color:#44506a}
.lvl{display:inline-block;min-width:1.5rem;text-align:center;border-radius:.3rem;padding:.05rem .3rem;font-size:.75rem;font-weight:700;white-space:nowrap;margin:.05rem 0}
.lvl0{background:#eef1f5;color:#8a94a6}.lvl1{background:#e6f4ec;color:#17794a}.lvl2{background:#fdf1dd;color:#8f5200}.lvl3{background:#fbe9e7;color:#a8261d}
details{margin-top:.25rem}
summary{cursor:pointer;color:var(--accent);font-size:.82rem}
blockquote{margin:.3rem 0;padding:.4rem .6rem;border-left:3px solid var(--line);background:#f8f9fb;color:#33415a;font-size:.84rem;overflow-wrap:anywhere}
.note{margin:.3rem 0;color:#44506a;font-size:.84rem}
.filter{margin:.4rem 0;font-size:.88rem;color:var(--muted)}
.filter input{font:inherit;padding:.3rem .5rem;border:1px solid #b9c2cf;border-radius:.4rem;min-width:14rem}
.steps{counter-reset:s;list-style:none;padding:0;max-width:62rem}
.steps li{counter-increment:s;position:relative;padding:.55rem .8rem .55rem 2.9rem;margin:.4rem 0;background:var(--panel);border:1px solid var(--line);border-radius:.6rem}
.steps li::before{content:counter(s);position:absolute;left:.8rem;top:.55rem;width:1.5rem;height:1.5rem;border-radius:50%;background:var(--accent);color:#fff;font-weight:700;font-size:.85rem;display:grid;place-items:center}
.bar{display:inline-block;height:.55rem;border-radius:.3rem;background:var(--accent);vertical-align:middle}
.bar.lo{background:#c9432f}
code{font:500 .85em ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:#eef1f5;padding:.05rem .3rem;border-radius:.25rem}
pre{background:#102a43;color:#e6edf5;padding:.8rem 1rem;border-radius:.6rem;overflow:auto;font-size:.85rem;max-width:62rem}
.foot{border-top:1px solid var(--line);background:var(--panel);padding:1rem 1.6rem;color:#44506a;font-size:.84rem}
.foot p{max-width:80rem;margin:.3rem auto}
@media (max-width:60rem){
 .shell{grid-template-columns:1fr}
 .menu{display:block}
 .asof{display:none}
 .side{display:none;position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}
 .side.open{display:grid;grid-template-columns:repeat(auto-fill,minmax(11rem,1fr));gap:.4rem}
 main{padding:1rem}
}
@media print{.top,.side,.foot,.filter,.menu{display:none}.shell{display:block}body{background:#fff}details{display:none}}
"""

JS = """(function(){
  var b=document.querySelector('.menu'),s=document.getElementById('side');
  if(b&&s){b.addEventListener('click',function(){var o=s.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false');});}
  Array.prototype.forEach.call(document.querySelectorAll('input[data-filter]'),function(inp){
    var prefix=inp.getAttribute('data-filter');
    var rows=Array.prototype.slice.call(document.querySelectorAll('table[id^="'+prefix+'"] tbody tr'));
    var out=document.querySelector('[data-count="'+prefix+'"]');
    function run(){var q=inp.value.trim().toLowerCase(),n=0;
      rows.forEach(function(r){var hit=!q||r.textContent.toLowerCase().indexOf(q)>-1;r.classList.toggle('hide',!hit);if(hit)n++;});
      if(out){out.textContent=q?(n+' of '+rows.length+' rows'):(rows.length+' rows');}}
    inp.addEventListener('input',run);run();
  });
  Array.prototype.forEach.call(document.querySelectorAll('[data-print]'),function(b){b.addEventListener('click',function(){window.print();});});
  if(location.hash&&location.hash.indexOf('#row-')===0){var t=document.getElementById(location.hash.slice(1));
    if(t){var d=t.querySelector('details');if(d){d.open=true;}}}
})();
"""

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f0a020"/><stop offset="1" stop-color="#e2542a"/></linearGradient></defs><rect width="32" height="32" rx="7" fill="#102a43"/><rect x="7" y="7" width="18" height="18" rx="4" fill="url(#g)"/></svg>
"""


# ----------------------------------------------------------------------------- prose discipline
PROSE_NUM = re.compile(r"(?<![A-Za-z0-9])\d[\d,]*(?:\.\d+)?(?![A-Za-z])")
MODEL_NUMS = set()


def _collect_model(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            _collect_model(v)
    elif isinstance(obj, list):
        for v in obj:
            _collect_model(v)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        for form in (f"{obj}", f"{obj:.1f}", f"{abs(obj):.1f}", f"{round(abs(obj))}", f"{round(obj)}"):
            MODEL_NUMS.update(nums(form))


_collect_model(MODEL)


def evidence_text(rid):
    r = ROWS[rid]
    parts = [r["value"], r["quote"], r["label"], r["period"], r["geo"], r.get("reason", ""), r.get("obtain", ""),
             SRC[r["source"]]["title"]]
    if r["status"] == "computed":
        parts += r["calc"]["operands"] + [r["calc"]["formula"]]
    return " ".join(parts)


ALL_LEDGER_NUMS = set()
for _s in SOURCES["sources"]:
    ALL_LEDGER_NUMS |= nums(_s["title"])
for _rid in ROW_ORDER:
    if ROWS[_rid]["status"] in ("verified", "computed"):
        ALL_LEDGER_NUMS |= nums(evidence_text(_rid))


def generic(tok):
    try:
        x = float(tok)
    except ValueError:
        return False
    return (x == int(x) and 0 <= x <= 12) or (x == int(x) and 1900 <= x <= 2100)


def check_prose(text, rids, where, allow_model=False, anywhere=False):
    """Every number written in prose must be in the evidence it cites."""
    text = re.sub(r"\[\[[A-Z]{2}-\d+[a-z]?\]\]", " ", text)
    text = re.sub(r"\{(?:snap|rev):[a-z_]+\}", " ", text)
    pool = set(ALL_LEDGER_NUMS) if anywhere else set()
    for rid in rids:
        pool |= nums(evidence_text(rid))
    if allow_model:
        pool |= MODEL_NUMS
    bad = []
    for tok in PROSE_NUM.findall(text):
        forms = nums(tok)
        if not forms or any(generic(f) for f in forms) or forms & pool:
            continue
        bad.append(tok)
    assert not bad, f"{where}: number(s) {bad} are not in the cited evidence {rids}"


def snap(text):
    table_ = {"open_prs": len(ARCHIVE["open_pull_requests"]), "unmerged_branches": len(ARCHIVE["branches_with_unmerged_work"]),
              "email_commits": ARCHIVE["history"]["commits_with_personal_provider_email"]}
    text = re.sub(r"\{snap:([a-z_]+)\}", lambda m: str(table_[m.group(1)]), text)
    return re.sub(r"\{rev:([a-z_]+)\}", lambda m: str(REVIEW["totals"][m.group(1)]), text)


def run_prose_checks():
    for r in RISKS["risks"]:
        assert r["evidence"], r["id"]
        check_prose(r["what"], r["evidence"], "risk " + r["id"])
        check_prose(r["mitigation"] + " " + r["watch"], r["evidence"], "risk " + r["id"] + " mitigation", anywhere=True)
    for q in QUESTIONS:
        assert q["have_rows"] or q["missing_rows"], q["id"]
        check_prose(q["have"], q["have_rows"], "question " + q["id"] + " (have)")
        check_prose(q["why"] + " " + q["how"], q["have_rows"] + q["missing_rows"], "question " + q["id"] + " (why)", allow_model=True, anywhere=True)
    for it in IRREG:
        if it["rows"]:
            check_prose(it["detail"], it["rows"], "irregularity " + it["id"])
    for n, pt in enumerate(DECIDE["answer_points"]):
        check_prose(pt["point"] + " " + pt["detail"], pt["rows"], f"answer point {n + 1}")
    loose = [DECIDE["question"], DECIDE["answer_short"]] + DECIDE["why_test_first"] + DECIDE["limits"]
    for o in DECIDE["options"]:
        loose += [o["what"], o["fits"], o["drawback"]]
    for r in DECIDE["rule"]:
        loose += [r["if"], r["then"], r["because"]]
    for p in DECIDE["plan"]:
        loose.append(p["action"])
    for t in DECIDE["triggers"]:
        loose += [t["watch"], t["act"]]
    for n, text in enumerate(loose):
        check_prose(text, [], f"decision text {n}", allow_model=True, anywhere=True)


# ----------------------------------------------------------------------------- model helpers
POOL = MODEL["pooled"]["simulation"]
RANK = MODEL["pooled"]["ranking_by_score"]
MODEL_SRC = ["S-TSY", "S-O-8K", "S-NNN-8K", "S-USGS"]


MODEL_SHORT = {"S-TSY": "Treasury", "S-O-8K": "Realty Income filing", "S-NNN-8K": "NNN REIT filing", "S-USGS": "USGS"}


def model_inputs():
    links = []
    for sid in MODEL_SRC:
        s_ = SRC[sid]
        links.append(f'<a href="{e(s_["url"])}" target="_blank" rel="noopener noreferrer" title="{e(s_["publisher"])}: {e(s_["title"])}">'
                     f'{MODEL_SHORT[sid]}<span aria-hidden="true"> ↗</span></a>')
    return '<span class="srcs compact">' + " ".join(links) + "</span>"


def n1(x):
    return format(x, ",.0f")


def strategy_rows(full=False):
    cash = POOL["sell_cash"]["median"]
    top = max(POOL[k]["p95"] for k in ORDER)
    rows = []
    for k in RANK:
        p = POOL[k]
        o = next(x for x in DECIDE["options"] if x["key"] == k)
        bar = (f'<span class="bar lo" style="width:{round(6 * p["p05"] / top, 2)}rem"></span>'
               f'<span class="bar" style="width:{round(6 * (p["median"] - p["p05"]) / top, 2)}rem"></span>')
        cells = [f'<strong>{RANK.index(k) + 1}</strong>', f'<strong>{e(o["label"])}</strong><br><span class="note">{e(o["family"])}</span>']
        if full:
            cells.append(e(o["what"]))
        cells += [f'<span class="num">{n1(p["median"])}</span>', f'<span class="num">{n1(p["p05"])}</span>',
                  f'<span class="num">{n1(p["score"])}</span>', bar,
                  f'<span class="num">{p["chance_below_cash_sale"]:.0f}%</span>']
        if full:
            cells += [e(o["fits"]), e(o["drawback"])]
        cells.append(model_inputs())
        rows.append(cells)
    return rows


def strategy_table(full=False):
    heads = ["Rank", "Strategy"] + (["What it is"] if full else []) + [
        "Typical outcome", "1-in-20 bad outcome", "Balanced score", "Bad to typical", "Chance of ending below a cash sale"]
    if full:
        heads += ["Fits an owner who", "Main drawback"]
    heads.append("Official inputs")
    cap = ("Model output, not a forecast. Money is wealth in " + str(MODEL["meta"]["horizon_year"]) +
           " per $100 of today's yearly rent, before income tax, pooled over the six possible expiry years. "
           "Balanced score = halfway between the typical and the bad outcome. Settings and their sources are on the Projections page.")
    return table(heads, strategy_rows(full), "model", "strategies", cap)


# ----------------------------------------------------------------------------- pages
def build_index():
    c = counts()
    a = MODEL["after_the_answer"]
    body = [f'<div class="answer"><p><strong>Short answer.</strong> {e(DECIDE["answer_short"])}</p>'
            f'<p class="note">The lease, the rent and the owner\'s own position are not public and are blank here. '
            f'<a href="executive-summary.html">Executive summary</a> &middot; <a href="decision.html">Decision analysis</a> &middot; '
            f'<a href="questions.html">What must be answered first</a></p></div>']
    body.append("<h2>The evidence at a glance</h2>")
    body.append('<div class="cards">' + "".join([
        kpi("PP-002b", "Change in county residents since 2020"),
        kpi("PJ-075", "Projected change in public school enrollment", "Los Angeles County, 2025-26 to 2035-36"),
        kpi("EC-064", "Restaurant jobs, change over the year", "Los Angeles County, September 2026"),
        kpi("TN-085", "Net change in the tenant's restaurants in a year", "Jack in the Box system, July 2025 to July 2026"),
        kpi("TN-020", "Tenant same-store sales", "Latest quarter, whole system"),
        kpi("CM-001", "10-year Treasury yield", "Latest posted date"),
        kpi("CM-020", "Yield a large buyer pays for long net leases", "National, third quarter 2026"),
        kpi("CM-054", "Expiring leases renewed by the same tenant", "National portfolio, nine months of 2026"),
        kpi("HZ-001", "Chance of a magnitude 6.7+ earthquake", "Los Angeles region, 30 years from 2014"),
        kpi("TX-015", "Transfer tax on a sale at or below $5,400,000", "City plus county"),
    ]) + "</div>")
    body.append("<h2>Six ways to act, compared</h2>")
    body.append(strategy_table(False))
    body.append(f'<p class="note">Once the tenant has answered an extension request, the comparison sharpens. '
                f'After a refusal, selling and exchanging gives a typical outcome of {n1(a["if_tenant_refuses"]["sell_and_exchange"]["median"])} '
                f'against {n1(a["if_tenant_refuses"]["keep"]["median"])} for keeping, and a bad outcome of '
                f'{n1(a["if_tenant_refuses"]["sell_and_exchange"]["p05"])} against {n1(a["if_tenant_refuses"]["keep"]["p05"])}. '
                f'See <a href="decision.html#after">Decision analysis</a>.</p>')
    body.append("<h2>What to do next</h2><ol class=\"steps\">" + "".join(f"<li>{e(x)}</li>" for x in [
        "Read the lease: expiry date, rent, options and notice dates, who the tenant is, and what happens after a disaster.",
        "Ask the tenant in writing for an early extension. The answer is the most useful single fact available.",
        "Then choose with the decision rule: a refusal points to selling before expiry; an agreement leaves a choice between keeping and selling a more valuable lease."]) + "</ol>")
    cats = [("demographics.html", "People and place", "Residents, households, income, housing, schools.", "people-place"),
            ("market-economics.html", "Economy and jobs", "Jobs, wages, prices, spending, wage rules.", "economy"),
            ("tenant.html", "Tenant", "The tenant's filed results, closures and debt.", "tenant"),
            ("property-lease.html", "Property and lease", "What is known and what must be obtained.", "property-lease"),
            ("valuation.html", "Capital markets", "Interest rates, buyers' yields, what happens at expiry.", "capital-markets"),
            ("taxes.html", "Taxes and costs", "Transfer tax, income tax, exchange rules, property tax.", "taxes"),
            ("hazards.html", "Hazards and insurance", "Earthquake, wildfire, flood, insurance.", "hazards"),
            ("projection-model.html", "Projections", "Official projections and the scenario model.", "projections")]
    body.append("<h2>Browse by category</h2><div class=\"cards\">")
    for href, name, what, cat in cats:
        k = counts(cat)
        body.append(f'<div class="card"><h3><a href="{href}">{name}</a></h3><p>{what}</p>'
                    f'<p class="meta">{k["published"]} values with sources &middot; {k["blank"]} blank</p></div>')
    for href, name, what, meta in [
            ("risks.html", "Risks", "Each risk rated against each strategy.", f'{len(RISKS["risks"])} risks'),
            ("questions.html", "Questions to answer", "What is known, what is missing, how to find out.", f"{len(QUESTIONS)} questions"),
            ("flagged.html", "Flagged for Review", "Every blank and every irregularity.", f'{c["blank"]} blanks &middot; {len(IRREG)} irregularities'),
            ("suggestions.html", "Suggestions for Review", "Ways to improve this site. None implemented.", f'{len(SUGGEST["suggestions"])} proposals')]:
        body.append(f'<div class="card"><h3><a href="{href}">{name}</a></h3><p>{what}</p><p class="meta">{meta}</p></div>')
    body.append("</div>")
    body.append(f'<div class="callout"><strong>What this site cannot tell you.</strong> {c["blank"]} facts are blank: '
                f'{c["unverified"]} could not be confirmed from an official source and {c["withheld"]} are withheld to protect the owner. '
                f'They include the rent, the exact expiry date, the renewal options, the property\'s value and the owner\'s tax position. '
                f'<a href="flagged.html">See them all</a>.</div>')
    lede = (e(DECIDE["question"]) + f" This site sets out what {len(SRC)} official sources say, what remains unknown, "
            "and how the choices compare.")
    return page("index.html", "Overview", lede, "".join(body), "Start")


def build_exec():
    c = counts()
    a = MODEL["after_the_answer"]
    body = [f'<div class="answer"><p><strong>{e(DECIDE["answer_short"])}</strong></p><ul>'
            + "".join(f"<li>{e(x)}</li>" for x in DECIDE["why_test_first"]) + "</ul></div>"]
    body.append("<h2>What the evidence shows</h2>")
    body.append(table(["Finding", "Detail", "Evidence and official sources"],
                      [[f"<strong>{e(p['point'])}</strong>", fill(p["detail"]), cites(p["rows"])] for p in DECIDE["answer_points"]], "data"))
    body.append("<h2>What the model adds</h2>")
    best, worst = RANK[0], RANK[-1]
    med_sorted = MODEL["pooled"]["ranking_by_median"]
    rows = [
        ["Highest typical outcome", f'{e(STRAT_SHORT[med_sorted[0]])}: {n1(POOL[med_sorted[0]]["median"])}',
         "Doing nothing pays the most when nothing goes wrong.", model_inputs()],
        ["Best outcome in a bad case", f'{e(STRAT_SHORT[MODEL["pooled"]["ranking_by_bad_case"][0]])}: {n1(POOL[MODEL["pooled"]["ranking_by_bad_case"][0]]["p05"])}',
         f'Doing nothing has the worst bad case: {n1(POOL["do_nothing"]["p05"])}.', model_inputs()],
        ["Best balance of the two", f'{e(STRAT_SHORT[best])}: {n1(POOL[best]["score"])}',
         f'Last on the same measure: {e(STRAT_SHORT[worst])}, {n1(POOL[worst]["score"])}.', model_inputs()],
        ["If the tenant refuses to extend", f'Sell and exchange: typical {n1(a["if_tenant_refuses"]["sell_and_exchange"]["median"])}, bad case {n1(a["if_tenant_refuses"]["sell_and_exchange"]["p05"])}',
         f'Keep: typical {n1(a["if_tenant_refuses"]["keep"]["median"])}, bad case {n1(a["if_tenant_refuses"]["keep"]["p05"])}. Selling is ahead on both.', model_inputs()],
        ["If the tenant agrees to extend", f'Keep: typical {n1(a["if_tenant_agrees"]["keep"]["median"])}, bad case {n1(a["if_tenant_agrees"]["keep"]["p05"])}',
         f'Sell and exchange: typical {n1(a["if_tenant_agrees"]["sell_and_exchange"]["median"])}, bad case {n1(a["if_tenant_agrees"]["sell_and_exchange"]["p05"])}. A real choice.', model_inputs()],
        ["Value of an extension to a seller", "Sale price " + " to ".join(f"{v:.0f}%" for v in (min(MODEL["today"]["price_gain_from_extension_pct"].values()), max(MODEL["today"]["price_gain_from_extension_pct"].values()))) + " higher",
         "Largest when the lease expires soonest.", model_inputs()],
    ]
    body.append(table(["Question", "Model result", "Reading", "Official inputs"], rows, "model", "",
                      "Wealth in " + str(MODEL["meta"]["horizon_year"]) + " per $100 of today's yearly rent, before income tax. Scenario output, not a forecast."))
    body.append("<h2>The decision rule</h2>")
    body.append(table(["If", "Then", "Because", "Official inputs"],
                      [[e(r["if"]), f"<strong>{e(r['then'])}</strong>", e(r["because"]), model_inputs()] for r in DECIDE["rule"]], "model"))
    body.append("<h2>The first twelve weeks</h2>")
    body.append(plan_table())
    body.append("<h2>Limits of this work</h2>")
    body.append(table(["Limit", "Where to read more"], [[e(x), l] for x, l in zip(DECIDE["limits"], [
        '<a href="verification.html">Verification</a>', '<a href="projection-model.html#settings">Model settings</a>',
        '<a href="projection-model.html#sensitivity">Sensitivity</a>', '<a href="valuation.html">Capital markets</a>'])], "site"))
    lede = (f"One page for a reader with ten minutes. Built from {c['published']} values read at {len(SRC)} official sources on {ACCESSED}; "
            f"{c['blank']} further values are blank because they could not be confirmed or are private.")
    return page("executive-summary.html", "Executive summary", lede, "".join(body), "Start")


def plan_table():
    qrow = {q["id"]: q for q in QUESTIONS}
    rows = []
    for p in DECIDE["plan"]:
        rids = []
        for qid in p["closes"]:
            rids += qrow[qid]["missing_rows"] + qrow[qid]["have_rows"]
        srcs = []
        for rid in rids:
            if ROWS[rid]["source"] not in srcs:
                srcs.append(ROWS[rid]["source"])
        rows.append([e(p["when"]), e(p["action"]), " ".join(f'<a class="rid" href="questions.html#{q}">{q}</a>' for q in p["closes"]),
                     e(p["who"]), '<span class="srcs">' + " ".join(src_link(s) for s in srcs[:4]) + "</span>"])
    return table(["When", "Action", "Questions it closes", "Who", "Official sources for the items sought"], rows, "data")


def build_decision():
    a = MODEL["after_the_answer"]
    body = ["<h2 id=\"options\">The six strategies</h2>", strategy_table(True)]
    body.append('<h2 id="after">After the tenant answers</h2>')
    body.append(f'<p>In the model the tenant agrees to an early extension in {a["share_agreeing_pct"]:.0f}% of trials (a setting, not a fact). '
                'What follows depends on the answer.</p>')
    rows = []
    for key, label in (("if_tenant_refuses", "Tenant refuses"), ("if_tenant_agrees", "Tenant agrees")):
        for act, alabel in (("keep", "Keep the property"), ("sell_and_exchange", "Sell and exchange")):
            x = a[key][act]
            rows.append([label, alabel, f'<span class="num">{n1(x["median"])}</span>', f'<span class="num">{n1(x["p05"])}</span>',
                         f'<span class="num">{n1(x["score"])}</span>', model_inputs()])
    body.append(table(["Tenant's answer", "Owner's move", "Typical outcome", "1-in-20 bad outcome", "Balanced score", "Official inputs"], rows, "model"))
    body.append("<h2 id=\"rule\">Decision rule</h2>")
    body.append(table(["If", "Then", "Because", "Official inputs"],
                      [[e(r["if"]), f"<strong>{e(r['then'])}</strong>", e(r["because"]), model_inputs()] for r in DECIDE["rule"]], "model"))
    body.append('<h2 id="weights">Does the ranking depend on how much the owner fears a bad outcome?</h2>')
    rows = []
    for w, order in MODEL["pooled"]["ranking_by_weight"].items():
        wl = {"0.0": "Typical outcome only (growth)", "0.25": "Mostly the typical outcome", "0.5": "Balanced (base case)",
              "0.75": "Mostly the bad outcome", "1.0": "Bad outcome only (preservation)"}[w]
        rows.append([wl, e(STRAT_SHORT[order[0]]), e(STRAT_SHORT[order[1]]), e(STRAT_SHORT[order[-1]]), model_inputs()])
    body.append(table(["Weight on the bad outcome", "First", "Second", "Last", "Official inputs"], rows, "model"))
    body.append('<h2 id="expiry">By expiry year</h2><p>The exact expiry date is unknown, so each year in the window is run separately.</p>')
    rows = []
    for y, blk in MODEL["by_expiry"].items():
        s = blk["simulation"]
        rows.append([y, f'<span class="num">{n1(MODEL["today"]["sale_price_as_is"][y])}</span>',
                     f'<span class="num">+{MODEL["today"]["price_gain_from_extension_pct"][y]:.0f}%</span>',
                     e(STRAT_SHORT[blk["ranking"][0]]), f'<span class="num">{n1(s["do_nothing"]["median"])} / {n1(s["do_nothing"]["p05"])}</span>',
                     f'<span class="num">{n1(s["sell_exchange"]["median"])} / {n1(s["sell_exchange"]["p05"])}</span>', model_inputs()])
    body.append(table(["Lease expires", "Sale price today, as is", "Price gain if extended first", "First on balanced score",
                       "Do nothing: typical / bad", "Sell and exchange: typical / bad", "Official inputs"], rows, "model"))
    body.append('<h2 id="breakevens">Breakevens</h2><p>The value of one setting at which two strategies give the same expected outcome, with everything else at its base value and no shocks.</p>')
    rows = []
    for y, b in MODEL["breakevens"].items():
        def f(x, suffix="%"):
            return "none in range" if x is None else f"{x:.1f}{suffix}"
        tax = b["tax_drag_where_cash_sale_equals_doing_nothing"]
        rows.append([y, f(b["renewal_chance_where_doing_nothing_equals_selling"]),
                     f(b["extension_rent_where_keeping_equals_selling"], "% of today's rent"),
                     f(b["short_lease_premium_where_doing_nothing_equals_selling"], " points"),
                     "none: a cash sale trails even before tax" if (tax is None or tax < 0) else f(tax), model_inputs()])
    body.append(table(["Lease expires", "Renewal chance above which doing nothing beats selling and exchanging",
                       "Lowest extension rent at which keeping still beats selling and exchanging",
                       "Short-lease penalty above which doing nothing beats selling and exchanging",
                       "Tax share at which a cash sale equals doing nothing", "Official inputs"], rows, "model"))
    body.append('<h2 id="stress">Stress cases</h2><p>The model re-run with a few settings changed, for an expiry in the middle of the window.</p>')
    rows = []
    for st in MODEL["stress"]:
        sm = st["summary"]
        rows.append([e(st["case"]), e(STRAT_SHORT[st["ranking"][0]]), e(STRAT_SHORT[st["ranking"][1]]),
                     f'<span class="num">{n1(sm["do_nothing"]["median"])} / {n1(sm["do_nothing"]["p05"])}</span>',
                     f'<span class="num">{n1(sm["sell_exchange"]["median"])} / {n1(sm["sell_exchange"]["p05"])}</span>',
                     f'<span class="num">{n1(sm["test_then_decide"]["median"])} / {n1(sm["test_then_decide"]["p05"])}</span>', model_inputs()])
    body.append(table(["Case", "First on balanced score", "Second", "Do nothing: typical / bad", "Sell and exchange: typical / bad",
                       "Extend and keep, or sell if refused: typical / bad", "Official inputs"], rows, "model"))
    body.append('<h2 id="exposure">Which risks bear on which strategy</h2><p>Every risk on the <a href="risks.html">Risks</a> page, rated for each strategy: 0 none, 1 low, 2 medium, 3 high.</p>')
    rows = []
    for r in RISKS["risks"]:
        rows.append([f'<a class="rid" href="risks.html#{r["id"]}">{r["id"]}</a>', e(r["title"])] +
                    [f'<span class="lvl lvl{r["exposure"][k]}">{r["exposure"][k]}</span>' for k in ORDER] + [cites(r["evidence"][:3])])
    totals = ["", "<strong>Sum of ratings</strong>"] + [f'<strong>{sum(r["exposure"][k] for r in RISKS["risks"])}</strong>' for k in ORDER] + [""]
    body.append(table(["Risk", "Title"] + [e(STRAT_SHORT[k]) for k in ORDER] + ["Evidence and official sources"], rows, "data", "exposure-t"))
    body.append(table(["", "Sum of ratings across all risks"] + [e(STRAT_SHORT[k]) for k in ORDER], [["", "A higher sum means more risks bear on the strategy; it is a count, not a probability."] + totals[2:-1]], "site"))
    body.append('<h2 id="plan">The first twelve weeks</h2>' + plan_table())
    body.append('<h2 id="triggers">What to watch</h2>')
    rows = []
    for t in DECIDE["triggers"]:
        r = ROWS[t["row"]]
        now = e(r["value"]) if r["value"] else '<span class="blank">&mdash;</span> ' + badge(r["status"])
        rows.append([e(t["watch"]), now, e(t["act"]), cites([t["row"]])])
    body.append(table(["Watch", "Reading on the access date", "What a change means", "Evidence and official source"], rows, "data"))
    lede = ("Six strategies, compared on what they typically deliver and on how they fare when things go wrong, with the risks that bear on each. "
            "The comparison is a scenario model built on verified anchors and labelled assumptions; it is not a forecast.")
    return page("decision.html", "Decision analysis", lede, "".join(body), "Decide")


CODES = {"sell_cash": "SC", "sell_exchange": "SX", "extend_then_sell": "ES", "test_then_decide": "TD", "extend_and_hold": "EH", "do_nothing": "DN"}


def exposure_chips(r):
    return " ".join(f'<span class="lvl lvl{r["exposure"][k]}" title="{e(STRAT_SHORT[k])}: {RISKS["levels"][str(r["exposure"][k])]}">'
                    f'{CODES[k]} {r["exposure"][k]}</span>' for k in ORDER)


def build_risks():
    body = ['<p>Each risk cites the verified rows it rests on, is rated against each of the six strategies '
            '(0 none, 1 low, 2 medium, 3 high) and says what would reduce it and what to watch.</p>']
    body.append(table(["Code", "Strategy", "What it is"],
                      [[f'<span class="lvl lvl0">{CODES[o["key"]]}</span>', f'<strong>{e(o["label"])}</strong>', e(o["what"])] for o in DECIDE["options"]],
                      "site", "", "Codes used in the exposure column"))
    body.append(filter_box("risk-"))
    for kind, tid, intro in (("Business as usual", "risk-bau", "Things that happen in ordinary years."),
                             ("Black swan", "risk-bs", "Rare events with large consequences: natural disasters, tenant failure, financial crisis.")):
        rows = []
        for r in RISKS["risks"]:
            if r["kind"] != kind:
                continue
            rows.append({"attrs": f' id="{r["id"]}"', "cells": [
                f'<span class="rid">{r["id"]}</span>', f'<strong>{e(r["title"])}</strong><br>{e(r["what"])}', exposure_chips(r),
                e(r["mitigation"]), e(r["watch"]), cites(r["evidence"])]})
        body.append(f'<h2 id="{tid}-h">{kind}</h2><p>{intro}</p>')
        body.append(table(["Risk", "What could happen", "Exposure by strategy", "What reduces it", "What to watch",
                           "Evidence and official sources"], rows, "data", tid))
    lede = (f'{len(RISKS["risks"])} risks: {sum(1 for r in RISKS["risks"] if r["kind"] == "Business as usual")} of the ordinary kind and '
            f'{sum(1 for r in RISKS["risks"] if r["kind"] == "Black swan")} rare, severe events. Each is tied to official sources and rated for every strategy.')
    return page("risks.html", "Risks", lede, "".join(body), "Decide")


def build_questions():
    body = ['<p>Everything that has to be settled before a decision can reasonably be taken. For each question: why it matters, '
            'what the official sources already say, what is missing, how to find it and who can answer.</p>', filter_box("q-")]
    rows = []
    order = {"Critical": 0, "High": 1, "Medium": 2}
    for q in sorted(QUESTIONS, key=lambda x: (order[x["priority"]], x["id"])):
        have = e(q["have"]) + ("<br>" + cites(q["have_rows"]) if q["have_rows"] else "")
        missing = (cites(q["missing_rows"]) if q["missing_rows"] else "Nothing further from public sources.")
        st = {"Open": "unverified", "Partly answered": "computed", "Answered": "verified"}[q["status"]]
        rows.append({"attrs": f' id="{q["id"]}"', "cells": [
            f'<span class="rid">{q["id"]}</span>', f'<span class="badge {"review" if q["priority"] == "Critical" else "na"}">{q["priority"]}</span>',
            f'<strong>{e(q["question"])}</strong><p class="note"><strong>Why it matters:</strong> {e(q["why"])}</p><p class="note">About: {e(q["category"]).lower()}</p>',
            have, missing, e(q["how"]) + f'<p class="note"><strong>Who can answer:</strong> {e(q["who"])}</p>',
            f'<span class="badge {st}">{q["status"]}</span>']})
    body.append(table(["No.", "Priority", "Question", "What we have", "What is missing (blank rows, and where each can be found)",
                       "How to find out", "Status"], rows, "data", "q-t"))
    n_open = sum(1 for q in QUESTIONS if q["status"] == "Open")
    lede = (f'{len(QUESTIONS)} questions, {sum(1 for q in QUESTIONS if q["priority"] == "Critical")} of them critical. '
            f'{n_open} are open: most can be closed by reading the lease, asking the tenant, and one meeting each with a broker, an attorney and a tax adviser.')
    return page("questions.html", "Questions to answer before deciding", lede, "".join(body), "Decide")


def evidence_page(slug, title, cat, lede, tiles, group="Evidence", extra=""):
    k = counts(cat)
    body = ['<div class="cards">' + "".join(kpi(*t) for t in tiles) + "</div>"]
    body.append(f'<p class="note">{k["published"]} values on this page were read at the official source on {ACCESSED} and link to it. '
                f'{k["blank"]} are blank on purpose and say why. Open "What the source says" under any item to see the text that was on the page.</p>')
    body.append(filter_box(cat))
    body.append(extra)
    body.append(ledger_table(cat, cat))
    return page(slug, title, lede, "".join(body), group)


def build_evidence():
    out = {}
    out["demographics.html"] = evidence_page(
        "demographics.html", "People and place", "people-place",
        "Who lives in the city and county the restaurant serves: how many, how the number is changing, what they earn, how they are housed and schooled. Figures are for the City and County of Los Angeles; the neighbourhood itself needs the address, which is withheld.",
        [("PP-001a", "City residents"), ("PP-002b", "Change in county residents since 2020"), ("PP-030a", "Median household income, city"),
         ("PP-021a", "Residents per square mile, city"), ("PP-069", "Public school enrollment, ten-year change", "Los Angeles County, 2015-16 to 2025-26")])
    out["market-economics.html"] = evidence_page(
        "market-economics.html", "Economy and jobs", "economy",
        "Whether nearby households and workers can keep spending at a fast-food restaurant: jobs, unemployment, wages, prices, restaurant employment and the wage rules the tenant must follow.",
        [("EC-022", "Unemployment rate, county"), ("EC-031", "Payroll jobs, change over the year"), ("EC-064", "Restaurant jobs, change over the year"),
         ("EC-040", "Consumer prices, change over the year"), ("EC-093", "Fast-food minimum wage")])
    out["tenant.html"] = evidence_page(
        "tenant.html", "Tenant", "tenant",
        "What Jack in the Box Inc. has told its regulator about its restaurants, sales, debt and plans. These are company-wide figures from filings; nothing here is specific to the subject restaurant, whose own sales are unknown.",
        [("TN-001", "Restaurants in the system"), ("TN-085", "Net change in a year"), ("TN-020", "Same-store sales, latest quarter"),
         ("TN-043", "Stockholders' deficit, $ thousand"), ("TN-080", "Closure programme")])
    out["property-lease.html"] = evidence_page(
        "property-lease.html", "Property and lease", "property-lease",
        "Everything on this page is blank. Either it sits in documents this workbook has not seen, or publishing it would identify the property or its owner. Each row says why it is blank, how to obtain it, and links to the official place where the public part can be looked up.",
        [], extra='<div class="callout"><strong>Nothing here is filled in.</strong> The rows are a checklist. Fill them privately; do not add them to this repository.</div>')
    out["valuation.html"] = evidence_page(
        "valuation.html", "Capital markets", "capital-markets",
        "What money costs and what buyers pay: Treasury yields, the central bank's rate, the yields two large net-lease buyers report, and what happened to leases that expired in their portfolios. National figures; no official source prices this property.",
        [("CM-001", "10-year Treasury yield"), ("CM-010", "Federal Reserve target range"), ("CM-020", "Buyer's purchase yield, long leases"),
         ("CM-054", "Expiring leases renewed"), ("CM-034", "Empty building price as a share of leased")])
    out["taxes.html"] = evidence_page(
        "taxes.html", "Taxes and costs", "taxes",
        "The taxes a sale would trigger, the rules for deferring them, and the property-tax rules that apply while the property is held. Rates are statutory; the owner's actual tax depends on private facts.",
        [("TX-015", "City plus county transfer tax, lower band"), ("TX-016", "The same above $5,400,000"), ("TX-049", "Top federal rate on a long-term gain"),
         ("TX-060", "Top California rate"), ("TX-054", "Days to name an exchange property")])
    out["hazards.html"] = evidence_page(
        "hazards.html", "Hazards and insurance", "hazards",
        "The region's record and official forecasts for earthquake and wildfire, and the state of the insurance market. Regional figures say little about one parcel: the parcel's own hazard zones are blank on the Property and lease page.",
        [("HZ-001", "Chance of a magnitude 6.7+ earthquake"), ("HZ-010", "The same as a yearly chance"), ("HZ-031", "Structures destroyed, January 2025 fires"),
         ("HZ-040", "Economic output lost to those fires"), ("HZ-060", "Assessment to keep the last-resort insurer paying")])
    return out


def build_projection():
    ao = MODEL["area_outlook"]
    body = ['<div class="cards">' + "".join(kpi(*t) for t in [
        ("PJ-070", "Projected change in county residents", "2025 to 2030"), ("PJ-071", "Projected change in county residents", "2025 to 2035"),
        ("PJ-075", "Projected change in school enrollment", "2025-26 to 2035-36"), ("PJ-053", "Projected job growth a year", "Los Angeles County, 2019 to 2050")]) + "</div>"]
    body.append('<p>This page has two parts. <a href="#official">Official projections</a> are other bodies\' numbers, read at the source. '
                '<a href="#model">The scenario model</a> is this workbook\'s own arithmetic on labelled settings.</p>')
    body.append('<h2 id="outlook">County outlook, year by year</h2>')
    rows = []
    sch = {s["school_year"][:4]: s for s in ao["school_enrollment"]}
    for r in ao["residents"]:
        s = sch.get(str(r["year"]))
        rows.append([str(r["year"]), f'<span class="num">{r["official_projection"]:,}</span>', f'<span class="num">{r["index_2025_100"]:.1f}</span>',
                     f'<span class="num">{r["if_2020_2025_trend_continued"]:,}</span>', f'<span class="num">{r["trend_index_2025_100"]:.1f}</span>',
                     (f'<span class="num">{s["official_projection"]:,}</span>' if s else "&mdash;"),
                     (f'<span class="num">{s["index_2025_26_100"]:.1f}</span>' if s else "&mdash;"),
                     '<span class="srcs">' + src_link("S-DOF-P2A") + " " + src_link("S-DOF-K12") + "</span>"])
    body.append(table(["Year", "Residents, State projection", "Index (2025 = 100)", "Residents if the 2020 to 2025 trend simply continued",
                       "Index", "Public school enrollment, State projection (school year starting)", "Index (2025-26 = 100)", "Official sources"],
                      rows, "data", "outlook-t", e(ao["note"]) + f' The trend used is {ao["residents_trend_pct_a_year"]:.2f}% a year.'))
    body.append('<h2 id="official">Official projections</h2>' + filter_box("projections"))
    body.append(ledger_table("projections", "projections"))
    body.append('<h2 id="model">The scenario model</h2>')
    body.append(f'<p>{e(MODEL["meta"]["unit"])} The model follows six strategies from {MODEL["meta"]["start_year"]} to {MODEL["meta"]["horizon_year"]} for each '
                f'possible expiry year, in {MODEL["meta"]["trials"]:,} seeded trials per year (seed {MODEL["meta"]["seed"]}). It adds yield movements, tenant failure '
                'and regional disasters to a closed-form calculation, so that the spread of outcomes is visible, not only the average. '
                'Every setting is listed below with its origin. <strong>It is a way of thinking with numbers, not a forecast.</strong></p>')
    body.append('<h3 id="results">Results</h3>' + strategy_table(False))
    body.append('<h3 id="settings">Settings</h3><p>An <span class="badge anchor">Anchor</span> is copied from a verified row and checked against it at every build. '
                'An <span class="badge assumption">Assumption</span> is the analyst\'s, because no official source exists; its range is tested in the sensitivity table.</p>')
    rows = []
    for key, s in ASSUME["settings"].items():
        linkrow = s.get("row")
        refs = re.findall(r"\b([A-Z]{2}-\d+[a-z]?)\b", s["why"])
        refs = [r for r in ([linkrow] if linkrow else []) + refs if r in ROWS]
        seen = []
        for r in refs:
            if r not in seen:
                seen.append(r)
        src = cites(seen) if seen else model_inputs()
        rows.append([e(s["label"]), f'<span class="num">{s["value"]:g} {e(s["unit"])}</span>', f'<span class="num">{s["low"]:g} to {s["high"]:g}</span>',
                     f'<span class="badge {s["kind"]}">{s["kind"].capitalize()}</span>', e(s["why"]), src])
    body.append(table(["Setting", "Base value", "Range tested", "Origin", "Why this value", "Evidence and official sources"], rows, "data", "settings-t"))
    body.append('<h3 id="sensitivity">Which settings matter most</h3><p>Each setting is moved to the low and high end of its range, one at a time. '
                f'The figure shown is the expected advantage of doing nothing over selling and exchanging, averaged over the six expiry years; at base values it is {MODEL["sensitivity_base_gap"]:+.0f}. '
                'The largest swings mark the facts most worth finding out.</p>')
    rows = []
    for s in MODEL["sensitivity"][:14]:
        spec = ASSUME["settings"][s["setting"]]
        refs = [r for r in re.findall(r"\b([A-Z]{2}-\d+[a-z]?)\b", spec["why"]) if r in ROWS]
        if spec.get("row"):
            refs = [spec["row"]] + refs
        rows.append([e(s["label"]), f'{s["low"]:g} to {s["high"]:g} {e(s["unit"])}', f'<span class="num">{s["gap_at_low"]:+.0f}</span>',
                     f'<span class="num">{s["gap_at_high"]:+.0f}</span>', f'<span class="num">{s["swing"]:.0f}</span>',
                     cites(list(dict.fromkeys(refs))[:3]) if refs else model_inputs()])
    body.append(table(["Setting", "Range", "Advantage of doing nothing at the low end", "At the high end", "Swing", "Evidence and official sources"], rows, "data"))
    body.append('<h3 id="later">Does waiting to sell pay?</h3><p>Hold for some years, then sell for cash, with nothing going wrong. Rent collected is set against the falling price of a shortening lease.</p>')
    rows = []
    for y in ("2030", "2032", "2035"):
        for pt in MODEL["sell_later"][y]:
            rows.append([y, str(pt["sell_year"]), str(pt["years_left_on_lease"]), f'<span class="num">{n1(pt["sale_price"])}</span>',
                         f'<span class="num">{n1(pt["wealth_2040"])}</span>', model_inputs()])
    body.append(table(["Lease expires", "Sell in", "Years left on the lease at sale", "Sale price", "Wealth in 2040", "Official inputs"], rows, "model", "later-t"))
    body.append('<h3 id="tax">Effect of income tax on a cash sale</h3><p>The base case is before tax because the owner\'s basis is unknown. '
                'This table takes a share of the net price as tax on a cash sale and leaves the other strategies untouched.</p>')
    rows = [[f'{t["tax_drag_pct"]:.0f}%', f'<span class="num">{n1(t["sell_cash"])}</span>', f'<span class="num">{n1(t["sell_exchange"])}</span>',
             f'<span class="num">{n1(t["do_nothing"])}</span>', cites(["TX-049", "TX-060"])] for t in MODEL["tax_sensitivity"]]
    body.append(table(["Share of net price lost to tax", "Sell for cash", "Sell and exchange", "Do nothing", "Evidence and official sources"], rows, "data"))
    body.append('<h3 id="reproduce">Reproduce it</h3><pre>python3 canonical/model.py                              # writes canonical/data/model_output.json\n'
                'python3 -m unittest discover -s canonical/tests -v    # 15 tests\npython3 canonical/build_site.py                         # rebuilds every page</pre>')
    lede = ("Where the county is officially projected to go, and how six strategies compare under labelled assumptions. "
            "Official projections are projections; the model is a scenario tool. Neither is a forecast of this property.")
    return page("projection-model.html", "Projections", lede, "".join(body), "Evidence")


def build_flagged():
    c = counts()
    body = ['<p>Two lists. <a href="#blanks">Blank values</a> are facts that could not be confirmed from an official source on the access date, '
            'or that are withheld to protect the owner; none was estimated. <a href="#irregularities">Irregularities</a> are things found during the review '
            'that a person should look at. Nothing on this page blocked publication.</p>']
    body.append(f'<h2 id="blanks">Blank values ({c["blank"]})</h2>' + filter_box("blank-"))
    rows = []
    for rid in ROW_ORDER:
        r = ROWS[rid]
        if r["status"] in ("unverified", "withheld"):
            rows.append([row_link(rid), e(r["label"]), e(r["geo"]), '<span class="blank">&mdash;</span>', badge(r["status"]),
                         e(r["reason"]), e(r["obtain"]), src_link(r["source"])])
    body.append(table(["Row", "Item", "Place or entity", "Value", "Status", "Why it is blank", "How to obtain it", "Official source or tool"], rows, "data", "blank-t"))
    body.append(f'<h2 id="irregularities">Irregularities ({len(IRREG)})</h2>' + filter_box("irr-"))
    for label, tid, cls, pick in (("In official sources", "irr-s", "data", lambda it: bool(it["rows"])),
                                  ("In the repository, its coordination and its privacy", "irr-r", "site", lambda it: not it["rows"])):
        rows = []
        for it in IRREG:
            if not pick(it):
                continue
            ev = cites(it["rows"]) if it["rows"] else ""
            ev += " ".join(f'<a href="{e(u)}"' + (' target="_blank" rel="noopener noreferrer"' if u.startswith("http") else "") + f'>{e(t)}</a>' for t, u in it["links"])
            rows.append({"attrs": f' id="{it["id"]}"', "cells": [f'<span class="rid">{it["id"]}</span>', e(it["area"]), f'<strong>{e(it["title"])}</strong>',
                         e(snap(it["detail"])), ev, e(it["action"]), '<span class="badge review">Needs review</span>']})
        note = "" if cls == "data" else " These rows concern the repository itself, so they link to its records."
        body.append(f"<h3>{label}</h3>" + (f'<p class="note">{note.strip()}</p>' if note else ""))
        body.append(table(["No.", "Area", "Irregularity", "Detail", "Evidence and links", "Suggested action", "Status"], rows, cls, tid))
    lede = (f'{c["blank"]} values are blank ({c["unverified"]} unverified, {c["withheld"]} withheld for privacy) and {len(IRREG)} irregularities '
            'are recorded. Each has a link to the official source or record concerned. Status "needs review" means published here and blocking nothing.')
    return page("flagged.html", "Flagged for Review", lede, "".join(body), "Review")


def earlier_suggestion_pages():
    out = []
    for name in sorted(os.listdir(REPO)):
        p = os.path.join(REPO, name, "suggestions.html")
        if name.startswith("session-") and os.path.isfile(p):
            with open(p, encoding="utf-8", errors="replace") as fh:
                t = re.search(r"<title>(.*?)</title>", fh.read(), flags=re.S | re.I)
            out.append((name, html.unescape(t.group(1).strip()) if t else "Suggestions"))
    return out


def build_suggestions():
    S = SUGGEST["suggestions"]
    body = ['<div class="callout info"><strong>Nothing on this page has been done.</strong> These are proposals for improving the site so that it '
            'supports the decision better. Each is for a reviewer to accept, reject or change. Rows describe the site itself, so they point to the '
            'part of the site concerned rather than to an outside source.</div>', filter_box("sg-")]
    rows = []
    for s in S:
        rows.append({"attrs": f' id="{s["id"]}"', "cells": [f'<span class="rid">{s["id"]}</span>', e(s["area"]), f'<strong>{e(s["title"])}</strong>', e(s["what"]),
                     e(s["benefit"]), e(s["cost"]), e(s["needs"]), '<span class="badge review">For review</span><br><span class="note">Not implemented</span>']})
    body.append(table(["No.", "Area", "Proposal", "What would change", "How it helps the decision", "Cost and trade-offs", "Needs first", "Status"], rows, "site", "sg-t"))
    prev = earlier_suggestion_pages()
    if prev:
        body.append('<h2 id="earlier">Suggestions published by earlier sessions</h2><p>Earlier workbooks published their own suggestion lists, mostly about the property rather than the site. '
                    'They are preserved as written, are not selected or endorsed here, and are linked for the reviewer.</p>')
        body.append(table(["Workbook", "Page", "Status here"],
                          [[f"<code>{e(n)}/</code>", f'<a href="{e(n)}/suggestions.html">{e(t)}</a>', '<span class="badge na">Not selected</span>'] for n, t in prev], "site"))
    lede = f"{len(S)} proposals for improving this site. None has been implemented; all await review."
    return page("suggestions.html", "Suggestions for Review", lede, "".join(body), "Review")


def build_verification():
    c = counts()
    body = [f'<p>Every published value was read at its official source on {ACCESSED} and written into the ledger together with the text that was on the page. '
            'The build then enforces the rules below on every run. This page says what each check proves and, as importantly, what it does not.</p>']
    checks = VERIF["checks"] if VERIF else []
    body.append('<h2 id="checks">Checks run on every build</h2>')
    if checks:
        rows = [[e(ch["name"]), e(ch["proves"]), e(ch["does_not_prove"]), e(ch["result"]),
                 f'<span class="badge {"verified" if ch["ok"] else "review"}">{"Pass" if ch["ok"] else "Fail"}</span>'] for ch in checks]
        body.append(table(["Check", "What it proves", "What it does not prove", "Result", "Status"], rows, "site"))
    else:
        body.append('<p class="note">Run <code>python3 canonical/verify.py</code> to record the results here.</p>')
    body.append('<h2 id="status">What the statuses mean</h2>')
    body.append(table(["Status", "Meaning", "Rows"], [
        [badge("verified"), "Read at the official source on the access date. The quoted text is stored, and every number in the value appears in that text.", str(c["verified"])],
        [badge("computed"), "Calculated here from verified rows. The formula and inputs are shown, and the build recalculates it.", str(c["computed"])],
        [badge("unverified"), "Could not be confirmed from an official source. Left blank; nothing was estimated.", str(c["unverified"])],
        [badge("withheld"), "Would identify the property or the owner. Left blank on purpose.", str(c["withheld"])]], "site"))
    body.append('<h2 id="readlog">What was read at each source</h2>' + filter_box("read-"))
    used = {}
    for rid in ROW_ORDER:
        used[ROWS[rid]["source"]] = used.get(ROWS[rid]["source"], 0) + 1
    rows = [[f'<span class="rid">{s["id"]}</span>', e(s["publisher"]), src_link(s["id"]), e(s["note"]),
             f'<span class="badge {"verified" if s["read"] == "read" else "unverified"}">{"Read" if s["read"] == "read" else "Could not be read"}</span>',
             str(used.get(s["id"], 0))] for s in SOURCES["sources"]]
    body.append(table(["Source", "Publisher", "Link", "What was read, and limits", "Status", "Rows"], rows, "data", "read-t"))
    body.append('<h2 id="repo">Review of the rest of the repository</h2>')
    t = REVIEW["totals"]
    body.append(f'<p>{e(REVIEW["note"])} The scan read {t["files"]:,} files and {t["lines"]:,} lines in {t["workspaces"]} folders, including {t["pages"]:,} pages. '
                'It is a structural read: it does not claim that every sentence in the earlier workbooks was fact-checked.</p>')
    rows = []
    for w in REVIEW["workspaces"]:
        pii = sum(w["privacy_pattern_hits"].values())
        link = f'<a href="{e(w["workspace"])}/index.html">{e(w["workspace"])}/</a>' if os.path.isfile(os.path.join(REPO, w["workspace"], "index.html")) else f'<code>{e(w["workspace"])}</code>'
        rows.append([link, f'<span class="num">{w["files"]}</span>', f'<span class="num">{w["lines"]:,}</span>', f'<span class="num">{w["pages"]}</span>',
                     f'<span class="num">{w["official_links"]}</span>', f'<span class="num">{w["official_links_reread_today"]}</span>',
                     f'<span class="num">{pii}</span>', f'<a href="{GH}/tree/main/{e(w["workspace"])}" target="_blank" rel="noopener noreferrer">files ↗</a>'
                     if not w["workspace"].startswith("(") else f'<a href="{GH}" target="_blank" rel="noopener noreferrer">files ↗</a>'])
    body.append(table(["Folder", "Files", "Lines", "Pages", "Links to official sites", "Of which re-read by this session today",
                       "Privacy-pattern hits", "For manual review"], rows, "site", "repo-t"))
    body.append('<h2 id="crosscheck">Key figures: earlier workbooks against today</h2><p>For ten quantities, every value that earlier workbooks print, '
                'with the number of workbooks printing it, beside the value verified today. A difference usually means an older access date or a different definition, '
                'not an error; the pattern search is mechanical and can pick up an unrelated number.</p>')
    rows = []
    for f in REVIEW["figures"]:
        seen = ", ".join(f'{e(v["value"])} <span class="note">({v["workbooks"]})</span>' for v in f["values_in_earlier_workbooks"]) or "none found"
        rows.append([e(f["figure"]), f'<strong>{e(f["verified_today"])}</strong>', seen, cites([f["row"]])])
    body.append(table(["Quantity", "Verified today", "Values in earlier workbooks (number of workbooks)", "Evidence and official source"], rows, "data"))
    body.append('<h2 id="reread">Re-read on 2026-11-13: decision-critical figures</h2>')
    body.append('<p>On 2026-11-13 nine official pages were opened again, covering eleven ledger figures that drive the decision. Each row below says what the page showed, '
                'which numbers of the ledger value were found again in it, and which were not re-read. No value was changed by this re-read.</p>')
    rr = []
    for en in RECONFIRM["entries"]:
        ids = ", ".join(f'<span class="rid">{x["id"]}</span>' for x in en["rows"])
        conf = "; ".join(", ".join(x["confirmed_numbers"]) for x in en["rows"] if x["confirmed_numbers"]) or "none"
        notre = "; ".join(", ".join(x["not_reread"]) for x in en["rows"] if x["not_reread"]) or "none"
        rr.append([src_link(en["source"]), ids, e(conf), e(notre), e(en["result"]), e(en["note"])])
    body.append(table(["Source", "Ledger rows", "Numbers found again", "Not re-read", "Result", "What the page showed"], rr, "data", "reread-t"))
    sens = RECONFIRM["sensitivity"]
    body.append(f'<p><strong>Sensitivity test (10-year yield at the latest posted row).</strong> {e(sens["test"])} '
                f'The ranking of the six strategies {"changes" if sens["ranking_changed"] else "does not change"}; {e(sens["score_change_range"])}.</p>')
    body.append('<p class="note">Treasury: the model anchor (CM-001) is the 11/13/2026 row, 5.15%, which session 575eebba moved on the access date from the 11/10/2026 row (4.98%). '
                'CM-008 holds the same 11/13/2026 row from the earlier re-read. Runs at both values leave the ranking unchanged; the choice of anchor date is an open owner decision '
                '(see Flagged for Review, IR-33). Check 12 below re-tests every number found again against the ledger value and the text recorded on the re-read.</p>')
    body.append('<h2 id="yourself">Check a row yourself</h2><ol class="steps"><li>Open the row and follow its official source link.</li>'
                '<li>Open "What the source says" under the item and find that text on the page.</li>'
                '<li>If the page now says something else, the source has changed since the access date: note it on Flagged for Review.</li></ol>')
    lede = (f'{c["published"]} published values, each tied to quoted source text or to a shown calculation; {c["blank"]} left blank. '
            'The checks below run on every build and the site is not published if one fails.')
    return page("verification.html", "Verification", lede, "".join(body), "Review")


def build_sources():
    used = {}
    for rid in ROW_ORDER:
        used.setdefault(ROWS[rid]["source"], []).append(rid)
    rows = []
    for s in SOURCES["sources"]:
        n = len(used.get(s["id"], []))
        rows.append({"attrs": f' id="{s["id"]}"', "cells": [
            f'<span class="rid">{s["id"]}</span>', e(s["publisher"]),
            f'<a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["title"])}<span aria-hidden="true"> ↗</span></a>',
            e(s["kind"]), e(s["published"]) or "&mdash;", e(s["accessed"]),
            f'<span class="badge {"verified" if s["read"] == "read" else "unverified"}">{"Read" if s["read"] == "read" else "Could not be read"}</span>', str(n)]})
    body = [filter_box("src-"), table(["Source", "Publisher", "Document", "Kind", "Published or as of", "Read on", "Status", "Rows"], rows, "data", "src-t")]
    kinds = {}
    for s in SOURCES["sources"]:
        kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
    lede = (f'{len(SRC)} sources, all government bodies or filings lodged with a securities regulator: '
            + ", ".join(f"{v} {k}" for k, v in sorted(kinds.items(), key=lambda kv: -kv[1])) + ". No aggregator, broker report or news article is used.")
    return page("sources.html", "Sources", lede, "".join(body), "Review")


def build_requirements():
    rows = []
    for r in REQS:
        links = " ".join(f'<a href="{e(p.strip())}">{e(p.strip())}</a>' if p.strip().endswith(".html") else f"<code>{e(p.strip())}</code>" for p in r["where"].split(","))
        rows.append([f'<span class="rid">{r["id"]}</span>', e(r["requirement"]), links,
                     f'<span class="badge {"verified" if r["status"].startswith("Done") else "unverified"}">{e(r["status"])}</span>', e(r["note"])])
    body = ['<p>Each requirement in the brief, where it is met on this site, and anything still outstanding. Rows describe the site itself.</p>',
            table(["No.", "Requirement", "Where it is met", "Status", "Note"], rows, "site")]
    return page("requirements.html", "Requirements", f"{len(REQS)} requirements from the brief, traced to pages.", "".join(body), "About")


def build_privacy():
    h = ARCHIVE["history"]
    rows = [
        ["Owner's name, contact details, identity", "Never collected. The owner is <code>[OWNER-01]</code> throughout.", "Build stops if an e-mail address, telephone number or a known individual's name is about to be published."],
        ["Property address, parcel number, map location", "Never collected. The property is <code>[PROPERTY-01]</code>. No parcel was looked up, because the lookup itself would identify it.", "Build stops on a street-address or parcel-number pattern."],
        ["Rent, lease terms, value, loan, tax basis", "Left blank. They are listed with how to obtain them privately.", "Build stops if a blank row carries a value."],
        ["Names of individuals in official documents", "Replaced with a placeholder ([OFFICER] or [name withheld], 2026-11-13) in the earlier folders. Company and agency names are kept.", "Names seen during research are stored only as salted hashes; the build hashes every pair of adjacent capitalised words and stops on a match."],
        ["Tracking, cookies, outside scripts or fonts", "None. The site is plain pages, one style sheet and one small script, all served from this repository.", "No address outside this site is loaded by any page."],
        ["Search within the site", "The filter boxes work in the reader's browser. Nothing typed is sent anywhere.", "The script has no network calls."],
    ]
    body = ['<p>Privacy was the first rule of the work. This page states what is not collected and how the build enforces it.</p>',
            table(["Information", "How it is handled", "How the build enforces it"], rows, "site")]
    body.append('<h2>Open privacy items for the owner</h2>')
    body.append(table(["Item", "Detail", "Where it is tracked"], [
        ["A personal e-mail address in the repository's history", f'{h["commits_with_personal_provider_email"]} of {h["commits_on_main"]} commits on the main branch carry one personal e-mail address in the author field (measured {e(ARCHIVE["measured"])}). It is not on this site and is not reproduced here.', '<a href="flagged.html#IR-30">IR-30</a>, <a href="suggestions.html#SG-18">SG-18</a>'],
        ["The site and repository are public", "Nobody is named, but the analysis is readable by anyone.", '<a href="flagged.html#IR-31">IR-31</a>, <a href="suggestions.html#SG-17">SG-17</a>'],
        ["Earlier workbooks", "They were scanned for the same patterns; the counts are on the Verification page. They are preserved as their sessions wrote them.", '<a href="verification.html#repo">Verification</a>']], "site"))
    return page("privacy.html", "Privacy", "No personal or parcel-identifying information is collected, stored or published, and the build refuses to publish anything that looks like it.", "".join(body), "About")


def discover_workbooks():
    out = []
    for name in sorted(os.listdir(REPO)):
        idx = os.path.join(REPO, name, "index.html")
        if (name.startswith("session-") or name == "docs") and os.path.isfile(idx):
            with open(idx, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            t = re.search(r"<title>(.*?)</title>", text, flags=re.S | re.I)
            pages = len([f for f in os.listdir(os.path.join(REPO, name)) if f.endswith(".html")])
            out.append({"folder": name, "title": re.sub(r"\s+", " ", html.unescape(t.group(1))).strip() if t else name, "pages": pages})
    return out


def build_archive():
    books = discover_workbooks()
    body = ['<div class="callout info"><strong>History, not guidance.</strong> Earlier sessions each published a complete workbook. They are kept exactly as written, '
            'at their original addresses, and are not endorsed by this site: they use other access dates, other assumptions and in several cases an assumed rent. '
            'Read this site first.</div>']
    body.append(f'<h2 id="workbooks">Earlier workbooks ({len(books)})</h2>' + filter_box("wb-"))
    rows = []
    for b in books:
        note = ("The earlier root site: 17 pages by several sessions, moved here unchanged in content."
                if b["folder"] == "session-742b6a03" else "")
        rows.append([f'<code>{e(b["folder"])}/</code>', f'<a href="{e(b["folder"])}/index.html">{e(b["title"])}</a>' + (f'<br><span class="note">{note}</span>' if note else ""),
                     f'<span class="num">{b["pages"]}</span>', '<span class="badge na">Archived</span>',
                     f'<a href="{GH}/tree/main/{e(b["folder"])}" target="_blank" rel="noopener noreferrer">files ↗</a>'])
    body.append(table(["Folder", "Opens", "Pages", "Status", "For manual review"], rows, "site", "wb-t"))
    prs = ARCHIVE["open_pull_requests"]
    body.append(f'<h2 id="pulls">Open pull requests ({len(prs)})</h2><p>Measured {e(ARCHIVE["measured"])}. They belong to other sessions and were left as they are.</p>')
    body.append(table(["No.", "Title", "Branch", "Opened", "Link"],
                      [[f'#{p["number"]}', e(p["title"]) + (' <span class="badge na">draft</span>' if p["draft"] else ""), f'<code>{e(p["branch"])}</code>', e(p["opened"]),
                        f'<a href="{e(p["url"])}" target="_blank" rel="noopener noreferrer">open ↗</a>'] for p in prs], "site"))
    br = ARCHIVE["branches_with_unmerged_work"]
    body.append(f'<h2 id="branches">Branches with work that is not on the main branch ({len(br)})</h2><p>Their content was not verified by this session and is not published here. '
                f'A further {ARCHIVE["branches_with_only_log_or_claim_commits"]} branches differ from the main branch only by log or claim commits.</p>')
    body.append(table(["Branch", "Commits not on main", "Files not on main", "Folders", "Last commit", "Link"],
                      [[f'<code>{e(b["branch"])}</code>', f'<span class="num">{b["commits_not_on_main"]}</span>', f'<span class="num">{b["files_not_on_main"]}</span>',
                        e(", ".join(b["folders"])) or "&mdash;", e(b["last_commit"]), f'<a href="{e(b["url"])}" target="_blank" rel="noopener noreferrer">open ↗</a>'] for b in br], "site"))
    lede = (f"{len(books)} earlier workbooks, preserved at their original addresses, plus the pull requests and branches that never reached the main branch.")
    return page("workspaces.html", "Archive of earlier workbooks", lede, "".join(body), "About")


def build_deployment():
    recs = DEPLOY.get("records", [])
    rows = []
    for r in recs:
        rows.append([e(r["when"]), e(r["what"]), f'<a href="{e(r["pr_url"])}" target="_blank" rel="noopener noreferrer">{e(r["pr"])} ↗</a>',
                     e(r["merge"]), e(r["checks"]), e(r["pages"])])
    body = ['<p>Where the site is served from, and the record of each merge. Rows describe the site itself.</p>',
            table(["Item", "Value"], [
                ["Public address", f'<a href="{LIVE}">{LIVE}</a>'],
                ["Served from", "The main branch of the repository, root folder, by GitHub Pages"],
                ["Repository", f'<a href="{GH}" target="_blank" rel="noopener noreferrer">{GH} ↗</a>'],
                ["Build", "<code>python3 canonical/model.py &amp;&amp; python3 canonical/review_repo.py &amp;&amp; python3 canonical/build_site.py &amp;&amp; python3 canonical/verify.py</code>"],
                ["Checks on every push", f'<a href="{GH}/actions/workflows/verify.yml" target="_blank" rel="noopener noreferrer">verify workflow ↗</a>'],
                ["Coordination record", f'<a href="{GH}/blob/main/COORDINATION.md" target="_blank" rel="noopener noreferrer">COORDINATION.md ↗</a>']], "site")]
    body.append('<h2 id="records">Merge and deployment record</h2>')
    body.append(table(["When (UTC)", "What", "Pull request", "Merge", "Checks", "Pages"], rows, "site") if rows
                else '<p class="note">No record yet.</p>')
    return page("deployment.html", "Deployment", "How the site is built and published, and the record of each merge.", "".join(body), "About")


REDIRECT = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=workspaces.html">
<title>Archive | Sell or renew</title><link rel="canonical" href="workspaces.html"></head>
<body><p>This page moved. <a href="workspaces.html">Open the archive of earlier workbooks</a>.</p></body></html>
"""


# ----------------------------------------------------------------------------- checks and output
def ledger_rules():
    for rid in ROW_ORDER:
        r = ROWS[rid]
        s = SRC.get(r["source"])
        assert s and s["url"].startswith("https://"), f"{rid}: no official source"
        if r["status"] == "verified":
            assert r["value"].strip() and r["quote"].strip(), f"{rid}: verified without value or quote"
            assert nums(r["value"]) <= nums(r["quote"]), f"{rid}: value not in quote"
            assert s["read"] == "read", f"{rid}: verified from a source that was not read"
        elif r["status"] == "computed":
            assert r["value"].strip() and r["calc"]["inputs"], rid
        else:
            assert not r["value"].strip(), f"{rid}: blank row carries a value"
            assert r["reason"].strip() and r["obtain"].strip(), f"{rid}: blank row without reason"


def check_links(pages):
    ids = {slug: set(re.findall(r'\bid="([^"]+)"', text)) for slug, text in pages.items()}
    problems = []
    for slug, text in pages.items():
        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(("http://", "https://", "mailto:")):
                if href.startswith("http://"):
                    problems.append(f"{slug}: insecure link {href}")
                continue
            target, _, frag = href.partition("#")
            target = target or slug
            if target in pages:
                if frag and frag not in ids[target]:
                    problems.append(f"{slug}: no anchor #{frag} in {target}")
            elif not os.path.exists(os.path.join(REPO, target)):
                problems.append(f"{slug}: missing {target}")
    assert not problems, "broken links:\n  " + "\n  ".join(problems[:40])


# ----------------------------------------------------------------------------- brief items (session 4112432a)
# Three pages that answer named items of the brief: the decision-gate progress board and brief coverage map (W-03,
# with W-01 to W-10 and the feature list), the browser-only after-tax calculator, and the one-page printable advisor
# summary (W-10). Every figure they print is a ledger value, linked to its official source, or a labelled blank.

def ref_value(rid):
    """The published value of a verified or computed ledger row, as shown on the site (never typed by hand)."""
    r = ROWS[rid]
    assert r["status"] in ("verified", "computed"), f"{rid} is blank and cannot be used as a reference value"
    return r["value"]


def ref_percent(rid):
    """A percentage read from a ledger value, e.g. '20%' or '3.8 percent' -> '20' or '3.8'. Used by the calculator's
    'use the verified figure' buttons; the number comes from the ledger, not from this file."""
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*(?:%|percent)", ref_value(rid))
    assert m, f"{rid}: {ref_value(rid)!r} does not begin with a percentage"
    return m.group(1)


def status_pill(text):
    cls = {"Done": "verified", "Partly": "computed", "Open": "unverified"}
    key = next((k for k in cls if text.startswith(k)), None)
    css = cls.get(key, "withheld")
    return f'<span class="badge {css}">{e(text)}</span>'


BRIEF_ITEMS = [
    # (ref, brief item, status, what the site has now, what is missing and why, official source id, source text)
    ("W-01", "Replace city and county proxies with trade-area figures", "Blocked: private location",
     "City and county figures are on the People and place and Economy pages. They are still the proxies.",
     "A trade-area figure needs the parcel's location. The location is kept in the private workspace, so no trade-area figure is published.",
     "S-CENSUS", "Census Bureau QuickFacts, the source of the city and county figures"),
    ("W-02", "Extend the private worksheet to a sell-versus-hold comparison", "Partly",
     "A six-strategy scenario model (Decision analysis and Projections) and a browser after-tax calculator with blank inputs (Calculator).",
     "The owner's rent, basis, loan and tax bracket are not in this repository. The private worksheet stays offline.",
     "S-IRS-409", "IRS Topic 409, capital gains rates and the 25% rate on real-property depreciation"),
    ("W-03", "Decision-gate progress board", "Done",
     "Gates G1 to G7 are on this page, each with what closes it and the official source for it.",
     "The gates close only when the private file is checked. No gate is marked closed in this repository.",
     "S-IRS-8824", "IRS Form 8824, the 45-day and 180-day exchange deadlines used in gate G6"),
    ("W-04", "Parcel-level hazard screening", "Blocked: private location",
     "Regional hazard context on the Hazards and insurance page. No parcel result is published.",
     "The parcel's zone status for earthquake, flood and fire must be looked up privately in the official maps, with the parcel identifier kept offline.",
     "S-CGS", "California Geological Survey, earthquake zone maps"),
    ("W-10", "One-page printable summary for advisors", "Done",
     "Advisor summary: one letter-size page, printed from the browser, with every figure linked to its official source.",
     "The page carries no owner or parcel detail, so an adviser who needs the parcel must use the private file.",
     "S-TSY", "U.S. Treasury daily par yield curve, the 10-year yield used in the summary"),
    ("F-01", "A private calculator that runs in the reader's browser", "Done",
     "Calculator: after-tax sale against renewal, every input blank. It makes no network call and stores nothing.",
     "The owner's inputs must be typed in by the reader. A winner is shown only when every input is entered and checked.",
     "S-IRS-409", "IRS Topic 409, capital gains rates"),
    ("F-02", "Neighbourhood-level data around the parcel", "Blocked: private location",
     "Not published. City, county and metro data only.",
     "Neighbourhood data needs the parcel's location in a secure workflow, as the brief requires.",
     "S-ZIMAS", "L.A. City Planning zoning and parcel lookup, used privately"),
    ("F-03", "An after-tax module", "Partly",
     "The calculator's tax step: federal long-term gain, the 25% depreciation rate, the 3.8% investment income tax and the California rate.",
     "The owner's basis, depreciation, loan and bracket are needed. Depreciation deductions and loss limits are not modelled (see Flagged for Review).",
     "S-IRS-559", "IRS Topic 559, net investment income tax"),
    ("F-04", "Price the short-lease discount from real quotes", "Blocked: no verified quote",
     "Not priced. The buyer's yield for this lease is a blank row.",
     "No official source gives a quote for this lease. A quote needs brokers' opinions, which are private until obtained.",
     "S-NNN-8K", "SEC filing by a listed net-lease REIT, the public sale and purchase yields"),
    ("F-05", "Tract-level trend evidence alongside the regional figures", "Blocked: private location",
     "Regional and county trends only.",
     "The Census tract depends on the location, which must be selected in the secure workflow.",
     "S-CENSUS", "Census Bureau QuickFacts"),
    ("F-06", "Use the location only in a secure workflow to select Census tracts and planning, traffic, school and competitor evidence", "Blocked: private location",
     "County school counts and the City planning tool are listed as sources. Traffic and competitor evidence are not sourced yet.",
     "The location is used only offline. Traffic counts and competitor lists are not yet sourced from an official site.",
     "S-CDE", "California Department of Education, school data"),
    ("F-07", "Privately check seismic, flood and fire maps, engineering and insurance; stress loss of rent, repairs and exit liquidity", "Partly",
     "Regional risks and stress cases in the projection model. Insurance and engineering are blank rows.",
     "Parcel map checks, an engineering inspection and an insurance quote are private and not yet done.",
     "S-CDI", "California Department of Insurance, consumer guidance on earthquake cover"),
    ("F-08", "Parcel's actual zone status for earthquake, fire and flood, replacing the regional context", "Blocked: private location",
     "Regional hazard figures are on the Hazards and insurance page.",
     "Replacing the regional context needs the parcel's zone status, from the official maps, checked privately.",
     "S-FEMA-MSC", "FEMA flood maps, the official flood-zone lookup"),
    ("F-09", "Create and back-test a versioned cash-flow model when verified inputs and comparable history exist", "Not started: conditions not met",
     "A versioned scenario model with labelled assumptions and a test suite (Projections).",
     "No back-test is run: the comparable history with verified inputs does not yet exist, and the private rent and basis are missing.",
     "S-NNN-8K", "SEC filing by a listed net-lease REIT, the comparable yields it reports"),
    ("F-10", "Same-store sales, unit counts, closures and franchise rental revenue, read as a direction over several quarters", "Partly",
     "Same-store sales for four periods, unit counts for two dates, and one quarter of franchise rent (Tenant page).",
     "More quarters are needed before the direction is reliable. Each new quarter should be added from the next filing.",
     "S-JACK-8K", "SEC: the tenant's quarterly results, the source of the same-store and unit figures"),
]

DECISION_GATES = [
    # (gate, what must be true, status, what closes it, official source id, source text)
    ("G1", "Lease facts: expiry date, rent, renewal options and notice dates", "Open: private file",
     "A one-page attorney abstract of the lease and every amendment, checked against the notice calendar. Check the County Recorder's index for a recorded memorandum.",
     "S-RRCC", "L.A. County Registrar-Recorder, the index of recorded documents"),
    ("G2", "The tenant's answer to an early extension", "Open",
     "A written answer from the tenant. Its own filings show that it is closing restaurants and selling real estate, with the timing limited.",
     "S-JACK-8K", "SEC: the tenant's quarterly results, which describe the closure programme"),
    ("G3", "Price evidence: two broker opinions, as is and as extended", "Open: private",
     "Two opinions with comparables. Public yields are on the NNN REIT filings, but they are not a quote for this lease.",
     "S-NNN-8K", "SEC filing by a listed net-lease REIT, public sale and purchase yields"),
    ("G4", "After-tax number for a cash sale and for renewal", "Open: inputs needed",
     "The calculator, run with the owner's basis, depreciation, loan and brackets, every input checked against its document.",
     "S-IRS-409", "IRS Topic 409, capital gains rates"),
    ("G5", "Parcel hazard screen: earthquake, flood, fire and insurance", "Open: private",
     "Official map checks and an insurance quote, both kept in the private file.",
     "S-CGS", "California Geological Survey, earthquake zone maps"),
    ("G6", "Exchange timing, if the owner sells and exchanges", "Open: depends on G1 to G4",
     "A replacement property named within the 45-day window and received within the 180-day window.",
     "S-IRS-8824", "IRS Form 8824, like-kind exchanges"),
    ("G7", "Final choice, sell or renew", "Open: depends on G1 to G6",
     "A winner is shown only when the calculator's inputs are all verified. The decision rule is on the Decision analysis page.",
     "S-TSY", "U.S. Treasury daily par yield curve, the benchmark for the discount rate"),
]

INTERNAL_ITEMS = [
    ("Keep identifiers, lease files and owner finances offline; publish only aggregate, non-identifying findings",
     "Partly: the site holds no identifiers. The GitHub Pages source is still the whole repository, which the owner must switch (see Flagged for Review)."),
    ("Executive summary of the important details", "Done: Executive summary page."),
    ("Suggestions for improving the site, nothing implemented before review", "Done: Suggestions for Review page, each marked not implemented."),
    ("Questions, information and answers needed before a decision", "Done: Questions to answer page."),
    ("Requirements traced to pages", "Done: Requirements page, one row per requirement."),
]


def _prose_ok(text, where):
    check_prose(text, [], where, anywhere=True)


for _n, _it in enumerate(BRIEF_ITEMS):
    for _t in _it[1:5]:
        _prose_ok(_t, f"brief item {_it[0]}")
for _n, _g in enumerate(DECISION_GATES):
    for _t in _g[1:4]:
        _prose_ok(_t, f"decision gate {_g[0]}")
for _a, _b in INTERNAL_ITEMS:
    _prose_ok(_a + " " + _b, "internal item")


def build_progress():
    n_done = sum(1 for it in BRIEF_ITEMS if it[2].startswith("Done"))
    n_part = sum(1 for it in BRIEF_ITEMS if it[2].startswith("Partly"))
    n_block = sum(1 for it in BRIEF_ITEMS if it[2].startswith("Blocked") or it[2].startswith("Not started"))
    assert n_done + n_part + n_block == len(BRIEF_ITEMS)
    cards = (f'<div class="cards"><div class="kpi"><div class="kpi-v">{n_done}</div><div class="kpi-l">Done</div>'
             f'<div class="kpi-s">of {len(BRIEF_ITEMS)} brief items</div></div>'
             f'<div class="kpi"><div class="kpi-v">{n_part}</div><div class="kpi-l">Partly done</div>'
             f'<div class="kpi-s">needs owner inputs or more evidence</div></div>'
             f'<div class="kpi"><div class="kpi-v">{n_block}</div><div class="kpi-l">Blocked or not started</div>'
             f'<div class="kpi-s">needs the private location or verified inputs</div></div></div>')
    body = [cards]
    body.append('<p class="note"><strong>Status key.</strong> Done: on the site. Partly: some of it is on the site, the rest needs '
                'owner inputs or more evidence. Blocked: needs the parcel location, which is kept in the private workspace, or a '
                'verified quote that does not yet exist. Not started: the conditions for it are not met. Open: a gate that is not yet '
                'closed. Nothing here is marked closed unless the evidence is in the repository.</p>')
    body.append('<h2 id="items">Brief items</h2>')
    body.append(filter_box("items-t"))
    rows = []
    for ref, item, status, now, missing, sid, stext in BRIEF_ITEMS:
        rows.append({"cells": [f'<span class="rid">{e(ref)}</span>', e(item), status_pill(status), e(now), e(missing),
                               src_link(sid) + f'<span class="note"> {e(stext)}</span>']})
    body.append(table(["Ref", "Brief item", "Status", "What the site has now", "What is missing, and why", "Official source"],
                      rows, "data", "items-t"))
    body.append('<h2 id="gates">Decision gates</h2>')
    body.append('<p class="note">A gate closes when its evidence is in the private file and checked. The gates are the order in which the '
                'decision can be made. G7 depends on the others.</p>')
    rows = []
    for gate, must, status, closes, sid, stext in DECISION_GATES:
        rows.append({"cells": [f'<span class="rid">{e(gate)}</span>', e(must), status_pill(status), e(closes),
                               src_link(sid) + f'<span class="note"> {e(stext)}</span>']})
    body.append(table(["Gate", "What must be true", "Status", "What closes it", "Official source"], rows, "data", "gates-t"))
    body.append('<h2 id="internal">Internal items</h2>')
    body.append('<p class="note">These items concern the site, the privacy of the owner\'s files, or the review process. No '
                'outside data applies to them, so they carry no official-source column. Each is listed with its status.</p>')
    rows = [[e(a), e(b)] for a, b in INTERNAL_ITEMS]
    body.append(table(["Item", "Status"], rows, "site", "internal-t"))
    lede = ("The brief's numbered items (W-01 to W-10) and the feature items that depend on outside data, each with a status, "
            "what is missing and why, and the official source it depends on. The decision gates set the order of the decision. "
            "Nothing private is shown.")
    return page("progress.html", "Progress board", lede, "".join(body), "Decide")


CALC_JS = r"""
(function(){
  var NIIT = __NIIT__;
  function $(id){ return document.getElementById(id); }
  function num(id){ var el=$(id); if(!el || el.value===''){ return null; } var x=Number(el.value); return isFinite(x)?x:null; }
  function sel(id){ return $(id).value; }
  var FIELDS = [
    ['s_price','Sale price'], ['s_cost','Sale costs the seller pays (enter 0 if none)'], ['s_loan','Loan paid off at sale (enter 0 if none)'],
    ['s_basis','Adjusted tax basis'], ['s_dep','Depreciation taken since purchase (enter 0 if none)'],
    ['s_r1250','Rate on depreciation recapture'], ['s_rltcg','Federal rate on the rest of the gain'],
    ['s_rca','California rate on the gain'], ['s_niit','Investment income tax applies (yes or no)'],
    ['h_rent','Current yearly base rent'], ['h_esc','Rent increase each year (enter 0 if flat)'], ['h_years','Years of renewed term to model (1 to 30)'],
    ['h_fed','Your federal income tax rate on the rent'], ['h_ca','Your California rate on the rent'],
    ['h_niit','Investment income tax applies to the rent (yes or no)'], ['h_end_net','Net sale proceeds at the end of the term, after costs and loan'],
    ['h_end_basis','Adjusted tax basis at the end of the term'], ['h_end_dep','Depreciation taken by the end of the term (enter 0 if none)'],
    ['h_disc','Discount rate, after tax (the rate you use to compare cash over time)']
  ];
  var PCT = ['s_r1250','s_rltcg','s_rca','h_esc','h_fed','h_ca','h_disc'];
  var YN = ['s_niit','h_niit'];
  function money(x){ return (x < 0 ? '\u2212' : '') + '$' + Math.round(Math.abs(x)).toLocaleString('en-US'); }
  function taxOnGain(gain, dep, r1250, rltcg, niit, rca){
    if (gain <= 0) { return 0; }
    var rec = Math.min(Math.max(dep, 0), gain);
    var rest = gain - rec;
    return rec*r1250 + rest*rltcg + (niit ? gain*NIIT/100 : 0) + gain*rca;
  }
  function missingFields(){
    var miss = [];
    FIELDS.forEach(function(f){
      var id=f[0];
      if (YN.indexOf(id)>=0) { if (sel(id)==='') miss.push(f[1]); return; }
      var v = num(id);
      if (v === null) { miss.push(f[1]); return; }
      if (PCT.indexOf(id)>=0 && (v<0 || v>100)) miss.push(f[1] + ' (must be between 0 and 100)');
      if (id==='h_years' && (v<1 || v>30 || Math.floor(v)!==v)) miss.push(f[1] + ' (whole years from 1 to 30)');
      if (id!=='h_years' && PCT.indexOf(id)<0 && v<0) miss.push(f[1] + ' (cannot be negative)');
    });
    if (num('s_price') !== null && num('s_price') <= 0) miss.push('Sale price (must be above 0)');
    return miss;
  }
  function run(){
    var out = $('calc-out');
    var miss = missingFields();
    if (miss.length){
      out.innerHTML = '<div class="calc-warn"><p><strong>Not calculated yet.</strong> These inputs are missing or not valid:</p><ul>' +
        miss.map(function(m){ return '<li>' + m.replace(/</g,'&lt;') + '</li>'; }).join('') + '</ul></div>';
      return;
    }
    var price=num('s_price'), cost=num('s_cost'), loan=num('s_loan'), basis=num('s_basis'), dep=num('s_dep');
    var r1250=num('s_r1250')/100, rltcg=num('s_rltcg')/100, rca=num('s_rca')/100, niitS = sel('s_niit')==='yes';
    var gain = price - cost - basis;
    var taxSale = taxOnGain(gain, dep, r1250, rltcg, niitS, rca);
    var now = price - cost - loan - taxSale;
    var rent=num('h_rent'), esc=num('h_esc')/100, years=num('h_years'), fed=num('h_fed')/100, ca=num('h_ca')/100;
    var niitR = sel('h_niit')==='yes' ? NIIT/100 : 0;
    var disc=num('h_disc')/100, taxRent = fed + ca + niitR;
    var pvRent = 0, i, r;
    for (i=1; i<=years; i++){
      r = rent * Math.pow(1+esc, i-1);
      pvRent += r * (1 - taxRent) / Math.pow(1+disc, i);
    }
    var endNet=num('h_end_net'), endBasis=num('h_end_basis'), endDep=num('h_end_dep');
    var taxEnd = taxOnGain(endNet - endBasis, endDep, r1250, rltcg, niitS, rca);
    var pvEnd = (endNet - taxEnd) / Math.pow(1+disc, years);
    var hold = pvRent + pvEnd;
    var diff = now - hold;
    var checked = $('attest').checked;
    var h = '<h3>Sell now</h3><table class="tbl calc-t"><tbody>' +
      '<tr><td>Sale price</td><td>' + money(price) + '</td></tr>' +
      '<tr><td>Less sale costs and loan paid off</td><td>' + money(-(cost+loan)) + '</td></tr>' +
      '<tr><td>Gain for tax (price less costs less basis)</td><td>' + money(gain) + (gain<0?' (a loss: no tax is modelled)':'') + '</td></tr>' +
      '<tr><td>Less tax on the sale</td><td>' + money(-taxSale) + '</td></tr>' +
      '<tr class="calc-total"><th scope="row">After-tax cash today</th><th>' + money(now) + '</th></tr></tbody></table>';
    h += '<h3>Renew (negotiated rent)</h3><table class="tbl calc-t"><tbody>' +
      '<tr><td>Present value of after-tax rent over ' + years + ' years</td><td>' + money(pvRent) + '</td></tr>' +
      '<tr><td>Present value of the after-tax sale at the end of the term</td><td>' + money(pvEnd) + '</td></tr>' +
      '<tr class="calc-total"><th scope="row">Present value today</th><th>' + money(hold) + '</th></tr></tbody></table>';
    if (!checked){
      h += '<div class="calc-warn"><p><strong>No comparison shown.</strong> Tick the check box below, once every input has been checked against its document. Until then the calculator does not say which option is better.</p></div>';
    } else {
      var word = diff > 0 ? 'Selling now is worth more' : (diff < 0 ? 'Renewing is worth more' : 'The two are equal');
      h += '<div class="calc-result"><p><strong>' + word + '</strong>' + (diff!==0 ? ' by ' + money(Math.abs(diff)) : '') +
        ' in today\'s after-tax money, at the discount rate you entered.</p><p class="note">This is arithmetic on the inputs you entered. It is not advice, and it is not a decision.</p></div>';
    }
    out.innerHTML = h;
  }
  function clearAll(){
    FIELDS.forEach(function(f){ var el=$(f[0]); if(el){ el.value=''; } });
    $('attest').checked=false; $('calc-out').innerHTML='<p class="note">Cleared. Nothing was stored.</p>';
  }
  Array.prototype.forEach.call(document.querySelectorAll('button[data-set]'), function(b){
    b.addEventListener('click', function(){ $(b.getAttribute('data-set')).value = b.getAttribute('data-val'); });
  });
  $('calc-run').addEventListener('click', run);
  $('calc-clear').addEventListener('click', clearAll);
})();
"""


def _rate_button(field, rid, label):
    return (f'<button type="button" class="chip" data-set="{field}" data-val="{ref_percent(rid)}" '
            f'title="Fill this box with the figure from {rid}">Use the verified figure ({rid})</button>')


def build_calculator():
    niit = ref_percent("TX-043")
    js = CALC_JS.replace("__NIIT__", niit)
    fields = [
        ("Sale now", [
            ("s_price", "Sale price (USD)", "The price the buyer would pay for the property as it is.", None),
            ("s_cost", "Sale costs the seller pays (USD)", "Broker fees, transfer taxes and other seller costs. Enter 0 if none.", None),
            ("s_loan", "Loan paid off at sale (USD)", "Enter 0 if the property has no loan.", None),
            ("s_basis", "Adjusted tax basis (USD)", "From your tax records. Ask your tax adviser to confirm the figure.", None),
            ("s_dep", "Depreciation taken since purchase (USD)", "From the tax returns. Enter 0 if none.", None),
            ("s_r1250", "Rate on depreciation recapture (%)", f"Maximum federal rate on the part of the gain from past depreciation: {ref_value('TX-042')} (IRS Topic 409).",
             _rate_button("s_r1250", "TX-042", "")),
            ("s_rltcg", "Federal rate on the rest of the gain (%)", f"Enter the rate for your taxable income. The top rate is {ref_value('TX-040')} (IRS Topic 409).",
             _rate_button("s_rltcg", "TX-040", "")),
            ("s_rca", "California rate on the gain (%)", f"California taxes gains at ordinary rates. The top rate is {ref_value('TX-060')} including the additional 1% (FTB).",
             _rate_button("s_rca", "TX-060", "")),
        ]),
        ("Renew (negotiated)", [
            ("h_rent", "Current yearly base rent (USD)", "From the lease abstract and the rent ledger. Not the owner's guess.", None),
            ("h_esc", "Rent increase each year (%)", "From the lease. Enter 0 if the rent is flat.", None),
            ("h_years", "Years of renewed term to model", "A whole number from 1 to 30.", None),
            ("h_fed", "Your federal income tax rate on the rent (%)", "Your marginal federal rate, from your own return.", None),
            ("h_ca", "Your California rate on the rent (%)", "Your marginal California rate, from your own return.", None),
            ("h_end_net", "Net sale proceeds at the end of the term (USD)", "After sale costs and any loan at that time.", None),
            ("h_end_basis", "Adjusted tax basis at the end of the term (USD)", "From the tax records at that date.", None),
            ("h_end_dep", "Depreciation taken by the end of the term (USD)", "Enter 0 if none.", None),
            ("h_disc", "Discount rate, after tax (%)", f"The rate for comparing cash over time. For reference, the 10-year Treasury yield was {ref_value('CM-001')} (U.S. Treasury). It is a benchmark, not a recommendation.",
             None),
        ]),
    ]
    sel_fields = {"s_niit": ("Investment income tax applies to the gain?", f"The investment income tax is {ref_value('TX-043')} on the lesser of your net investment income or your income above {ref_value('TX-044')} (IRS Topic 559). The page applies the rate to the whole gain, so answer yes only if you are above the threshold, and expect it to overstate the tax when you are only just above it."),
                  "h_niit": ("Investment income tax applies to the rent?", f"Rents and net gains from real estate are within the tax (IRS Topic 559). Answer yes only if you are above {ref_value('TX-044')}; the page applies the rate to the whole rent, which can overstate it.")}
    body = ['<div class="calc-note"><p><strong>Private to you.</strong> Nothing you type is sent, saved or shared. This page makes no network call, '
            'stores nothing, and forgets everything when you close it. Keep your figures in the private file and type only what you need.</p>'
            '<p>Every box starts blank. No figure is filled in for you, except the buttons that copy a verified rate from the ledger.</p></div>']
    body.append('<form id="calc" class="calc" autocomplete="off" onsubmit="return false">')
    for legend, items in fields:
        body.append(f'<fieldset class="calc-group"><legend>{e(legend)}</legend>')
        for fid, label, hint, extra in items:
            body.append(f'<div class="calc-row"><label for="{fid}">{e(label)}</label>'
                        f'<input id="{fid}" type="number" step="any" inputmode="decimal" min="0">'
                        f'<p class="hint">{fill(hint)}</p>{extra or ""}</div>')
        if legend == "Sale now":
            for sid in ("s_niit",):
                label, hint = sel_fields[sid]
                body.append(f'<div class="calc-row"><label for="{sid}">{e(label)}</label><select id="{sid}"><option value="">Choose</option>'
                            f'<option value="yes">Yes</option><option value="no">No</option></select><p class="hint">{fill(hint)}</p></div>')
        else:
            for sid in ("h_niit",):
                label, hint = sel_fields[sid]
                body.append(f'<div class="calc-row"><label for="{sid}">{e(label)}</label><select id="{sid}"><option value="">Choose</option>'
                            f'<option value="yes">Yes</option><option value="no">No</option></select><p class="hint">{fill(hint)}</p></div>')
        body.append('</fieldset>')
    body.append('<fieldset class="calc-group"><legend>Check before the comparison is shown</legend>'
                '<label class="check"><input type="checkbox" id="attest"> I have checked every amount above against its document '
                '(the lease, the rent ledger, the tax records and my return). I accept that the calculator leaves out '
                'depreciation deductions, the loss limit and any state rule it does not name.</label></fieldset>')
    body.append('<div class="calc-actions"><button type="button" id="calc-run" class="btn">Calculate</button> '
                '<button type="button" id="calc-clear" class="btn ghost">Clear every box</button></div></form>')
    body.append('<section id="calc-out" class="calc-out" aria-live="polite"><p class="note">Fill in every box, tick the check, then press Calculate.</p></section>')
    body.append(f"<script>{js}</script>")
    body.append('<h2 id="method">How the arithmetic works</h2>')
    rows = [
        ["Gain", "Sale price, less sale costs, less adjusted tax basis."],
        ["Depreciation recapture", "The part of a gain up to the depreciation taken, taxed at the recapture rate. The rest of the gain is taxed at the federal rate you enter."],
        ["Investment income tax", "If you answer yes, the investment income tax rate is applied to the whole gain or rent. Its rate is a ledger value."],
        ["California", "The California rate you enter is applied to the whole gain, because California taxes gains at ordinary rates."],
        ["Renewal", "Each year's rent is grown by the increase you enter, taxed at the rates you enter, and discounted to today at the discount rate."],
        ["End of renewed term", "The end-of-term sale is taxed with the same rates as the sale now. This is an assumption, stated here."],
        ["Left out", "Depreciation deductions during the hold, the limit on deducting capital losses, and any state rule the page does not name. Those are for the private model."],
    ]
    body.append(table(["Step", "What it does"], rows, "site", "method-t"))
    body.append(f'<p class="note">Rates and thresholds come from the ledger rows named beside each box, each linked to its official '
                f'source: <a href="taxes.html">Taxes and costs</a>, and <a href="valuation.html">Capital markets</a>.</p>')
    lede = ("A browser calculator that sets the after-tax cash from a sale now against the present value of a negotiated renewal. "
            "Every box starts blank, nothing is stored or sent, and no winner is shown until every input is entered and checked.")
    return page("calculator.html", "After-tax calculator", lede, "".join(body), "Decide")


ADVISOR_FIGURES = [
    ("Restaurants in the tenant's system", "TN-001", "Its own quarterly filing; a year earlier it was [[TN-004]]."),
    ("Same-store sales, whole system, latest quarter", "TN-020", "As the tenant reports it in its quarterly filing. The company gives the reason: " + "[[TN-025]]."),
    ("Same-store sales, last full fiscal year", "TN-023", "Annual report; the year before was [[TN-024]]."),
    ("Share of restaurants run by franchisees", "TN-008", "Annual report, at fiscal year-end."),
    ("10-year Treasury yield, the discount benchmark", "CM-001", "U.S. Treasury; the Federal Reserve target range is [[CM-010]]."),
    ("Top federal rate on most long-term gains", "TX-040", "IRS Topic 409; the rate on depreciation recapture is [[TX-042]]."),
    ("Federal investment income tax", "TX-043", "IRS Topic 559; it applies above [[TX-044]]."),
    ("Top California rate including the extra 1% surcharge", "TX-060", "Franchise Tax Board schedules for tax year 2025, the latest the ledger holds. See the [[TX-059]] surcharge."),
    ("Measure ULA thresholds on sale price", "TX-003", "City of Los Angeles. The thresholds are adjusted each year: [[TX-010]]."),
]


def build_advisor():
    figs = []
    for label, rid, note in ADVISOR_FIGURES:
        figs.append([e(label), f'<strong>{e(ref_value(rid))}</strong>', e(ROWS[rid]["period"] or "") or "&mdash;",
                     row_link(rid) + " " + src_link(ROWS[rid]["source"])])
    fig_rows = []
    for (label, rid, note), row in zip(ADVISOR_FIGURES, figs):
        fig_rows.append({"cells": row + [fill(note)]})
    body = ['<div class="print-bar no-print"><button type="button" class="btn" data-print="1">Print this page</button> '
            '<span class="note">Prints on one letter-size page. Each figure links to its official source.</span></div>']
    body.append('<section class="one-page">')
    body.append(f'<p class="question"><strong>Question.</strong> {e(DECIDE["question"])}</p>')
    body.append(f'<p class="answer"><strong>Short answer.</strong> {e(DECIDE["answer_short"])}</p>')
    body.append('<h2>Key figures, each read at its official source</h2>')
    body.append(table(["Figure", "Value", "Period", "Official source", "Note"], fig_rows, "data", "adv-figs"))
    body.append('<h2>The rule, by answer</h2><ol class="rules">')
    for rule in DECIDE["rule"][:3]:
        cond = rule["if"][0].lower() + rule["if"][1:]
        act = rule["then"][0].lower() + rule["then"][1:]
        body.append(f'<li><strong>If</strong> {e(cond)}, <strong>then</strong> {e(act)}</li>')
    body.append('</ol>')
    body.append('<h2>Blank until the private file is checked</h2><ul class="blanks">')
    critical = [q for q in QUESTIONS if q["priority"] == "Critical" and q["status"] == "Open"][:8]
    for q in critical:
        body.append(f'<li>{e(q["question"])} <span class="ref">({e(q["id"])})</span></li>')
    body.append('</ul>')
    body.append('<h2>First steps</h2><ol class="steps">')
    for p in DECIDE["plan"][:2]:
        body.append(f'<li><strong>{e(p["when"])}:</strong> {e(p["action"])}</li>')
    body.append('</ol>')
    body.append('<p class="fine">Decision support only: not an appraisal, not tax advice, not investment advice. The owner is '
                '[OWNER-01] and the property is [PROPERTY-01]; no identifying detail is published. Full figures, sources and blanks: '
                '<a href="questions.html">Questions</a>, <a href="flagged.html">Flagged for Review</a>, <a href="sources.html">Sources</a>.</p>')
    body.append('</section>')
    lede = ("A one-page summary for an adviser: the question, the short answer, the figures that matter, the rule, what is still "
            "blank, and the first steps. Print it from the browser.")
    return page("advisor-summary.html", "Advisor summary", lede, "".join(body), "Start")


PRINT_CSS = """
.print-bar{margin:0 0 .8rem}
.one-page .question,.one-page .answer{margin:.2rem 0;font-size:.95rem}
.one-page h2{font-size:1rem;margin:.7rem 0 .25rem}
.one-page table{font-size:.78rem}
.one-page .rules,.one-page .steps,.one-page .blanks{font-size:.82rem;margin:.2rem 0;padding-left:1.1rem}
.one-page .fine{font-size:.72rem;color:var(--muted)}
.calc-note{background:var(--accent-bg);border:1px solid var(--line);border-radius:10px;padding:.7rem 1rem;margin:0 0 1rem}
.calc-note p{margin:.3rem 0}
.calc{display:grid;gap:.9rem}
.calc-group{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:.8rem 1rem}
.calc-group legend{font-weight:700;padding:0 .3rem}
.calc-row{display:grid;grid-template-columns:minmax(12rem,1fr) minmax(8rem,12rem);gap:.2rem .8rem;align-items:center;padding:.35rem 0;border-top:1px dashed var(--line)}
.calc-row:first-of-type{border-top:0}
.calc-row label{font-weight:600}
.calc-row input,.calc-row select{font:inherit;padding:.35rem .5rem;border:1px solid var(--line);border-radius:6px;width:100%;box-sizing:border-box}
.calc-row .hint{grid-column:1/-1;margin:0;font-size:.82rem;color:var(--muted)}
.chip{font:inherit;font-size:.78rem;border:1px solid var(--accent);background:#fff;color:var(--accent);border-radius:999px;padding:.12rem .6rem;cursor:pointer;margin:.2rem 0 0}
.check{display:flex;gap:.5rem;align-items:flex-start}
.btn{font:inherit;background:var(--accent);color:#fff;border:0;border-radius:8px;padding:.5rem .9rem;cursor:pointer}
.btn.ghost{background:#fff;color:var(--accent);border:1px solid var(--accent)}
.calc-actions{display:flex;gap:.6rem;flex-wrap:wrap}
.calc-out{margin-top:1rem}
.calc-t{width:100%}
.calc-total th{text-align:left}
.calc-warn{background:#fff7e6;border:1px solid #f0c36d;border-radius:10px;padding:.7rem 1rem}
.calc-result{background:#eef8f0;border:1px solid #9ccfa8;border-radius:10px;padding:.7rem 1rem}
@media (max-width:640px){.calc-row{grid-template-columns:1fr}}
@media print{
  @page{size:letter;margin:.45in}
  header.top,nav.side,footer.foot,.menu,.no-print,.crumb,.lede,.skip{display:none !important}
  body{background:#fff;color:#000}
  main{padding:0;margin:0;max-width:none}
  .one-page{break-inside:avoid}
  .one-page table{break-inside:avoid}
  .one-page h1{font-size:1.2rem;margin:0 0 .3rem}
  a{color:#000;text-decoration:none}
  .src{color:#000}
}
"""



def main():
    ledger_rules()
    run_prose_checks()
    pages = {"index.html": build_index(), "executive-summary.html": build_exec(), "decision.html": build_decision(),
             "risks.html": build_risks(), "questions.html": build_questions()}
    pages.update(build_evidence())
    pages.update({"advisor-summary.html": build_advisor(), "calculator.html": build_calculator(), "progress.html": build_progress()})
    pages.update({"projection-model.html": build_projection(), "flagged.html": build_flagged(), "suggestions.html": build_suggestions(),
                  "verification.html": build_verification(), "sources.html": build_sources(), "requirements.html": build_requirements(),
                  "privacy.html": build_privacy(), "workspaces.html": build_archive(), "deployment.html": build_deployment(),
                  "archive.html": REDIRECT})
    nav_slugs = [h for _, items in NAV for h, _ in items]
    assert set(nav_slugs) <= set(pages), set(nav_slugs) - set(pages)
    for slug, text in pages.items():
        hits = privacy.scan(text, is_html=True)
        assert not hits, f"{slug}: possible personal information: {hits[:5]}"
        assert "http://" not in re.sub(r'xmlns="http://www\.w3\.org/[^"]+"', "", text), f"{slug}: insecure address"
    os.makedirs(os.path.join(REPO, "assets"), exist_ok=True)
    outputs = dict(pages)
    outputs["assets/site.css"] = CSS + PRINT_CSS
    outputs["assets/site.js"] = JS
    outputs["favicon.svg"] = FAVICON
    for rel, text in outputs.items():
        with open(os.path.join(REPO, rel), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    check_links(pages)
    c = counts()
    print(f"built {len(pages)} pages: {c['published']} published values ({c['verified']} verified, {c['computed']} computed), "
          f"{c['blank']} blank, {len(SRC)} sources, {len(RISKS['risks'])} risks, {len(QUESTIONS)} questions, "
          f"{len(SUGGEST['suggestions'])} suggestions, {len(IRREG)} irregularities")


if __name__ == "__main__":
    main()

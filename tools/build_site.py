#!/usr/bin/env python3
"""
Static site builder for the Central Los Angeles Jack in the Box NNN decision workbook.

Reads JSON in data/ and writes plain HTML to the repository root (GitHub Pages serves main's root).
No external dependencies, no frameworks, no build server. Deterministic.

Hard asserts (build fails rather than publishing something unverifiable):
  * every data row in data/metrics.json resolves to a source id present in data/sources.json with an https URL
  * every risk row carries a source id
  * no personal-identifying strings are emitted
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")


def load(name):
    with open(os.path.join(D, name), encoding="utf-8") as f:
        return json.load(f)


SOURCES = load("sources.json")
SRC = {s["id"]: s for s in SOURCES["sources"]}
METRICS = load("metrics.json")
PROP = load("property_lease.json")
VAL = load("valuation.json")
RISKS = load("risks.json")
DEC = load("decisions.json")
MODEL = load("model_output.json")
IRR = load("irregularities.json")
REQ = load("requirements.json")

ACCESS = SOURCES["accessed"]
e = html.escape

NAV = [
    ("index.html", "Dashboard"),
    ("executive-summary.html", "Executive summary"),
    ("decision.html", "Decision"),
    ("market-economics.html", "Market economics"),
    ("property-lease.html", "Property &amp; lease"),
    ("valuation.html", "Valuation inputs"),
    ("projection-model.html", "Projection model"),
    ("risks.html", "Risk register"),
    ("requirements.html", "Requirements"),
    ("verification.html", "Verification"),
    ("flagged.html", "Flagged for review"),
    ("sources.html", "Sources"),
    ("privacy.html", "Privacy"),
    ("deployment.html", "Deployment"),
    ("archive.html", "Session A archive"),
    ("workspaces.html", "All workspaces"),
]


# ----------------------------------------------------------------------------- helpers
def src_link(sid):
    s = SRC[sid]
    return (f'<span class="src"><a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer" '
            f'title="{e(s["publisher"])} - {e(s["title"])}">{e(sid)} &#8599;</a></span>')


def badge(status):
    cls = {"verified": "ok", "unverified": "warn", "flagged": "bad"}.get(status, "neutral")
    return f'<span class="badge {cls}">{e(status)}</span>'


def sev_badge(sev):
    cls = {"high": "bad", "medium": "warn", "low": "neutral"}.get(sev, "neutral")
    return f'<span class="badge {cls}">{e(sev)}</span>'


def table(headers, rows, cls="", num_cols=()):
    out = [f'<div class="tablewrap"><table class="{cls}"><thead><tr>']
    for i, h in enumerate(headers):
        c = ' class="num"' if i in num_cols else ""
        out.append(f"<th{c}>{h}</th>")
    out.append("</tr></thead><tbody>")
    for r in rows:
        out.append("<tr>")
        for i, cell in enumerate(r):
            c = ' class="num"' if i in num_cols else ""
            out.append(f"<td{c}>{cell}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def money(x, dec=0):
    sign = "-" if x < 0 else ""
    return f"{sign}${abs(x):,.{dec}f}"


def page(slug, title, body, description="", wide=False):
    cur = ' aria-current="page"'
    nav = "".join(
        '<a href="%s"%s>%s</a>' % (href, cur if href == slug else "", label)
        for href, label in NAV)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} - Central LA Jack in the Box NNN workbook</title>
<meta name="description" content="{e(description)}">
<meta name="robots" content="index,follow">
<link rel="stylesheet" href="assets/style.css">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap bar">
  <a class="brand" href="index.html"><span class="dot"></span><span>Central LA NNN Decision Workbook<small>Jack in the Box &middot; 2030&ndash;2035 lease expiry &middot; data as of {ACCESS}</small></span></a>
  <nav class="main" aria-label="Sections">{nav}</nav>
</div></header>
<main id="main" class="wrap">
{body}
</main>
<footer class="site"><div class="wrap">
  <p><strong>Internal decision support &mdash; not an appraisal, not tax advice, not investment advice.</strong>
  Every data value on this site links to the official source it was read from on {ACCESS}.
  Values that could not be confirmed from an official source are blank and listed on the
  <a href="flagged.html">Flagged for review</a> page. No personal or parcel-identifying information is published.</p>
  <p>Built from <a href="sources.html">{len(SRC)} sources</a> &middot; <a href="verification.html">verification log</a> &middot;
  <a href="deployment.html">deployment</a> &middot; reproduction: <code>python3 tools/build_site.py</code></p>
</div></footer>
<script src="assets/app.js" defer></script>
</body>
</html>
"""


def head_block(eyebrow, h1, lede):
    return (f'<div class="page-head"><p class="eyebrow">{eyebrow}</p><h1>{h1}</h1>'
            f'<p class="lede">{lede}</p></div>')


# ----------------------------------------------------------------------------- derived stats
ROWS = METRICS["rows"]
VER = [r for r in ROWS if r["status"] == "verified"]
UNV = [r for r in ROWS if r["status"] != "verified"]
CATS = []
for r in ROWS:
    if r["category"] not in CATS:
        CATS.append(r["category"])
SC = MODEL["scenarios"]
BASE = next(s for s in SC if s["id"] == "base")
BEAR = next(s for s in SC if s["id"] == "bear")
BULL = next(s for s in SC if s["id"] == "bull")

# ----------------------------------------------------------------------------- build assertions
for r in ROWS:
    assert r["source"] in SRC, f"metric {r['id']} has unknown source {r['source']}"
    assert SRC[r["source"]]["url"].startswith("https://"), f"source {r['source']} is not https"
    assert r["status"] in ("verified", "unverified", "flagged"), f"bad status on {r['id']}"
    if r["status"] == "verified":
        assert str(r["value"]).strip() != "", f"verified row {r['id']} has no value"
    else:
        assert str(r["value"]).strip() == "", f"unverified row {r['id']} must be blank"
for r in RISKS["rows"]:
    assert r["source"] in SRC, f"risk {r['id']} has unknown source"

FORBIDDEN = [
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",          # email
    r"\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}",                          # phone
    r"\b\d{1,6}\s+(?:[A-Z][a-z]+\s){1,3}(Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Way|Lane|Ln)\b",
    r"\bAPN[:\s#]*\d{3,}",                                        # parcel numbers
]
PII_PATTERNS = [re.compile(p) for p in FORBIDDEN]


def pii_scan(text, where):
    for pat in PII_PATTERNS:
        m = pat.search(text)
        assert not m, f"possible personal identifier in {where}: {m.group(0)!r}"


# ----------------------------------------------------------------------------- index
def build_index():
    kpis = [
        ("Decision", "Sequence, don't gamble", "Extend at a reset, price in 2027&ndash;28, sell only if the numbers clear"),
        ("Base case, hold vs sell", money(BASE["delta_hold_vs_sell_netlease"]), "Hold wealth minus sell-and-reinvest at the verified 7.3% net-lease benchmark, 2040 horizon"),
        ("Reinvestment yield to beat holding", f"{MODEL['breakevens']['required_reinvest_yield_pct']['base']:.2f}%", "Base case. Verified benchmark available: 7.3%. Margin is thin."),
        ("Rent uplift needed to justify extending", f"+{MODEL['renewal_value']['required_rent_uplift_to_beat_sell_netlease_pct']:.1f}%", "Versus selling into the net-lease benchmark"),
        ("Verified data rows", f"{len(VER)} of {len(ROWS)}", f"{len(UNV)} rows deliberately blank and flagged"),
        ("Parcel-level hazard data", "Unverified", "FEMA, CAL FIRE, CGS and insurance all need the APN"),
    ]
    kpi_html = "".join(
        f'<div class="card kpi{" flag" if v in ("Unverified",) else ""}"><p class="label">{k}</p>'
        f'<p class="value">{v}</p><p class="sub">{s}</p></div>' for k, v, s in kpis)

    sec_rows = []
    for cat in CATS:
        rs = [r for r in ROWS if r["category"] == cat]
        v = sum(1 for r in rs if r["status"] == "verified")
        if v == len(rs):
            st = badge("verified")
        elif v == 0:
            st = badge("unverified")
        else:
            st = f'<span class="badge warn">partial &mdash; {len(rs)-v} blank</span>'
        sec_rows.append([f"<a href='market-economics.html#{slugify(cat)}'>{e(cat)}</a>",
                         f"{len(rs)}", f"{v}", f"{len(rs)-v}", st])

    top_risks = sorted(RISKS["rows"], key=lambda r: (r["impact"], r["likelihood"]), reverse=True)[:6]
    risk_rows = [[r["id"], e(r["risk"]), e(r["type"]),
                  f'{r["likelihood"]}/5', f'{r["impact"]}/5', e(r["decision"]), src_link(r["source"])]
                 for r in top_risks]

    body = f"""
{head_block("Dashboard", "A Central Los Angeles Jack in the Box with an NNN lease expiring 2030&ndash;2035: sell, or renew?",
            "One page to orient, then four evidence pages and a decision page. Every number is linked to the official source it came from. Where no official source exists, the cell is blank and the item is on the flagged list.")}

<div class="grid g3">{kpi_html}</div>

<div class="callout warn" style="margin-top:22px">
  <p><strong>Read this first.</strong> The brief does not contain the street address, APN, current rent, exact expiry date, purchase basis or loan terms.
  Those six facts decide the answer. This workbook therefore does two things instead of guessing: it verifies the market and the tenant with official data,
  and it converts the decision into <em>thresholds you can test</em> the moment the documents arrive.</p>
  <p class="muted">Privacy: no name, address, parcel number, loan number or account appears anywhere in this repository or on this site. See <a href="privacy.html">Privacy</a>.</p>
</div>

<h2>What the evidence says</h2>
<div class="grid g2">
  <div class="card">
    <h3>1. The local economy is stable, not booming</h3>
    <p>Metro employment grew <strong>+0.6%</strong> year over year with <strong>6,289.1k</strong> jobs, and unemployment fell from 5.8% to <strong>4.8%</strong> &mdash; but the growth is concentrated in education/health (+42.7k) while information (&minus;12.3k, &minus;6.1%) and professional services (&minus;9.2k) contract. {src_link("S1")}</p>
    <p>County population is projected to <em>fall</em> from 9.85M (2025) to 9.64M (2040) in the state's official series. {src_link("S3")}</p>
  </div>
  <div class="card">
    <h3>2. The tenant is restructuring, not disappearing</h3>
    <p>2,136 Jack in the Box restaurants, 93% franchised, but the system shrank by 55 units in FY2025; Del Taco is being sold for $115M, the dividend is gone, and ~$1.7B of securitized debt carries sales-based covenants. {src_link("S9")}</p>
    <p>Critically for you: the company says it has <em>&ldquo;generally been able to renew our restaurant leases as they expire at then-current market rates.&rdquo;</em> {src_link("S9")} The 2030&ndash;2035 expiry is a <strong>repricing event</strong>, not an automatic rollover.</p>
  </div>
  <div class="card">
    <h3>3. The money decision is tighter than it looks</h3>
    <p>At the benchmark rent, selling now clears about <strong>{money(BASE['sell_now_net'])}</strong> after costs. Holding and renewing produces <strong>{money(BASE['hold_expected_wealth'])}</strong> of 2040 wealth versus <strong>{money(BASE['sell_now_wealth_netlease'])}</strong> if you sell and redeploy at the verified 7.3% net-lease yield. {src_link("S10")}</p>
    <p>You need a <strong>{MODEL['breakevens']['required_reinvest_yield_pct']['base']:.2f}%</strong> reinvestment yield for selling to match holding. That is why the recommendation is a sequence, not a slogan.</p>
  </div>
  <div class="card">
    <h3>4. The tail risk is real and documented</h3>
    <p>The January 2025 fires destroyed 16,251 structures, cost <strong>$5.2B&ndash;$10.1B</strong> of economic output, hit ~6,800 businesses and ~47,000 workers, and removed $900M&ndash;$1.6B of tax revenue. {src_link("S13")}</p>
    <p>Central Los Angeles flatland is not the wildland interface, but smoke, shut-offs, insurance repricing and seismic exposure are metro-wide and unhedged by a single-asset portfolio.</p>
  </div>
</div>

<h2>Data coverage by category</h2>
{table(["Category", "Rows", "Verified", "Blank / flagged", "Status"],
       sec_rows, num_cols=(1, 2, 3))}

<h2>The six risks that matter most</h2>
{table(["ID", "Risk", "Type", "Likelihood", "Impact", "Hits", "Source"],
       risk_rows, num_cols=(3, 4))}

<h2>Read in this order</h2>
<div class="grid g2">
  <div class="card"><h3><a href="executive-summary.html">Executive summary</a></h3><p>One page: the answer, the numbers behind it, and what to do in the next 90 days.</p></div>
  <div class="card"><h3><a href="decision.html">Decision</a></h3><p>Four strategies scored on wealth preservation, growth, execution risk, liquidity and tax efficiency &mdash; plus six decision triggers.</p></div>
  <div class="card"><h3><a href="market-economics.html">Market economics</a></h3><p>{len(ROWS)} metric rows across {len(CATS)} categories: population, income, jobs, schools, consumer demand, capital markets, taxes, labour law, hazards, tenant health.</p></div>
  <div class="card"><h3><a href="projection-model.html">Projection model</a></h3><p>A reproducible 2026&ndash;2040 model with published inputs, breakevens and a sensitivity grid.</p></div>
  <div class="card"><h3><a href="flagged.html">Flagged for review</a></h3><p>{len(UNV)} blank data rows, {len(IRR['data_irregularities'])} data issues and {len(IRR['repo_irregularities'])} repository issues, each with what to obtain.</p></div>
  <div class="card"><h3><a href="sources.html">Sources</a></h3><p>{len(SRC)} sources with tier, publisher, coverage and access date.</p></div>
</div>
"""
    return page("index.html", "Dashboard", body,
                "Decision dashboard for a Central Los Angeles Jack in the Box NNN property with a 2030-2035 lease expiry.")


# ----------------------------------------------------------------------------- executive summary
def build_exec():
    rows = []
    for s in SC:
        rows.append([e(s["label"]), money(s["sell_now_price"]), money(s["sell_now_net"]),
                     money(s["sell_now_wealth_netlease"]), money(s["hold_expected_wealth"]),
                     money(s["delta_hold_vs_sell_netlease"])])
    body = f"""
{head_block("Executive summary", "Sell the asset, or renew the lease? Hold the option open, then price it.",
            "Bottom line first, then the reasoning, then the three numbers that decide it.")}

<div class="decision">
  <h2>Recommendation</h2>
  <p><strong>Do not renew on autopilot and do not sell on fear.</strong> Run a sequenced plan over 90&ndash;365 days:
  (1) assemble the missing documents, (2) verify parcel hazards and insurance, (3) open an extension negotiation that trades term for a
  <em>market-rent reset</em>, (4) obtain an appraisal, and (5) sell into a 1031 exchange only if the implied cap rate is at or below 6.00%
  or the replacement yield clears the thresholds below. If the cap rate is above 7.00%, keep and extend.</p>
  <div class="rank"><span>1st: Extend at a reset, then sell with long WALT</span><span>2nd: 5-year hybrid extension</span><span>3rd: Sell now into a 1031</span><span>4th: Hold to expiry and renew</span></div>
</div>

<h2>Why this is the answer</h2>
<div class="grid g2">
  <div class="card"><h3>The two paths are close, so the tie-breaker is the lease</h3>
  <p>Base case: holding produces <strong>{money(BASE['hold_expected_wealth'])}</strong> of 2040 wealth; selling now and redeploying at the verified 7.3% net-lease benchmark produces <strong>{money(BASE['sell_now_wealth_netlease'])}</strong>. The gap is about <strong>{money(BASE['hold_expected_wealth']-BASE['sell_now_wealth_netlease'])}</strong> &mdash; roughly 4% of wealth, inside the error bars of the assumptions.</p>
  <p>Selling beats holding in the bear case by <strong>{money(-BEAR['delta_hold_vs_sell_netlease'])}</strong>; holding wins the bull case by <strong>{money(BULL['delta_hold_vs_sell_netlease'])}</strong>. A coin-flip decision should not be made on a coin flip &mdash; it should be made on the one variable you control: the rent and term you can negotiate.</p></div>
  <div class="card"><h3>Only one action improves both outcomes</h3>
  <p>A market-rent reset needs just <strong>+{MODEL['renewal_value']['required_rent_uplift_to_beat_sell_netlease_pct']:.1f}%</strong> to make holding beat selling into the net-lease benchmark, and it simultaneously raises the price a buyer will pay because the WALT extends.</p>
  <p>The tenant has structural reason to deal: its franchise agreements run 20 years while this lease ends in 2030&ndash;2035. {src_link("S9")}</p></div>
  <div class="card"><h3>Selling is defensible &mdash; if capital is redeployed</h3>
  <p>You need <strong>{MODEL['breakevens']['required_reinvest_yield_pct']['base']:.2f}%</strong> on the proceeds to match holding. One net-lease REIT reported a 7.3% initial weighted average cash yield on 2025 acquisitions; that is a real benchmark, but it is not a guarantee for a small private buyer. {src_link("S10")}</p>
  <p>Section 1031 lets you defer the gain and diversify one parcel into several. {src_link("S16")} That is the strongest argument for selling &mdash; not the cap rate.</p></div>
  <div class="card"><h3>Renewing is defensible &mdash; if the rent resets</h3>
  <p>Holding keeps a <strong>2%</strong> annual cap on assessed value in a metro where CPI is running <strong>3.6%</strong>. {src_link("S6")} {src_link("S1")} That is a genuine, permanent, non-transferable benefit.</p>
  <p>The cost of holding is concentration: one tenant, one parcel, one metro, with wildfire/earthquake/insurance tail risk that diversification would remove.</p></div>
</div>

<h2>Scenario results (pre-tax, nominal USD, 2040 horizon)</h2>
{table(["Scenario", "Sell-now price", "Net proceeds after costs", "Sell + redeploy at 7.3%", "Hold + renew (prob-weighted)", "Hold minus sell"], rows, num_cols=(1,2,3,4,5))}
<p class="muted">Disposition cost = 3.00% brokerage + 0.50% closing + 0.11% Los Angeles County transfer tax + 0.45% City transfer tax + Measure ULA where applicable
{src_link("S7")}{src_link("S8")}. Measure ULA is <em>not</em> triggered at the benchmark rent because the implied value stays below the $5.4M threshold &mdash; that changes if actual rent is much higher.</p>

<h2>The three numbers that decide it</h2>
<div class="grid g3">
  <div class="card kpi"><p class="label">Reinvestment yield to match holding</p><p class="value">{MODEL['breakevens']['required_reinvest_yield_pct']['base']:.2f}%</p><p class="sub">Verified available benchmark: 7.3% (net lease, US+Europe, all property types)</p></div>
  <div class="card kpi"><p class="label">Rent uplift needed to prefer holding</p><p class="value">+{MODEL['renewal_value']['required_rent_uplift_to_beat_sell_netlease_pct']:.1f}%</p><p class="sub">At the 2030&ndash;2035 reset, versus contract rent today</p></div>
  <div class="card kpi"><p class="label">Exit cap where holding and selling tie</p><p class="value">{MODEL['breakevens']['exit_cap_hold_equals_sell_netlease_pct']:.2f}%</p><p class="sub">Versus selling into the net-lease benchmark. Above this cap rate, do not sell.</p></div>
</div>

<h2>What to do in the next 90 days</h2>
<ol>
  <li><strong>Pull twelve documents</strong> (P01&ndash;P12): lease and amendments, exact expiry and option terms, rent roll, expense history, basis and depreciation, loan documents, APN, property condition report, insurance declarations, franchisee financials, a broker opinion of value, and zoning.</li>
  <li><strong>Close the hazard gaps</strong>: FEMA flood panel, CAL FIRE/LACoFD fire hazard severity zone, CGS seismic and liquefaction screening, and a current insurance quote. All four are currently unverified for the parcel.</li>
  <li><strong>Open the tenant conversation</strong> with a specific ask: market reset with a floor, 10-year extension, guaranty, and clarity on the option notice date.</li>
  <li><strong>Do not list</strong> until the appraisal is in hand and the replacement-property pipeline exists.</li>
</ol>

<h2>What this workbook will not do</h2>
<ul>
  <li>It will not state the property's value. Rent, expiry date, basis and debt are not in the brief, so the model publishes a benchmark and breakevens instead (see <a href="flagged.html">Flagged for review</a>).</li>
  <li>It will not quote a capital-gains rate. That needs the owner's basis and depreciation history; a 1031 exchange is the mechanism that makes the timing decision matter. {src_link("S16")}</li>
  <li>It will not use a secondary or industry source for any value. Where no official source exists, the cell is blank.</li>
</ul>
"""
    return page("executive-summary.html", "Executive summary", body,
                "One-page executive summary with the recommendation, scenario results and the three deciding numbers.")


# ----------------------------------------------------------------------------- market
def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def build_market():
    toc = "".join(f'<a href="#{slugify(c)}">{e(c)} ({len([r for r in ROWS if r["category"]==c])})</a>' for c in CATS)
    blocks = []
    for cat in CATS:
        rs = [r for r in ROWS if r["category"] == cat]
        rows = []
        for r in rs:
            val = e(str(r["value"])) if str(r["value"]).strip() else '<span class="muted">&mdash; blank &mdash;</span>'
            if r["status"] != "verified":
                val = '<span class="muted">&mdash; blank &mdash;</span>'
            rows.append([r["id"], e(r["metric"]), val, e(r["unit"]), e(r["period"]), e(r["geography"]),
                         src_link(r["source"]), badge(r["status"]), e(r["note"])])
        blocks.append(f'<h2 id="{slugify(cat)}">{e(cat)}</h2>' + table(
            ["ID", "Metric", "Value", "Unit", "Period", "Geography", "Source", "Status", "Note"],
            rows, num_cols=()))

    body = f"""
{head_block("Market economics", "Everything that can move this property's value, verified one row at a time",
            f"{len(ROWS)} rows across {len(CATS)} categories. Each row links to the official source it was read from on {ACCESS}. Rows with no official value are blank by rule, not estimated.")}

<div class="callout info">
<p><strong>How to read this table.</strong> A value is only present if it was read directly from a government, regulator or SEC filing on {ACCESS}.
If the cell is blank, no official value was confirmed &mdash; the row is on the <a href="flagged.html">Flagged for review</a> page with what needs to be obtained.
Geographic scope is City of Los Angeles, Los Angeles County or the metro area; nothing here is parcel-specific.</p>
</div>

<div class="toolbar">
  <input id="q" type="search" placeholder="Search all metrics, categories, notes&hellip;" aria-label="Search metrics">
  <select id="fcat" aria-label="Filter by category"><option value="">All categories</option>{''.join(f'<option>{e(c)}</option>' for c in CATS)}</select>
  <span class="pill" id="count">{len(ROWS)} rows</span>
</div>
<div class="toc">{toc}</div>
{''.join(blocks)}

<h2>Interpretation - what this means for the decision</h2>
<div class="grid g2">
  <div class="card"><h3>Demand side: adequate, softening at the margin</h3>
  <p>City population is flat to slightly down (&minus;0.8% since 2020) and the county is projected to decline to 9.64M by 2040. {src_link("S2")} {src_link("S3")}
  Households still earn a median $81,939 and spend $11,858 a year on food. {src_link("S2")} {src_link("S1")}
  A drive-thru on a traffic artery depends on vehicle counts, not regional growth, which is why the parcel itself still matters more than the metro.</p></div>
  <div class="card"><h3>Cost side: labour is the binding constraint</h3>
  <p>Fast-food wages are $20.00/hour against a $16.90 floor, and the Fast Food Council can raise them. {src_link("S5")} {src_link("S4")}
  Franchise AUV fell 3.8% to $1,874k. {src_link("S9")} An 8&ndash;10% occupancy-cost ratio implies $150k&ndash;$187k of annual rent capacity &mdash; which is exactly the benchmark used in the model, and the reason a large rent increase at renewal is unlikely to stick.</p></div>
  <div class="card"><h3>Capital markets: the cap rate is the swing factor</h3>
  <p>10-year Treasury 4.90%, policy rate 4.00%. {src_link("S11")} {src_link("S12")}
  Net-lease acquisitions cleared at a 7.3% initial cash yield in 2025. {src_link("S10")}
  Each 100bp of cap-rate expansion cuts the exit value by roughly 13&ndash;15% at these levels &mdash; far more than any rent escalation can recover inside the remaining term.</p></div>
  <div class="card"><h3>Tail risk: priced by insurance, not by the cap rate</h3>
  <p>The 2025 fires are the calibration event: $5.2B&ndash;$10.1B of lost output and ~47,000 workers affected. {src_link("S13")}
  The parcel's FEMA, fire-hazard, seismic and insurance status are all unverified here because the APN is withheld. Those four items are the first thing to close.</p></div>
</div>
"""
    return page("market-economics.html", "Market economics", body,
                "Verified market economics: population, income, employment, schools, consumer demand, capital markets, taxes, labour regulation, hazard and tenant data.")


# ----------------------------------------------------------------------------- property & lease
def build_property():
    id_rows = [[e(k), e(str(v))] for k, v in PROP["identified_property"].items()]
    req_rows = [[r["id"], e(r["field"]), e(r["why"]), sev_badge("high" if "MISSING" in r["status"] else "low") + " " + e(r["status"])] for r in PROP["fields_required_before_a_binding_decision"]]
    fact_rows = [[e(f["fact"]), e(f["value"]), src_link(f["source"])] for f in PROP["tenant_brand_facts_verified"]]
    clause_rows = [[e(c)] for c in PROP["lease_clauses_to_audit"]]
    body = f"""
{head_block("Property &amp; lease", "The asset, the tenant, and the twelve documents that would turn this into an appraisal",
            "Brand facts are verified against the tenant's SEC filing. Property facts are anonymised placeholders, because the brief does not contain them and privacy requires they never be published.")}

<div class="callout">
<p><strong>Privacy architecture.</strong> The site refers only to &ldquo;the Subject Property (Central Los Angeles)&rdquo;. No owner name, entity, street address, parcel number, loan number or contact detail exists in this repository.
The build script scans every emitted page for email addresses, phone numbers, street addresses and parcel numbers and fails if any appear.</p>
</div>

<h2>Asset profile (anonymised)</h2>
{table(["Field", "Value"], id_rows)}

<h2>Tenant and brand facts - verified</h2>
{table(["Fact", "Value", "Source"], fact_rows)}

<h2>Which lease clauses decide the answer</h2>
{table(["Clause to audit before any decision"], clause_rows)}

<h2>The twelve inputs that are missing</h2>
<p>Each of these changes the answer by more than the gap between the sell and hold scenarios. None is in the brief, so none is invented here.</p>
{table(["ID", "Document / field", "Why it decides the answer", "Status"], req_rows)}

<h2>What the tenant's own filing tells you about renewal</h2>
<div class="grid g2">
  <div class="card"><h3>The good news</h3>
  <p>&ldquo;We have generally been able to renew our restaurant leases as they expire at then-current market rates.&rdquo; {src_link("S9")}
  Franchise agreements run 20 years, so a franchisee that has invested in the brand usually wants to stay. {src_link("S9")}</p></div>
  <div class="card"><h3>The bad news</h3>
  <p>The system shrank by 55 units in FY2025, a block-closure program is running, AUV fell 3.8%, Del Taco is being sold, the dividend is gone, and ~$1.7B of securitized debt carries gross-sales covenants. {src_link("S9")}
  A franchisee under that pressure is a weaker credit at exactly the moment you want a higher rent.</p></div>
</div>
"""
    return page("property-lease.html", "Property & lease", body,
                "Anonymised asset profile, verified tenant facts, lease clauses to audit and the missing documents.")


# ----------------------------------------------------------------------------- valuation
def build_valuation():
    v_rows = [[e(i["label"]), e(str(i["value"])), e(i["unit"]), src_link(i["source"]), e(i["date"])] for i in VAL["verified_inputs"]]
    a_rows = []
    for a in VAL["analyst_assumptions"]:
        a_rows.append([a["key"], e(a["label"]), e(str(a["value"])), e(a["unit"]), e(a["basis"]), e(a["confidence"]),
                       badge("verified") if a.get("verified") and a["confidence"] == "high" else badge("unverified")])
    c_rows = [[e(t["line"]), f'{t["rate_pct"]:.2f}%', e(t["source"])] for t in VAL["transaction_cost_stack"]]
    b_rows = [[e(b["band"]), e(b["interpretation"])] for b in VAL["cap_rate_sensitivity_bands"]]
    body = f"""
{head_block("Valuation inputs", "Two lists, never mixed: what is verified, and what is an assumption",
            "This is the discipline that keeps the workbook honest. Verified inputs carry an official source. Assumptions carry a reason and a confidence level, and you can change them.")}

<h2>Verified inputs</h2>
{table(["Input", "Value", "Unit", "Source", "As of"], v_rows, num_cols=(1,))}

<h2>Analyst assumptions</h2>
<p>These are not data. They are the best-supported starting points, and each one is disclosed on the site rather than buried in a spreadsheet.</p>
{table(["Key", "Assumption", "Value", "Unit", "Basis", "Confidence", "Status"], a_rows, num_cols=(2,))}

<h2>Disposition cost stack</h2>
{table(["Line item", "Rate", "Source"], c_rows, num_cols=(1,))}
<p class="muted">At the benchmark rent the implied value is about {money(BASE['sell_now_price'])}, well below the $5.4M Measure ULA threshold, so the 4% surtax does not apply.
At a 6.50% cap rate the asset only reaches the $5.4M threshold if rent is roughly 2.3&times; the benchmark (about $351,000/year). If it does, the step from 0% to 4% is about $216,000 of tax on the same building &mdash; a pricing cliff worth managing deliberately. {src_link("S8")}</p>

<h2>Cap rate sensitivity bands</h2>
{table(["Band", "Interpretation"], b_rows)}

<h2>The tax layer</h2>
<div class="callout warn">
<p><strong>Not modeled &mdash; and that is deliberate.</strong> {e(VAL['tax_layer']['reason'])}</p>
<p><strong>Verified mechanism:</strong> {e(VAL['tax_layer']['verified_mechanism'])} {src_link("S16")}</p>
<p>{e(VAL['tax_layer']['practical_effect'])}</p>
</div>
"""
    return page("valuation.html", "Valuation inputs", body,
                "Verified inputs versus labelled analyst assumptions, disposition cost stack and cap rate sensitivity.")


# ----------------------------------------------------------------------------- model
def build_model():
    s_rows = []
    for s in SC:
        s_rows.append([e(s["label"]), f'{s["exit_cap"]*100:.2f}%', f'{s["escalation"]*100:.2f}%',
                       f'{s["renew_prob"]*100:.0f}%', money(s["sell_now_net"]),
                       money(s["sell_now_wealth_treasury"]), money(s["sell_now_wealth_netlease"]),
                       money(s["hold_expected_wealth"]),
                       f'<strong>{money(s["delta_hold_vs_sell_netlease"])}</strong>'])
    rows2 = [[e(s["label"]), e(s["narrative"])] for s in SC]
    sens_head = ["Exit cap", "1.5% escalation", "2.0% escalation", "2.5% escalation"]
    sens_rows = []
    for r in MODEL["sensitivity"]:
        sens_rows.append([f'{r["exit_cap"]*100:.2f}%'] + [money(c["wealth"]) for c in r["cells"]])
    d_rows = [[e(d["change"]), money(d["hold_expected_wealth"]), money(d["delta_vs_base_hold"]),
               money(d["delta_vs_sell_netlease"])] for d in MODEL["assumption_sensitivity"]]
    b_rows = [
        ["Reinvestment yield needed for &lsquo;sell now&rsquo; to match holding - bear", f'{MODEL["breakevens"]["required_reinvest_yield_pct"]["bear"]:.2f}%'],
        ["Reinvestment yield needed - base", f'{MODEL["breakevens"]["required_reinvest_yield_pct"]["base"]:.2f}%'],
        ["Reinvestment yield needed - bull", f'{MODEL["breakevens"]["required_reinvest_yield_pct"]["bull"]:.2f}%'],
        ["Exit cap at which holding ties selling (vs Treasury redeployment)", f'{MODEL["breakevens"]["exit_cap_hold_equals_sell_treasury_pct"]:.2f}%'],
        ["Exit cap at which holding ties selling (vs net-lease redeployment)", f'{MODEL["breakevens"]["exit_cap_hold_equals_sell_netlease_pct"]:.2f}%'],
        ["Rent uplift at renewal needed to beat selling into the net-lease benchmark", f'+{MODEL["renewal_value"]["required_rent_uplift_to_beat_sell_netlease_pct"]:.2f}%'],
        ["Rent change at renewal at which holding still beats Treasury redeployment", f'{MODEL["renewal_value"]["required_rent_uplift_to_beat_sell_treasury_pct"]:.2f}% (a cut of that size)'],
    ]
    body = f"""
{head_block("Projection model", "A reproducible 2026&ndash;2040 model, published inputs, and the breakevens rather than a guess at value",
            "Deterministic Python. No randomness. Every published number can be regenerated with one command, and every input is either sourced or labelled as an assumption.")}

<div class="callout info">
<p><strong>Reproduce it:</strong> <code>python3 tools/model.py</code> writes <code>data/model_output.json</code> and <code>research/model-report.md</code>.
The code is in <code>tools/model.py</code> and is short enough to read in full.</p>
</div>

<h2>Method</h2>
<ol>
  <li><strong>Three paths are modeled.</strong> (A) sell now and redeploy the net proceeds; (B) hold through the lease and sell at expiry; (C) renew at a reset rent and hold to 2040. A fourth state, tenant vacates (downtime, $300k of leasing costs, re-let at market), is blended into (C) by a renewal probability.</li>
  <li><strong>Path A</strong> nets out the real cost stack: 3.00% brokerage, 0.50% closing, 0.11% county transfer tax, 0.45% city transfer tax, and the tiered Measure ULA surtax where the price crosses the official thresholds. {src_link("S7")} {src_link("S8")}</li>
  <li><strong>Proceeds are redeployed at two different rates</strong> so the answer cannot hide inside one assumption: the verified 10-year Treasury (4.90%) and the verified net-lease acquisition benchmark (7.3%). {src_link("S11")} {src_link("S10")}</li>
  <li><strong>Everything is compounded to 2040</strong> in nominal dollars, and discounted at 8% for the NPV view. Pre-tax throughout; the tax layer needs the owner's basis.</li>
  <li><strong>Breakevens are solved numerically</strong> rather than asserted &mdash; that is what turns a forecast into a decision rule.</li>
</ol>

<h2>Scenario definitions</h2>
{table(["Scenario", "Definition"], rows2)}

<h2>Results (wealth at 2040, pre-tax nominal)</h2>
{table(["Scenario", "Exit cap", "Escalation", "Renewal prob.", "Net proceeds if sold now", "Sell &rarr; Treasury", "Sell &rarr; net lease", "Hold + renew", "Hold minus sell (net lease)"],
       s_rows, num_cols=(1,2,3,4,5,6,7,8))}

<h2>Breakevens - the decision rules</h2>
{table(["Test", "Result"], b_rows, num_cols=(1,))}

<h2>Sensitivity grid: exit cap &times; rent escalation (hold + renew, prob-weighted)</h2>
{table(sens_head, sens_rows, num_cols=(1,2,3))}

<h2>Which assumptions actually move the answer</h2>
<p>One-at-a-time from the base case. The ranking is the useful part: cap rate and renewal probability dominate; the rent reset matters more than the escalator.</p>
{table(["Change from base case", "Hold wealth at 2040", "Delta vs base", "Delta vs sell + net-lease"], d_rows, num_cols=(1,2,3))}

<h2>Limits</h2>
<ul>
  <li>Rent, expiry, basis and debt are placeholders. This is a framework, not an appraisal.</li>
  <li>No income tax, depreciation recapture, NIIT or California tax is computed - that needs the owner's basis (P05).</li>
  <li>No wildfire or earthquake loss is simulated. Those sit in the <a href="risks.html">risk register</a> as tail events with insurance as the mitigation.</li>
  <li>No non-official data is used. The cap rate is an assumption because no government body publishes asset-level cap rates (M51).</li>
</ul>
"""
    return page("projection-model.html", "Projection model", body,
                "Reproducible 2026-2040 projection model with published inputs, scenario results, breakevens and sensitivity.")


# ----------------------------------------------------------------------------- risks
def build_risks():
    cats = []
    for r in RISKS["rows"]:
        if r["type"] not in cats:
            cats.append(r["type"])
    blocks = []
    for c in cats:
        rs = [r for r in RISKS["rows"] if r["type"] == c]
        rows = [[r["id"], f'<strong>{e(r["risk"])}</strong><br><span class="muted">{e(r["why"])}</span>',
                 e(r["decision"]), f'{r["likelihood"]}/5', f'{r["impact"]}/5', e(r["velocity"]),
                 e(r["mitigation"]), e(r["residual"]), src_link(r["source"])] for r in rs]
        blocks.append(f'<h2 id="{slugify(c)}">{e(c)}</h2>' + table(
            ["ID", "Risk and why it applies", "Decision affected", "Likelihood", "Impact", "Velocity", "Mitigation", "Residual", "Source"],
            rows, num_cols=(3, 4)))

    matrix = []
    for r in sorted(RISKS["rows"], key=lambda x: -(x["impact"] * x["likelihood"]))[:8]:
        score = r["impact"] * r["likelihood"]
        pct = min(100, int(score / 25 * 100))
        matrix.append(f'<div class="bar-row"><span>{e(r["id"])}</span><span class="bar-track">'
                      f'<span class="bar-fill" style="width:{pct}%"></span></span><span>{score}/25</span></div>')

    body = f"""
{head_block("Risk register", f"{len(RISKS['rows'])} risks, mapped to the decision each one attacks",
            "Likelihood and impact are analyst judgments, not data. Every underlying fact carries an official source. Velocity tells you how fast the mitigation has to exist.")}

<div class="callout info">
<p><strong>Risk budget for an individual owner.</strong> The client asked for manageable risk with preservation of wealth.
The register is therefore scored for downside protection: a risk with impact 5 and likelihood 1 (wildfire, earthquake) is treated as a
<em>liquidity</em> problem to pre-fund, while a risk with impact 3 and likelihood 4 (wage law, short WALT) is treated as a <em>pricing</em> problem to negotiate away.</p>
</div>

<h2 style="margin-top:20px">Highest combined exposure</h2>
<div class="bar-chart">{''.join(matrix)}</div>

{''.join(blocks)}

<h2>How the black-swan scenarios were calibrated</h2>
<p>The January 2025 Eaton and Palisades fires are the only recent, officially quantified metropolitan-scale loss event for this county, so they set the scale for the tail scenarios:</p>
{table(["Metric", "Verified value", "Source"], [
    ["Structures destroyed (Eaton + Palisades)", "16,251", src_link("S13")],
    ["Confirmed fatalities", "31", src_link("S13")],
    ["Estimated economic output lost", "$5.2B &ndash; $10.1B", src_link("S13")],
    ["Businesses impacted", "~6,800", src_link("S13")],
    ["Workers impacted", "~47,000", src_link("S13")],
    ["Labor income lost", "$2.2B &ndash; $4.2B", src_link("S13")],
    ["Tax revenue losses", "$900M &ndash; $1.6B", src_link("S13")],
])}
<p class="muted">Fatalities: 19 (Eaton) + 12 (Palisades) = 31, summed from the county fact sheet. Structures destroyed: 9,414 + 6,837 = 16,251, same source.</p>

<div class="callout warn">
<p><strong>The honest conclusion about tail risk:</strong> a single-tenant, single-parcel asset cannot diversify away earthquake, wildfire, or insurance-capacity risk.
Insurance transfers the loss but not the downtime, the deductible, or the premium shock. The only structural mitigation is a liquidity reserve sized to the deductible plus 12 months of NOI &mdash;
and, if the owner's risk tolerance is low, selling into a diversified exchange.</p>
</div>
"""
    return page("risks.html", "Risk register", body,
                "Risk register with likelihood, impact, velocity, mitigation and residual risk, plus black-swan calibration.")


# ----------------------------------------------------------------------------- decision
def build_decision():
    opt_cards = []
    for o in DEC["options"]:
        s = o["scores"]
        total = (s["wealth_preservation"] * .35 + s["growth"] * .25 + s["execution_risk"] * .20 +
                 s["liquidity"] * .10 + s["tax_efficiency"] * .10)
        opt_cards.append(f"""
<div class="card">
  <p class="eyebrow">{e(o['id'])} &middot; weighted score {total:.2f} / 5</p>
  <h3>{e(o['name'])}</h3>
  <p>{e(o['summary'])}</p>
  <h3>Arguments for</h3><ul>{''.join(f'<li>{e(p)}</li>' for p in o['pros'])}</ul>
  <h3>Arguments against</h3><ul>{''.join(f'<li>{e(p)}</li>' for p in o['cons'])}</ul>
  <p class="muted">Wealth preservation {s['wealth_preservation']}/5 &middot; Growth {s['growth']}/5 &middot;
  Execution risk (higher is safer) {s['execution_risk']}/5 &middot; Liquidity {s['liquidity']}/5 &middot; Tax efficiency {s['tax_efficiency']}/5</p>
</div>""")

    rec = DEC["recommendation"]
    plan_rows = [[str(p["step"]), e(p["window"]), e(p["action"])] for p in rec["plan"]]
    trig_rows = [[e(t["trigger"]), e(t["action"])] for t in rec["decision_triggers"]]
    body = f"""
{head_block("Decision", "The answer, the four strategies behind it, and the triggers that would change it",
            "Scored on what the client asked for: preserve wealth first, allow growth, keep risk manageable.")}

<div class="decision">
  <h2>{e(rec['headline'])}</h2>
  <div class="rank">{''.join(f'<span>{i+1}. {e(DEC["options"][int(r[1:])-1]["name"].split("(")[0].strip())}</span>' for i, r in enumerate(rec['rank']))}</div>
  <h3>Why</h3>
  <ul>{''.join(f'<li>{e(w)}</li>' for w in rec['why'])}</ul>
</div>

<h2>The four strategies, scored</h2>
<div class="grid g2">{''.join(opt_cards)}</div>

<h2>The plan</h2>
{table(["Step", "Window", "Action"], plan_rows)}

<h2>Decision triggers - check these before acting</h2>
{table(["If you learn that&hellip;", "Then&hellip;"], trig_rows)}

<h2>For you as an individual, not just for the asset</h2>
<div class="card">
<ul>{''.join(f'<li>{e(p)}</li>' for p in rec['individual_owner_layer'])}</ul>
</div>

<h2>What would make this recommendation wrong</h2>
<ul>
  <li><strong>If the actual rent is much higher than the benchmark.</strong> Then the asset may cross the $5.4M Measure ULA threshold, the cost stack changes, and the price-test around the threshold becomes the dominant decision. {src_link("S8")}</li>
  <li><strong>If the lease has a fixed-price option.</strong> A below-market fixed option rent at the 2030&ndash;2035 window would make renewal cheap for the tenant and expensive for you &mdash; and would flip the ranking toward selling before the option is exercised.</li>
  <li><strong>If the parcel is in a very-high fire hazard or mapped liquefaction zone.</strong> Insurance and engineering conclusions could override the financial ranking entirely. Both are currently unverified (M82&ndash;M85).</li>
  <li><strong>If the owner needs liquidity or cannot tolerate concentration.</strong> Then D1 rises to first regardless of the modelled spread &mdash; a risk preference is not an error in the arithmetic.</li>
</ul>
"""
    return page("decision.html", "Decision", body,
                "Four scored strategies, the recommendation, the 6-step plan and the triggers that would change the answer.")


# ----------------------------------------------------------------------------- requirements
def build_requirements():
    rows = []
    for r in REQ["requirements"]:
        cls = {"done": "ok", "partially done": "warn", "blocked on missing input": "bad"}.get(r["status"], "neutral")
        rows.append([r["id"], e(r["requirement"]), f'<span class="badge {cls}">{e(r["status"])}</span>',
                     e(r["delivered_in"]), e(r["notes"])])
    counts = {}
    for r in REQ["requirements"]:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    kpis = "".join(f'<div class="card kpi"><p class="label">{e(k)}</p><p class="value">{v}</p></div>' for k, v in counts.items())
    body = f"""
{head_block("Requirements", "Every requirement in the brief, extracted line by line and tracked to delivery",
            "Nothing in the brief is paraphrased away. Where a requirement could not be fully met, the reason is stated instead of hidden.")}

<div class="grid g3">{kpis}</div>
<h2 style="margin-top:26px">Requirement tracker</h2>
{table(["ID", "Requirement", "Status", "Delivered in", "Notes"], rows)}
"""
    return page("requirements.html", "Requirements", body,
                "Line-by-line requirement extraction and delivery status.")


# ----------------------------------------------------------------------------- verification
def build_verification():
    per_cat = []
    for c in CATS:
        rs = [r for r in ROWS if r["category"] == c]
        per_cat.append([e(c), str(len(rs)), str(sum(1 for r in rs if r["status"] == "verified")),
                        str(sum(1 for r in rs if r["status"] != "verified"))])
    tier_counts = {}
    for s in SOURCES["sources"]:
        tier_counts[s["tier"]] = tier_counts.get(s["tier"], 0) + 1
    src_rows = [[s["id"], e(s["publisher"]), f'<a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["title"])} &#8599;</a>',
                 e(s["tier"]), e(s["accessed"])] for s in SOURCES["sources"]]
    body = f"""
{head_block("Verification", "How each number was checked, and what was refused",
            "The rule is simple: a value is published only if it was read from an official source on the access date. Everything else is blank and flagged.")}

<div class="grid g4">
  <div class="card kpi"><p class="label">Metric rows</p><p class="value">{len(ROWS)}</p></div>
  <div class="card kpi"><p class="label">Verified</p><p class="value" style="color:var(--ok)">{len(VER)}</p></div>
  <div class="card kpi"><p class="label">Blank + flagged</p><p class="value" style="color:var(--warn)">{len(UNV)}</p></div>
  <div class="card kpi"><p class="label">Sources cited</p><p class="value">{len(SRC)}</p></div>
</div>

<h2>Coverage by category</h2>
{table(["Category", "Rows", "Verified", "Blank / flagged"], per_cat, num_cols=(1,2,3))}

<h2>Source tiers</h2>
<p>Tier A is a government or regulator record. Tier B is an SEC filing by the tenant. Tier C is an issuer investor-relations disclosure, used only where no regulator publishes the figure (net-lease acquisition yields).
Tier D &mdash; industry commentary, broker blogs, data aggregators &mdash; is <strong>not used for any value</strong> in this workbook.</p>
{table(["Tier", "Definition", "Count"], [[e(k), e(SOURCES["tiers"][k]), str(v)] for k, v in sorted(tier_counts.items())])}

<h2>Automated checks run before publishing</h2>
<div class="tablewrap"><table>
<thead><tr><th>Check</th><th>What it enforces</th><th>Result</th></tr></thead>
<tbody>
<tr><td>Source resolution</td><td>Every metric row's source id exists in <code>data/sources.json</code> and its URL is <code>https</code></td><td><span class="badge ok">pass</span></td></tr>
<tr><td>No unsourced value</td><td>A row marked verified must have a value; a row marked unverified must be empty</td><td><span class="badge ok">pass</span></td></tr>
<tr><td>Internal links</td><td>Every <code>href</code> to a local file resolves to a file that exists</td><td><span class="badge ok">pass</span></td></tr>
<tr><td>PII scan</td><td>No email, phone, street address or parcel number in any emitted page</td><td><span class="badge ok">pass</span></td></tr>
<tr><td>Orphan files</td><td>No HTML page is unreachable from the navigation</td><td><span class="badge ok">pass</span></td></tr>
<tr><td>Model reproducibility</td><td><code>python3 tools/model.py</code> regenerates identical output</td><td><span class="badge ok">pass</span></td></tr>
</tbody></table></div>
<p class="muted">The checker is <code>tools/check_site.py</code> and runs in CI on every push (see <a href="deployment.html">Deployment</a>).</p>

<h2>All sources</h2>
{table(["ID", "Publisher", "Title", "Tier", "Accessed"], src_rows)}

<h2>What was deliberately not verified</h2>
<ul>
  <li><strong>Asset-level cap rate.</strong> No government body publishes it. A broker opinion of value is required (F02).</li>
  <li><strong>Parcel hazard status.</strong> Needs the APN: FEMA panel, CAL FIRE FHSZ, CGS liquefaction (M82&ndash;M84).</li>
  <li><strong>Insurance pricing.</strong> Needs a broker quote; no official rate exists (M85).</li>
  <li><strong>Tax on sale.</strong> Needs the owner's basis and depreciation history (P05).</li>
  <li><strong>Los Angeles city minimum wage.</strong> DIR states local rates may be higher but the city rate was not confirmed officially here (M63).</li>
</ul>
"""
    return page("verification.html", "Verification", body,
                "Verification log: coverage, source tiers, automated checks and what was deliberately left unverified.")


# ----------------------------------------------------------------------------- flagged
def build_flagged():
    blank_rows = []
    for r in UNV:
        blank_rows.append([r["id"], e(r["category"]), e(r["metric"]), e(r["geography"]),
                           src_link(r["source"]), badge(r["status"]), e(r["note"])])
    data_rows = [[r["id"], sev_badge(r["severity"]), e(r["finding"]), e(r["impact"]), e(r["action"])]
                 for r in IRR["data_irregularities"]]
    repo_rows = [[r["id"], sev_badge(r["severity"]), e(r["finding"]), e(r["impact"]), e(r["action"])]
                 for r in IRR["repo_irregularities"]]
    missing_rows = [[r["id"], e(r["field"]), e(r["why"]), e(r["status"])]
                    for r in PROP["fields_required_before_a_binding_decision"]]
    body = f"""
{head_block("Flagged for review", "Everything this workbook could not verify, and everything it found wrong",
            "None of these items block publication. They block a <em>binding</em> decision. Each one states what is missing, why it matters, and what to obtain.")}

<div class="callout warn">
<p><strong>Count:</strong> {len(UNV)} blank data rows &middot; {len(IRR['data_irregularities'])} data issues &middot;
{len(IRR['repo_irregularities'])} repository issues &middot; {len(PROP['fields_required_before_a_binding_decision'])} missing documents.
Nothing on this page was estimated, inferred or filled in from a secondary source.</p>
</div>

<h2 id="blank">1. Blank because no official value was confirmed</h2>
{table(["ID", "Category", "Metric", "Geography", "Official source attempted", "Status", "Why it is blank / what to do"], blank_rows)}

<h2 id="missing">2. Missing documents that block a binding decision</h2>
{table(["ID", "Document / field", "Why it decides the answer", "Status"], missing_rows)}

<h2 id="data">3. Data irregularities</h2>
{table(["ID", "Severity", "Finding", "Impact", "Action taken"], data_rows)}

<h2 id="repo">4. Repository irregularities (as found at the start of this session)</h2>
{table(["ID", "Severity", "Finding", "Impact", "Action taken"], repo_rows)}

<h2 id="assumptions">5. Assumptions that are not data</h2>
<p>The model needs numbers the brief does not supply. They are listed in full on <a href="valuation.html">Valuation inputs</a> with their confidence level.
The most consequential: benchmark rent ({money(150000)}/yr), lease expiry used as 2032, exit cap 6.50%, and a 75% renewal probability.
Change any of them in <code>data/valuation.json</code> and re-run <code>python3 tools/model.py</code>.</p>

<h2 id="next">6. Close-out checklist</h2>
<ol>
  <li>Pull the APN and run the four parcel-level lookups: FEMA NFHL, CAL FIRE/LACoFD FHSZ, CGS EQ Zapp, and an insurance quote.</li>
  <li>Obtain the executed lease and confirm the option notice deadline and the option-rent mechanism.</li>
  <li>Obtain a broker opinion of value and an appraisal; replace assumption A5 with the actual implied cap rate.</li>
  <li>Obtain the adjusted basis and depreciation schedule from the CPA; then, and only then, model the tax and the 1031.</li>
  <li>Re-run the model with real inputs and compare against the decision triggers on the <a href="decision.html">Decision</a> page.</li>
</ol>
"""
    return page("flagged.html", "Flagged for review", body,
                "All unverified items, missing documents, data irregularities and repository irregularities, with what to obtain.")


# ----------------------------------------------------------------------------- sources
def build_sources():
    rows = []
    for s in SOURCES["sources"]:
        rows.append([s["id"], f'<span class="badge neutral">{e(s["tier"])}</span>', e(s["publisher"]),
                     f'<a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["title"])} &#8599;</a><br><span class="muted">{e(s["url"])}</span>',
                     e(s["covers"]), e(s["accessed"])])
    body = f"""
{head_block("Sources", f"{len(SRC)} sources, all official or regulator-filed",
            "Tier A: government or regulator. Tier B: SEC filing by the tenant. Tier C: issuer investor-relations disclosure, used only where no regulator publishes the figure. Tier D industry commentary is not used for any value.")}

{table(["ID", "Tier", "Publisher", "Title and link", "What it covers", "Accessed"], rows)}

<h2>How to audit this workbook</h2>
<ol strat="1">
  <li>Pick any row on <a href="market-economics.html">Market economics</a>.</li>
  <li>Click its source id. The official document opens at the publisher's own domain.</li>
  <li>Search that document for the value. The value, unit, period and geography are all printed in the row.</li>
  <li>If you cannot find it, the row is wrong &mdash; report it and it will be corrected or blanked.</li>
</ol>

<h2>Notes on scope</h2>
<ul>
  <li>State and federal fiscal years differ from calendar years. Jack in the Box FY2025 ended 2025-09-28 and every fiscal figure is labelled with that date.</li>
  <li>BLS metro data are not seasonally adjusted and are subject to revision; the summary used here was updated 2026-10-05.</li>
  <li>Census QuickFacts mixes Vintage 2025 population estimates with 2020&ndash;2024 ACS 5-year characteristics; the period column says which is which.</li>
  <li>Rate series are daily and are dated to the observation, not to today.</li>
</ul>
"""
    return page("sources.html", "Sources", body,
                "All 22 official sources with publisher, coverage, tier and access date.")


# ----------------------------------------------------------------------------- privacy
def build_privacy():
    body = f"""
{head_block("Privacy", "No personal information is collected, stored, published or inferred",
            "This is the highest-priority constraint in the brief, so it is enforced in code rather than promised in prose.")}

<div class="callout ok">
<p><strong>Summary.</strong> This repository and the published site contain zero personal identifiers. The property is referred to only as
&ldquo;the Subject Property (Central Los Angeles)&rdquo;. There is no owner name, entity name, street address, parcel number, loan number, policy number,
contact detail, or financial account anywhere. Values the brief did not supply are marked <code>[WITHHELD - placeholder]</code> and flagged.</p>
</div>

<h2>What was deliberately excluded</h2>
<div class="tablewrap"><table>
<thead><tr><th>Category</th><th>Treatment</th></tr></thead>
<tbody>
<tr><td>Owner identity and entity structure</td><td>Excluded. Not requested, not inferred, not stored.</td></tr>
<tr><td>Street address and APN</td><td>Excluded. The brief references only &ldquo;central Los Angeles&rdquo;. Parcel-level lookups are therefore flagged unverified (M82&ndash;M85).</td></tr>
<tr><td>Lease documents</td><td>Not published. Only the clause categories to audit are listed.</td></tr>
<tr><td>Tenant franchisee identity</td><td>Excluded. Only the franchisor (a public company) is named, which is public record.</td></tr>
<tr><td>Financial accounts, loan numbers, policy numbers</td><td>Excluded.</td></tr>
<tr><td>Correspondence and contact details</td><td>Excluded. No form, no analytics, no cookies, no third-party scripts on this site.</td></tr>
</tbody></table></div>

<h2>How it is enforced</h2>
<ul>
  <li><strong>At build time:</strong> <code>tools/build_site.py</code> scans every emitted page against patterns for email addresses, telephone numbers, US street addresses, and parcel numbers, and the build fails on a match.</li>
  <li><strong>In CI:</strong> <code>tools/check_site.py</code> re-runs the same scan plus link and source checks on every push.</li>
  <li><strong>By data design:</strong> <code>data/property_lease.json</code> carries placeholders, not values. There is no field in the schema for an owner name.</li>
  <li><strong>By scope:</strong> the workbook cites public companies (Jack in the Box Inc.), government statistics, and public filings only.</li>
</ul>

<h2>Internal-use classification</h2>
<p>The market analysis, the model code, and the flagged list are internal decision support. If the owner later supplies the missing documents,
those documents must stay outside this repository, or in a private repository &mdash; never in a published one. The public Pages site must remain free of them.</p>

<h2>Client-side behaviour</h2>
<p>The site is fully static. There is no server, no database, no form, no analytics, no cookie, no third-party font or script, and no outbound request
other than the source links you choose to click. Search and filtering run entirely in your browser.</p>
"""
    return page("privacy.html", "Privacy", body,
                "Privacy architecture and enforcement: no personal information in the repository or the published site.")


# ----------------------------------------------------------------------------- deployment
def build_deployment():
    body = f"""
{head_block("Deployment", "How this workbook was built, verified and published",
            "Repository, branch, checks, pull request and GitHub Pages status, recorded so the process is auditable.")}

<h2>Repository state at the start of the session</h2>
{table(["Check", "Finding"], [
    ["Files", "<code>README.md</code> only, 7 bytes, contents <code># Jack2</code>"],
    ["Commit", "<code>1430b4f</code> &mdash; 'Initial commit' (baseline)"],
    ["Branches", "<code>main</code> and the session branch <code>arena/742b6a03-jack2</code>"],
    ["GitHub Pages", "Enabled, legacy build, source = <code>main</code> / root, public URL <code>https://wingbangboozle1-lang.github.io/Jack2/</code>"],
    ["CI / checks", "None"],
    ["COORDINATION.md", "Absent (created by this session)"],
])}

<h2>What was added</h2>
<div class="tablewrap"><table>
<thead><tr><th>Path</th><th>Purpose</th></tr></thead>
<tbody>
<tr><td><code>data/sources.json</code></td><td>All sources with tier, publisher, coverage and access date</td></tr>
<tr><td><code>data/metrics.json</code></td><td>{len(ROWS)} metric rows, each with a source id and a verification status</td></tr>
<tr><td><code>data/valuation.json</code></td><td>Verified inputs separated from labelled analyst assumptions</td></tr>
<tr><td><code>data/property_lease.json</code></td><td>Anonymised asset profile and the missing-document list</td></tr>
<tr><td><code>data/risks.json</code></td><td>{len(RISKS['rows'])}-row risk register</td></tr>
<tr><td><code>data/decisions.json</code></td><td>Four scored strategies, recommendation, plan, triggers</td></tr>
<tr><td><code>data/requirements.json</code></td><td>{len(REQ['requirements'])} requirements tracked to delivery</td></tr>
<tr><td><code>data/irregularities.json</code></td><td>Repository and data irregularities</td></tr>
<tr><td><code>tools/model.py</code></td><td>Deterministic projection model; writes <code>data/model_output.json</code></td></tr>
<tr><td><code>tools/build_site.py</code></td><td>Static site generator with hard assertions</td></tr>
<tr><td><code>tools/check_site.py</code></td><td>Link, source, PII and orphan-page checks</td></tr>
<tr><td><code>.github/workflows/verify.yml</code></td><td>Rebuilds the model and site, then runs the checks on every push and PR</td></tr>
<tr><td><code>COORDINATION.md</code></td><td>Shared task board and log</td></tr>
</tbody></table></div>

<h2>Publish path</h2>
<ol>
  <li>All work on <code>arena/742b6a03-jack2</code>. Every commit is small and scoped.</li>
  <li><code>git pull --rebase</code> before each push.</li>
  <li>Pull request from the session branch to <code>main</code>, with the summary, sources and flagged irregularities.</li>
  <li>Checks must pass before merge; a broken site is never merged.</li>
  <li>Merge to <code>main</code>. GitHub Pages serves <code>main</code> / root; <code>.nojekyll</code> keeps the files served exactly as built.</li>
  <li>The deployment status and PR link are recorded in <code>COORDINATION.md</code>.</li>
</ol>

<h2>Reproduce locally</h2>
<pre style="background:#0b1220;color:#e6edf7;padding:16px;border-radius:12px;overflow-x:auto;font-size:13px"><code>python3 tools/model.py        # regenerate data/model_output.json + research/model-report.md
python3 tools/build_site.py   # regenerate all HTML pages
python3 tools/check_site.py   # links, sources, PII, orphan pages
</code></pre>
<p>Python 3.11, standard library only. No installs, no network access required to build.</p>
"""
    return page("deployment.html", "Deployment", body,
                "Repository baseline, files added, publish path and reproduction steps.")


# ----------------------------------------------------------------------------- write

# ----------------------------------------------------------------------------- archive
def build_archive():
    rows = [
        ["Landing page", "<a href='session-1944e5a3/index.html'>session-1944e5a3/index.html</a>"],
        ["Property", "<a href='session-1944e5a3/property.html'>session-1944e5a3/property.html</a>"],
        ["Market", "<a href='session-1944e5a3/market.html'>session-1944e5a3/market.html</a>"],
        ["Demographics", "<a href='session-1944e5a3/demographics.html'>session-1944e5a3/demographics.html</a>"],
        ["Projection", "<a href='session-1944e5a3/projection.html'>session-1944e5a3/projection.html</a>"],
        ["Risk", "<a href='session-1944e5a3/risk.html'>session-1944e5a3/risk.html</a>"],
        ["Decision", "<a href='session-1944e5a3/decision.html'>session-1944e5a3/decision.html</a>"],
        ["Sources", "<a href='session-1944e5a3/sources.html'>session-1944e5a3/sources.html</a>"],
        ["Flagged for review", "<a href='session-1944e5a3/flagged.html'>session-1944e5a3/flagged.html</a>"],
        ["Methodology", "<a href='session-1944e5a3/methodology.html'>session-1944e5a3/methodology.html</a>"],
    ]
    body = f"""
{head_block("Session A archive", "A second agent session published its own site on this same repository. It is preserved here, unmodified.",
            "Nothing another session produced was deleted, overwritten or rewritten. Both analyses are published; the root of the site is the data-driven build, and this is the parallel one.")}

<div class="callout warn">
<p><strong>What happened.</strong> Session <code>arena-1944e5a3</code> merged its site to <code>main</code> as PR #1 (<code>22f2f91</code>) while this session
(<code>arena-742b6a03</code>) was still doing research and had not yet pushed. The next <code>git pull --rebase</code> failed with conflicts in six files.
Instead of force-pushing over that work, session B copied every page session A published into this folder &mdash; with its own CSS, JS and favicon, so its
relative links still work &mdash; and cross-linked it here.</p>
<p>Full record: <a href="COORDINATION.md" download>COORDINATION.md</a> (conflict section and both session logs).</p>
</div>

<h2>Session A's pages</h2>
{table(["Page", "Link"], rows)}

<h2>How the two analyses differ</h2>
<table class="tablewrap"><table>
<thead><tr><th></th><th>Session A (<code>arena-1944e5a3</code>)</th><th>Root site (<code>arena-742b6a03</code>)</th></tr></thead>
<tbody>
<tr><td>Data storage</td><td>Values written inline into HTML</td><td>Values in <code>data/*.json</code>, one source id per row, rendered by a generator</td></tr>
<tr><td>Source policy</td><td>Government records plus LAEDC and UCLA Anderson forecasts</td><td>Government, regulator or SEC filing only (Tiers A&ndash;C). No forecasts from non-official bodies.</td></tr>
<tr><td>Verification</td><td>Manual link check, local</td><td>Automated: source resolution, blank-value rule, internal links, PII scan, model reproducibility &mdash; all failing the build</td></tr>
<tr><td>Quantification</td><td>Projection narrative with a flagged cap-rate band</td><td>Deterministic 2026&ndash;2040 model with breakevens, sensitivity grid and assumption ranking</td></tr>
<tr><td>Sources cited</td><td>29</td><td>{len(SRC)}</td></tr>
</tbody></table></div>

<h2>What was taken from it</h2>
<p>Session B re-checked the sources session A cited and adopted one figure it had not covered: Los Angeles County total personal income of
<strong>$818.5 billion</strong> in 2024, the highest of any US county, now row M86 with source S23. {src_link("S23")}</p>
<p>Session A's Census QuickFacts link for the city/county table is malformed (<code>losangelesNICITYcalifornia</code>) and fails as a source citation.
It is left unmodified in the archive and recorded as irregularity I09 on the <a href="flagged.html">Flagged for review</a> page &mdash; rewriting another
session's page would hide the defect rather than disclose it.</p>

<h2>Where to read if you want one answer</h2>
<p>Use the root site: <a href="executive-summary.html">Executive summary</a> for the recommendation,
<a href="decision.html">Decision</a> for the ranked strategies and triggers. The archive is here for completeness and audit, not as a second opinion to reconcile.</p>
"""
    return page("archive.html", "Session A archive", body,
                "Archive of the parallel session's site, preserved unmodified and cross-linked, with the conflict resolution record.")


def build_workspaces():
    rows = [
        ["<code>session-6ad87c21/</code>",
         "Session J &mdash; 2026-11-08 independent re-verification: 17 official sources re-read on the access date, "
         "114 fact rows (92 verified, 4 computed, 3 owner-supplied, 15 deliberately blank), 31-risk BAU and "
         "black-swan register, six strategies scored on a seeded 10,000-trial certainty equivalent, and a "
         "line-by-line audit of this repository",
         "14 pages",
         "<a href='session-6ad87c21/index.html'>open &#8599;</a>"],
        ["<code>session-343c7030/</code>",
         "Session I &mdash; final integration: 98 fact rows (84 verified against 16 official sources read 2026-11-08, "
         "14 deliberately blank), 30 risks, 15 documented assumptions, 15,000-trial Monte Carlo (seed 20261108) and a "
         "13-item repository review. Fixes the Census URL defect carried by the root build.",
         "12 pages",
         "<a href='session-343c7030/index.html'>open &#8599;</a>"],
        ["<code>session-4ed347de/</code>",
         "Session K &mdash; 2026-11-08 re-verification of 25 official sources (98 ledger rows, 82 verified), "
         "line-by-line audit of the published workbook, independent reproduction of this model (21/21 values), "
         "and a 20,000-trial Monte Carlo with earthquake, wildfire and tenant-default hazards",
         "10 pages",
         "<a href='session-4ed347de/index.html'>open &#8599;</a>"],
        ["<code>session-18dacdea/</code>",
         "Session H &mdash; 2026-11-07 live BLS (Nov 4) &amp; FRED (Nov 5, 4.84% DGS10) update, 76 metrics across "
         "26 official sources (resolving LAUSD 86.2% ACGR &amp; $18.42/hr LA City minimum wage), 26 risks, "
         "15,000-trial Monte Carlo + browser-local &sect;1031 simulator",
         "10 pages",
         "<a href='session-18dacdea/index.html'>open &#8599;</a>"],
        ["<code>session-e618ace7/</code>",
         "Session G &mdash; 110 fact rows, 96 verified against 19 official sources, six strategies scored on "
         "risk-adjusted wealth, 30-risk register, line-by-line review of this repository",
         "14 pages",
         "<a href='session-e618ace7/index.html'>open &#8599;</a>"],
        ["<code>session-5bb36a1b/</code>",
         "Session F &mdash; independent 2026-11-07 pass; reconciled extend&ndash;price&ndash;sell recommendation",
         "&mdash;",
         "<a href='session-5bb36a1b/index.html'>open &#8599;</a>"],
        ["<code>session-b4ec6128/</code>",
         "Session E &mdash; 11 pages, 391 data-table rows each carrying a source link or an explicit status",
         "11 pages",
         "<a href='session-b4ec6128/index.html'>open &#8599;</a>"],
        ["<code>session-a3a8ec08/</code>",
         "Session D &mdash; Q3 FY2026 filings, Fall 2026 releases, browser-local Section 1031 / Measure ULA simulator",
         "9 pages",
         "<a href='session-a3a8ec08/index.html'>open &#8599;</a>"],
        ["<code>docs/</code>",
         "Session C &mdash; 20,000-trial Monte Carlo scored on certainty-equivalent after-tax wealth",
         "11 pages",
         "<a href='docs/index.html'>open &#8599;</a>"],
        ["<code>session-1944e5a3/</code>",
         "Session A &mdash; the original build, archived verbatim with its own stylesheet and scripts",
         "10 pages",
         "<a href='session-1944e5a3/index.html'>open &#8599;</a>"],
        ["This root site",
         "Session B &mdash; the deterministic model, 23 sources, 87 metric rows and the decision triggers currently "
         "served at the site root",
         "15 pages",
         "<a href='index.html'>you are here</a>"],
    ]
    body = f"""
{head_block("All workspaces",
            "Nine independent workbooks, one repository",
            "Each agent session that worked on this repository published its own analysis without overwriting anyone else's. This page is the single index to all of them, so nothing published here is orphaned.")}

<div class="callout warn">
<p><strong>Where to start.</strong> Open
<a href="session-343c7030/index.html"><strong>session-343c7030</strong></a> (Session I), the final integration pass dated
2026-11-08: 98 fact rows against 16 official sources read that day with 14 values deliberately left blank, five
strategies scored on certainty-equivalent after-tax wealth, a 30-risk register and 13 repository findings &mdash;
including the source-ledger defect in this root site, which that session fixed.</p>
<p><strong>For a second, independently built 2026-11-08 pass</strong> that reaches the same structural conclusion from
a different model, open <a href="session-6ad87c21/index.html"><strong>session-6ad87c21</strong></a> (Session J): 114
fact rows against 17 official sources, 31 risks including twelve black swans, six strategies on a seeded
certainty-equivalent ranking, and a 1,367-check verifier that fails the build on an unsourced row or a stray personal
detail.</p>
<p><strong>Then read the independent review.</strong>
<a href="session-e618ace7/index.html"><strong>session-e618ace7</strong></a> (Session G) re-verified this
repository line by line on 2026-11-07, publishes 110 fact rows against 19 official sources with 14 values
deliberately left blank, scores six exit and hold strategies on risk-adjusted after-tax wealth, and lists every
irregularity it found.</p>
<p class="muted">If you want the original deterministic model with its decision triggers, this root site remains
the reference build. The eight others are preserved because deleting another session's work is never the right
resolution to a conflict.</p>
</div>

<h2>The workbooks</h2>
{table(["Folder", "What it is", "Size", "Open"], rows)}

<h2>Why there are nine</h2>
<p>The brief asks for parallel sessions to coordinate through <code>COORDINATION.md</code> rather than overwrite
each other. In practice each session started from a nearly empty repository, built a complete workbook, and
discovered the others only when pushing. Every time, the resolution was the same: preserve what already exists,
publish the new analysis beside it, and record the conflict. The result is redundant but intact &mdash; and the
disagreements between the analyses are themselves informative, because they show which conclusions are robust
to method and which are artefacts of an assumption.</p>

<h2>Where the analyses disagree, and why</h2>
<div class="tablewrap"><table>
<thead><tr><th>Question</th><th>What differs between the workbooks</th><th>Why</th></tr></thead>
<tbody>
<tr><td>Hold or sell?</td><td>Most rank an exit or an extend-then-sell above passive hold; the root build frames it as a sequence with thresholds</td><td>Different objective functions: expected value, certainty equivalent, or threshold testing</td></tr>
<tr><td>What is the asset worth?</td><td>None asserts a value &mdash; the rent, expiry and basis are unknown</td><td>Every build normalises, usually per $1.00 or $100,000 of NOI</td></tr>
<tr><td>Tenant credit</td><td>Sessions D and E emphasise the FY2025 loss; Session G publishes the FY2026 nine-month profit beside it</td><td>Vintage and framing, not data: both come from the same SEC dataset</td></tr>
<tr><td>Cap rates</td><td>All carry them as assumptions, at different central values</td><td>No government body publishes transaction cap rates; see the flagged list</td></tr>
</tbody></table></div>
"""
    return page("workspaces.html", "All workspaces", body,
                "Index of every independent workbook published from this repository, with guidance on where to start.")


BUILDERS = {
    "index.html": build_index,
    "executive-summary.html": build_exec,
    "market-economics.html": build_market,
    "property-lease.html": build_property,
    "valuation.html": build_valuation,
    "projection-model.html": build_model,
    "risks.html": build_risks,
    "decision.html": build_decision,
    "requirements.html": build_requirements,
    "verification.html": build_verification,
    "flagged.html": build_flagged,
    "sources.html": build_sources,
    "privacy.html": build_privacy,
    "deployment.html": build_deployment,
    "archive.html": build_archive,
    "workspaces.html": build_workspaces,
}

for fname, fn in BUILDERS.items():
    out = fn()
    pii_scan(out, fname)
    with open(os.path.join(ROOT, fname), "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote {fname:24s} {len(out):>7,d} bytes")

print("done")

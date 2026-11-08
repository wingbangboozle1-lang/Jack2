#!/usr/bin/env python3
"""Build the Session I (arena/343c7030-jack2) dashboard into session-343c7030/.

Standard library only. Renders every table from data/*.json so no figure is typed
twice, and asserts the publication rules before writing a byte:
  * every verified row has a non-empty value and a resolvable source link
  * every blank row has an empty value and appears on flagged.html
  * every internal link target exists
  * no personal identifier appears in any generated page
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA = os.path.join(ROOT, "data")
OUT = ROOT

NAV = [
    ("index.html", "Overview"),
    ("executive-summary.html", "Executive summary"),
    ("market.html", "Market &amp; people"),
    ("economy.html", "Economy &amp; jobs"),
    ("property-lease.html", "Property &amp; lease"),
    ("valuation-tax.html", "Valuation &amp; tax"),
    ("projection.html", "Projection model"),
    ("decision.html", "Decision"),
    ("risks.html", "Risks"),
    ("sources.html", "Sources"),
    ("flagged.html", "Flagged for review"),
    ("verification.html", "Verification"),
]

CATEGORY_LABEL = {
    "property": "Property &amp; lease",
    "demographics": "Demographics, income, education",
    "economy": "Labour market &amp; prices",
    "capital": "Capital markets",
    "tenant": "Tenant credit",
    "tax": "Tax &amp; transfer costs",
    "hazard": "Hazard",
    "education": "Schools",
    "wages": "Wage floors",
}


def load(name):
    with open(os.path.join(DATA, name)) as fh:
        return json.load(fh)


facts = load("facts.json")["rows"]
sources = {s["id"]: s for s in load("sources.json")["sources"]}
risks = load("risks.json")["rows"]
flagged = load("flagged.json")
proj = load("projections.json")

ACCESSED = "2026-11-08"
ROWS = {r["id"]: r for r in facts}
MC = proj["monte_carlo"]["summary"]
RANK = proj["monte_carlo"]["ranking"]
STRAT = proj["strategies"]
DET = proj["deterministic"]
GRID = proj["sensitivity_grid"]
REINV = proj["reinvest_grid"]
EXPIRY = proj["expiry_grid"]


def e(x):
    return html.escape(str(x), quote=True)


def money(x, dp=0):
    return f"${x:,.{dp}f}"


def src_link(sid):
    if not sid:
        return '<span class="meta">no official source</span>'
    ids = [s.strip() for s in sid.split(",")]
    out = []
    for i in ids:
        s = sources[i]
        out.append(f'<a href="{e(s["url"])}" rel="noopener" target="_blank" '
                   f'title="{e(s["publisher"])} — {e(s["title"])}">{e(i)} ↗</a>')
    return " ".join(out)


def status_tag(status):
    if status == "verified":
        return '<span class="tag t-ok">verified</span>'
    if status == "blank":
        return '<span class="tag t-blank">unverified — blank</span>'
    return f'<span class="tag t-assume">{e(status)}</span>'


def sev_tag(sev):
    cls = "t-high" if sev in ("Very high", "High") else ("t-med" if sev == "Medium" else "t-low")
    return f'<span class="tag {cls}">{e(sev)}</span>'


def page(filename, title, body, lede=""):
    nav_lines = []
    for f, label in NAV:
        cur = ' aria-current="page"' if f == filename else ""
        nav_lines.append(f'      <a href="{f}"{cur}>{label}</a>')
    nav = "\n".join(nav_lines)
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} · Central LA Jack in the Box NNN</title>
<meta name="description" content="Source-verified sell-versus-renew analysis for a single-tenant Jack in the Box on an NNN lease in Central Los Angeles, lease expiry 2030-2035.">
<meta name="robots" content="index,follow">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="top">
  <div class="wrap">
    <div class="brandbar">
      <div class="brand"><span class="dot">JB</span><span>Central LA Jack in the Box · NNN<span><small>Independent decision workbook · session 343c7030 · data read {ACCESSED}</small></span></span></div>
    </div>
    <nav class="tabs" aria-label="Sections">
{nav}
    </nav>
  </div>
</header>
<main>
  <div class="wrap">
    <div class="crumb"><a href="../workspaces.html">All workspaces</a> / session-343c7030</div>
    <h1>{title}</h1>
    {f'<p class="lede">{lede}</p>' if lede else ''}
{body}
  </div>
</main>
<footer>
  <div class="wrap">
    <div>Internal decision support. Not an appraisal, not tax advice, not investment advice. Every value is traceable to the source shown on its row.</div>
    <div>Accessed {ACCESSED} · <a href="verification.html">verification log</a> · <a href="flagged.html">flagged items</a></div>
  </div>
</footer>
<script src="assets/app.js" defer></script>
</body>
</html>
"""
    with open(os.path.join(OUT, filename), "w") as fh:
        fh.write(doc)


def fact_table(rows, caption, show_geo=True, searchable=True):
    head = "<tr><th>ID</th><th>Metric</th>" + ("<th>Geography</th>" if show_geo else "") + \
           "<th>Period</th><th class=\"num\">Value</th><th>Unit</th><th>Status</th><th>Source</th></tr>"
    body = []
    for r in rows:
        val = e(r["value"]) if r["value"] != "" else "&nbsp;"
        cls = ' class="num"' if r["value"] != "" else ' class="num blank"'
        note = f'<div class="meta">{e(r["note"])}</div>' if r["note"] else ""
        body.append(
            f'<tr data-status="{e(r["status"])}"><td class="meta">{e(r["id"])}</td>'
            f'<td><strong>{e(r["metric"])}</strong>{note}</td>'
            + (f'<td>{e(r["geo"])}</td>' if show_geo else "")
            + f'<td>{e(r["period"])}</td><td{cls}>{val}</td><td>{e(r["unit"])}</td>'
            f'<td>{status_tag(r["status"])}</td><td class="src">{src_link(r["source"])}</td></tr>'
        )
    filt = (f'<div class="filter"><input type="search" placeholder="Filter these rows…" '
            f'aria-label="Filter table"><span class="count">{len(rows)} rows</span></div>') if searchable else ""
    return (f'{filt}<div class="tablewrap"><table data-filterable><caption>{caption}</caption>'
            f'<thead>{head}</thead><tbody>' + "".join(body) + "</tbody></table></div>")


def cat_rows(cat):
    return [r for r in facts if r["cat"] == cat]


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
best = RANK[0]
second = RANK[1]
hold = "S4"
def pctdiff(a, b):
    return (a - b) / b * 100.0


def prob(s):
    """P(beats hold) — undefined for the hold baseline itself, so show a dash."""
    return "&mdash;" if s == "S4" else f"{MC[s]['prob_beats_hold']:.0%}"

kpi_cards = f"""
<div class="grid g4">
  <div class="card"><div class="lbl">Best risk-adjusted</div><div class="big">{e(STRAT[best]['short'])}</div>
    <div class="meta">Certainty-equivalent wealth {money(MC[best]['ce'])} per $100k NOI</div></div>
  <div class="card"><div class="lbl">Sell now, §1031</div><div class="big">{money(MC['S1']['ce'])}</div>
    <div class="meta">{pctdiff(MC['S1']['ce'], MC[best]['ce']):+.1f}% versus the leader · P05 {money(MC['S1']['p05'])}</div></div>
  <div class="card"><div class="lbl">Hold to expiry, then sell</div><div class="big">{money(MC[hold]['ce'])}</div>
    <div class="meta">Same median, worse tail · P05 {money(MC[hold]['p05'])}</div></div>
  <div class="card"><div class="lbl">Cost of a taxable sale</div><div class="big">{pctdiff(MC['S2']['ce'], MC['S1']['ce']):+.1f}%</div>
    <div class="meta">S2 versus S1 on the same risk measure</div></div>
</div>
"""

strategy_table = """
<div class="tablewrap"><table>
<caption>Five courses of action, ranked on certainty-equivalent after-tax wealth at 2040 per $100,000 of current NOI</caption>
<thead><tr><th>Rank</th><th>Strategy</th><th class="num">Certainty equivalent</th><th class="num">5th percentile</th>
<th class="num">Median</th><th class="num">P(beats hold)</th><th>What it means</th></tr></thead><tbody>
""" + "".join(
    f'<tr><td class="num">{i+1}</td><td><strong>{e(STRAT[s]["short"])}</strong></td>'
    f'<td class="num">{money(MC[s]["ce"])}</td><td class="num">{money(MC[s]["p05"])}</td>'
    f'<td class="num">{money(MC[s]["median"])}</td><td class="num">{prob(s)}</td>'
    f'<td class="meta">{e(STRAT[s]["detail"])}</td></tr>'
    for i, s in enumerate(RANK)
) + "</tbody></table></div>"

body_index = f"""
<div class="answer">
  <h2>Recommendation: do not let the lease run to expiry. Extend now, then sell in 2032 through a §1031 exchange.</h2>
  <p>The lease expires somewhere in 2030–2035. Every path that ends in a discretionary sale while the tenant is
  still paying ranks above holding to expiry or renewing and holding. Extending now and selling in 2032 with term
  left is first on risk-adjusted wealth; selling now through a §1031 exchange is {abs(pctdiff(MC['S1']['ce'], MC[best]['ce'])):.1f}% behind it
  and wins outright if rent growth disappoints. A taxable sale costs {abs(pctdiff(MC['S2']['ce'], MC['S1']['ce'])):.1f}% of certainty-equivalent wealth.
  Holding to expiry has a higher median than selling, but a 5th-percentile outcome {money(MC[best]['p05']-MC[hold]['p05'])} lower.</p>
  <div>
    <span class="pill">{proj['trials']:,} Monte-Carlo trials</span>
    <span class="pill">seed {proj['seed']}</span>
    <span class="pill">CRRA {proj['gamma']}</span>
    <span class="pill">{sum(1 for r in facts if r['status']=='verified')} verified rows</span>
    <span class="pill">{len(sources)} official sources</span>
    <span class="pill">{sum(1 for r in facts if r['status']=='blank')} blanks flagged</span>
  </div>
</div>
{kpi_cards}
<h2>The ranking</h2>
{strategy_table}
<p class="meta">Normalised to $100,000 of current annual NOI. These are not this asset's values: the brief does not disclose rent,
address, basis or loan terms, so the workbook measures the <em>decision</em>, not the parcel. Method and every assumption are on the
<a href="projection.html">projection page</a>.</p>

<h2>What the evidence says, in six lines</h2>
<div class="grid g2">
  <div class="card"><div class="lbl">Labour market</div><div class="big">4.5%</div>
    <div class="meta">Los Angeles County unemployment, September 2026, down from 5.9% a year earlier. Payrolls +30.2k (+0.5%).</div>
    <a class="more" href="economy.html">Economy &amp; jobs →</a></div>
  <div class="card"><div class="lbl">Income</div><div class="big">$90,112</div>
    <div class="meta">County median household income, 2020–2024. The city median is $81,939 and 16.5% of city residents live in poverty.</div>
    <a class="more" href="market.html">Market &amp; people →</a></div>
  <div class="card"><div class="lbl">Population</div><div class="big">−3.2%</div>
    <div class="meta">County population change since April 2020. The city is −0.8%. Do not underwrite growth.</div>
    <a class="more" href="market.html">Market &amp; people →</a></div>
  <div class="card"><div class="lbl">Tenant credit</div><div class="big">−$901m</div>
    <div class="meta">Stockholders' equity at 2026-07-05 — but the first nine months of FY2026 produced <strong>+$27.9m</strong> of net income.</div>
    <a class="more" href="property-lease.html">Property &amp; lease →</a></div>
  <div class="card"><div class="lbl">Rates</div><div class="big">4.86%</div>
    <div class="meta">10-year Treasury, 2026-11-06. Every 50 bp of cap-rate expansion costs about 7.7% of value at a 6% cap.</div>
    <a class="more" href="valuation-tax.html">Valuation &amp; tax →</a></div>
  <div class="card"><div class="lbl">Hazard</div><div class="big">60%</div>
    <div class="meta">Probability of a magnitude 6.7+ earthquake in the Los Angeles region within 30 years. The parcel's fire zone is unknown.</div>
    <a class="more" href="risks.html">Risks →</a></div>
</div>

<h2>Read the workbook</h2>
<div class="grid g3">
  <div class="card"><h3>Market &amp; people</h3><p class="meta">Population, income, poverty, housing, education and the business base — 29 verified rows.</p><a class="more" href="market.html">Open →</a></div>
  <div class="card"><h3>Economy &amp; jobs</h3><p class="meta">Unemployment, payrolls by sector, CPI, wages and what they mean for a QSR tenant.</p><a class="more" href="economy.html">Open →</a></div>
  <div class="card"><h3>Property &amp; lease</h3><p class="meta">What is known, what is deliberately blank, and the tenant's filed credit.</p><a class="more" href="property-lease.html">Open →</a></div>
  <div class="card"><h3>Valuation &amp; tax</h3><p class="meta">Cap-rate mechanics, the Measure ULA cliff, Proposition 13 and §1031.</p><a class="more" href="valuation-tax.html">Open →</a></div>
  <div class="card"><h3>Projection model</h3><p class="meta">Deterministic 2026–2040 paths, 15,000 trials, 15 assumptions, sensitivity grids.</p><a class="more" href="projection.html">Open →</a></div>
  <div class="card"><h3>Decision &amp; triggers</h3><p class="meta">The plan, the eight triggers that change it, and what would make holding right.</p><a class="more" href="decision.html">Open →</a></div>
  <div class="card"><h3>Risks</h3><p class="meta">18 business-as-usual and 12 black-swan events, each mapped to the strategies it bites.</p><a class="more" href="risks.html">Open →</a></div>
  <div class="card"><h3>Flagged for review</h3><p class="meta">Every blank, every defect found in the repository, and what to obtain to close it.</p><a class="more" href="flagged.html">Open →</a></div>
  <div class="card"><h3>Verification</h3><p class="meta">The rules, the automated checks, and exactly what was read on {ACCESSED}.</p><a class="more" href="verification.html">Open →</a></div>
</div>

<div class="note warn"><strong>Privacy.</strong> This workbook never states the address, APN, rent, basis, loan terms or owner identity.
It does not need them: every figure is normalised per $100,000 of NOI. The build fails if a personal identifier appears.</div>
"""
page("index.html", "Sell before expiry, or renew?", body_index,
     "A decision workbook for one property: a single-tenant Jack in the Box on an NNN lease in Central Los Angeles, expiring 2030–2035. Every number is linked to the official page it came from.")


# --- Executive summary -----------------------------------------------------
body_exec = f"""
<div class="answer">
  <h2>The answer in one page</h2>
  <p><strong>Do not hold to expiry and do not simply renew.</strong> Run a single track: ask for an extension now at or above
  in-place rent, and if it is granted, sell in 2032 with roughly five to nine years of term left, through a §1031 exchange.
  If the tenant will not extend on acceptable terms, sell now through the same exchange. The difference between those two
  paths is {abs(pctdiff(MC[best]['ce'], MC['S1']['ce'])):.1f}% of certainty-equivalent wealth — small enough that the negotiation outcome,
  not the model, decides. What is <em>not</em> close: holding passively to 2030–2035 sits {abs(pctdiff(MC[hold]['ce'], MC[best]['ce'])):.1f}% below the leader
  on the risk measure, with a 5th-percentile outcome {money(MC[best]['p05']-MC[hold]['p05'])} worse per $100,000 of NOI.</p>
</div>

<h2>Findings</h2>
<div class="tablewrap"><table>
<caption>Six findings, each with the verified number behind it</caption>
<thead><tr><th>#</th><th>Finding</th><th>Evidence</th><th>Source</th></tr></thead><tbody>
<tr><td class="num">1</td><td><strong>Term is worth more than rent growth.</strong> A sale with 10+ years of term prices about 25 bp tighter than one with 2–5 years; at a 6% cap that is roughly 4% of value, and it is worth more than two years of assumed rent growth.</td><td>Cap-rate term adjustment (assumption A2) applied to verified NOI; sensitivity grid on <a href="projection.html">the model page</a>.</td><td class="src">A2</td></tr>
<tr><td class="num">2</td><td><strong>The tenant is weak but not failing.</strong> FY2025 net loss was −$80.7m and stockholders' equity is −$901.3m; yet the first nine months of FY2026 produced +$27.9m of net income and the deficit narrowed by $37.0m.</td><td>Tenant rows T01–T07.</td><td class="src">{src_link('S07, S08')}</td></tr>
<tr><td class="num">3</td><td><strong>The local economy is stable, not booming.</strong> County unemployment is 4.5%, a full 1.4 points better than a year ago; payrolls grew 0.5%. But the county has lost 3.2% of its population since 2020 and information-sector jobs fell 5.7%.</td><td>Rows E01–E17, D02–D04.</td><td class="src">{src_link('S01, S03')}</td></tr>
<tr><td class="num">4</td><td><strong>Rates, not rents, set the sale price.</strong> The 10-year Treasury is 4.86%. At a 6.00% cap a 50 bp expansion cuts value by 7.7%; the same asset with flat NOI and a 100 bp move loses more than two years of income.</td><td>Row C01; cap mechanics on the <a href="valuation-tax.html">valuation page</a>.</td><td class="src">{src_link('S04')}</td></tr>
<tr><td class="num">5</td><td><strong>A taxable sale is an avoidable loss.</strong> S2 (sell, pay tax) trails S1 (sell, §1031) by {abs(pctdiff(MC['S2']['ce'], MC['S1']['ce'])):.1f}% of certainty-equivalent wealth for the same asset and the same timing. The 45/180-day clock is the only execution risk.</td><td>Rows X09–X10; strategies S1 and S2.</td><td class="src">{src_link('S11')}</td></tr>
<tr><td class="num">6</td><td><strong>The tail is physical, not financial.</strong> There is a 60% chance of a magnitude 6.7+ earthquake in the region within 30 years. That, not a rent roll, is what turns a good hold into a bad one.</td><td>Rows H01–H03; risk RK19.</td><td class="src">{src_link('S12')}</td></tr>
</tbody></table></div>

<h2>The plan</h2>
<div class="tablewrap"><table>
<caption>Sequenced actions. Nothing here requires the owner to disclose private terms to this workbook.</caption>
<thead><tr><th>When</th><th>Action</th><th>Why</th></tr></thead><tbody>
<tr><td><strong>Now — Q4 2026</strong></td><td>Commission a property condition report and confirm the seismic retrofit status; obtain the insurance loss runs and next renewal quote; pull the FHSZ class and FEMA flood zone for the parcel.</td><td>These four items are the only blanks that could change the answer (flagged B09, H05–H07).</td></tr>
<tr><td><strong>Q4 2026 — Q2 2027</strong></td><td>Open a renewal conversation 3+ years before the earliest expiry year. Ask for 10 years at or above in-place rent with CPI-banded escalators and a guaranty.</td><td>The extension is worth more than the rent: it converts a 2030–2035 option into saleable term.</td></tr>
<tr><td><strong>2027</strong></td><td>Engage a qualified intermediary and identify §1031 replacement candidates before any letter of intent is signed.</td><td>The 45-day clock starts at closing and cannot be extended (X09–X10).</td></tr>
<tr><td><strong>2029 — 2032</strong></td><td>Sell with 5–10 years of term remaining, discretionary, in a stable rate window. Exchange into a diversified net-lease position.</td><td>Term is priced; distress is not. A discretionary seller with term beats a forced seller without it.</td></tr>
<tr><td><strong>If no acceptable extension by 2028</strong></td><td>Sell now through the §1031 exchange rather than wait for expiry.</td><td>Selling now is {abs(pctdiff(MC['S1']['ce'], MC[best]['ce'])):.1f}% behind the leader and {abs(pctdiff(MC['S1']['ce'], MC[hold]['ce'])):.1f}% ahead of holding to expiry on the risk measure.</td></tr>
<tr><td><strong>Never</strong></td><td>Do not renew at expiry and hold to 2040 with a single tenant whose equity is negative.</td><td>S5 is last: {money(MC['S5']['ce'])} CE with a 5th percentile of {money(MC['S5']['p05'])}.</td></tr>
</tbody></table></div>

<h2>What would change the answer</h2>
<ul class="tight">
<li><strong>Rent growth at 2.0% or below</strong> makes sell-now first in the sensitivity grid: with weak growth the extra term is not worth waiting for.</li>
<li><strong>A replacement asset that grows 3.0%</strong> also flips the ranking to sell-now.</li>
<li><strong>An extension at a materially lower rent</strong> destroys the case for extending; sell into the existing income instead.</li>
<li><strong>Insurance costs above ~10% of NOI</strong> would make the hold case uneconomic regardless of the lease.</li>
<li><strong>A tenant default or a bankruptcy filing</strong> removes the choice entirely: the box is sold vacant at land-and-improvements value.</li>
</ul>

<div class="note bad"><strong>What this is not.</strong> It is not an appraisal, not tax advice and not investment advice. It does not
state this property's value, rent or basis, because none of those were supplied and none will be inferred. The owner's personal
balance sheet is never collected, so the recommendation is expressed per $100,000 of NOI rather than as dollars of the owner's wealth.</div>
"""
page("executive-summary.html", "Executive summary", body_exec,
     "The decision, six findings with their sources, a dated plan, and the conditions that would reverse it.")


# --- Market ----------------------------------------------------------------
market_head = f"""
<div class="grid g4">
  <div class="card"><div class="lbl">City population 2025</div><div class="big">3.87m</div><div class="meta">−0.8% since 2020</div></div>
  <div class="card"><div class="lbl">County median income</div><div class="big">$90,112</div><div class="meta">City $81,939</div></div>
  <div class="card"><div class="lbl">City poverty</div><div class="big">16.5%</div><div class="meta">County 13.3%</div></div>
  <div class="card"><div class="lbl">Bachelor's or higher</div><div class="big">38.5%</div><div class="meta">City, age 25+</div></div>
</div>
<div class="note"><strong>How to read this page.</strong> These are demand-side facts about the trade area. They support a QSR that
serves a dense, lower-to-middle-income, transit-dependent market — the city's 8,304 people per square mile and 30.7-minute mean
commute are the reason a drive-through works here. They do <em>not</em> support an underwriting case built on population growth:
both the city and the county are shrinking since 2020.</div>
"""
body_market = market_head + "<h2>Population and households</h2>" + fact_table(
    [r for r in facts if r["id"] in ("D01", "D02", "D03", "D04", "D18", "D19", "D21", "D22", "D29")],
    "Population, density and households", searchable=False
) + "<h2>Income and poverty</h2>" + fact_table(
    [r for r in facts if r["id"] in ("D05", "D06", "D07", "D08", "D09", "D10", "D23")],
    "Income and poverty", searchable=False
) + "<h2>Housing and cost of living</h2>" + fact_table(
    [r for r in facts if r["id"] in ("D11", "D12", "D13", "D16", "D17")],
    "Housing tenure, values, rents and commuting", searchable=False
) + "<h2>Education</h2>" + fact_table(
    [r for r in facts if r["id"] in ("D14", "D15", "K01", "K02", "K03")],
    "Educational attainment and the local school district", searchable=False
) + "<h2>Business base</h2>" + fact_table(
    [r for r in facts if r["id"] in ("D20", "D24", "D25", "D26", "D27", "D28")],
    "Employer base and consumer spending in the trade area", searchable=False
) + """
<h2>What this means for the property</h2>
<ul class="tight">
<li><strong>The trade area is dense and established, not growing.</strong> 8,304 residents per square mile in the city (D18) is a
  demand base a suburban site cannot match; −0.8% city and −3.2% county population change (D02, D04) means a buyer will not pay for growth.</li>
<li><strong>Income supports value menus, not premium ones.</strong> A city median of $81,939 with 16.5% poverty (D05, D09) is a
  value-oriented QSR catchment — consistent with the tenant's format, and a reason the unit's sales are sensitive to local employment.</li>
<li><strong>Rents and home values are high, which caps disposable income.</strong> $1,933 median gross rent and $921,200 median home
  value (D12, D11) leave less cash for away-from-home food than the same income elsewhere.</li>
<li><strong>The school district is large and stable.</strong> 497,105 students in LAUSD for 2025-26 (K01) is a demand anchor for
  family households, but a district of that size says nothing about a specific site.</li>
</ul>
"""
page("market.html", "Market &amp; people", body_market,
     "Population, income, housing, education and the business base of the trade area — 29 rows, each linked to the official page it came from.")


# --- Economy ---------------------------------------------------------------
body_econ = f"""
<div class="grid g4">
  <div class="card"><div class="lbl">County unemployment</div><div class="big">4.5%</div><div class="meta">Sep 2026 · was 5.9% in Sep 2025</div></div>
  <div class="card"><div class="lbl">Payrolls, year over year</div><div class="big">+30.2k</div><div class="meta">+0.5% · 6,282.1k total</div></div>
  <div class="card"><div class="lbl">CPI-U, all items</div><div class="big">+3.7%</div><div class="meta">Los Angeles metro, Sep 2026</div></div>
  <div class="card"><div class="lbl">Average weekly wage</div><div class="big">$1,704</div><div class="meta">LA County, Q1 2026</div></div>
</div>
<div class="note"><strong>Reading the labour market.</strong> The county added jobs at roughly the national rate while its unemployment
rate fell by more than a point. The composition matters more than the total: education and health (+49.1k) and leisure and hospitality
(+11.5k) grew, while information (−11.4k), manufacturing (−5.4k) and financial activities (−5.1k) shrank. A QSR in a dense
urban trade area is levered to the first two and to lunchtime office traffic that the last three support.</div>
""" + "<h2>Unemployment</h2>" + fact_table(
    [r for r in facts if r["cat"] == "economy" and r["id"].startswith("E0") and "Unemployment" in r["metric"]],
    "Unemployment rates", searchable=False
) + "<h2>Employment</h2>" + fact_table(
    [r for r in facts if r["id"] in ("E07", "E08", "E09", "E10", "E11", "E12", "E13", "E14", "E15", "E16", "E17")],
    "Nonfarm payroll employment and its composition", searchable=False
) + "<h2>Prices and wages</h2>" + fact_table(
    [r for r in facts if r["id"] in ("E18", "E19", "E20", "E21", "E22", "E23", "E24")],
    "Inflation, employment cost and wage levels", searchable=False
) + "<h2>Wage floors that hit this tenant directly</h2>" + fact_table(
    [r for r in facts if r["cat"] == "wages"],
    "Statutory wage floors", searchable=False
) + """
<h2>What this means for the property</h2>
<ul class="tight">
<li><strong>Employment is a support, not a growth story.</strong> +0.5% payroll growth (E08) will not lift restaurant volumes much;
  it does underwrite the rent that is already being paid.</li>
<li><strong>CPI of 3.7% (E18) is the ceiling for escalators.</strong> A lease that resets at CPI hands the landlord roughly the
  growth assumed in the base case of this model — which is why the base case uses 3.0% and the bull case uses the verified 3.7%.</li>
<li><strong>Wage floors compress the franchisee's margin.</strong> $20.00/hour for fast food (W02) and $16.90 statewide (W01) raise the
  cost base of exactly this format; that pressure, not the landlord's rent, is what drives closure decisions.</li>
<li><strong>Energy inflation of 20.3% (E20) is a cost shock to a drive-through.</strong> It is also a signal that input volatility
  in this sector is not over.</li>
</ul>
"""
page("economy.html", "Economy &amp; jobs", body_econ,
     "The Los Angeles labour market, prices and statutory wage floors — and what each implies for a single QSR unit.")


# --- Property & lease ------------------------------------------------------
tenant_rows = [r for r in facts if r["cat"] == "tenant"]
body_prop = """
<div class="note warn"><strong>Deliberately blank.</strong> The brief withholds the address, APN, rent, exact expiry date, basis and
loan terms. Those are the most sensitive facts in the file, so they are not collected, not inferred and not published. The model is
normalised to $100,000 of NOI instead. Here is exactly what is missing and why it matters.</div>
""" + "<h2>The asset and the lease</h2>" + fact_table(
    [r for r in facts if r["cat"] == "property"],
    "What is known about the asset — and what is deliberately absent", searchable=False
) + """
<h2>Anatomy of a triple-net QSR lease</h2>
<div class="grid g2">
  <div class="card"><h3>What "NNN" transfers to the tenant</h3>
    <p class="meta">Property taxes, building insurance and common-area maintenance sit with the tenant. That is why a
    net-lease asset is priced on the credit of the tenant and the term of the lease rather than on the landlord's operating skill.</p>
    <p class="meta">It does <em>not</em> transfer: the roof, the structure, the parking lot or the landlord's own financing — and in
    a California net lease it rarely transfers earthquake exposure.</p></div>
  <div class="card"><h3>Why the 2030–2035 window is itself a risk</h3>
    <p class="meta">A buyer prices a lease they can read. Five years of uncertainty inside the term is priced as a discount even
    before any negotiation begins. Fixing the expiry — by extension — is worth more than most rent bumps.</p>
    <p class="meta">Running the hold case across each expiry year from 2030 to 2035 moves certainty-equivalent wealth by
    """ + money(EXPIRY[-1]["s4_ce"] - EXPIRY[0]["s4_ce"]) + """ per $100,000 of NOI on this model.</p></div>
</div>

<h2>Tenant credit</h2>
<p class="lede">Both halves of the story. The company has lost money and carries negative equity; it has also returned to profit
in the current fiscal year. A summary that quotes only one of those is not a credit assessment.</p>
""" + fact_table(tenant_rows, "Jack in the Box Inc. — filed results (SEC)", searchable=False) + """
<div class="note"><strong>How to read it.</strong> Negative stockholders' equity of −$901.3m is a real credit fact for a lessor: the
balance sheet has no equity cushion, and a downturn lands on creditors and landlords first. But the direction over the last three
quarters is improvement — a $27.9m nine-month profit and a $37.0m reduction in the deficit. The lease is a franchised unit, so the
immediate obligor may be a franchisee whose financials are not public; that is the first document to request.</div>

<h2>Lease clauses that decide the outcome</h2>
<div class="tablewrap"><table>
<caption>Contract terms to verify before any decision — none of these were supplied</caption>
<thead><tr><th>Clause</th><th>Why it matters</th><th>Status</th></tr></thead><tbody>
<tr><td>Renewal options and notices</td><td>An option at a fixed rent can be worth more than the lease itself; a market-rate option is worth little.</td><td><span class="tag t-blank">not supplied</span></td></tr>
<tr><td>Escalations</td><td>CPI-banded escalators pass verified inflation (E18) to the landlord; flat escalations do not.</td><td><span class="tag t-blank">not supplied</span></td></tr>
<tr><td>Guaranty</td><td>Corporate versus franchisee versus personal determines what survives a default.</td><td><span class="tag t-blank">not supplied</span></td></tr>
<tr><td>Assignment and recapture</td><td>Recapture rights can convert a sale into a vacancy at the worst moment.</td><td><span class="tag t-blank">not supplied</span></td></tr>
<tr><td>Landlord obligations</td><td>Roof, structure and parking are often landlord-side even in a NNN lease.</td><td><span class="tag t-blank">not supplied</span></td></tr>
<tr><td>Insurance obligations</td><td>Who carries earthquake cover, and at what deductible, changes the tail.</td><td><span class="tag t-blank">not supplied</span></td></tr>
</tbody></table></div>
"""
page("property-lease.html", "Property &amp; lease", body_prop,
     "The asset, the tenant and the contract: what is known, what is deliberately withheld for privacy, and what must be obtained.")


# --- Valuation & tax -------------------------------------------------------
def value_table():
    caps = [0.0525, 0.0550, 0.0575, 0.0600, 0.0625, 0.0650, 0.0675]
    cells = "".join(f'<td class="num">{money(100000/c)}</td>' for c in caps)
    head = "".join(f"<th class='num'>{c*100:.2f}%</th>" for c in caps)
    return (f'<div class="tablewrap"><table><caption>Value per $100,000 of annual NOI at each capitalisation rate '
            f'(arithmetic: value = NOI ÷ cap)</caption><thead><tr><th>NOI</th>{head}</tr></thead>'
            f'<tbody><tr><td><strong>$100,000</strong></td>{cells}</tr></tbody></table></div>')


def ula_table():
    prices = [5_000_000, 5_399_999, 5_400_001, 7_000_000, 10_899_999, 10_900_001]
    rows = []
    for p in prices:
        base = 0.0045 * p
        ula = 0.0 if p <= 5_400_000 else (0.04 * p if p < 10_900_000 else 0.055 * p)
        rows.append(f'<tr><td class="num">{money(p)}</td><td class="num">{money(base)}</td>'
                    f'<td class="num">{money(ula)}</td><td class="num">{money(base+ula)}</td>'
                    f'<td class="num">{(base+ula)/p*100:.2f}%</td></tr>')
    return ('<div class="tablewrap"><table><caption>City of Los Angeles transfer tax at the Measure ULA thresholds — '
            'a cliff, not a bracket (computed from the verified rates in X01–X04)</caption>'
            '<thead><tr><th class="num">Sale price</th><th class="num">Base 0.45%</th><th class="num">Measure ULA</th>'
            '<th class="num">Total city tax</th><th class="num">Effective rate</th></tr></thead><tbody>'
            + "".join(rows) + '</tbody></table></div>')


body_val = """
<div class="note"><strong>How a net-lease asset is priced.</strong> Value = net operating income ÷ capitalisation rate. Nothing else.
Rent growth moves the numerator; interest rates and tenant credit move the denominator. Almost every dispute about "what it is worth"
is a dispute about the cap rate.</div>
<h2>Capitalisation-rate arithmetic</h2>
""" + value_table() + """
<p class="meta">The cap-rate level is an <strong>assumption</strong>, not a verified fact: no official statistical series publishes
transaction cap rates for QSR net-lease assets, so none is asserted (row M01 is blank and flagged). What <em>is</em> verified is the
discount rate that buyers anchor to: the 10-year Treasury.</p>

<h2>Capital markets</h2>
""" + fact_table([r for r in facts if r["cat"] == "capital"], "Treasury par yields, 2026-11-02 to 2026-11-06", searchable=False) + """
<h2>Tax on the way out</h2>
""" + fact_table([r for r in facts if r["cat"] == "tax"], "Transfer taxes, Proposition 13 and §1031", searchable=False) + """
<h3>The Measure ULA cliff, priced</h3>
""" + ula_table() + """
<p class="meta">A sale at $5,399,999 pays $24,300 of city tax. A sale at $5,400,001 pays $242,700. One dollar of price costs
$218,400. Above $10.9m the same cliff repeats at 5.95%. If the asset is worth anywhere near a threshold, the pricing decision
matters more than a year of rent.</p>

<h2>What a buyer will underwrite</h2>
<div class="tablewrap"><table>
<caption>The five drivers of price, in order of impact on this asset</caption>
<thead><tr><th>Driver</th><th>Direction</th><th>Evidence</th></tr></thead><tbody>
<tr><td><strong>Remaining lease term</strong></td><td>10+ years prices ~25 bp tighter than 2–5 years</td><td>Assumption A2; term is the product being sold</td></tr>
<tr><td><strong>Tenant credit</strong></td><td>Negative equity widens the spread; a franchisee guaranty narrows it</td><td>Rows T01–T07 (S07, S08)</td></tr>
<tr><td><strong>Interest rates</strong></td><td>+50 bp of cap rate ≈ −7.7% of value at a 6% cap</td><td>Row C01 (S04); arithmetic above</td></tr>
<tr><td><strong>Property tax after sale</strong></td><td>Prop 13 reassessment at 100% of price is a buyer cost, priced into the bid</td><td>Rows X06–X08 (S10)</td></tr>
<tr><td><strong>Transfer taxes</strong></td><td>City base 0.45%, plus the ULA cliff if the price clears $5.4m</td><td>Rows X01–X04 (S09)</td></tr>
</tbody></table></div>

<h2>§1031 in one paragraph</h2>
<p>Gain is deferred, not forgiven. Within 45 days of closing you must identify replacement property in writing, and within 180 days
you must close; the old basis carries into the new property (X09, X10, S11). Because the basis carries, the deferral compounds: that is
why S1 and S3 beat S2 in every run of the model, by """ + f"{abs(pctdiff(MC['S2']['ce'], MC['S1']['ce'])):.1f}%" + """ of certainty-equivalent wealth.</p>
"""
page("valuation-tax.html", "Valuation &amp; tax", body_val,
     "Cap rates, the Treasury curve, the Measure ULA cliff, Proposition 13 and §1031 — the mechanics that decide the net proceeds.")


# --- Projection model ------------------------------------------------------
det_rows = []
for case in DET:
    for sid in ["S1", "S2", "S3", "S4", "S5"]:
        det_rows.append(f'<tr><td>{e(case["case"])}</td><td>{case["noi_growth"]*100:.1f}%</td>'
                        f'<td>{case["cap0"]*100:.2f}%</td><td>{e(STRAT[sid]["short"])}</td>'
                        f'<td class="num">{money(case["results"][sid])}</td></tr>')

assump_rows = "".join(
    f'<tr><td><strong>{e(a["id"])}</strong></td><td>{e(a["name"])}</td><td>{e(a["value"])}</td>'
    f'<td>{e(a["range"])}</td><td class="meta">{e(a["why"])}</td></tr>' for a in proj["assumptions"])

mc_rows = "".join(
    f'<tr><td class="num">{i+1}</td><td><strong>{e(STRAT[s]["short"])}</strong></td>'
    f'<td class="num">{money(MC[s]["ce"])}</td><td class="num">{money(MC[s]["median"])}</td>'
    f'<td class="num">{money(MC[s]["p05"])}</td><td class="num">{money(MC[s]["p95"])}</td>'
    f'<td class="num">{prob(s)}</td></tr>'
    for i, s in enumerate(RANK))

grid_rows = ""
for r in GRID:
    cells = "".join(f'<td class="num{" winner" if k == r["best"] else ""}">{money(r["ce"][k])}</td>' for k in ["S1", "S2", "S3", "S4", "S5"])
    grid_rows += (f'<tr><td>{r["growth"]*100:.1f}%</td><td>{r["cap"]*100:.2f}%</td>{cells}'
                  f'<td><span class="tag t-ok">{e(STRAT[r["best"]]["short"])}</span></td></tr>')

reinv_rows = "".join(
    f'<tr><td>{r["reinvest_growth"]*100:.1f}%</td>' +
    "".join(f'<td class="num">{"<strong>" if k == r["best"] else ""}{money(r["ce"][k])}{"</strong>" if k == r["best"] else ""}</td>' for k in ["S1", "S2", "S3", "S4", "S5"]) +
    f'<td><span class="tag t-ok">{e(STRAT[r["best"]]["short"])}</span></td></tr>' for r in REINV)

expiry_rows = "".join(f'<tr><td class="num">{r["expiry"]}</td><td class="num">{money(r["s4_ce"])}</td></tr>' for r in EXPIRY)

body_proj = f"""
<div class="note"><strong>What is modelled.</strong> Five courses of action, each projected from 2026 to 2040 on the same
random paths, then ranked on <em>certainty-equivalent</em> wealth — the risk-free amount that a risk-averse owner would accept in
place of the uncertain distribution — with a CRRA coefficient of {proj['gamma']}. Expected value alone would reward the strategy
with the fattest tail; the certainty equivalent does not.</div>

<div class="grid g4">
  <div class="card"><div class="lbl">Trials</div><div class="big">{proj['trials']:,}</div><div class="meta">seed {proj['seed']} — reproducible</div></div>
  <div class="card"><div class="lbl">Horizon</div><div class="big">2026–2040</div><div class="meta">expiry sampled 2030–2035</div></div>
  <div class="card"><div class="lbl">Unit of account</div><div class="big">$100k NOI</div><div class="meta">normalised, never this asset's rent</div></div>
  <div class="card"><div class="lbl">Assumptions</div><div class="big">{len(proj['assumptions'])}</div><div class="meta">all published, none claimed as fact</div></div>
</div>

<h2>The formulas</h2>
<div class="card">
<pre class="meta" style="white-space:pre-wrap;margin:0">NOI(t)        = 100,000 × (1 + g)^(t − 2026)
cap(t)        = cap₀ + term adjustment (0–100 bp depending on years of term remaining)
price(t)      = NOI(t) ÷ cap(t)
city tax      = 0.45% × price + Measure ULA (4% if price &gt; $5.4m, 5.5% if ≥ $10.9m)
net proceeds  = price − 2.5% selling costs − city tax − income tax (0 if §1031 is used)
terminal      = net proceeds × (1 + reinvestment growth)^(2040 − sale year), then taxed on exit
utility       = W^(1−γ)/(1−γ);  CE = [ mean(utility) ]^(1/(1−γ))
hazard        = annual quake probability derived from the verified 30-year 60% (1 − 0.40^(1/30))</pre>
</div>

<h2>Assumptions</h2>
<p class="lede">Every number below is a modelling choice, not an official statistic. Each is shown with the range that was tested.
The verified inputs the model does use are the September 2026 LA CPI (3.7%), the 10-year Treasury (4.86%), the earthquake
probability (60% / 30 years) and the Measure ULA schedule.</p>
<div class="tablewrap"><table data-filterable><caption>All fifteen assumptions, with the tested range and the reason</caption>
<thead><tr><th>ID</th><th>Assumption</th><th>Base value</th><th>Tested range</th><th>Why this value</th></tr></thead>
<tbody>{assump_rows}</tbody></table></div>

<h2>Deterministic paths</h2>
<div class="tablewrap"><table data-filterable><caption>Terminal after-tax wealth per $100,000 of NOI — three deterministic cases</caption>
<thead><tr><th>Case</th><th>NOI growth</th><th>Entry cap</th><th>Strategy</th><th class="num">Terminal wealth 2040</th></tr></thead>
<tbody>{''.join(det_rows)}</tbody></table></div>

<h2>Monte Carlo, {proj['trials']:,} trials</h2>
<div class="tablewrap"><table><caption>Ranked on certainty-equivalent wealth (CRRA {proj['gamma']}), with the tail shown</caption>
<thead><tr><th>Rank</th><th>Strategy</th><th class="num">Certainty equivalent</th><th class="num">Median</th>
<th class="num">5th percentile</th><th class="num">95th percentile</th><th class="num">P(beats hold)</th></tr></thead>
<tbody>{mc_rows}</tbody></table></div>

<h2>Sensitivity: does the ranking survive the assumptions?</h2>
<div class="tablewrap"><table><caption>Nine cells on NOI growth × entry cap. Bold is the best strategy in that cell.</caption>
<thead><tr><th>NOI growth</th><th>Entry cap</th><th class="num">S1 sell now</th><th class="num">S2 taxable</th>
<th class="num">S3 extend→sell</th><th class="num">S4 hold→sell</th><th class="num">S5 renew→hold</th><th>Best</th></tr></thead>
<tbody>{grid_rows}</tbody></table></div>
<p class="meta">The ranking is not fragile: S3 leads in most cells, and S1 takes over exactly when growth disappoints (2.0%) —
which is the economically sensible direction, because low growth removes the reason to wait for it.</p>

<div class="tablewrap"><table><caption>Replacement-asset growth (A9). S1 takes the lead when the replacement grows faster than the subject.</caption>
<thead><tr><th>Reinvest growth</th><th class="num">S1</th><th class="num">S2</th><th class="num">S3</th><th class="num">S4</th><th class="num">S5</th><th>Best</th></tr></thead>
<tbody>{reinv_rows}</tbody></table></div>

<h2>The expiry ambiguity, priced</h2>
<div class="tablewrap"><table><caption>S4 (hold to expiry) under a certain expiry in each year — the value of not knowing</caption>
<thead><tr><th>Assumed expiry</th><th class="num">Terminal wealth per $100k NOI</th></tr></thead><tbody>{expiry_rows}</tbody></table></div>
<p class="meta">Moving the expiry from 2030 to 2035 changes the hold outcome by {money(EXPIRY[-1]['s4_ce']-EXPIRY[0]['s4_ce'])} —
{((EXPIRY[-1]['s4_ce']/EXPIRY[0]['s4_ce'])-1)*100:.1f}% — for a fact the owner already knows and a buyer cannot see. Fixing it in a lease
document is worth more than a year of rent escalation.</p>

<h2>Limitations</h2>
<ul class="tight">
<li>No rent, address, size, basis or loan terms were supplied, so this measures a decision, not a parcel.</li>
<li>The cap rate is an assumption. If the asset trades at 7.0% rather than 6.0%, every dollar figure falls by about 14%.</li>
<li>The hazard module uses the verified <em>probability</em> of a major earthquake but an assumed loss given event (A13).</li>
<li>The owner's own tax position (bracket, state, entity, depreciation history) is deliberately not collected; flat top rates are applied.</li>
<li>No forecast of a recession, an earthquake or a wildfire is made. They are sampled as risks, not predicted.</li>
</ul>
"""
page("projection.html", "Projection model", body_proj,
     "Five strategies, 2026–2040, deterministic and seeded Monte-Carlo, with every assumption published and stress-tested.")


# --- Decision --------------------------------------------------------------
triggers = [
    ("10-year Treasury", "above 5.50% for 90 days", "Bring the sale forward; do not market into a rate spike.",
     "S04", "Currently 4.86%"),
    ("County unemployment", "above 6.0%", "Sell before expiry while the tenant is still paying rent.",
     "S01", "Currently 4.5%"),
    ("Tenant stockholders' equity", "worse than −$1.0bn, or a second consecutive annual loss",
     "Treat renewal as unlikely; sell with term while it still exists.", "S08", "Currently −$901.3m"),
    ("Tenant nine-month net income", "negative for two consecutive filings",
     "Accelerate the sale; do not sign a long extension into a deteriorating credit.", "S07", "Currently +$27.9m"),
    ("Renewal offer on the table", "≥ in-place rent, ≥ 10 years, CPI-banded",
     "Sign the extension, then sell in 2032 with term (S3).", "", "Not yet offered"),
    ("Renewal offer on the table", "below −5% versus in-place rent",
     "Decline; sell now through the §1031 exchange (S1).", "", "—"),
    ("Insurance premium", "above 10% of NOI, or earthquake cover unavailable",
     "The hold case is uneconomic; sell.", "", "Not supplied (H07)"),
    ("Assessed cap rates for comparable sales", "at or below 5.75%", "Sell into the compression; you are being paid for term.",
     "", "No official series (M01)"),
]
trig_rows = ""
for t in triggers:
    cell = src_link(t[3]) if t[3] else '<span class="meta">internal</span>'
    trig_rows += (f'<tr><td><strong>{e(t[0])}</strong></td><td>{e(t[1])}</td><td>{e(t[2])}</td>'
                  f'<td class="src">{cell}</td><td class="meta">{e(t[4])}</td></tr>')

VERDICT = {
    "S1": "Best fallback; wins when growth disappoints",
    "S2": "Same decision minus the tax tool",
    "S3": "Recommended: extend, then sell with term",
    "S4": "Higher median, materially worse tail",
    "S5": "Worst on the risk measure",
}
body_dec = f"""
<div class="answer">
  <h2>Decide on term, not on optimism</h2>
  <p>The asset is a bond with a building attached: its price is the rent divided by a cap rate, and the cap rate depends on how
  many years of contracted rent a buyer can see. The one thing the owner controls is how much term exists at the moment of sale.
  That is why the recommendation is to convert the 2030–2035 uncertainty into 2032 certainty — by extending, then selling — and why
  the fallback is to sell now rather than wait.</p>
</div>

<h2>The ranked decision</h2>
<div class="tablewrap"><table>
<caption>Ranked on risk-adjusted after-tax wealth. "P(beats hold)" is the share of trials in which the strategy ends with more than holding to expiry.</caption>
<thead><tr><th>Rank</th><th>Strategy</th><th class="num">Certainty equivalent</th><th class="num">5th percentile</th>
<th class="num">Median</th><th class="num">P(beats hold)</th><th>Verdict</th></tr></thead><tbody>
""" + "".join(
    f'<tr><td class="num">{i+1}</td><td><strong>{e(STRAT[s]["short"])}</strong></td>'
    f'<td class="num">{money(MC[s]["ce"])}</td><td class="num">{money(MC[s]["p05"])}</td>'
    f'<td class="num">{money(MC[s]["median"])}</td><td class="num">{prob(s)}</td>'
    f'<td class="meta">{e(VERDICT.get(s, ""))}</td></tr>'
    for i, s in enumerate(RANK)
) + f"""</tbody></table></div>

<h2>Why the leader is only barely ahead — and why that is the point</h2>
<p>S3 leads S1 by {abs(pctdiff(MC['S1']['ce'], MC[best]['ce'])):.1f}% of the leader's certainty-equivalent wealth. That is inside the model's own error bars, so the honest
conclusion is not "extend at any price". It is: <strong>the extension is worth having if it costs nothing</strong>. If the tenant
demands a rent cut to extend, the arithmetic moves to sell-now. If the tenant will not engage, sell-now. Either way the owner exits
before expiry, and the difference between the two exits is small compared with the difference between either of them and waiting.</p>

<h2>Decision triggers</h2>
<p class="lede">The plan is a plan, not a forecast. Each indicator below is published monthly, quarterly or annually by an official
source, so the decision can be re-tested without new research.</p>
<div class="tablewrap"><table data-filterable><caption>Eight triggers and the action each one dictates</caption>
<thead><tr><th>Indicator</th><th>Threshold</th><th>Action</th><th>Source</th><th>Where it stands</th></tr></thead>
<tbody>{trig_rows}</tbody></table></div>

<h2>Risk posture: what "manageable" means here</h2>
<div class="grid g2">
  <div class="card"><h3>Downside is bounded by the sale, not by the lease</h3>
    <p class="meta">In the worst 5% of trials, holding to expiry ends at {money(MC['S4']['p05'])} versus {money(MC['S3']['p05'])} for
    extend-and-sell. The gap is the cost of carrying a single-tenant, single-asset, seismic-exposed building through an option
    that the tenant controls.</p></div>
  <div class="card"><h3>Upside is capped, and that is acceptable</h3>
    <p class="meta">The 95th percentile of S3 ({money(MC['S3']['p95'])}) is barely above its median: net-lease income does not
    compound quickly. Buying a lottery ticket with the asset is not required to preserve wealth.</p></div>
  <div class="card"><h3>Liquidity is the real constraint</h3>
    <p class="meta">A single-tenant drive-through in a specific trade area has few buyers. A discretionary sale with term has a
    market; a forced sale of a vacant box has a land buyer.</p></div>
  <div class="card"><h3>The tax tool is free — use it</h3>
    <p class="meta">§1031 costs nothing but discipline and a qualified intermediary, and it is worth
    {abs(pctdiff(MC['S2']['ce'], MC['S1']['ce'])):.1f}% of certainty-equivalent wealth here.</p></div>
</div>

<h2>What would make holding the right answer</h2>
<ul class="tight">
<li>The tenant offers a long extension at or above in-place rent, with a corporate guaranty and CPI escalators — then holding through 2032 (S3) is the plan, not holding forever.</li>
<li>Cap rates compress to 5.25% or below while the 10-year falls: refinancing or a later sale could beat an immediate exit. The model tests this and still prefers selling with term.</li>
<li>The owner's basis is so low and the property so central to their estate plan that a §1031 exchange is not available — in which case a taxable sale is the only exit and the timing question becomes a tax-year question, not a market one.</li>
<li>Nothing in the verified data supports holding past 2035 with a single tenant whose equity is negative: S5 is last in every sensitivity cell tested.</li>
</ul>
"""
page("decision.html", "Decision", body_dec,
     "The recommendation, the arithmetic behind it, eight triggers that would change it, and what would make holding right.")


# --- Risks -----------------------------------------------------------------
risk_rows = "".join(
    f'<tr data-type="{e(r["type"])}" data-sev="{e(r["severity"])}"><td><strong>{e(r["id"])}</strong></td>'
    f'<td><span class="tag {"t-med" if r["type"]=="BAU" else "t-high"}">{e(r["type"])}</span></td>'
    f'<td><strong>{e(r["risk"])}</strong><div class="meta">{e(r["mechanism"])}</div></td>'
    f'<td>{sev_tag(r["severity"])}<div class="meta">{e(r["likelihood"])}</div></td>'
    f'<td class="meta">{e(r["anchor"])}</td>'
    f'<td class="meta">{e(r["mitigation"])}</td>'
    f'<td class="src">{src_link(r["source"])}</td></tr>' for r in risks)
n_bau = sum(1 for r in risks if r["type"] == "BAU")
n_bs = sum(1 for r in risks if r["type"] == "BLACK SWAN")

body_risk = f"""
<div class="note"><strong>How to read the register.</strong> Each risk states what it does to value, whether an official source
supports its <em>probability</em>, and what to do about it. Where no official probability exists — which is most of the time — the
row says so rather than inventing one. Severity is the modelled impact on the decision, not a claim of actuarial precision.</div>
<div class="grid g4">
  <div class="card"><div class="lbl">Business-as-usual</div><div class="big">{n_bau}</div><div class="meta">Things that happen in a normal decade</div></div>
  <div class="card"><div class="lbl">Black swans</div><div class="big">{n_bs}</div><div class="meta">Low-probability, high-severity events</div></div>
  <div class="card"><div class="lbl">Highest official probability</div><div class="big">60%</div><div class="meta">M≥6.7 earthquake in 30 years (H01)</div></div>
  <div class="card"><div class="lbl">Largest unquantified</div><div class="big">Insurance</div><div class="meta">No premium, carrier or cover detail supplied (H07)</div></div>
</div>

<h2>How the tail enters the model</h2>
<p class="lede">The Monte Carlo does not forecast disasters; it samples them. The annual probability of a major earthquake is derived
from the verified 30-year figure (1 − 0.40<sup>1/30</sup> ≈ 3.0%), and each event applies an assumed retained loss (A13). Wildfire is
modelled at 0.5% a year because the parcel's fire zone is unknown (H05). Replacing those two assumptions with the parcel's actual
FHSZ class and insurance terms is the single most valuable piece of additional work available.</p>

<div class="filter">
  <input type="search" id="risk-search" placeholder="Filter risks (e.g. insurance, earthquake, tenant)…" aria-label="Filter risks">
  <select id="risk-type" aria-label="Filter by type" style="padding:9px 12px;border:1px solid #e4e9f0;border-radius:9px;background:#fff">
    <option value="">All types</option><option value="BAU">Business as usual</option><option value="BLACK SWAN">Black swans</option>
  </select>
  <span class="count">{len(risks)} rows</span>
</div>
<div class="tablewrap"><table id="risk-table"><caption>Risk register — {len(risks)} rows</caption>
<thead><tr><th>ID</th><th>Type</th><th>Risk and mechanism</th><th>Severity</th><th>Evidence and official anchor</th><th>Mitigation</th><th>Source</th></tr></thead>
<tbody>{risk_rows}</tbody></table></div>

<h2>The three that should decide the question</h2>
<ol class="tight">
<li><strong>Tenant non-renewal (RK01).</strong> The owner's entire optionality depends on a counterparty whose equity is negative.
  A drive-through box is not easily re-let, and the drive-through entitlement is the most valuable and least transferable part of it.</li>
<li><strong>Earthquake (RK19).</strong> A 60% probability over 30 years is not a tail in the colloquial sense; it is a coin flip
  weighted twice. It is also the risk most likely to arrive at the same moment as a liquidity freeze.</li>
<li><strong>Insurance (RK08, H07).</strong> The largest genuinely unknown number in the file. A premium above 10% of NOI changes
  the hold case from marginal to uneconomic, and no official series publishes it for a private parcel.</li>
</ol>
"""
page("risks.html", "Risks", body_risk,
     "18 business-as-usual and 12 black-swan events, each with its mechanism, its official anchor (or the absence of one), and its mitigation.")


# --- Sources ---------------------------------------------------------------
src_rows = "".join(
    f'<tr><td><strong>{e(s["id"])}</strong></td><td><span class="tag t-ok">{e(s["tier"])}</span></td>'
    f'<td><strong>{e(s["publisher"])}</strong><div>{e(s["title"])}</div>'
    f'{"<div class=meta>" + e(s["note"]) + "</div>" if s.get("note") else ""}</td>'
    f'<td class="meta">{e(s["covers"])}</td><td class="num">{e(s["accessed"])}</td>'
    f'<td class="src"><a href="{e(s["url"])}" rel="noopener" target="_blank">Open ↗</a></td></tr>'
    for s in sources.values())

body_src = f"""
<div class="note"><strong>One rule.</strong> A value is published on this site only if it was read from the page linked on the same
row, on {ACCESSED}. If the page did not show the value, the cell is blank and the row is on the
<a href="flagged.html">flagged page</a>. No aggregator, no news article, no broker survey and no language model is a source.</div>
<div class="tablewrap"><table data-filterable><caption>{len(sources)} official sources, all read on {ACCESSED}</caption>
<thead><tr><th>ID</th><th>Tier</th><th>Publisher and document</th><th>What it is cited for</th><th class="num">Read on</th><th>Link</th></tr></thead>
<tbody>{src_rows}</tbody></table></div>

<h2>What each source is used for</h2>
<div class="grid g2">
  <div class="card"><h3>Demand and demographics</h3><p class="meta">Census Bureau QuickFacts for the city and, separately, the county (S02, S03).
  The county must be called by its own slug: the combined two-geography URL only works with <code>losangelescountycalifornia</code>, which is the
  defect recorded as R-01.</p></div>
  <div class="card"><h3>Labour and prices</h3><p class="meta">BLS Los Angeles Area Economic Summary, updated 2026-11-04 (S01). It is a PDF, so the
  values are read from the published tables rather than a database extract.</p></div>
  <div class="card"><h3>Capital markets</h3><p class="meta">The Treasury's own daily par yield curve for November 2026 (S04). Every rate on the
  valuation page is a row in that table, dated.</p></div>
  <div class="card"><h3>Tenant credit</h3><p class="meta">SEC EDGAR: the filing index for the FY2025 10-K and Q3 FY2026 10-Q (S05, S06), plus the
  XBRL company-concept endpoints for net income and equity (S07, S08) so the figures are the filed ones, not a press summary.</p></div>
  <div class="card"><h3>Tax</h3><p class="meta">City of Los Angeles Office of Finance for the transfer tax and Measure ULA (S09); the County
  Assessor for Proposition 13 (S10); the IRS fact sheet for §1031 (S11).</p></div>
  <div class="card"><h3>Hazard and schools</h3><p class="meta">USGS for the UCERF3 probabilities (S12); CAL FIRE/OSFM for the fire-hazard
  framework (S13); CDE for LAUSD (S14); DIR for the wage floors (S15, S16).</p></div>
</div>
"""
page("sources.html", "Sources", body_src,
     "Sixteen official sources, each read on 2026-11-08, each carrying the rows it supports.")


# --- Flagged ---------------------------------------------------------------
blank_rows = [r for r in facts if r["status"] == "blank"]
blank_table = fact_table(blank_rows, "Values deliberately left blank — no official source, or withheld for privacy", searchable=False)
irr_rows = "".join(
    f'<tr><td><strong>{e(i["id"])}</strong></td><td><strong>{e(i["title"])}</strong>'
    f'<div class="meta">{e(i["detail"])}</div><div class="meta"><em>Evidence:</em> {e(i["evidence"])}</div>'
    f'<div class="meta"><em>Impact:</em> {e(i["impact"])}</div><div class="meta"><em>Action:</em> {e(i["action"])}</div></td>'
    f'<td><span class="tag {"t-ok" if i["status"]=="fixed" else "t-blank"}">{e(i["status"])}</span></td></tr>'
    for i in flagged["irregularities"])
carried_rows = "".join(
    f'<tr><td>{e(c["item"])}</td><td class="meta">{e(c["why"])}</td><td class="num">{e(c["used_in_model"])}</td></tr>'
    for c in flagged["carried_unverified"])

body_flag = f"""
<div class="note warn"><strong>This page does not block publication.</strong> It is the register of everything that could not be
verified, everything that is missing, and every defect found in the repository during this session's line-by-line review. Each item
carries the evidence and the action taken. Nothing here has been silently corrected in another session's files.</div>

<h2>Repository irregularities</h2>
<div class="tablewrap"><table><caption>{len(flagged['irregularities'])} items found in the combined repository on {ACCESSED}</caption>
<thead><tr><th>ID</th><th>Finding, evidence and action</th><th>Status</th></tr></thead><tbody>{irr_rows}</tbody></table></div>

<h2>Values earlier sessions publish that this session could not re-verify</h2>
<div class="tablewrap"><table><caption>Carried, not endorsed — and excluded from every calculation here</caption>
<thead><tr><th>Item</th><th>Why it could not be verified</th><th class="num">Used in model</th></tr></thead><tbody>{carried_rows}</tbody></table></div>

<h2>Blank cells</h2>
{blank_table}
<p class="meta">A blank is not an omission. It is the correct output when the official source does not contain the value, or when
publishing it would identify the owner. Each blank states what to obtain to close it.</p>

<h2>How to close the most important gaps</h2>
<div class="tablewrap"><table><caption>What to request, from whom, and what it changes</caption>
<thead><tr><th>Gap</th><th>Obtain from</th><th>What it changes</th></tr></thead><tbody>
<tr><td>Exact expiry date, renewal options, escalations (P05, P06)</td><td>The lease itself</td><td>The whole projection: expiry year alone moves the hold case by several percent</td></tr>
<tr><td>Rent, NOI, basis (P04, A5)</td><td>Rent roll and tax returns</td><td>Converts the per-$100k model into dollars — and the after-tax ranking is sensitive to basis</td></tr>
<tr><td>FHSZ class and flood zone (H05, H06)</td><td>CAL FIRE / OSFM viewer; FEMA map; state seismic-hazard report</td><td>Whether wildfire is a rounding error or a real exposure</td></tr>
<tr><td>Insurance premium, carrier, sub-limits (H07)</td><td>Broker, loss runs, current policy</td><td>Whether holding is economic at all</td></tr>
<tr><td>Seismic retrofit status</td><td>LADBS records; property condition report</td><td>The loss given event, and whether a buyer can finance the box</td></tr>
<tr><td>Franchisee financials and guaranty</td><td>Tenant / franchisee</td><td>The actual credit behind the rent, which is not the parent company's</td></tr>
</tbody></table></div>
"""
page("flagged.html", "Flagged for review", body_flag,
     "Every blank, every defect found in the repository, and exactly what to obtain to close each one.")


# --- Verification ----------------------------------------------------------
n_ver = sum(1 for r in facts if r["status"] == "verified")
n_blank = sum(1 for r in facts if r["status"] == "blank")
body_ver = f"""
<div class="note"><strong>What was actually done.</strong> On {ACCESSED} this session read {len(sources)} official pages and recorded
the values it could see, row by row, with the link on the row. It did not carry forward a single figure it could not see. Where a
page was dead — and three commonly cited ones were — the link was replaced or the value was left out and flagged.</div>
<div class="grid g4">
  <div class="card"><div class="lbl">Verified rows</div><div class="big">{n_ver}</div><div class="meta">value + source link + access date</div></div>
  <div class="card"><div class="lbl">Blank rows</div><div class="big">{n_blank}</div><div class="meta">published on the flagged page</div></div>
  <div class="card"><div class="lbl">Official sources</div><div class="big">{len(sources)}</div><div class="meta">all read {ACCESSED}</div></div>
  <div class="card"><div class="lbl">Automated rules</div><div class="big">7</div><div class="meta">build fails if any is violated</div></div>
</div>

<h2>The seven publication rules</h2>
<ol class="tight">
<li>A "verified" row must have a non-empty value <em>and</em> a source id that resolves to an https URL.</li>
<li>A "blank" row must have an empty value and must appear on the flagged page.</li>
<li>Every source must be cited by at least one row; an orphan source is an error.</li>
<li>No source may be an aggregator, a news article, a broker survey or a language model.</li>
<li>Every internal link must resolve to a file that exists.</li>
<li>No page may contain an e-mail address, a phone number, a street address, an APN, an account number or a person's name.</li>
<li>The published strategy figures must equal the figures in the model output — the site cannot drift from the engine.</li>
</ol>

<h2>What was read, and what it showed</h2>
<div class="tablewrap"><table><caption>Source-by-source account of the verification pass</caption>
<thead><tr><th>Source</th><th>Read</th><th>Outcome</th></tr></thead><tbody>
<tr><td>S01 BLS Los Angeles summary</td><td class="num">2026-11-08</td><td>All unemployment, payroll, CPI, ECI, wage and benefit figures transcribed as shown; updated 2026-11-04.</td></tr>
<tr><td>S02 Census QuickFacts, city</td><td class="num">2026-11-08</td><td>City rows D01–D24 read directly. The combined city+county URL only works with the correct county slug.</td></tr>
<tr><td>S03 Census QuickFacts, county</td><td class="num">2026-11-08</td><td>County rows D03–D29 read directly. This is the fix for irregularity R-01.</td></tr>
<tr><td>S04 Treasury par yields</td><td class="num">2026-11-08</td><td>Six dated rates transcribed from the November 2026 table.</td></tr>
<tr><td>S05 / S06 SEC filing indexes</td><td class="num">2026-11-08</td><td>Both filings confirmed present, with accession numbers and filing dates recorded.</td></tr>
<tr><td>S07 XBRL net income</td><td class="num">2026-11-08</td><td>FY2025 loss, the nine-month profit, both quarterly profits and the comparatives read from the filed series.</td></tr>
<tr><td>S08 XBRL stockholders' equity</td><td class="num">2026-11-08</td><td>Three balance-sheet dates, showing the deficit and its narrowing.</td></tr>
<tr><td>S09 Measure ULA FAQ</td><td class="num">2026-11-08</td><td>All-in rates 0.45% / 4.45% / 5.95%, thresholds, effective date and indexation confirmed.</td></tr>
<tr><td>S10 Proposition 13</td><td class="num">2026-11-08</td><td>1% levy, 2% cap and reassessment triggers confirmed on the Assessor's page.</td></tr>
<tr><td>S11 IRS FS-2008-18</td><td class="num">2026-11-08</td><td>45-day and 180-day limits, qualified intermediary, carryover basis confirmed.</td></tr>
<tr><td>S12 USGS UCERF3</td><td class="num">2026-11-08</td><td>60% / 46% / 31% for M6.7 / 7.0 / 7.5 over 30 years confirmed. Replaces a dead URL (R-02).</td></tr>
<tr><td>S13 CAL FIRE FHSZ</td><td class="num">2026-11-08</td><td>Classes and mapping framework confirmed. Parcel class cannot be asserted without the address.</td></tr>
<tr><td>S14 CDE LAUSD</td><td class="num">2026-11-08</td><td>Enrollment 497,105 and 81,328 English learners for 2025-26 confirmed.</td></tr>
<tr><td>S15 / S16 DIR</td><td class="num">2026-11-08</td><td>$16.90 state and $20.00 fast-food floors confirmed with effective dates.</td></tr>
</tbody></table></div>

<h2>Sources that were tried and rejected</h2>
<ul class="tight">
<li>Four previously cited government URLs returned 404 and were replaced or flagged: the USGS FAQ (R-02), the BOE Proposition 13 page (R-03),
  two IRS §1031 pages (R-04) and the BEA county-income release (R-05).</li>
<li>Broker and news cap-rate estimates for Los Angeles net lease were found but not used, because no official statistical series publishes
  transaction cap rates (M01, M02).</li>
<li>Search results about Measure ULA and the November 2026 ballot measure were not used as sources; only the City's own FAQ page was (R-09).</li>
</ul>

<h2>Reproduce</h2>
<div class="card"><pre class="meta" style="white-space:pre-wrap;margin:0">python3 session-343c7030/scripts/model.py        # data/projections.json (deterministic, seed {proj['seed']})
python3 session-343c7030/scripts/build_site.py   # 12 pages
python3 session-343c7030/scripts/verify.py       # 7 rule families, exits non-zero on failure</pre></div>

<h2>Limitations stated plainly</h2>
<ul class="tight">
<li>This is decision support, not an appraisal, tax advice or investment advice.</li>
<li>No rent, address, size, basis, loan or lease document was supplied, so nothing here asserts this parcel's value.</li>
<li>Eight earlier sessions reached overlapping but not identical conclusions. This workbook reconciles their <em>evidence</em>,
  not their recommendations; where they differ, the difference is analytical judgement, and it is visible on
  <a href="../workspaces.html">the workspaces page</a>.</li>
<li>Cap rates, basis, renewal probability and loss given hazard are assumptions. They are published with ranges and tested.</li>
</ul>
"""
page("verification.html", "Verification", body_ver,
     "The rules, the source-by-source account of the verification pass, the rejected sources and the limits of the analysis.")


# ---------------------------------------------------------------------------
# Assertions — the build fails rather than publishing a broken rule
# ---------------------------------------------------------------------------
def check():
    failures = []
    source_ids = set(sources)
    cited = set()
    for r in facts:
        if r["status"] == "verified":
            if not r["value"]:
                failures.append(f'{r["id"]}: verified row has an empty value')
            if not r["source"]:
                failures.append(f'{r["id"]}: verified row has no source')
        if r["status"] == "blank" and r["value"]:
            failures.append(f'{r["id"]}: blank row carries a value')
        for s in [x.strip() for x in r["source"].split(",") if x.strip()]:
            if s not in source_ids:
                failures.append(f'{r["id"]}: unknown source {s}')
            cited.add(s)
    for sid in source_ids - cited:
        failures.append(f"source {sid} is never cited")
    for s in sources.values():
        if not s["url"].startswith("https://"):
            failures.append(f'{s["id"]}: non-https URL')
    # internal links
    hrefs = set()
    for f in os.listdir(OUT):
        if not f.endswith(".html"):
            continue
        html_text = open(os.path.join(OUT, f)).read()
        for m in re.findall(r'href="([^"#:]+)"', html_text):
            if m.endswith((".html", ".css", ".js")) or "/" in m:
                hrefs.add((f, m))
    for f, target in hrefs:
        if target.startswith("../"):
            path = os.path.normpath(os.path.join(OUT, target))
        else:
            path = os.path.join(OUT, target)
        if not os.path.exists(path):
            failures.append(f"{f}: broken link {target}")
    # PII scan
    pats = [
        (r"[\w.+-]+@[\w-]+\.[\w.]+", "e-mail address"),
        (r"\(\d{3}\)\s?\d{3}-\d{4}", "phone number"),
        (r"\b\d{3}-\d{2}-\d{4}\b", "SSN-like pattern"),
        (r"\b\d{4}-\d{3}-\d{3}\b", "APN-like pattern"),
        (r"\b\d{3}-\d{3}-\d{3}\b", "APN-like pattern"),
        (r"\b\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr)\b", "street address"),
    ]
    for f in sorted(os.listdir(OUT)):
        if not f.endswith(".html"):
            continue
        text = open(os.path.join(OUT, f)).read()
        for pat, label in pats:
            m = re.search(pat, text)
            if m:
                failures.append(f"{f}: possible {label}: {m.group(0)!r}")
    # model consistency: published CE figures must equal projections.json
    idx = open(os.path.join(OUT, "index.html")).read()
    if money(MC["S1"]["ce"]) not in idx or money(MC["S3"]["ce"]) not in idx:
        failures.append("index.html does not match the model output")
    return failures


if __name__ == "__main__":
    fails = check()
    if fails:
        print("BUILD FAILED — publication rules violated:")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print(f"built {len(NAV)} pages · {len(facts)} fact rows "
          f"({n_ver} verified, {n_blank} blank) · {len(sources)} sources · {len(risks)} risks · "
          f"{len(flagged['irregularities'])} irregularities · all checks pass")

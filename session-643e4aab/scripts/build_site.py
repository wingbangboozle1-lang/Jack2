#!/usr/bin/env python3
"""Static site builder for the session-643e4aab dashboard. Standard library only."""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = ROOT

SITE = "Central LA Jack in the Box (NNN) - Decision Workbook"
URL = "https://wingbangboozle1-lang.github.io/Jack2/session-643e4aab/"


def load(n):
    with open(os.path.join(DATA, n), encoding="utf-8") as f:
        return json.load(f)


SOURCES = load("sources.json")
SRC = {s["id"]: s for s in SOURCES["sources"]}
METRICS = load("metrics.json")
RISKS = load("risks.json")
PROJ = load("projections.json")
ACCESS = SOURCES["meta"]["accessed"]
e = html.escape

NAV = [
    ("index.html", "Overview"),
    ("executive-summary.html", "Executive summary"),
    ("property.html", "Property & lease"),
    ("market.html", "Market economics"),
    ("tenant.html", "Tenant"),
    ("hazards.html", "Hazards & insurance"),
    ("taxes.html", "Taxes & exit"),
    ("risks.html", "Risks"),
    ("projection.html", "Projection model"),
    ("verification.html", "Verification"),
    ("flagged.html", "Flagged for review"),
    ("sources.html", "Sources"),
]

CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#16181d;--muted:#5b6472;--line:#e2e6ec;--accent:#0b5cad;
--ok:#0f7b47;--warn:#a36100;--bad:#a11f34;--chip:#eef2f7;--computed:#4b3ca7}
@media(prefers-color-scheme:dark){:root{--bg:#0f1216;--card:#161b22;--ink:#e8edf3;--muted:#9aa6b5;
--line:#242c36;--accent:#69a9f0;--ok:#4fbf85;--warn:#e0a44a;--bad:#f0798c;--chip:#1d2530;--computed:#a99bf0}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
header{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:10}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
.brand{display:flex;align-items:center;gap:12px;padding:14px 0 10px}
.brand b{font-size:16px;letter-spacing:.2px}
.brand span{color:var(--muted);font-size:12.5px}
nav{display:flex;flex-wrap:wrap;gap:4px;padding-bottom:10px}
nav a{font-size:13px;color:var(--muted);text-decoration:none;padding:6px 10px;border-radius:7px;border:1px solid transparent}
nav a:hover{background:var(--chip);color:var(--ink)}
nav a.on{background:var(--accent);color:#fff;border-color:var(--accent)}
main{padding:26px 0 60px}
h1{font-size:27px;line-height:1.25;margin:0 0 6px}
h2{font-size:19px;margin:34px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--line)}
h3{font-size:15.5px;margin:22px 0 8px}
p{max-width:78ch}
.lede{color:var(--muted);font-size:15px;max-width:80ch}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:14px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin:14px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.kpi .k{font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.kpi .v{font-size:23px;font-weight:650;margin:6px 0 2px;font-variant-numeric:tabular-nums}
.kpi .s{font-size:12px;color:var(--muted)}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);
border-radius:10px;overflow:hidden;font-size:13.2px;margin:10px 0 6px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:var(--chip);font-size:11.5px;text-transform:uppercase;letter-spacing:.045em;color:var(--muted);font-weight:600;white-space:nowrap}
tr:last-child td{border-bottom:none}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
code,.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.4px}
.badge{display:inline-block;font-size:10.5px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;
padding:2px 7px;border-radius:20px;white-space:nowrap}
.b-verified{background:rgba(15,123,71,.12);color:var(--ok)}
.b-unverified{background:rgba(161,31,52,.12);color:var(--bad)}
.b-computed{background:rgba(75,60,167,.13);color:var(--computed)}
.b-given{background:rgba(163,97,0,.13);color:var(--warn)}
.blank{color:var(--muted);font-style:italic}
a.src{font-size:11.5px;color:var(--accent);text-decoration:none;border:1px solid var(--line);border-radius:5px;padding:1px 5px;white-space:nowrap}
a.src:hover{background:var(--chip)}
.note{font-size:12.6px;color:var(--muted);margin:4px 0 18px;max-width:88ch}
.callout{border-left:3px solid var(--accent);background:var(--card);border-radius:0 10px 10px 0;padding:12px 16px;margin:14px 0}
.callout.warn{border-left-color:var(--warn)}
.callout.bad{border-left-color:var(--bad)}
.callout.good{border-left-color:var(--ok)}
ul,ol{max-width:82ch}
li{margin:4px 0}
footer{border-top:1px solid var(--line);padding:22px 0 40px;color:var(--muted);font-size:12.4px}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.tabs{display:flex;gap:6px;flex-wrap:wrap;margin:12px 0}
.tabs a{font-size:12.5px;padding:5px 10px;border:1px solid var(--line);border-radius:20px;text-decoration:none;color:var(--muted)}
.tabs a:hover{background:var(--chip);color:var(--ink)}
.small{font-size:12px;color:var(--muted)}
"""


def page(slug, title, body, subtitle=""):
    nav = "".join(f'<a class="{"on" if f == slug else ""}" href="{f}">{e(t)}</a>' for f, t in NAV)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} - {e(SITE)}</title><meta name="description" content="{e(SITE)}, sourced and independently verified. Accessed {ACCESS}.">
<link rel="stylesheet" href="assets/style.css"></head><body>
<header><div class="wrap"><div class="brand"><b>{e(SITE)}</b>
<span>Source-verified workbook &middot; accessed {ACCESS} &middot; all figures normalised to $100,000 NOI</span></div>
<nav>{nav}</nav></div></header>
<main><div class="wrap">
<h1>{e(title)}</h1>
{f'<p class="lede">{subtitle}</p>' if subtitle else ''}
{body}
</div></main>
<footer><div class="wrap">
<p>Internal decision support for the property owner. Not an appraisal, not investment, legal or tax advice. No personal
information (name, street address, parcel number, loan number, account number or tax identifiers) is published here;
the subject is referred to only as the Subject Property. Every figure carries the official source it was read from on
{ACCESS}, or is left blank and listed on the Flagged for review page. See <a href="verification.html">Verification</a>.</p>
</div></footer></body></html>"""


def badge(status):
    cls = {"verified": "b-verified", "unverified": "b-unverified", "computed": "b-computed", "given": "b-given"}.get(status, "b-given")
    label = {"verified": "verified", "unverified": "unverified", "computed": "computed", "given": "stated in brief"}.get(status, status)
    return f'<span class="badge {cls}">{e(label)}</span>'


def src_link(sid):
    if not sid or sid not in SRC:
        return '<span class="blank">&mdash;</span>'
    s = SRC[sid]
    return f'<a class="src" href="{e(s["url"])}" title="{e(s["publisher"] + " - " + s["title"])}" target="_blank" rel="noopener">{e(sid)}&nbsp;&#8599;</a>'


def metric_rows(rows, show_note=True):
    out = ['<div class="scroll"><table><thead><tr><th>ID</th><th>Metric</th><th>Value</th><th>Period</th>'
           '<th>Geography</th><th>Status</th><th>Source</th></tr></thead><tbody>']
    for r in rows:
        val = e(r["value"]) if r["value"] else '<span class="blank">left blank</span>'
        note = f'<div class="small">{e(r["note"])}</div>' if (show_note and r.get("note")) else ""
        unit = f' <span class="small">{e(r["unit"])}</span>' if (r["value"] and r.get("unit")) else ""
        out.append(
            f'<tr><td class="mono">{e(r["id"])}</td><td>{e(r["metric"])}{note}</td>'
            f'<td><b>{val}</b>{unit}</td>'
            f'<td>{e(r.get("period",""))}</td><td>{e(r.get("geography",""))}</td>'
            f'<td>{badge(r["status"])}</td><td>{src_link(r.get("source",""))}</td></tr>')
    out.append("</tbody></table></div>")
    return "".join(out)


def money(x):
    try:
        return f"${x:,.0f}"
    except (TypeError, ValueError):
        return "-"


def pct(x):
    try:
        return f"{x:+.2f}%"
    except (TypeError, ValueError):
        return "-"


# ------------------------------------------------------------------ pages
def pg_index():
    b = PROJ["base_case"]
    mc = PROJ["monte_carlo"]
    mcm = PROJ["meta"]["monte_carlo"]
    counts = {"verified": 0, "unverified": 0, "computed": 0, "given": 0}
    for r in METRICS["rows"]:
        counts[r["status"]] += 1
    body = f"""
<div class="callout"><b>Short answer.</b> The rent is the asset, and the lease is what the rent is worth.
Financially, holding to expiry wins in {mc['win_rate_pct']['HOLD_TO_EXPIRY']}% of {PROJ['meta']['monte_carlo']['trials']:,} simulated futures, but only
because the model assumes the tenant renews at market. The decision that actually controls the outcome is
<b>whether the owner has a long, priced term to sell</b> - not whether the corner is gentrifying.
Do not hold passively to expiry. Either sign a long extension now and sell into it, or run a 1031 sale
while at least five years of term remain. <a href="executive-summary.html">Read the executive summary &rarr;</a></div>

<div class="grid">
<div class="kpi"><div class="k">Value today (per $100k NOI, 6.25% cap)</div><div class="v">{money(b['price_today'])}</div>
<div class="s">Cap-rate band 4.50%-7.25% &rarr; {money(100000/0.0725)} to {money(100000/0.045)}</div></div>
<div class="kpi"><div class="k">Best modelled outcome, 2040</div><div class="v">{money(b['strategies'][b['ranking'][0]])}</div>
<div class="s">{b['ranking'][0].replace('_',' ').title()} &middot; spread across strategies {b['spread_pct']}%</div></div>
<div class="kpi"><div class="k">Tenant equity</div><div class="v">-$901M</div>
<div class="s">FY2025 net loss $80.7M, but FY2026 nine months <b>+$27.9M</b> {src_link('S18')}</div></div>
<div class="kpi"><div class="k">Facts verified</div><div class="v">{counts['verified']}</div>
<div class="s">of {len(METRICS['rows'])} rows; {counts['unverified']} left blank and flagged</div></div>
</div>

<h2>What decides this, in order</h2>
<div class="scroll"><table>
<thead><tr><th>Rank</th><th>Driver</th><th>Evidence</th><th>Why it dominates</th></tr></thead><tbody>
<tr><td class="num">1</td><td><b>Remaining lease term</b></td><td>{badge('unverified')}</td>
<td>The exact expiry is not in the brief or the documents provided (a 2030-2035 window). A buyer prices term, not
neighbourhood optimism. Every other variable moves value by single-digit percentages; term moves it by double digits.</td></tr>
<tr><td class="num">2</td><td><b>Rent versus market at the reset</b></td><td>{badge('computed')}</td>
<td>The model needs only a {pct(b['breakeven_uplift_vs_best_exit_pct'])} reset to beat the best exit. That is a low bar, and it
is the one number the owner can negotiate rather than forecast.</td></tr>
<tr><td class="num">3</td><td><b>Cap rate / interest rates</b></td><td>{src_link('S05')}</td>
<td>10-year Treasury 4.84% (5 Nov 2026). A 100 bp cap move is roughly a 14% value move at a 6-7% cap - larger than any rent growth
the owner can realistically negotiate in the same period.</td></tr>
<tr><td class="num">4</td><td><b>Tenant renewal behaviour and credit</b></td><td>{src_link('S17')}{src_link('S18')}</td>
<td>Equity is negative (-$901.3M) but improving, and FY2026 is profitable. A tenant that renews at market makes holding work;
one that closes the unit does not.</td></tr>
<tr><td class="num">5</td><td><b>Local demand fundamentals</b></td><td>{src_link('S01')}{src_link('S04')}</td>
<td>Real, but slow-moving: unemployment has fallen to 4.5% in the city, leisure and hospitality is adding jobs, while office-using
sectors shrink and the county's official population projection declines 2.2% by 2040. This is a support, not a catalyst.</td></tr>
</tbody></table></div>

<h2>The four decisions, on one clock</h2>
<p class="note">Each strategy is valued in nominal 2040 dollars per $100,000 of current NOI. Both the subject and any
replacement asset are held as property: growing rent, reinvested cash, and a sale at the horizon net of costs and tax.
A tactical note on method is in <a href="verification.html">Verification</a> (item V18) - the first version of this model
compared holding against cash invested at a flat yield, which mechanically favoured holding, and it was discarded.</p>
<div class="scroll"><table><thead><tr><th>Strategy</th><th>What it means</th><th class="num">2040 value / $100k NOI</th><th>Simulated win rate</th><th class="num">5th percentile</th></tr></thead><tbody>
""" + "".join(
        f'<tr><td><b>{k.replace("_"," ").title()}</b></td><td>{desc}</td><td class="num">{money(b["strategies"][k])}</td>'
        f'<td>{mc["win_rate_pct"][k]}%</td><td class="num">{money(mc["results"][k]["p05"])}</td></tr>'
        for k, desc in [
            ("HOLD_TO_EXPIRY", "Keep the asset, renew at the reset (or re-let after a vacancy), sell in 2040."),
            ("SELL_1031_NOW", "Sell now into a Section 1031 exchange; defer the gain, buy a replacement asset."),
            ("EXTEND_THEN_SELL", "Negotiate a market reset and a long term now, then sell in 2028 with the term intact."),
            ("SELL_TAXABLE_NOW", "Sell now, pay the tax, redeploy what is left."),
        ]) + f"""</tbody></table></div>

<h2>Where to look</h2>
<div class="tabs">
<a href="property.html">What is known and unknown about the asset</a>
<a href="market.html">The verified economic data</a>
<a href="tenant.html">The tenant's filed financials</a>
<a href="taxes.html">Exit costs and the ULA threshold</a>
<a href="risks.html">28 risks, decision by decision</a>
<a href="projection.html">Every assumption and every formula</a>
<a href="flagged.html">The {counts['unverified']} blanks you need to fill</a>
</div>
<div class="callout warn"><b>Read the flagged page before acting.</b> {counts['unverified']} values could not be confirmed
from an official source - starting with the actual rent, the exact expiry date, the parcel's hazard classification and the
owner's cost basis. They are deliberately blank rather than estimated. Each one states exactly which document closes it.</div>
"""
    return page("index.html", "Sell the lease, or keep the rent?", body,
                "A source-verified decision workbook for a single-tenant Jack in the Box on a triple-net lease in Central Los Angeles, expiry window 2030-2035.")


def pg_exec():
    b = PROJ["base_case"]
    mc = PROJ["monte_carlo"]
    body = f"""
<p class="lede">For the owner. Six things you need, in the order they matter.</p>

<h2>1. The recommendation</h2>
<div class="callout good"><p><b>Do not drift to expiry. Control the term, then decide.</b>
Open a renewal conversation now around a market reset and a longer term. Run a sale process in parallel, priced on
a 1031 exchange. Sell if the achievable price implies a cap rate at or below
<b>{b['breakeven_replacement_cap_pct']:.2f}%</b> - the point at which the replacement asset you could buy stops beating
holding. If the achievable cap rate is above that, keep the asset and take the reset.</p></div>
<p>This is not a hedge, it is a sequence: the extension conversation is the same conversation as the sale, because
both are priced off the same thing - remaining term. Signing a long extension <i>raises</i> the sale price; it does not
foreclose the sale.</p>

<h2>2. Why the financial answer looks like "hold"</h2>
<p>On the model, holding to expiry produces {money(b['strategies']['HOLD_TO_EXPIRY'])} per $100k of NOI by 2040 against
{money(b['strategies']['SELL_1031_NOW'])} for a 1031 sale today - a gap of
{money(b['strategies']['HOLD_TO_EXPIRY']-b['strategies']['SELL_1031_NOW'])}. Across
{PROJ['meta']['monte_carlo']['trials']:,} draws over cap rates, rent growth, renewal probability and the expiry year, holding wins
{mc['win_rate_pct']['HOLD_TO_EXPIRY']}% of the time. A taxable sale never wins: it gives up
{money(b['price_today']-b['net_if_taxable'])} of value on day one between costs and tax, and the model shows the deferral
is what makes an exit competitive at all.</p>
<p><b>That result rests on one assumption the model cannot verify:</b> that the tenant renews at market. If it does not,
the same model gives the re-let path {money(b['hold_relet_path'])}, and the advantage shrinks. The tenant's own stated
renewal practice is on the flagged list precisely because it is the highest-leverage sentence in the 10-K and could not
be re-read this session.</p>

<h2>3. The two reasons to sell anyway</h2>
<div class="scroll"><table><thead><tr><th>Reason</th><th>The evidence</th><th>What it costs you to ignore</th></tr></thead><tbody>
<tr><td><b>Concentration</b></td><td>One tenant, one parcel, one metro, one building. {src_link('S18')}</td>
<td>The cash-flow model values a diversified asset and a single asset the same way. They are not the same risk. A
1031 into several properties or a DST removes that, and the deferral makes the diversification close to free.</td></tr>
<tr><td><b>Tail risk you cannot model</b></td><td>60% chance of an M6.7+ quake in the LA region within 30 years {src_link('S24')};
16,251 structures lost and a $1bn FAIR Plan assessment from the January 2025 fires {src_link('S25')}{src_link('S26')}</td>
<td>A single uninsured or under-insured event can exceed years of rent. Insurance market withdrawal after a shock is what
makes an otherwise good asset unsellable - and it is exactly when you would want to sell.</td></tr>
</tbody></table></div>

<h2>4. What the local economy actually says</h2>
<p>Better than the headline reputation, and not strong enough to change the decision:</p>
<ul>
<li><b>Labour market has tightened.</b> City unemployment was 4.5% in September 2026, down from 5.9% a year earlier, and
now below the state's 5.1% and only half a point above the national 4.0%. {src_link('S01')}</li>
<li><b>The job mix is shifting, not shrinking.</b> Education and health added 49.1k jobs and leisure/hospitality added 11.5k;
information lost 11.4k and professional services lost 5.2k. A lunch-driven office location is the exposure; an all-day
residential catchment is not. {src_link('S01')}</li>
<li><b>Population is projected to decline.</b> The state's official projection has Los Angeles County falling from
{int(PROJ['meta']['population_projection']['2025']):,} in 2025 to {int(PROJ['meta']['population_projection']['2040']):,} in 2040,
a {abs(PROJ['meta']['population_projection']['change_2025_to_2040_pct'])}% decline. This is a real headwind for unit volume and it is
the single best argument against a 15-year lock-in at flat rent. {src_link('S04')}</li>
<li><b>Income and demand are high in absolute terms</b> - county personal income of $818.5bn is the largest of any US county -
but the city median household income ($81,939) trails the county ($90,112), and 16.5% of city residents are in poverty.
A value QSR fits that profile; a premium repositioning does not. {src_link('S03')}{src_link('S20')}</li>
</ul>

<h2>5. Your actual next 90 days</h2>
<ol>
<li><b>Pull the lease and amendments.</b> Exact expiry, every renewal option, the notice dates, the escalation formula, the
percentage-rent clause, the maintenance allocation (roof, structure, parking lot) and the casualty clause. Six of the
25 blank rows close with this one document.</li>
<li><b>Price the parcel's hazards.</b> City of LA fire hazard severity zone, FEMA flood panel, a seismic screening and a
current insurance quote. Three blank rows close with the address; the fourth needs a broker.</li>
<li><b>Get a broker opinion of value and an appraisal.</b> The workbook cannot state a cap rate because no official
source publishes one. This is the input that turns every scenario table on this site into a decision.</li>
<li><b>Ask the tenant for unit-level sales and their renewal intention.</b> A tenant that shares sales is signalling it
wants the site. A refusal is also information.</li>
<li><b>Line up a qualified intermediary before any listing.</b> The 45-day identification and 180-day receipt deadlines are
hard; missing them makes the sale taxable. {src_link('S12')}</li>
<li><b>Do not list until the appraisal and a replacement pipeline exist.</b> Selling into a search, with a clock running,
is how owners convert a good asset into a bad exchange.</li>
</ol>

<h2>6. What this workbook refuses to do</h2>
<ul>
<li>It will not tell you the property's value. Rent, basis, debt and the exact expiry were never provided.</li>
<li>It will not tell you your tax liability. Your marginal rates and depreciation history are withheld for privacy; the
tax mechanics are modelled with stated assumptions so you can substitute your own numbers.</li>
<li>It will not quote a cap rate as fact. No official source publishes one, so the model runs a band and says so.</li>
<li>It will not publish a street address, parcel number or any personal identifier. The site is built to fail if one appears.</li>
</ul>
<p><a href="flagged.html">The complete list of what is missing, and which document closes each gap &rarr;</a></p>
"""
    return page("executive-summary.html", "Executive summary", body,
                "The answer, the reasoning, the two reasons to sell anyway, and what to do in the next 90 days.")


def pg_property():
    rows = [r for r in METRICS["rows"] if r["category"] == "Property and lease"]
    body = f"""
<p class="lede">What is known about the asset, what is stated in the brief, and - deliberately - what is blank.</p>

<div class="callout warn"><b>Privacy by design.</b> The street address, assessor parcel number, legal description, owner
identity, loan terms and tax identifiers are not in this repository and are not on this site. The subject is referred to
only as the Subject Property. The build fails if an address-like or parcel-like string appears anywhere in the output.</div>

<h2>What the brief states</h2>
<div class="scroll"><table><thead><tr><th>Item</th><th>Stated value</th></tr></thead><tbody>
<tr><td>Asset</td><td>Single-tenant quick-service restaurant, Jack in the Box brand</td></tr>
<tr><td>Lease structure</td><td>Triple net (NNN)</td></tr>
<tr><td>Submarket</td><td>Central Los Angeles (parcel withheld)</td></tr>
<tr><td>Expiry window</td><td>2030-2035 <span class="small">(a five-year window, not a date)</span></td></tr>
<tr><td>Decision on the table</td><td>Sell before expiry, or renew</td></tr>
</tbody></table></div>

<h2>The lease register</h2>
{metric_rows(rows)}

<h2>Why "2030-2035" is itself a finding</h2>
<p>A buyer prices <i>term</i>. Two assets with identical rent, one with nine years remaining and one with four, do not trade
at the same cap rate - the shorter one carries re-leasing risk, downtime and re-fitting capital. A five-year uncertainty
band around the expiry therefore cannot be treated as a rounding error: it is the difference between selling a bond and
selling a vacancy risk.</p>
<p>It runs the other way too. If the tenant holds renewal options, the tenant decides whether the lease continues, not the
owner. The owner's "renew or sell" framing assumes a choice the owner may not have. The first question for the lease is
not "when does it end" but <b>"who controls what happens when it ends"</b>.</p>
"""
    return page("property.html", "Property and lease", body,
                "The asset register: what the brief states, what the documents must confirm, and what stays blank.")


def pg_market():
    cats = ["Capital markets", "Population", "Income", "Employment", "Wages and prices", "Labor regulation",
            "Consumer demand", "Education"]
    blocks = []
    for c in cats:
        rows = [r for r in METRICS["rows"] if r["category"] == c]
        if rows:
            blocks.append(f"<h3>{e(c)} <span class='small'>({len(rows)} rows)</span></h3>" + metric_rows(rows))
    body = f"""
<p class="lede">Every figure below was read from the official source on {ACCESS}. Where an agency publishes no value,
the cell is blank rather than estimated.</p>

<div class="callout"><b>Two things to notice before the tables.</b> First, the labour market in the city has genuinely
improved: unemployment is 4.5% and below the state average, and the metro is adding jobs faster than the nation. Second,
the mix is shifting away from office employment and the state's own projection has the county losing population through 2040.
Those two facts point in opposite directions, which is why this is a term-and-rent decision rather than a location bet.</div>

<div class="grid">
<div class="kpi"><div class="k">City unemployment, Sep 2026</div><div class="v">4.5%</div><div class="s">State 5.1%, US 4.0% {src_link('S01')}</div></div>
<div class="kpi"><div class="k">Metro jobs, 12-month change</div><div class="v">+30.2k</div><div class="s">+0.5%, ahead of the US +0.3% {src_link('S01')}</div></div>
<div class="kpi"><div class="k">County population, 2040 projection</div><div class="v">{int(PROJ['meta']['population_projection']['2040']):,}</div><div class="s">{PROJ['meta']['population_projection']['change_2025_to_2040_pct']}% vs 2025 {src_link('S04')}</div></div>
<div class="kpi"><div class="k">LA CPI-U, 12-month</div><div class="v">+3.7%</div><div class="s">The rate a CPI escalator would track {src_link('S01')}</div></div>
</div>

<h2>The verified series</h2>
{''.join(blocks)}

<h2>What is deliberately not projected</h2>
<p>No official agency publishes a projection of <i>employment</i>, <i>household income</i>, <i>rent</i> or <i>cap rates</i>
for a single parcel or submarket. Population is projected by the state; that is the projection used. Everything else in the
model is a declared assumption with a published sensitivity band, because a fabricated growth rate would look like data.
Note also that the Bureau of Economic Analysis discontinued metropolitan-area statistics with its 2024 county release
{src_link('S20')}, so any metro-level income projection would have to come from somewhere other than the federal statistical system.</p>
"""
    return page("market.html", "Market economics", body,
                "Population, income, employment, wages, labour regulation, demand and schools - verified against official sources.")


def pg_tenant():
    rows = [r for r in METRICS["rows"] if r["category"] == "Tenant"]
    body = f"""
<p class="lede">The tenant's own filings with the Securities and Exchange Commission. This is the only part of the analysis
where the counterparty's financial statements are a matter of public record.</p>

<div class="grid">
<div class="kpi"><div class="k">FY2025 revenue</div><div class="v">$1.465bn</div><div class="s">Down 6.7% from $1.571bn in FY2024 {src_link('S16')}</div></div>
<div class="kpi"><div class="k">FY2025 net income</div><div class="v">-$80.7M</div><div class="s">A loss {src_link('S17')}</div></div>
<div class="kpi"><div class="k">FY2026, nine months</div><div class="v">+$27.9M</div><div class="s">Back in profit {src_link('S17')}</div></div>
<div class="kpi"><div class="k">Stockholders' equity</div><div class="v">-$901.3M</div><div class="s">Improving from -$938.3M {src_link('S18')}</div></div>
</div>

{metric_rows(rows)}

<h2>How to read the credit</h2>
<p>Negative stockholders' equity is a capital-structure condition, not an imminent default signal - the company has been
profitable in fiscal 2026 to date, has reduced long-term debt from $1.603bn to $1.492bn, and is generating positive
annual revenue of roughly $1.2bn on a nine-month run rate. The correct reading for a landlord is that the tenant can pay
this rent, but that the tenant is a rational operator managing its own store portfolio, and this particular unit will
survive on its own economics.</p>

<div class="callout warn"><b>What is missing here matters more than what is present.</b> The unit count, the average unit volume
and the company's own statement about its renewal practice are all blank rows. Those figures sit in the narrative sections of
the 10-K rather than in the machine-readable financial data, and this session did not re-read that narrative. They are left
blank rather than carried over from another session's work, and they are the first thing to pull from the filing.</div>
"""
    return page("tenant.html", "Tenant", body,
                "The tenant's SEC-filed financials, with the narrative disclosures that still need to be read.")



def pg_hazards():
    rows = [r for r in METRICS["rows"] if r["category"] == "Hazard"]
    body = f"""
<p class="lede">The brief asks for black-swan events - the ones that could destroy the local economy. This is the page for
them. Earthquake and wildfire are the two that matter in Los Angeles, and they are not modelled as "a bad year": they are
the events that can remove the building, the tenant, or the insurance market.</p>

<div class="grid">
<div class="kpi"><div class="k">M6.7+ earthquake, LA region, 30 yrs</div><div class="v">60%</div><div class="s">USGS UCERF3 {src_link('S24')}</div></div>
<div class="kpi"><div class="k">Structures lost, Jan 2025 fires</div><div class="v">16,251</div><div class="s">Eaton 9,414 + Palisades 6,837 {src_link('S25')}</div></div>
<div class="kpi"><div class="k">Lost economic output, Jan 2025 fires</div><div class="v">$5.2-10.1bn</div><div class="s">County estimate {src_link('S25')}</div></div>
<div class="kpi"><div class="k">FAIR Plan assessment</div><div class="v">$1bn</div><div class="s">First in over 30 years {src_link('S26')}</div></div>
</div>

<h2>Earthquake</h2>
<p>The USGS Uniform California Earthquake Rupture Forecast puts the Los Angeles region at a 60% probability of an
magnitude 6.7 or greater earthquake within 30 years, 46% for magnitude 7.0 and 31% for magnitude 7.5 {src_link('S24')}.
Those are 30-year figures; over the roughly four to nine years remaining on this lease, the probability is proportionally
lower but not small. The exposure is not uniform across buildings - it depends on construction, age, soil and retrofit
status, none of which were provided for this parcel.</p>
<div class="callout bad"><b>The thing that actually hurts.</b> Earthquake insurance typically carries a percentage deductible
(commonly 10-15% of the limit). On a building where the deductible is 15% of a $1.3m structure, the deductible alone is about
$200,000 of uninsured loss before a single dollar of coverage responds. In an NNN lease the tenant may carry the policy, but
the owner still owns the uninsured gap and the re-leasing problem after the event. Confirm the deductible before extending.</div>

<h2>Wildfire</h2>
<p>The January 2025 Eaton and Palisades fires burned 37,469 acres, destroyed 16,251 structures, damaged 2,047 more and
killed 31 people. The County estimated $5.2-10.1bn of lost economic output, $2.2-4.2bn of lost labour income,
$900m-1.6bn of lost tax revenue, and about 6,800 businesses impacted {src_link('S25')}. Neither fire reached the Central
Los Angeles commercial corridor, but the second-order effects were regional and immediate: the insurance market repriced,
and the FAIR Plan needed a $1bn assessment from its member insurers - the first such assessment in over 30 years
{src_link('S26')}.</p>
<div class="callout warn"><b>The parcel's fire hazard class is genuinely unknown.</b> CAL FIRE maps State Responsibility
Areas; a densely built Los Angeles commercial parcel is a <i>Local</i> Responsibility Area, and the Office of the State Fire
Marshal states plainly that Local Responsibility Area zones are adopted by the local jurisdiction {src_link('S27')}. So the
answer for this parcel comes from the City of Los Angeles, by address, and the address is withheld here by policy. The row is
blank rather than guessed.</div>

<h2>Flood and seismic site conditions</h2>
<p>The parcel's FEMA flood zone requires the effective Flood Insurance Rate Map panel for the address {src_link('S28')};
liquefaction and fault-rupture zones require a geotechnical screening by parcel. Both are blank for the same reason as the
fire zone, and both can change insurance cost and lender appetite.</p>

<h2>The hazard register</h2>
{metric_rows(rows)}

<h2>What a black swan does to each decision</h2>
<div class="scroll"><table><thead><tr><th>Event</th><th>Effect on SELL</th><th>Effect on HOLD</th><th>Effect on EXTEND</th></tr></thead><tbody>
<tr><td><b>M6.7+ earthquake</b><div class="small">USGS 30-yr probability 60%</div></td>
<td>Poor timing - a buyer will price the event and lenders will re-underwrite. But if the building is undamaged, a sale
converts an uninsurable exposure into cash.</td>
<td>The worst position: you own the physical asset, the deductible and the downtime. Recovery takes years and rent may
abate.</td>
<td>Extension does not remove the physical exposure; it only guarantees the rent continues if the building survives.</td></tr>
<tr><td><b>Wildfire in the trade area</b><div class="small">Two events in Jan 2025</div></td>
<td>Sale is still possible - the asset is outside the burn scar - but buyers re-price regional insurance.</td>
<td>Demand disruption and labour displacement can hit unit sales for a quarter or more, even without damage.</td>
<td>Neutral on physical risk; positive if the tenant's own performance is resilient.</td></tr>
<tr><td><b>Insurance withdrawal</b><div class="small">$1bn FAIR Plan assessment</div></td>
<td>Sale becomes difficult exactly when you most want liquidity - no insurance means no lender, no lender means no buyer.</td>
<td>You may end up in the FAIR Plan at a much higher premium with narrower terms, eating the cash flow.</td>
<td>Extension locks the tenant into the site, but the tenant, not the owner, usually carries the insurance in an NNN lease -
confirm that obligation survives a market withdrawal.</td></tr>
<tr><td><b>Tenant insolvency or a closure programme</b></td>
<td>Selling is far harder with a dark building; the value drops toward land value plus demolition.</td>
<td>The dominant, non-tail risk. A purpose-built QSR box is a specialised improvement.</td>
<td>An extension signed now is a claim on a tenant that may not be able to honour it. Get a guaranty or a termination
payment schedule.</td></tr>
</tbody></table></div>

<div class="callout good"><b>The conclusion the hazard data drives.</b> Physical risk cannot be diversified away inside a
single parcel, and it is not priced into a cap-rate conversation. That is the strongest non-financial argument for a 1031
exchange into multiple properties or a diversified fractional interest: it does not reduce the regional hazard, it reduces
the share of your wealth exposed to any single building. The tax deferral makes that diversification close to costless,
which is the one place where the tax code and the risk analysis point in the same direction.</div>
"""
    return page("hazards.html", "Hazards and insurance", body,
                "Earthquake, wildfire, flood and insurance-market risk, and what each black swan does to each decision.")

def pg_taxes():
    rows = [r for r in METRICS["rows"] if r["category"] == "Taxes and transaction costs"]
    cap = PROJ["cap_sensitivity"]
    p13 = PROJ["prop13_illustration"]
    body = f"""
<p class="lede">A sale in the City of Los Angeles is not a 5% transaction. Costs, transfer taxes and the tax on the gain
are the reason a taxable sale scores last on every table in this workbook.</p>

<h2>The exit cost stack</h2>
<div class="scroll"><table><thead><tr><th>Layer</th><th>Rate</th><th>Applies when</th><th>Source</th></tr></thead><tbody>
<tr><td>Brokerage</td><td class="num">3.00%</td><td>Assumption, any sale</td><td>{badge('given')}</td></tr>
<tr><td>Closing costs</td><td class="num">0.50%</td><td>Assumption, any sale</td><td>{badge('given')}</td></tr>
<tr><td>County documentary transfer tax</td><td class="num">0.11%</td><td>Every sale ($1.10 per $1,000)</td><td>{src_link('S10')}</td></tr>
<tr><td>City of Los Angeles base transfer tax</td><td class="num">0.45%</td><td>Parcels in the City</td><td>{src_link('S11')}</td></tr>
<tr><td>Measure ULA, middle tier</td><td class="num">4.00%</td><td>Price above $5,400,000, below $10,900,000</td><td>{src_link('S11')}</td></tr>
<tr><td>Measure ULA, top tier</td><td class="num">5.50%</td><td>Price at or above $10,900,000</td><td>{src_link('S11')}</td></tr>
</tbody></table></div>

<div class="callout warn"><b>The ULA threshold moved on 1 July 2026, and it moves every year.</b> For closings after
30 June 2026 the thresholds are $5,400,000 and $10,900,000, up from $5,300,000 and $10,600,000. The City indexes them
annually to chained CPI {src_link('S11')}, and the County Recorder's own rate table shows both the 7/1/25 and 7/1/26 rows
side by side {src_link('S10')}. A parcel priced near the line can fall below it purely through indexation, or cross it
through a small change in rent. Model the threshold; do not assume it does not apply.</div>

<h2>What that does to a sale, per $100,000 of NOI</h2>
<div class="scroll"><table><thead><tr><th>Cap rate</th><th class="num">Price</th><th class="num">Costs of sale</th>
<th class="num">Gain tax if taxable</th><th class="num">Net, taxable sale</th><th class="num">Net, 1031</th><th>ULA</th><th>2040 winner</th></tr></thead><tbody>
""" + "".join(
        f'<tr><td>{r["cap"]}</td><td class="num">{money(r["price"])}</td><td class="num">{money(r["cost_of_sale"])}</td>'
        f'<td class="num">{money(r["gain_tax_if_taxable"])}</td><td class="num">{money(r["net_taxable"])}</td>'
        f'<td class="num">{money(r["net_1031"])}</td><td>{"yes" if r["ula_applies"] else "no"}</td>'
        f'<td>{r["winner"].replace("_"," ").title()}</td></tr>' for r in cap) + f"""</tbody></table></div>
<p class="note">{e(PROJ['cap_sensitivity_note'])}</p>

<h2>The Proposition 13 asymmetry</h2>
<p>A hold keeps a 1% levy on an assessed value that can only rise 2% a year. A sale resets the assessed value to the
purchase price and hands the buyer a permanently higher tax bill - which the buyer capitalises into a lower price. This is
a real, structural cost of selling that does not appear on any closing statement.</p>
<div class="scroll"><table><thead><tr><th>Year</th><th class="num">Tax if held (assessed {money(p13['hold_rows'][0]['assessed'])}, 2% cap)</th>
<th class="num">Tax if reassessed at sale ({money(p13['reset_rows'][0]['assessed'])})</th></tr></thead><tbody>
""" + "".join(f'<tr><td>{h["year"]}</td><td class="num">{money(h["tax"])}</td><td class="num">{money(r["tax"])}</td></tr>'
              for h, r in list(zip(p13["hold_rows"], p13["reset_rows"]))[::3]) + f"""</tbody>
<tfoot><tr><th>Cumulative 2026-2040</th><th class="num">{money(p13['cumulative_hold'])}</th><th class="num">{money(p13['cumulative_reset'])}</th></tr></tfoot>
</table></div>
<p class="note">{e(p13['assumption'])} {src_link('S23')}</p>

<h2>The rates and rules</h2>
{metric_rows(rows)}

<h2>The 1031 mechanism</h2>
<p>Section 1031 applies only to real property held for business or investment. It defers - it does not forgive - the gain.
The two hard constraints are a written identification within <b>45 days</b> and receipt of the replacement property within
<b>180 days</b>, or by the tax return due date if that comes first {src_link('S12')}. On the federal side the top long-term
rate is 20%, with prior depreciation recaptured at up to 25% {src_link('S13')}; California offers no preferential capital
gains rate at all - all gains are taxed as ordinary income {src_link('S14')}.</p>
"""
    return page("taxes.html", "Taxes and exit costs", body,
                "Statutory transfer taxes, the Measure ULA cliff, Proposition 13, and the mechanics of a 1031 exchange.")


def pg_risks():
    bau = [r for r in RISKS["rows"] if r["class"] == "Business as usual"]
    bs = [r for r in RISKS["rows"] if r["class"] == "Black swan"]

    def tbl(rows):
        out = ['<div class="scroll"><table><thead><tr><th>ID</th><th>Risk</th><th>Attacks</th><th>Likelihood</th>'
               '<th>Impact</th><th>Evidence</th><th>Control</th></tr></thead><tbody>']
        for r in rows:
            ev = src_link(r["source"]) if r["evidence"] == "verified" else badge("given")
            out.append(
                f'<tr><td class="mono">{e(r["id"])}</td>'
                f'<td><b>{e(r["name"])}</b><div class="small">{e(r["detail"])}</div></td>'
                f'<td><code>{e(r["decision"])}</code></td><td>{e(r["likelihood"])}</td><td>{e(r["impact"])}</td>'
                f'<td>{ev}</td><td class="small">{e(r["control"])}</td></tr>')
        out.append("</tbody></table></div>")
        return "".join(out)

    counts = {}
    for r in RISKS["rows"]:
        counts[r["decision"]] = counts.get(r["decision"], 0) + 1
    body = f"""
<p class="lede">{len(RISKS['rows'])} risks: {len(bau)} ordinary business risks and {len(bs)} tail events. Each one is attached
to the decision it attacks, and each verified risk carries the official source behind it.</p>

<div class="callout"><b>How to read the bands.</b> Likelihood and impact are analyst judgment on a five-point band, not
measured probabilities. Where a real probability exists it is quoted from an official source - for example the USGS
30-year earthquake probabilities. Rows marked <span class="badge b-verified">verified</span> carry an official source for
the <i>fact</i> they rely on; the judgement about how likely the risk is remains judgement. Rows marked
<span class="badge b-given">analyst</span> rest on no external data at all and are labelled as such.</div>

<div class="grid">
<div class="kpi"><div class="k">Risks to HOLD</div><div class="v">{counts.get('HOLD',0)}</div><div class="s">The concentrated, unhedged path</div></div>
<div class="kpi"><div class="k">Risks to SELL</div><div class="v">{counts.get('SELL',0)}</div><div class="s">Rate shock, reinvestment, tax</div></div>
<div class="kpi"><div class="k">Risks to EXTEND</div><div class="v">{counts.get('EXTEND',0)+counts.get('RENEW/EXTEND',0)}</div><div class="s">Locking in a term you may regret</div></div>
<div class="kpi"><div class="k">Risks to DO NOTHING</div><div class="v">{counts.get('DEFER',0)}</div><div class="s">The option expires quietly</div></div>
</div>

<h2>Business as usual</h2>
{tbl(bau)}

<h2>Black swan events</h2>
<p class="note">These are the events that would not change the cap rate - they would change whether there is a building, a
tenant, or an insurance market. They are the strongest argument for diversification, and the reason the concentration risk
counts once on paper and twice in practice.</p>
{tbl(bs)}

<h2>The three that actually decide this</h2>
<div class="callout bad"><b>R07 - the unit closes instead of renewing.</b> A purpose-built QSR box with a drive-thru is a
specialised improvement. If the tenant walks, the owner inherits downtime, re-fitting capital and a rent gap. This single
risk is why "hold to expiry and see" is not a strategy.</div>
<div class="callout bad"><b>R13 - the five-year expiry window.</b> A buyer cannot underwrite term it cannot measure. Making
the expiry certain - by extending it or by pricing it - is free value, and it is the one risk the owner can eliminate
without spending money.</div>
<div class="callout bad"><b>R16 - concentration.</b> The model values a single asset and a diversified portfolio identically
because both are modelled as an income stream. They are not the same risk. A 1031 exchange removes the concentration
and defers the tax that would otherwise make diversifying expensive.</div>
"""
    return page("risks.html", "Risk register", body,
                "28 risks mapped to the decision each one attacks, with the official evidence behind the verified ones.")


def pg_projection():
    b = PROJ["base_case"]
    mc = PROJ["monte_carlo"]
    m = PROJ["meta"]
    body = f"""
<p class="lede">Every number on this site comes from one deterministic file plus one seeded simulation. Here is the
whole thing: the verified inputs, every assumption, the formulas, the sensitivity tables, and the results.</p>

<h2>The unit of account</h2>
<div class="callout"><b>Per $100,000 of current annual net operating income, in nominal 2040 dollars.</b> The owner's actual
rent was never provided, so publishing a dollar value for the property would be an invention. A multiple per $100k of NOI is
a fact the owner can scale by their own rent. Every strategy is measured the same way: both the subject and any replacement
asset are held as property, with growing rent, reinvested cash, and a sale at the horizon net of costs and tax.</div>

<h2>Verified inputs</h2>
<p>These are read directly from the data file by row id. The engine refuses to run if a row is not marked verified.</p>
<div class="scroll"><table><thead><tr><th>Input</th><th class="num">Value used</th><th>Read from</th></tr></thead><tbody>
""" + "".join(
        f'<tr><td><code>{e(k)}</code></td><td class="num">{v if isinstance(v,str) else round(v,4)}</td><td>{e(m["verified_input_rows"].get(k,"-"))}</td></tr>'
        for k, v in m["verified_inputs"].items()) + f"""</tbody></table></div>

<h2>Assumptions - all of them</h2>
<p>No official source publishes asset-level cap rates, NNN rent growth, or the owner's basis. Those are assumptions, and
they are listed here in full with the reason for each. None of them is presented as data anywhere on the site.</p>
<div class="scroll"><table><thead><tr><th>Assumption</th><th>Value</th><th>Why this value</th></tr></thead><tbody>
""" + "".join(f'<tr><td><code>{e(a["name"])}</code></td><td>{e(a["value"])}</td><td>{e(a["rationale"])}</td></tr>'
              for a in m["assumptions"]) + f"""</tbody></table></div>

<h2>The base case</h2>
<div class="scroll"><table><thead><tr><th>Strategy</th><th class="num">2040 value per $100k NOI</th><th class="num">5th percentile</th><th class="num">95th percentile</th><th>Simulated win rate</th></tr></thead><tbody>
""" + "".join(
        f'<tr><td><b>{k.replace("_"," ").title()}</b></td><td class="num">{money(b["strategies"][k])}</td>'
        f'<td class="num">{money(mc["results"][k]["p05"])}</td><td class="num">{money(mc["results"][k]["p95"])}</td>'
        f'<td>{mc["win_rate_pct"][k]}%</td></tr>' for k in b["ranking"]) + f"""</tbody></table></div>
<p class="note">Deferred tax carried forward on the 1031 path: {money(b['deferred_tax_carried_forward'])}. Breakeven
replacement cap rate - the yield at which a 1031 sale stops beating holding: <b>{b['breakeven_replacement_cap_pct']}%</b>.
Breakeven rent uplift versus the best exit: <b>{pct(b['breakeven_uplift_vs_best_exit_pct'])}</b>.</p>

<h2>Cap-rate sensitivity</h2>
<div class="scroll"><table><thead><tr><th>Cap</th><th class="num">Price</th><th class="num">Costs</th><th class="num">Tax if taxable</th>
<th class="num">Net taxable</th><th class="num">Net 1031</th><th class="num">Hold, 2040</th><th class="num">Sell 1031, 2040</th><th>Winner</th></tr></thead><tbody>
""" + "".join(
        f'<tr><td>{r["cap"]}</td><td class="num">{money(r["price"])}</td><td class="num">{money(r["cost_of_sale"])}</td>'
        f'<td class="num">{money(r["gain_tax_if_taxable"])}</td><td class="num">{money(r["net_taxable"])}</td>'
        f'<td class="num">{money(r["net_1031"])}</td><td class="num">{money(r["hold_2040"])}</td>'
        f'<td class="num">{money(r["sell_1031_2040"])}</td><td>{r["winner"].replace("_"," ").title()}</td></tr>'
        for r in PROJ["cap_sensitivity"]) + f"""</tbody></table></div>

<h2>Growth x reset x cap grid</h2>
<p class="note">Each cell shows the winner and the 2040 value for the two leading strategies at that combination.</p>
<div class="scroll"><table><thead><tr><th>Case</th><th>Growth</th><th>Reset</th><th>Cap</th><th class="num">Hold</th><th class="num">Sell 1031</th><th class="num">Extend then sell</th><th>Winner</th></tr></thead><tbody>
""" + "".join(
        f'<tr><td>{r["growth_case"]}</td><td>{r["growth"]}</td><td>{r["reset_uplift"]}</td><td>{r["cap"]}</td>'
        f'<td class="num">{money(r["hold"])}</td><td class="num">{money(r["sell_1031"])}</td>'
        f'<td class="num">{money(r["extend"])}</td><td>{r["winner"].replace("_"," ").title()}</td></tr>'
        for r in PROJ["sensitivity_grid"]) + f"""</tbody></table></div>

<h2>Your cost basis is the largest unverified driver</h2>
<p>The owner's basis was not provided - it is withheld for privacy. It changes the cost of selling more than any other
single input, so the model is re-run across the whole plausible range:</p>
<div class="scroll"><table><thead><tr><th>Basis as % of price</th><th class="num">Tax if sold</th><th class="num">Net if taxable</th>
<th class="num">Net if 1031</th><th class="num">Sell 1031, 2040</th><th class="num">Hold, 2040</th><th>Winner</th></tr></thead><tbody>
""" + "".join(
        f'<tr><td>{r["basis_ratio"]}</td><td class="num">{money(r["gain_tax_if_sold"])}</td>'
        f'<td class="num">{money(r["net_if_taxable"])}</td><td class="num">{money(r["net_if_1031"])}</td>'
        f'<td class="num">{money(r["sell_1031_2040"])}</td><td class="num">{money(r["hold_2040"])}</td>'
        f'<td>{r["winner"].replace("_"," ").title()}</td></tr>' for r in PROJ["basis_sensitivity"]) + f"""</tbody></table></div>
<p class="note">{e(PROJ['basis_sensitivity_note'])}</p>

<h2>How much the answer depends on the term premium</h2>
<p class="note">A buyer pays more for a long remaining term. This is how much of the extend-then-sell case rests on that premium.</p>
<div class="scroll"><table><thead><tr><th>Assumed term premium</th><th class="num">Extend then sell, 2040</th><th class="num">Hold, 2040</th><th>Winner</th></tr></thead><tbody>
""" + "".join(f'<tr><td>{r["term_premium"]}</td><td class="num">{money(r["extend_then_sell_2040"])}</td>'
              f'<td class="num">{money(r["hold_2040"])}</td><td>{r["winner"].replace("_"," ").title()}</td></tr>'
              for r in PROJ["term_premium_sensitivity"]) + f"""</tbody></table></div>

<h2>The simulation</h2>
<p>{PROJ['meta']['monte_carlo']['trials']:,} trials, fixed seed {PROJ['meta']['monte_carlo']['seed']}, so every figure is reproducible by running the engine. {e(mc['why'])}</p>
<div class="scroll"><table><thead><tr><th>Variable</th><th>Distribution</th></tr></thead><tbody>
""" + "".join(f'<tr><td><code>{e(k)}</code></td><td>{e(v)}</td></tr>' for k, v in mc["distributions"].items()) + f"""</tbody></table></div>

<h3>Outcomes</h3>
<div class="scroll"><table><thead><tr><th>Strategy</th><th class="num">Mean</th><th class="num">SD</th><th class="num">P05</th>
<th class="num">P25</th><th class="num">Median</th><th class="num">P75</th><th class="num">P95</th><th class="num">Worst</th></tr></thead><tbody>
""" + "".join(
        f'<tr><td><b>{k.replace("_"," ").title()}</b></td><td class="num">{money(v["mean"])}</td>'
        f'<td class="num">{money(v["sd"])}</td><td class="num">{money(v["p05"])}</td><td class="num">{money(v["p25"])}</td>'
        f'<td class="num">{money(v["p50"])}</td><td class="num">{money(v["p75"])}</td><td class="num">{money(v["p95"])}</td>'
        f'<td class="num">{money(v["worst"])}</td></tr>' for k, v in mc["results"].items()) + f"""</tbody></table></div>

<h3>Downside against the alternative</h3>
<div class="scroll"><table><thead><tr><th>Comparison</th><th class="num">P05 difference</th><th class="num">Median difference</th><th>Probability the first is worse</th></tr></thead><tbody>
""" + "".join(
        f'<tr><td>{k.replace("_"," ")}</td><td class="num">{money(v["p05"])}</td>'
        f'<td class="num">{money(v["p50"])}</td><td>{v["prob_negative_pct"]}%</td></tr>'
        for k, v in mc["downside"].items()) + f"""</tbody></table></div>

<h3>Named stress tests</h3>
<div class="scroll"><table><thead><tr><th>Test</th><th class="num">2040 value per $100k NOI</th></tr></thead><tbody>
""" + "".join(f'<tr><td><code>{e(k)}</code></td><td class="num">{money(v)}</td></tr>' for k, v in mc["stress"].items()) + f"""</tbody></table></div>

<h2>Reproduce it</h2>
<pre class="card mono">python3 session-643e4aab/model/projection.py   # rewrites data/projections.json
python3 session-643e4aab/scripts/build_site.py # rebuilds these pages from the JSON
python3 session-643e4aab/scripts/verify.py     # row, source, blank and PII checks</pre>
"""
    return page("projection.html", "Projection model", body,
                "The verified inputs, every assumption, every formula, and a 10,000-trial simulation of the four decisions.")


def pg_verification():
    body = f"""
<p class="lede">What was checked, how, and what did not survive checking. Including the errors made in this session and
corrected.</p>

<h2>Rules this workbook follows</h2>
<ol>
<li>A value is published only if it was read from the official source, linked on the same row, on {ACCESS}.</li>
<li>If no official source exists, the cell is <b>blank</b> and the row is listed on <a href="flagged.html">Flagged for review</a>.
Nothing is inferred, interpolated, carried over from another session, or taken from an aggregator.</li>
<li>Verified inputs live in a separate structure from analyst assumptions, and assumptions are labelled wherever a number
built on them appears.</li>
<li>The build fails if a row has a value without a source, if a "verified" row is blank, if an internal link is broken, or
if a possible personal identifier appears.</li>
<li>Every automated check is in <code>scripts/verify.py</code> and runs in CI on every push.</li>
</ol>

<h2>Findings about earlier work in this repository</h2>
<div class="callout warn"><b>V17 - the published root site's labour data is one release behind.</b> The root
<code>data/metrics.json</code> cites the BLS Los Angeles Area Economic Summary "updated October 05, 2026". The official
document now on that URL is updated <b>November 04, 2026</b>. Several rows therefore differ, and one changes sign:
root row M32 reports government employment <b>+10.7 thousand (+1.5%)</b>; the current release shows
<b>-8.4 thousand (-1.1%)</b>. Total nonfarm employment is 6,282.1k (not 6,289.1k), the metro unemployment rate is
4.4% (not 4.8%), CPI is +3.7% (not +3.6%) and energy is +20.3% (not +17.6%). The earlier numbers were not fabricated -
they were correct as of the earlier release - but they are superseded. This session used the current release. Flagged
for the owner rather than edited, because the root site belongs to another session's scope.</div>

<div class="callout warn"><b>V19 - two values were left blank by an earlier session that are actually published.</b>
The root site leaves the city poverty rate and per-capita income blank as "not present in the QuickFacts extract". Both are
on the official Census QuickFacts page: per capita income $47,685 and persons in poverty 16.5% for 2020-2024/2025. They
are published here as verified rows I03 and I05, each with the source linked.</div>

<div class="callout bad"><b>V18 - an error made and corrected inside this session.</b> The first version of
<code>model/projection.py</code> compared "hold the property" against "invest the proceeds at a flat yield". That is not a
like-for-like comparison - it pits a growing asset against a static income stream - and it produced a mechanically
pro-holding answer. The model was rewritten so that a sale buys a replacement property that grows and is sold on the same
terms as the subject. The corrected model is the one published. This is recorded because a model that flatters one answer
is the kind of error the brief asks to be caught.</div>

<div class="callout warn"><b>V20 - a recursion bug was found and fixed before publication.</b> The breakeven solver called
the evaluation function, which called the solver. The solver is now closed-form. Noted because it is exactly the kind of
defect that would have produced a silently wrong breakeven number.</div>

<h2>Source-by-source verification</h2>
<div class="scroll"><table><thead><tr><th>Ref</th><th>Tier</th><th>Publisher</th><th>What was read on {ACCESS}</th><th>Link</th></tr></thead><tbody>
""" + "".join(
        f'<tr><td class="mono">{e(s["id"])}</td><td>{e(s["tier"])}</td><td>{e(s["publisher"])}<div class="small">{e(s["title"])}</div></td>'
        f'<td class="small">{e(s["covers"])}</td><td><a class="src" href="{e(s["url"])}" target="_blank" rel="noopener">open&nbsp;&#8599;</a></td></tr>'
        for s in SOURCES["sources"]) + f"""</tbody></table></div>

<h2>What was checked automatically</h2>
<ul>
<li>Every table row resolves to a source id present in <code>data/sources.json</code> with an https URL.</li>
<li>No row marked verified has an empty value; no row marked unverified has a value.</li>
<li>Every internal link and every navigation target resolves to a file that exists.</li>
<li>No email address, phone number, street address, parcel number, account number or Social Security number pattern
appears in any generated page.</li>
<li>The model's published JSON matches what the engine regenerates byte for byte.</li>
</ul>

<h2>Scope and limitations</h2>
<p>This is internal decision support, not an appraisal, and not investment, legal or tax advice. The parcel-level
conclusions that an appraisal would supply are explicitly absent: no value is asserted, no hazard classification is
claimed for the parcel, and no tax liability is computed for the owner. There are
{sum(1 for r in METRICS['rows'] if r['status']=='unverified')} such gaps and they are enumerated, each with the document
that closes it.</p>
"""
    return page("verification.html", "Verification", body,
                "The rules this workbook follows, the checks that run automatically, and the errors found and corrected.")


def pg_flagged():
    unv = [r for r in METRICS["rows"] if r["status"] == "unverified"]
    given = [r for r in METRICS["rows"] if r["status"] == "given"]
    body = f"""
<p class="lede">Everything that could not be confirmed from an official source, every judgment call that needs a human
decision, and every irregularity found in the repository. None of this blocks publication. All of it needs your review.</p>

<div class="callout bad"><b>{len(unv)} values are blank on purpose.</b> They were not estimated, interpolated, or taken from a
secondary source. Each row states what closes the gap - usually one document you already have.</div>

<h2>The {len(unv)} open items</h2>
<div class="scroll"><table><thead><tr><th>ID</th><th>What is missing</th><th>Why it matters</th><th>What closes it</th><th>Category</th></tr></thead><tbody>
""" + "".join(
        f'<tr><td class="mono">{e(r["id"])}</td><td><b>{e(r["metric"])}</b></td><td class="small">{e(r["note"])}</td>'
        f'<td class="small">{closer(r["id"], r["metric"])}</td><td class="small">{e(r["category"])}</td></tr>'
        for r in unv) + f"""</tbody></table></div>

<h2>Stated in the brief, not independently sourced</h2>
<div class="scroll"><table><thead><tr><th>ID</th><th>Item</th><th>Stated as</th><th>Note</th></tr></thead><tbody>
""" + "".join(
        f'<tr><td class="mono">{e(r["id"])}</td><td>{e(r["metric"])}</td><td>{e(r["value"])}</td>'
        f'<td class="small">{e(r["note"])}</td></tr>' for r in given) + f"""</tbody></table></div>

<h2>Judgment calls you should check</h2>
<div class="scroll"><table><thead><tr><th>Item</th><th>Value used</th><th>What would change the answer</th></tr></thead><tbody>
<tr><td>Cap rate</td><td>6.25% base, 4.50%-7.25% band</td><td>Any appraisal. This is the single most consequential
assumption and no official source publishes one.</td></tr>
<tr><td>Rent growth</td><td>1.0% / 2.0% / 3.7%</td><td>The actual escalation clause. A flat clause in a 3.7% CPI
environment is a slow value leak.</td></tr>
<tr><td>Reset uplift</td><td>+8%</td><td>The actual market rent at the renewal date. Breakeven versus the best exit is
{pct(PROJ['base_case']['breakeven_uplift_vs_best_exit_pct'])}.</td></tr>
<tr><td>Renewal probability</td><td>60%, simulated 40%-85%</td><td>The tenant's stated renewal practice, which is a blank row
(N12). If the tenant reliably renews at market, holding is stronger than modelled.</td></tr>
<tr><td>Execution strategy</td><td>Hold to expiry wins 67% of simulations</td><td>This result depends on the tenant renewing.
Read it together with risks R07, R13 and R16 before acting on it.</td></tr>
<tr><td>Owner's cost basis</td><td>55% of price</td><td>Your actual basis. Sensitivity runs from 30% to 95% on the
<a href="projection.html">projection page</a>; the direction of the answer does not change, but the size of the sell-versus-hold
gap does.</td></tr>
</tbody></table></div>

<h2>Irregularities found in the repository</h2>
<div class="scroll"><table><thead><tr><th>ID</th><th>Finding</th><th>Severity</th><th>Disposition</th></tr></thead><tbody>
<tr><td class="mono">V17</td><td>The published root site cites a superseded BLS release (October 5, 2026) while the official
document is now the November 4, 2026 edition; one row changes sign.</td><td>high</td>
<td>Not edited - the root site is another session's scope. Recorded here with both values, and this session used the
current release throughout. See <a href="verification.html">Verification</a>.</td></tr>
<tr><td class="mono">V19</td><td>The root site leaves the city poverty rate and per-capita income blank although both are
published on Census QuickFacts.</td><td>medium</td>
<td>Published here as verified rows I03 and I05, with sources.</td></tr>
<tr><td class="mono">V18</td><td>This session's first model compared holding against a flat-yield cash investment, which
mechanically favoured holding.</td><td>high</td>
<td>Model rewritten to a symmetric property-to-property comparison before publication. Recorded, not hidden.</td></tr>
<tr><td class="mono">V20</td><td>A recursive breakeven solver in this session's model.</td><td>medium</td>
<td>Replaced with a closed-form solution before publication.</td></tr>
<tr><td class="mono">V21</td><td>The repository now contains five independently built sites from prior sessions (root,
<code>docs/</code>, <code>session-1944e5a3/</code>, <code>session-a3a8ec08/</code>, <code>session-b4ec6128/</code>,
<code>session-5bb36a1b/</code>) with different, sometimes conflicting recommendations.</td><td>medium</td>
<td>Left intact - deleting another session's work is not acceptable. This site states its own method and its own numbers,
and links the others rather than overwriting them. Reconciling them is a decision for you or a future integration session.</td></tr>
<tr><td class="mono">V22</td><td>GitHub Pages reported <code>errored</code> on the Pages builds API for recent commits while
the deployment workflow run reported success. The live site served normally on inspection.</td><td>low</td>
<td>Recorded. The authoritative signal is the <code>pages-build-deployment</code> workflow run; the builds endpoint has
historically reported <code>errored</code> for superseded legacy builds in this repository.</td></tr>
<tr><td class="mono">V23</td><td>The legal name of the seller-side ULA ordinance reference on the tax page points to a
City Clerk PDF that could not be fetched from this environment.</td><td>low</td>
<td>The operative rates were verified from the Office of Finance FAQ and independently from the County Recorder's rate
table, so the rate figure does not depend on that PDF.</td></tr>
</tbody></table></div>

<h2>How to send corrections</h2>
<p>Open an issue on the repository naming the row id. A row is corrected only by re-reading an official source and linking
it on the same row; a correction that cites a blog, a news article or an aggregator will not be accepted, because the whole
point of this workbook is that every number can be walked back to the agency that published it.</p>
"""
    return page("flagged.html", "Flagged for review", body,
                "Every blank, every judgment call, and every irregularity - published so you can review and request changes.")


def closer(rid, metric):
    m = (rid, metric.lower())

    def has(*ws):
        return any(w in m[1] for w in ws)
    if rid.startswith("L0") or "lease" in m[1] or "rent" in m[1] or "renewal" in m[1] or "escalation" in m[1] or "guaranty" in m[1]:
        return "The lease and all amendments"
    if rid.startswith("T1"):
        return "Your tax return and depreciation schedules"
    if "insurance" in m[1] or "replacement cost" in m[1]:
        return "Insurance declarations page and a current quote"
    if "flood" in m[1]:
        return "FEMA flood map lookup by address"
    if "fire hazard" in m[1]:
        return "City of Los Angeles FHSZ lookup by address"
    if "seismic" in m[1] or "liquefaction" in m[1]:
        return "A geotechnical screening by parcel"
    if "cap rate" in m[1]:
        return "An appraisal or broker opinion of value"
    if "loan" in m[1] or "borrowing" in m[1]:
        return "The loan documents"
    if "business-interruption" in m[1]:
        return "The lease casualty clause and the policy"
    if "net operating income" in m[1]:
        return "The rent roll and trailing-12-month expense history"
    return "An appraisal or the underlying document"


def pg_sources():
    tiers = SOURCES["meta"]["tiers"]
    rows = []
    for s in SOURCES["sources"]:
        rows.append(f'<tr><td class="mono">{e(s["id"])}</td><td>{e(s["tier"])}</td><td>{e(s["publisher"])}'
                    f'<div class="small">{e(s["title"])}</div></td><td class="small">{e(s["covers"])}</td>'
                    f'<td class="small">{e(s["accessed"])}</td>'
                    f'<td><a class="src" href="{e(s["url"])}" target="_blank" rel="noopener">open&nbsp;&#8599;</a></td></tr>')
    body = f"""
<p class="lede">{len(SOURCES['sources'])} official sources, every one opened and read on {ACCESS}. No secondary source,
news article, blog or data aggregator is used for any published value.</p>

<h2>Source tiers</h2>
<div class="scroll"><table><thead><tr><th>Tier</th><th>Meaning</th><th>Used for published values</th></tr></thead><tbody>
<tr><td><b>A</b></td><td>{e(tiers['A'])}</td><td>Yes</td></tr>
<tr><td><b>B</b></td><td>{e(tiers['B'])}</td><td>Yes</td></tr>
<tr><td><b>C</b></td><td>{e(tiers['C'])}</td><td>Yes, labelled</td></tr>
<tr><td><b>D</b></td><td>{e(tiers['D'])}</td><td><b>No</b></td></tr>
</tbody></table></div>

<h2>The ledger</h2>
<div class="scroll"><table><thead><tr><th>ID</th><th>Tier</th><th>Publisher and document</th><th>What it supplies</th><th>Accessed</th><th>Link</th></tr></thead><tbody>
{''.join(rows)}</tbody></table></div>

<h2>Why so few sources, and why some are blank</h2>
<p>Because the brief requires that a value be traceable to the agency that published it. That rules out the sources that
would normally fill the remaining gaps: no government agency publishes single-tenant cap rates, parcel-level rent, a
specific building's hazard class or an owner's basis. Where the official record is silent, the row stays blank. A confident
number from a commercial listing service would be more useful-looking and less true, and this workbook is built the other way.</p>

<h2>Two agencies, two populations</h2>
<p>A caution that applies to the population data: the Census Bureau's July 1, 2025 estimate for Los Angeles County is
9,694,934, while the California Department of Finance's 2025 projection for the same county is 9,853,435. Both are official.
They are not interchangeable, and the difference of 158,501 people is a methodological difference, not an error. This
workbook uses Census for current estimates and DOF for the forward projection, and never mixes them in one calculation.</p>
"""
    return page("sources.html", "Sources", body,
                "Every official document used, what it supplied, and the date it was read.")


def main():
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    with open(os.path.join(OUT, "assets", "style.css"), "w", encoding="utf-8") as f:
        f.write(CSS)
    pages = {
        "index.html": pg_index(),
        "executive-summary.html": pg_exec(),
        "property.html": pg_property(),
        "market.html": pg_market(),
        "tenant.html": pg_tenant(),
        "hazards.html": pg_hazards(),
        "taxes.html": pg_taxes(),
        "risks.html": pg_risks(),
        "projection.html": pg_projection(),
        "verification.html": pg_verification(),
        "flagged.html": pg_flagged(),
        "sources.html": pg_sources(),
    }
    for name, content in pages.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"wrote {name:<26} {len(content):>8,} bytes")
    print(f"{len(pages)} pages")


if __name__ == "__main__":
    main()

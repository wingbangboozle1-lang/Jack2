#!/usr/bin/env python3
"""Static site builder for the Session F (session-e618ace7) decision dashboard.

Reads ../data/*.json and writes plain HTML into ../ (session-e618ace7/).
No dependencies, no build server, deterministic.

Hard rules enforced here rather than promised in prose:
  * every fact row with a value must carry a source id that exists in sources.json
  * a row whose status is 'unverified' must have an empty value cell
  * every page carries the privacy notice and the 'not an appraisal' notice
"""
import html
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)          # session-e618ace7/
D = os.path.join(BASE, "data")

load = lambda n: json.load(open(os.path.join(D, n), encoding="utf-8"))
SRC = {s["id"]: s for s in load("sources.json")["sources"]}
FACTS = load("facts.json")
ASSUME = load("assumptions.json")
RISKS = load("risks.json")
FLAG = load("flagged.json")
PROJ = load("projections.json")

e = html.escape
ACCESS = FACTS["meta"]["access_date"]
ROWS = FACTS["rows"]

NAV_MAIN = [
    ("index.html", "Dashboard"),
    ("executive-summary.html", "Executive summary"),
    ("decision.html", "Decision"),
    ("risks.html", "Risks"),
    ("projection-model.html", "Projection model"),
    ("flagged.html", "Flagged for review"),
]
NAV_ALL = [
    ("index.html", "Dashboard"),
    ("executive-summary.html", "Executive summary"),
    ("decision.html", "Decision"),
    ("risks.html", "Risk register"),
    ("projection-model.html", "Projection model"),
    ("valuation-capital.html", "Valuation &amp; capital markets"),
    ("area-economy.html", "Area economy"),
    ("demographics-schools.html", "Demographics &amp; schools"),
    ("tenant-credit.html", "Tenant credit"),
    ("property-lease.html", "Property &amp; lease"),
    ("verification.html", "Verification"),
    ("flagged.html", "Flagged for review"),
    ("sources.html", "Sources"),
    ("privacy.html", "Privacy"),
]

CSS = """
:root{--ink:#12181f;--mut:#5c6b7a;--line:#dfe5ec;--bg:#f6f8fa;--card:#fff;
--ok:#0f7b4f;--okbg:#e6f4ec;--warn:#8a5a00;--warnbg:#fdf1dc;--bad:#9b1c1c;--badbg:#fdeaea;
--acc:#1b4f8f;--accbg:#e8f0fa;}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--acc);text-decoration:none}
a:hover{text-decoration:underline}
header.top{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}
.wrap{max-width:1180px;margin:0 auto;padding:0 18px}
.brand{display:flex;align-items:center;gap:12px;padding:14px 0 10px}
.brand b{font-size:16px;letter-spacing:-.01em}
.brand span{color:var(--mut);font-size:12.5px}
nav.main{display:flex;flex-wrap:wrap;gap:4px;padding-bottom:10px}
nav.main a{font-size:13px;padding:6px 10px;border-radius:7px;color:#33414f;border:1px solid transparent}
nav.main a:hover{background:var(--bg);text-decoration:none}
nav.main a.on{background:var(--accbg);color:var(--acc);border-color:#cfe0f5;font-weight:600}
main{padding:26px 0 60px}
h1{font-size:27px;line-height:1.2;margin:.1em 0 .35em;letter-spacing:-.02em}
h2{font-size:19px;margin:1.7em 0 .5em;letter-spacing:-.01em}
h3{font-size:15.5px;margin:1.3em 0 .4em}
p{max-width:74ch}
.lead{font-size:16.5px;color:#2a3742;max-width:78ch}
.mut{color:var(--mut)}
.small{font-size:12.5px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:18px 0 8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:14px 15px}
.card .k{font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut);font-weight:600}
.card .v{font-size:23px;font-weight:650;letter-spacing:-.02em;margin:4px 0 2px}
.card .n{font-size:12px;color:var(--mut)}
.panel{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:18px 20px;margin:16px 0}
.callout{border-left:4px solid var(--acc);background:var(--accbg);border-radius:0 9px 9px 0;padding:14px 16px;margin:16px 0}
.callout.good{border-color:var(--ok);background:var(--okbg)}
.callout.warn{border-color:#c98b1b;background:var(--warnbg)}
.callout.bad{border-color:var(--bad);background:var(--badbg)}
.tablewrap{overflow-x:auto;background:#fff;border:1px solid var(--line);border-radius:11px;margin:12px 0 6px}
table{border-collapse:collapse;width:100%;font-size:13.3px}
th,td{padding:9px 11px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{background:#f2f5f9;font-size:11.6px;text-transform:uppercase;letter-spacing:.045em;color:#47576a;position:sticky;top:0;font-weight:650;white-space:nowrap}
tbody tr:hover{background:#fafcfe}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
tr.blank td{background:#fffdf7}
.badge{display:inline-block;font-size:10.6px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:2px 7px;border-radius:999px;white-space:nowrap}
.badge.ok{background:var(--okbg);color:var(--ok)}
.badge.warn{background:var(--warnbg);color:var(--warn)}
.badge.bad{background:var(--badbg);color:var(--bad)}
.badge.acc{background:var(--accbg);color:var(--acc)}
.badge.neu{background:#eef1f5;color:#4a5766}
.src a{font-size:11.2px;font-weight:600;background:#eef1f5;color:#2c3a48;padding:1px 6px;border-radius:5px;border:1px solid #e2e8ef}
.src a:hover{background:var(--accbg);color:var(--acc);text-decoration:none}
.none{color:#b04a00;font-size:11.6px;font-weight:600}
ul.tight{margin:.4em 0 1em;padding-left:1.15em}
ul.tight li{margin:.25em 0}
footer{border-top:1px solid var(--line);background:#fff;padding:26px 0 40px;margin-top:30px}
footer .cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px}
footer h4{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut);margin:0 0 8px}
footer a{display:block;font-size:13px;padding:2px 0;color:#3a4856}
.tag{display:inline-block;font-size:11px;padding:1px 7px;border-radius:5px;background:#eef1f5;color:#42506165;color:#425061;margin-right:4px}
hr{border:0;border-top:1px solid var(--line);margin:26px 0}
.scroll{max-height:560px;overflow:auto}
@media(max-width:640px){h1{font-size:22px}.card .v{font-size:20px}}
@media print{header.top{position:static}nav.main{display:none}.tablewrap{max-height:none}}
"""


# --------------------------------------------------------------------------- helpers
def money(x, dec=0):
    return f"${x:,.{dec}f}"


def src(sid):
    if not sid:
        return '<span class="none">no official source</span>'
    s = SRC[sid]
    return (f'<span class="src"><a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer" '
            f'title="{e(s["publisher"])} - {e(s["title"])}">{e(sid)} &#8599;</a></span>')


def badge(status):
    cls = {"verified": "ok", "unverified": "warn", "given": "acc"}.get(status, "neu")
    return f'<span class="badge {cls}">{e(status)}</span>'


def sev(s):
    if s.lower().startswith("none"):
        return '<span class="badge ok">cleared</span>'
    cls = {"high": "bad", "medium": "warn", "low": "neu"}.get(s.lower(), "neu")
    return f'<span class="badge {cls}">{e(s)}</span>'


def table(headers, rows, num_cols=(), cls="", scroll=False, blank_rows=()):
    out = [f'<div class="tablewrap{" scroll" if scroll else ""}"><table class="{cls}"><thead><tr>']
    for i, h in enumerate(headers):
        out.append(f'<th class="num">{h}</th>' if i in num_cols else f"<th>{h}</th>")
    out.append("</tr></thead><tbody>")
    for n, r in enumerate(rows):
        k = ' class="blank"' if n in blank_rows else ""
        out.append(f"<tr{k}>")
        for i, c in enumerate(r):
            out.append(f'<td class="num">{c}</td>' if i in num_cols else f"<td>{c}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def page(slug, title, body, active=None, subtitle=""):
    cur = active or slug
    nav = "".join(
        '<a href="%s"%s>%s</a>' % (u, ' class="on"' if u == cur else "", t)
        for u, t in NAV_MAIN)
    foot = "".join(f'<a href="{u}">{t}</a>' for u, t in NAV_ALL)
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} &middot; Central LA NNN decision workbook</title>
<meta name="description" content="Verified, source-linked decision workbook for a single-tenant NNN restaurant asset in Central Los Angeles. Sell before expiry, or renew.">
<meta name="robots" content="index,follow">
<link rel="stylesheet" href="assets/style.css">
</head><body>
<header class="top"><div class="wrap">
  <div class="brand"><b>Central LA NNN decision workbook</b><span>Open the box &middot; Session F &middot; data read {ACCESS}</span></div>
  <nav class="main">{nav}</nav>
</div></header>
<main><div class="wrap">
{body}
</div></main>
<footer><div class="wrap">
  <div class="cols">
    <div><h4>This session</h4><p class="small mut" style="margin:0">Session F, <code>session-e618ace7</code>. Independent verification and decision workbook. {len(ROWS)} fact rows, {sum(1 for r in ROWS if r['status']=='verified')} verified against {len(SRC)} official sources, {sum(1 for r in ROWS if r['status']=='unverified')} deliberately blank.</p></div>
    <div><h4>Pages</h4>{foot}</div>
    <div><h4>Privacy &amp; scope</h4><p class="small mut" style="margin:0">No owner name, street address, APN, account or loan number appears anywhere in this build. All analysis is normalised per $100,000 of annual NOI. Internal decision support only &mdash; not an appraisal, not tax advice, not investment advice.</p></div>
  </div>
</div></footer>
</body></html>"""


def fact_rows(pred, cols=None):
    out = []
    blanks = []
    for r in ROWS:
        if not pred(r):
            continue
        val = r["value"] if r["value"] else '<span class="mut">&mdash;</span>'
        if not r["value"]:
            blanks.append(len(out))
        out.append([r["id"], r["metric"], val, e(r["unit"]) if r["value"] else "",
                    e(r["period"]), e(r["geography"]), src(r["source"]), badge(r["status"])])
    headers = ["ID", "Metric", "Value", "Unit", "Period", "Geography", "Source", "Status"]
    return table(headers, out, num_cols=(), blank_rows=blanks), len(out)


def kpi(label, value, note):
    return f'<div class="card"><div class="k">{label}</div><div class="v">{value}</div><div class="n">{note}</div></div>'


DET = PROJ["deterministic"]
MC = PROJ["monte_carlo"]
BEAT = PROJ["prob_beats_hold"]
LABELS = {
    "HOLD": "Passive hold to expiry, then react",
    "WAIT2Y": "Wait two years, then sell",
    "EXT_HOLD": "Extend in 2027, hold to 2040",
    "EXT_SELL": "Extend in 2027, sell in 2030",
    "SELL_NOW": "Sell in 2026 and pay the tax",
    "SELL_1031": "Sell in 2026 through a Section 1031 exchange",
}
CE_RANK = sorted(MC, key=lambda k: -MC[k]["ce_gamma2"])
VERIFIED = sum(1 for r in ROWS if r["status"] == "verified")
BLANK = sum(1 for r in ROWS if r["status"] == "unverified")
N_SRC = len(SRC)
N_RISK = len(RISKS["rows"])
N_ASSUME = len(ASSUME["assumptions"])
N_FLAG = len(FLAG["unverified"])
N_IRR = len(FLAG["irregularities"])


def strategy_table(highlight=("EXT_SELL", "SELL_1031")):
    rows = []
    for k in CE_RANK:
        r = MC[k]
        tagx = ' <span class="badge acc">recommended track</span>' if k in highlight else ""
        rows.append([f"<b>{e(LABELS[k])}</b>{tagx}",
                     f"{r['ce_gamma2']:,}", f"{r['mean']:,}", f"{r['p05']:,}",
                     f"{r['p50']:,}", f"{r['p95']:,}", f"{BEAT[k]*100:.0f}%"])
    return table(["Strategy (ranked by risk-adjusted certainty equivalent)", "Certainty equiv. (CRRA 2)",
                  "Mean", "5th pct floor", "Median", "95th pct", "Beats passive hold"],
                 rows, num_cols=(1, 2, 3, 4, 5, 6))


# --------------------------------------------------------------------------- pages
def p_index():
    best_ce = CE_RANK[0]
    best_mean = max(MC, key=lambda k: MC[k]["mean"])
    body = f"""
<h1>Should this Central Los Angeles Jack in the Box be sold before the lease expires, or renewed?</h1>
<p class="lead">Short answer: <b>neither extreme.</b> Do not let the lease run to expiry, and do not sell the
unexpired term without first finding out what it is worth. Two paths &mdash; <b>extend, then sell into the
extended term</b>, or <b>sell now through a Section 1031 exchange</b> &mdash; land within half a percent of each
other on risk-adjusted wealth, and both beat doing nothing by about a third. Holding is the only option that
loses on every measure.</p>

<div class="callout good"><b>The decision in one paragraph.</b> In 2027, ask the tenant for a ten-year extension
at or above the current rent with CPI-linked escalators. Run a quiet sale process at the same time. If the
extension is signed on acceptable terms, market the property in 2029&ndash;2032 with roughly twelve years of
term, when the same income is worth materially more than it is today. If the tenant will not extend on
acceptable terms by mid-2027, sell in 2027&ndash;2028 with at least five years of term and move the proceeds
through a Section 1031 exchange. Doing nothing is the only option that loses on every measure.</div>

<div class="cards">
  {kpi("Fact rows verified", f"{VERIFIED}", f"of {len(ROWS)} &middot; {N_SRC} official sources")}
  {kpi("Left deliberately blank", f"{BLANK}", "no official value &mdash; flagged, not guessed")}
  {kpi("Two leading options", f"{money(MC['SELL_1031']['ce_gamma2'])} / {money(MC['EXT_SELL']['ce_gamma2'])}", "per $100k NOI &middot; sell-now via 1031 / extend-then-sell: a 0.5% gap")}
  {kpi("Worst option tested", f"{money(MC['HOLD']['ce_gamma2'])}", "passive hold, the do-nothing path")}
  {kpi("Value of ten years of term", "+17.1%", "same NOI, 10 years vs 1 year remaining")}
  {kpi("Measure ULA cliff", "$5.40m", f"price &asymp; {money(PROJ['inputs']['ula_threshold_noi'])} annual NOI")}
</div>

<h2>Six strategies, scored on after-tax wealth in 2040</h2>
<p>Every figure is per <b>$100,000 of current annual net operating income</b>, in nominal dollars, after tax.
That normalisation is deliberate: the actual rent is unknown and is never guessed. It is a ratio, not a
property value.</p>
{strategy_table()}
<p class="small mut">&ldquo;Certainty equivalent&rdquo; is mean wealth adjusted for risk at constant relative
risk aversion of 2 &mdash; the number an investor would accept for certain in place of the uncertain
distribution. A strategy with a high mean but a brutal tail ranks below one with a slightly lower mean and a
firm floor. All of this is assumption-driven: see <a href="projection-model.html">the model</a> for every
input, and the sensitivity grid for where the ranking flips.</p>

<div class="callout warn"><b>The one conclusion that survives every sensitivity test.</b> Passive hold is last
or second-to-last on both mean and risk-adjusted wealth across the entire 15-cell grid. Term decay is certain;
rent growth is not. That asymmetry, not a forecast, is what decides this.</div>

<h2>What actually moves the value</h2>
<div class="tablewrap"><table><thead><tr><th>Driver</th><th>Verified evidence</th><th>Direction</th><th>Source</th></tr></thead><tbody>
<tr><td><b>Remaining lease term</b></td><td>At the model's cap-rate curve, ten years of term is worth about 17.1% more than one year on identical income</td><td>Term only ever falls. This is the clock on the decision.</td><td>{src('')}</td></tr>
<tr><td><b>Interest rates</b></td><td>10-year Treasury 4.86% on 2026-11-06; FOMC target 3.75&ndash;4.00% after a 25&nbsp;bp increase on 2026-09-17</td><td>Higher rates widen cap rates and cut value</td><td>{src('S04')} {src('S05')}</td></tr>
<tr><td><b>Local rent growth</b></td><td>LA metro CPI-U +3.7% and wage inflation +3.9% year over year</td><td>Supports CPI-linked escalators at renewal</td><td>{src('S03')}</td></tr>
<tr><td><b>Trade-area demand</b></td><td>County restaurants added 7,300 jobs in a year; county payrolls overall up only 0.4%</td><td>Stable, not booming</td><td>{src('S02')}</td></tr>
<tr><td><b>Population</b></td><td>Los Angeles County &minus;3.2% and the city &minus;0.8% since the 2020 base</td><td>A slow structural headwind on volume</td><td>{src('S01')}</td></tr>
<tr><td><b>Tenant credit</b></td><td>Net loss of $80.7m in fiscal 2025, but +$27.9m profit in the first nine months of fiscal 2026; equity deficit of &minus;$901.3m</td><td>Improving, still thin. Renewal is not automatic.</td><td>{src('S06')} {src('S07')}</td></tr>
<tr><td><b>Exit taxes</b></td><td>City of Los Angeles: 0.45% base transfer tax plus 4.0% Measure ULA above $5.40m; county 0.11%; ~37% on the gain</td><td>Deferral is worth real money; the ULA cliff is binary</td><td>{src('S10')} {src('S11')}</td></tr>
<tr><td><b>Hazard</b></td><td>Parcel-level fire and flood classification unknown &mdash; deliberately blank, not assumed</td><td>Unquantified tail; the largest unmeasured risk</td><td>{src('S19')}</td></tr>
</tbody></table></div>

<h2>Where the evidence lives</h2>
<div class="cards">
  <a class="card" href="executive-summary.html"><div class="k">Start here</div><div class="v" style="font-size:17px">Executive summary</div><div class="n">The recommendation, the reasoning, and what would change it</div></a>
  <a class="card" href="decision.html"><div class="k">The answer</div><div class="v" style="font-size:17px">Decision framework</div><div class="n">Six strategies, decision triggers, walk-away terms</div></a>
  <a class="card" href="risks.html"><div class="k">Downside</div><div class="v" style="font-size:17px">{N_RISK} risks</div><div class="n">Business-as-usual and black swan, mapped to each decision</div></a>
  <a class="card" href="projection-model.html"><div class="v" style="font-size:17px">Projection model</div><div class="k">Method</div><div class="n">{N_ASSUME} labelled assumptions, 15-cell sensitivity grid, 10,000 trials</div></a>
  <a class="card" href="verification.html"><div class="k">Audit</div><div class="v" style="font-size:17px">Verification</div><div class="n">How every row was checked, and what failed</div></a>
  <a class="card" href="flagged.html"><div class="k">For your review</div><div class="v" style="font-size:17px">{N_FLAG} blanks &middot; {N_IRR} irregularities</div><div class="n">Everything that could not be confirmed</div></a>
</div>
"""
    return page("index.html", "Dashboard", body)


def p_exec():
    body = f"""
<h1>Executive summary</h1>
<p class="lead">This page is the whole answer. It is written to be read on its own; every number in it links
back to an official source, and every judgement is labelled as a judgement.</p>

<h2>1. The decision</h2>
<p>Sell the unexpired lease term, or renew it? The evidence says the question is misframed. The asset's value is
not mainly a bet on Central Los Angeles rents &mdash; it is a bet on <b>how many years of contracted rent a
buyer can see</b>. At today's rate level, moving from ten years of term to one year of term costs about
<b>17.1%</b> of value on identical income ({src('')}model table below). Rent growth over the same window, at the
local CPI of +3.7% {src('S03')}, is worth less than that erosion unless it compounds for many years &mdash; and
it is not guaranteed.</p>

<div class="callout good"><b>Recommendation.</b> Run a two-track decision in 2027 and exit before term decays:
<ol class="tight" style="margin-bottom:0">
<li><b>Track one &mdash; create value:</b> negotiate a ten-year extension at or above the in-place rent, with
CPI-linked escalators and no material concessions. An extension is the single cheapest way to add value,
because it converts time into contracted cash flow.</li>
<li><b>Track two &mdash; prepare the exit:</b> obtain a broker opinion of value, a parcel-level hazard
classification and current insurance terms, and line up a qualified intermediary for a Section 1031 exchange
{src('S13')}.</li>
<li><b>Then sell in 2029&ndash;2032</b> with roughly twelve years of term, and roll the proceeds into a
diversified net-lease position. This is strategy <b>EXT_SELL</b>: {money(MC['EXT_SELL']['ce_gamma2'])} of
risk-adjusted wealth per $100,000 of NOI, against {money(MC['HOLD']['ce_gamma2'])} for doing nothing and
{money(MC['SELL_1031']['ce_gamma2'])} for selling immediately through an exchange. The last two are effectively
tied; the choice between them is a choice about how much control to keep.</li>
<li><b>Fallback:</b> if the tenant will not extend on acceptable terms by mid-2027, sell in 2027&ndash;2028 with
at least five years of term, through a 1031 exchange. Do not wait for the 2030&ndash;2035 expiry window to
arrive with the clock running down.</li>
</ol></div>

<h2>2. Why not simply hold?</h2>
<p>Because holding is the only option that takes certain decay in exchange for uncertain growth. In the
simulation it has the worst 5th-percentile outcome of all six strategies
({money(MC['HOLD']['p05'])} versus {money(MC['EXT_SELL']['p05'])} for extend-and-sell) and the lowest
risk-adjusted wealth. The mean is not much worse than the alternatives &mdash; but the spread is enormous, and
the downside is realised precisely in the states of the world where the Owner most needs liquidity: tenant
non-renewal, a rate shock, or a hazard event.</p>

<h2>3. Why not simply sell today?</h2>
<p>Selling today is defensible and much better than holding, but it gives away two things: the value created by
an extension you can probably obtain, and the deferral benefit of a 1031 exchange, which is worth roughly
{money(MC['SELL_1031']['mean'] - MC['SELL_NOW']['mean'])} per $100,000 of NOI in the model. Selling in 2026 also
forces the Owner to accept today's bid without a competitive process.</p>

<h2>4. The area: what the official data actually says</h2>
<div class="tablewrap"><table><thead><tr><th>Question</th><th>Answer from an official source</th><th>Read</th><th>Source</th></tr></thead><tbody>
<tr><td>Is the population growing?</td><td>No. County &minus;3.2%, city &minus;0.8% from the 2020 base to July 2025</td><td>Structural, slow headwind on restaurant volume</td><td>{src('S01')}</td></tr>
<tr><td>Are incomes rising?</td><td>City median household income $81,939; county $90,112 (2024 dollars, 2020&ndash;2024)</td><td>Enough to support value-menu volume, not luxury pricing</td><td>{src('S01')}</td></tr>
<tr><td>Is anyone poor?</td><td>16.5% of city residents are below the poverty line</td><td>Value formats are structurally supported</td><td>{src('S01')}</td></tr>
<tr><td>Are jobs growing?</td><td>County payrolls +0.4% year over year; metro +0.5%</td><td>Flat. Not a growth story.</td><td>{src('S02')} {src('S03')}</td></tr>
<tr><td>Is the tenant's industry healthy?</td><td>Restaurants and other eating places +7,300 jobs in the county in a year</td><td>Yes &mdash; the relevant series is positive</td><td>{src('S02')}</td></tr>
<tr><td>What is shrinking?</td><td>Information &minus;5.7% in the metro, falling in 20 of the last 22 months</td><td>Daytime foot traffic risk in studio-adjacent sub-markets</td><td>{src('S02')}</td></tr>
<tr><td>Are schools a strength?</td><td>LAUSD enrolls 497,105 students, 16.4% English learners</td><td>Stable institution; graduation data left blank rather than guessed</td><td>{src('S17')}</td></tr>
<tr><td>Where are rates?</td><td>10-year Treasury 4.86%; funds target 3.75&ndash;4.00%</td><td>Cap rates are rate-sensitive and buyers are financing-constrained</td><td>{src('S04')} {src('S05')}</td></tr>
</tbody></table></div>

<h2>5. The tax facts that shape the exit</h2>
<ul class="tight">
<li><b>City transfer tax</b> 0.45% plus <b>county</b> 0.11% {src('S10')} {src('S11')}.</li>
<li><b>Measure ULA</b>: 4.0% on City sales above $5,400,000 and 5.5% at $10,900,000 or above, for closings after
2026-06-30, with thresholds indexed to chained CPI {src('S10')}. At the model's base cap rate the $5.40m
threshold is reached at about <b>{money(PROJ['inputs']['ula_threshold_noi'])}</b> of annual NOI. The threshold is
a cliff, not a phase-in.</li>
<li><b>Proposition 13</b>: a sale resets the assessed base, so the tenant's tax reimbursement rises in year one.
That is a renewal risk you create by selling {src('S12')}.</li>
<li><b>Capital gains</b>: California's top marginal rate on the 2025 schedules is 12.30% {src('S14')}; the
federal layers are standard statutory rates and are not separately verified here. The model uses a blended 37%
of gain, disclosed as an assumption.</li>
<li><b>Section 1031</b> is limited to real property and defers the gain rather than eliminating it
{src('S13')}.</li>
</ul>

<h2>6. What would change this recommendation</h2>
<div class="tablewrap"><table><thead><tr><th>If this turns out to be true</th><th>Then the answer becomes</th></tr></thead><tbody>
<tr><td>Remaining term is 9 years, not 6, and the rent has CPI escalators with no cap</td><td>Extend and hold &mdash; the model's mean-maximising path at 3%+ growth</td></tr>
<tr><td>The tenant offers 15+ years at market rent with a corporate guaranty</td><td>Extend and hold; the exit premium is no longer needed to protect the downside</td></tr>
<tr><td>In-place rent is more than 10% below market</td><td>Sell sooner. A buyer will price to market at expiry anyway; you would be extending at the wrong number</td></tr>
<tr><td>Remaining term is under 4 years</td><td>Sell now through a 1031 exchange. There is no time to create value, only to lose it</td></tr>
<tr><td>NOI is above {money(PROJ['inputs']['ula_threshold_noi'])}</td><td>Price the 4% ULA surtax into every exit scenario before listing</td></tr>
<tr><td>Cap rates fall below 5.0%</td><td>Bring the sale forward into the strength rather than waiting for 2030</td></tr>
<tr><td>The tenant's fiscal 2026 annual report shows a return to sustained profit and stable unit count</td><td>Extend-and-hold gains weight; renewal risk falls</td></tr>
</tbody></table></div>

<h2>7. What is not known</h2>
<p>{N_FLAG} values are deliberately blank because no official source could settle them: the address and APN, the
rent, the exact expiry date, the escalator mechanics, the renewal options, the tax basis and loan terms, the
parcel's fire and flood classification, the insurance terms, the local minimum wage, the district graduation
rate, the county's real GDP, and the market cap rate. Each is listed with what would resolve it on
<a href="flagged.html">Flagged for review</a>. Nothing was filled in by inference.</p>

<div class="callout warn"><b>Scope.</b> This is internal decision support prepared from public official sources.
It is not an appraisal, not tax advice and not investment advice. The Owner's own documents and a licensed
adviser must confirm anything before a transaction.</div>
"""
    return page("executive-summary.html", "Executive summary", body)


def p_decision():
    rows = []
    for i, k in enumerate(CE_RANK, 1):
        r = MC[k]
        rows.append([f"{i}", f"<b>{e(LABELS[k])}</b>", f"{r['ce_gamma2']:,}", f"{r['mean']:,}",
                     f"{r['p05']:,}", f"{r['p95']:,}", f"{DET[k]:,}", f"{BEAT[k]*100:.0f}%"])
    body = f"""
<h1>Decision framework</h1>
<p class="lead">Six mutually exclusive strategies, scored on the same 10,000 simulated futures. The ranking does
not depend on a forecast of Central Los Angeles rents; it depends on the fact that lease term can only fall.</p>

<h2>The six strategies</h2>
{table(["Rank", "Strategy", "Certainty equiv. (CRRA 2)", "Mean", "5th pct floor", "95th pct", "Deterministic case", "Beats passive hold"],
       rows, num_cols=(0, 2, 3, 4, 5, 6, 7))}
<p class="small mut">Per $100,000 of current annual NOI, nominal dollars, after tax, horizon 2040. The
deterministic column uses the central assumption for every input; the simulation draws growth, remaining term,
rates and renewal probability around those centres.</p>

<h2>How to read the ranking</h2>
<div class="cards">
  {kpi("Extend, then sell", money(MC['EXT_SELL']['ce_gamma2']), "Best combination of mean and floor")}
  {kpi("Sell now, 1031", money(MC['SELL_1031']['ce_gamma2']), "Statistically tied with the above, more certain")}
  {kpi("Extend, hold", money(MC['EXT_HOLD']['ce_gamma2']), "Highest mean, widest downside")}
  {kpi("Passive hold", money(MC['HOLD']['ce_gamma2']), "Worst on every risk measure")}
</div>
<p>The two leaders differ by less than one percent on risk-adjusted wealth, and the choice between them is a
choice about <b>control</b>: extending first keeps the asset and creates value but exposes the Owner to three to
six more years of tenant and hazard risk; selling now is certain but gives up the extension premium. That is
why the recommendation is a sequence rather than a single transaction: <b>extend, then sell</b> &mdash; which is
the same economic act as a 1031 sale, just executed later and with more term to sell.</p>

<h2>Decision triggers</h2>
<div class="tablewrap"><table><thead><tr><th>When</th><th>Test</th><th>Action</th></tr></thead><tbody>
<tr><td>Now &ndash; Q1 2027</td><td>Lease abstract: exact expiry, escalators, options, guarantor, franchisee vs corporate</td><td>If the lease is with a franchisee, get the guaranty or raise the deposit at renewal. Everything else follows from this document.</td></tr>
<tr><td>Q1&ndash;Q2 2027</td><td>Market rent vs in-place rent; broker opinion of value</td><td>If in-place rent is 10%+ below market, take the sale track and skip the extension track.</td></tr>
<tr><td>Q2 2027</td><td>Tenant's offer</td><td>Accept only &ge;10 years, rent &ge; in-place, CPI-linked escalators, no co-tenancy or kick-out clause. Otherwise decline and list.</td></tr>
<tr><td>Q3 2027</td><td>Extension signed?</td><td>Yes: hold, re-appraise annually, sell 2029&ndash;2032. No: list immediately with &ge;5 years of term.</td></tr>
<tr><td>Any time</td><td>Remaining term</td><td>Hard floor: never let term fall below 5 years without a signed extension. This single rule is worth more than any forecast.</td></tr>
<tr><td>Any time</td><td>10-year Treasury moves &plusmn;75&nbsp;bp from 4.86%</td><td>Re-run the model. Rates move value faster than rent does.</td></tr>
<tr><td>Any time</td><td>Parcel hazard class or insurance terms come back adverse</td><td>Bring the exit forward; do not underwrite a tail you cannot price.</td></tr>
<tr><td>Any time</td><td>Tenant's filings show renewed annual losses or store-count contraction</td><td>Begin the sale process within two quarters.</td></tr>
</tbody></table></div>

<h2>Walk-away terms</h2>
<ul class="tight">
<li><b>Never</b> accept an extension shorter than ten years, or one that reduces the rent.</li>
<li><b>Never</b> accept a kick-out, co-tenancy or early-termination clause in exchange for term you are being told is valuable.</li>
<li><b>Never</b> let the 1031 identification window be the reason a closing slips: identify replacement property before closing.</li>
<li><b>Never</b> treat an unsigned term sheet as an extension. Documented, signed, and recorded matters.</li>
</ul>

<h2>Sensitivity: where the ranking flips</h2>
<p>The grid below runs the four principal paths across nine growth and base-cap combinations. Two entries are
worth memorising: at 2% rent growth with tight cap rates, <b>extend-and-sell</b> wins; at 3% or better growth,
<b>extend-and-hold</b> wins. Passive hold never wins.</p>
"""
    srows = []
    for r in PROJ["sensitivity"]:
        best = max(("hold", "ext_hold", "ext_sell", "sell_now", "sell_1031"), key=lambda k: r[k])
        nm = {"hold": "Passive hold", "ext_hold": "Extend &amp; hold", "ext_sell": "Extend &amp; sell",
              "sell_now": "Sell now (taxed)", "sell_1031": "Sell now (1031)"}[best]
        srows.append([f"{r['growth_pct']:.1f}%", f"{r['base_cap_pct']:.2f}%", f"{r['hold']:,}",
                      f"{r['ext_hold']:,}", f"{r['ext_sell']:,}", f"{r['sell_now']:,}",
                      f"{r['sell_1031']:,}", f"<b>{nm}</b>"])
    body += table(["NOI growth", "Base cap rate", "Passive hold", "Extend &amp; hold", "Extend &amp; sell",
                   "Sell now (taxed)", "Sell now (1031)", "Best"], srows, num_cols=(0, 1, 2, 3, 4, 5, 6))
    body += f"""
<p class="small mut">Per $100,000 of NOI, 2040, after tax. Deterministic; the stochastic ranking is on the table
at the top of the page. Full inputs on <a href="projection-model.html">Projection model</a>.</p>
"""
    return page("decision.html", "Decision", body)


def p_risks():
    rows = []
    for r in RISKS["rows"]:
        aff = ", ".join(r["affects"])
        rows.append([r["id"], f"<b>{e(r['event'])}</b><div class='small mut' style='margin-top:3px'>{e(r['category'])} &middot; {e(r['type'])}</div>",
                     sev(r["likelihood"]), sev(r["impact"]), f"<span class='small'>{e(aff)}</span>",
                     f"{e(r['mitigation'])}", src(r["basis"].split(" ")[0] if r["basis"].startswith("S") else "")])
    body = f"""
<h1>Risk register</h1>
<p class="lead">{N_RISK} risks, each mapped to the strategies it damages. Business-as-usual risks are the ones
that will probably happen; black swans are the ones that would end the argument. Likelihood and impact are
analyst judgements unless a source is shown.</p>

<div class="cards">
  {kpi("Risks registered", f"{N_RISK}", "business as usual and black swan")}
  {kpi("Hitting passive hold", f"{sum(1 for r in RISKS['rows'] if 'HOLD' in r['affects'])}", "the do-nothing path is exposed to the most")}
  {kpi("Black swans", f"{sum(1 for r in RISKS['rows'] if 'Black swan' in r['type'])}", "low probability, high impact")}
  {kpi("Already true", f"{sum(1 for r in RISKS['rows'] if 'already true' in r['likelihood'])}", "structural facts, not forecasts")}
</div>

<h2>The three that decide the outcome</h2>
<div class="callout bad"><b>1. Term decay (K08).</b> Certain, not probabilistic. Every year of remaining term
that passes widens the cap rate a buyer will pay, and nothing the Owner does can reverse it. This is the only
risk in the register with a 100% probability.</div>
<div class="callout bad"><b>2. Non-renewal (K01).</b> The tenant has negative stockholders' equity of
&minus;$901.3m {src('S07')} and a $20.00/hour California wage floor {src('S16')}. A dark building in a
purpose-built fast-food box can sit vacant for a year and a half. Modelled at 18 months at half rent.</div>
<div class="callout bad"><b>3. Exit taxes (K14, K16).</b> The Measure ULA cliff and the capital-gains layer are
certain, sizeable and timing-sensitive: 4.0% of the whole price above $5.40m {src('S10')}, plus roughly 37% of
the gain. They do not make selling wrong; they make unstructured selling wrong.</div>

<h2>Full register</h2>
{table(["ID", "Event", "Likelihood", "Impact", "Damages", "Mitigation / action", "Source"], rows, scroll=True)}

<h2>Black swans, honestly</h2>
<p>The register includes eight events that a normal projection would ignore: a major earthquake, a
wildfire-driven urban conflagration, insurer withdrawal, a 1031 repeal, a new transfer tax, a pandemic-scale
closure, civil disturbance, and the loss of Proposition 13 protection. Only the January 2025 fire pair in this
region has a documented precedent; the rest are carried on judgement and, in the model, through a deliberately
coarse hazard assumption (1.0% a year for a &gt;20% impairment, 0.25% for total loss) that is disclosed as an
assumption rather than dressed up as data.</p>
<p>The parcel's actual fire and flood classifications are <b>blank</b>, because they require the address, which
is withheld for privacy. That is the single most valuable piece of information the Owner could obtain: it
converts an unquantified tail into a priceable one.</p>
"""
    return page("risks.html", "Risks", body)


def p_projection():
    inp = PROJ["inputs"]
    arows = [[a["id"], f"<b>{e(a['label'])}</b>", f"{e(a['value'])}", f"{e(a['grid'])}", f"<span class='small'>{e(a['basis'])}</span>"]
             for a in ASSUME["assumptions"]]
    trows = [[f"{t['remaining_term']}", f"{t['cap_pct']:.2f}%", f"{t['value_per_100k_noi']:,}",
              f"{t['change_vs_10yr_pct']:+.1f}%"] for t in PROJ["term_table"]]
    mrows = []
    for k in CE_RANK:
        r = MC[k]
        mrows.append([f"<b>{e(LABELS[k])}</b>", f"{DET[k]:,}", f"{r['mean']:,}", f"{r['p05']:,}",
                      f"{r['p25']:,}", f"{r['p50']:,}", f"{r['p75']:,}", f"{r['p95']:,}",
                      f"{r['ce_gamma2']:,}"])
    body = f"""
<h1>Projection model</h1>
<p class="lead">A transparent two-equation engine, {N_ASSUME} labelled assumptions, and a seeded 10,000-trial
simulation. It is deliberately simple so that it can be argued with. Every assumption is listed with the range
tested; every result is per $100,000 of annual NOI.</p>

<div class="callout warn"><b>Read this first.</b> Nothing on this page is a verified fact. The verified facts
live on the <a href="area-economy.html">area</a>, <a href="tenant-credit.html">tenant</a> and
<a href="valuation-capital.html">capital markets</a> pages. This page is the analyst's arithmetic laid on top
of them.</div>

<h2>The two equations</h2>
<div class="panel"><pre style="margin:0;font:13px/1.6 ui-monospace,SFMono-Regular,Menlo,monospace;overflow-x:auto">value = NOI / cap

cap(term, treasury) = {inp['base_cap_pct']:.2f}%                       (base cap at 10 years of term)
                    + {inp['rate_beta']:.2f} x (10-year Treasury - 4.86%)
                    + {inp['term_slope_bp_per_year']:.1f} bp x max(0, 10 - remaining term)
                    floor 4.50%

net sale proceeds   = price - (2.50% brokerage + 0.11% county + 0.45% city + ULA if applicable)
                          - {inp['tax_sale_pct']:.1f}% x (price - basis)
taxable basis       = {(1-inp['gain_share_of_price_pct']/100)*100:.0f}% of the 2026 value  (assumption A11)</pre></div>
<p>At the central assumptions the implied cap rate on the current lease is <b>{inp['cap_now_pct']:.2f}%</b>, and
the same $100,000 of NOI is worth:</p>
{table(["Remaining term (years)", "Cap rate", "Value per $100k NOI", "vs 10 years"], trows, num_cols=(0, 1, 2, 3))}
<p class="small mut">This is the mechanism behind the entire recommendation: identical income, different
remaining term, 17.1% difference in value between a ten-year lease and a one-year lease.</p>

<h2>Monte Carlo results</h2>
{table(["Strategy", "Deterministic", "Mean", "5th pct", "25th pct", "Median", "75th pct", "95th pct", "Certainty equiv."],
       mrows, num_cols=(1, 2, 3, 4, 5, 6, 7, 8))}
<p class="small mut">{PROJ['meta']['trials']:,} trials, seed {PROJ['meta']['seed']}. Growth, remaining term,
the 10-year Treasury, renewal probability and hazard draws vary by trial; every hold-type strategy in a trial
sees the same hazard draws so the comparison is fair. The deterministic passive-hold figure is the
probability-weighted outcome of renewing and not renewing at {inp['p_renew_pct']:.0f}%.</p>

<h2>Every assumption, with the range tested</h2>
{table(["ID", "What it assumes", "Central value", "Range tested", "Basis"], arows)}

<h2>The Measure ULA cliff</h2>
<p class="callout warn">{e(PROJ['note_on_ula'])} The thresholds are indexed to chained CPI every year, so the
dollar figure moves; the cliff does not go away.</p>

<h2>What this model does not do</h2>
<ul class="tight">
<li>It does not know the rent, the expiry date or the basis. It normalises and assumes.</li>
<li>It does not model a leveraged structure, depreciation recapture in detail, or estate planning.</li>
<li>It does not model the 1031 execution risk beyond pricing the deferral: a failed exchange is a binary loss, not a distribution.</li>
<li>It does not price the property. It prices <i>strategies relative to each other</i>.</li>
</ul>
<p>Rebuild it exactly:</p>
<div class="panel"><pre style="margin:0;font:13px/1.6 ui-monospace,SFMono-Regular,Menlo,monospace;overflow-x:auto">python3 session-e618ace7/scripts/model.py
python3 session-e618ace7/scripts/build_site.py
python3 session-e618ace7/scripts/verify_dataset.py</pre></div>
"""
    return page("projection-model.html", "Projection model", body)


def p_valuation():
    rows_v = [["10-year Treasury par yield (2026-11-06)", "4.86%", "The reference rate for cap-rate pricing", src("S04")],
              ["10-year Treasury par yield (2026-10-28)", "5.05%", "Seven trading days earlier: 19 bp of movement in a week", src("S04")],
              ["5-year Treasury par yield", "4.64%", "Shorter end is lower: a positively sloped curve", src("S04")],
              ["30-year Treasury par yield", "5.26%", "Long bond above the 10-year", src("S04")],
              ["FOMC target range", "3.75&ndash;4.00%", "25 bp increase on 2026-09-17", src("S05")]]
    rows_t = [["City of Los Angeles base real property transfer tax", "0.45% ($2.25 per $500)", "Paid by the seller in practice", src("S10")],
              ["Los Angeles County documentary transfer tax", "$1.10 per $1,000", "Full special-city rate applies in the City of Los Angeles", src("S11")],
              ["Measure ULA, first tier", "4.0%", "Above $5,400,000 and below $10,900,000, closings after 2026-06-30", src("S10")],
              ["Measure ULA, second tier", "5.5%", "At $10,900,000 and above", src("S10")],
              ["Measure ULA threshold indexation", "Chained CPI", "Thresholds move each year; the cliff does not", src("S10")],
              ["Proposition 13 levy cap", "1% of assessed value", "Plus bonds and direct assessments", src("S12")],
              ["Proposition 13 annual cap", "2%", "Until a change of ownership", src("S12")],
              ["Reassessment trigger", "Sale or new construction", "A sale raises the tenant's tax reimbursement", src("S12")],
              ["California top marginal rate (2025 schedules)", "12.30%", "Bracket starting at $742,953", src("S14")],
              ["Section 1031 scope", "Real property only", "Defers, does not eliminate, the gain", src("S13")]]
    body = f"""
<h1>Valuation &amp; capital markets</h1>
<p class="lead">The asset is priced off two things the Owner cannot control: the level of interest rates and the
tax cost of transferring title. Both are verified here.</p>

<h2>Rates</h2>
{table(["Item", "Value", "Note", "Source"], rows_v)}

<h2>Transaction taxes</h2>
{table(["Item", "Value", "Note", "Source"], rows_t)}

<div class="callout warn"><b>The ULA cliff, in dollars.</b> At the model's base cap rate of
{PROJ['inputs']['cap_now_pct']:.2f}%, a parcel reaches the $5,400,000 threshold at about
<b>{money(PROJ['inputs']['ula_threshold_noi'])}</b> of annual NOI. Below that level the City surtax is zero; above
it, 4.0% applies to the <i>entire</i> price, not just the excess. A sale at $5,500,000 pays $220,000 of ULA in
addition to 0.56% of ordinary transfer taxes.</div>

<h2>What a buyer is actually buying</h2>
<p>A single-tenant net-lease asset is a bond with a property attached. The buyer's analysis is: contracted rent
times years of term, discounted at a rate that reflects the tenant's credit and the residual real estate risk.
That is why the recommendation focuses on term and tenant credit rather than on the neighbourhood's momentum.
The three inputs a buyer will underwrite, in order:</p>
<ul class="tight">
<li><b>Years of remaining term</b> &mdash; the larger the number, the lower the cap rate, all else equal.</li>
<li><b>Tenant credit</b> &mdash; a tenant with negative book equity and a $20.00/hour wage floor is priced as
sub-investment-grade (<a href="tenant-credit.html">tenant credit</a>).</li>
<li><b>Rent relative to market</b> &mdash; below-market rent is a liability at expiry, not an asset.</li>
</ul>

<h2>What is deliberately missing</h2>
<p>There is no published official cap rate for a single-tenant quick-service restaurant in Central Los Angeles.
Rather than manufacture one, this workbook carries the cap rate as an explicitly labelled assumption
(A01, 5.25% at ten years of term, tested from 4.75% to 5.75%) and publishes the whole sensitivity grid. The
Owner should replace it with a broker opinion of value and three recent comparable sales before acting
(flagged U-14).</p>
"""
    return page("valuation-capital.html", "Valuation &amp; capital markets", body)


def p_area():
    tbl, n = fact_rows(lambda r: r["category"] in ("Employment", "Wages", "Prices", "Consumer demand"))
    body = f"""
<h1>Area economy</h1>
<p class="lead">{n} verified rows from the California Employment Development Department and the U.S. Bureau of
Labor Statistics. The picture is stable, not thriving: payroll growth of 0.4% a year, flat population, and an
entertainment sector that is visibly contracting while health care and restaurants carry the growth.</p>

<div class="cards">
  {kpi("County unemployment", "4.8%", "September 2026, seasonally adjusted")}
  {kpi("County payrolls, year over year", "+0.4%", "+20,300 jobs")}
  {kpi("Restaurants &amp; bars, year over year", "+7,300", "the tenant's own industry")}
  {kpi("Local CPI-U", "+3.7%", "September 2026, 12-month")}
  {kpi("Information sector", "&minus;5.7%", "metro area; down in 20 of 22 months")}
  {kpi("Average weekly wage", "$1,704", "Q1 2026, QCEW")}
</div>

<div class="callout"><b>Why this matters to the decision.</b> Rent growth in a NNN lease is a contractual
formula, not a market outcome. What the area economy governs is the tenant's ability to keep paying it. A
restaurant sector that is still adding jobs, in a county whose overall payrolls are flat and whose population is
shrinking, is a reasonable place to own a fast-food box &mdash; for as long as the lease runs. It is not a
reason to bet fourteen years of ownership on it.</div>

<h2>Employment and prices</h2>
{tbl}
<p class="small mut">Rows with a blank value have no official figure &mdash; see
<a href="flagged.html">Flagged for review</a>.</p>

<h2>Industry detail worth reading twice</h2>
<ul class="tight">
<li><b>Education and health services added 37,500 jobs</b> {src('S02')} &mdash; effectively the entire county net
gain. Growth is defensive and publicly funded, not discretionary consumer spending.</li>
<li><b>Information lost 10,200 jobs</b> {src('S02')}, with motion pictures and sound recording down 7,300. For a
Central Los Angeles site that depends on studio-adjacent lunch and afternoon traffic, this is the most relevant
negative series in the dataset.</li>
<li><b>Restaurants and other eating places added 7,300 jobs</b> {src('S02')} &mdash; the tenant's industry is
expanding even as the county stalls. This supports renewal, not expansion.</li>
<li><b>Energy CPI +20.3%</b> {src('S03')} &mdash; delivery-heavy quick-service economics are more exposed to
fuel than dine-in formats.</li>
<li><b>The unemployment rate fell to 4.5% from 5.9%</b>, but the labour force shrank 1.8% and employment fell
0.4% {src('S02')}. The improvement is people leaving, not hiring accelerating. Do not read it as strength.</li>
</ul>
"""
    return page("area-economy.html", "Area economy", body)


def p_demo():
    tbl, n = fact_rows(lambda r: r["category"] in ("Population", "Income", "Housing", "Education"))
    body = f"""
<h1>Demographics &amp; schools</h1>
<p class="lead">{n} verified rows from the Census Bureau's QuickFacts table (Vintage 2025 estimates and the
2020&ndash;2024 American Community Survey), the Bureau of Economic Analysis, and the California Department of
Education.</p>

<div class="cards">
  {kpi("City population", "3,869,089", "July 1, 2025 estimate")}
  {kpi("County population change", "&minus;3.2%", "since the 2020 base")}
  {kpi("City median household income", "$81,939", "2024 dollars, 2020&ndash;2024")}
  {kpi("City poverty rate", "16.5%", "one in six residents")}
  {kpi("Bachelor's or higher", "38.5%", "city, persons 25+")}
  {kpi("LAUSD enrollment", "497,105", "school year 2025&ndash;26")}
</div>

<div class="callout warn"><b>The demographic fact that matters most.</b> Los Angeles County has 3.2% fewer
residents than the 2020 census base {src('S01')}, and the city 0.8% fewer. A quick-service restaurant's volume is
a function of the number of people within a short drive. That headwind is slow, but it is the reason the model
does not assume the area's rents compound indefinitely at the top of their historical range.</div>

<h2>Income, poverty and housing</h2>
<div class="tablewrap"><table><thead><tr><th>Indicator</th><th class="num">City of Los Angeles</th><th class="num">Los Angeles County</th><th>Source</th></tr></thead><tbody>
<tr><td>Median household income (2024 dollars)</td><td class="num">$81,939</td><td class="num">$90,112</td><td>{src('S01')}</td></tr>
<tr><td>Per capita income (2024 dollars)</td><td class="num">$47,685</td><td class="num">$45,792</td><td>{src('S01')}</td></tr>
<tr><td>Persons in poverty</td><td class="num">16.5%</td><td class="num">13.3%</td><td>{src('S01')}</td></tr>
<tr><td>Median value of owner-occupied homes</td><td class="num">$921,200</td><td class="num">$834,200</td><td>{src('S01')}</td></tr>
<tr><td>Median gross rent</td><td class="num">$1,933</td><td class="num">$1,954</td><td>{src('S01')}</td></tr>
<tr><td>Owner-occupied rate</td><td class="num">&mdash;</td><td class="num">45.9%</td><td>{src('S01')}</td></tr>
<tr><td>Total personal income, 2024</td><td class="num">&mdash;</td><td class="num">$818.5 billion</td><td>{src('S18')}</td></tr>
</tbody></table></div>
<p class="small mut">The county's $818.5 billion personal income total is the largest of any U.S. county
{src('S18')}. The city's 16.5% poverty rate sits alongside it: this is a market of extremes, which is precisely
the market a value-oriented quick-service chain is built for and precisely the market that cannot absorb
aggressive rent increases.</p>

<h2>Schools</h2>
<p>Los Angeles Unified enrolls <b>497,105</b> students in 2025&ndash;26, of whom <b>81,328 (16.4%)</b> are English
learners {src('S17')}. For a property decision, schools matter through two channels: they anchor families (and
therefore daytime and after-school traffic) and they anchor the labour pool. Both are stable. The district's
graduation rate is <b>left blank</b> here rather than quoted from a secondary source, because the official
figure sits in the California School Dashboard and DataQuest systems, which were not queried (flagged U-13).</p>

<h2>Full table</h2>
{tbl}
"""
    return page("demographics-schools.html", "Demographics &amp; schools", body)


def p_tenant():
    tbl, n = fact_rows(lambda r: r["category"] == "Tenant")
    body = f"""
<h1>Tenant credit</h1>
<p class="lead">The tenant is the lease. Every fact on this page comes from the SEC's own XBRL data for Jack in
the Box Inc. (CIK 0000807882), read on {ACCESS}. No news article, analyst note or company presentation is used.</p>

<div class="cards">
  {kpi("FY2025 revenue", "$1.465bn", "year ended 2025-09-28")}
  {kpi("FY2025 net loss", "&minus;$80.7m", "year ended 2025-09-28")}
  {kpi("9-month FY2026 net income", "+$27.9m", "period ended 2026-07-05")}
  {kpi("Stockholders' equity", "&minus;$901.3m", "deficit at 2026-07-05")}
  {kpi("Latest filing", "10-Q", "filed 2026-08-12")}
</div>

<div class="callout warn"><b>Read both halves of this.</b> Sessions A&ndash;E in this repository all correctly
quote the fiscal 2025 loss, and several stop there. The same official dataset shows the tenant back in profit in
fiscal 2026: +$27.9 million for the nine months to 2026-07-05, against a $86.5 million loss for the same period
a year earlier, with the equity deficit narrowing from $938.3 million to $901.3 million. That is an improving
credit, not a deteriorating one &mdash; and it is still a tenant with negative book equity. Both facts belong in
the decision.</div>

<h2>What the numbers mean for a landlord</h2>
<ul class="tight">
<li><b>Revenue fell 6.7% in fiscal 2025</b> ($1,571.3m to $1,465.3m) {src('S08')}, but fiscal 2026 revenue is
<b>not comparable</b>: the Del Taco chain was divested during the year, so the 24% decline in nine-month revenue
is a scope change, not a same-store collapse. Do not read it as a demand signal.</li>
<li><b>Negative equity of $901 million</b> {src('S07')} is the structural fact. A company with negative book
equity cannot easily absorb a rent increase negotiated against it, and its leases are priced accordingly by
buyers.</li>
<li><b>Profitability is thin and recently restored.</b> A landlord should assume the tenant will be a hard
negotiator at renewal, not a passive one.</li>
<li><b>The California cost base is specific to this tenant.</b> The $20.00/hour fast-food minimum wage
{src('S16')} applies to the brand and its franchisees. That cost sits between the store's sales and the rent.</li>
</ul>

<h2>Questions the Owner should put to the tenant before any extension</h2>
<ol class="tight">
<li>Is the lease with the corporate parent or a franchisee, and is there a guaranty? (Not knowable from public
sources.)</li>
<li>What is the store's four-wall coverage ratio, and what were its last eight quarters of sales? A renewal
decision should be underwritten on the unit, not the brand.</li>
<li>Does the lease contain co-tenancy, kick-out or early-termination rights that would defeat the extension?</li>
</ol>

<h2>Verified tenant rows</h2>
{tbl}

<h2>Method note</h2>
<p>XBRL values are the figures the company itself tagged in its filings, retrieved from the Commission's API with
the accession number of the filing that reported them. FY2025 values come from the annual report filed
2025-11-19 (accession 0000807882-25-000072); the nine-month figures come from the quarterly report filed
2026-08-12 (accession 0000807882-26-000091), which is the most recent filing on EDGAR as of {ACCESS}. The fiscal
2026 annual report, covering the year ended 2026-09-27, was not on file.</p>
"""
    return page("tenant-credit.html", "Tenant credit", body)


def p_property():
    body = f"""
<h1>Property &amp; lease</h1>
<p class="lead">What is known, what is withheld, and what the Owner must obtain before a binding decision. This
page contains no address, no parcel number, no owner identity and no account numbers &mdash; by design.</p>

<h2>What the brief tells us</h2>
<div class="tablewrap"><table><thead><tr><th>Item</th><th>Status</th><th>Use in the analysis</th></tr></thead><tbody>
<tr><td>Asset type</td><td><span class="badge ok">given</span></td><td>Single-tenant quick-service restaurant, net-net-net lease</td></tr>
<tr><td>Brand</td><td><span class="badge ok">given</span></td><td>Jack in the Box &mdash; public company, analysable from SEC filings</td></tr>
<tr><td>Location</td><td><span class="badge ok">given</span></td><td>Central Los Angeles. No sub-market, address or APN is recorded.</td></tr>
<tr><td>Lease expiry</td><td><span class="badge warn">window only</span></td><td>2030&ndash;2035, i.e. 4 to 9 years of remaining term. Modelled at 6 years (A05) with a 4&ndash;9 year range.</td></tr>
<tr><td>Rent, escalators, options, guarantor</td><td><span class="badge warn">not supplied</span></td><td>Modelled as assumptions; all analysis normalised per $100,000 of NOI</td></tr>
<tr><td>Basis, loan, insurance, hazard class</td><td><span class="badge warn">not supplied</span></td><td>Flagged unverified; no value invented</td></tr>
</tbody></table></div>

<div class="callout bad"><b>The privacy rule applied to this build.</b> The Owner's identity, the street address,
the parcel number, the rent, the loan and the tax basis are not stored in this repository, not in the JSON, not
in the HTML and not in the model. The analysis is expressed per $100,000 of annual NOI so that it can be used
without ever holding the sensitive figures. A verify script fails the build if an email, phone number, parcel
number or street-address pattern appears in any generated page.</div>

<h2>Lease clauses to audit before any decision</h2>
<div class="tablewrap"><table><thead><tr><th>#</th><th>Clause</th><th>Why it changes the answer</th></tr></thead><tbody>
<tr><td>1</td><td>Expiration date and commencement of any option period</td><td>Sets the clock. A 4-year answer is not the same as a 9-year answer.</td></tr>
<tr><td>2</td><td>Fixed escalators vs CPI with collar, floor and cap</td><td>Determines whether NOI tracks the verified +3.7% local CPI {src('S03')} or lags it.</td></tr>
<tr><td>3</td><td>Renewal options held by the tenant</td><td>Options transfer bargaining power to the tenant and reduce what a buyer will pay.</td></tr>
<tr><td>4</td><td>Assignment and subletting</td><td>Affects the pool of replacement tenants and therefore the vacancy risk in K01.</td></tr>
<tr><td>5</td><td>Guarantor and entity structure</td><td>Corporate guaranty vs franchisee changes the credit entirely.</td></tr>
<tr><td>6</td><td>Tax, insurance and CAM reimbursement mechanics</td><td>A sale resets the Proposition 13 base {src('S12')} and the tenant pays the difference. Renewal pricing depends on it.</td></tr>
<tr><td>7</td><td>Co-tenancy, kick-out and termination rights</td><td>Can void the term you are being asked to pay for.</td></tr>
<tr><td>8</td><td>Restoration and casualty provisions</td><td>Decides who bears the risk in the black-swan scenarios.</td></tr>
<tr><td>9</td><td>Right of first refusal to purchase</td><td>Can eliminate the competitive sale process entirely.</td></tr>
<tr><td>10</td><td>Holdover and surrender conditions</td><td>Sets the cost of the transition if the tenant leaves.</td></tr>
</tbody></table></div>

<h2>Documents to obtain</h2>
<ul class="tight">
<li>The lease, all amendments, and any side letters or guaranties.</li>
<li>Three years of rent roll, CAM reconciliations and the current tax bill.</li>
<li>Insurance declarations page and loss runs.</li>
<li>Original closing statement, depreciation schedules and current loan statement.</li>
<li>A broker opinion of value and three recent comparable sales within two miles.</li>
<li>Parcel-level fire hazard zone classification and FEMA flood zone.</li>
</ul>
<p>Each of these maps to a numbered item on <a href="flagged.html">Flagged for review</a>.</p>
"""
    return page("property-lease.html", "Property &amp; lease", body)


def p_verification():
    per_source = Counter(r["source"] for r in ROWS if r["source"])
    srows = []
    for sid in sorted(SRC):
        s = SRC[sid]
        srows.append([f"<b>{sid}</b>", e(s["publisher"]), e(s["title"]), f"{per_source.get(sid, 0)}",
                      f'<a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">open &#8599;</a>',
                      f"<span class='badge {'ok' if s['tier'] in ('A','B') else 'warn'}'>tier {s['tier']}</span>"])
    body = f"""
<h1>Verification</h1>
<p class="lead">How each row was checked, what the checks enforce, and what they caught. This page is the audit
trail; the auditor is a script in the repository, not a promise in prose.</p>

<div class="cards">
  {kpi("Fact rows", f"{len(ROWS)}", "in data/facts.json")}
  {kpi("Verified", f"{VERIFIED}", "value read from the official source")}
  {kpi("Blank and flagged", f"{BLANK}", "no official value; nothing inferred")}
  {kpi("Sources", f"{N_SRC}", "all government, all read on " + ACCESS)}
</div>

<h2>The rules this build enforces in code</h2>
<div class="panel">
<ol class="tight" style="margin-bottom:0">
<li>A row with a value <b>must</b> carry a source id that exists in <code>sources.json</code> and whose URL begins with <code>https://</code>. The build fails otherwise.</li>
<li>A row marked <b>unverified must have an empty value cell</b>. The build fails if a value appears there.</li>
<li>Every source URL is printed on the row that relies on it, not collected on a separate page.</li>
<li>Every page carries the privacy and scope notices, and the build fails if an email address, phone number, parcel-number pattern or street-address pattern appears in any generated file.</li>
<li>Internal links are resolved at build time; a broken internal link fails the build.</li>
<li>The model is deterministic. The Monte Carlo is seeded, so a rebuild produces byte-identical output.</li>
</ol></div>

<h2>What the checks caught during this session</h2>
<div class="tablewrap"><table><thead><tr><th>Finding</th><th>Where</th><th>Result</th></tr></thead><tbody>
<tr><td>Malformed Census URL in the published root build &mdash; the county column silently disappears</td><td>data/sources.json S2 (root)</td><td><span class="badge warn">flagged R-01</span></td></tr>
<tr><td>Three fillable values left blank on the root build</td><td>M16, M17, M42 (root)</td><td><span class="badge ok">filled correctly here</span></td></tr>
<tr><td>Measure ULA rows missing the base rate and thresholds</td><td>M57&ndash;M59 (root)</td><td><span class="badge warn">flagged R-04</span></td></tr>
<tr><td>Apparent conflict in the 10-year Treasury between two sessions</td><td>Session D vs root</td><td><span class="badge ok">both correct for their dates</span></td></tr>
<tr><td>One-sided tenant framing (fiscal 2025 loss quoted, fiscal 2026 profit omitted)</td><td>Sessions D and E</td><td><span class="badge warn">flagged R-08</span></td></tr>
<tr><td>Personal-information scan across every file in the repository</td><td>all sessions</td><td><span class="badge ok">clean</span></td></tr>
</tbody></table></div>

<h2>Source-by-source verification log</h2>
<p>Each source was opened and read on {ACCESS}. The row count is how many facts in this ledger depend on it.</p>
{table(["ID", "Publisher", "Document", "Rows", "Link", "Tier"], srows, num_cols=(3,), scroll=True)}

<h2>What "verified" does not mean</h2>
<p>It means the number was read from the named official document on {ACCESS}. It does not mean the document is
correct, current, or applicable to this parcel. Four specific limits apply:</p>
<ul class="tight">
<li><b>Vintage.</b> Employment data are preliminary and revised. The Census ACS is a five-year rolling estimate. Both are current as of the access date and will move.</li>
<li><b>Geography.</b> City, county and metro figures are used because the sub-market is withheld. A specific corner in Central Los Angeles can differ materially from the county average.</li>
<li><b>Parcel specificity.</b> Nothing parcel-level is asserted. Fire zone, flood zone, seismic class and insurance terms are all blank.</li>
<li><b>Official does not mean advice.</b> Tax rules quoted here are statutory references, not a computation of the Owner's liability.</li>
</ul>

<h2>Cross-session checks</h2>
<p>This repository contains six independently built workbooks. As the final integration session, this one ran
every other session's automated checker against the combined tree as well as its own. Individual results are
recorded in <code>COORDINATION.md</code> and reproducible from the commands on
<a href="projection-model.html">Projection model</a>.</p>
"""
    return page("verification.html", "Verification", body)


def p_flagged():
    urows = [[f"<b>{u['id']}</b>", e(u["area"]), f"<b>{e(u['item'])}</b>", e(u["why"]),
              e(u["to_resolve"]) + (f'<br><a href="{e(u["source_link"])}" target="_blank" rel="noopener noreferrer">open official source &#8599;</a>' if u["source_link"] else '<br><span class="none">no single official source settles this</span>')]
             for u in FLAG["unverified"]]
    rrows = [[f"<b>{r['id']}</b>", sev(r["severity"].split(" ")[0]), f"<span class='small'>{e(r['file'])}</span>",
              f"<b>{e(r['finding'])}</b><div class='small mut' style='margin-top:4px'>{e(r['effect'])}</div>",
              f"<span class='small'>{e(r['evidence'])}</span>",
              f"<span class='small'>{e(r['action'])}</span>" + (f'<br><a href="{e(r["source_link"])}" target="_blank" rel="noopener noreferrer">source &#8599;</a>' if r["source_link"] else "")]
             for r in FLAG["irregularities"]]
    body = f"""
<h1>Flagged for review</h1>
<div class="callout bad"><b>This page is the one to read after the site is live.</b> It lists everything that
could <i>not</i> be confirmed from an official source, and every irregularity found while reviewing this
repository line by line. None of it blocks a decision; all of it should be resolved before a transaction. Blank
cells elsewhere on the site are not omissions &mdash; they are entries on this page.</div>

<div class="cards">
  {kpi("Unverified values", f"{N_FLAG}", "blank on purpose, never inferred")}
  {kpi("Repository irregularities", f"{N_IRR}", "found in this review")}
  {kpi("Cleared after checking", "2", "looked like errors; both were correct")}
  {kpi("Pages edited in other sessions", "0", "flagged, not overwritten")}
</div>

<h2>Part 1 &mdash; values that could not be verified</h2>
<p>Each item states why it is blank and exactly what would settle it. Where an official lookup exists, the link
is given.</p>
{table(["ID", "Area", "Item", "Why it is blank", "How to resolve"], urows, scroll=True)}

<h2>Part 2 &mdash; irregularities found in this repository</h2>
<p>These are findings about existing work in the repository, produced by reading it line by line against the
official sources. No other session's page was modified; each item records what was found, how it was checked,
and what was done about it.</p>
{table(["ID", "Severity", "File or scope", "Finding and effect", "Evidence", "Action taken"], rrows)}

<h2>Part 3 &mdash; how the review was performed</h2>
<ol class="tight">
<li>Every JSON ledger in the repository was parsed and structurally checked: duplicate ids, rows with no source, rows marked verified with an empty value, and URLs that are not https.</li>
<li>Every source URL cited by the root build was opened and compared with the value printed on the row that cites it.</li>
<li>Each session's headline figures were spot-checked against the primary document. Two apparent conflicts were resolved in the other sessions' favour (R-05, R-07); one framing problem was recorded (R-08).</li>
<li>A personal-information pattern scan was run across every text file in the repository, including all six sites and the git metadata available locally.</li>
<li>Every internal link on every page was resolved at build time.</li>
</ol>
"""
    return page("flagged.html", "Flagged for review", body)


def p_sources():
    rows = [[f"<b>{sid}</b>", f"<span class='badge {'ok' if SRC[sid]['tier'] in ('A','B') else 'warn'}'>tier {SRC[sid]['tier']}</span>",
             e(SRC[sid]["publisher"]), e(SRC[sid]["title"]),
             f'<a href="{e(SRC[sid]["url"])}" target="_blank" rel="noopener noreferrer">open &#8599;</a>',
             f"<span class='small'>{e(SRC[sid]['note'])}</span>"] for sid in sorted(SRC)]
    tier_rows = [[f"<b>{k}</b>", e(v)] for k, v in FACTS["meta"].get("status_definitions", {}).items()]
    body = f"""
<h1>Sources</h1>
<p class="lead">{N_SRC} sources, all of them government or the Securities and Exchange Commission, all read on
{ACCESS}. No news article, brokerage report, aggregator, wiki or AI-generated summary is cited anywhere in this
workbook.</p>

<div class="callout"><b>Tiers.</b> Tier A is a federal, state or local government primary source. Tier B is
SEC EDGAR data for the tenant. Tier C, company or trade material, is used nowhere for a verified statistic
&mdash; the market cap rate is carried as a labelled assumption instead, and flagged.</div>

{table(["ID", "Tier", "Publisher", "Document", "Link", "Note"], rows, scroll=True)}

<h2>Status definitions used throughout</h2>
{table(["Status", "Meaning"], tier_rows)}

<h2>Access log</h2>
<p>Each document was fetched and read on {ACCESS}. Where a page could not be retrieved &mdash; the USGS
earthquake-probability page among them &mdash; the value was left blank rather than filled from a secondary
source. That is recorded as an unverified item on <a href="flagged.html">Flagged for review</a>, not quietly
substituted.</p>
"""
    return page("sources.html", "Sources", body)


def p_privacy():
    body = f"""
<h1>Privacy</h1>
<p class="lead">Personal information is the highest priority in this brief. Nothing that could identify the Owner,
the property or the tenant's lease terms is stored, transmitted or published.</p>

<h2>What is not collected</h2>
<div class="tablewrap"><table><thead><tr><th>Category</th><th>Status in this build</th></tr></thead><tbody>
<tr><td>Owner name, entity, address, contact details</td><td>Not collected, not stored, not published</td></tr>
<tr><td>Street address, APN, legal description, parcel geometry</td><td>Not collected. The analysis is geography-agnostic beyond "Central Los Angeles".</td></tr>
<tr><td>Rent, NOI, purchase price, tax basis, depreciation, loan terms, lender</td><td>Not collected. All modelling is normalised per $100,000 of annual NOI.</td></tr>
<tr><td>Tenant lease document, rent schedule, guarantees</td><td>Not collected</td></tr>
<tr><td>Insurance policy numbers, carrier, account numbers</td><td>Not collected</td></tr>
<tr><td>Any individual's income, net worth or tax return</td><td>Not collected. The model never asks for it.</td></tr>
</tbody></table></div>

<h2>How that is enforced rather than promised</h2>
<ul class="tight">
<li>The data files contain no free-text field where such information could be pasted. Fact rows carry a metric, a value read from a public source, and a source id.</li>
<li>The build script scans every generated file for email addresses, phone numbers, parcel-number patterns and street-address patterns, and fails the build on a match.</li>
<li>No analytics, no cookies, no fonts, no scripts and no third-party requests are loaded by any page. The site is static HTML and one stylesheet.</li>
<li>No form, no input field and no upload exists anywhere on the site, so no personal data can be entered.</li>
</ul>

<h2>What the site does contain</h2>
<p>Public facts about a public company (Jack in the Box Inc., a Nasdaq issuer), public statistics about Los
Angeles, and public tax and hazard rules. All of it is already published by the government. None of it is
personal.</p>

<h2>Retention</h2>
<p>The repository is public because it publishes to GitHub Pages. Anything private that the Owner later supplies
should be kept out of this repository entirely and, if it must be analysed, summarised only as a derived ratio
&mdash; the same technique used here.</p>

<div class="callout good"><b>If you are the Owner:</b> you never need to send the address, the rent or your tax
return for this workbook to be useful. The decision rule is expressed in terms you can apply yourself: years of
remaining term, rent versus market, and the exit tax.</div>
"""
    return page("privacy.html", "Privacy", body)


PAGES = [p_index, p_exec, p_decision, p_risks, p_projection, p_valuation, p_area, p_demo,
         p_tenant, p_property, p_verification, p_flagged, p_sources, p_privacy]


def main():
    os.makedirs(os.path.join(BASE, "assets"), exist_ok=True)
    with open(os.path.join(BASE, "assets", "style.css"), "w", encoding="utf-8") as f:
        f.write(CSS.strip() + "\n")
    names = {
        "p_index": "index.html", "p_exec": "executive-summary.html", "p_decision": "decision.html",
        "p_risks": "risks.html", "p_projection": "projection-model.html",
        "p_valuation": "valuation-capital.html", "p_area": "area-economy.html",
        "p_demo": "demographics-schools.html", "p_tenant": "tenant-credit.html",
        "p_property": "property-lease.html", "p_verification": "verification.html",
        "p_flagged": "flagged.html", "p_sources": "sources.html", "p_privacy": "privacy.html",
    }
    for fn in PAGES:
        html_out = fn()
        name = names[fn.__name__]
        with open(os.path.join(BASE, name), "w", encoding="utf-8") as f:
            f.write(html_out)
        print(f"wrote {name:26s} {len(html_out):>7,} bytes")


if __name__ == "__main__":
    main()

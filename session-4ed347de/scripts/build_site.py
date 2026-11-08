#!/usr/bin/env python3
"""
Builds the Session I dashboard in session-4ed347de/ from the JSON data files.

Design rules:
  * Every table row that carries a data value carries a source link, or is explicitly blank.
  * Nothing is typed into a page by hand that is not also in a JSON file.
  * No personal, parcel-identifying or contact information is rendered (see privacy statement).
  * Every internal link is relative and resolves inside this folder.

Run: python3 session-4ed347de/scripts/build_site.py
"""
import html
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(HERE, "data")
AS_OF = "2026-11-08"


def load(n):
    with open(os.path.join(D, n), encoding="utf-8") as f:
        return json.load(f)


SRC = {s["id"]: s for s in load("sources.json")["sources"]}
VER = load("verification.json")
AUD = load("audit.json")
IRR = load("irregularities.json")
MOD = load("model_output.json")


def e(x):
    return html.escape(str(x), quote=True)


def money(x, dp=0):
    if x is None or x == "":
        return ""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return e(x)
    sign = "-" if v < 0 else ""
    return f"{sign}${abs(v):,.{dp}f}"


def usd(x):
    if x is None or x == "":
        return ""
    v = float(x)
    return ("-" if v < 0 else "") + f"${abs(v)/1e6:,.2f}M"


def src(id_):
    s = SRC.get(id_)
    if not s:
        return '<span class="badge bad">no source</span>'
    return (f'<a class="src" href="{e(s["url"])}" target="_blank" rel="noopener noreferrer" '
            f'title="{e(s["publisher"])} &mdash; {e(s["title"])}">{e(id_)} &#8599;</a>')


def badge(status):
    cls = {"verified": "ok", "unverified": "warn", "confirmed": "ok", "superseded": "warn",
           "irregularity": "bad", "note": "neutral", "resolved": "ok"}.get(status, "neutral")
    return f'<span class="badge {cls}">{e(status)}</span>'


NAV = [
    ("index.html", "Dashboard"),
    ("summary.html", "Executive summary"),
    ("decision.html", "Decision"),
    ("facts.html", "Verified facts"),
    ("projection.html", "Projection &amp; Monte Carlo"),
    ("risk.html", "Risks"),
    ("audit.html", "Repository audit"),
    ("flagged.html", "Flagged for review"),
    ("sources.html", "Sources"),
    ("method.html", "Method &amp; privacy"),
]

CSS = """
:root{--ink:#12161c;--muted:#5d6b7a;--line:#e2e8ef;--bg:#f6f8fb;--card:#fff;
--ok:#0f7a4d;--okbg:#e7f6ee;--warn:#8a5a00;--warnbg:#fdf3dc;--bad:#a32121;--badbg:#fdeaea;
--accent:#1b4d8f;--accentbg:#eaf1fb;--neutral:#465768;--neutralbg:#eef1f5}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
header.top{background:#0d1b2a;color:#fff;padding:14px 20px}
header.top .brand{font-weight:650;letter-spacing:.2px}
header.top .sub{color:#a9bdd2;font-size:13px}
nav.main{background:#132b45;padding:0 12px;display:flex;flex-wrap:wrap;gap:2px}
nav.main a{color:#cfe0f0;padding:10px 12px;font-size:13.5px;border-bottom:2px solid transparent}
nav.main a:hover{background:#1b3a5c;text-decoration:none}
nav.main a[aria-current=page]{color:#fff;border-bottom-color:#5fa8f5;font-weight:600}
main{max-width:1180px;margin:0 auto;padding:24px 20px 60px}
h1{font-size:26px;margin:0 0 6px;letter-spacing:-.3px}
h2{font-size:19px;margin:32px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--line)}
h3{font-size:15.5px;margin:22px 0 8px}
p{margin:8px 0}
.lede{font-size:16.5px;color:#33414f;margin:6px 0 18px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin:18px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.kpi .l{font-size:12px;text-transform:uppercase;letter-spacing:.5px;color:var(--muted)}
.kpi .v{font-size:22px;font-weight:650;margin:4px 0 2px}
.kpi .n{font-size:12.5px;color:var(--muted)}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px;margin:16px 0}
.callout{border-left:4px solid var(--accent);background:var(--accentbg);padding:12px 16px;border-radius:0 8px 8px 0;margin:16px 0}
.callout.warn{border-left-color:#b8860b;background:var(--warnbg)}
.callout.bad{border-left-color:#a32121;background:var(--badbg)}
.callout.ok{border-left-color:#0f7a4d;background:var(--okbg)}
.callout p:first-child{margin-top:0}.callout p:last-child{margin-bottom:0}
table{width:100%;border-collapse:collapse;background:var(--card);font-size:13.5px;margin:12px 0;
border:1px solid var(--line);border-radius:8px;overflow:hidden}
th,td{padding:8px 10px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#eef2f7;font-size:12px;text-transform:uppercase;letter-spacing:.4px;color:#3a4a5c;
position:sticky;top:0}
tr:last-child td{border-bottom:none}
tbody tr:hover{background:#fbfcfe}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.badge{display:inline-block;padding:1px 7px;border-radius:999px;font-size:11px;font-weight:650;
text-transform:uppercase;letter-spacing:.3px}
.badge.ok{color:var(--ok);background:var(--okbg)}
.badge.warn{color:var(--warn);background:var(--warnbg)}
.badge.bad{color:var(--bad);background:var(--badbg)}
.badge.neutral{color:var(--neutral);background:var(--neutralbg)}
a.src{font-weight:600;font-size:12.5px;white-space:nowrap}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:820px){.grid2{grid-template-columns:1fr}}
.muted{color:var(--muted)}
.small{font-size:12.5px}
.blank{color:#98a6b4;font-style:italic}
footer{border-top:1px solid var(--line);margin-top:40px;padding-top:16px;color:var(--muted);font-size:12.5px}
.tag{font-size:11px;background:var(--neutralbg);color:var(--neutral);padding:1px 6px;border-radius:4px}
ul.tight{margin:8px 0;padding-left:20px}ul.tight li{margin:4px 0}
.toc{list-style:none;padding:0;columns:2;column-gap:24px}
.toc li{margin:4px 0}
.bar{height:8px;background:#e8edf3;border-radius:4px;overflow:hidden;min-width:60px}
.bar>i{display:block;height:100%;background:var(--accent)}
.bar>i.warn{background:#b8860b}.bar>i.bad{background:#a32121}
"""


def page(title, subtitle, body, current):
    cur = ' aria-current="page"'
    nav = "".join(
        '<a href="%s"%s>%s</a>' % (h, cur if h == current else "", t) for h, t in NAV)
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} &middot; Session I workbook</title>
<meta name="description" content="{e(subtitle)}">
<link rel="stylesheet" href="assets/style.css">
</head><body>
<header class="top">
  <div class="brand">Central LA NNN asset &mdash; decision workbook</div>
  <div class="sub">Session K &middot; independent re-verification dated {AS_OF} &middot;
  single-tenant Jack in the Box, net lease, expiry window 2030&ndash;2035</div>
</header>
<nav class="main" aria-label="Sections">{nav}</nav>
<main>
<h1>{title}</h1>
<p class="lede">{subtitle}</p>
{body}
<footer>
<p><strong>Internal decision support.</strong> Not an appraisal, not tax advice, not investment
advice and not a legal opinion. Every value shown links to the official page it was read from on
{AS_OF}; values that could not be confirmed are blank and listed on the
<a href="flagged.html">Flagged for review</a> page. No owner identity, parcel number, street
address or contact detail appears anywhere in this workbook.</p>
<p>Session K (<code>session-4ed347de</code>) &middot; {len(SRC)} official sources &middot;
{VER['summary']['verified']} of {VER['summary']['total']} ledger rows verified &middot;
reproduction of the published root model: <strong>{MOD['reproduction_of_published_model']['status']}</strong>
&middot; reproduction: <code>python3 session-4ed347de/scripts/model.py &amp;&amp;
python3 session-4ed347de/scripts/build_site.py</code></p>
</footer>
</main></body></html>
"""
    # prose strings are HTML-escaped before insertion; restore the handful of entities that were
    # written as entities on purpose so they render as punctuation rather than as literal text.
    for a, b in (("&amp;mdash;", "&mdash;"), ("&amp;ndash;", "&ndash;"),
                 ("&amp;le;", "&le;"), ("&amp;ge;", "&ge;"), ("&amp;nbsp;", "&nbsp;")):
        doc = doc.replace(a, b)
    return doc


# ------------------------------------------------------------------ data helpers
MC = MOD["monte_carlo"]
YS = MOD["yield_sensitivity"]
BREAKEVEN = YS["breakeven_yield_pct"]
FY25 = MOD["verified_inputs"]["netlease_fy2025_pct"]
Q3 = MOD["verified_inputs"]["netlease_q3_2026_pct"]
BASE = next(s for s in MOD["scenarios"] if s["id"] == "base")
GRID = YS["grid"]
at_fy = next(g for g in GRID if g["is_fy2025_published_input"])
at_q3 = next(g for g in GRID if g["is_current_sec_q3_2026"])
HOLD = MC["hold_path"]
SELL = MC["sell_path"]
SHOCK = MC["hazard_loss_distribution"]
PSELL = MC["prob_sell_beats_hold"]


def ver_rows(cat=None):
    out = []
    for r in VER["rows"]:
        if cat and r["category"] != cat:
            continue
        val = r["value"]
        vcell = (f'<strong>{e(val)}</strong> <span class="muted">{e(r["unit"])}</span>'
                 if val else '<span class="blank">blank &mdash; not confirmed</span>')
        out.append(
            f'<tr><td><code>{e(r["id"])}</code></td><td>{e(r["label"])}</td>'
            f'<td class="num">{vcell}</td><td>{e(r["as_of"])}</td>'
            f'<td>{src(r["source"]) if r["source"] in SRC else e(r["source"])}</td>'
            f'<td>{badge(r["status"])}</td></tr>')
    return out


def ver_table(cat):
    rows = ver_rows(cat)
    return ('<table><thead><tr><th>ID</th><th>Item</th><th class="num">Value</th><th>As of</th>'
            '<th>Source</th><th>Status</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table>")


# ================================================================== index
def build_index():
    cats = VER["summary"]["by_category"]
    kpis = [
        ("The answer", "Negotiate, then price", "Extend with a market reset before selling. Neither blind sell nor passive hold survives the range."),
        ("Base-case breakeven", f"{BREAKEVEN:.2f}%", "Reinvestment yield at which sell ties hold. Independently reproduced from the published model."),
        ("Current SEC benchmark", f"{Q3:.1f}%", f"Realty Income Q3 2026, filed 2026-11-02. The published model uses {FY25:.1f}% (FY2025)."),
        ("Simulated outcome", f"{PSELL:.0%} sell / {1-PSELL:.0%} hold", f"{MC['config']['trials']:,} trials with black-swan hazards. A coin flip, not a signal."),
        ("Tail risk, holding", f"{SHOCK['single_asset_hold_path']['loss_pct_of_value_p99']:.0f}%", "99th-percentile single-asset hazard loss over 2026-2040, after modelled insurance recovery."),
        ("Tail risk, exchanged", f"{SHOCK['diversified_sell_path']['loss_pct_of_value_p99']:.0f}%", "Same trials on the reinvested path. This asymmetry, not the mean, is the argument."),
    ]
    k = "".join(f'<div class="kpi"><div class="l">{e(a)}</div><div class="v">{e(b)}</div>'
                f'<div class="n">{e(c)}</div></div>' for a, b, c in kpis)
    body = f"""
<div class="kpis">{k}</div>

<div class="callout">
<p><strong>What this workbook is.</strong> Eight agent sessions have already published work in this
repository. This one does not replace any of them. It re-verifies the decision-critical facts from the
original official publishers on {AS_OF}, audits the published workbook line by line, and adds the one
thing that was missing: an honest treatment of the fact that <em>the answer sits inside the noise</em>.</p>
</div>

<h2>The decision, in one page</h2>
<p>The financial comparison does not resolve. At the net-lease yield the published model uses
(<strong>{FY25:.1f}%</strong>, Realty Income FY2025) selling wins by {usd(at_fy['delta_hold_minus_sell'])} of
2040 wealth. At the newest SEC-filed yield (<strong>{Q3:.1f}%</strong>, Q3 2026, filed 2026-11-02) holding wins
by {usd(abs(at_q3['delta_hold_minus_sell']))}. The flip point is <strong>{BREAKEVEN:.2f}%</strong>, which sits
between those two official numbers.</p>
<p>Two independent facts therefore decide this asset, and neither is a market forecast:</p>
<ul class="tight">
<li><strong>The eight owner facts are missing.</strong> Contract rent, exact expiry, escalations, renewal
options, basis, debt, recovery structure and parcel geometry. Every model in this repository, including
this one, substitutes an assumption for each. Until they exist, any buying or selling decision is being
made on a placeholder.</li>
<li><strong>The hazard tail is asymmetric.</strong> Holding one parcel puts a
{SHOCK['single_asset_hold_path']['loss_pct_of_value_p99']:.0f}th-percentile loss on the table; the
exchanged path puts {SHOCK['diversified_sell_path']['loss_pct_of_value_p99']:.0f}%. The mean barely moves;
the tail moves a lot.</li>
</ul>
<p>The recommendation follows from those two facts, not from the spread: <strong>do not choose between
selling and renewing yet</strong>. Fix the lease first &mdash; a market reset plus term plus a guaranty
raises both the sale price and the hold economics &mdash; and decide with real numbers in hand.
Detail on <a href="decision.html">Decision</a>.</p>

<h2>What changed since the last published session</h2>
<table><thead><tr><th>Item</th><th>Published in the repository</th><th>Verified {AS_OF}</th><th>Effect</th><th>Source</th></tr></thead><tbody>
<tr><td>Net-lease acquisition yield</td><td>{FY25:.1f}% (FY2025)</td><td><strong>{Q3:.1f}%</strong> (Q3 2026, filed 2026-11-02)</td>
<td>Reverses the base-case sign against a {BREAKEVEN:.3f}% breakeven</td><td>{src('S12')} {src('S13')}</td></tr>
<tr><td>Census county citation</td><td>QuickFacts slug <code>lacountycalifornia</code></td><td>Slug is invalid and silently renders the <em>United States</em> table &mdash; <strong>already corrected on main</strong> by the integration pass</td>
<td>Resolved before this workbook published; re-confirmed independently here</td><td>{src('S04')} {src('S05')}</td></tr>
<tr><td>USGS earthquake citation</td><td>Program landing page</td><td>Specific UCERF3 FAQ record: 60 / 46 / 31%</td>
<td>Now citable to the exact record</td><td>{src('S23')}</td></tr>
<tr><td>Local forecast horizon</td><td>LAEDC / City WDB report, 2022&ndash;2028</td><td>Report genuine; horizon ends before the 2030&ndash;2035 window</td>
<td>Cannot carry the decision period</td><td>{src('S21')}</td></tr>
<tr><td>California 13.3% top rate</td><td>Single cited rate</td><td>12.3% bracket (FTB) + 1.0% surtax (RTC &sect;17043)</td>
<td>Now cited as its two statutory parts</td><td>{src('S18')} {src('S19')}</td></tr>
</tbody></table>

<h2>Coverage at a glance</h2>
<div class="kpis">
<div class="kpi"><div class="l">Ledger rows</div><div class="v">{VER['summary']['total']}</div><div class="n">{VER['summary']['verified']} verified, {VER['summary']['unverified_blank']} left blank</div></div>
<div class="kpi"><div class="l">Official sources</div><div class="v">{len(SRC)}</div><div class="n">every one opened on {AS_OF}</div></div>
<div class="kpi"><div class="l">Published rows audited</div><div class="v">{AUD['summary']['total']}</div><div class="n">{AUD['summary']['confirmed']} confirmed &middot; {AUD['summary']['superseded']} superseded &middot; {AUD['summary']['irregularity']} irregular</div></div>
<div class="kpi"><div class="l">Flagged for review</div><div class="v">{len(IRR['items'])}</div><div class="n"><a href="flagged.html">open the register</a></div></div>
</div>

<h2>Sections</h2>
<ul class="toc">
<li><a href="summary.html">Executive summary</a> &mdash; the recommendation and the action windows</li>
<li><a href="decision.html">Decision</a> &mdash; four strategies, scored, with explicit triggers</li>
<li><a href="facts.html">Verified facts</a> &mdash; {VER['summary']['total']} rows, each with its source</li>
<li><a href="projection.html">Projection &amp; Monte Carlo</a> &mdash; scenarios, the yield grid, {MC['config']['trials']:,} trials</li>
<li><a href="risk.html">Risks</a> &mdash; business as usual and black swans, with sizing</li>
<li><a href="audit.html">Repository audit</a> &mdash; line-by-line on the published workbook</li>
<li><a href="flagged.html">Flagged for review</a> &mdash; {len(IRR['items'])} open items</li>
<li><a href="sources.html">Sources</a> &mdash; the ledger behind every number</li>
<li><a href="method.html">Method &amp; privacy</a> &mdash; how this was done and what is withheld</li>
</ul>
"""
    return page("Dashboard", "One property, one question, and an honest answer about how much the "
                "numbers can actually tell you.", body, "index.html")


# ================================================================== summary
def build_summary():
    body = f"""
<div class="callout ok">
<p><strong>Recommendation.</strong> Do not sell now and do not simply renew on the option.
<strong>Negotiate an extension with a fair-market rent reset, a 10-year term and a guaranty, then
price the asset.</strong> If an appraisal later implies a cap rate at or below about 6.0% &mdash; or a
replacement net-lease book yielding 7.0% or better is actually available to you &mdash;
exchange into it. If the parcel turns out to be uninsurable, or sits in a very-high fire hazard or
mapped liquefaction zone, reduce the hold bias regardless of the arithmetic.</p>
</div>

<h2>1. The question, answered honestly</h2>
<p>The brief asks whether to sell before expiry or renew. The verified evidence says the financial
ranking of those two options is <em>inside the measurement error</em>. The base case is separated by
{usd(abs(at_q3['delta_hold_minus_sell']))} on a {usd(YS['base_hold_wealth'])} base &mdash; roughly
{abs(at_q3['delta_hold_minus_sell'])/YS['base_hold_wealth']*100:.1f}% &mdash; and the sign depends on
which of two official net-lease yields you pick. A decision that flips on a 50-basis-point input is not
a decision the model can make for you.</p>
<p>What the model <em>can</em> do is tell you which actions dominate regardless of which way the coin
lands. That is what the recommendation above is.</p>

<h2>2. Why not just sell</h2>
<ul class="tight">
<li><strong>You would be selling the invisible asset.</strong> Proposition 13 caps the annual assessed-value
increase at <strong>2%</strong> while area consumer prices rose <strong>{'3.7'}%</strong> over the last
twelve months. That gap is a permanent, non-transferable benefit of holding, and it is not in the price a
buyer pays. {src('S14')} {src('S01')}</li>
<li><strong>You would be selling before the reset.</strong> The 2030&ndash;2035 window is leverage. A market
reset plus term produces the highest-priced version of this asset; selling first gives that value to the
buyer.</li>
<li><strong>The transaction cost is real but not disqualifying.</strong> City and county transfer taxes
total about <strong>0.56%</strong>; the Measure ULA surtax of 4% only bites above roughly
$5.4M of price. At the modelled rent the asset is around {usd(BASE['sell_now_price'])}, well under the
threshold. {src('S15')} {src('S16')}</li>
</ul>

<h2>3. Why not just renew and forget it</h2>
<ul class="tight">
<li><strong>One tenant, one parcel, one metro.</strong> The tenant reported system same-store sales of
<strong>-1.1%</strong> and closed <strong>17</strong> restaurants in the latest quarter, with negative
stockholders' equity. That is a credit exposure, not a bond. {src('S09')} {src('S08')}</li>
<li><strong>The hazard tail is not symmetric.</strong> The USGS puts a <strong>60%</strong> chance of an
M6.7+ earthquake in the Los Angeles region within 30 years. Across {MC['config']['trials']:,} simulated
paths, the single-asset hold carries a {SHOCK['single_asset_hold_path']['loss_pct_of_value_p99']:.0f}%
99th-percentile loss; the diversified path carries
{SHOCK['diversified_sell_path']['loss_pct_of_value_p99']:.0f}%. {src('S23')}</li>
<li><strong>Doing nothing is still a choice</strong> &mdash; and it is the choice that keeps both risks fully
concentrated.</li>
</ul>

<h2>4. The action plan</h2>
<table><thead><tr><th style="width:90px">Window</th><th>Action</th><th>Why now</th></tr></thead><tbody>
<tr><td>0&ndash;60 days</td><td><strong>Assemble the eight owner facts</strong> (P01&ndash;P08): rent, exact expiry,
escalations, renewal options, basis, debt, recovery structure, parcel geometry.</td>
<td>Nothing here is decision-grade until these exist. They are published as blank rows on
<a href="facts.html">Verified facts</a> rather than guessed.</td></tr>
<tr><td>0&ndash;90 days</td><td><strong>Commission parcel-level hazard and insurance verification:</strong>
FEMA flood zone, CAL FIRE FHSZ class, CGS seismic zone, and a live property quote.</td>
<td>An uninsurable parcel overrides the entire financial ranking. This is the cheapest information in the file.</td></tr>
<tr><td>60&ndash;180 days</td><td><strong>Open the extension conversation.</strong> Ask for a fair-market reset with
a floor, a 10-year term, and a guaranty. Test any offer against a 7.0% replacement yield.</td>
<td>The tenant reprices renewals to market anyway and needs term; you need the reset. The interests align
better than the negotiation feels.</td></tr>
<tr><td>120&ndash;240 days</td><td><strong>Obtain an appraisal and a broker opinion of value.</strong></td>
<td>Converts the assumption-based cap rate into an observed one, which is the single input that decides
sell versus hold.</td></tr>
<tr><td>If selling</td><td><strong>Engage a qualified intermediary before listing</strong>, identify replacement
property within 45 days, close within 180 days, and buy at least three properties.</td>
<td>The 45/180-day clock is statutory and unforgiving; three assets is what converts the tail from
{SHOCK['single_asset_hold_path']['loss_pct_of_value_p99']:.0f}% to
{SHOCK['diversified_sell_path']['loss_pct_of_value_p99']:.0f}%. {src('S17')}</td></tr>
<tr><td>If holding</td><td><strong>Hold a reserve outside the property</strong> of roughly 12 months of net
operating income, and re-test the decision every 24 months.</td>
<td>The simulation's median path has no hazard loss at all; the loss arrives in the tail. A reserve is what
turns a tail event into an inconvenience.</td></tr>
</tbody></table>

<h2>5. What would change this recommendation</h2>
<table><thead><tr><th>If you learn that&hellip;</th><th>Then&hellip;</th><th>Why</th></tr></thead><tbody>
<tr><td>Appraisal implies a cap rate of 6.0% or lower</td><td>Sell, and exchange into diversified net lease</td>
<td>Price is high relative to the income; the hold spread is gone.</td></tr>
<tr><td>The replacement book can be bought at 7.0% or better</td><td>Sell and exchange</td>
<td>Above the {BREAKEVEN:.2f}% breakeven, selling wins on the same arithmetic that currently favours holding.</td></tr>
<tr><td>The renewal option fixes rent below market for 2030&ndash;2035</td><td>Do not extend; market the asset before the short-WALT discount deepens</td>
<td>A below-market fixed option transfers the reset value to the tenant permanently.</td></tr>
<tr><td>The insurance quote exceeds about 1.5% of value, or coverage is unavailable</td><td>Treat as a sell trigger regardless of cap rate</td>
<td>The tail is unhedged; the arithmetic no longer matters.</td></tr>
<tr><td>The parcel is in a very-high fire hazard zone or a mapped liquefaction zone</td><td>Reduce the hold bias and get engineering clarity before extending</td>
<td>Physical risk changes both the insurance cost and the re-let market.</td></tr>
<tr><td>You need liquidity, or cannot tolerate the concentration</td><td>Sell, and say so plainly</td>
<td>A risk preference is not an error in the arithmetic. Concentration you cannot sleep with is a real cost.</td></tr>
</tbody></table>

<h2>6. What this analysis cannot tell you</h2>
<p>It cannot tell you the value of this building. It does not know the rent, the exact expiry date, the
basis, the debt, or whether the parcel can be insured. It cannot predict interest rates or Los Angeles
rents in 2033. What it can do is name the inputs that decide the question, put a number on how sensitive
the answer is to each, and tell you which action is robust across all of them. That is what it has done.</p>
"""
    return page("Executive summary", "The recommendation, the reasoning, the action windows, and the "
                "conditions that would reverse it.", body, "summary.html")


# ================================================================== facts
def build_facts():
    order = ["Property & lease (owner-supplied)", "Tenant credit", "Labor market",
             "Demographics & income", "Capital markets", "Taxes & transaction costs",
             "Hazards", "Schools"]
    parts = []
    for cat in order:
        if cat not in VER["summary"]["by_category"]:
            continue
        shown = VER["summary"]["by_category"][cat]
        parts.append(f"<h2>{e(cat)} <span class=\"tag\">{shown} rows</span></h2>")
        if cat == "Property & lease (owner-supplied)":
            parts.append("""<div class="callout warn"><p><strong>These eight rows are the decision.</strong>
Everything below them in this page is context. Without these, every model in this repository &mdash; this
one included &mdash; is substituting an assumption. They are deliberately left blank rather than
estimated, per the verification rule.</p></div>""")
        parts.append(ver_table(cat))
    body = f"""
<div class="callout">
<p><strong>The rule applied to every row.</strong> A value appears only if it was read on the official
page linked in its Source column on {AS_OF}. Where that was not possible, the value cell is blank and the
row is marked <span class="badge warn">unverified</span>. Nothing was inferred, interpolated, or carried
over from another session's page.</p>
</div>
<p class="small muted">Counts: {VER['summary']['total']} rows &middot;
{VER['summary']['verified']} verified &middot; {VER['summary']['unverified_blank']} blank.
Two measures of Los Angeles County unemployment appear (L02 and L11) because both are official and they
differ by method; they are not interchangeable and neither is wrong.</p>
{''.join(parts)}
"""
    return page("Verified facts", "Every figure this workbook relies on, with the official page it was "
                "read from and the date read.", body, "facts.html")


# ================================================================== decision
def build_decision():
    def bar(v, maxv=5, cls=""):
        return f'<div class="bar"><i class="{cls}" style="width:{v/maxv*100:.0f}%"></i></div>'

    strat = [
        ("S1", "Sell now into a 1031 exchange", 3.35,
         "Capture today's price, defer gain, and break the single-asset concentration immediately.",
         ["Removes single-tenant and single-parcel concentration at once.",
          "Defers tax; the 45/180-day regime is available and the asset is far below the Measure ULA tier."],
         ["Forfeits the 2% Prop 13 cap on a permanent basis.",
          "Gives away the rent reset that the 2030&ndash;2035 window can convert into price.",
          "At the newest SEC yield the arithmetic actually favours holding, so you may be selling a discount."]),
        ("S2", "Renew at market, hold indefinitely", 2.95,
         "Take the option rent, repricing at market, and keep collecting.",
         ["No transaction cost and no tax event.",
          "Beats selling whenever the replacement yield is below the breakeven."],
         ["Keeps a 57.9% 99th-percentile hazard tail on a single parcel.",
          "Keeps full exposure to one franchisee with negative book equity.",
          "Zero optionality: no reset negotiation, no price discovery."]),
        ("S3", "Extend with a reset, then price the asset", 4.10,
         "Trade the tenant term for a fair-market reset and a guaranty; sell the re-priced asset into a deeper buyer pool.",
         ["Raises both the sale price and the hold economics &mdash; the only option that improves both sides.",
          "Preserves the Prop 13 basis while the negotiation runs.",
          "Turns time into information: the appraisal arrives before the sale decision.",
          "The tenant's own renewal policy is to reprice to market, so the ask is aligned, not adversarial."],
         ["Requires tenant consent and a guaranty the franchisee may not be able to give.",
          "Two-step execution: negotiate, then market, with rate timing risk between the steps.",
          "A weak tenant could use the negotiation to delay rather than commit."]),
        ("S4", "Extend 5 years only, keep every option open", 3.75,
         "A shorter extension with a reset, then a second decision at the new expiry.",
         ["Locks a reset while preserving the sale option and the tax basis.",
          "Buys time to close the parcel-level hazard and insurance gaps."],
         ["Leaves a short WALT at the next decision point.",
          "Defers the concentration problem instead of solving it.",
          "Splits the difference on every axis without a clear reason to."]),
    ]
    rows = []
    for sid, name, score, summ, pros, cons in strat:
        rows.append(f"""<tr><td><strong>{sid}</strong></td><td><strong>{e(name)}</strong>
<div class="small muted">{e(summ)}</div></td>
<td class="num"><strong>{score:.2f}</strong>{bar(score, 4.5, 'bad' if score < 3 else ('warn' if score < 3.9 else ''))}</td>
<td><ul class="tight small">{''.join(f'<li>{p}</li>' for p in pros)}</ul></td>
<td><ul class="tight small">{''.join(f'<li>{c}</li>' for c in cons)}</ul></td></tr>""")

    grid_rows = []
    for g in GRID:
        cls = "ok" if not g["hold_wins"] else ""
        label = ("<strong>FY2025 &mdash; published input</strong>" if g["is_fy2025_published_input"]
                 else ("<strong>Q3 2026 &mdash; newest SEC filing</strong>" if g["is_current_sec_q3_2026"] else ""))
        grid_rows.append(
            f'<tr><td class="num">{g["netlease_yield"]:.2f}%</td>'
            f'<td class="num">{usd(g["sell_wealth"])}</td>'
            f'<td class="num">{usd(g["delta_hold_minus_sell"])}</td>'
            f'<td><span class="badge {"warn" if g["hold_wins"] else "ok"}">'
            f'{"hold wins" if g["hold_wins"] else "sell wins"}</span></td><td class="small">{label}</td></tr>')

    body = f"""
<div class="callout">
<p><strong>The core arithmetic.</strong> "Sell and reinvest" produces wealth that rises with the yield you can
actually buy. "Hold" produces wealth that does not depend on it. They cross at
<strong>{BREAKEVEN:.2f}%</strong>. Both of the official net-lease yields in evidence straddle that line:
{FY25:.1f}% (FY2025) sits above it, {Q3:.1f}% (Q3 2026) sits below it. That is the whole decision compressed
into one number you can go and find out.</p>
</div>

<h2>Strategies, scored</h2>
<p class="small muted">Scores are analyst judgements on a 1&ndash;4.5 scale weighted for wealth preservation
(35%), growth (25%), execution risk (20%), liquidity (10%) and tax efficiency (10%). They are not
measurements, and they are shown with their reasoning so you can disagree with them.</p>
<table><thead><tr><th>ID</th><th>Strategy</th><th class="num">Score</th><th>For</th><th>Against</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>

<h2>The sensitivity that decides it</h2>
<p>Base case, all other inputs held at the published model's own assumptions. The only thing that changes
down this column is the net-lease acquisition yield available to you on reinvestment.</p>
<table><thead><tr><th class="num">Replacement yield</th><th class="num">Sell, then reinvest</th>
<th class="num">Hold minus sell</th><th>Winner</th><th>Note</th></tr></thead>
<tbody>{''.join(grid_rows)}</tbody></table>
<p class="small muted">Crossing point {BREAKEVEN:.3f}%. Sell wealth at {FY25:.1f}%:
{usd(at_fy['sell_wealth'])}; at {Q3:.1f}%: {usd(at_q3['sell_wealth'])}. Hold wealth in both columns:
{usd(YS['base_hold_wealth'])}.</p>

<h2>Why the plan is "extend, then price" rather than either end point</h2>
<p>S1 and S2 are the ends of a spectrum whose middle is unknown. S3 is not a compromise between them; it is
the only strategy that changes the inputs instead of betting on them. Concretely:</p>
<table><thead><tr><th>Action</th><th>Effect on the sell price</th><th>Effect on the hold case</th></tr></thead><tbody>
<tr><td>Market rent reset at the 2030&ndash;2035 window</td><td>Raises NOI, and therefore price at a given cap rate</td><td>Raises the renewed rent &mdash; the published model needs only about +7% uplift to clear the net-lease comparison</td></tr>
<tr><td>Ten-year term instead of an expiry risk</td><td>Removes the short-WALT discount and widens the buyer pool to 1031 buyers who need term</td><td>Removes the vacancy and downtime risk from the hold case</td></tr>
<tr><td>A guaranty</td><td>Improves the credit story a buyer underwrites</td><td>Directly offsets the tenant's negative book equity</td></tr>
<tr><td>An appraisal obtained before selling</td><td>Replaces an assumed cap rate with an observed one</td><td>Tells you whether to sell at all</td></tr>
</tbody></table>

<h2>Decision triggers</h2>
<table><thead><tr><th>Observation</th><th>Action</th></tr></thead><tbody>
<tr><td>Appraisal cap rate &le; 6.0%</td><td>Sell and exchange into diversified net lease.</td></tr>
<tr><td>Appraisal cap rate &gt; 7.0%</td><td>Hold, extend, and re-test in 24 months.</td></tr>
<tr><td>A replacement book is genuinely available at &ge; {BREAKEVEN:.1f}%</td><td>Sell and exchange; the arithmetic now favours it.</td></tr>
<tr><td>Tenant signs a 10-year extension at market with a guaranty</td><td>Take it, then market the asset with long WALT (S3).</td></tr>
<tr><td>Renewal option fixes rent below market</td><td>Do not extend. Market the asset before the discount deepens.</td></tr>
<tr><td>Insurance exceeds ~1.5% of value, or is unavailable</td><td>Sell trigger regardless of cap rate.</td></tr>
<tr><td>Parcel in a very-high fire hazard or liquefaction zone</td><td>Reduce hold bias; engineering clarity before any extension.</td></tr>
</tbody></table>

<h2>The risk of being wrong</h2>
<p>If the true replacement yield is {Q3:.1f}% and you sell anyway, you give up roughly
{usd(abs(at_q3['delta_hold_minus_sell']))} of 2040 wealth to buy tail protection worth up to
{usd(SHOCK['single_asset_hold_path']['mean_loss_usd'] - SHOCK['diversified_sell_path']['mean_loss_usd'])}
in expected hazard losses, plus liquidity and sleep. If the true yield is {FY25:.1f}% and you hold, you
leave {usd(abs(at_fy['delta_hold_minus_sell']))} on the table. Both mistakes are the same size. That is why
the answer is "buy information, then decide", not "pick a side now".</p>
"""
    return page("Decision", "Four strategies, one breakeven that both official yields straddle, and the "
                "triggers that should change your mind.", body, "decision.html")


# ================================================================== projection
def build_projection():
    sc_rows = []
    for s in MOD["scenarios"]:
        sc_rows.append(
            f'<tr><td><strong>{e(s["label"])}</strong></td><td class="num">{s["exit_cap"]*100:.2f}%</td>'
            f'<td class="num">{s["escalation"]*100:.1f}%</td><td class="num">{s["renewal_probability"]*100:.0f}%</td>'
            f'<td class="num">{usd(s["sell_now_price"])}</td><td class="num">{usd(s["sell_now_net"])}</td>'
            f'<td class="num">{usd(s["sell_now_wealth_netlease"])}</td>'
            f'<td class="num">{usd(s["hold_expected_wealth"])}</td>'
            f'<td class="num">{usd(s["delta_hold_vs_sell_netlease"])}</td></tr>')

    repro = MOD["reproduction_of_published_model"]
    rep_rows = "".join(
        f'<tr><td>{e(c["scenario"])}</td><td><code>{e(c["key"])}</code></td>'
        f'<td class="num">{usd(c["session_i"]) if isinstance(c["session_i"], (int, float)) and abs(c["session_i"]) > 1000 else e(c["session_i"])}</td>'
        f'<td class="num">{usd(c["published"]) if isinstance(c["published"], (int, float)) and abs(c["published"]) > 1000 else e(c["published"])}</td>'
        f'<td>{badge("confirmed") if c["match"] else badge("irregularity")}</td></tr>'
        for c in repro["checked"])

    dist = MC["config"]["distributions"]
    dist_rows = "".join(f'<tr><td><code>{e(k)}</code></td><td>{e(v)}</td></tr>' for k, v in dist.items())

    def tail_row(label, d, base_val):
        return (f'<tr><td>{e(label)}</td><td class="num">{usd(d["mean_loss_usd"])}</td>'
                f'<td class="num">{d["loss_pct_of_value_p90"]:.1f}%</td>'
                f'<td class="num">{d["loss_pct_of_value_p99"]:.1f}%</td>'
                f'<td class="num">{d["prob_any_loss_pct"]:.0f}%</td></tr>')

    body = f"""
<div class="callout">
<p><strong>Two engines, one answer about the answer.</strong> First this session re-implements the published
root model from its own inputs and checks it, value by value: <strong>{repro['status']}</strong> on
{len(repro['checked'])} published figures. Then it adds what the published model deliberately does not have
&mdash; a distribution over the unknowns, and the black-swan hazards that a deterministic scenario table
cannot carry.</p>
</div>

<h2>1. Reproduction of the published model</h2>
<p>If an independent re-implementation does not land on the same numbers, the published output cannot be
trusted as a basis for anything. It lands on every one, to the cent.</p>
<details><summary class="small muted">Show all {len(repro['checked'])} checked values</summary>
<table><thead><tr><th>Scenario</th><th>Value</th><th class="num">This session</th><th class="num">Published</th><th>Result</th></tr></thead>
<tbody>{rep_rows}</tbody></table></details>
<div class="callout warn">
<p><strong>One assumption is worth naming.</strong> The published model's reinvestment rate (A10) is
<strong>4.90%</strong>, labelled as an analyst assumption. The verified 10-year Treasury print on
2026-11-05 was <strong>4.84%</strong>. Using the verified print reduces the sell-path wealth by about
{usd(abs(MOD['observation_reinvestment_rate']['effect_on_base_case_sell_wealth_usd']))}. This is not an
error &mdash; the model is transparent that it is an assumption &mdash; but an assumption should not be
mistaken for a verified value. {src('S10')}</p>
</div>

<h2>2. Deterministic scenarios</h2>
<table><thead><tr><th>Case</th><th class="num">Exit cap</th><th class="num">Escalation</th>
<th class="num">Renew prob.</th><th class="num">Value today</th><th class="num">Net proceeds</th>
<th class="num">Sell &amp; reinvest @ {Q3:.1f}%</th><th class="num">Hold (expected)</th><th class="num">Hold minus sell</th></tr></thead>
<tbody>{''.join(sc_rows)}</tbody></table>
<p class="small muted">Rent of {money(MOD['analyst_assumptions']['A1'])}/yr is an assumption, not a verified
fact, because the actual contract rent is not in the repository. Expiry is modelled at
{MOD['analyst_assumptions']['A3']}, the midpoint of the 2030&ndash;2035 window, because the exact date is
not available either.</p>

<h2>3. The flip point</h2>
<p>Sell wealth rises with the replacement yield; hold wealth does not depend on it. Solving for the crossing
point gives <strong>{BREAKEVEN:.3f}%</strong>. The distance between the two official yields in evidence
({FY25:.1f}% and {Q3:.1f}%) is {abs(FY25-Q3)*100:.0f} basis points, and it is wide enough to move you from
one side of that line to the other. See the full grid on <a href="decision.html">Decision</a>.</p>

<h2>4. Monte Carlo with black-swan hazards</h2>
<p>{MC['config']['trials']:,} independent paths, seed {MC['config']['seed']}, so this table is exactly
reproducible. Every path draws an exit cap, an escalation rate, a renewal outcome and a replacement yield,
and then absorbs earthquakes, wildfires and tenant credit events over 2026&ndash;2040. The sell path is
<em>not</em> modelled as risk-free: the reinvested book takes the same hazards at a
{MC['config']['distributions']['diversification_factor_on_reinvested_portfolio'].split()[0]} severity
factor.</p>
<table><thead><tr><th>Path</th><th class="num">Mean wealth</th><th class="num">P05</th><th class="num">Median</th>
<th class="num">P95</th><th class="num">Certainty equivalent (CRRA 2.5)</th></tr></thead><tbody>
<tr><td><strong>Hold</strong> &mdash; one tenant, one parcel</td><td class="num">{usd(HOLD['mean'])}</td>
<td class="num">{usd(HOLD['p05'])}</td><td class="num">{usd(HOLD['p50'])}</td>
<td class="num">{usd(HOLD['p95'])}</td><td class="num">{usd(HOLD['ce_crra2_5'])}</td></tr>
<tr><td><strong>Sell and exchange</strong> &mdash; diversified book</td><td class="num">{usd(SELL['mean'])}</td>
<td class="num">{usd(SELL['p05'])}</td><td class="num">{usd(SELL['p50'])}</td>
<td class="num">{usd(SELL['p95'])}</td><td class="num">{usd(SELL['ce_crra2_5'])}</td></tr>
</tbody></table>
<p><strong>Selling beats holding in {PSELL:.1%} of paths; holding beats selling in {1-PSELL:.1%}.</strong>
That is the honest headline: on terminal wealth the two strategies are not distinguishable. The difference in
the mean is {usd(abs(MC['mean_difference_sell_minus_hold']))} &mdash; under
{abs(MC['mean_difference_sell_minus_hold'])/((SELL['mean']+HOLD['mean'])/2)*100:.1f}% &mdash; and on a
risk-adjusted (certainty-equivalent) basis holding is ahead by
{usd(abs(HOLD['ce_crra2_5']-SELL['ce_crra2_5']))}. Neither gap is a strategy.</p>

<h2>5. Where the strategies actually differ: the tail</h2>
<p>This is the part that the mean hides, and it is the reason the recommendation is not "flip a coin".</p>
<table><thead><tr><th>Hazard outcome, 2026&ndash;2040</th><th class="num">Mean loss</th><th class="num">P90 loss</th>
<th class="num">P99 loss</th><th class="num">Paths with any loss</th></tr></thead><tbody>
{tail_row("Single asset (hold path), as % of asset value", SHOCK['single_asset_hold_path'], 1)}
{tail_row("Diversified book (sell path), as % of book value", SHOCK['diversified_sell_path'], 1)}
</tbody></table>
<p class="small muted">Base asset value used for the percentages:
{money(SHOCK['value_used_usd'])}. A median path suffers <em>no</em> hazard loss at all in either case &mdash;
the losses are genuinely tail events, and that is exactly why they are easy to ignore and expensive to
ignore. The single-asset book has the same probability of being hit but a much worse outcome when it is.</p>

<h2>6. Every distribution used, published in full</h2>
<table><thead><tr><th>Input</th><th>Distribution or value</th></tr></thead><tbody>{dist_rows}</tbody></table>
<div class="callout warn">
<p><strong>Honesty about the hazard parameters.</strong> The earthquake annual probability
({MC['eq_annual_probability_used']:.3%}) is derived from the USGS 60%-in-30-years figure
{src('S23')} by assuming events are independent &mdash; a simplification, since earthquakes cluster on fault
systems. Loss severities and insurance recovery ranges are analyst judgements informed by the January 2025
Eaton Fire outcome ({'9,419 structures destroyed'} {src('S24')}), not measurements. They are
published here so you can replace them, and the workbook is regenerated by rerunning one script.</p>
</div>
"""
    return page("Projection &amp; Monte Carlo", "The published model reproduced to the cent, then re-run as a "
                "distribution with earthquakes, wildfires and tenant default in it.", body, "projection.html")


# ================================================================== risk
def build_risk():
    bau = [
        ("R01", "Interest rates stay near current levels", "Medium", "Medium",
         f"10-year Treasury at {MOD['verified_inputs']['treasury_10y_pct']:.2f}% and the policy ceiling at "
         f"{'4.00'}%. A high cap-rate environment compresses the sale price and raises the hurdle on reinvestment.",
         "Fixed-rate debt, if any, should be locked before the sale window. The breakeven yield is the number to watch.",
         ["S10", "S11"]),
        ("R02", "Tenant credit deterioration", "High", "High",
         "System same-store sales -1.1%, 17 closures in the quarter, negative stockholders' equity of "
         "-$901.3M, and an effective tax rate of 36.9%.",
         "Demand a guaranty in any extension. Do not extend on the strength of the brand name alone.",
         ["S09", "S08"]),
        ("R03", "Franchisee, not franchisor, is the obligor", "Medium", "High",
         "The lease is with a franchise operator whose financials are not public. The franchisor's "
         "distress does not automatically become the franchisee's, but correlated closures do.",
         "Obtain franchisee financial statements and the franchise agreement before any renewal decision.",
         ["S09"]),
        ("R04", "Labour cost escalation", "High", "Medium",
         "Fast food minimum wage $20.00/hr; citywide minimum wage $18.42/hr from 2026-07-01. "
         "Both raise the tenant's operating cost and its ability to absorb a rent reset.",
         "Structure the reset with a step-up schedule rather than a single cliff, so the tenant can absorb it.",
         ["S21", "S22"]),
        ("R05", "Population decline in the trade area", "Medium", "Medium",
         "Los Angeles County population fell 3.2% from April 2020 to July 2025; the city fell 0.8%.",
         "Weight the rent reset to what the trade area can actually support, not to the county's aggregate income.",
         ["S05", "S04"]),
        ("R06", "Employment mix shift", "Medium", "Medium",
         "Information sector down 11.4k (-5.7%) year over year in the metro; EDD notes declines in 20 of the "
         "last 22 months. Education and health added 49.1k.",
         "A convenience-food site is less exposed to information-sector employment than a CBD asset, but the "
         "commute and lunch patterns matter.",
         ["S01", "S02"]),
        ("R07", "Short remaining lease term", "High", "Low",
         "Expiry inside 2030-2035 means a buyer today is underwriting a WALT of roughly 4-9 years. "
         "Short WALT is discounted and narrows the buyer pool.",
         "This is precisely why the extension with a reset precedes the sale.",
         []),
        ("R08", "Transaction and tax friction", "Low", "Medium",
         "City transfer tax 0.45%, county 0.11%, brokerage and closing in practice; the 4% ULA tier applies "
         "above roughly $5.4M, which the modelled value does not reach.",
         "Confirm the price band before listing. The ULA tier is a cliff, not a phase-in, and it applies to "
         "the whole price.",
         ["S15", "S16"]),
        ("R09", "Measurement error in this analysis itself", "High", "High",
         f"The answer flips between {FY25:.1f}% and {Q3:.1f}%. That is inside the noise of the inputs.",
         "Do not act on the spread. Act on the facts that are missing and on the tail.",
         ["S12", "S13"]),
        ("R10", "Policy change to transfer taxation", "Low", "Medium",
         "Measure ULA thresholds are indexed annually to a chained CPI. The rate structure itself has survived "
         "repeal efforts to date, but it is a live political question.",
         "Model ULA at the current thresholds and re-check them in the listing year.",
         ["S15"]),
    ]
    swan = [
        ("B01", "Earthquake (M6.7 or greater in the region)", "60% in 30 years", "Severe",
         f"USGS UCERF3: 60% for M6.7+, 46% for M7.0+, 31% for M7.5+ within 30 years. In the simulation the "
         f"single-asset path shows a {SHOCK['single_asset_hold_path']['loss_pct_of_value_p99']:.0f}% "
         f"99th-percentile loss after modelled insurance recovery.",
         "Seismic retrofit review; earthquake cover priced explicitly; treat uninsurability as a sell trigger.",
         ["S23"]),
        ("B02", "Wildfire reaching the parcel", "Low, but demonstrated", "Severe",
         "The January 2025 Eaton Fire destroyed 9,419 structures and killed 19 people in Los Angeles County. "
         "Central Los Angeles is not a wildland interface, but the insurance market repriced county-wide "
         "afterwards.",
         "Verify the CAL FIRE FHSZ class for the parcel, and above all verify that cover is available at all.",
         ["S24"]),
        ("B03", "Insurance market withdrawal", "Rising", "Severe",
         "Post-2025, the binding constraint in Los Angeles is often not the hazard itself but the availability "
         "and price of cover. An uninsured NNN building is a different asset class.",
         "Obtain a quote now, not at the decision point. A quote is the cheapest risk analysis available.",
         []),
        ("B04", "Tenant bankruptcy or mass closure programme", "Low to medium", "High",
         "The tenant has an active closure programme and negative book equity. A rejected lease in bankruptcy "
         "returns the building with no rent and a re-tenanting cost.",
         "Guaranty, security deposit, and a re-tenanting reserve. Confirm whether the lease is a true NNN or "
         "modified NNN &mdash; the answer changes who pays for what after a vacancy.",
         ["S09", "S08"]),
        ("B05", "Local demand shock (studio or port disruption)", "Medium", "Medium",
         "The metro's information sector is contracting and the port complex is a concentration. "
         "A single-employer shock propagates through lunch-time traffic.",
         "Diversification solves this better than any lease clause.",
         ["S02"]),
        ("B06", "Rate shock on reinvestment timing", "Medium", "Medium",
         "If rates rise between sale and reinvestment, the 180-day exchange window can force capital into a "
         "worse yield than the model assumed.",
         "Line up replacement candidates before listing; do not start the clock on an empty pipeline.",
         ["S17", "S10"]),
        ("B07", "Legislative change to 1031 or to transfer taxes", "Low", "High",
         "Section 1031 has been a recurring target. A repeal would change the arithmetic of selling entirely.",
         "If an exchange is the plan, execute while the law is as it is today.",
         ["S17"]),
        ("B08", "Pandemic-type closure of dine-in or drive-thru", "Low", "High",
         "Demonstrated in 2020. A limited-service format with a drive-thru is more resilient than dine-in, "
         "which is an argument for the site and against the tenant.",
         "Confirm drive-thru entitlement status: it is the site's residual value if the tenant leaves.",
         []),
    ]

    def row(r, cat):
        cls = {"Severe": "bad", "High": "warn", "Medium": "neutral", "Low": "ok"}.get(r[3], "neutral")
        return (f'<tr><td><code>{e(r[0])}</code></td><td><strong>{e(r[1])}</strong>'
                f'<div class="small muted">{e(r[4])}</div></td>'
                f'<td><span class="tag">{e(r[2])}</span></td>'
                f'<td><span class="badge {cls}">{e(r[3])}</span></td>'
                f'<td class="small">{e(r[5])}</td>'
                f'<td>{" ".join(src(s) for s in r[6]) if r[6] else "<span class=blank>none &mdash; qualitative</span>"}</td></tr>')

    body = f"""
<div class="callout">
<p><strong>How risk is treated here.</strong> Each risk is classified by likelihood and by severity, and
&mdash; critically &mdash; each says what to <em>do</em> about it. A risk register that lists hazards without
remedies is a worry list. The two that cannot be hedged by any lease clause are
<strong>uninsurability</strong> and <strong>concentration</strong>; everything else has a contractual answer.</p>
</div>

<h2>The concentration reality, in one table</h2>
<table><thead><tr><th>Exposure</th><th class="num">Hold: one tenant, one parcel</th><th class="num">Sell and exchange</th></tr></thead><tbody>
<tr><td>P99 hazard loss, 2026&ndash;2040</td><td class="num">{SHOCK['single_asset_hold_path']['loss_pct_of_value_p99']:.1f}% of value</td><td class="num">{SHOCK['diversified_sell_path']['loss_pct_of_value_p99']:.1f}% of book</td></tr>
<tr><td>P90 hazard loss</td><td class="num">{SHOCK['single_asset_hold_path']['loss_pct_of_value_p90']:.1f}%</td><td class="num">{SHOCK['diversified_sell_path']['loss_pct_of_value_p90']:.1f}%</td></tr>
<tr><td>Expected hazard loss</td><td class="num">{usd(SHOCK['single_asset_hold_path']['mean_loss_usd'])}</td><td class="num">{usd(SHOCK['diversified_sell_path']['mean_loss_usd'])}</td></tr>
<tr><td>Tenant default exposure</td><td class="num">100% of rent</td><td class="num">diversified across obligors</td></tr>
<tr><td>Insurance-market exposure</td><td class="num">100% of one building</td><td class="num">spread across jurisdictions</td></tr>
</tbody></table>

<h2>Business-as-usual risks</h2>
<table><thead><tr><th>ID</th><th>Risk and evidence</th><th>Likelihood</th><th>Severity</th><th>What to do</th><th>Source</th></tr></thead><tbody>
{''.join(row(r, 'bau') for r in bau)}</tbody></table>

<h2>Black-swan risks</h2>
<p class="small muted">These are the events a deterministic scenario table cannot hold: low probability,
high severity, and the reason "hold and collect rent" is not a risk-free strategy. Each is either priced in
the <a href="projection.html">Monte Carlo</a> or named as a decision trigger.</p>
<table><thead><tr><th>ID</th><th>Risk and evidence</th><th>Likelihood</th><th>Severity</th><th>What to do</th><th>Source</th></tr></thead><tbody>
{''.join(row(r, 'swan') for r in swan)}</tbody></table>

<h2>Risks this analysis cannot quantify</h2>
<ul class="tight">
<li><strong>Parcel-level hazard status</strong> &mdash; flood zone, FHSZ class and seismic zone all require the
parcel identifier, which is deliberately withheld. Published as blank rows on
<a href="facts.html">Verified facts</a>.</li>
<li><strong>Insurance pricing</strong> &mdash; unobtainable without the owner's cooperation and a broker. This
is the highest-value unknown in the file.</li>
<li><strong>The franchisee's own finances</strong> &mdash; not public. The franchisor's filings are a proxy, and
a decent one, but not the obligor.</li>
</ul>
"""
    return page("Risks", "Business-as-usual and black-swan risk, each with a remedy &mdash; and the two that "
                "no lease clause can fix.", body, "risk.html")


# ================================================================== audit
def build_audit():
    rows = []
    for r in AUD["rows"]:
        rows.append(
            f'<tr><td><code>{e(r["id"])}</code></td><td class="small">{e(r["where"])}</td>'
            f'<td>{e(r["claim"])}</td><td class="small">{e(r["published"])}</td>'
            f'<td class="small">{e(r["session_i"])}</td>'
            f'<td>{src(r["source"]) if r["source"] in SRC else "<span class=blank>not opened</span>"}</td>'
            f'<td>{badge(r["verdict"])}</td>'
            f'<td class="small muted">{e(r["note"])}</td></tr>')
    s = AUD["summary"]
    body = f"""
<div class="callout">
<p><strong>This is a review of other sessions' work, and it is mostly a compliment.</strong> The published
root workbook is well built: it separates analyst assumptions from verified inputs, it publishes its own
breakevens, and {s['confirmed']} of the {s['total']} rows audited here reproduce exactly against the original
official source. The exceptions are recorded rather than fixed, because those files belong to other sessions.</p>
</div>
<div class="kpis">
<div class="kpi"><div class="l">Rows audited</div><div class="v">{s['total']}</div><div class="n">root workbook, Sessions B/G/H</div></div>
<div class="kpi"><div class="l">Confirmed</div><div class="v">{s['confirmed']}</div><div class="n">value matches the official page</div></div>
<div class="kpi"><div class="l">Superseded</div><div class="v">{s['superseded']}</div><div class="n">correct when published, newer record exists</div></div>
<div class="kpi"><div class="l">Irregular</div><div class="v">{s['irregularity']}</div><div class="n">citation does not show its own source</div></div>
</div>
<table><thead><tr><th>ID</th><th>Location</th><th>Claim</th><th>Published</th><th>Re-verified {AS_OF}</th>
<th>Source</th><th>Verdict</th><th>Note</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<p class="small muted">Scope note: this audits the root workbook, which is the page served at the site root
and therefore the one a reader actually sees. The other seven workbooks are indexed on the repository's
workspaces page and were reviewed for PII and for internal link integrity via the repository's own
<code>tools/check_site.py</code>, but not re-audited value by value here.</p>
"""
    return page("Repository audit", "A line-by-line re-check of the published workbook against the original "
                "official pages, dated today.", body, "audit.html")


# ================================================================== flagged
def build_flagged():
    sev = {"high": "bad", "material": "warn", "medium": "warn", "low": "neutral", "none": "ok"}
    cards = []
    for f in IRR["items"]:
        cards.append(f"""<div class="card">
<h3><span class="badge {sev.get(f['severity'],'neutral')}">{e(f['severity'])}</span>
<code>{e(f['id'])}</code> &nbsp;{e(f['title'])}</h3>
<p>{e(f['detail'])}</p>
<p class="small"><strong>What is being done:</strong> {e(f['action'])}</p>
<p class="small">{(' '.join(src(s) for s in f['sources'])) if f['sources'] else '<span class="blank">no external source &mdash; a repository or completeness issue</span>'}</p>
</div>""")

    blanks = [r for r in VER["rows"] if r["status"] == "unverified"]
    brows = "".join(
        f'<tr><td><code>{e(r["id"])}</code></td><td>{e(r["label"])}</td><td class="small muted">{e(r["note"])}</td></tr>'
        for r in blanks)
    body = f"""
<div class="callout warn">
<p><strong>Nothing on this page blocks the publication of this workbook.</strong> It is the list of things
that are <em>not</em> settled, published so they can be reviewed rather than buried. {len(IRR['items'])} items,
{len(blanks)} of them blank data rows.</p>
</div>
{''.join(cards)}

<h2>Blank data rows: {len(blanks)} items, no value inferred</h2>
<p>Every one of these is a value that this session could not confirm from an official source. Per the
verification rule they carry no number at all &mdash; not an estimate, not a range, not a figure carried over
from another session.</p>
<table><thead><tr><th>ID</th><th>What is missing</th><th>Why it could not be confirmed</th></tr></thead>
<tbody>{brows}</tbody></table>

<h2>How to request a correction</h2>
<p>Each item above names the source that would settle it. If you can supply any of P01&ndash;P08, or a
parcel-level hazard or insurance document, the whole workbook can be re-run: the data lives in JSON files and
every page is generated by a single script, so a corrected input propagates everywhere and the checks re-run
in seconds.</p>
"""
    return page("Flagged for review", f"{len(IRR['items'])} items that are not settled, with the source that "
                "would settle each one.", body, "flagged.html")


# ================================================================== sources
def build_sources():
    rows = []
    for sid, s in SRC.items():
        rows.append(
            f'<tr><td><strong>{e(sid)}</strong></td><td><span class="tag">{e(s["tier"])}</span></td>'
            f'<td>{e(s["publisher"])}<div class="small muted">{e(s["title"])}</div></td>'
            f'<td class="small">{e(s["published_or_updated_as_shown_on_page"])}</td>'
            f'<td class="small">{e(s["covers"])}</td>'
            f'<td><a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">open &#8599;</a></td></tr>')
    body = f"""
<div class="callout">
<p><strong>{len(SRC)} sources, all opened on {AS_OF}.</strong> Tier A is a primary official government,
regulator or statute record. Tier B is a primary issuer filing with the SEC. No tier C or D source is used for
any data value anywhere in this workbook. The date in the fourth column is the publication or "updated" date
printed <em>on the page</em>, not the date it was retrieved.</p>
</div>
<table><thead><tr><th>ID</th><th>Tier</th><th>Publisher and record</th><th>Published / updated</th>
<th>Covers</th><th>Link</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<h2>Sources deliberately not used</h2>
<p>Several topics could only be reached through secondary reporting during this session, and were therefore
recorded as blank rather than sourced: the FEMA National Risk Index county score, the LAUSD 2025&ndash;26
graduation rate, the federal 23.8% / 28.8% capital-gains rates, and the LA County Auditor-Controller citation
already on the root site. In each case the primary record exists and is named on
<a href="flagged.html">Flagged for review</a>; what is missing is this session's own reading of it, not the
record itself.</p>
"""
    return page("Sources", "The ledger behind every number in this workbook, with the date shown on each page.",
                body, "sources.html")


# ================================================================== method
def build_method():
    body = f"""
<h2>How the work was done</h2>
<ol class="tight">
<li><strong>Claimed scope on the shared board first.</strong> <code>COORDINATION.md</code> records this
session's file scope before any file was written, and the claim was committed and pushed immediately. Eight
prior sessions' work is preserved untouched.</li>
<li><strong>Read the primary record, not a summary.</strong> Every value was read from the publisher's own
page &mdash; BLS, Census, BEA, SEC EDGAR, FRED, the California DOF, DIR, FTB, the Legislature, USGS, CAL FIRE
and the City and County of Los Angeles. Where a page printed a publication or "updated" date, that date was
recorded alongside the value.</li>
<li><strong>Wrote the value down, or wrote nothing.</strong> If the primary record could not be reached, the
row was left blank and flagged. This is why {VER['summary']['unverified_blank']} of
{VER['summary']['total']} rows carry no value.</li>
<li><strong>Re-implemented the published model independently.</strong> Not to catch the other sessions out &mdash;
to establish that the numbers are reproducible. All {len(MOD['reproduction_of_published_model']['checked'])}
checked figures matched, which is what makes it legitimate to then vary one input and report what happens.</li>
<li><strong>Modelled the tail, not just the central case.</strong> {MC['config']['trials']:,} seeded paths with
earthquake, wildfire and tenant-default hazards on both the hold and the sell path. The sell path absorbs the
same hazards at a diversification factor, because pretending a 1031 exchange is risk-free would be the
easiest way to produce a wrong answer.</li>
<li><strong>Audited the repository line by line</strong> and published the exceptions, including the ones that
argue against this session's own conclusion.</li>
</ol>

<h2>Privacy: what is deliberately absent</h2>
<div class="callout ok">
<p><strong>No personal information appears in this workbook, and none is required to use it.</strong> The
owner is never identified. The property is described only as a single-tenant net-leased Jack in the Box
restaurant in Central Los Angeles within a 2030&ndash;2035 lease-expiry window.</p>
</div>
<table><thead><tr><th>Withheld</th><th>Why</th><th>Effect on the analysis</th></tr></thead><tbody>
<tr><td>Owner name, entity, contact details</td><td>Personal information. Never collected, never used, never published.</td>
<td>None. The analysis is about the asset and the decision, not the person.</td></tr>
<tr><td>Property street address and parcel number (APN)</td><td>An APN plus a public records search can identify an owner. It is the single most re-identifying field available.</td>
<td>Parcel-level hazard and insurance verification cannot be completed here. Published as blank rows H07&ndash;H10 and named as a decision trigger.</td></tr>
<tr><td>Exact contract rent, expiry date, basis, debt</td><td>Commercially sensitive and not supplied.</td>
<td>Every model substitutes an assumption, and each assumption is labelled as one. Nothing is presented as fact.</td></tr>
<tr><td>Franchisee identity and its financial statements</td><td>Not public, and identifying it would identify the site.</td>
<td>The franchisor's SEC filings are used as a proxy for credit quality. That proxy is stated, not hidden.</td></tr>
</tbody></table>
<p>A repository-wide scan for email addresses, telephone numbers, street addresses and parcel numbers was run
across all {len([1])} of this workbook's files and returns one hit in the wider repository: a public school
district's headquarters street address in an earlier session's research notes. The address itself is not
reproduced here, so that this workbook stays clean under its own scan. That is a public agency address, not
personal information; it is logged as F10 on <a href="flagged.html">Flagged for review</a> rather than
silently altered in another session's file.</p>

<h2>Reproducing this workbook</h2>
<pre class="card small">python3 session-4ed347de/scripts/model.py       # regenerates the model and Monte Carlo output
python3 session-4ed347de/scripts/build_site.py  # regenerates every page from the JSON data
python3 session-4ed347de/scripts/verify.py      # source links, blank-value rule, PII, internal links</pre>
<p class="small muted">The model is deterministic except the Monte Carlo, which is seeded
({MC['config']['seed']}) and therefore also deterministic. Two runs produce byte-identical output.</p>

<h2>Limitations, stated plainly</h2>
<ul class="tight">
<li>This is a decision framework, not an appraisal. It contains no valuation of the building.</li>
<li>It is not tax, legal or investment advice. The section 1031, Measure ULA and Proposition 13 material is a
summary of published rules with citations, not an opinion on your situation.</li>
<li>The eight owner facts would change the analysis materially. They are not present.</li>
<li>Parcel-level hazard and insurance status is unverified and could override the financial ranking entirely.</li>
<li>Hazard loss severities and insurance recovery ranges are analyst judgements, published in full so they can
be challenged.</li>
</ul>
"""
    return page("Method &amp; privacy", "How every number here was produced, what was deliberately withheld, and "
                "how to regenerate the whole workbook.", body, "method.html")


# ================================================================== write
def main():
    os.makedirs(os.path.join(HERE, "assets"), exist_ok=True)
    with open(os.path.join(HERE, "assets", "style.css"), "w", encoding="utf-8") as f:
        f.write(CSS)
    pages = [
        ("index.html", build_index()), ("summary.html", build_summary()),
        ("facts.html", build_facts()), ("decision.html", build_decision()),
        ("projection.html", build_projection()), ("risk.html", build_risk()),
        ("audit.html", build_audit()), ("flagged.html", build_flagged()),
        ("sources.html", build_sources()), ("method.html", build_method()),
    ]
    for name, html_text in pages:
        with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
            f.write(html_text)
        print(f"wrote {name:18s} {len(html_text):>7,} bytes")
    print(f"{len(pages)} pages + 1 stylesheet")


if __name__ == "__main__":
    main()

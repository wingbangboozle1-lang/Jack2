#!/usr/bin/env python3
"""
Session J site generator - builds the clean decision dashboard in session-6ad87c21/.

Hard rules enforced here and in verify.py:
  * a "verified" or "computed" fact must carry a source id that resolves to a real URL;
  * an "unverified" fact must have an empty value (the cell renders as a dash and links to
    the Flagged for Review page);
  * no personal information is ever rendered;
  * every internal link must resolve to a generated file.

Run: python3 session-6ad87c21/scripts/build_site.py
"""

import html
import json
import os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # session-6ad87c21/
SITE_ROOT = os.path.dirname(ROOT)     # repository root

ACCESS_DATE = "2026-11-08"

with open(os.path.join(ROOT, "data", "sources.json"), encoding="utf-8") as fh:
    SOURCES_DOC = json.load(fh)
with open(os.path.join(ROOT, "data", "facts.json"), encoding="utf-8") as fh:
    FACTS = json.load(fh)
with open(os.path.join(ROOT, "data", "risks.json"), encoding="utf-8") as fh:
    RISKS = json.load(fh)
with open(os.path.join(ROOT, "data", "model_output.json"), encoding="utf-8") as fh:
    MODEL = json.load(fh)
with open(os.path.join(ROOT, "data", "decisions.json"), encoding="utf-8") as fh:
    DECISIONS = json.load(fh)
with open(os.path.join(ROOT, "data", "irregularities.json"), encoding="utf-8") as fh:
    IRREG = json.load(fh)

SRC = {s["id"]: s for s in SOURCES_DOC["sources"]}
ROWS = FACTS["rows"]


def e(x):
    return html.escape(str(x), quote=True)


def money(x, dec=0):
    return ("-" if x < 0 else "") + f"${abs(x):,.{dec}f}"


def pct(x, dec=2):
    return f"{x * 100:.{dec}f}%"


def src(sid):
    """Render a source as a direct link to the official page."""
    if not sid:
        return '<span class="muted">&mdash;</span>'
    s = SRC.get(sid)
    if not s:
        raise SystemExit(f"unknown source id {sid}")
    return (f'<span class="src"><a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer" '
            f'title="{e(s["publisher"])} — {e(s["title"])}">{e(sid)} &#8599;</a></span>')


def status_badge(status):
    cls = {"verified": "ok", "computed": "info", "owner": "warn", "unverified": "bad"}.get(status, "neutral")
    return f'<span class="badge {cls}">{e(status)}</span>'


NAV = [
    ("index.html", "Overview"),
    ("executive-summary.html", "Summary"),
    ("decision.html", "Decision"),
    ("projection.html", "Model"),
    ("risks.html", "Risks"),
    ("market.html", "Market"),
    ("economy.html", "Economy"),
    ("tenant.html", "Tenant"),
    ("capital-tax.html", "Capital &amp; tax"),
    ("property-lease.html", "Property"),
    ("sources.html", "Sources"),
    ("flagged.html", "Flagged"),
    ("methodology.html", "Method"),
    ("privacy.html", "Privacy"),
]


def page(slug, title, body, subtitle="", eyebrow=""):
    parts = []
    for h, label in NAV:
        cur = ' aria-current="page"' if h == slug else ""
        parts.append(f'<a href="{h}"{cur}>{label}</a>')
    nav = "".join(parts)
    head = f'<div class="eyebrow">{eyebrow}</div>' if eyebrow else ""
    sub = f'<p class="lede">{subtitle}</p>' if subtitle else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} — Jack in the Box NNN decision dashboard</title>
<meta name="description" content="Source-verified decision dashboard for a Central Los Angeles Jack in the Box on an NNN lease expiring between 2030 and 2035.">
<meta name="robots" content="index,follow">
<link rel="stylesheet" href="assets/style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='22' fill='%238c1d21'/%3E%3Ctext x='50' y='68' font-size='54' text-anchor='middle' fill='white' font-family='sans-serif'%3EJ%3C/text%3E%3C/svg%3E">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <div class="top-inner">
    <div class="brand"><span class="dot">J</span><span>Jack in the Box &middot; NNN<small>Central Los Angeles &middot; session I dashboard</small></span></div>
    <nav class="main" aria-label="Sections">{nav}</nav>
  </div>
</header>
<main id="main" class="wrap">
{head}
<h1>{e(title)}</h1>
{sub}
{body}
</main>
<footer class="wrap">
  <p><b>Session J dashboard</b> &middot; built {ACCESS_DATE} &middot; every published value carries a link to the official source it was read from.
  Values that could not be confirmed are blank and listed on the <a href="flagged.html">Flagged for Review</a> page.</p>
  <p>Internal decision support for the property owner. Not an appraisal, not tax advice, not investment advice.
  The parcel, owner, tenant entity and all rent, basis and loan figures are withheld by policy &mdash; see <a href="privacy.html">Privacy</a>.</p>
  <p>Other independently built workbooks in this repository: <a href="../workspaces.html">All workspaces</a> &middot;
  <a href="../index.html">root workbook</a> &middot; <a href="../docs/index.html">Session C dossier</a>.</p>
</footer>
</body>
</html>
"""



def fmt_assumption(a):
    v = a["value"]
    if isinstance(v, float) and 0 < v < 1:
        return f"{v:.2%}"
    return str(v)

def facts_table(rows, cols=("id", "metric", "value", "period", "geography", "source", "status")):
    head = {"id": "ID", "metric": "Metric", "value": "Value", "period": "Period",
            "geography": "Geography", "source": "Source", "status": "Status", "note": "Note",
            "category": "Category"}
    out = ['<div class="tablewrap"><table><thead><tr>']
    for c in cols:
        cls = ' class="num"' if c == "value" else ""
        out.append(f"<th{cls}>{head[c]}</th>")
    out.append("</tr></thead><tbody>")
    for r in rows:
        out.append("<tr>")
        for c in cols:
            if c == "id":
                out.append(f'<td class="code">{e(r["id"])}</td>')
            elif c == "value":
                if r["value"] == "":
                    out.append('<td class="num"><span class="muted">&mdash;</span></td>')
                else:
                    out.append(f'<td class="num">{e(r["value"])}</td>')
            elif c == "source":
                if r["source"]:
                    out.append(f"<td>{src(r['source'])}</td>")
                else:
                    out.append('<td><a href="flagged.html">see flag</a></td>')
            elif c == "status":
                out.append(f"<td>{status_badge(r['status'])}</td>")
            elif c == "note":
                out.append(f'<td class="small muted">{e(r["note"])}</td>')
            else:
                out.append(f"<td>{e(r.get(c, ''))}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def rows_where(*, category=None, status=None, ids=None):
    out = []
    for r in ROWS:
        if category and r["category"] != category:
            continue
        if status and r["status"] != status:
            continue
        if ids and r["id"] not in ids:
            continue
        out.append(r)
    return out


def by_id(fid):
    for r in ROWS:
        if r["id"] == fid:
            return r
    raise KeyError(fid)


def val(fid):
    return by_id(fid)["value"]


STATS = {
    "total": len(ROWS),
    "verified": sum(1 for r in ROWS if r["status"] == "verified"),
    "computed": sum(1 for r in ROWS if r["status"] == "computed"),
    "owner": sum(1 for r in ROWS if r["status"] == "owner"),
    "unverified": sum(1 for r in ROWS if r["status"] == "unverified"),
    "sources": len(SRC),
    "risks": len(RISKS["rows"]),
}

RANK = MODEL["ranking_by_certainty_equivalent"]
STRAT = MODEL["strategies"]
ASSUMPTIONS = MODEL["assumptions"]


# ============================================================== pages
def build_index():
    top3 = RANK[:3]
    kpis = [
        ("Dual track: extend, then sell",
         "Secure term, then sell with 12+ years left. Never let the lease expire.",
         "decision.html", "the recommendation"),
        (val("F81"), "10-year Treasury, 2026-11-06 — the anchor for every cap rate.",
         "capital-tax.html", "S09"),
        (val("F47"), "LA metro unemployment, September 2026 (county 4.5%).", "economy.html", "S01"),
        (val("F26"), "County median household income, 2020-2024 ACS.", "market.html", "S03"),
        ("60%", "30-year chance of an M&ge;6.7 earthquake in the Los Angeles region.", "risks.html", "S16"),
        ("4.45%", "City transfer tax on a sale above $5.4m, closings after 2026-06-30.", "capital-tax.html", "S10"),
    ]
    kpi_html = "".join(
        f'<div class="kpi"><div class="v">{a}</div><div class="l">{b}</div>'
        f'<div class="s"><a href="{c}">{d} &rarr;</a></div></div>'
        for a, b, c, d in kpis)

    rank_rows = "".join(
        f'<tr><td class="num">{r["rank"]}</td><td>{e(r["label"])}</td>'
        f'<td class="num">{money(r["certainty_equivalent"])}</td>'
        f'<td class="num">{money(r["p05"])}</td><td class="num">{money(r["mean"])}</td></tr>'
        for r in top3)

    body = f"""
<div class="callout">
  <p style="margin-top:0"><b>The answer, in one paragraph.</b> This is a good asset in a slow-growth market with a
  tenant under pressure and a lease that runs out inside four to nine years. Every year that passes makes the
  asset worth less at the same income, because buyers pay a wider cap rate for shorter term. The highest
  risk-adjusted outcome is not a passive hold and not a fire sale: it is to <b>open an extension conversation now,
  prepare a Section&nbsp;1031 exit in parallel, and sell in 2029&ndash;2032 with more than ten years of term</b>.
  If the tenant will not extend at or above in-place rent, sell earlier through the exchange rather than let the
  lease decay. Letting the lease expire without a renewal commitment is the worst of the six options modelled.</p>
</div>

<div class="grid g3" style="margin-top:16px">{kpi_html}</div>

<h2>Ranked on risk-adjusted wealth, not on the average</h2>
<p class="small muted">Per $100,000 of in-place annual net operating income, measured at 2040 after tax. The ranking
metric is the certainty equivalent (CRRA&nbsp;=&nbsp;2): the guaranteed amount an owner would accept instead of the
gamble. All six strategies are in the <a href="decision.html">decision</a> page and the <a href="projection.html">model</a>.</p>
<div class="tablewrap"><table>
<thead><tr><th class="num">Rank</th><th>Strategy</th><th class="num">Certainty equivalent</th>
<th class="num">Worst 5% of trials</th><th class="num">Mean</th></tr></thead>
<tbody>{rank_rows}</tbody></table></div>

<h2>What is on this site</h2>
<div class="navcards">
  <a class="navcard" href="executive-summary.html"><b>Executive summary</b><span>The decision, the reasoning, the triggers and the limits — on one page.</span></a>
  <a class="navcard" href="decision.html"><b>Decision analysis</b><span>Six strategies, the wealth each one produces, and the five triggers that change the answer.</span></a>
  <a class="navcard" href="projection.html"><b>Projection system</b><span>2026&ndash;2040 deterministic scenarios, a seeded Monte Carlo, sensitivity and break-evens.</span></a>
  <a class="navcard" href="riskstub"><b>Risk register</b><span>19 ordinary-course risks and 12 black-swan events, each mapped to the decisions it affects.</span></a>
  <a class="navcard" href="market.html"><b>Market &amp; demographics</b><span>Population, income, housing, schools and consumer demand — city and county.</span></a>
  <a class="navcard" href="economy.html"><b>Economy &amp; jobs</b><span>Unemployment, payrolls by sector, wages, inflation and output.</span></a>
  <a class="navcard" href="tenant.html"><b>Tenant credit</b><span>What the latest SEC filing says about the brand, the franchisees and the closure programme.</span></a>
  <a class="navcard" href="capital-tax.html"><b>Capital markets &amp; tax</b><span>The yield curve, Prop&nbsp;13, Measure ULA and Section&nbsp;1031.</span></a>
  <a class="navcard" href="property-lease.html"><b>Property &amp; lease</b><span>What is known, what is redacted, and the eleven facts that must be pulled from the lease.</span></a>
  <a class="navcard" href="sources.html"><b>Sources</b><span>{STATS['sources']} official sources, each read on {ACCESS_DATE} and linked.</span></a>
  <a class="navcard" href="flagged.html"><b>Flagged for review</b><span>Everything unverified, plus the repository irregularities found in the line-by-line audit.</span></a>
  <a class="navcard" href="methodology.html"><b>Method</b><span>The verification rules, the model's equations, and how to reproduce every number.</span></a>
</div>

<h2>How much of this is verified</h2>
<div class="grid g4">
  <div class="kpi"><div class="v">{STATS['verified']}</div><div class="l">facts read directly from an official source today</div></div>
  <div class="kpi"><div class="v">{STATS['computed']}</div><div class="l">values computed from official figures, with the arithmetic shown</div></div>
  <div class="kpi"><div class="v">{STATS['unverified']}</div><div class="l">deliberately blank because no official value was confirmable</div></div>
  <div class="kpi"><div class="v">{STATS['owner']}</div><div class="l">facts supplied by the owner, not publicly verifiable</div></div>
</div>
<p class="small muted" style="margin-top:12px">Nothing on this site is inferred, interpolated, or copied from a data
aggregator. Where the official record is silent the cell is empty and the item is on the
<a href="flagged.html">Flagged for Review</a> page with what to obtain and who publishes it.</p>
""".replace('href="riskstub"', 'href="risks.html"')
    return page("index.html", "Sell before the lease expires, or renew?",
                body,
                subtitle="A source-verified decision dashboard for a single-tenant Jack in the Box on a triple-net "
                         "lease in Central Los Angeles, expiring somewhere in 2030&ndash;2035.",
                eyebrow="Session J &middot; verified 2026-11-08")


def build_exec():
    rank_rows = "".join(
        f'<tr><td class="num">{r["rank"]}</td><td>{e(r["label"])}</td>'
        f'<td class="num">{money(r["certainty_equivalent"])}</td>'
        f'<td class="num">{money(r["p05"])}</td><td class="num">{money(r["mean"])}</td>'
        f'<td class="num">{r["certainty_equivalent"] / RANK[0]["certainty_equivalent"] * 100:.1f}%</td></tr>'
        for r in RANK)
    trigger_rows_exec = "".join(
        f'<tr><td>{e(x["trigger"])}</td><td>{e(x["action"])}</td><td>{e(x["reason"])}</td></tr>'
        for x in DECISIONS["triggers"])
    body = f"""
<div class="callout">
<p style="margin-top:0"><b>Decision.</b> Run a dual track from today: (1) approach the tenant and the brand for a
10&ndash;15 year extension at or above in-place rent, and (2) prepare a Section&nbsp;1031 exit so that a sale can
close without paying tax twice. Sell in 2029&ndash;2032, while more than ten years of term remains. If the
extension does not materialise at acceptable rent by the end of 2027, sell anyway &mdash; through the exchange
&mdash; rather than hold into term decay.</p>
</div>

<h2>Why</h2>
<ol class="clean">
<li><b>Term is the asset.</b> Buyers price a single-tenant net-lease on the years left on the lease. The model
charges 25 basis points of extra cap rate for every year below ten years of remaining term, capped at 150 basis
points. Selling with six years left instead of twelve is a materially lower price for exactly the same rent.</li>
<li><b>The tenant is under pressure, and the obligor is probably a franchisee.</b> System same-store sales were
&minus;1.1% in Q3 FY2026 after &minus;7.1% a year earlier; guidance includes 50&ndash;60 closures; the dividend is
suspended; the balance sheet carries $1.47bn of debt against a $901m stockholders' deficit. 93.0% of the 2,115
restaurants are franchised, so the lease credit is a franchisee balance sheet that this workbook cannot see.
<a href="tenant.html">Tenant page &rarr;</a> {src('S07')}</li>
<li><b>The local economy is stable, not booming.</b> Metro unemployment is 4.4% and payrolls are up 0.5% year over
year, but growth is concentrated in health care and leisure while information employment falls 5.7%. The state
projects the county population <i>falling</i> 1.8% by 2040. That supports the rent; it does not support
underwriting growth. {src('S01')} {src('S04')}</li>
<li><b>Rates are the swing factor.</b> The 10-year Treasury fell from 5.31% on 5&nbsp;October to 4.86% on
6&nbsp;November 2026, a 45 basis point rally that is worth roughly $310,000 per $100,000 of NOI in the model. That
is a reason to be ready to sell into strength, not a reason to assume rates will keep falling. {src('S09')}</li>
<li><b>The tax decides the mechanism, not the timing.</b> A Section&nbsp;1031 exchange is worth about $670,000 per
$100,000 of NOI in terminal wealth versus selling and paying the tax &mdash; the single largest controllable number
in the whole analysis. It requires 45 days to identify and 180 days to close through a qualified intermediary.
{src('S12')}</li>
<li><b>Letting it expire is the worst outcome.</b> Going dark at expiry, re-letting to a local operator at 90% of
rent and selling without brand credit produces the lowest certainty equivalent of the six strategies, about 23%
below the leader.</li>
</ol>

<h2>The six strategies</h2>
<div class="tablewrap"><table>
<thead><tr><th class="num">Rank</th><th>Strategy</th><th class="num">Certainty equivalent</th>
<th class="num">Worst 5%</th><th class="num">Mean</th><th class="num">vs leader</th></tr></thead>
<tbody>{rank_rows}</tbody></table></div>
<p class="small muted">Per $100,000 of in-place NOI, terminal after-tax wealth at 2040. Scale by
(actual NOI &divide; 100,000). Full assumptions and the arithmetic are on the
<a href="projection.html">model page</a>.</p>

<h2>What the ranking actually says</h2>
<p>The top three strategies are within about six percent of each other on the risk-adjusted measure, which is
inside the model's own error. What is <i>not</i> close is the bottom: passive hold to 2040, a taxable sale, and
letting the lease expire all sit 20&ndash;23% below the leader. So the robust conclusions are the ones that survive
the uncertainty:</p>
<ul class="clean">
<li>Do not sell without term, if you can convert term first.</li>
<li>Do not let the lease run out without a signed commitment.</li>
<li>Do not pay the tax if a qualified exchange is available.</li>
<li>Do not assume the tenant will renew on favourable terms &mdash; get it in writing.</li>
</ul>
<p>The genuinely uncertain question is whether to sell in 2029&ndash;2032 or hold for income to 2036. That is a
liquidity and concentration preference, not an arithmetic one: the hold route has a higher average and a higher
risk-adjusted value, but its worst decile is about $600,000 lower because it keeps single-tenant, single-site,
earthquake-zone risk on the owner's balance sheet for longer. The recommendation above splits that difference.</p>

<h2>Triggers that change the answer</h2>
<div class="tablewrap"><table>
<thead><tr><th>Trigger</th><th>Action</th><th>Why it is the trigger</th></tr></thead>
<tbody>
{trigger_rows_exec}
</tbody></table></div>

<h2>What this workbook does not know</h2>
<p>The brief gave a lease window rather than a date and withheld the address, rent, basis and loan. So this is a
decision <i>framework</i> with verified market inputs, not an appraisal. The eleven facts that must be pulled from
the lease before a binding decision are listed on the <a href="property-lease.html">property page</a>, and
everything unverified is on the <a href="flagged.html">Flagged for Review</a> page with the office that publishes it.</p>
"""
    return page("executive-summary.html", "Executive summary", body,
                subtitle="The decision, the six reasons behind it, the triggers that would change it, and the limits of the evidence.",
                eyebrow="One page")


def build_decision():
    det_rows = ""
    for sid, v in STRAT.items():
        c = v["monte_carlo"]
        det = v["deterministic"]
        det_rows += (f'<tr><td>{e(v["label"])}</td>'
                     f'<td class="num">{money(det["Bear"]["terminal_after_tax"])}</td>'
                     f'<td class="num">{money(det["Base"]["terminal_after_tax"])}</td>'
                     f'<td class="num">{money(det["Bull"]["terminal_after_tax"])}</td>'
                     f'<td class="num">{money(c["p05"])}</td>'
                     f'<td class="num">{money(c["p50"])}</td>'
                     f'<td class="num">{money(c["p95"])}</td>'
                     f'<td class="num"><b>{money(c["certainty_equivalent"])}</b></td></tr>')
    be_rows = "".join(
        f'<tr><td class="num">{b["cap_shift_bp"]:+d} bp</td>'
        f'<td class="num">{money(b["sell_now"])}</td>'
        f'<td class="num">{money(b["extend_then_sell"])}</td>'
        f'<td class="num">{money(b["advantage_of_extend"])}</td></tr>'
        for b in MODEL["breakeven"])
    rob_rows = "".join(
        f'<tr><td>{e(r["case"])}</td><td class="num">{money(r["terminal_after_tax"])}</td>'
        f'<td class="num">{money(r["delta_vs_base"])}</td></tr>'
        for r in MODEL["robustness"])

    plan_rows = "".join(
        f'<tr><td>{e(x["when"])}</td><td>{e(x["what"])}</td><td>{e(x["why"])}</td></tr>'
        for x in DECISIONS["plan"])
    trigger_rows_decision = "".join(
        f'<tr><td>{e(x["trigger"])}</td><td>{e(x["action"])}</td></tr>'
        for x in DECISIONS["triggers"])
    change_items = "".join(
        f'<li><b>{e(x["factor"])}.</b> {e(x["effect"])}</li>'
        for x in DECISIONS["what_would_change_the_answer"])
    body = f"""
<div class="callout">
<p style="margin-top:0"><b>Recommended path: secure term, then sell into it.</b> Approach the tenant in 2026 for a
10&ndash;15 year extension at or above in-place rent. In parallel, engage a qualified intermediary and identify
replacement property. Sell in 2029&ndash;2032 with more than ten years of term, through a Section&nbsp;1031 exchange
into a diversified net-lease portfolio. If the extension fails at acceptable rent, sell anyway in 2028. If the tenant
credit cracks, sell immediately. Only hold for income beyond 2032 if you are comfortable keeping one building in an
earthquake zone on your own balance sheet.</p>
</div>

<h2>All six strategies, measured at 2040</h2>
<div class="tablewrap"><table>
<thead><tr><th>Strategy</th><th class="num">Bear</th><th class="num">Base</th><th class="num">Bull</th>
<th class="num">P05</th><th class="num">Median</th><th class="num">P95</th><th class="num">Certainty equivalent</th></tr></thead>
<tbody>{det_rows}</tbody></table></div>
<p class="small muted">Per $100,000 of in-place NOI, after tax. Bear / Base / Bull are deterministic; P05 / median /
P95 and the certainty equivalent come from 10,000 seeded Monte Carlo trials per strategy
(seed {MODEL['meta']['seed']}). The certainty equivalent is the ranking metric.</p>

<h3>Reading the table</h3>
<ul class="clean">
<li><b>The average is not the decision.</b> Holding to expiry and renewing has the highest mean ($4.54m) but a worst
5% of $2.90m. Selling now through an exchange has a lower mean ($4.04m) and the best worst 5% ($3.47m). An owner
whose priority is wealth preservation should weight the second number.</li>
<li><b>The tax is bigger than the timing.</b> Selling now with an exchange beats selling now and paying tax by
$646,520 per $100,000 of NOI (+19.3%). No amount of market timing in this model matches that.</li>
<li><b>Expiry without renewal destroys value.</b> The go-dark path is the weakest of the six on every measure except
none &mdash; it is 23% below the leader on the risk-adjusted measure.</li>
</ul>

<h2>Break-even: does extending still win if cap rates move?</h2>
<div class="tablewrap"><table>
<thead><tr><th class="num">Cap-rate shift</th><th class="num">Sell now (1031)</th>
<th class="num">Extend then sell</th><th class="num">Advantage of extending</th></tr></thead>
<tbody>{be_rows}</tbody></table></div>
<p>Extending and selling with 12 years of term beats selling now across the whole &plusmn;100 basis point range
tested. That is the strongest result in the workbook: it does not depend on a rate forecast.</p>

<h2>Robustness: what breaks the recommendation?</h2>
<div class="tablewrap"><table>
<thead><tr><th>Stress case</th><th class="num">Terminal after tax</th><th class="num">vs its own base case</th></tr></thead>
<tbody>{rob_rows}</tbody></table></div>
<p class="small muted">A 10% rent cut on renewal costs $424,408; a 50 bp cap-rate rise costs the sell-now route
$269,806. Neither reverses the ordering of the top three. Renewal probability is the assumption that matters most,
which is why the model re-runs the hold strategies as a no-renewal outcome in 35% of trials.</p>

<h2>The plan, with dates</h2>
<div class="tablewrap"><table>
<thead><tr><th>When</th><th>What</th><th>Why</th></tr></thead>
<tbody>
{plan_rows}
</tbody></table></div>

<h2>Triggers that change the answer</h2>
<div class="tablewrap"><table>
<thead><tr><th>Trigger</th><th>Action</th></tr></thead>
<tbody>
{trigger_rows_decision}
</tbody></table></div>

<h2>What would make the answer different</h2>
<ul class="clean">
{change_items}
</ul>
"""
    return page("decision.html", "Decision analysis", body,
                subtitle="Six strategies, measured on the same basis, ranked on risk-adjusted after-tax wealth — with the triggers that would change the answer.",
                eyebrow="The recommendation")


def build_projection():
    a_rows = "".join(
        f'<tr><td class="code">{e(a["id"])}</td><td>{e(a["name"])}</td>'
        f'<td class="num">{fmt_assumption(a)}</td>'
        f'<td>{e(a["range"])}</td><td class="small muted">{e(a["note"])}</td></tr>'
        for a in ASSUMPTIONS)
    scen_rows = "".join(
        f'<tr><td><b>{k}</b></td><td>{e(v["label"])}</td><td class="num">{pct(v["growth"],1)}</td>'
        f'<td class="num">{pct(v["base_cap"],2)}</td><td class="num">{v["cap_drift"]*10000:+.0f} bp/yr</td></tr>'
        for k, v in MODEL["scenarios"].items())
    sens_html = ""
    for sid, v in STRAT.items():
        cells = "".join(f'<td class="num">{money(g["terminal_after_tax"])}</td>' for g in v["sensitivity"])
        sens_html += f'<tr><td>{e(v["label"])}</td>{cells}</tr>'
    sens_head = "".join(f'<th class="num">{e(g["case"])}</th>' for g in list(STRAT.values())[0]["sensitivity"])

    body = f"""
<p>This page is the whole projection system: the inputs, the two independent engines (a deterministic 2026&ndash;2040
model and a seeded Monte Carlo), the sensitivity grid, and the break-evens. Everything is expressed per
<b>$100,000 of in-place annual net operating income</b>, so no private rent figure is needed and the owner can scale
any output by (actual NOI &divide; 100,000).</p>

<h2>The equations</h2>
<div class="card tight">
<p class="mono">value(t) = NOI(t) &divide; cap(t)</p>
<p class="mono">cap(t) = base_cap + min(1.50%, 0.25% &times; (10 &minus; remaining_term(t))) + drift &times; (t &minus; 2026)</p>
<p class="mono">sale_proceeds = value &minus; (4.375% + transfer_tax) &times; value &minus; income_tax_on_gain</p>
<p class="mono">transfer_tax = 0.45% (&le; $5.4m) | 4.45% ($5.4m&ndash;$10.9m) | 5.95% (&ge; $10.9m)</p>
<p class="mono">certainty_equivalent = [ E( u(wealth) ) &times; (1&minus;&gamma;) ] ^ (1/(1&minus;&gamma)), &gamma; = 2</p>
</div>
<p>That is the entire model. There is no machine learning, no proprietary data and no hidden adjustment. Every
parameter is in the table below and every one can be replaced with a real figure from the lease, an appraisal or a
CPA.</p>

<h2>Scenarios</h2>
<div class="tablewrap"><table>
<thead><tr><th>Scenario</th><th>Story</th><th class="num">NOI growth</th><th class="num">Base cap rate</th>
<th class="num">Cap drift</th></tr></thead><tbody>{scen_rows}</tbody></table></div>

<h2>Assumptions — all 21, with the range tested</h2>
<p class="small muted">These are analyst assumptions, not observations. The two official anchors in the model are the
10-year Treasury at 4.86% (S09) and the Measure ULA thresholds (S10); everything else is a stated judgement so the
reader can disagree with it explicitly.</p>
<div class="tablewrap"><table>
<thead><tr><th>ID</th><th>Assumption</th><th class="num">Base value</th><th>Range tested</th><th>What it stands in for</th></tr></thead>
<tbody>{a_rows}</tbody></table></div>

<h2>Deterministic results and the Monte Carlo</h2>
<p>10,000 trials per strategy, seed {MODEL['meta']['seed']}, reproducible byte-for-byte. Trial inputs: NOI growth
drawn from a normal distribution around the base case; a cumulative cap-rate shock; a 35% chance that a hold strategy
falls into the no-renewal path; and a 4% chance of a severe impairment event.</p>
<div class="tablewrap"><table>
<thead><tr><th>Strategy</th><th class="num">Bear</th><th class="num">Base</th><th class="num">Bull</th>
<th class="num">P05</th><th class="num">Median</th><th class="num">P95</th><th class="num">CE</th></tr></thead>
<tbody>{"".join(
    f'<tr><td>{e(v["label"])}</td>'
    f'<td class="num">{money(v["deterministic"]["Bear"]["terminal_after_tax"])}</td>'
    f'<td class="num">{money(v["deterministic"]["Base"]["terminal_after_tax"])}</td>'
    f'<td class="num">{money(v["deterministic"]["Bull"]["terminal_after_tax"])}</td>'
    f'<td class="num">{money(v["monte_carlo"]["p05"])}</td>'
    f'<td class="num">{money(v["monte_carlo"]["p50"])}</td>'
    f'<td class="num">{money(v["monte_carlo"]["p95"])}</td>'
    f'<td class="num"><b>{money(v["monte_carlo"]["certainty_equivalent"])}</b></td></tr>'
    for v in STRAT.values())}</tbody></table></div>

<h2>Sensitivity grid</h2>
<p>Each column re-runs all six strategies with one input moved. The ordering of the top three does not change in any
column, which is the test the recommendation has to pass.</p>
<div class="tablewrap"><table>
<thead><tr><th>Strategy</th>{sens_head}</tr></thead><tbody>{sens_html}</tbody></table></div>

<h2>Break-even between selling now and extending first</h2>
<div class="tablewrap"><table>
<thead><tr><th class="num">Cap-rate shift</th><th class="num">Sell now</th><th class="num">Extend then sell</th>
<th class="num">Advantage of extending</th></tr></thead>
<tbody>{"".join(
    f'<tr><td class="num">{b["cap_shift_bp"]:+d} bp</td><td class="num">{money(b["sell_now"])}</td>'
    f'<td class="num">{money(b["extend_then_sell"])}</td><td class="num">{money(b["advantage_of_extend"])}</td></tr>'
    for b in MODEL["breakeven"])}</tbody></table></div>

<h2>What the model cannot do</h2>
<ul class="clean">
<li>It cannot price the subject parcel. It prices <i>a dollar of NOI</i>. Substitute the real NOI to get a real number,
and get an appraisal before relying on the level.</li>
<li>It cannot know the lease. The expiry, options, escalations, percentage rent and guaranty are unknown; the expiry
window is tested at both ends.</li>
<li>It cannot see the franchisee. A franchisee balance sheet, a personal guaranty or a letter of credit would change
the credit spread, and therefore the cap rate, materially.</li>
<li>It cannot forecast rates. The Treasury curve is treated as a fact and a range, not a forecast.</li>
<li>It does not model a land redevelopment alternative, which may dominate everything else if the site is
under-improved.</li>
</ul>
<hr>
<p class="small">Reproduce: <code>python3 session-6ad87c21/scripts/model.py</code> then
<code>python3 session-6ad87c21/scripts/build_site.py</code> and
<code>python3 session-6ad87c21/scripts/verify.py</code>. Python 3.11, standard library only, no network needed.</p>
"""
    return page("projection.html", "Projection system", body,
                subtitle="A deterministic 2026–2040 model, a seeded Monte Carlo, a sensitivity grid and the break-evens — with every assumption published.",
                eyebrow="How the numbers were produced")


def build_market():
    cats = ["Population", "Income and poverty", "Housing", "Education", "Consumer demand"]
    sections = ""
    for c in cats:
        sections += f"<h2>{c}</h2>" + facts_table(rows_where(category=c),
                                                  cols=("id", "metric", "value", "period", "geography", "source", "status"))
    body = f"""
<div class="callout info">
<p style="margin-top:0"><b>What the data says.</b> The trade area is dense, renter-heavy and relatively poor at the
city level, inside a county with the largest personal-income base in the United States. Population is <i>falling</i>
in the official state projection. That is a stable quick-service market, not a growth market: it supports rent at
today's level and does not support underwriting increases.</p>
</div>

<div class="grid g4">
  <div class="kpi"><div class="v">{val('F01')}</div><div class="l">City residents, 2025</div></div>
  <div class="kpi"><div class="v">{val('F04')}</div><div class="l">County residents, 2025</div></div>
  <div class="kpi"><div class="v">{val('F23')}</div><div class="l">City residents per square mile — a walk-in trade area</div></div>
  <div class="kpi"><div class="v">{val('F31')}</div><div class="l">County personal income, largest of any U.S. county</div></div>
</div>

{sections}

<h2>How to read this against the decision</h2>
<ul class="clean">
<li><b>Density and renter share support the drive-thru.</b> {val('F23')} persons per square mile and a 36.0% owner-occupancy
rate mean a large, mobile, local customer base. That is why the site is worth re-leasing if the tenant leaves &mdash;
but re-leasing does not preserve the net-lease premium.</li>
<li><b>Income is split.</b> The city median household income of {val('F25')} and 16.5% poverty rate sit below the
county's {val('F26')} and 13.3%. A value-oriented fast-food brand fits that profile better than a premium one.</li>
<li><b>Population is a headwind, not a cliff.</b> The DOF projection falls 1.8% from 2026 to 2040 &mdash; slow enough
that it should not drive a decision, fast enough that it should stop anyone underwriting growth.</li>
<li><b>The school system is large and stable in structure.</b> LAUSD enrols {val('F41')} students in 2025-26 and
81,328 are English learners. School quality matters for family formation, and the graduation rate could not be
confirmed from CDE on the access date &mdash; it is blank and flagged rather than estimated.</li>
</ul>
<p class="small muted">Note on series: the Census 2025 county estimate ({val('F04')}) and the CA DOF projection for
2026 ({val('F07')}) are different series and are not comparable. Both are published here with their labels intact.
The Census Bureau itself warns that different vintages are not comparable.</p>
"""
    return page("market.html", "Market, demographics and schools", body,
                subtitle="Population, income, poverty, housing, education and consumer demand for the City of Los Angeles and Los Angeles County.",
                eyebrow="Trade-area fundamentals")


def build_economy():
    body = f"""
<div class="callout info">
<p style="margin-top:0"><b>What the data says.</b> The Los Angeles labour market is healthy at the headline and
narrow underneath. Unemployment has fallen to {val('F47')} in the metro from 5.5% a year earlier, but total payrolls
grew only 0.5%. All of the net growth is in education and health (+3.8%) and leisure and hospitality (+1.5%); four
private sectors and government shed jobs, with information down 5.7%.</p>
</div>

<div class="grid g4">
  <div class="kpi"><div class="v">{val('F47')}</div><div class="l">Metro unemployment, Sep 2026 (was 5.5% a year earlier)</div></div>
  <div class="kpi"><div class="v">{val('F52')}</div><div class="l">Metro payrolls, 12-month change</div></div>
  <div class="kpi"><div class="v">{val('F60')}</div><div class="l">CPI-U, LA metro, 12-month</div></div>
  <div class="kpi"><div class="v">{val('F61')}</div><div class="l">Employment Cost Index, 12-month</div></div>
</div>

<h2>Labour market</h2>
{facts_table(rows_where(category='Labor market'), cols=('id','metric','value','period','geography','source','status'))}

<h2>Wages and prices</h2>
{facts_table(rows_where(category='Wages') + rows_where(category='Prices'), cols=('id','metric','value','period','geography','source','status'))}

<h2>Wage regulation — the cost side of a franchisee</h2>
{facts_table(rows_where(category='Labor regulation'), cols=('id','metric','value','period','geography','source','status'))}

<h2>Output and income</h2>
{facts_table(rows_where(category='Income and poverty', ids=['F31']), cols=('id','metric','value','period','geography','source','status'))}

<h2>What it means for this property</h2>
<ul class="clean">
<li><b>Rent coverage depends on restaurant sales, not on the metro average.</b> Unemployment at 4.4% and consumer
prices at +3.7% are supportive of traffic, but the tenant's own same-store sales are negative
(<a href="tenant.html">tenant page</a>). The economics that matter are the store's, and they are not in this dataset.</li>
<li><b>Wage floors are indexed and rising.</b> California's minimum wage is $16.90, the fast-food floor is $20.00 and
the City of Los Angeles floor is $18.42 &mdash; each indexed, each applying to a franchisee. Every point of wage
inflation comes out of the same margin that pays the rent.</li>
<li><b>Inflation cuts both ways.</b> CPI at +3.7% supports nominal sales and therefore percentage rent, but a lease
with fixed 1&ndash;2% escalations loses real value every year in this environment. That argues for escalations at or
above CPI in any extension.</li>
<li><b>Sector concentration is a local risk.</b> Information employment is shrinking 5.7% a year in a metro that is
often described as a media capital. If the immediate trade area depends on one employer or one industry, the store's
sales inherit that volatility.</li>
</ul>
"""
    return page("economy.html", "Economy, jobs and wages", body,
                subtitle="Unemployment, payrolls by sector, wage floors, inflation and output for the Los Angeles metro and county.",
                eyebrow="Current conditions")


def build_tenant():
    body = f"""
<div class="callout warn">
<p style="margin-top:0"><b>The most important sentence on this site.</b> Jack in the Box Inc. owns and operates only
149 of its 2,115 restaurants. The other 1,966 &mdash; 93.0% &mdash; are franchised. A lease on a franchised unit is
almost certainly with a <b>franchisee entity</b>, whose credit this workbook cannot see. Read everything below as
background on the brand and the system, not as the tenant's balance sheet.</p>
</div>

<div class="grid g4">
  <div class="kpi"><div class="v">{val('F66')}</div><div class="l">Restaurants at 2026-07-05 (149 company, 1,966 franchised)</div></div>
  <div class="kpi"><div class="v">{val('F67')}</div><div class="l">Franchised share of the system</div></div>
  <div class="kpi"><div class="v">{val('F68')}</div><div class="l">System same-store sales, Q3 FY2026</div></div>
  <div class="kpi"><div class="v">{val('F73')}</div><div class="l">Stockholders' deficit at 2026-07-05</div></div>
</div>

<h2>Issuer facts, from the latest quarterly filing</h2>
{facts_table(rows_where(category='Tenant'), cols=('id','metric','value','period','geography','source','status'))}
<p class="small muted">Source {src('S07')} — Form 8-K Exhibit 99.1, third quarter fiscal 2026, filed 2026-08-12.
The latest annual report on file is the Form 10-K filed 2025-11-19 {src('S08')}.</p>

<h2>What this means for a landlord</h2>
<ul class="clean">
<li><b>Closures are a programme, not an accident.</b> The brand guides to 50&ndash;60 closures in FY2026 after 86 in
FY2025, under a plan it calls "JACK on Track", which also includes selling real estate. A single unit can be closed
for portfolio reasons that have nothing to do with its own sales.</li>
<li><b>Real-estate sales by the tenant compete with you.</b> When the brand sells property it is, in effect, a seller
of net-lease product in the same market at the same time. That is a negotiation fact, not a financial one.</li>
<li><b>Leverage is high but improving.</b> $1.47bn of debt against a $901m stockholders' deficit, with $46m of cash
and the dividend suspended. Net earnings for the first 40 weeks of FY2026 were <i>positive</i> at $27.9m, against a
loss in the prior-year period &mdash; a genuine improvement that should be stated alongside the deficit, not instead
of it.</li>
<li><b>Refinancing is done for now.</b> The company completed a $500m 2026-1 Class A-2 issuance with an anticipated
repayment date in May 2031 and repaid its 2019-1 notes. Near-term refinancing risk is lower than it was.</li>
<li><b>What to ask for.</b> Unit-level sales, the franchisee's financial statements, the guaranty, and a written
statement that the unit is not on a closure list. Without those, the lease credit is ununderwritten.</li>
</ul>

<h2>The two-sided view</h2>
<div class="grid g2">
<div class="card"><h3 style="margin-top:0">Case for the tenant performing</h3>
<ul class="clean">
<li>Same-store sales improved from &minus;7.1% to &minus;1.1% year over year.</li>
<li>Net earnings turned positive in the first 40 weeks of FY2026.</li>
<li>Refinancing completed; no 2026 maturity wall.</li>
<li>Drive-thru sites are scarce and the brand needs its best units.</li>
</ul></div>
<div class="card"><h3 style="margin-top:0">Case against</h3>
<ul class="clean">
<li>Negative same-store sales and a guided low-single-digit decline.</li>
<li>50&ndash;60 closures guided for one year, mostly franchised.</li>
<li>Dividend and buyback suspended; negative book equity.</li>
<li>Franchisee-level margin fell to 37.4% from 39.3% a year earlier, with higher bad debt.</li>
<li>93% franchisee-operated: the brand's health is not the obligor's health.</li>
</ul></div>
</div>
<p>The model does not try to resolve this. It prices it: a 35% chance that a hold strategy falls into the
no-renewal path, and a credit spread inside the cap rate. Both are stated assumptions, both are published, and both
can be replaced with the franchisee's actual financials.</p>
"""
    return page("tenant.html", "Tenant and brand credit", body,
                subtitle="What the latest SEC filing actually says about the brand, the franchisees, the closure programme and the balance sheet.",
                eyebrow="Credit risk")


def build_capital_tax():
    curve_rows = "".join(
        f'<tr><td>{e(k)}</td><td class="num">{e(v)}</td><td>{src("S09")}</td></tr>' for k, v in [
            ("2-year", val("F83")), ("5-year", val("F84")), ("10-year (2026-11-06)", val("F81")),
            ("10-year (2026-11-02)", val("F82")), ("30-year", val("F85"))])
    body = f"""
<div class="callout info">
<p style="margin-top:0"><b>What the data says.</b> Long money is expensive and the curve is steep at the long end:
the 10-year is 4.86% and the 30-year 5.26%. The 10-year fell 45 basis points between 5 October and 6 November 2026
(5.31% &rarr; 4.86%), which is the kind of move that re-prices net-lease assets. Transaction taxes are unusually high
in this jurisdiction, and the Section&nbsp;1031 exchange is the only mechanism that avoids paying them twice.</p>
</div>

<h2>The yield curve — the anchor for every cap rate</h2>
<div class="tablewrap"><table>
<thead><tr><th>Maturity</th><th class="num">Par yield</th><th>Source</th></tr></thead>
<tbody>{curve_rows}</tbody></table></div>
<p class="small muted">U.S. Treasury daily par yield curve. Rates are a fact of the access date, not a forecast.</p>

<h2>Taxes and transaction costs</h2>
{facts_table(rows_where(category='Taxes and transaction costs'), cols=('id','metric','value','period','geography','source','status'))}

<h2>What each item does to a sale</h2>
<div class="tablewrap"><table>
<thead><tr><th>Item</th><th>Effect on the owner</th><th>Size</th></tr></thead>
<tbody>
<tr><td>City base real property transfer tax</td><td>Paid on every sale in the City</td><td>{val('F90')}</td></tr>
<tr><td>Measure ULA surtax above $5.4m</td><td>Paid by the seller; it is a cliff, not a marginal rate &mdash; it applies to the whole price</td><td>+4.0% &rarr; 4.45% combined</td></tr>
<tr><td>Measure ULA above $10.9m</td><td>Same cliff, higher band</td><td>+5.5% &rarr; 5.95% combined</td></tr>
<tr><td>Proposition 13 reassessment</td><td>Not the seller's cost, but the buyer prices it in: a sale resets the tax base to market</td><td>1% of value a year, capped at 2% growth</td></tr>
<tr><td>Section 1031 exchange</td><td>Defers federal and state capital-gains tax on the sale if the rules are met</td><td>45 / 180 days</td></tr>
</tbody></table></div>

<h2>Measure ULA in detail — the cliff that can cost more than the sale</h2>
<p>The City of Los Angeles imposes a base real property transfer tax of 0.45% and, for closings after 30 June 2026, a
Measure ULA surtax of 4.0% above $5,400,000 and 5.5% at or above $10,900,000. Because the surtax applies to the
consideration for the whole property rather than the excess over the threshold, a sale priced just above $5.4m pays
4.0% on everything. The thresholds are re-indexed every year to chained CPI, so a price that is under the threshold
this year may be over it next year. {src('S10')}</p>
<div class="callout warn">
<p style="margin:0"><b>Practical consequence.</b> If the modelled value of this asset is anywhere near $5.4m, the
difference between a $5.35m sale and a $5.45m sale can be about $218,000 of tax on $100,000 of extra price. That is a
structuring question for the sale, and it needs professional advice &mdash; but it belongs in the plan from day one,
not at the closing table.</p>
</div>

<h2>Section 1031, precisely</h2>
<ul class="clean">
<li>Both the relinquished and the replacement property must be held for business or investment use. Real property is
like-kind to other real property inside the United States. {src('S12')}</li>
<li>45 calendar days from closing to identify replacement property in writing, signed and delivered to a person
involved in the exchange. Notice to your own attorney or broker is not sufficient.</li>
<li>180 calendar days to close, or the tax-return due date if earlier. The limits cannot be extended for hardship
except after a presidentially declared disaster.</li>
<li>A qualified intermediary must hold the proceeds; you cannot be your own facilitator, and neither can your agent
of the past two years.</li>
<li>Gain is deferred, not forgiven: basis carries over, so the tax is eventually paid. That is why the model taxes the
2040 liquidation in every strategy, including the exchange ones.</li>
</ul>

<h2>Capital markets and the cap rate</h2>
{facts_table(rows_where(category='Capital markets'), cols=('id','metric','value','period','geography','source','status'))}
<p>There is no official public cap-rate series for single-tenant restaurants. The cap rate in the model is therefore
an assumption anchored to the Treasury curve and a property spread, and it is the assumption the owner should replace
first, with a broker opinion of value or an appraisal. The sensitivity grid on the
<a href="projection.html">model page</a> shows what happens across the full range.</p>
"""
    return page("capital-tax.html", "Capital markets and tax", body,
                subtitle="The Treasury curve, the transaction-tax stack, Proposition 13 and the Section 1031 mechanics that decide the sale structure.",
                eyebrow="Money and tax")


def build_property():
    lease_rows = facts_table(rows_where(category='Property and lease'),
                             cols=('id', 'metric', 'value', 'period', 'source', 'status'))
    body = f"""
<div class="callout">
<p style="margin-top:0"><b>Privacy first.</b> The address, assessor parcel number, owner identity, rent, basis and
loan terms are <b>not</b> in this repository and are not on this site. The property is described only at
&ldquo;Central Los Angeles&rdquo; and every financial output is normalised to $100,000 of NOI. Placeholders
<code>[REDACTED-PROPERTY-01]</code>, <code>[REDACTED-PARCEL-01]</code> and <code>[REDACTED-OWNER-01]</code> are used
where an identifier would otherwise appear. See the <a href="privacy.html">privacy page</a>.</p>
</div>

<h2>Asset profile</h2>
<div class="tablewrap"><table>
<thead><tr><th>Item</th><th>Value</th><th>Basis</th></tr></thead>
<tbody>
<tr><td>Asset type</td><td>Single-tenant quick-service restaurant with drive-thru</td><td>Owner brief</td></tr>
<tr><td>Brand</td><td>Jack in the Box</td><td>Owner brief</td></tr>
<tr><td>Lease structure</td><td>Triple net (NNN) — tenant pays taxes, insurance and maintenance</td><td>Owner brief</td></tr>
<tr><td>Location</td><td>Central Los Angeles, City of Los Angeles</td><td>Owner brief</td></tr>
<tr><td>Lease expiration</td><td>Between 2030 and 2035 (a five-year window, not a date)</td><td>Owner brief — see F108</td></tr>
<tr><td>Address / APN / owner</td><td>[REDACTED-PROPERTY-01] / [REDACTED-PARCEL-01] / [REDACTED-OWNER-01]</td><td>Withheld by policy</td></tr>
<tr><td>Rent, escalations, options, guaranty</td><td>Not supplied</td><td>Must be read from the lease</td></tr>
</tbody></table></div>

<h2>Lease and property facts</h2>
{lease_rows}

<h2>Why an NNN lease is worth more than the building</h2>
<p>A triple-net lease transfers the operating risks &mdash; property tax, insurance, roof and structure &mdash; to the
tenant, so the owner receives a bond-like rent stream. Buyers price that stream on the tenant's credit and on the
number of years left. That is why the same building with the same rent is worth materially more with twelve years of
term than with four: the buyer is not buying the bricks, it is buying a contractual cash flow with a known end date.</p>

<h2>The eleven things to pull from the lease today</h2>
<p>These are the facts that would change the recommendation more than any forecast on this site. Every one of them is
private and none is in this workbook.</p>
<div class="tablewrap"><table>
<thead><tr><th>#</th><th>Obtain</th><th>Why it changes the answer</th></tr></thead>
<tbody>
<tr><td>1</td><td>Exact expiration date</td><td>The whole term-premium calculation depends on it; the 2030 vs 2035 endpoints are tested but a real date is better.</td></tr>
<tr><td>2</td><td>Renewal options and notice windows</td><td>An option held by the tenant at a fixed rent is a landlord liability if rent is below market, and an asset if above.</td></tr>
<tr><td>3</td><td>In-place rent and escalations</td><td>Determines the real NOI and whether the rent is above or below market.</td></tr>
<tr><td>4</td><td>Percentage rent clause</td><td>Adds upside tied to the store's sales, which are currently declining.</td></tr>
<tr><td>5</td><td>Tenant entity and guaranty</td><td>The difference between a franchisee and a corporate obligor is the credit spread in the cap rate.</td></tr>
<tr><td>6</td><td>Assignment and subletting rights</td><td>Determines whether the tenant can hand the lease to a weaker operator.</td></tr>
<tr><td>7</td><td>Insurance obligations and deductibles</td><td>Earthquake cover is the largest unquantified operating cost for this asset class in Los Angeles.</td></tr>
<tr><td>8</td><td>Roof, structure and parking-lot obligations</td><td>&ldquo;NNN&rdquo; leases often leave structure and parking on the landlord.</td></tr>
<tr><td>9</td><td>Co-tenancy, go-dark and radius clauses</td><td>Can allow the tenant to pay reduced rent or leave early.</td></tr>
<tr><td>10</td><td>Environmental indemnity and existing reports</td><td>A Phase I is required by most buyers and can surface a liability.</td></tr>
<tr><td>11</td><td>Loan documents: rate, maturity, prepayment</td><td>A defeasance penalty can make a sale uneconomic in a given year.</td></tr>
</tbody></table></div>

<h2>Permitted-use and drive-thru risk</h2>
<p>The value of this asset to a replacement tenant depends on the drive-thru entitlement, not just the building. A
drive-thru that requires a new conditional-use permit can sit dark for a year or more, and City rules on drive-thrus
have tightened over time. The workbook cannot verify the site's entitlement without the address, so the re-leasing
case is modelled with a vacancy allowance and a re-leasing cost rather than assumed to be instant.</p>
"""
    return page("property-lease.html", "Property and lease", body,
                subtitle="What is known about the asset, what is deliberately redacted, and the eleven lease facts that must be read before a binding decision.",
                eyebrow="The asset")


def build_risks():
    bau = [r for r in RISKS["rows"] if r["class"] == "Business as usual"]
    swan = [r for r in RISKS["rows"] if r["class"] == "Black swan"]

    def table(rows):
        out = ['<div class="tablewrap"><table><thead><tr><th>ID</th><th>Risk</th><th>Likelihood</th>'
               '<th>Impact</th><th>Hits</th><th>Mitigation</th><th>Evidence</th></tr></thead><tbody>']
        for r in rows:
            sev = {"High": "warn", "Medium": "neutral", "Low": "ok"}.get(r["likelihood"], "neutral")
            imp = {"Severe": "bad", "High": "bad", "Medium": "warn", "Low": "neutral"}.get(r["impact"], "neutral")
            ev = src(r["source"]) if r["source"].startswith("S") else '<span class="muted">Analysis</span>'
            out.append(
                f'<tr><td class="code">{e(r["id"])}</td><td>{e(r["risk"])}</td>'
                f'<td><span class="badge {sev}">{e(r["likelihood"])}</span></td>'
                f'<td><span class="badge {imp}">{e(r["impact"])}</span></td>'
                f'<td class="small">{e(r["affects"])}</td><td class="small">{e(r["mitigation"])}</td>'
                f'<td>{ev}</td></tr>')
        out.append("</tbody></table></div>")
        return "".join(out)

    body = f"""
<div class="callout warn">
<p style="margin-top:0"><b>How to read this register.</b> Every risk is mapped to the decisions it actually affects:
<b>SELL</b> (sell now through a 1031), <b>EXTEND</b> (extend then sell), <b>HOLD</b> (hold to expiry and renew), and
<b>EXPIRE</b> (let it expire with no commitment). Likelihood and impact are graded judgements, not probabilities,
except where an official measured anchor exists and is linked. The register is not a list of things that might happen
&mdash; it is a list of things that would change the decision.</p>
</div>

<h2>Business as usual — {len(bau)} risks</h2>
{table(bau)}

<h2>Black swans — {len(swan)} events</h2>
{table(swan)}

<h2>Verified hazard baseline</h2>
<p>These are the measured hazard inputs the register rests on. The parcel-specific classifications are blank because
an address is required and the address is withheld by policy.</p>
{facts_table(rows_where(category='Hazard'), cols=('id','metric','value','period','geography','source','status'))}

<h2>The three that dominate</h2>
<ol class="clean">
<li><b>Term decay (R01)</b> is certain, not probable. It happens in every scenario in which nothing is done, and it is
the only risk on the list that the owner can eliminate without predicting anything. Its mitigation is the
recommendation.</li>
<li><b>Earthquake (R20)</b> is the largest single-event exposure: a 60% chance of an M&ge;6.7 earthquake in the Los
Angeles region within 30 years, and a 31% chance of M&ge;7.5 {src('S16')}. It cannot be diversified inside one
building. It can be insured, retrofitted, or sold &mdash; and a 1031 exchange into several properties in several
markets is the only structural transfer of that risk available to a single-asset owner.</li>
<li><b>Tenant credit (R03, R04)</b> is the risk most likely to arrive early. 93% of the system is franchised and the
brand is closing 50&ndash;60 units a year. The owner's exposure is not to Jack in the Box's brand equity; it is to one
franchisee's balance sheet.</li>
</ol>

<h2>What is <i>not</i> on this register</h2>
<p>Events that would affect the owner but not the decision: a change in the owner's own tax residence, a change in
family circumstances, or a desire to hold the asset for reasons that are not financial. Those are real and they
outrank everything on this page, but they are not risks to the property and this workbook does not model them.</p>
"""
    return page("risks.html", "Risk register", body,
                subtitle="19 ordinary-course risks and 12 black-swan events, each mapped to the decisions it affects, with an official anchor where one exists.",
                eyebrow=f"{STATS['risks']} risks")


def build_sources():
    rows = "".join(
        f'<tr><td class="code"><a name="{e(s["id"])}"></a>{e(s["id"])}</td>'
        f'<td><span class="badge neutral">{e(s["tier"])}</span></td>'
        f'<td>{e(s["publisher"])}</td><td>{e(s["title"])}<div class="small muted">{e(s["supports"])}</div></td>'
        f'<td><a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">open &#8599;</a></td></tr>'
        for s in SOURCES_DOC["sources"])
    body = f"""
<p>Every value published on this site was read from one of these {STATS['sources']} sources on
<b>{ACCESS_DATE}</b>. A source is listed here only if it was actually opened and read during this session &mdash; no
citation was copied from another document, and no value came from a data aggregator.</p>
<div class="callout info">
<p style="margin:0"><b>Tiers.</b> A = primary official government or regulator record. B = primary issuer filing with a
securities regulator. C = analyst assumption published by this workbook and never presented as a fact.
D = secondary or commercial commentary, used for orientation only and never for a published value. <b>No tier D source
is used for any number on this site.</b></p>
</div>
<div class="tablewrap"><table>
<thead><tr><th>ID</th><th>Tier</th><th>Publisher</th><th>Document and what it supports</th><th>Link</th></tr></thead>
<tbody>{rows}</tbody></table></div>

<h2>What is deliberately absent from this list</h2>
<ul class="clean">
<li>Commercial brokerage research, cap-rate surveys and news articles. They are useful orientation but they are not
official records, so no value on this site depends on them.</li>
<li>Aggregator statistics. Where an official series exists, the official series is cited; where it does not, the value
is blank.</li>
<li>Anything the owner did not supply and that is not public: rent, basis, loan terms, the lease itself, the
franchisee's financials.</li>
</ul>

<h2>Reproducing the verification</h2>
<p>Each fact row on the site carries its source id and that id resolves to the URL above. The automated checker
re-tests every row: a verified or computed fact must resolve to a URL in this ledger, an unverified fact must be
blank, every internal link must exist, and a personal-information scan must return nothing. Run
<code>python3 session-6ad87c21/scripts/verify.py</code>.</p>
"""
    return page("sources.html", "Sources", body,
                subtitle="The complete ledger: every official record used, its tier, and what it supports.",
                eyebrow=f"{STATS['sources']} official sources")


def build_flagged():
    unv = [r for r in ROWS if r["status"] == "unverified"]
    own = [r for r in ROWS if r["status"] == "owner"]
    unv_rows = "".join(
        f'<tr><td class="code">{e(r["id"])}</td><td>{e(r["metric"])}</td><td>{e(r["geography"])}</td>'
        f'<td class="small">{e(r["note"])}</td></tr>' for r in unv)
    own_rows = "".join(
        f'<tr><td class="code">{e(r["id"])}</td><td>{e(r["metric"])}</td><td class="num">{e(r["value"])}</td>'
        f'<td class="small">{e(r["note"])}</td></tr>' for r in own)

    irregularities = [(i["id"], i["class"], i["finding"], i["resolution"], i["evidence"], i["status"])
                      for i in IRREG["items"]]
    irr_rows = "".join(
        f'<tr><td class="code">{e(i)}</td><td><span class="badge warn">{e(cat)}</span></td><td>{e(text)}</td>'
        f'<td class="small">{e(res)}</td><td class="code small">{e(ev)}</td></tr>'
        for i, cat, text, res, ev, _ in irregularities)

    body = f"""
<div class="callout warn">
<p style="margin-top:0"><b>This page is the point of the exercise.</b> Everything below either could not be confirmed
from an official source, was supplied by the owner and cannot be checked publicly, or is a defect found in this
repository during a line-by-line audit. None of it blocks the decision &mdash; but none of it is hidden either.
Items marked <b>open</b> need the owner or a professional to close them.</p>
</div>

<h2>1. Unverified data — {len(unv)} items deliberately left blank</h2>
<p>No official value was confirmable on {ACCESS_DATE}. The cell is empty on the site rather than filled with an
estimate, and the note says what to obtain and who publishes it.</p>
<div class="tablewrap"><table>
<thead><tr><th>ID</th><th>Item</th><th>Geography</th><th>What is missing and how to close it</th></tr></thead>
<tbody>{unv_rows}</tbody></table></div>

<h2>2. Owner-supplied facts — {len(own)} items that cannot be publicly verified</h2>
<p>These came from the brief. They are used, they are labelled, and they are not presented as independently verified.</p>
<div class="tablewrap"><table>
<thead><tr><th>ID</th><th>Item</th><th class="num">Value used</th><th>Status</th></tr></thead>
<tbody>{own_rows}</tbody></table></div>

<h2>3. Repository irregularities found in the line-by-line audit — {len(irregularities)} items</h2>
<p>Eight sessions have built on this repository. The audit below records what is inconsistent or unresolved, in the
order it would matter to someone relying on the published work. Nothing here is a criticism of another session's
work: every one of these is a normal consequence of parallel authorship, and each has a stated fix.</p>
<div class="tablewrap"><table>
<thead><tr><th>ID</th><th>Class</th><th>Finding</th><th>What was done / recommended fix</th><th>Evidence</th></tr></thead>
<tbody>{irr_rows}</tbody></table></div>

<h2>4. What this means for relying on the site</h2>
<ul class="clean">
<li><b>The direction is robust; the levels are not.</b> The ranking of strategies survives every sensitivity tested.
The dollar amounts depend on a cap rate that nobody has verified, so treat them as ratios, not appraisals.</li>
<li><b>Three facts would change the answer most</b>: the exact lease expiry and options, the tenant entity and
guaranty, and the in-place rent against market. All three are obtainable this week.</li>
<li><b>The privacy control is absolute.</b> No address, APN, owner name, rent, basis or loan figure is in this
repository or on this site. If one appears, it is a defect and should be reported immediately.</li>
</ul>
"""
    return page("flagged.html", "Flagged for review", body,
                subtitle="Every unverified value, every owner-supplied fact, and every repository irregularity found in the audit — with what to do about each.",
                eyebrow=f"{len(unv)} blanks · {len(irregularities)} irregularities")


def build_methodology():
    body = f"""
<h2>The rules this workbook follows</h2>
<ol class="clean">
<li><b>A value is published only if it was read from the official source on {ACCESS_DATE} and that source is linked
on the same row.</b> Not from memory, not from a summary, not from another dashboard in this repository.</li>
<li><b>If no official value exists, the cell is blank.</b> Nothing is inferred, interpolated, annualised or copied from
an aggregator. The row appears on the <a href="flagged.html">Flagged for Review</a> page with what to obtain.</li>
<li><b>Computed values are labelled computed</b>, cite the official series they are computed from, and show the
arithmetic in the note.</li>
<li><b>Assumptions are labelled assumptions</b> and are never presented as observations. All {len(ASSUMPTIONS)} of them
are published with the range tested.</li>
<li><b>The build fails</b> if a verified row lacks a source, if an unverified row carries a value, if an internal link
is broken, or if a possible personal identifier appears. See <code>scripts/verify.py</code>.</li>
<li><b>Privacy overrides convenience.</b> If a fact cannot be published without identifying the owner, the parcel or
the tenant entity, it is not published.</li>
</ol>

<h2>How the review was actually done</h2>
<p>The session opened each official document, read the specific table or paragraph, and recorded the value with the
document it came from. Where a retrieval returned something unexpected, that is recorded rather than smoothed over:
for example, a Census QuickFacts request for the county returned <i>national</i> figures on one URL form, which is why
the county rows here cite the separate county slug and why the county education rows are blank instead of filled from
the national table.</p>

<h2>How the model was built and tested</h2>
<ul class="clean">
<li>Six strategies, each carried to 2040 so the comparison is like-for-like.</li>
<li>All figures normalised to $100,000 of in-place NOI, so the workbook never needs the private rent.</li>
<li>A deterministic engine across Bear / Base / Bull, a 10,000-trial seeded Monte Carlo, a seven-column sensitivity
grid, a five-point cap-rate break-even, and eight robustness stress cases.</li>
<li>The ranking metric is the certainty equivalent at CRRA = 2, which penalises downside &mdash; not the mean, which
rewards it.</li>
<li>Two defects were found and fixed during the build and are recorded here rather than hidden: the hold strategies
were initially taxed at their interim sale (inconsistent with the exchange strategies), and the Monte Carlo seed
initially used Python's randomised <code>hash()</code>, which would have made the published output irreproducible.</li>
</ul>

<h2>What would falsify the recommendation</h2>
<ul class="clean">
<li>A verified cap rate materially different from the 6.00% base &mdash; for example a broker opinion of value implying
5.25% or 7.25%.</li>
<li>Lease terms that give the tenant a below-market fixed-price renewal option, which converts the option into a
liability rather than an asset.</li>
<li>A corporate guaranty or a letter of credit that removes the franchisee credit risk.</li>
<li>Evidence of redevelopment value in the land that exceeds the net-lease value.</li>
</ul>

<h2>Reproduce everything</h2>
<div class="card tight">
<pre class="mono" style="margin:0;white-space:pre-wrap">python3 session-6ad87c21/scripts/model.py       # deterministic + 10,000-trial Monte Carlo
python3 session-6ad87c21/scripts/build_site.py  # all 14 pages
python3 session-6ad87c21/scripts/verify.py      # source, blank-value, link and PII checks</pre>
</div>
<p>Python 3.11, standard library only. No network access is needed to rebuild, and the model output is deterministic
across runs.</p>

<h2>Scope and limitations</h2>
<p>This is internal decision support for one owner. It is not an appraisal, not tax advice, not investment advice and
not legal advice. It does not value the parcel; it values a dollar of net operating income. The address, rent, basis,
loan terms and lease itself were not supplied and are not guessed at. Before relying on any number here, obtain an
appraisal or broker opinion of value, read the lease, and take tax advice from a CPA who has seen the basis
schedule.</p>
"""
    return page("methodology.html", "Method and limitations", body,
                subtitle="The verification rules, how the model was tested, two defects found and fixed during the build, and what would falsify the recommendation.",
                eyebrow="Method")


def build_privacy():
    body = f"""
<div class="callout ok">
<p style="margin-top:0"><b>No personal information is published on this site.</b> Not the owner's name, not the
property address, not the assessor parcel number, not the rent, not the purchase basis, not any loan or account
number. The site describes a &ldquo;Central Los Angeles&rdquo; single-tenant restaurant and expresses every financial
result per $100,000 of net operating income.</p>
</div>

<h2>What is withheld, and how</h2>
<div class="tablewrap"><table>
<thead><tr><th>Item</th><th>Handling</th></tr></thead>
<tbody>
<tr><td>Owner identity</td><td>Not collected. Never appears. Placeholder <code>[REDACTED-OWNER-01]</code> where an identifier would otherwise be required.</td></tr>
<tr><td>Property address</td><td>Not collected. Placeholder <code>[REDACTED-PROPERTY-01]</code>. Geography is limited to City / County / metro.</td></tr>
<tr><td>Assessor parcel number</td><td>Not collected. Placeholder <code>[REDACTED-PARCEL-01]</code>.</td></tr>
<tr><td>In-place rent, escalations, percentage rent</td><td>Not collected. The model is normalised to $100,000 of NOI, so the private figure is never needed.</td></tr>
<tr><td>Purchase basis and depreciation</td><td>Not collected. The after-tax model uses a published basis <i>ratio</i> (A6) and tests the range instead.</td></tr>
<tr><td>Loan balance, rate, lender</td><td>Not collected. Listed as an unknown to obtain.</td></tr>
<tr><td>Tenant legal entity and guarantor</td><td>Not collected. Described only as &ldquo;likely a franchisee&rdquo; because 93% of the system is franchised.</td></tr>
</tbody></table></div>

<h2>The one personal identifier that does exist in this repository</h2>
<p>The git commit history contains the repository owner's personal email address in the author metadata of every
commit. That is a property of how the repository was created, not of this site, and it is published on the
<a href="flagged.html">Flagged for Review</a> page as I-01 with the recommended fix (enable GitHub's email-privacy
setting; history rewriting is not attempted because it would invalidate every prior session's commit references).
No other personal identifier was found in a scan of the repository's HTML, JSON, Markdown and Python files.</p>

<h2>How the control is enforced, not just promised</h2>
<ul class="clean">
<li><code>scripts/verify.py</code> scans every generated page and every data file for email addresses, telephone
numbers, US street-address patterns, assessor parcel numbers, and the placeholder-free mention of the owner or the
tenant entity.</li>
<li>The build fails if the scan matches. It is not a manual promise that the site is clean &mdash; it is a test that
runs on every build and can be re-run by anyone.</li>
<li>The fact ledger uses a dedicated status for private facts (<code>owner</code>) so that they cannot be confused with
verified public data, and unverified facts are structurally incapable of carrying a value.</li>
</ul>

<h2>If you believe something private has been published</h2>
<p>Report it immediately and treat it as a defect. The correct response is to remove the page from publication first
and investigate second. Nothing on this site is worth publishing at the cost of the owner's privacy.</p>
"""
    return page("privacy.html", "Privacy", body,
                subtitle="What is withheld, what is never collected, and how the control is enforced in code rather than promised in prose.",
                eyebrow="Privacy")


SLUGS = {
    "build_index": "index.html",
    "build_exec": "executive-summary.html",
    "build_decision": "decision.html",
    "build_projection": "projection.html",
    "build_risks": "risks.html",
    "build_market": "market.html",
    "build_economy": "economy.html",
    "build_tenant": "tenant.html",
    "build_capital_tax": "capital-tax.html",
    "build_property": "property-lease.html",
    "build_sources": "sources.html",
    "build_flagged": "flagged.html",
    "build_methodology": "methodology.html",
    "build_privacy": "privacy.html",
}

BUILDERS = [
    build_index, build_exec, build_decision, build_projection, build_risks,
    build_market, build_economy, build_tenant, build_capital_tax, build_property,
    build_sources, build_flagged, build_methodology, build_privacy,
]


def main():
    written = []
    for fn in BUILDERS:
        html_out = fn()
        # extract the slug from the page() call by regenerating the name
        slug = SLUGS[fn.__name__]
        path = os.path.join(ROOT, slug)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html_out)
        written.append(slug)
    print(f"built {len(written)} pages in {ROOT}:")
    for w in written:
        print("  ", w)


if __name__ == "__main__":
    main()

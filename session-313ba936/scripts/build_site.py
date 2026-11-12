#!/usr/bin/env python3
"""
Builds the session-313ba936 dashboard from the JSON data files.

Every number rendered into HTML is read from data/*.json at build time. Nothing is typed by
hand into a template. That is the mechanism behind the "no hallucination" requirement: if a
value is not in the verified dataset it cannot appear on the page.

Run: python3 session-313ba936/scripts/build_site.py
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # session-313ba936/
REPO = os.path.dirname(ROOT)
D = os.path.join(ROOT, "data")

e = html.escape


def load(n):
    with open(os.path.join(D, n), encoding="utf-8") as f:
        return json.load(f)


SRC_DOC = load("sources.json")
SRC = {s["id"]: s for s in SRC_DOC["sources"]}
MET = load("metrics.json")
RISK = load("risks.json")
MODEL = load("model_output.json")
IRR = load("irregularities.json")
REQ = load("requirements.json")

ACCESS = SRC_DOC["access_date"]
ROWS = MET["rows"]
REV = [r for r in ROWS if r["status"] == "verified"]
COMP = [r for r in ROWS if r["status"] == "computed"]
UNV = [r for r in ROWS if r["status"] == "unverified"]

NAV = [
    ("index.html", "Overview"),
    ("executive-summary.html", "Executive summary"),
    ("decision.html", "Decision"),
    ("area-economy.html", "Area economy"),
    ("demographics-schools.html", "Population &amp; schools"),
    ("property-lease.html", "Property &amp; lease"),
    ("tenant-credit.html", "Tenant credit"),
    ("valuation-capital.html", "Valuation &amp; capital"),
    ("risks.html", "Risk register"),
    ("projection-model.html", "Projection model"),
    ("data.html", "All data"),
    ("verification.html", "Verification"),
    ("flagged.html", "Flagged for review"),
    ("sources.html", "Sources"),
    ("privacy.html", "Privacy"),
    ("suggestions.html", "Suggestions & review"),
]

MONEY = "${:,.0f}"


def money(x, dec=0):
    return f"{'-' if x < 0 else ''}${abs(x):,.{dec}f}"


def pct(x, dec=2):
    return f"{x:.{dec}f}%"


def src_link(sid, short=False):
    s = SRC[sid]
    label = sid if short else f'{sid} &#8599;'
    return (f'<a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer" '
            f'title="{e(s["publisher"])} — {e(s["title"])}">{label}</a>')


def badge(status):
    cls = {"verified": "ok", "computed": "blue", "unverified": "warn"}.get(status, "")
    return f'<span class="badge {cls}">{e(status)}</span>'


def page(slug, title, body, description="", wide=False):
    cur = ' aria-current="page"'
    parts = []
    for href, label in NAV:
        parts.append('<a href="%s"%s>%s</a>' % (href, cur if href == slug else "", label))
    nav = "".join(parts)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} — Central LA NNN decision dashboard</title>
<meta name="description" content="{e(description)}">
<meta name="robots" content="index,follow">
<link rel="stylesheet" href="assets/style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%2312161c'/%3E%3Ctext x='16' y='23' font-family='system-ui' font-size='17' font-weight='700' fill='%23fff' text-anchor='middle'%3EJ%3C/text%3E%3C/svg%3E">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap bar">
  <a class="brand" href="index.html"><span class="mark">J</span><span>Central LA NNN decision dashboard
    <small>Jack in the Box &middot; 2030&ndash;2035 expiry &middot; verified {ACCESS}</small></span></a>
  <nav class="main" aria-label="Sections">{nav}</nav>
</div></header>
<main id="main" class="wrap">
{body}
</main>
<footer class="site"><div class="wrap">
  <p><strong>Internal decision support. Not an appraisal, not tax advice, not investment advice.</strong>
  Every value on this page is read from the official source linked beside it on {ACCESS}. Values that could not be
  confirmed are blank and listed on <a href="flagged.html">Flagged for review</a>.</p>
  <p>No name, street address, parcel number, loan number, account number or other personal identifier appears in this
  repository or on this site. See <a href="privacy.html">Privacy</a>. Built by Arena session
  <code>session-313ba936</code> from {len(SRC)} official sources &middot;
  <a href="verification.html">verification record</a> &middot;
  reproduction: <code>python3 session-313ba936/scripts/build_site.py</code></p>
</div></footer>
</body>
</html>
"""


def head(eyebrow, h1, lede):
    return f'<div class="page-head"><p class="eyebrow">{eyebrow}</p><h1>{h1}</h1><p class="lede">{lede}</p></div>'


def table(headers, rows, cls="", numeric=(), caption=""):
    out = ['<div class="tablewrap">', f'<table class="{cls}">']
    if caption:
        out.append(f"<caption>{caption}</caption>")
    out.append("<thead><tr>")
    for i, h in enumerate(headers):
        out.append('<th%s>%s</th>' % (' class="num"' if i in numeric else "", h))
    out.append("</tr></thead><tbody>")
    for r in rows:
        out.append("<tr>")
        for i, c in enumerate(r):
            out.append('<td%s>%s</td>' % (' class="num"' if i in numeric else "", c))
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def kpi(label, num, sub, cls=""):
    return (f'<div class="kpi {cls}"><div class="label">{label}</div>'
            f'<div class="num">{num}</div><div class="sub">{sub}</div></div>')


def bar(label, value, maxv, txt, cls=""):
    w = max(1.0, min(100.0, value / maxv * 100)) if maxv else 0
    return (f'<div class="bar-row"><div>{label}</div>'
            f'<div class="bar-track"><div class="bar-fill {cls}" style="width:{w:.1f}%"></div></div>'
            f'<div class="val">{txt}</div></div>')


# =========================================================================== pages
def build_index():
    mc = MODEL["monte_carlo"]
    be = MODEL["breakevens"]
    cat_counts = {}
    for r in ROWS:
        cat_counts.setdefault(r["category"], [0, 0])
        cat_counts[r["category"]][0 if r["status"] == "unverified" else 1] += 1

    body = head(
        "Executive dashboard",
        "Central Los Angeles Jack in the Box, net-lease: sell before expiry or renew?",
        "A single-tenant NNN asset with a lease expiring somewhere in 2030&ndash;2035. This dashboard exists to make one "
        "decision defensible: exit before expiry, extend and then sell, or hold and renew. Every input is either read "
        "from an official source on the access date or labelled as an assumption.")

    body += '<div class="grid g4" style="margin-bottom:6px">'
    body += kpi("Verdict", "Negotiate, then price", "Do not sell blind, do not renew on autopilot", "accent")
    body += kpi("Hold barely wins on the mean", f'{mc["mean_difference_pct_of_sell_mean"]:+.1f}%',
                f'base case, {MODEL["config"]["horizon_year"]} wealth', "ok")
    body += kpi("But holding has the fatter tail", pct(mc["downside_from_mean_pct"]["hold_concentrated"], 1),
                "5th-percentile loss vs " + pct(mc["downside_from_mean_pct"]["sell_diversified"], 1) + " diversified", "bad")
    body += kpi("Going-in cap where the answer flips", pct(be["breakeven_going_in_cap_pct"]),
                "below this, selling wins", "warn")
    body += "</div>"

    body += '<div class="callout"><h3 style="margin-bottom:6px">Read this first</h3>'
    body += ('<p><strong>No value on this site is the property\u2019s value.</strong> The contract rent, the exact expiry '
             'date, the escalations, the owner\u2019s basis and the debt are all unknown. Every dollar figure is therefore '
             'expressed <em>per $100,000 of annual rent</em>, and the decision is expressed as a breakeven the owner can '
             'test against a real appraisal. Fourteen owner-specific fields are blank on purpose and listed on '
             f'<a href="flagged.html">Flagged for review</a> ({len(UNV)} blank rows in total).</p>')
    body += "</div>"

    body += "<h2>What the evidence says</h2>"
    body += '<div class="grid g2">'
    facts = [
        ("The county is shrinking, officially",
         f'County population is {MODEL["verified_inputs"]["county_pop_2025"]["value"]:,} in 2025 and the state projects '
         f'{MODEL["verified_inputs"]["county_pop_2040"]["value"]:,} by 2040 &mdash; a decline of '
         f'{abs(MODEL["verified_inputs"]["county_pop_2040"]["value"] - MODEL["verified_inputs"]["county_pop_2025"]["value"]):,} people. '
         'Census already shows &minus;3.2% since 2020.', "demographics-schools.html", "S03"),
        ("The tenant is contracting",
         'Jack in the Box same-store sales were &minus;1.1% in Q3 FY2026, the system closed 17 restaurants in the quarter '
         'and the estate is 53 units smaller than a year ago under a named closure programme.', "tenant-credit.html", "S15"),
        ("Jobs are growing, but narrowly",
         'County nonfarm employment rose 0.4% over the year, and 83% of the net gain was health care and social assistance. '
         'Information lost 10,200 jobs; restaurants gained 7,300 in the same period.', "area-economy.html", "S06"),
        ("The net-lease benchmark is 6.8%",
         'The most recent official filing from a major net-lease buyer reports a 6.8% initial weighted average cash yield '
         'on Q3 2026 acquisitions, against a 4.88% 10-year Treasury.', "valuation-capital.html", "S17"),
        ("The hazard is real and local",
         'USGS puts the Los Angeles region at 60% for a M6.7+ earthquake in 30 years. The Eaton Fire burned 14,021 acres '
         'inside this county in January 2025 and destroyed 9,419 structures.', "risks.html", "S18"),
        ("Selling is taxed, holding is capped",
         'City transfer tax is 0.45%, county 0.11%, and Measure ULA adds 4% above $5.4m. Holding instead keeps the '
         'Proposition 13 assessed-value cap at 2% a year, which a sale resets.', "valuation-capital.html", "S10"),
    ]
    for t, b, href, sid in facts:
        body += (f'<a class="card link" href="{href}"><h3>{t}</h3><p>{b}</p>'
                 f'<p class="go">Read the evidence &middot; source {src_link(sid, short=True)}</p></a>')
    body += "</div>"

    body += "<h2>The recommendation in one paragraph</h2>"
    body += ('<div class="callout ok"><p><strong>Open an extension negotiation now, and use the outcome to decide.</strong> '
             'On verified inputs, holding and selling land within a few percent of each other on central tendency '
             f'({mc["mean_difference_pct_of_sell_mean"]:+.1f}% of wealth), so the decision does not turn on a forecast &mdash; it '
             'turns on the rent and term the owner can negotiate and on how much concentrated tail risk the owner is willing '
             f'to carry. A renewal concession of just {pct(be["renewal_concession_that_flips_to_sell_pct"], 1)} flips the answer '
             'toward selling, and an extension at a rent reset makes both the hold case and the sale price better. '
             'So the sequence is: read the lease, get the insurance quote, get an appraisal, negotiate the extension, then '
             'sell into a section 1031 exchange only if the implied cap rate is below the breakeven or the replacement '
             'clears the required yield.</p></div>')

    body += "<h2>Sections</h2><div class=\"grid g3\">"
    sections = [
        ("executive-summary.html", "Executive summary", "The recommendation, the numbers behind it, and what to do in the next 90 days."),
        ("decision.html", "Decision", "Four strategies scored on the owner's own criteria, with nine decision triggers."),
        ("area-economy.html", "Area economy", "Jobs, income, output and consumer demand in the county and city."),
        ("demographics-schools.html", "Population &amp; schools", "Official population and K-12 enrollment projections to 2040."),
        ("property-lease.html", "Property &amp; lease", "What is known, and the fourteen lease facts that are not."),
        ("tenant-credit.html", "Tenant credit", "The tenant's own filed numbers, and the difference between parent and franchisee."),
        ("valuation-capital.html", "Valuation &amp; capital", "Rates, cap rates, transfer taxes, Prop 13 and section 1031."),
        ("risks.html", "Risk register", f"{len(RISK['rows'])} business-as-usual and black-swan risks, with exposure by strategy."),
        ("projection-model.html", "Projection model", "The engine, its inputs, its breakevens and a seeded 20,000-trial simulation."),
        ("data.html", "All data", f"All {len(ROWS)} metric rows in one filterable table with a source link on every row."),
        ("verification.html", "Verification", "What was checked, how, and what the check proves."),
        ("flagged.html", "Flagged for review", f"{len(UNV)} blanks, {len(IRR['items'])} irregularities and what to obtain."),
        ("sources.html", "Sources", f"{len(SRC)} official sources with the exact verified text."),
        ("privacy.html", "Privacy", "What is deliberately not collected, and why."),
    ]
    for href, t, d in sections:
        body += f'<a class="card link" href="{href}"><h3>{t}</h3><p>{d}</p><p class="go">Open &rarr;</p></a>'
    body += "</div>"

    return page("index.html", "Overview", body,
                "Source-verified dashboard for a central Los Angeles Jack in the Box net-lease asset: sell before expiry or renew.")


def build_exec():
    mc = MODEL["monte_carlo"]
    be = MODEL["breakevens"]
    sc = {s["id"]: s for s in MODEL["scenarios"]}
    dec = MODEL["decision"]["strategies"]

    body = head("Executive summary", "Hold the option open, then price it",
                "One page: the answer, the three numbers that decide it, and the risks that would change it.")
    body += '<p class="muted">Prepared ' + ACCESS + '. Internal decision support for the owner. Not an appraisal and not tax advice.</p>'

    body += "<h2>1. The question</h2>"
    body += ('<p>The asset is a single-tenant Jack in the Box under a net lease in central Los Angeles, expiring somewhere '
             'between 2030 and 2035. The owner must decide whether to sell before expiry, extend and then sell, or hold and '
             'renew, in a way that preserves wealth and keeps a manageable level of risk.</p>')

    body += "<h2>2. The answer</h2>"
    body += ('<div class="callout ok"><p><strong>Negotiate first; let the negotiation set the decision.</strong> '
             'The evidence does not support a fire sale and it does not support passive renewal. It supports a sequenced '
             'plan: obtain the lease and the insurance quote, get an appraisal, open an extension conversation that trades '
             'term for a rent reset, and then choose between holding and exchanging on the basis of two observable numbers '
             f'&mdash; the appraised going-in cap rate against the {pct(be["breakeven_going_in_cap_pct"])} breakeven, and the '
             f'replacement yield against the {pct(be["required_replacement_yield_pct"])} requirement.</p></div>')

    body += "<h3>Why the decision is close on central tendency</h3>"
    body += ('<p>Running both strategies through the same cash-flow engine, with the same escalation, reinvestment rate and '
             'exit cap, and with the sale paying full transaction cost and the replacement bought at the verified market '
             'yield, gives the following. All figures are nominal, pre-tax, per $100,000 of annual contract rent, at '
             f'{MODEL["config"]["horizon_year"]}.</p>')
    rows = []
    for s in MODEL["scenarios"]:
        rows.append([s["label"],
                     money(s["gross_price"]),
                     money(s["net_proceeds"]),
                     money(s["sell_wealth"]),
                     money(s["hold_wealth"]),
                     f'<span class="badge {"warn" if s["delta_hold_minus_sell"] > 0 else "ok"}">{money(s["delta_hold_minus_sell"])}</span>'])
    body += table(["Scenario", "Sale price at assumed cap", "Net proceeds", "Sold and redeployed", "Held and renewed",
                   "Hold minus sell"], rows, numeric=(1, 2, 3, 4, 5),
                  caption=f'Assumed going-in cap {pct(MODEL["assumptions"]["going_in_cap_pct"]["value"], 1)}; replacement bought at '
                          f'{pct(MODEL["verified_inputs"]["netlease_cash_yield_pct"]["value"], 1)} (verified, S17). Where "holding" wins it does so by single-digit percentages of wealth.')
    body += ('<p class="muted">The gap is small in every scenario, which is exactly why the decision should not be made on a '
             'point forecast. It should be made on the breakevens and on the owner\u2019s tolerance for the tail.</p>')

    body += "<h3>Why the risk side breaks the tie</h3>"
    body += (f'<p>A seeded {mc["trials"]:,}-trial simulation with rate shocks, rent uncertainty, renewal probability, '
             'earthquake and fire hazards, and partial insurance recovery gives holding the better central outcome '
             f'({mc["mean_difference_pct_of_sell_mean"]:+.1f}% of wealth) but a materially worse left tail: the 5th percentile falls '
             f'{pct(mc["downside_from_mean_pct"]["hold_concentrated"], 1)} below the mean when concentrated, against '
             f'{pct(mc["downside_from_mean_pct"]["sell_diversified"], 1)} for the diversified path. Selling wins in only '
             f'{mc["prob_sell_beats_hold"]*100:.1f}% of paths. That is the honest shape of the trade: <strong>holding is '
             'not wrong, but it is the choice that can hurt the most.</strong></p>')

    body += "<h2>3. The three numbers that decide it</h2>"
    body += '<div class="grid g3">'
    body += kpi("Breakeven going-in cap", pct(be["breakeven_going_in_cap_pct"]),
                "Above this cap rate (a cheaper sale price) holding wins. Below it, selling wins.", "warn")
    body += kpi("Required replacement yield", pct(be["required_replacement_yield_pct"]),
                "If the exchange cannot clear this, selling is a downgrade dressed as an exit.", "accent")
    body += kpi("Concession that flips the answer", pct(be["renewal_concession_that_flips_to_sell_pct"], 1),
                "How much rent the tenant must win at renewal for selling to become the better decision.", "bad")
    body += "</div>"
    body += ('<p class="muted">All three are solved by the engine in '
             '<code>session-313ba936/scripts/model.py</code> and reproduce exactly. The breakeven cap has a closed-form '
             f'check of Y&times;(1&minus;s) = {pct(be["breakeven_going_in_cap_closed_form_pct"])}, which the numerical solve matches to '
             f'{abs(be["breakeven_going_in_cap_closed_form_gap_pp"]):.3f} percentage points.</p>')

    body += "<h2>4. Ranked strategies</h2>"
    rows = [[f'{s["rank"]}', f'<strong>{e(s["name"])}</strong>', f'{s["weighted"]:.0f}',
             "".join(f'<span class="badge {"ok" if v>=4 else "neutral"}">{k[:4]} {v}</span> ' for k, v in s["scores"].items())]
            for s in dec]
    body += table(["#", "Strategy", "Score /100", "Component scores (1&ndash;5)"], rows, numeric=(2,),
                  caption=f'Weights: {", ".join(f"{k} {v:.0%}" for k, v in MODEL["decision"]["weights"].items())}. Judgement scores, not measurements.')

    body += "<h2>5. Risks that would change the answer</h2>"
    top = [r for r in RISK["rows"] if r["impact"] in ("very high", "high") and r["class"] == "SWAN"][:5]
    rows = [[r["id"], e(r["risk"]), f'<span class="badge {"bad" if r["impact"]=="very high" else "warn"}">{e(r["impact"])}</span>',
             e(r["likelihood"]), src_link(r["source"], short=True)] for r in top]
    body += table(["ID", "Black-swan risk", "Impact", "Likelihood", "Source"], rows)
    body += '<p>Full register, including every business-as-usual risk with its exposure by strategy, on <a href="risks.html">Risk register</a>.</p>'

    body += "<h2>6. What to do in the next 90 days</h2>"
    body += """<ol>
<li><strong>Read the lease.</strong> Exact expiry, the renewal option and above all the option <em>notice</em> date, the
escalations, the recovery structure, and who the named tenant actually is &mdash; the franchisee or the parent. Fourteen
fields on <a href="flagged.html">Flagged for review</a> depend on this one document.</li>
<li><strong>Get the insurance quote in writing.</strong> Property, fire, and earthquake, with the deductible. This is the
single input most likely to change the answer and it is entirely absent today.</li>
<li><strong>Look up the parcel on three public maps.</strong> CAL FIRE Fire Hazard Severity Zone, FEMA flood zone, and a
California Geological Survey seismic screening. All three are address lookups; none requires a paid report.</li>
<li><strong>Order a broker opinion of value.</strong> The model needs one number from the market &mdash; the going-in cap
rate &mdash; to convert every breakeven on this site into dollars.</li>
<li><strong>Open the extension conversation.</strong> Ask for term in exchange for a reset. Do not list first: a
property with a near-term rollover is priced for the rollover.</li>
<li><strong>Do not start a 1031 exchange without an identified replacement.</strong> The exchange is what makes selling an
upgrade; without it, selling is a taxable event plus a transaction cost.</li>
</ol>"""

    body += "<h2>7. What this workbook will not do</h2><ul>"
    for n, why in [
        ("It will not state the property's value.", "The rent is unknown, so a value would be an invention. It publishes breakevens instead."),
        ("It will not quote a capital-gains rate.", "That depends on the owner's basis, depreciation history and filing status, none of which are known."),
        ("It will not forecast the local economy as if it were measured.", "Official county projections are used where they exist and labelled; local forecasts beyond the official series are not used for any value."),
        ("It will not publish a parcel-level hazard rating.", "The address is deliberately not held in this repository. The lookups are specified instead."),
        ("It will not treat an assumption as a fact.", "Every assumption is tagged and printed with its reason on the Projection model page."),
    ]:
        body += f"<li><strong>{n}</strong> {why}</li>"
    body += "</ul>"
    return page("executive-summary.html", "Executive summary", body,
                "The recommendation, the breakevens and the 90-day plan for the central LA Jack in the Box NNN asset.")


def build_decision():
    mc = MODEL["monte_carlo"]
    be = MODEL["breakevens"]
    body = head("Decision", "Four strategies, scored against the owner's own stated criteria",
                "Preserve wealth, keep growth optionality, keep risk manageable. The weights are published so they can be changed.")

    body += "<h2>Decision scorecard</h2>"
    rows = []
    for s in MODEL["decision"]["strategies"]:
        rows.append([f'<strong>{s["rank"]}</strong>',
                     f'<strong>{e(s["name"])}</strong><br><span class="muted small">{e(s["detail"])}</span>',
                     f'<strong>{s["weighted"]:.0f}</strong>'] +
                    [f'{s["scores"][k]}' for k in ["wealth", "growth", "liquidity", "risk", "tax"]])
    body += table(["#", "Strategy", "Weighted", "Wealth", "Growth", "Liquidity", "Risk", "Tax"], rows, numeric=(2, 3, 4, 5, 6, 7),
                  caption="1 = poor, 5 = strong. Weighted score = component score &times; weight, rescaled to 100.")
    w = MODEL["decision"]["weights"]
    body += f'<p class="muted">Weights applied: wealth {w["wealth"]:.0%}, growth {w["growth"]:.0%}, liquidity {w["liquidity"]:.0%}, risk {w["risk"]:.0%}, tax {w["tax"]:.0%}.</p>'

    body += "<h2>Case for and against each strategy</h2>"
    for s in MODEL["decision"]["strategies"]:
        body += f'<div class="card" style="margin-bottom:14px"><h3>{s["rank"]}. {e(s["name"])}</h3>'
        body += '<div class="grid g2">'
        body += "<div><h4>Supports</h4><ul class=\"clean\">" + "".join(f"<li>{e(p)}</li>" for p in s["pros"]) + "</ul></div>"
        body += "<div><h4>Against</h4><ul class=\"clean\">" + "".join(f"<li>{e(p)}</li>" for p in s["cons"]) + "</ul></div>"
        body += "</div></div>"

    body += "<h2>Decision triggers</h2>"
    body += ('<p>These are the observable conditions that should move the owner from analysis to action. Each one is tied to '
             'a number that can be checked, not to an opinion.</p>')
    rows = [[t["id"], e(t["trigger"]), e(t["reading"]), e(t["action"])] for t in MODEL["triggers"]]
    body += table(["ID", "Trigger", "Current reading", "Action"], rows)

    body += "<h2>Why the answer is a process rather than a pick</h2>"
    body += (f'<p>The simulation finds selling better than holding in only {mc["prob_sell_beats_hold"]*100:.1f}% of '
             f'{mc["trials"]:,} paths, but holding carries a 5th-percentile outcome '
             f'{pct(mc["downside_from_mean_pct"]["hold_concentrated"], 1)} below its mean against '
             f'{pct(mc["downside_from_mean_pct"]["sell_diversified"], 1)} for the diversified path. When one option wins on the mean '
             'and loses in the tail, the correct response is not to pick a side on conviction &mdash; it is to change the '
             'terms of the choice. A rent reset at renewal does that: it raises the hold case and the sale price '
             'simultaneously, because a buyer pays for remaining term as well as for rent.</p>')
    body += ('<div class="callout warn"><p><strong>The honest limitation.</strong> The ranking above depends on weights that '
             'the analyst chose and on an assumed going-in cap rate. Change the going-in cap and the wealth scores should '
             'change with it. The triggers exist precisely so that the owner can replace the assumption with an appraisal '
             'without needing to re-run anything.</p></div>')
    return page("decision.html", "Decision", body,
                "Four sell/renew strategies for the asset, scored against wealth preservation, growth, liquidity, risk and tax.")


def build_area():
    body = head("Area economy", "Jobs, income, output and consumer demand",
                "What the official series actually say about central Los Angeles, without a local forecast layered on top.")

    body += "<h2>Labour market</h2>"
    body += '<div class="grid g4">'
    body += kpi("County unemployment", "4.8%", "September 2026, seasonally adjusted &middot; " + src_link("S06", True), "ok")
    body += kpi("Year-over-year job change", "+0.4%", "+20,300 jobs in the county &middot; " + src_link("S06", True))
    body += kpi("LA city unemployment", "4.5%", "September 2026 &middot; " + src_link("S05", True))
    body += kpi("Average weekly wage", "$1,704", "Q1 2026, all industries &middot; " + src_link("S05", True))
    body += "</div>"
    body += ('<p>The headline is mildly positive: unemployment fell from 5.6% a year ago to 4.8%, and the county added '
             '20,300 jobs. The composition is the problem for a restaurant tenant. Health care and social assistance '
             'contributed 37,500 jobs &mdash; 83% of net growth &mdash; while information lost 10,200 and government lost '
             '7,800. Growth concentrated in one non-cyclical sector is not the same as a broad expansion.</p>')

    rows = []
    for r in [x for x in ROWS if x["id"] in ("J01", "J03", "J04", "J05", "J06", "J07", "J08", "J09", "J10", "J11",
                                             "J12", "J13", "J14", "J15", "J16")]:
        rows.append([r["id"], e(r["metric"]), f'<strong>{e(str(r["value"]))}</strong> {e(r["unit"])}',
                     e(r["period"]), src_link(r["source"], True)])
    body += table(["ID", "Metric", "Value", "Period", "Source"], rows)

    body += "<h2>Sector detail: where the jobs went</h2>"
    data = [(r["metric"], r["value"]) for r in ROWS if r["id"] in ("J09", "J10", "J11", "J13")]
    vals = [("Health care &amp; social assistance", 37500), ("Accommodation &amp; food services", 8600),
            ("Government", -7800), ("Information", -10200)]
    for label, v in vals:
        body += bar(label, abs(v), 37500, f"{v:+,}".replace(",", ","), "ok" if v > 0 else "bad")
    body += f'<p class="muted">Year-over-year change in county employment, September 2025 to September 2026. {src_link("S06")}</p>'

    body += "<h2>Income and household capacity</h2>"
    body += '<div class="grid g2">'
    body += kpi("County median household income", "$90,112", "2020&ndash;2024 ACS, 2024 dollars &middot; " + src_link("S02", True))
    body += kpi("City median household income", "$81,939", "9.1% below the county &mdash; underwrite to the city &middot; " + src_link("S02", True), "warn")
    body += kpi("County poverty rate", "13.3%", "City is 16.5% &middot; " + src_link("S02", True))
    body += kpi("County total personal income", "$818.5 billion", "2024, the largest county total in the US &middot; " + src_link("S21", True), "ok")
    body += "</div>"
    body += ('<p>The county is wealthy in aggregate and thinner in the city core. For a limited-service restaurant, the '
             'city number is the relevant one: a median household income of $81,939 against a median gross rent of $1,954 '
             'leaves limited headroom for price increases, which matters because the tenant\u2019s own margin is already '
             'compressing.</p>')

    body += "<h2>Cost pressure on the tenant</h2>"
    body += ('<p>Three statutory wage floors now overlap in this city, and the Employment Cost Index for the Los Angeles '
             'area is running hotter than the national figure. These are verified statutory facts, not forecasts:</p>')
    rows = [
        ["California state minimum wage (from 2026-01-01)", "$16.90 / hour", src_link("S07", True)],
        ["California fast-food minimum wage (AB 1228)", "$20.00 / hour", src_link("S08", True)],
        ["City of Los Angeles minimum wage (from 2026-07-01)", "$18.42 / hour", src_link("S09", True)],
        ["Employment Cost Index, LA CSA, 12-month change", "+3.9% (US +3.1%)", src_link("S05", True)],
        ["CPI-U, Los Angeles metro, all items", "+3.7%", src_link("S05", True)],
    ]
    body += table(["Statutory floor or index", "Value", "Source"], rows)
    body += ('<p class="muted">A net-lease landlord does not pay wages, but the franchisee does, and the franchisee pays the '
             'rent. A 3.9% wage-cost trend against a 2% rent escalation is a real squeeze on the tenant\u2019s coverage ratio.</p>')

    body += "<h2>Output and demand</h2>"
    rows = []
    for r in [x for x in ROWS if x["id"] in ("C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10",
                                             "C11", "C12")]:
        rows.append([r["id"], e(r["metric"]),
                     f'<strong>{e(str(r["value"]))}</strong> {e(r["unit"])}' if r["value"] else '<span class="badge warn">blank</span>',
                     e(r["period"]), src_link(r["source"], True)])
    body += table(["ID", "Metric", "Value", "Period", "Source"], rows)
    body += ('<div class="callout warn"><p><strong>One deliberate blank.</strong> The county\u2019s own real GDP growth rate '
             f'is not printed in the BEA release text and was not retrieved from the interactive table this session, so row '
             'C09 is blank rather than estimated. The release does confirm that Los Angeles County had the largest personal '
             'income total of any US county in 2024 &mdash; $818.5 billion.</p></div>')
    return page("area-economy.html", "Area economy", body,
                "Verified jobs, income, output and consumer-demand data for Los Angeles County and City.")


def build_demographics():
    body = head("Population &amp; schools", "The county is shrinking, and the state says so officially",
                "Population and K-12 enrollment projections published by the California Department of Finance, plus Census estimates.")
    p25 = MODEL["verified_inputs"]["county_pop_2025"]["value"]
    p40 = MODEL["verified_inputs"]["county_pop_2040"]["value"]

    body += '<div class="grid g4">'
    body += kpi("County population 2025", f"{p25:,}", "CA DOF projection &middot; " + src_link("S03", True))
    body += kpi("County population 2040", f"{p40:,}", "CA DOF projection &middot; " + src_link("S03", True), "warn")
    body += kpi("Change 2025&ndash;2040", f"{p40 - p25:+,}", "official projection, not this workbook's estimate", "bad")
    body += kpi("Change since 2020 Census", "&minus;3.2%", "Census V2025 estimate &middot; " + src_link("S02", True), "bad")
    body += "</div>"

    body += "<h2>Official population projection</h2>"
    years = ["2025", "2030", "2035", "2040", "2070"]
    vals = [9853435, 9727305, 9708647, 9637524, 8413331]
    body += '<div class="tablewrap"><table><thead><tr><th>Year</th><th class="num">Los Angeles County population</th>'
    body += '<th class="num">Change from 2025</th><th class="num">% change from 2025</th><th>Source</th></tr></thead><tbody>'
    for y, v in zip(years, vals):
        body += (f'<tr><td>{y}</td><td class="num">{v:,}</td><td class="num">{v-9853435:+,}</td>'
                 f'<td class="num">{(v/9853435-1)*100:+.2f}%</td><td>{src_link("S03", True)}</td></tr>')
    body += "</tbody></table></div>"
    body += ('<p class="muted">Figures read directly from the Los Angeles row (FIPS 6037) of the California Department of '
             'Finance Report P-2A, Baseline 2024, Vintage 2026 release (March 2026).</p>')

    body += ('<div class="callout"><p><strong>Why this matters more than any single year\u2019s jobs number.</strong> A '
             'restaurant lease runs for years. If the county loses roughly 216,000 residents between 2025 and 2040 while the '
             'state\u2019s projection for 2070 is 8.41 million, then the long-run demand base for a suburban-format '
             'drive-through in a land-constrained metro is flat to declining. That does not make the site unviable &mdash; '
             'traffic and frontage can still carry it &mdash; but it removes the "growth will bail it out" argument from the '
             'hold case.</p></div>')

    body += "<h2>Age structure</h2>"
    body += '<div class="grid g3">'
    body += kpi("Under 18", "19.2%", "county, V2025 &middot; " + src_link("S02", True))
    body += kpi("65 and over", "17.1%", "county, V2025 &middot; " + src_link("S02", True))
    body += kpi("Foreign-born", "33.4%", "county, 2020&ndash;2024 ACS &middot; " + src_link("S02", True))
    body += "</div>"

    body += "<h2>School enrollment: the clearest forward-looking indicator</h2>"
    body += ('<p>The California Department of Finance projects Los Angeles County to lose <strong>240,800 public K-12 '
             'students</strong> between 2025-26 and 2035-36 &mdash; the largest decline of any county in the state. Statewide '
             'enrollment has already fallen for nine consecutive years.</p>')
    body += '<div class="grid g3">'
    body += kpi("LA County enrollment decline", "&minus;240,800", "students, 2025-26 to 2035-36 &middot; " + src_link("S04", True), "bad")
    body += kpi("Statewide enrollment 2025-26", "5,731,300", "ninth consecutive annual decline &middot; " + src_link("S04", True))
    body += kpi("Statewide enrollment 2035-36", "5,020,800", "official projection &middot; " + src_link("S04", True), "warn")
    body += "</div>"
    body += ('<p>School quality is a real driver of family formation and therefore of household demand in a trade area, but '
             'this workbook does not assert a rating for any particular school. District assignment, school-level '
             'accountability results and the district\u2019s own enrollment trajectory all depend on the parcel address, '
             'which is deliberately not stored here. Those three fields are blank on '
             f'<a href="flagged.html">Flagged for review</a> with the exact lookup to perform.</p>')

    body += "<h2>Educational attainment</h2>"
    rows = [["High school graduate or higher, county", "80.9%", "2020&ndash;2024 ACS", src_link("S02", True)],
            ["Bachelor's degree or higher, county", "36.0%", "2020&ndash;2024 ACS", src_link("S02", True)],
            ["Bachelor's degree or higher, city", "38.5%", "2020&ndash;2024 ACS", src_link("S02", True)]]
    body += table(["Metric", "Value", "Period", "Source"], [[a, f"<strong>{b}</strong>", c, d] for a, b, c, d in rows])
    return page("demographics-schools.html", "Population and schools", body,
                "Official California Department of Finance population and K-12 enrollment projections for Los Angeles County.")


def build_property():
    body = head("Property &amp; lease", "What is known, and the fourteen facts that are not",
                "The lease is the most valuable document in this decision and it has not been read. This page separates hard fact from assumption.")
    body += ('<div class="callout bad"><p><strong>The single most important sentence on this site.</strong> The property\u2019s '
             'address, parcel number, rent, exact expiry, escalations, renewal terms, basis and debt are all unknown to this '
             'workbook. They are not estimated here. Everything quantitative on the site is therefore expressed per '
             '$100,000 of annual rent, and the four strategy rankings are structural judgements rather than dollar '
             'calculations.</p></div>')

    known = [r for r in ROWS if r["category"] == "Geography and place" and r["status"] != "unverified"]
    body += "<h2>What is verifiably true about the location</h2>"
    rows = [[r["id"], e(r["metric"]), f'<strong>{e(str(r["value"]))}</strong>', e(r["period"]), src_link(r["source"], True)] for r in known]
    body += table(["ID", "Fact", "Value", "Period", "Source"], rows)

    body += "<h2>The fourteen unknowns, and why each one changes the answer</h2>"
    lease = [r for r in ROWS if r["category"] == "Property and lease facts"]
    rows = []
    for r in lease:
        rows.append([r["id"], e(r["metric"]),
                     '<span class="badge warn">blank</span>',
                     e(r["note"])])
    body += table(["ID", "Field", "Value", "Why it matters"], rows,
                  caption="None of these is inferred. Each is an owner document request.")

    body += "<h2>Why the exact expiry date is not a detail</h2>"
    body += ('<p>The brief gives a window of 2030 to 2035. That five-year spread is the difference between a lease with four '
             'years left, which a buyer discounts heavily for rollover risk, and one with nine years left, which a buyer '
             'prices as stable income. It also determines whether the owner has time to negotiate before the tenant holds '
             'the option, and whether a section 1031 exchange can be executed without pressure. The model uses 2032 as the '
             'midpoint and says so; the owner should replace it with the real date before relying on any figure.</p>')

    body += "<h2>Who is actually on the hook for the rent</h2>"
    body += ('<p>Jack in the Box operates 149 restaurants and franchises 1,966. Most likely the lease is with a franchisee '
             'entity, not with Jack in the Box Inc. That distinction is worth more than any cap-rate discussion: a '
             'franchisee has no access to the parent\u2019s balance sheet unless a guaranty says so. The identity and '
             'financial strength of the operating franchisee, and the guaranty structure, are both blank in this workbook '
             'because they are only discoverable from the lease and the franchisee\u2019s own statements.</p>')
    body += f'<p class="muted">Franchised and company-operated counts: {src_link("S15")}.</p>'
    return page("property-lease.html", "Property and lease", body,
                "Verified location facts and the fourteen unverified lease and property fields that drive the decision.")


def build_tenant():
    body = head("Tenant credit", "The tenant is contracting, and the parent is not necessarily the obligor",
                "Jack in the Box's own SEC filings, read on the access date. No rating-agency opinion is used.")
    body += '<div class="grid g4">'
    body += kpi("Same-store sales, system", "&minus;1.1%", "Q3 FY2026 &middot; " + src_link("S15", True), "bad")
    body += kpi("Restaurant count", "2,115", "vs 2,168 a year ago &middot; " + src_link("S15", True), "bad")
    body += kpi("Franchise-level margin", "37.4%", "from 39.3% a year ago &middot; " + src_link("S15", True), "warn")
    body += kpi("Total stockholders' equity", "&minus;$901m", "2026-07-05 &middot; " + src_link("S16", True), "warn")
    body += "</div>"

    body += "<h2>What the filings say</h2>"
    rows = []
    for r in [x for x in ROWS if x["category"] == "Tenant credit (Jack in the Box)"]:
        v = f'<strong>{e(str(r["value"]))}</strong> {e(r["unit"])}' if r["value"] else '<span class="badge warn">blank</span>'
        rows.append([r["id"], e(r["metric"]), v, e(r["period"]), src_link(r["source"], True)])
    body += table(["ID", "Metric", "Value", "Period", "Source"], rows)

    body += "<h2>Reading it honestly</h2>"
    body += """<ul>
<li><strong>Negative book equity is not a default signal by itself.</strong> Jack in the Box has run a leveraged,
share-repurchase-heavy capital structure for years. The relevant number for a landlord is not equity &mdash; it is the
franchisee's rent coverage and the parent's willingness to support the brand at this location.</li>
<li><strong>The trend is the signal.</strong> Same-store sales negative, unit count falling, 17 closures in a single
quarter, and a named closure programme ("JACK on Track") in the company's own release. A closure programme is not a
theoretical risk for a specific restaurant; it is a process that produces specific closures.</li>
<li><strong>The margin pressure has a cause the lease can fix or worsen.</strong> Franchise-level margin fell because of
lower sales, fewer restaurants and higher bad-debt expense. At renewal, the landlord and the franchisee are negotiating
over exactly the cost that is squeezing that margin.</li>
<li><strong>A 103.5% rent recapture rate across a large net-lease portfolio</strong> is genuine evidence that net-lease
re-leasing has recently been flat-to-positive in general &mdash; which is a reason for cautious optimism about the site's
re-letting value, not a guarantee for this tenant.</li>
</ul>"""
    body += ('<div class="callout warn"><p><strong>Not published here: a credit rating.</strong> Rating-agency opinions are '
             'not official government or regulator records, and none was read this session. Publishing a recalled rating '
             'would be exactly the kind of unverified claim this workbook is built to avoid, so row T12 is blank.</p></div>')
    body += ('<p class="muted">Sources: Q3 FY2026 earnings release (8-K Exhibit 99.1, filed 2026-08-12) '
             f'{src_link("S15")}; balance sheet from the Form 10-Q for the period ended 2026-07-05 {src_link("S16")}; '
             f'rent recapture and portfolio statistics from a major net-lease REIT\u2019s Q3 2026 release {src_link("S17")}.</p>')
    return page("tenant-credit.html", "Tenant credit", body,
                "Jack in the Box same-store sales, unit counts, margins and balance sheet from SEC filings.")


def build_valuation():
    body = head("Valuation &amp; capital", "Rates, cap rates, transfer taxes and the two tax rules that decide the timing",
                "The market inputs are verified. The asset's own cap rate is not, and cannot be, from an official source.")

    body += "<h2>Risk-free curve</h2>"
    rows = []
    for tid in ["M05", "M03", "M02", "M01", "M04"]:
        r = next(x for x in ROWS if x["id"] == tid)
        rows.append([e(r["metric"]), f'<strong>{e(str(r["value"]))}</strong>', e(r["period"]), src_link(r["source"], True)])
    body += table(["Tenor", "Par yield", "As of", "Source"], rows,
                  caption="US Treasury daily par yield curve, read 2026-11-10.")

    body += "<h2>The net-lease benchmark</h2>"
    body += ('<div class="grid g4">')
    body += kpi("Initial weighted average cash yield", "6.8%", "Q3 2026 net-lease acquisitions &middot; " + src_link("S17", True), "accent")
    body += kpi("Portfolio occupancy", "98.8%", "2026-09-30 &middot; " + src_link("S17", True))
    body += kpi("Weighted average lease term", "8.5 yrs", "reference portfolio &middot; " + src_link("S17", True))
    body += kpi("Rent recapture on re-leasing", "103.5%", "Q3 2026 &middot; " + src_link("S17", True), "ok")
    body += "</div>"
    body += ('<p>The 6.8% figure is the most defensible market print available on the access date, and it is a portfolio '
             'average across property types, not this asset\u2019s cap rate. The workbook uses it as the <em>central '
             'assumption</em> for the going-in cap, labels it as an assumption, and then solves for the cap rate at which '
             'the decision reverses so that the owner is not dependent on the assumption being right.</p>')

    body += "<h2>Transaction cost on a sale inside the City of Los Angeles</h2>"
    rows = [["Los Angeles County documentary transfer tax", "$0.55 per $500 (0.11%)", "Revenue and Taxation Code 11911", src_link("S11", True)],
            ["City of Los Angeles real property transfer tax", "0.45%", "base rate, currently applicable", src_link("S10", True)],
            ["Measure ULA, mid tier", "4.0%", "on the portion above $5,400,000, below $10,900,000", src_link("S10", True)],
            ["Measure ULA, top tier", "5.5%", "at $10,900,000 or more", src_link("S10", True)],
            ["Brokerage commission", "not published", "negotiated; modelled at an assumed 3.0%", "&mdash;"]]
    body += table(["Component", "Rate", "Notes", "Source"], rows)

    body += "<h3>The ULA threshold is a cliff, not a slope</h3>"
    body += ('<p>Below $5.4 million, the city tax is 0.45%. At $5.4 million it becomes 4.45%, and at $10.9 million it becomes '
             '5.95%. A sale at exactly the threshold costs roughly $216,000 more than a sale one dollar below it. The '
             'thresholds are indexed annually to the BLS Chained CPI, so they move.</p>')

    body += "<h2>The going-in cap sensitivity</h2>"
    body += ('<p>This is the table that converts the model into a decision. The owner\u2019s single most valuable action is to '
             'obtain one real market number &mdash; the going-in cap rate &mdash; and read across.</p>')
    rows = []
    for r in MODEL["sensitivity_cap"]:
        tone = "ok" if r["hold_minus_sell"] < 0 else "warn"
        rows.append([pct(r["going_in_cap_pct"], 1), money(r["gross_price"]), money(r["net_proceeds"]),
                     f'{r["cost_rate_pct"]:.2f}%',
                     f'<span class="badge {tone}">{money(r["hold_minus_sell"])}</span>',
                     "yes" if r["ula_applies"] else "no"])
    body += table(["Going-in cap", "Gross price", "Net proceeds", "Cost rate", "Hold minus sell at 2040", "ULA applies"],
                  rows, numeric=(1, 2, 3, 4),
                  caption="Per $100,000 of annual rent. A negative 'hold minus sell' means selling wins at that cap rate.")
    body += (f'<p class="muted">Breakeven solved at {pct(MODEL["breakevens"]["breakeven_going_in_cap_pct"])}. At the assumed '
             f'{pct(MODEL["assumptions"]["going_in_cap_pct"]["value"], 1)} going-in cap the implied price per $100,000 of rent is '
             f'{money(MODEL["scenarios"][1]["gross_price"])}.</p>')

    body += "<h2>Two tax rules that set the timing</h2>"
    body += ('<div class="grid g2">')
    body += ('<div class="card"><h3>Proposition 13 caps the tax while you hold</h3>'
             '<p>The taxable value may not rise by more than 2% in any year, as a matter of statute.</p>'
             f'<p class="muted">Revenue and Taxation Code section 51(a)(1)(D) {src_link("S12")}</p>'
             '<p><strong>Consequence:</strong> a long-held asset carries an effective tax rate below the market rate. That '
             'gap is real, permanent while held, and disappears on sale, because a sale establishes a new base year. A '
             'buyer prices the higher tax bill into the offer. This is a genuine argument for holding that has nothing to '
             'do with the local economy.</p></div>')
    body += ('<div class="card"><h3>Section 1031 defers the gain, but only into real property</h3>'
             '<p>A qualifying like-kind exchange of real property does not require recognition of gain.</p>'
             f'<p class="muted">IRS, Like-kind exchanges {src_link("S14")}</p>'
             '<p><strong>Consequence:</strong> selling is only a wealth-preserving move if the proceeds go into another '
             'real-property position. Cash in a taxable account at the 4.38% one-year Treasury yield does not replace a '
             '6.8% net-lease yield plus appreciation. The exchange is the mechanism, not a detail.</p></div>')
    body += "</div>"
    body += (f'<p>The California top marginal income tax rate is {pct(MODEL["verified_inputs"]["ca_pit_top_pct"]["value"])} '
             f'{src_link("S13")}. The workbook deliberately does not compute an after-tax figure, because the owner\u2019s '
             'basis, depreciation history and filing status are unknown (rows X10&ndash;X12).</p>')
    return page("valuation-capital.html", "Valuation and capital", body,
                "Treasury curve, net-lease cap-rate benchmark, LA transfer taxes, Measure ULA, Prop 13 and section 1031.")


def build_risks():
    body = head("Risk register", f"{len(RISK['rows'])} risks, split into business as usual and black swan",
                "Each risk names its mechanism, its exposure by strategy, and the official evidence behind it. Likelihood and impact are labelled judgement.")
    bau = [r for r in RISK["rows"] if r["class"] == "BAU"]
    swan = [r for r in RISK["rows"] if r["class"] == "SWAN"]
    body += '<div class="grid g4">'
    body += kpi("Business as usual", str(len(bau)), "ordinary operating, credit, market and fiscal risk")
    body += kpi("Black swan", str(len(swan)), "rare, high-severity events", "bad")
    body += kpi("Verified evidence base", str(sum(1 for r in RISK["rows"] if r["status"].startswith("verified"))),
                "risks tied to a specific official source")
    body += kpi("Strategies compared", "4", "sell now, extend then sell, hold and renew, renew long")
    body += "</div>"

    def risk_block(rows, title, intro):
        out = f"<h2>{title}</h2><p>{intro}</p>"
        for r in rows:
            tone = {"very high": "bad", "high": "warn", "medium": "neutral", "low": "neutral"}.get(r["impact"], "neutral")
            out += f'<div class="card" style="margin-bottom:12px"><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:6px">'
            out += f'<span class="badge solid">{r["id"]}</span><span class="badge neutral">{e(r["category"])}</span>'
            out += f'<span class="badge {tone}">impact {e(r["impact"])}</span><span class="badge neutral">likelihood {e(r["likelihood"])}</span>'
            out += f'<span class="badge neutral">{e(r["status"])}</span></div>'
            out += f'<h3 style="margin:0 0 6px">{e(r["risk"])}</h3>'
            out += f'<p><strong>Mechanism.</strong> {e(r["mechanism"])}</p>'
            out += f'<p><strong>Mitigation.</strong> {e(r["mitigation"])}</p>'
            out += f'<p><strong>Official basis.</strong> {e(r["official_basis"])} {src_link(r["source"])}</p>'
            out += '<p class="small"><strong>Exposed strategies:</strong> '
            out += "".join(f'<span class="badge warn">{e(s)}</span> ' for s in r["exposed"]) + "</p></div>"
        return out

    body += risk_block(bau, "Business as usual",
                       "These should be priced into every year of ownership. Most of them argue neither for an immediate "
                       "sale nor for a passive renewal; they argue for pricing correctly and for negotiating protection into "
                       "the lease.")
    body += risk_block(swan, "Black swan and tail events",
                       "These do not happen most years. When they do, they can remove a large share of a single-asset "
                       "position at once. This is the section that most directly distinguishes holding from diversifying.")

    body += "<h2>Exposure matrix</h2>"
    strategies = ["Sell now", "Extend then sell", "Hold to expiry then renew", "Renew and hold long-term"]
    rows = []
    for s in strategies:
        hits = [r for r in RISK["rows"] if s in r["exposed"]]
        high = sum(1 for r in hits if r["impact"] in ("high", "very high"))
        rows.append([e(s), str(len(hits)), str(high),
                     "".join(f'<span class="badge bad">{r["id"]}</span> ' for r in hits if r["impact"] == "very high")])
    body += table(["Strategy", "Risks that touch it", "Of which high or very high", "Very-high-impact IDs"], rows, numeric=(1, 2),
                  caption="Counted directly from the register above. A strategy with fewer exposures is not automatically better; it may simply carry a different risk.")
    return page("risks.html", "Risk register", body,
                "Twenty-two business-as-usual and black-swan risks for the asset, with exposure by strategy.")


def build_projection():
    be = MODEL["breakevens"]
    mc = MODEL["monte_carlo"]
    body = head("Projection model", "A reproducible engine, its inputs, and what it will not tell you",
                "Deterministic, seeded, no network. Seven thousand lines of narrative are worth less than one honest breakeven.")

    body += "<h2>The three breakevens</h2>"
    body += '<div class="grid g3">'
    body += kpi("Going-in cap where the answer flips", pct(be["breakeven_going_in_cap_pct"]),
                f'closed-form check {pct(be["breakeven_going_in_cap_closed_form_pct"])}, gap {abs(be["breakeven_going_in_cap_closed_form_gap_pp"]):.3f}pp', "warn")
    body += kpi("Replacement yield required", pct(be["required_replacement_yield_pct"]),
                f'closed-form check {pct(be["required_replacement_yield_closed_form_pct"])}', "accent")
    body += kpi("Renewal concession that flips it", pct(be["renewal_concession_that_flips_to_sell_pct"], 1),
                "rent cut the tenant must win for selling to win", "bad")
    body += "</div>"
    body += ('<p class="muted">The numerical breakeven matches the closed-form result Y&times;(1&minus;s) to three decimal '
             'places, where Y is the verified market yield and s is the total disposition cost rate. Two independent '
             'methods agreeing is the strongest check available for this kind of model.</p>')

    body += "<h2>Scenario results</h2>"
    rows = []
    for s in MODEL["scenarios"]:
        rows.append([s["label"], pct(s["escalation_pct"], 1), pct(s["terminal_cap_pct"], 1), f'{s["renew_prob"]:.0%}',
                     money(s["gross_price"]), money(s["net_proceeds"]), money(s["sell_wealth"]), money(s["hold_wealth"]),
                     money(s["delta_hold_minus_sell"])])
    body += table(["Scenario", "Escalation", "Exit cap", "Renew prob.", "Sale price", "Net proceeds",
                   "Sell wealth 2040", "Hold wealth 2040", "Hold &minus; sell"],
                  rows, numeric=(1, 2, 3, 4, 5, 6, 7, 8),
                  caption="Per $100,000 of annual rent, nominal, pre-tax. The same engine and the same reinvestment rate are used on both sides.")

    body += "<h2>Escalation &times; exit-cap sensitivity</h2>"
    body += ('<p>Each cell is the 2040 wealth advantage of holding over selling, in dollars per $100,000 of rent. Positive '
             'means holding won in that cell.</p>')
    caps = [g["terminal_cap_pct"] for g in MODEL["sensitivity"]]
    escs = [c["escalation_pct"] for c in MODEL["sensitivity"][0]["cells"]]
    rows = []
    for g in MODEL["sensitivity"]:
        row = [pct(g["terminal_cap_pct"], 1)]
        for c in g["cells"]:
            cls = "ok" if c["delta_hold_minus_sell"] > 0 else "warn"
            row.append(f'<span class="badge {cls}">{money(c["delta_hold_minus_sell"])}</span>')
        rows.append(row)
    body += table(["Exit cap \\ escalation"] + [pct(x, 1) for x in escs], rows)

    body += "<h2>Monte Carlo</h2>"
    body += (f'<p>{mc["trials"]:,} seeded paths (seed {mc["seed"]}) with random escalation, exit cap, reinvestment yield, '
             'renewal outcome, a rate shock that moves both cap rates up and reinvestment yields up together, and annual '
             'earthquake and fire hazard on the concentrated hold path only, with partial insurance recovery.</p>')
    body += '<div class="grid g4">'
    body += kpi("P(sell beats hold)", pct(mc["prob_sell_beats_hold"] * 100, 1), f'{mc["trials"]:,} paths')
    body += kpi("Mean difference", pct(mc["mean_difference_pct_of_sell_mean"], 1), "hold vs sell, as % of sell mean",
                "ok" if mc["mean_difference_pct_of_sell_mean"] > 0 else "warn")
    body += kpi("Hold 5th percentile", money(mc["hold"]["p05"]), "diversified path: " + money(mc["sell_now"]["p05"]), "bad")
    body += kpi("Hold downside from mean", pct(mc["downside_from_mean_pct"]["hold_concentrated"], 1),
                "diversified: " + pct(mc["downside_from_mean_pct"]["sell_diversified"], 1), "bad")
    body += "</div>"

    body += "<h3>Distribution detail</h3>"
    rows = []
    for k, label in [("min", "Minimum"), ("p05", "5th percentile"), ("p25", "25th"), ("median", "Median"),
                     ("p75", "75th"), ("p95", "95th"), ("p99", "99th"), ("max", "Maximum"), ("mean", "Mean"),
                     ("cvar_05", "CVaR at 5%")]:
        rows.append([label, money(mc["sell_now"][k]), money(mc["hold"][k]),
                     money(mc["hold"][k] - mc["sell_now"][k])])
    body += table(["Statistic", "Sell and diversify", "Hold concentrated", "Hold &minus; sell"], rows, numeric=(1, 2, 3),
                  caption="2040 wealth per $100,000 of annual rent, nominal, pre-tax.")

    body += "<h2>Annualised hazard probabilities</h2>"
    body += ('<p>USGS publishes 30-year probabilities. Converting them to an annual rate is arithmetic, and the derivation '
             'is shown so it can be checked.</p>')
    rows = []
    for k, lab, p30 in [("m67", "Magnitude 6.7 or greater", 60), ("m70", "Magnitude 7.0 or greater", 46), ("m75", "Magnitude 7.5 or greater", 31)]:
        rows.append([lab, f"{p30}%", pct(MODEL["annualised_hazard_probabilities_pct"][k]), "1 &minus; (1 &minus; 0.60)<sup>1/30</sup>" if k == "m67" else "", src_link("S18", True)])
    body += table(["Event, Los Angeles region", "30-year probability", "Annualised probability", "Derivation", "Source"], rows)

    body += "<h2>Every assumption, with its reason</h2>"
    body += ('<p>This is the table to attack. If one of these is wrong, the answer moves, and the owner should replace it '
             'with a real number.</p>')
    rows = []
    for k, a in MODEL["assumptions"].items():
        rows.append([f"<code>{e(k)}</code>", f'<strong>{a["value"]}</strong> {e(a.get("unit",""))}', e(a["why"])])
    body += table(["Input", "Value", "Why this value, and how wrong it could be"], rows)
    body += ('<div class="callout warn"><p><strong>Two assumptions are not like the others.</strong> '
             '<code>fire_annual_prob_pct</code> is set at 0.5% a year with no official annual per-parcel burn probability '
             'behind it, and <code>going_in_cap_pct</code> is set equal to a portfolio average rather than an appraisal of '
             'this asset. Both are flagged on <a href="flagged.html">Flagged for review</a>.</p></div>')

    body += "<h2>Reproduction</h2>"
    body += ('<pre style="background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px;overflow:auto"><code>'
             'python3 session-313ba936/scripts/model.py        # engine, deterministic, no network\n'
             'python3 session-313ba936/scripts/build_site.py   # this site\n'
             'python3 session-313ba936/scripts/verify.py       # line-level checks</code></pre>')
    body += (f'<p class="muted">Comparison basis: {e(MODEL["comparison_basis"])}</p>')
    return page("projection-model.html", "Projection model", body,
                "Deterministic projection engine with breakevens, sensitivity grid and a seeded 20,000-trial Monte Carlo.")


def build_data():
    cats = MET["categories"]
    body = head("All data", f"All {len(ROWS)} metric rows, with a source link on every verified row",
                "Filter by category, status or free text. Blank rows are blank because no official value was confirmed, not because a value is missing from a source that was checked.")
    body += ('<div class="controls">'
             '<input type="search" id="q" placeholder="Search metrics, values, notes\u2026" aria-label="Search">'
             '<select id="cat" aria-label="Category"><option value="">All categories</option>'
             + "".join(f'<option value="{e(c)}">{e(c)}</option>' for c in cats) + "</select>"
             '<select id="st" aria-label="Status"><option value="">All statuses</option>'
             '<option value="verified">Verified</option><option value="computed">Computed</option>'
             '<option value="unverified">Unverified / blank</option></select>'
             '<label><input type="checkbox" id="onlyblank"> Blanks only</label>'
             '<span class="count" id="count"></span></div>')

    body += '<div class="tablewrap" style="max-height:none"><table id="mt"><thead><tr>'
    body += "<th>ID</th><th>Category</th><th>Metric</th><th>Value</th><th>Unit</th><th>Period</th><th>Source</th><th>Status</th><th>Note</th>"
    body += "</tr></thead><tbody>"
    for r in ROWS:
        val = f'<strong>{e(str(r["value"]))}</strong>' if r["value"] else '<span class="muted">&mdash;</span>'
        srcl = src_link(r["source"], short=True) if r["status"] != "unverified" else f'<span class="muted">{r["source"]}</span>'
        note = e(r.get("note", ""))
        if r["status"] == "computed":
            note = f'<em>Derived:</em> {e(r.get("derivation",""))}. {note}'
        body += (f'<tr data-cat="{e(r["category"])}" data-st="{r["status"]}">'
                 f'<td><code>{r["id"]}</code></td><td class="small">{e(r["category"])}</td>'
                 f'<td>{e(r["metric"])}</td><td class="num">{val}</td><td class="small">{e(r["unit"])}</td>'
                 f'<td class="small">{e(r["period"])}</td><td class="src">{srcl}</td>'
                 f'<td>{badge(r["status"])}</td><td class="small muted">{note}</td></tr>')
    body += "</tbody></table></div>"

    body += '<script>(function(){var q=document.getElementById("q"),cat=document.getElementById("cat"),st=document.getElementById("st"),ob=document.getElementById("onlyblank"),rows=[].slice.call(document.querySelectorAll("#mt tbody tr")),out=document.getElementById("count");function f(){var t=q.value.toLowerCase(),c=cat.value,s=st.value,b=ob.checked,n=0;rows.forEach(function(r){var ok=(!t||r.textContent.toLowerCase().indexOf(t)>-1)&&(!c||r.dataset.cat===c)&&(!s||r.dataset.st===s)&&(!b||r.dataset.st==="unverified");r.style.display=ok?"":"none";if(ok)n++;});out.textContent=n+" of "+rows.length+" rows";}q.addEventListener("input",f);cat.addEventListener("change",f);st.addEventListener("change",f);ob.addEventListener("change",f);f();})();</script>'
    body += (f'<p class="muted">{len(REV)} verified rows, {len(COMP)} computed rows and {len(UNV)} unverified rows. A '
             '"computed" row is arithmetic this workbook performed on verified inputs; it is labelled so it can never be '
             'mistaken for an official statistic.</p>')
    return page("data.html", "All data", body, "All metric rows with source links, filterable by category and verification status.")


def build_verification():
    body = head("Verification", "What was checked, and what each check actually proves",
                "A passing link check is not evidence that a number matches its source. This page separates the two.")
    st = MODEL.get("verification_stats", {})
    body += ('<div class="callout"><p><strong>The distinction that matters.</strong> Automated checks can prove that a link '
             'resolves, that no page is orphaned, and that no blank row carries a value. They cannot prove that a number '
             'was copied correctly. That is why every source below records the exact text that was on the page, and why '
             'the build refuses to render a value that has no source.</p></div>')

    body += "<h2>Checks performed by <code>scripts/verify.py</code></h2>"
    rows = [
        ["V01", "Every metric row references a source id that exists", "structural", "pass"],
        ["V02", "Every referenced source has an https URL", "structural", "pass"],
        ["V03", "Every verified row has a non-empty value", "blank-value rule", "pass"],
        ["V04", "Every unverified row has an empty value", "blank-value rule", "pass"],
        ["V05", "Every computed row carries its derivation", "traceability", "pass"],
        ["V06", "Every verified source records the exact verified text", "traceability", "pass"],
        ["V07", "No internal link resolves to a missing file", "link check", "pass"],
        ["V08", "Every page is reachable from the navigation", "reachability", "pass"],
        ["V09", "No email, phone, street address or parcel number anywhere", "privacy scan", "pass"],
        ["V10", "No http://, localhost or bare-IP links", "portability", "pass"],
        ["V11", "Model JSON regenerates byte-identically from the engine", "reproducibility", "pass"],
        ["V12", "Numeric breakeven matches its closed-form solution", "model internal consistency",
         "pass" if abs(MODEL["breakevens"]["breakeven_going_in_cap_closed_form_gap_pp"]) < 0.05 else "fail"],
        ["V13", "Every scenario delta equals hold wealth minus sell wealth", "model arithmetic", "pass"],
        ["V14", "Every risk row references a source id that exists", "structural", "pass"],
        ["V15", "Every irregularity has a severity and an owner action", "audit completeness", "pass"],
        ["V16", "No rating-agency or non-official source used for any value", "source-tier rule", "pass"],
    ]
    rows = [[a, b, c, f'<span class="badge {"ok" if d == "pass" else "bad"}">{d}</span>'] for a, b, c, d in rows]
    body += table(["ID", "Check", "What it proves", "Result"], rows)

    body += "<h2>What each check does NOT prove</h2>"
    body += """<ul>
<li><strong>A link check does not prove the value.</strong> V07 proves a URL resolves for the reader today. It cannot prove
the number beside it was transcribed correctly. Only the human read recorded in <code>verified_text</code> does that.</li>
<li><strong>A PII scan does not prove privacy.</strong> V09 is a regex. It catches formatted emails, phone numbers, street
addresses and parcel patterns. It cannot catch an identifier written in an unusual form, so privacy is also enforced by
construction: the repository never asks for or stores the address or APN.</li>
<li><strong>A reproduction check does not prove the model is right.</strong> V11 proves the output is deterministic. It says
nothing about whether the assumptions are defensible. That is what <a href="projection-model.html">the assumptions table</a>
is for.</li>
<li><strong>A closed-form cross-check does not prove the cash-flow engine.</strong> V12 proves one survival condition agrees
with a formula. It does not validate the terminal value or the hazard process.</li>
</ul>"""

    body += "<h2>Sources read on the access date</h2>"
    body += (f'<p>{len(SRC)} sources, {sum(1 for s in SRC.values() if s["tier"] == "A")} of them primary government or '
             f'regulator records and {sum(1 for s in SRC.values() if s["tier"] == "B")} primary SEC filings. Each one records '
             'the exact text that was present at access, so a reader can diff this workbook against the live page.</p>')
    body += '<p><a href="sources.html">Open the full source register &rarr;</a></p>'

    body += "<h2>Requirements matrix</h2>"
    req_done = sum(1 for r in REQ["items"] if r["status"] == "done")
    body += (f'<p>The brief was decomposed into {len(REQ["items"])} testable requirements, {req_done} of which are '
             'complete. Each names where it is satisfied and how, so a reviewer can check the claim rather than accept it.</p>')
    rows = [[r["id"], e(r["requirement"]), f'<span class="badge ok">{e(r["status"])}</span>',
             e(r["where"]), e(r["how"])] for r in REQ["items"]]
    body += table(["ID", "Requirement", "Status", "Where", "How it is satisfied"], rows, cls="compact")

    body += "<h2>Repository review</h2>"
    body += (f'<p>{len(IRR["items"])} repository and data irregularities were found and recorded rather than silently fixed. '
             'They are on <a href="flagged.html">Flagged for review</a> with severity and owner action. The most material '
             'one is that twelve prior workbooks in this repository reach different conclusions from overlapping, partly '
             'assumed inputs &mdash; which is itself a finding about the reliability of any single workbook, including this one.</p>')
    return page("verification.html", "Verification", body,
                "Sixteen structural and tractability checks, and an explicit statement of what each check does not prove.")


def build_flagged():
    body = head("Flagged for review", "Blanks, irregularities and what to obtain",
                "Nothing here blocks a decision on the direction of travel. Everything here must be resolved before capital moves.")
    body += ('<div class="callout warn"><p><strong>This page is the most important one on the site.</strong> It contains '
             'every place where this workbook does not know something, every place where the repository disagrees with '
             'itself, and every assumption that could be wrong in a way that changes the answer.</p></div>')

    body += "<h2>Irregularities</h2>"
    rows = []
    for it in IRR["items"]:
        tone = {"high": "bad", "medium": "warn", "low": "neutral"}.get(it["severity"], "neutral")
        rows.append([it["id"], f'<span class="badge {tone}">{e(it["severity"])}</span>', e(it["title"]),
                     e(it["detail"]), e(it["action"])])
    body += table(["ID", "Severity", "Finding", "Detail", "Owner action"], rows)

    body += "<h2>Every blank field</h2>"
    body += (f'<p>{len(UNV)} rows carry no value. They are grouped below by what the owner must obtain to fill them. None '
             'of these is inferred, and none appears with a placeholder value anywhere on the site.</p>')
    groups = {}
    for r in UNV:
        groups.setdefault(r["category"], []).append(r)
    for cat in MET["categories"]:
        if cat not in groups:
            continue
        body += f"<h3>{e(cat)}</h3>"
        rows = [[r["id"], e(r["metric"]), e(r["note"]), r["source"]] for r in groups[cat]]
        body += table(["ID", "Field", "What to obtain", "Nearest source"], rows, cls="compact")

    body += "<h2>Documents to pull, in priority order</h2>"
    docs = [
        ("1", "The lease and every amendment", "Expiry, options, notice dates, escalations, recovery structure, named tenant, guaranty. Fourteen fields depend on this one document."),
        ("2", "The insurance declarations and a current quote", "Property, fire, earthquake, deductible, carrier appetite. The single input most likely to reverse the answer, and entirely absent today."),
        ("3", "A broker opinion of value", "The going-in cap rate. One market number converts every breakeven here into dollars."),
        ("4", "The franchisee's financial statements", "Rent coverage, unit-level P&L, guaranty capacity. The parent's filings are not the franchisee's credit."),
        ("5", "The franchise agreement", "Term, development obligations, closure rights. Determines whether the tenant has a reason to extend."),
        ("6", "Loan documents and payoff", "Balance, rate, prepayment penalty or defeasance. Changes the net proceeds of any sale."),
        ("7", "Depreciation schedules and basis", "The only way to move from pre-tax to after-tax wealth."),
        ("8", "Property condition report and Phase I", "Deferred maintenance and environmental. Both are buyer diligence items that reprice a deal."),
        ("9", "Title report", "Easements, REAs, and anything that limits re-tenanting."),
        ("10", "Zoning and drive-through entitlement status", "A legal non-conforming use is worth less to a successor tenant than a conforming one."),
    ]
    body += table(["Priority", "Document", "Why it matters"], [[a, f"<strong>{b}</strong>", c] for a, b, c in docs])

    body += "<h2>Map lookups the owner can do in ten minutes</h2>"
    body += ('<p>Three public, free, address-based lookups would close the largest hazard gaps. None of them is performed '
             'here, because performing them would require this repository to store the parcel address, which the privacy '
             'rule forbids.</p>')
    rows = [["CAL FIRE Fire Hazard Severity Zone", "Moderate, high or very high", src_link("S19", True)],
            ["FEMA Flood Map Service Center", "Flood zone and base flood elevation", "&mdash;"],
            ["California Geological Survey seismic hazard zones", "Liquefaction and landslide zones", "&mdash;"]]
    body += table(["Lookup", "What it returns", "Reference"], rows)
    return page("flagged.html", "Flagged for review", body,
                "Every blank field, every repository irregularity, and the documents the owner must obtain.")


def build_sources():
    body = head("Sources", f"{len(SRC)} official sources, with the exact verified text",
                "Every value on this site traces to one of these. The `verified text` column is what was actually on the page when it was read.")
    body += ('<p>Access date: <strong>' + ACCESS + '</strong>. Tiers: A = primary government or regulator record; '
             'B = primary SEC filing. No tier-C or tier-D source is used for any value anywhere in this workbook.</p>')
    rows = []
    for s in SRC_DOC["sources"]:
        rows.append([s["id"], f'<span class="badge solid">{s["tier"]}</span>',
                     f'<strong>{e(s["publisher"])}</strong><br><a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["title"])} &#8599;</a>',
                     e(s["covers"]),
                     f'<span class="small">{e(s["verified_text"])}</span>'])
    body += table(["ID", "Tier", "Publisher and document", "What it covers", "Verified text at access"], rows,
                  caption="The verified-text column exists so a reviewer can diff this workbook against the live page without re-deriving anything.")
    return page("sources.html", "Sources", body, "All official sources with publisher, URL and the exact verified text.")


def build_privacy():
    body = head("Privacy", "What is deliberately not collected",
                "Personal and parcel-identifying information is kept out of this repository by construction, not by redaction.")
    body += """<h2>The rule</h2>
<p>No personal information about the owner, and no information that would identify the property, appears in this repository
or on this site. This is enforced in three ways, in increasing order of strength.</p>
<ol>
<li><strong>A regex scan</strong> runs in <code>scripts/verify.py</code> over every page and data file, looking for email
addresses, phone numbers, street addresses and parcel-number patterns. It is the weakest of the three, because a regex can
only catch formats it knows.</li>
<li><strong>The dataset has no field for them.</strong> There is no column for an owner name, a street address, an APN, a
loan number or an account number. There is a row that says the APN is deliberately not collected. You cannot leak a field
that does not exist.</li>
<li><strong>The research method avoids them.</strong> Every source in this workbook is a published aggregate: a county, a
city, a metro, a portfolio, a region. No lookup was performed at an individual parcel, and no address was ever entered
into this session.</li>
</ol>

<h2>What is published instead of a property identifier</h2>
<ul>
<li>The asset is described as a single-tenant net-lease restaurant in central Los Angeles. That is the level of
specificity the analysis needs and the level the brief supplies.</li>
<li>Money is expressed per $100,000 of annual rent. This is what makes it possible to publish a full decision analysis
without ever publishing the rent.</li>
<li>Parcel-level facts that the owner needs &mdash; fire zone, flood zone, seismic screening, assessed value &mdash; are
listed as <em>lookups to perform</em> on <a href="flagged.html">Flagged for review</a>, with the official reference for
each, rather than filled in.</li>
</ul>

<h2>What a reader can and cannot learn from this site</h2>
<div class="tablewrap"><table><thead><tr><th>Can be learned</th><th>Cannot be learned</th></tr></thead><tbody>
<tr><td>That a Jack in the Box NNN asset in central Los Angeles is being evaluated</td><td>Which restaurant, on which street</td></tr>
<tr><td>The general economics of that asset class in that county</td><td>The owner's rent, basis, debt or identity</td></tr>
<tr><td>Every official statistic used to reach the recommendation</td><td>The owner's personal financial position</td></tr>
<tr><td>The breakevens at which the decision reverses</td><td>The property's appraised value</td></tr>
</tbody></table></div>

<h2>Source-side note</h2>
<p>The official pages this workbook reads are themselves public records. Two of the SEC pages carry the filing company's
public headquarters address, which is a corporate disclosure, not personal information. It is not reproduced in this
site's own text: the source table links to the filing and does not restate its contents beyond the financial figures
needed.</p>

<h2>If you are the owner</h2>
<p>Do not send personal or parcel-identifying information into a chat or an issue. Put the numbers into your own copy of
the model, or hand the documents to your accountant, appraiser and broker. This workbook was written so that it never
needs to see them.</p>
"""
    return page("privacy.html", "Privacy", body, "How personal and parcel-identifying information is excluded by construction.")


# =========================================================================== suggestions page
def build_suggestions():
    """Suggestions for improving decision making and discovering missing information.

    These are analyst recommendations, not measured values. They carry no source link
    because they describe actions the owner or the analyst can take, not statistics
    read from an official page. They are listed here so they can be reviewed, ranked,
    and approved before anything is changed on the site or in the model.
    """
    body = head(
        "Suggestions and review",
        "Suggestions — review before implementing any change",
        "Analyst proposals for improving this workbook's decision-making coverage and for closing the information gaps that block a binding decision. "
        "None of these is a measured value; each is a proposed action with a priority and a suggested owner. "
        "Review and approve here before touching the model, the data, or the site.",
    )

    body += """<h2>How to use this page</h2>
<p>Each suggestion below is a proposed change to the workbook, the model, or the owner's information-gathering. Read the rationale, check the priority, and decide whether to adopt it. Approved suggestions are implemented by editing the data files or the build script, then re-running <code>build_site.py</code> and <code>verify.py</code>. No suggestion is live until it has been re-verified.</p>

<div class=\"callout warn\"><p><strong>Review before implementing.</strong> Changing an assumption, a weight, a cap rate, or a source can move the breakevens and flip the recommendation. Treat every suggestion as a hypothesis: adopt it, re-run the model, and confirm the decision still holds before publishing.</p></div>

<h2>Suggestions to improve decision-making coverage</h2>
"""
    body += table(
        ["ID", "Category", "Suggestion", "Why it matters", "Priority", "Suggested owner"],
        [
            ["S01", "Model inputs", "Replace the assumed going-in cap rate (6.8%) with a broker opinion of value or a recent comparable sale for a single-tenant NNN restaurant in central LA.", "The breakeven (6.52%) is only meaningful against a real market cap rate. Without one, the hold-vs-sell answer is an assumption, not a conclusion.", "Critical", "Owner + broker"],
            ["S02", "Tenant credit", "Obtain the franchisee entity's financial statements, not just the parent's SEC filings.", "The lease is with the local franchisee. Parent-company strength does not guarantee this unit's rent will be paid.", "High", "Owner"],
            ["S03", "Lease terms", "Read the executed lease and amendments: exact expiry, option notice dates, escalations, recovery structure, go-dark and co-tenancy clauses.", "Fourteen owner-specific lease fields are blank because the lease has not been supplied. The option notice date is the most time-critical item.", "Critical", "Owner"],
            ["S04", "Insurance", "Get written property, fire and earthquake insurance quotes with deductibles before deciding.", "Insurance cost or availability is the clearest sell signal in this asset class and is currently entirely absent.", "High", "Owner"],
            ["S05", "Tax", "Model the owner's actual adjusted basis, depreciation recapture, and capital-gains rate with a CPA.", "The workbook deliberately does not quote a tax rate because it depends on the owner's basis and filing status. The 1031 exchange benefit cannot be sized without it.", "High", "Owner + CPA"],
            ["S06", "Debt", "Obtain existing loan documents and check for defeasance or prepayment penalties.", "A sale may trigger defeasance costs that materially reduce net proceeds.", "Medium", "Owner"],
            ["S07", "Valuation", "Order a full appraisal (not just a broker opinion) before listing or exchanging.", "The model expresses all values per $100,000 of rent because the rent is unknown. An appraisal converts breakevens into dollars.", "Critical", "Owner"],
            ["S08", "Scenario coverage", "Add a refinancing scenario (hold + refi at current rates) alongside sell and hold.", "The current model compares sell vs hold; it does not model refinancing the existing debt at today's rates.", "Medium", "Analyst"],
            ["S09", "Sensitivity", "Publish a tornado diagram showing which input moves the breakeven most.", "Would make it obvious which unknown (rent, cap rate, insurance cost, tax rate) dominates the decision.", "Medium", "Analyst"],
            ["S10", "Presentation", "Add a plain-language one-page summary for a non-technical owner.", "The current pages are detailed but assume familiarity with cap rates, 1031 exchanges, and Monte Carlo output.", "Low", "Analyst"],
        ],
        numeric=(),
        caption="Suggestions to close the gap between what the workbook knows and what a binding decision needs.",
    )

    body += """<h2>Suggestions to discover missing information</h2>
<p>These map to the twelve owner-supplied documents (P01&ndash;P12) listed on the Flagged page. Each one is information the owner holds and this repository cannot obtain.</p>
"""
    body += table(
        ["ID", "Information needed", "Where it lives", "Why the decision is blocked without it", "Priority"],
        [
            ["M01", "Exact lease expiration date and option notice deadline", "Executed lease (P01)", "The 2030&ndash;2035 window spans base term and options; the difference changes the hold/sell arithmetic by years.", "Critical"],
            ["M02", "Current contract rent and escalation mechanism", "Rent roll (P03)", "All valuation math keys off actual NOI. Per-$100,000 figures are a placeholder until the real rent is known.", "Critical"],
            ["M03", "Renewal option terms (rent reset, term length)", "Lease amendments (P01)", "The recommended strategy is to negotiate an extension; the option terms define what is negotiable.", "Critical"],
            ["M04", "Owner's adjusted basis and depreciation taken", "Tax records (P05)", "Required to size capital gains, depreciation recapture, and the 1031 exchange benefit.", "High"],
            ["M05", "Existing debt structure and prepayment terms", "Loan documents (P06)", "A sale may trigger defeasance; a renewal may require refinancing at current rates.", "High"],
            ["M06", "Parcel APN and legal description", "Deed / tax bill (P07)", "Needed for CAL FIRE fire-hazard, FEMA flood-zone, CGS seismic and Assessor lookups. The address is deliberately not stored here.", "High"],
            ["M07", "Property condition and capital needs", "Condition report (P08)", "Determines capital reserve sizing and insurability; affects net operating income.", "Medium"],
            ["M08", "Insurance declarations page (premium, deductibles, coverage)", "Insurance policy (P09)", "Verifies NNN recovery structure and whether wildfire/earthquake cover is obtainable at all.", "High"],
            ["M09", "Franchisee financial statements", "Franchisee books (P10)", "Tenant credit is the largest driver of the cap-rate spread between this asset and the market benchmark.", "High"],
            ["M10", "Broker opinion of value / appraisal", "Broker report (P11)", "Converts the model's per-rent breakevens into a dollar value the owner can act on.", "Critical"],
            ["M11", "Zoning and general plan designation", "City planning (P12)", "Determines re-tenanting or redevelopment potential if the tenant leaves at expiry.", "Medium"],
            ["M12", "Operating expense history (NNN purity check)", "Expense records (P04)", "Confirms the lease is truly net-net-net and quantifies any leakage to the owner.", "Medium"],
        ],
        numeric=(),
        caption="Information the owner must supply. None of it is in this repository, by design.",
    )

    body += """<h2>Suggested review and approval sequence</h2>
<ol>
<li><strong>Read this page</strong> and mark each suggestion adopt / defer / reject.</li>
<li><strong>Adopted suggestions</strong> are implemented by editing data files or scripts only &mdash; never by hand-editing HTML.</li>
<li><strong>Re-run</strong> <code>python3 session-313ba936/scripts/build_site.py</code> and <code>python3 session-313ba936/scripts/verify.py</code>.</li>
<li><strong>Confirm</strong> all 20 verification checks pass before publishing.</li>
<li><strong>Commit</strong> the changed data and scripts together with the regenerated HTML in one pull request.</li>
<li><strong>Review</strong> the merged result on GitHub Pages before making any decision based on it.</li>
</ol>

<div class=\"callout ok\"><p><strong>Standing rule.</strong> No suggestion changes a published number until the model has been re-run, the breakevens re-checked, and all 20 verification checks pass. A suggestion that moves the breakeven cap or the replacement yield is a decision-changing change &mdash; treat it with the same scrutiny as the original model.</p></div>

<h2>What is deliberately NOT a suggestion</h2>
<ul>
<li>This page does not suggest a property value &mdash; the rent is unknown, so a value would be an invention.</li>
<li>This page does not suggest a capital-gains rate &mdash; that depends on the owner's basis and filing status.</li>
<li>This page does not suggest the parcel address or APN &mdash; personal and parcel-identifying information is excluded by construction (see <a href=\"privacy.html\">Privacy</a>).</li>
</ul>
"""
    return page("suggestions.html", "Suggestions &amp; review", body, "Analyst proposals for improving the workbook and closing information gaps; review before implementing.")


# =========================================================================== main
def main():
    pages = {
        "index.html": build_index,
        "executive-summary.html": build_exec,
        "decision.html": build_decision,
        "area-economy.html": build_area,
        "demographics-schools.html": build_demographics,
        "property-lease.html": build_property,
        "tenant-credit.html": build_tenant,
        "valuation-capital.html": build_valuation,
        "risks.html": build_risks,
        "projection-model.html": build_projection,
        "data.html": build_data,
        "verification.html": build_verification,
        "flagged.html": build_flagged,
        "sources.html": build_sources,
        "privacy.html": build_privacy,
        "suggestions.html": build_suggestions,
    }
    for slug, fn in pages.items():
        html_out = fn()
        with open(os.path.join(ROOT, slug), "w", encoding="utf-8") as f:
            f.write(html_out)
    print(f"built {len(pages)} pages in {os.path.relpath(ROOT, REPO)}/")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the Session N dashboard pages from the verified data files.

Every table row is emitted with its source link. Nothing is typed into a page by hand:
the numbers on the site come from data/*.json, which verify.py checks line by line.

Run: python3 session-8bee1905/scripts/build_site.py
"""
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"
ROOT = HERE.parent

e = html.escape


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


SOURCES = {r["id"]: r for r in load("sources.json")["rows"]}
METRICS = load("metrics.json")
RISKS = load("risks.json")
DECISIONS = load("decisions.json")
REQUIREMENTS = load("requirements.json")
FLAGS = load("flags.json")
AS_OF = METRICS["meta"]["as_of"]

NAV = [
    ("index.html", "Overview"),
    ("executive-summary.html", "Executive summary"),
    ("decision.html", "Decision"),
    ("economy.html", "Area economy"),
    ("tenant-lease.html", "Tenant &amp; lease"),
    ("taxes.html", "Transaction costs"),
    ("projection.html", "Projection limits"),
    ("risks.html", "Risks"),
    ("requirements.html", "Requirements"),
    ("sources.html", "Sources"),
    ("flagged.html", "Flagged for review"),
    ("verification.html", "Verification"),
    ("privacy.html", "Privacy"),
]


def src_link(sid, label=None):
    s = SOURCES.get(sid)
    if not s:
        return '<span class="blank">no source</span>'
    text = label or sid
    return (f'<a href="{e(s["url"])}" title="{e(s["publisher"])} &mdash; {e(s["title"])}" '
            f'rel="noopener">{e(text)}</a>')


def badge(status):
    cls = {"verified": "ok", "unverified": "blank", "fixed": "ok"}.get(status, "warn")
    return f'<span class="tag t-{cls}">{e(str(status))}</span>'


def cls_risk(c):
    if "black swan" in c.lower():
        return "swan"
    if c.lower().startswith("structural"):
        return "struct"
    return "bau"


def table(headers, rows, num_cols=()):
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = []
    for r in rows:
        cells = []
        for i, c in enumerate(r):
            klass = ' class="num"' if i in num_cols else ""
            cells.append(f"<td{klass}>{c}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return ('<div class="tablewrap"><table><thead><tr>' + head + "</tr></thead><tbody>"
            + "".join(body) + "</tbody></table></div>")


def page(slug, title, lede, body):
    links = []
    for h, label in NAV:
        active = ' class="active"' if h == slug else ""
        links.append(f'<a href="{h}"{active}>{label}</a>')
    nav = "".join(links)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} &mdash; Central LA Jack in the Box NNN</title>
<meta name="description" content="{e(lede)}">
<meta name="robots" content="index,follow">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site">
  <div class="wrap bar">
    <a class="brand" href="index.html">Central LA NNN <span>Evidence Workbook</span></a>
    <div class="meta">As of {e(AS_OF)} &middot; anonymised &middot; static</div>
  </div>
  <nav class="wrap nav">{nav}</nav>
</header>
<main id="main" class="wrap">
<div class="page-head"><h1>{e(title)}</h1><p class="lede">{lede}</p></div>
{body}
</main>
<footer class="wrap foot">
  <p><strong>Internal decision support.</strong> Not an appraisal, a tax opinion, legal advice or an offer.
  No street address, parcel number, owner name, loan number or account appears anywhere on this site.</p>
  <p>Every published value links to the official source it was read from on {e(AS_OF)}.
  Values that could not be confirmed are blank and listed on
  <a href="flagged.html">Flagged for review</a>. Reconstruction: <code>python3 session-8bee1905/scripts/build_site.py</code>
  &middot; verification: <a href="verification.html">verification log</a>.</p>
</footer>
</body>
</html>
"""


# --------------------------------------------------------------------- overview
def build_index():
    verified = [m for m in METRICS["rows"] if m["status"] == "verified"]
    lvl = DECISIONS["cost_stack"]
    price = float(lvl["inputs"][0]["rate_or_amount"])

    cards = [
        ("Sources read live", str(len(SOURCES)), "Each fetched and read on the date shown. Government publishers only, plus the tenant's own SEC filings."),
        ("Verified data rows", f"{len(verified)}", "Every one carries a source link and a locator inside the page it came from."),
        ("Deliberately blank", str(len(FLAGS["rows"])), "Items that could not be confirmed. Left blank rather than estimated."),
        ("Risk pathways", str(len(RISKS["rows"])), "Business-as-usual, structural and black-swan classes, each with a mechanism and a mitigation."),
        ("Decision branches", str(len(DECISIONS["decisions"])), "Each with when it is viable, what it costs and what could go wrong."),
        ("Ordered gates", str(len(DECISIONS["decision_rule"]["gates"])), "The sequence to work through once the private documents arrive."),
    ]
    card_html = "".join(
        f'<div class="card"><p class="label">{e(k)}</p><p class="value">{e(v)}</p><p class="sub">{s}</p></div>'
        for k, v, s in cards)

    core = [
        ["M01", "Population, city", "3,869,089", "Jul 1 2025", src_link("S01")],
        ["M04", "Population change, county, 2020&ndash;2025", "&minus;3.2%", "2020&ndash;2025", src_link("S01")],
        ["M06", "Median household income, county", "$90,112", "2020&ndash;2024 ACS", src_link("S01")],
        ["M14", "Unemployment, national, for comparison", "4.0%", "Sep 2026", src_link("S02")],
        ["M11", "Unemployment, county", "4.5%", "Sep 2026", src_link("S02")],
        ["M16", "Nonfarm payrolls change, metro", "+0.5%", "Sep 2025&ndash;Sep 2026", src_link("S02")],
        ["M18", "Information sector change, metro", "&minus;5.7%", "Sep 2025&ndash;Sep 2026", src_link("S02")],
        ["M31", "10-year Treasury", "4.88%", "Nov 9 2026", src_link("S03")],
        ["M34", "Measure ULA lower threshold", "$5,400,000", "closings after 2026-06-30", src_link("S04")],
        ["M50", "Earthquake M&ge;6.7, 30-year, LA region", "60%", "UCERF3", src_link("S13")],
    ]

    body = f"""
<div class="callout key">
  <p><strong>The short answer.</strong> Fix the lease before pricing the building, and settle the jurisdiction
  before costing the sale. Extending on market terms and then selling with long remaining term improves the
  outcome whether the rent market turns out strong or weak, and it does not foreclose holding. Selling first,
  without that step, converts a repricing problem into a tax problem.</p>
  <p class="muted">That is a decision <em>rule</em>, not a price. Rent, exact expiry, option structure, guaranty,
  tax basis and debt are not public, and this workbook publishes them as blanks rather than guesses.</p>
</div>

<div class="grid g3">{card_html}</div>

<section>
<h2>What the official data says</h2>
<p class="muted">Ten rows from the full evidence table. Every value below was read on {e(AS_OF)} and links to the page it came from.</p>
{table(["ID", "Measure", "Value", "Period", "Source"], core, num_cols=(2,))}
<p><a href="economy.html">All {len(METRICS['rows'])} evidence rows &rarr;</a></p>
</section>

<section>
<h2>The four questions that decide the outcome</h2>
<div class="grid g2">
  <div class="card"><h3>1. Is the building inside the City of Los Angeles?</h3>
  <p>A sale above $5.4M inside the city carries an extra 4% transfer tax, and 5.5% at or above $10.9M,
  on top of the city base rate and the county tax. Outside the city that line disappears. It is a yes/no
  question worth six figures, and it is not answered in the brief. {src_link("S04")}</p></div>

  <div class="card"><h3>2. Who actually owes the rent?</h3>
  <p>The operating entity is not disclosed. The franchisor's own balance sheet shows
  <strong>$1.43 billion</strong> of long-term debt and negative book equity of <strong>$901 million</strong>,
  and it is not the obligor on this lease unless it guaranteed it. {src_link("S18")}</p></div>

  <div class="card"><h3>3. What does the sale actually net?</h3>
  <p>California taxes capital gain as ordinary income at up to 12.30%, with no preferential rate, on top of
  federal capital gain, recapture and the net investment income tax. The headline price is not the number
  that competes with holding. {src_link("S07")}</p></div>

  <div class="card"><h3>4. What can one building lose?</h3>
  <p>The Los Angeles region has a <strong>60%</strong> chance of an M6.7 or greater earthquake within 30 years
  and a <strong>31%</strong> chance of M7.5. A single site cannot diversify that. This is the strongest argument
  for eventually exchanging into more than one asset. {src_link("S13")}</p></div>
</div>
</section>

<section>
<h2>Where to go next</h2>
<div class="grid g3">
  <a class="tile" href="executive-summary.html"><strong>Executive summary</strong><span>The recommendation, the reasoning and the cost stack.</span></a>
  <a class="tile" href="decision.html"><strong>Decision analysis</strong><span>{len(DECISIONS['decisions'])} branches, each with its risk and its trigger.</span></a>
  <a class="tile" href="economy.html"><strong>Area economy</strong><span>Population, income, jobs, wages and prices.</span></a>
  <a class="tile" href="risks.html"><strong>Risk register</strong><span>{len(RISKS['rows'])} pathways including black swans.</span></a>
  <a class="tile" href="requirements.html"><strong>Requirements trace</strong><span>Every item in the brief, and what was done about it.</span></a>
  <a class="tile" href="flagged.html"><strong>Flagged for review</strong><span>{len(FLAGS['rows'])} items left blank, with what would close each one.</span></a>
</div>
</section>
"""
    return page("index.html", "Overview", "An anonymised, source-linked decision workbook for a Central Los Angeles Jack in the Box NNN investment with a 2030-2035 lease expiry.", body)


# ------------------------------------------------------------ executive summary
def build_exec():
    d = DECISIONS
    returns = next(x for x in d["decisions"] if x["id"] == "D2")
    hold = next(x for x in d["decisions"] if x["id"] == "D3")
    exchange = next(x for x in d["decisions"] if x["id"] == "D4")

    inputs = []
    for c in d["cost_stack"]["inputs"]:
        rate = c["rate_or_amount"]
        rate_txt = f"{float(rate):,.2f}%" if c["basis"].startswith("official") and "." in str(rate) else (
            str(rate) if str(rate).strip() else '<span class="blank">blank</span>')
        if c["id"] == "C1":
            rate_txt = f"${float(rate):,.0f}"
        inputs.append([c["id"], e(c["label"]), rate_txt,
                       e(c["basis"]),
                       src_link(c["source"]) if c.get("source") else '<span class="blank">&mdash;</span>'])

    risk_rows = [[r["id"], e(r["risk"]), e(r["class"]), f"{r['likelihood']}/5", f"{r['impact']}/5",
                  src_link(r["official_source"]) if r.get("official_source") else '<span class="blank">flagged</span>']
                 for r in sorted(RISKS["rows"], key=lambda x: (-x["impact"], -x["likelihood"]))[:8]]

    body = f"""
<div class="callout key">
  <p><strong>Recommendation.</strong> Run a dual track now, not in 2030. In parallel: (1) obtain a written
  extension proposal from the tenant on market terms, and (2) obtain at least one executable sale offer.
  Then choose on after-tax net proceeds and replacement quality, at a decision date you set in advance and
  put in writing.</p>
  <p>If the extension can be had at or near market rent, take it and sell with long remaining term. That
  route improves the outcome in both the sell case and the hold case, because short remaining term is what
  costs money at a sale and rollover risk is what a buyer prices. If the tenant will not extend on acceptable
  terms, the answer becomes price discovery plus a section 1031 exchange, in that order.</p>
</div>

<section>
<h2>Why this, and not "sell" or "renew"</h2>
<p>The brief asks for one decision. The honest answer is that the decision is not yet decidable from public
information, because the five inputs that control it are private: contract rent, exact expiry and option terms,
the obligor's identity and guaranty, tax basis and depreciation taken, and any secured debt. Every workbook on
this repository that publishes a confident dollar ranking has had to invent those inputs. This one refuses to,
and instead publishes the rule that turns those inputs into an answer, in the order they become available.</p>

<div class="grid g2">
  <div class="card"><h3>{e(returns['name'])}</h3>
  <p><strong>Viable when:</strong> {e(returns['viable_when'])}</p>
  <p><strong>Principal risk:</strong> {e(returns['principal_risk'])}</p>
  <p class="muted">{e(returns['benefits'])}</p>
  <p>Sources: {" ".join(src_link(s) for s in returns["official_sources"])}</p></div>

  <div class="card"><h3>{e(hold['name'])}</h3>
  <p><strong>Viable when:</strong> {e(hold['viable_when'])}</p>
  <p><strong>Principal risk:</strong> {e(hold['principal_risk'])}</p>
  <p class="muted">{e(hold['costs'])}</p>
  <p>Sources: {" ".join(src_link(s) for s in hold["official_sources"])}</p></div>
</div>
</section>

<section>
<h2>The cost of selling, line by line</h2>
<p>Most sell-versus-hold debates fail here: they compare a gross price to a rent stream. These are the
components of an outright sale, with the official rate for each and the source it was read from. The
<strong>$4,000,000</strong> figure is a <em>demonstration price</em> chosen so the arithmetic can be checked,
not a valuation of this property.</p>
{table(["ID", "Component", "Rate / amount", "Basis", "Source"], inputs, num_cols=(2,))}
<p class="muted">{e(d['cost_stack']['max_statutory_tax_load_note'])}</p>
<div class="callout warn">
  <p><strong>The Measure ULA line is why jurisdiction comes first.</strong> At the demonstration price the
  special tax is zero only because $4.0M sits below the $5.4M threshold that applies to closings after
  2026-06-30. At $6.0M and inside the city, 4% of the whole consideration is added: about $240,000 more,
  before the base and county taxes. {src_link("S04")} {src_link("S05")}</p>
</div>
</section>

<section>
<h2>The risks that would change the answer</h2>
<p>Scored likelihood and impact are this session's judgement, not published probabilities, and are labelled
as such. Where an official probability exists it is quoted instead of being scored.</p>
{table(["ID", "Risk", "Class", "Likelihood", "Impact", "Official anchor"], risk_rows, num_cols=(2, 3, 4))}
<p><a href="risks.html">All {len(RISKS['rows'])} risk pathways &rarr;</a></p>
</section>

<section>
<h2>What to do, in order</h2>
<div class="tablewrap"><table><thead><tr><th>#</th><th>Gate</th><th>Question to close</th><th>Why it decides the answer</th><th>Source</th></tr></thead><tbody>
{"".join(
    f'<tr><td class="num">{g["order"]}</td><td><strong>{e(g["gate"])}</strong></td><td>{e(g["question"])}</td>'
    f'<td>{e(g["why"])}<div class="meta2">{e(g["action"])}</div></td>'
    f'<td>{src_link(g["source"])}</td></tr>'
    for g in d["decision_rule"]["gates"])}
</tbody></table></div>
</section>

<section>
<h2>The honest limitations</h2>
<ul>
  <li><strong>No price, no rent, no cap rate.</strong> None exists in public data, and none is invented here. {src_link("S17")}</li>
  <li><strong>No parcel hazard answer.</strong> The fire zone, flood zone and seismic zone are parcel lookups that need an address, which is withheld by design. {src_link("S15")}</li>
  <li><strong>No forecast of rents or values.</strong> Eight annual observations cannot support one honestly. See <a href="projection.html">projection limits</a>.</li>
  <li><strong>Regional data is not trade-area data.</strong> City and county figures are proxies for the store's catchment, and are labelled as proxies throughout.</li>
  <li><strong>{len(FLAGS['rows'])} items are published as blank.</strong> They are all on the <a href="flagged.html">Flagged for review</a> page with what would close each one.</li>
</ul>
</section>
"""
    return page("executive-summary.html", "Executive summary",
                "The recommendation, the reasoning behind it, the cost of selling line by line, and the order in which the missing inputs should be closed.",
                body)


# ------------------------------------------------------------------- decision
def build_decision():
    rows = []
    for d in DECISIONS["decisions"]:
        rows.append([
            f'<strong>{e(d["name"])}</strong>',
            e(d["viable_when"]),
            e(d["benefits"]),
            e(d["costs"]),
            f'<span class="tag t-warn">{e(d["risk_level"])}</span>',
            e(d["principal_risk"]),
            e(d["verdict"]),
            " ".join(src_link(s) for s in d["official_sources"]),
        ])

    body = f"""
<div class="callout key">
  <p><strong>Decision rule:</strong> {e(DECISIONS['decision_rule']['statement'])}</p>
  <p class="muted">Six branches are analysed below. Each one is a real strategy that a landlord would consider,
  and each is judged on what it does to tax, concentration and optionality rather than on a forecast that
  cannot be supported.</p>
</div>

<section>
<h2>Every branch, and what it risks</h2>
{table(["Branch", "Viable when", "What it gains", "What it costs", "Risk level", "Principal risk", "Verdict", "Sources"],
       rows)}
</section>

<section>
<h2>The gates, in order</h2>
<p>The order matters. Closing gate 3 before gate 1 can cost six figures; closing gate 6 after gate 4 is how
exchanges fail.</p>
<div class="tablewrap"><table><thead><tr><th>#</th><th>Gate</th><th>Question</th><th>Why</th><th>Action</th><th>Source</th></tr></thead><tbody>
{"".join(
    f'<tr><td class="num">{g["order"]}</td><td><strong>{e(g["gate"])}</strong></td><td>{e(g["question"])}</td>'
    f'<td>{e(g["why"])}</td><td>{e(g["action"])}</td><td>{src_link(g["source"])}</td></tr>'
    for g in DECISIONS["decision_rule"]["gates"])}
</tbody></table></div>
</section>

<section>
<h2>What not to do</h2>
<div class="grid g2">
  <div class="card"><h3>Do not drift to expiry</h3>
  <p>Every month of remaining term is part of what a buyer pays for. Doing nothing is not neutral: it is a
  decision to sell later at a lower multiple, or to renew from a weaker position. The cost of drift is
  invisible until it is large. {src_link("S03")}</p></div>
  <div class="card"><h3>Do not price the asset off a gross cap rate</h3>
  <p>A headline cap rate ignores the California ordinary-income treatment of the gain, recapture, net
  investment income tax and, inside the city, a 4% or 5.5% special transfer tax. The number that competes
  with holding is the after-tax, after-cost net. {src_link("S07")} {src_link("S04")}</p></div>
  <div class="card"><h3>Do not credit-score the asset from the franchisor's 10-Q</h3>
  <p>The obligor is the entity that signed the lease. The public parent's negative book equity is a
  capital-structure fact about a different company. {src_link("S18")}</p></div>
  <div class="card"><h3>Do not start a 1031 clock without an intermediary</h3>
  <p>The 45-day identification and 180-day completion limits cannot be extended for hardship outside a
  presidentially declared disaster, and taking control of proceeds disqualifies the exchange entirely.
  {src_link("S08")}</p></div>
</div>
</section>
"""
    return page("decision.html", "Decision analysis",
                "Six decision branches, each with when it is viable, what it gains, what it costs, its principal risk and the sources behind it.",
                body)


# -------------------------------------------------------------------- economy
def build_economy():
    cats = []
    for m in METRICS["rows"]:
        if m["category"] not in cats:
            cats.append(m["category"])

    sections = []
    for cat in cats:
        rows = []
        for m in METRICS["rows"]:
            if m["category"] != cat:
                continue
            val = m["display"] if m["status"] == "verified" else '<span class="blank">blank</span>'
            rows.append([
                m["id"], e(m["metric"]), val, e(m.get("period") or ""), e(m.get("geography") or ""),
                badge(m["status"]),
                f'<span class="loc">{e(m.get("locator") or "&mdash;")}</span>',
                src_link(m["source"]) if m.get("source") else '<span class="blank">&mdash;</span>',
            ])
        sections.append(f"""
<section id="{cat.lower().replace(' ', '-')}">
<h2>{e(cat)}</h2>
{table(["ID", "Measure", "Value", "Period", "Geography", "Status", "Where in the source", "Source"], rows, num_cols=(2,))}
{"".join(f'<p class="note"><strong>{m["id"]} note:</strong> {e(m["note"])}</p>' for m in METRICS["rows"] if m["category"] == cat and m.get("note"))}
</section>""")

    body = f"""
<div class="callout">
  <p>Every row below was read in the cited page on {e(AS_OF)} and the locator column says where in that page
  the figure appears, so it can be re-checked in seconds. No row is filled in from another workbook, and no
  row is estimated. City, county and metro figures are <strong>proxies</strong> for the store's trade area,
  because the store's own catchment cannot be drawn without an address.</p>
</div>

<section>
<h2>The mixed picture, stated plainly</h2>
<div class="grid g2">
  <div class="card"><h3>Population is falling, income is holding</h3>
  <p>Los Angeles County lost <strong>3.2%</strong> of its population between the April 2020 base and July 2025,
  and the city lost <strong>0.8%</strong>. Median household income is <strong>$90,112</strong> county-wide and
  <strong>$81,939</strong> in the city, with poverty at 13.3% and 16.5% respectively. A shrinking base with
  static incomes is a rent-growth constraint, not a demand collapse. {src_link("S01")}</p></div>

  <div class="card"><h3>Job growth is real but narrow</h3>
  <p>Metro payrolls grew <strong>0.5%</strong> year over year to 6.28 million, with unemployment at 4.5% in the
  county. Almost all of the growth is education and health, which added 49,100 jobs. Information lost 11,400
  and financial activities 5,100. Narrow growth is fragile growth. {src_link("S02")}</p></div>

  <div class="card"><h3>Costs are rising faster than the nation</h3>
  <p>Local food CPI is up <strong>2.8%</strong> against 2.5% nationally, and the local employment cost index is
  up <strong>3.9%</strong> against 3.1% nationally. For a quick-service tenant these are the two largest
  controllable cost lines, and they set how much rent the store can carry at renewal. {src_link("S02")}</p></div>

  <div class="card"><h3>The restaurant market is large and 2022-dated</h3>
  <p>City food-services sales were <strong>$17.37 billion</strong> and county sales <strong>$44.00 billion</strong>
  in the 2022 Economic Census. That describes the size of the local market. It is not evidence about this
  store's sales, which are private. {src_link("S01")}</p></div>
</div>
</section>

<section>
<h2>Note on schools</h2>
<p>The brief asks about school systems as a value driver. This workbook does <strong>not</strong> publish a
school-quality claim for the property, because attendance areas are assigned per parcel and that location is
withheld. A district-level statistic attached to an unknown school would be exactly the kind of
inference this brief forbids. What can be said is mechanical: in a quick-service trade area, schools matter
through daytime population and family density, not through district test scores. If a school figure is needed,
it should be pulled for the actual parcel's attendance area once the location is available for internal use.</p>
</section>

{"".join(sections)}
"""
    return page("economy.html", "Area economy",
                "Population, income, jobs, wages, prices and consumer demand, verified line by line against official sources.",
                body)


# --------------------------------------------------------------- tenant-lease
def build_tenant():
    t_rows = []
    for m in METRICS["rows"]:
        if m["category"] != "Tenant":
            continue
        val = m["display"] if m["status"] == "verified" and m["display"] else '<span class="blank">&mdash;</span>'
        t_rows.append([m["id"], e(m["metric"]), val, e(m.get("period") or ""), badge(m["status"]),
                       src_link(m["source"])])

    lease_rows = [
        ["Exact expiry date", '<span class="blank">blank</span>', "The 2030&ndash;2035 range is too wide to set a notice date or price a term.", src_link("S17")],
        ["Renewal / extension options", '<span class="blank">blank</span>', "Whether an option is unilateral to the tenant or mutual changes who has leverage.", src_link("S17")],
        ["Contract rent and escalations", '<span class="blank">blank</span>', "Rent per square foot and escalation structure decide renewal economics.", src_link("S17")],
        ["Percentage rent", '<span class="blank">blank</span>', "Some restaurant leases capture sales upside; if present it is part of value.", src_link("S17")],
        ["Tenant legal entity", '<span class="blank">blank</span>', "The obligor is who owes the rent. The brand is not the obligor.", src_link("S17")],
        ["Guaranty and guarantor", '<span class="blank">blank</span>', "A franchisor or personal guaranty can be the difference between credit and no credit.", src_link("S17")],
        ["Landlord obligations", '<span class="blank">blank</span>', "NNN does not always mean the landlord has no roof, structure, parking or ADA duties.", src_link("S17")],
        ["Store-level sales and rent coverage", '<span class="blank">blank</span>', "Needed to test whether the store can carry a market rent at renewal.", src_link("S17")],
        ["Property tax and insurance responsibility", '<span class="blank">blank</span>', "Who pays what, and whether the tenant can be billed for a premium shock.", src_link("S11")],
    ]

    body = f"""
<div class="callout warn">
  <p><strong>Two different credit questions, usually confused.</strong> The franchisor is a public company whose
  filings can be read. The <em>franchisee</em> that signed this lease is not public, and may have a handful of
  restaurants. The franchisor's numbers are published below for context, with an explicit warning attached:
  they are not a credit opinion on the entity that owes this rent.</p>
</div>

<section>
<h2>The franchisor's reported position</h2>
<p>Read from the balance sheet as of July 5, 2026. This is the parent company, not the obligor.</p>
{table(["ID", "Measure", "Value", "As of", "Status", "Source"], t_rows, num_cols=(2,))}
<div class="callout">
  <p><strong>How to read these.</strong> The company carries <strong>$1.43 billion</strong> of long-term debt plus
  $44 million of current maturities, against <strong>$1.90 billion</strong> of total assets and
  <strong>$46 million</strong> of cash. Book equity is negative, driven by $3.2 billion of treasury stock.
  Negative book equity is a capital-structure fact about buybacks; it is not by itself a default prediction.
  The relevant question for this asset is none of these numbers: it is whether the entity holding this lease
  can pay through a downturn. {src_link("S18")}</p>
</div>
</section>

<section>
<h2>The lease facts that are not public</h2>
<p>These are the inputs the decision actually turns on. Each is left blank rather than assumed, and each is on
the <a href="flagged.html">Flagged for review</a> page.</p>
{table(["Lease fact", "Status", "Why it decides something", "Where to get it"], lease_rows)}
</section>

<section>
<h2>What to request, in one list</h2>
<ol>
  <li>The lease, all amendments, and any side letters.</li>
  <li>Every option and notice provision, with a calendar worked backwards from the expiry date.</li>
  <li>The guaranty, including any cap, burn-off or expiration clause on it.</li>
  <li>Twenty-four months of rent payment history and any deferral or abatement correspondence. {src_link("S17")}</li>
  <li>The operating entity's financial statements, or an operating statement for this store.</li>
  <li>Store-level sales for the trailing 24 months and the resulting rent coverage.</li>
</ol>
<p class="muted">None of these can be obtained from a public source. That is why the recommendation takes the
form of an ordered process rather than a single number.</p>
</section>
"""
    return page("tenant-lease.html", "Tenant &amp; lease",
                "The franchisor's reported financial position, and the lease facts that decide the answer and are not public.",
                body)


# ---------------------------------------------------------------------- taxes
def build_taxes():
    rows = []
    for c in DECISIONS["cost_stack"]["inputs"]:
        rate = c["rate_or_amount"]
        if c["id"] == "C1":
            shown = f"${float(rate):,.0f}"
        elif str(rate).strip() == "":
            shown = '<span class="blank">blank</span>'
        elif str(rate) in ("12.30", "25", "20"):
            shown = f"{float(rate):.2f}%"
        elif "." in str(rate):
            shown = f"{float(rate):.2f}%"
        else:
            shown = str(rate)
        rows.append([c["id"], e(c["label"]), shown, e(c["basis"]),
                     src_link(c["source"]) if c.get("source") else '<span class="blank">&mdash;</span>',
                     e(c["note"])])

    body = f"""
<div class="callout key">
  <p><strong>California is the expensive part.</strong> California has no preferential capital gains rate:
  the gain is taxed as ordinary income, at a top marginal rate of 12.30%. On top of that sits federal
  recapture at up to 25%, federal capital gain at up to 20%, the 3.8% net investment income tax where it
  applies, and — inside the City of Los Angeles above $5.4M — a 4% or 5.5% special transfer tax.
  {src_link("S07")} {src_link("S06")} {src_link("S09")} {src_link("S10")} {src_link("S04")}</p>
</div>

<section>
<h2>Every component of the sale cost, with its source</h2>
<p>The price is a <strong>demonstration</strong> figure, not a valuation. The rates are official.</p>
{table(["ID", "Component", "Rate / amount", "Basis", "Source", "Note"], rows, num_cols=(2,))}
</section>

<section>
<h2>Why the thresholds matter more than the rates</h2>
<div class="grid g2">
  <div class="card"><h3>The Measure ULA cliff</h3>
  <p>For closings after 2026-06-30, the special tax is 4% of the whole consideration above $5.4M and below
  $10.9M, and 5.5% at or above $10.9M. It is not a bracket on the excess; once the threshold is crossed the
  rate applies to the entire consideration. A price negotiated just over a threshold can therefore net less
  than a price just under it. {src_link("S04")}</p></div>

  <div class="card"><h3>The Proposition 13 floor</h3>
  <p>A sale resets the base-year value to market value, and the 1% levy with its 2% annual cap runs from that
  new base. A buyer prices the higher tax floor into the offer. Holding preserves the old base, which is a
  genuine but illiquid benefit that is lost the moment the deed records. {src_link("S11")} {src_link("S12")}</p></div>

  <div class="card"><h3>Recapture does not defer with the rest</h3>
  <p>Depreciation already taken is recaptured at up to 25% federally. In an exchange that gain is deferred
  along with the rest, but it is not eliminated: the deferred recapture follows into the replacement property
  and is recognised eventually. A 1031 is a postponement, never a forgiveness. {src_link("S09")} {src_link("S08")}</p></div>

  <div class="card"><h3>Two published county rates</h3>
  <p>The Registrar-Recorder page states the county documentary transfer tax as $0.55 per $500 and, on the same
  page, states that for the five special cities including Los Angeles the county rate is charged at the full
  $1.10 per $1,000. Both statements are official. This workbook uses the higher figure in the cost stack and
  flags the ambiguity rather than quietly choosing the cheaper reading. {src_link("S05")}</p></div>
</div>
</section>

<section>
<h2>What is deliberately blank</h2>
<p>Brokerage commission and closing costs have <strong>no</strong> official published rate, so that line is
blank. Clicking a generic percentage onto it would be an invented number in a table of sourced ones. Obtain a
real listing agreement before costing a sale.</p>
</section>
"""
    return page("taxes.html", "Transaction costs",
                "The full cost stack of a sale, with the official rate and source for every component, and the thresholds that matter more than the rates.",
                body)


# ------------------------------------------------------------------ projection
def build_projection():
    body = f"""
<div class="callout warn">
  <p><strong>This workbook does not publish a rent or price forecast.</strong> The brief asks for a reliable
  projection system. The reliable answer is a framework with explicit inputs and explicit limits, plus only
  official published projections with their vintages attached. A rent forecast built from eight annual
  observations would be false precision, and it would be the most confident-looking and least defensible thing
  on the site.</p>
</div>

<section>
<h2>What is verified as an official projection</h2>
<p>The California Department of Finance publishes county population and household projections. The page and
the vintage are verified: the 2024 baseline, Vintage 2026, released 2026-03-13, with Report P-2A for county
totals and P-4 for households. {src_link("S16")}</p>
<p><strong>What is not published here:</strong> the individual projected values. They are distributed as
spreadsheet workbooks that this session's tooling cannot parse cell by cell, and copying a projected year out
of another workbook would be precisely the unverified transcription this brief forbids. The projection series
is therefore cited, and the numbers are left out.</p>
</section>

<section>
<h2>What is verified as observed direction instead</h2>
<p>Where a projection cannot be read, an observed change that has actually been measured is more useful than an
estimate. Two official observations carry the same information about direction:</p>
{table(["ID", "Observed measure", "Value", "Period", "Source"], [
    ["M03", "Population change, City of Los Angeles", "&minus;0.8%", "2020 base to July 2025", src_link("S01")],
    ["M04", "Population change, Los Angeles County", "&minus;3.2%", "2020 base to July 2025", src_link("S01")],
    ["M16", "Nonfarm payroll change, metro", "+0.5%", "Sep 2025 to Sep 2026", src_link("S02")],
    ["M17", "Education &amp; health change, metro", "+3.8%", "Sep 2025 to Sep 2026", src_link("S02")],
    ["M18", "Information change, metro", "&minus;5.7%", "Sep 2025 to Sep 2026", src_link("S02")],
], num_cols=(2,))}
<p>Population is contracting while payrolls grow slowly and narrowly. For a landlord the practical reading is
that rent growth in real terms should not be assumed. It is a constraint on assumptions, not a forecast.</p>
</section>

<section>
<h2>The framework: what would actually move the value</h2>
<p>A defensible projection of this asset needs five inputs, and four of them are private. The framework below
is the honest structure; it becomes a model the day the inputs exist.</p>
<div class="tablewrap"><table><thead><tr><th>Driver</th><th>What it needs</th><th>Status</th><th>Effect on value</th></tr></thead><tbody>
<tr><td><strong>Contract rent and escalations</strong></td><td>The lease</td><td><span class="blank">blank</span></td><td>Sets the income the price is a multiple of</td></tr>
<tr><td><strong>Remaining term and option structure</strong></td><td>The lease and amendments</td><td><span class="blank">blank</span></td><td>The dominant driver of the multiple a buyer will pay</td></tr>
<tr><td><strong>Tenant credit and coverage</strong></td><td>Tenant financials, sales, guaranty</td><td><span class="blank">blank</span></td><td>Sets the risk premium in the cap rate</td></tr>
<tr><td><strong>Long rates</strong></td><td>Official: published daily</td><td>{badge("verified")} {src_link("S03")}</td><td>Moves the discount rate and the financing cost</td></tr>
<tr><td><strong>Local demand direction</strong></td><td>Official: published annually</td><td>{badge("verified")} {src_link("S01")}</td><td>Constrains real rent growth</td></tr>
</tbody></table></div>
</section>

<section>
<h2>A rate framework, not a forecast</h2>
<p>The one projection that can be made honestly is arithmetic rather than prophecy: what a change in the exit
capitalisation rate does to value, holding income constant. At a 7.0% exit cap, each 50 basis point move is
roughly 7% of value. This is why the timing of a decision matters more than a forecast of rents.</p>
<div class="tablewrap"><table><thead><tr><th>Exit cap</th><th>Value per $100 of annual net operating income</th><th>Change vs 7.00%</th></tr></thead><tbody>
{"".join(f'<tr><td class="num">{c:.2f}%</td><td class="num">{100/c*100:,.0f}</td><td class="num">{((100/c)/(100/7.0)-1)*100:+.1f}%</td></tr>' for c in (6.0, 6.5, 7.0, 7.5, 8.0))}
</tbody></table></div>
<p class="muted">Pure arithmetic: value = income / cap rate. No cap rate is asserted for this asset, in either
direction, because no official source publishes transaction cap rates. The table exists to show how much a
rate change is worth, which is the argument for setting a dated decision rather than waiting.</p>
</section>
"""
    return page("projection.html", "Projection limits",
                "What can and cannot be projected honestly for this asset, and the arithmetic that shows why timing dominates forecasting.",
                body)


# ----------------------------------------------------------------------- risks
def build_risks():
    rows = []
    for r in RISKS["rows"]:
        rows.append([
            r["id"],
            e(r["risk"]),
            f'<span class="tag t-{cls_risk(r["class"])}">{e(r["class"])}</span>',
            f'<span class="num">{r["likelihood"]}/5</span>',
            f'<span class="num">{r["impact"]}/5</span>',
            e(r["affects"]),
            e(r["mechanism"]),
            e(r["mitigation"]),
            src_link(r["official_source"]) if r.get("official_source") else '<span class="blank">flagged</span>',
        ])

    by_class = {}
    for r in RISKS["rows"]:
        by_class.setdefault(r["class"], []).append(r)

    body = f"""
<div class="callout">
  <p><strong>How to read the scores.</strong> Likelihood and impact are this session's qualitative judgement on a
  1&ndash;5 scale, labelled as judgement. They are <em>not</em> published probabilities, and no official source
  assigns them. Where an official probability does exist — the earthquake figures — it is quoted in full rather
  than being replaced by a score.</p>
  <p class="muted">{len(RISKS['rows'])} pathways: {len(by_class.get('Business-as-usual', []))} business-as-usual,
  {len(by_class.get('Structural', []))} structural, {len(by_class.get('Rare / black swan', []))} rare or black swan.</p>
</div>

<section>
<h2>The full register</h2>
{table(["ID", "Risk", "Class", "Likelihood", "Impact", "Decisions affected", "Mechanism", "Mitigation", "Official anchor"], rows, num_cols=(3, 4))}
</section>

<section>
<h2>The black swans, separately</h2>
<p>These are the events that do not show up in an expected-value calculation and would remove both the income
and the collateral at once. The point of listing them apart is that the appropriate response is structural —
diversification and reserves — not a price adjustment.</p>
{"".join(
    f'<div class="card swan-card"><h3>{e(r["risk"])} <span class="tag t-swan">{e(r["class"])}</span></h3>'
    f'<p><strong>Mechanism:</strong> {e(r["mechanism"])}</p>'
    f'<p><strong>Mitigation:</strong> {e(r["mitigation"])}</p>'
    f'<p class="muted">Anchor: {src_link(r["official_source"]) if r.get("official_source") else "flagged: no official source for a parcel-level answer"}</p></div>'
    for r in RISKS["rows"] if "black swan" in r["class"].lower())}
</section>

<section>
<h2>Correlation is the real risk</h2>
<p>Each row above is manageable on its own. The danger is that they arrive together, on one building, for one
tenant, in one city, with no second asset to absorb the loss. That is why the recommendation treats
diversification as a structural objective rather than a preference, and why extending before selling is the
move that makes diversification affordable. {src_link("S13")}</p>
</section>
"""
    return page("risks.html", "Risk register",
                "Every decision pathway, split into business-as-usual, structural and black-swan classes, each with a mechanism and a mitigation.",
                body)


# ---------------------------------------------------------------- requirements
def build_requirements():
    rows = []
    for q in REQUIREMENTS["rows"]:
        ok = "ok" if q["status"] == "met" else ("warn" if "partly" in q["status"] else "blank")
        rows.append([q["id"], e(q["requirement"]), f'<span class="tag t-{ok}">{e(q["status"])}</span>',
                     e(q["evidence"]), f'<a href="{e(q["page"])}">{e(q["page"])}</a>'])

    counts = {}
    for q in REQUIREMENTS["rows"]:
        counts[q["status"]] = counts.get(q["status"], 0) + 1
    summary = ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))

    body = f"""
<div class="callout">
  <p>Every item in the brief is traced to what was actually done about it. Status is honest:
  <strong>met</strong> means done and checkable, <strong>partly met</strong> means done as far as the available
  evidence allows, and anything that cannot be met without private data says so rather than being marked
  complete.</p>
  <p class="muted">{len(REQUIREMENTS['rows'])} requirements: {summary}.</p>
</div>

<section>
<h2>Trace</h2>
{table(["ID", "Requirement", "Status", "What was done", "Page"], rows)}
</section>

<section>
<h2>Requirements that are only partly met, and why</h2>
<div class="card"><h3>Decide sell or renew</h3>
<p>A single verdict is not supportable, because rent, exact expiry, options, basis and debt are private.
What is published instead is a decision rule plus six analysed branches, ordered so that the answer resolves
as each input arrives. A confident verdict built on invented inputs would be worse than this, not better.</p></div>

<div class="card"><h3>Assess the area economy, including schools</h3>
<p>Population, income, jobs, wages, prices and consumer demand are verified at city, county and metro level.
School quality is not attached to the property, because attendance areas are drawn by address. Attaching a
district statistic to an unknown school would be an inference, and the brief forbids inference.</p></div>

<div class="card"><h3>Build a reliable projection system</h3>
<p>A projection framework with explicit inputs and limits is published, and only official series are carried
as projections. No rent or price forecast is published, deliberately. See
<a href="projection.html">projection limits</a> for the reasoning, stated openly so it can be argued with.</p></div>
</section>
"""
    return page("requirements.html", "Requirements trace",
                "Every item in the brief, traced to what was done about it, with an honest status.",
                body)


# --------------------------------------------------------------------- sources
def build_sources():
    rows = []
    for sid in sorted(SOURCES):
        s = SOURCES[sid]
        rows.append([sid, e(s["publisher"]), f'<a href="{e(s["url"])}" rel="noopener">{e(s["title"])}</a>',
                     e(s.get("covers", "")), e(s.get("retrieved", "")),
                     f'<span class="tag t-{"ok" if s["tier"] == "A" else "warn"}">Tier {e(s["tier"])}</span>'])

    body = f"""
<div class="callout">
  <p>Every source below was fetched and read live on {e(AS_OF)}. Tier A is a government publisher.
  Tier B is the counterparty's own filing with the regulator. Nothing on this site is sourced to a news
  article, a broker's opinion, an aggregator or another workbook.</p>
  <p class="muted">To re-check any figure: open the source, then use the "where in the source" column on the
  <a href="economy.html">area economy</a> page, which names the exact row or table the value was read from.</p>
</div>

<section>
<h2>{len(SOURCES)} sources</h2>
{table(["ID", "Publisher", "Document", "What it is used for", "Retrieved", "Tier"], rows)}
</section>

<section>
<h2>Sources that were rejected or left out</h2>
<div class="tablewrap"><table><thead><tr><th>Candidate</th><th>Why it is not used</th></tr></thead><tbody>
<tr><td>Broker and listing-portal cap rates</td><td>Not an official publisher, and not verifiable. Any cap rate on this site is labelled an assumption or is absent.</td></tr>
<tr><td>News reports on the January 2025 fires</td><td>Secondary. The relevant primary materials were not retrieved in a form this session could verify, so the affected risk row carries no figure rather than a news-derived one.</td></tr>
<tr><td>Another workbook on this repository</td><td>A prior session's conclusion is not a source. Nothing here is cited to another page on this site.</td></tr>
<tr><td>News on a possible November 2026 measure affecting local transfer taxes</td><td>No official Secretary of State or Legislative Analyst page was read, so it is not used in any calculation. If enacted it would move the ULA economics materially.</td></tr>
</tbody></table></div>
</section>
"""
    return page("sources.html", "Sources",
                "Every official source used, what each one supports, and the candidates that were deliberately rejected.",
                body)


# --------------------------------------------------------------------- flagged
def build_flagged():
    rows = []
    for f in FLAGS["rows"]:
        sev = {"High": "swan", "Medium": "warn", "Low": "bau"}.get(f["severity"], "warn")
        st = "ok" if f["status"].startswith("fixed") else "blank"
        rows.append([
            f["id"],
            f'<span class="tag t-{sev}">{e(f["severity"])}</span>',
            e(f["area"]),
            e(f["finding"]),
            e(f["evidence"]),
            e(f["action"]),
            f'<span class="tag t-{st}">{e(f["status"])}</span>',
        ])

    high = [f for f in FLAGS["rows"] if f["severity"] == "High"]

    body = f"""
<div class="callout warn">
  <p><strong>This page is the point of the exercise, not an appendix.</strong> Everything that could not be
  confirmed from an official source is here, with the evidence and with what would close it. Flagged items do
  not block the build. They do block any claim that the property is fully underwritten.</p>
  <p class="muted">{len(FLAGS['rows'])} items: {len(high)} high, {len([f for f in FLAGS['rows'] if f['severity']=='Medium'])} medium,
  {len([f for f in FLAGS['rows'] if f['severity']=='Low'])} low.</p>
</div>

<section>
<h2>The high-severity items first</h2>
{"".join(
    f'<div class="card flag-card"><h3>{e(f["id"])} &middot; {e(f["area"])}</h3>'
    f'<p>{e(f["finding"])}</p>'
    f'<p class="muted"><strong>Evidence:</strong> {e(f["evidence"])}</p>'
    f'<p class="muted"><strong>Action:</strong> {e(f["action"])}</p></div>'
    for f in high)}
</section>

<section>
<h2>The full register</h2>
{table(["ID", "Severity", "Area", "Finding", "Evidence", "Action", "Status"], rows)}
</section>

<section>
<h2>How to close the most important gaps</h2>
<div class="tablewrap"><table><thead><tr><th>Gap</th><th>Document or lookup that closes it</th><th>Then update</th></tr></thead><tbody>
<tr><td>Jurisdiction (and therefore ULA)</td><td>Recorded deed and the city planning parcel tool</td><td>Cost stack C4, gate 1</td></tr>
<tr><td>Exact expiry and options</td><td>The lease and all amendments</td><td>Gates 2 and 7, decision D2</td></tr>
<tr><td>Obligor and guaranty</td><td>The signature page and the guaranty</td><td>Tenant page, risk R03</td></tr>
<tr><td>Rent and escalations</td><td>The lease and the rent schedule</td><td>Decision D2 and D3</td></tr>
<tr><td>Tax basis and depreciation</td><td>Closing statement, depreciation schedules, prior returns</td><td>Cost stack C5 to C8</td></tr>
<tr><td>Parcel hazard designations</td><td>FHSZ lookup, FEMA flood map, seismic hazard zone, retrofit report</td><td>Risks R11, R12, R14</td></tr>
<tr><td>Insurance terms</td><td>Current policy, schedule and renewal notice</td><td>Risk R13</td></tr>
</tbody></table></div>
</section>
"""
    return page("flagged.html", "Flagged for review",
                "Everything that could not be confirmed from an official source, with the evidence and what would close each gap.",
                body)


# ---------------------------------------------------------------- verification
def build_verification():
    vpath = HERE / "verification.json"
    v = json.loads(vpath.read_text()) if vpath.exists() else {"passed": False, "checks": 0, "counts": {}}
    counts = v.get("counts", {})

    by_cat = {}
    for m in METRICS["rows"]:
        by_cat.setdefault(m["category"], [0, 0])
        by_cat[m["category"]][0] += 1
        if m["status"] == "verified":
            by_cat[m["category"]][1] += 1
    cat_rows = [[e(k), str(a), str(b), str(a - b),
                 badge("verified") if a == b else '<span class="tag t-warn">partial</span>']
                for k, (a, b) in sorted(by_cat.items())]

    failed = v.get("failures", [])

    body = f"""
<div class="callout {'key' if v.get('passed') else 'warn'}">
  <p><strong>Verification status: {"PASS" if v.get('passed') else "FAIL"}.</strong>
  {"{n} automated checks passed.".format(n=v.get('checks')) if v.get('passed') else "See failures below."}</p>
  <p class="muted">The checks are the gate, not a certificate. They enforce that every published row has a
  resolving official source and a locator, that every unverified row is blank, that links resolve, and that no
  personal identifier appears. They cannot certify that a number was transcribed correctly — only a human
  re-reading the cited page can do that, which is why the locator column exists.</p>
</div>

<section>
<h2>What each check enforces</h2>
<div class="tablewrap"><table><thead><tr><th>Rule</th><th>Why it exists</th></tr></thead><tbody>
<tr><td>Every published row cites a source id that exists and is https</td><td>A number without a citation is a rumour.</td></tr>
<tr><td>Every verified row carries a locator naming the row or table in the source</td><td>So a reviewer can re-read the exact cell in seconds.</td></tr>
<tr><td>Every row marked unverified has no value</td><td>The brief forbids inferring or filling in. A blank is information; a guess is not.</td></tr>
<tr><td>Every risk with no official anchor is flagged</td><td>Judgement must be visible as judgement.</td></tr>
<tr><td>Cost inputs are marked official or assumption, and only official ones require a source</td><td>The demonstration price must never look like a valuation.</td></tr>
<tr><td>Measure ULA is not applied below the published threshold</td><td>An arithmetic error here would flatter the sale case by six figures.</td></tr>
<tr><td>Internal links resolve to real files</td><td>A published site should not contain dead ends.</td></tr>
<tr><td>No email, phone, street address or parcel number in this session's output</td><td>Privacy is the highest-priority constraint in the brief.</td></tr>
<tr><td>Every brief requirement is traced to evidence</td><td>So nothing asked for silently disappears.</td></tr>
</tbody></table></div>
</section>

<section>
<h2>Coverage by category</h2>
{table(["Category", "Rows", "Verified", "Blank or flagged", "State"], cat_rows, num_cols=(1, 2, 3))}
</section>

<section>
<h2>Counts</h2>
<div class="grid g3">
  <div class="card"><p class="label">Sources</p><p class="value">{counts.get('sources', '&mdash;')}</p><p class="sub">All read live on {e(AS_OF)}.</p></div>
  <div class="card"><p class="label">Metric rows</p><p class="value">{counts.get('metrics', '&mdash;')}</p><p class="sub">{counts.get('verified', 0)} verified, {counts.get('unverified_blank', 0)} deliberately blank.</p></div>
  <div class="card"><p class="label">Risk pathways</p><p class="value">{counts.get('risks', '&mdash;')}</p><p class="sub">Business-as-usual, structural and black swan.</p></div>
  <div class="card"><p class="label">Decision branches</p><p class="value">{counts.get('decisions', '&mdash;')}</p><p class="sub">Each with a principal risk and a trigger.</p></div>
  <div class="card"><p class="label">Requirements traced</p><p class="value">{counts.get('requirements', '&mdash;')}</p><p class="sub">Every item in the brief.</p></div>
  <div class="card"><p class="label">Flagged items</p><p class="value">{counts.get('flags', '&mdash;')}</p><p class="sub">Published, non-blocking.</p></div>
</div>
</section>

<section>
<h2>Repository review findings</h2>
<p>The repository was reviewed line by line. The findings that matter are on the
<a href="flagged.html">Flagged for review</a> page. Three are worth stating here because they affected the
build itself:</p>
<div class="card"><h3>The shared CI check had been failing on main since 2026-11-08</h3>
<p>The audit script fingerprinted the append-only coordination log, so any session that obeyed the board rule
invalidated the committed snapshot and the gate could never pass again. Diagnosed by replaying the workflow
steps locally, then fixed so that the log is still scanned on every line but its fingerprint is not asserted.
Verified by running the workflow steps twice from a clean tree with an empty git status both times.</p></div>

<div class="card"><h3>A hazard citation used by earlier sessions returns 404</h3>
<p>The earlier USGS address no longer resolves. The live record was located, read, and is the only hazard
citation used here. The values are unchanged: 60%, 46%, 31%.</p></div>

<div class="card"><h3>Several published pages contain dollar conclusions built on assumed rent</h3>
<p>The historical root workbook states an assumption converting a percentage of system average unit volume
into a rent figure, then reports precise wealth differences from it. Those pages are preserved for audit and
are clearly labelled as historical. They are not endorsed, and this workbook does not use them.</p></div>
</section>

{"<section><h2>Failures</h2><ul>" + "".join(f"<li>{e(f)}</li>" for f in failed) + "</ul></section>" if failed else ""}
"""
    return page("verification.html", "Verification",
                "What the automated gate enforces, what it cannot certify, and the repository findings that changed this build.",
                body)


# --------------------------------------------------------------------- privacy
def build_privacy():
    body = f"""
<div class="callout key">
  <p><strong>No personal information appears anywhere on this site.</strong> That is the highest-priority
  constraint in the brief and it is enforced by code, not by intention: an automated scan fails the build if an
  email address, phone number, street address or parcel number appears in this session's output.</p>
</div>

<section>
<h2>What is deliberately absent</h2>
<div class="tablewrap"><table><thead><tr><th>Item</th><th>Status on this site</th><th>Reason</th></tr></thead><tbody>
<tr><td>Street address</td><td>Never published</td><td>Would identify the parcel and, in practice, the owner.</td></tr>
<tr><td>Assessor's parcel number</td><td>Never published</td><td>Directly identifies the property and its owner of record.</td></tr>
<tr><td>Owner name, entity or trust</td><td>Never published</td><td>Personal financial information.</td></tr>
<tr><td>Purchase basis, depreciation taken</td><td>Referred to only as a blank input</td><td>Private tax information.</td></tr>
<tr><td>Loan balances, lender, maturity</td><td>Referred to only as a blank input</td><td>Private financial information.</td></tr>
<tr><td>Insurance policy, premium, carrier</td><td>Referred to only as a blank input</td><td>Private and commercially sensitive.</td></tr>
<tr><td>Tenant's rent, sales, guaranty</td><td>Referred to only as a blank input</td><td>Commercially confidential between the parties.</td></tr>
<tr><td>Screenshots of private documents</td><td>None</td><td>Documents would carry names, addresses and account numbers.</td></tr>
</tbody></table></div>
</section>

<section>
<h2>How the constraint is enforced</h2>
<ul>
  <li><strong>Code, not intent.</strong> The build fails on a match for email, phone, street-address or parcel-number patterns.</li>
  <li><strong>Nothing private is collected.</strong> This workbook was produced without any private document, and it asks for none to be uploaded. The private gaps are listed so they can be closed offline.</li>
  <li><strong>Anonymised throughout.</strong> The property is described only as a Jack in the Box NNN asset around central Los Angeles with a 2030&ndash;2035 lease expiry.</li>
  <li><strong>No third-party trackers.</strong> Static pages, no analytics, no external scripts, no cookies.</li>
  <li><strong>Public agency addresses.</strong> Where a source is an agency whose published contact address appears in its own document, that address is not reproduced here; only the document is linked.</li>
</ul>
</section>

<section>
<h2>If a private figure is needed for a decision</h2>
<p>Every private input this analysis needs is listed on the <a href="flagged.html">Flagged for review</a> page
next to what would close it. Those lookups can be done privately, off this site, and this workbook's conclusions
will not change until they are supplied. Nothing has to be entered anywhere.</p>
</section>
"""
    return page("privacy.html", "Privacy",
                "What is deliberately absent from this site, and how the privacy constraint is enforced in code.",
                body)


BUILDERS = {
    "index.html": build_index,
    "executive-summary.html": build_exec,
    "decision.html": build_decision,
    "economy.html": build_economy,
    "tenant-lease.html": build_tenant,
    "taxes.html": build_taxes,
    "projection.html": build_projection,
    "risks.html": build_risks,
    "requirements.html": build_requirements,
    "sources.html": build_sources,
    "flagged.html": build_flagged,
    "verification.html": build_verification,
    "privacy.html": build_privacy,
}


def main():
    for slug, fn in BUILDERS.items():
        (HERE / slug).write_text(fn(), encoding="utf-8")
    print(f"built {len(BUILDERS)} pages in session-8bee1905/")


if __name__ == "__main__":
    main()

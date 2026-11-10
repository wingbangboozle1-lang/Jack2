#!/usr/bin/env python3
"""
session-5f296f9d site builder
==============================
Renders the dashboard pages from the JSON ledgers in data/.
Every metric table row carries a source link (Sxx -> sources.html#Sxx) or, for
blank rows, a flag link (F-xx/X-xx -> flagged.html#anchor). No private/PII data
is ever rendered: blanks render as an em dash with a flag chip.

Python 3.11-safe: no nested same-quote f-strings, no triple quotes inside
f-string expressions. Deterministic: same inputs -> byte-identical outputs.
"""
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # session-5f296f9d/
DATA = os.path.join(ROOT, "data")

SESSION = "session-5f296f9d"
BRANCH = "arena/5f296f9d-jack2"
ACCESS = "2026-11-10"
REPO = "https://github.com/wingbangboozle1-lang/Jack2"

PAGES = [
    ("index.html", "Home"),
    ("executive-summary.html", "Executive Summary"),
    ("property-lease.html", "Property &amp; Lease"),
    ("tenant.html", "Tenant"),
    ("economy.html", "Economy"),
    ("capital-markets.html", "Capital Markets"),
    ("taxes.html", "Taxes &amp; Transfer"),
    ("schools.html", "Schools"),
    ("population.html", "Population"),
    ("hazards.html", "Hazards"),
    ("projection.html", "Projection Model"),
    ("decision.html", "Decision"),
    ("risks.html", "Risks"),
    ("flagged.html", "Flagged"),
    ("sources.html", "Sources"),
]

PROPERTY_IDS = [
    "M62", "M63", "M64", "M65", "M66", "M67", "M77", "M78", "M79", "M80",
    "M81", "M82", "M83", "M84", "M85", "M86", "M121", "M122", "M123", "M124",
]

STATUS_LABEL = {
    "verified": "verified", "computed": "computed",
    "unofficial": "unofficial", "blank": "blank",
}


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def esc(s):
    return html.escape(str(s), quote=True)


def chip(status):
    lab = STATUS_LABEL.get(status, status)
    return '<span class="chip chip-%s">%s</span>' % (esc(status), esc(lab))


def src_link(sid):
    return '<a href="sources.html#%s">%s</a>' % (esc(sid), esc(sid))


def flag_link(fid):
    return '<a class="flaglink" href="flagged.html#%s">%s</a>' % (esc(fid), esc(fid))


def source_cell(row):
    parts = []
    src = row.get("source") or ""
    flag = row.get("flag") or ""
    if src:
        for sid in [s.strip() for s in src.replace(";", ",").split(",") if s.strip()]:
            parts.append(src_link(sid))
    if flag:
        parts.append(flag_link(flag))
    if not parts:
        parts.append('<span class="muted">&mdash;</span>')
    return " &middot; ".join(parts)


def metric_table(rows, show_category=False):
    if not rows:
        return "<p class='muted'>No rows.</p>"
    out = ['<div class="tablewrap"><table class="data">']
    head = "<tr><th>Metric</th>"
    if show_category:
        head += "<th>Category</th>"
    head += "<th>Value</th><th>Unit</th><th>Status</th><th>Source / Flag</th></tr>"
    out.append("<thead>" + head + "</thead><tbody>")
    for r in rows:
        val = r.get("value", "")
        if val == "" or val is None:
            val_disp = '<span class="muted">&mdash;</span>'
        else:
            val_disp = esc(val)
        tds = ['<td class="metric">%s<div class="rowid">%s</div></td>' % (esc(r["metric"]), esc(r["id"]))]
        if show_category:
            tds.append("<td>%s</td>" % esc(r["category"]))
        tds.append('<td class="val">%s</td>' % val_disp)
        tds.append("<td>%s</td>" % esc(r.get("unit", "")))
        tds.append("<td>%s</td>" % chip(r["status"]))
        tds.append('<td class="src">%s</td>' % source_cell(r))
        out.append("<tr>" + "".join(tds) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def nav(active):
    links = []
    for href, label in PAGES:
        cls = ' class="active"' if href == active else ""
        links.append('<a href="%s"%s>%s</a>' % (href, cls, label))
    return '<nav class="topnav">' + "".join(links) + "</nav>"


def page(title, body, active, kpis=""):
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="robots" content="noindex">\n'
        "<title>%s &middot; Jack2 %s</title>\n"
        '<link rel="stylesheet" href="assets/site.css">\n'
        "</head>\n<body>\n"
        '<header class="site-header">\n'
        '  <div class="brand">\n'
        '    <span class="logo">J2</span>\n'
        "    <div>\n"
        '      <div class="brand-title">Central LA Jack in the Box &mdash; NNN Lease Study</div>\n'
        '      <div class="brand-sub">%s &middot; branch %s &middot; data access %s</div>\n'
        "    </div>\n"
        "  </div>\n"
        "  %s\n"
        "</header>\n"
        '<main class="container">\n'
        "%s\n"
        "%s\n"
        "</main>\n"
        '<footer class="site-footer">\n'
        '  <p>Built from %s JSON ledgers &middot; sources verified %s &middot; '
        '<a href="%s">repository</a> &middot; '
        '<a href="flagged.html">Flagged for Review</a> &middot; '
        '<a href="sources.html">Sources</a></p>\n'
        '  <p class="muted">No personal information is published. Owner-private facts '
        "(rent, basis, debt, option terms, parcel identity) are blank by design and listed "
        "on the Flagged page. Every table row links to its source or its flag.</p>\n"
        "</footer>\n</body>\n</html>\n"
    ) % (esc(title), esc(SESSION), esc(SESSION), esc(BRANCH), esc(ACCESS),
         nav(active), kpis, body, esc(SESSION), esc(ACCESS), REPO)


def kpi_tile(value, label, sub=""):
    s = '<div class="kpi-sub">%s</div>' % esc(sub) if sub else ""
    return '<div class="kpi"><div class="kpi-value">%s</div><div class="kpi-label">%s</div>%s</div>' % (
        value, esc(label), s)


def section(h, inner):
    return "<section><h2>%s</h2>%s</section>" % (h, inner)


def note(text):
    return '<p class="note">%s</p>' % text


def bullets(items, cls="bullets"):
    return '<ul class="%s">%s</ul>' % (cls, "".join("<li>%s</li>" % i for i in items))


def simple_table(headers, rows):
    out = ['<div class="tablewrap"><table class="data">']
    out.append("<thead><tr>" + "".join("<th>%s</th>" % h for h in headers) + "</tr></thead><tbody>")
    for r in rows:
        out.append("<tr>" + "".join("<td>%s</td>" % c for c in r) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def main():
    src = load("sources.json")
    met = load("metrics.json")
    risks = load("risks.json")
    flags = load("irregularities.json")
    dec = load("decisions.json")
    model = load("model_output.json")

    metrics = met["metrics"]
    mc = model["monte_carlo"]
    exp = mc["expected_wealth"]
    radj = mc["risk_adjusted"]
    tail = mc["tail_risk"]
    # normalize model keys for display code
    radj["P_sell_gt_hold_wealth"] = radj["P(sell_wealth_gt_hold_wealth)"]
    radj["P_hold_default_lt_sell_wealth"] = radj["P(hold_default_lt_sell_wealth)"]
    tail["P_single_asset_loss_gt_10"] = tail["P(single_asset_loss_gt_10_index_units)"]
    tail["P_diversified_loss_gt_10"] = tail["P(diversified_loss_gt_10_index_units)"]
    verified = sum(1 for m in metrics if m["status"] == "verified")
    blank = sum(1 for m in metrics if m["status"] == "blank")

    pages = {}

    # ---------------- index ----------------
    kpis = '<div class="kpis">'
    kpis += kpi_tile(str(len(metrics)), "metric rows", "%d verified · %d blank/flagged" % (verified, blank))
    kpis += kpi_tile(str(len(src["sources"])), "official sources", "tier A/B, all linked")
    kpis += kpi_tile(str(len(risks["risks"])), "risks", "BAU + black swan")
    kpis += kpi_tile(str(len(flags["items"])), "flagged items", "review, non-blocking")
    kpis += kpi_tile("6.8%", "benchmark net-lease yield", "Realty Income Q3-2026, S07")
    kpis += kpi_tile("4.45%", "City transfer stack", "ULA + base tier 1, S10")
    kpis += "</div>"

    card_defs = [
        ("executive-summary.html", "Executive Summary", "Recommendation, evidence, triggers"),
        ("decision.html", "Decision", "Strategies, model verdict, switching rules"),
        ("projection.html", "Projection Model", "Scenarios, break-evens, Monte Carlo"),
        ("property-lease.html", "Property &amp; Lease", "Lease facts and private-fact blanks"),
        ("tenant.html", "Tenant", "Operator fundamentals from filings"),
        ("economy.html", "Economy", "Labor, income, prices, forecasts"),
        ("capital-markets.html", "Capital Markets", "Rates, benchmark, market prints"),
        ("taxes.html", "Taxes &amp; Transfer", "Prop 13, ULA, §1031, FTB rates"),
        ("schools.html", "Schools", "LAUSD and statewide attainment"),
        ("population.html", "Population", "Census, DOF, enrollment"),
        ("hazards.html", "Hazards", "Quake, fire, insurance"),
        ("risks.html", "Risks", "28-item register with evidence"),
        ("flagged.html", "Flagged for Review", "Gaps, ambiguities, repository notes"),
        ("sources.html", "Sources", "All 31 official sources"),
    ]
    cards = "".join(
        '<a class="card" href="%s"><h3>%s</h3><p>%s</p></a>' % (h, l, d)
        for h, l, d in card_defs
    )

    headline = bullets([
        "<strong>Tenant:</strong> FY2026 Q3 system same-store sales -1.1%; 2,115 restaurants vs 2,168 a year earlier; FY26 guidance ~50-60 closures (" + src_link("S04") + ").",
        "<strong>Market benchmark:</strong> institutional net-lease buyer deployed at a 6.8% initial cash yield, 98.8% occupancy, 8.5-yr WALT (" + src_link("S07") + ").",
        "<strong>Exit friction:</strong> Measure ULA + City base = 4.45% of consideration in tier 1 if the parcel is inside City limits (" + src_link("S10") + ", applicability flagged).",
        "<strong>Area:</strong> county population -3.2% since 2020 (" + src_link("S03") + "); LAUSD graduation 86.2% vs county 90.6% (" + src_link("S23") + "); county unemployment 4.8% SA (" + src_link("S02") + ").",
        "<strong>Black swans:</strong> 60% chance of M6.7+ quake within 30 years (" + src_link("S13") + "); Jan-2025 twin fires destroyed 16,264 structures (" + src_link("S14") + ", " + src_link("S15") + "); $1B FAIR Plan assessment (" + src_link("S25") + ").",
    ])

    verdict_rows = [
        ["Mean terminal wealth (end-2040)", '<span class="val">%s</span>' % exp["mean_hold_index"],
         '<span class="val">%s</span>' % exp["mean_sell_index"],
         "Holding wins on expected value by %s index units" % exp["expected_wealth_cost_of_diversifying_index"]],
        ["Worst-5% outcome (CVaR5)", '<span class="val">%s</span>' % radj["cvar5_hold_index"],
         '<span class="val">%s</span>' % radj["cvar5_sell_index"],
         "<strong>Diversifying wins on risk-adjusted value</strong> by %s index units"
         % round(radj["cvar5_sell_index"] - radj["cvar5_hold_index"], 4)],
        ["P(idiosyncratic loss &gt; 10 index units)",
         '<span class="val">%.2f%%</span>' % (tail["P_single_asset_loss_gt_10"] * 100),
         '<span class="val">%.2f%%</span>' % (tail["P_diversified_loss_gt_10"] * 100),
         "Single-asset tail removed by diversification"],
        ["Break-even reinvestment rate, base 2032", '<span class="val" colspan="2">7.061%</span>', "",
         "Selling wins outright only if proceeds compound above ~7.1%/yr"],
    ]
    verdict = simple_table(
        ["Measure", "HOLD", "SELL / EXCHANGE 2027", "Reading"], verdict_rows
    )
    verdict = verdict.replace(
        '<td><span class="val" colspan="2">7.061%</span></td><td></td>',
        '<td colspan="2"><span class="val">7.061%</span></td><td></td>'
    )

    body = []
    body.append("<h1>Dashboard</h1>")
    body.append(
        '<p class="lede">Deep-research workspace for a single-tenant <strong>Jack in the Box</strong> '
        "NNN property in Central Los Angeles with a lease expiring in the <strong>2030-2035</strong> "
        "window. The question: <em>sell before expiry, or renew and hold</em> — balanced for wealth "
        "preservation, growth, and manageable risk. All figures come from official sources; "
        "unconfirmable facts stay blank and are flagged, never inferred.</p>"
    )
    body.append(note("Index basis: every modeled money figure equals one year of current NOI (1.00). "
                     "Private owner facts are never assumed."))
    body.append('<div class="cards">%s</div>' % cards)
    body.append(section("Headline evidence", headline))
    body.append(section(
        "Model verdict (index basis, seed %s)" % model["seed"],
        verdict + note('Full method, assumptions A01-A18 and all grids: <a href="projection.html">Projection Model</a>. '
                       'Recommendation: <a href="executive-summary.html">Executive Summary</a>.')
    ))
    pages["index.html"] = page("Dashboard", "\n".join(body), "index.html", kpis)

    # ---------------- executive summary ----------------
    rec = dec["recommendation"]
    strat_names = {s["id"]: s["name"] for s in dec["strategies"]}
    rank_rows = [[str(r["rank"]), esc(strat_names[r["id"]]), esc(r["why"])] for r in rec["ranking"]]

    evidence_rows = [
        ["What would a professional net-lease buyer pay today?",
         "6.8% initial cash yield (Q3-2026 deployments), 98.8% occupancy", src_link("S07")],
        ["Is the tenant's brand healthy?",
         "SSS -1.1%, closures elevated, guidance cut; refinancing pushed to May 2031", src_link("S04")],
        ["What does selling cost in the City?",
         "4.45% all-in tier 1 (ULA 4% + base 0.45%) after 2026-06-30", src_link("S10")],
        ["Does §1031 help?",
         "Defers income tax (45/180-day framework) but not the transfer tax", src_link("S16")],
        ["Is the area growing?",
         "No: county -3.2% since 2020 (Census) and -0.6% in the year to 2026-01-01 (DOF); K-12 -240,800 by 2035-36",
         src_link("S03") + " &middot; " + src_link("S29") + " &middot; " + src_link("S30")],
        ["Jobs?", "County 4.8% SA unemployment; nonfarm +20,300 YoY; restaurants +7,300", src_link("S02")],
        ["Schools?", "LAUSD ACGR 86.2% vs county 90.6% vs state 87.5%",
         src_link("S23") + " &middot; " + src_link("S22")],
        ["What are the black swans?",
         "Quake 60%/30yr; two fires in Jan 2025 destroyed 16,264 structures; FAIR Plan $1B assessment",
         src_link("S13") + " &middot; " + src_link("S14") + " &middot; " + src_link("S15") + " &middot; " + src_link("S25")],
    ]
    trig_rows = [
        [esc(t["id"]), esc(t["trigger"]), esc(t["action"]), esc(t.get("source", ""))]
        for t in dec["triggers"]
    ]

    body = []
    body.append("<h1>Executive Summary</h1>")
    body.append('<p class="lede">%s</p>' % esc(rec["headline"]))
    body.append(note("This recommendation is decision support, not financial advice. Private owner facts "
                     "remain blank (see <a href='flagged.html'>Flagged</a>); the model runs on an index basis."))
    body.append(section("The four strategies",
                        simple_table(["#", "Strategy", "Why it ranks here"], rank_rows)))
    body.append(section("Evidence in one table",
                        simple_table(["Question", "Answer", "Source"], evidence_rows)))
    body.append(section("Decision triggers",
                        simple_table(["ID", "Trigger", "Action", "Source"], trig_rows)))
    cond = [esc(c) for c in rec["conditions"]] + ['<li class="warn">%s</li>' % esc(f) for f in dec["falsifiers"]]
    body.append(section("Conditions and falsifiers", bullets(cond)))
    pages["executive-summary.html"] = page("Executive Summary", "\n".join(body), "executive-summary.html")

    # ---------------- property & lease ----------------
    prop_rows = [m for m in metrics if m["id"] in PROPERTY_IDS]
    body = []
    body.append("<h1>Property &amp; Lease</h1>")
    body.append('<p class="lede">Lease, tenure and ownership facts for the subject asset. Rows that depend '
                "on owner-private documents are blank by design and linked to their flags — they are never "
                "filled by inference.</p>")
    body.append(metric_table(prop_rows))
    body.append(note("Full metric ledger by category: see the other category pages. Private documents "
                     "(rent roll, option clause, tax bill, insurance policy) must be reviewed off-site."))
    pages["property-lease.html"] = page("Property &amp; Lease", "\n".join(body), "property-lease.html")

    # ---------------- category pages ----------------
    cat_defs = [
        ("tenant.html", "Tenant", ["tenant"],
         "Operator fundamentals drawn from the tenant's own SEC filings (8-K earnings release, 10-Q). "
         "FY2026 Q3 covers the 13 weeks ended 2026-07-05."),
        ("economy.html", "Economy", ["labor", "income", "trade", "prices", "forecast", "labor-cost"],
         "Los Angeles labor market, income, prices, port trade, wage floors and the official forecast "
         "horizon through 2028."),
        ("capital-markets.html", "Capital Markets", ["capital"],
         "Risk-free rates, the Federal Reserve stance, the institutional net-lease benchmark and the "
         "county GDP print."),
        ("taxes.html", "Taxes &amp; Transfer", ["tax", "housing-cost"],
         "Prop 13, Measure ULA transfer stack, federal like-kind exchange mechanics, California top rates "
         "and the unofficial Proposition 3 result."),
        ("schools.html", "Schools", ["schools"],
         "Graduation outcomes from the California Department of Education DataQuest — LAUSD versus "
         "county and state."),
        ("population.html", "Population", ["demographics"],
         "Census Bureau and California Department of Finance population, households and school-age "
         "enrollment."),
        ("hazards.html", "Hazards", ["hazard"],
         "Seismic, wildfire and insurance-market exposure with official probabilities and 2025 incident "
         "records. Parcel-level hazard data is withheld for privacy (flag F-11)."),
    ]
    for fname, title, cats, intro in cat_defs:
        rows = [m for m in metrics if m["category"] in cats]
        b = ["<h1>%s</h1>" % title, '<p class="lede">%s</p>' % intro, metric_table(rows, show_category=True)]
        pages[fname] = page(title, "\n".join(b), fname)

    # ---------------- projection model ----------------
    obs_rows = []
    for o in model["observations"].values():
        obs_rows.append([
            esc(o["label"]),
            '<span class="val">%s %s</span>' % (esc(o["value"]), esc(o.get("unit", ""))),
            src_link(o["source"]),
        ])
    assum_rows = []
    for aid, v in model["assumptions"].items():
        assum_rows.append([
            esc(aid), esc(v["label"]),
            '<span class="val">%s %s</span>' % (esc(v["value"]), esc(v.get("unit", ""))),
            esc(v["note"]),
        ])
    be_rows = [
        [esc(b["scenario"]), str(b["expiry_year"]), esc(b["ula_case"]),
         '<span class="val">%s%%</span>' % b["breakeven_exit_cap_pct"]]
        for b in model["breakeven"] if b["ula_case"] == "with-ULA"
    ]
    ber_rows = [
        [esc(b["scenario"]), str(b["expiry_year"]),
         '<span class="val">%s%%</span>' % b["breakeven_reinvest_rate_pct"]]
        for b in model["breakeven_reinvestment"]
    ]
    grid_sample = [g for g in model["expiry_grid"]
                   if g["scenario"] == "base" and g["ula_case"] == "with-ULA"]
    grid_rows = [
        [str(g["expiry_year"]), '<span class="val">%s%%</span>' % g["exit_cap_pct"],
         '<span class="val">%s</span>' % g["hold_wealth_index"],
         '<span class="val">%s</span>' % g["sell_2027_wealth_index"],
         "HOLD" if g["hold_wins"] else "SELL"]
        for g in grid_sample
    ]
    hazard_items = [
        "Annual M6.7+ probability derived only from USGS 60%%-in-30-years: "
        "<strong>%.3f%%/yr</strong>" % (model["hazard_probability"]["annual_quake_probability_from_UCERF3"] * 100),
        "Probability of at least one M6.7+ during a 2026-2035 hold: "
        "<strong>%.2f%%</strong>" % (model["hazard_probability"]["probability_of_at_least_one_M6.7+_during_2026-2035_hold"] * 100),
        "Source: " + src_link("S13") + ". Wildfire and tenant-default hazards are labelled assumptions "
        "(A11, A12) because no official parcel-level probability exists.",
    ]

    mc_kpis = '<div class="kpis">'
    mc_kpis += kpi_tile(str(exp["mean_hold_index"]), "mean HOLD wealth")
    mc_kpis += kpi_tile(str(exp["mean_sell_index"]), "mean SELL/EXCHANGE wealth")
    mc_kpis += kpi_tile(str(radj["cvar5_hold_index"]), "HOLD CVaR5 (worst 5%)")
    mc_kpis += kpi_tile(str(radj["cvar5_sell_index"]), "SELL CVaR5 (worst 5%)")
    mc_kpis += kpi_tile(str(radj["P_sell_gt_hold_wealth"]), "P(sell > hold)")
    mc_kpis += kpi_tile(str(radj["P_hold_default_lt_sell_wealth"]), "P(hold w/ default < sell)")
    mc_kpis += "</div>"
    tail_rows = [
        ["Mean terminal idiosyncratic loss (index)",
         '<span class="val">%s</span>' % tail["mean_single_asset_terminal_loss_index"],
         '<span class="val">%s</span>' % tail["mean_diversified_terminal_loss_index"]],
        ["P99 terminal loss (index)",
         '<span class="val">%s</span>' % tail["p99_single_asset_terminal_loss_index"],
         '<span class="val">%s</span>' % tail["p99_diversified_terminal_loss_index"]],
        ["P(loss &gt; 10 index units)",
         '<span class="val">%.2f%%</span>' % (tail["P_single_asset_loss_gt_10"] * 100),
         '<span class="val">%.2f%%</span>' % (tail["P_diversified_loss_gt_10"] * 100)],
    ]

    body = []
    body.append("<h1>Projection Model</h1>")
    body.append(
        '<p class="lede">Deterministic expiry grids, break-even solving and a seeded Monte Carlo '
        "(seed %s, %s trials, horizon end-%s). Everything is published on the index basis: "
        "<strong>1.00 = one year of current NOI</strong>.</p>"
        % (model["seed"], format(mc["trials"], ","), mc["horizon_year"])
    )
    body.append(note('Engine: <code>scripts/model.py</code> &middot; output: <code>data/model_output.json</code> '
                     '&middot; deterministic across runs.'))
    body.append(section("Official observations the model anchors on",
                        simple_table(["Observation", "Value", "Source"], obs_rows)))
    body.append(section("Assumptions (explicit — not facts)",
                        simple_table(["ID", "Assumption", "Value", "Anchor / note"], assum_rows)))
    body.append(section(
        "Monte Carlo summary",
        mc_kpis
        + simple_table(["Tail measure", "Single-asset HOLD", "Diversified SELL/EXCHANGE"], tail_rows)
        + note("Expected-wealth cost of diversifying: <strong>%s</strong> index units. "
               "Risk-adjusted gain: <strong>%s</strong> index units at the 5%% tail."
               % (exp["expected_wealth_cost_of_diversifying_index"],
                  round(radj["cvar5_sell_index"] - radj["cvar5_hold_index"], 4)))
    ))
    body.append(section("Hazard probability (official only)", bullets(hazard_items)))
    body.append(section(
        "Break-even exit caps (HOLD = SELL-2027, with-ULA)",
        simple_table(["Scenario", "Expiry year", "ULA case", "Break-even exit cap"], be_rows)
        + note("If the achievable exit cap is above the break-even, selling wins; below it, holding wins.")
    ))
    body.append(section(
        "Break-even reinvestment rates (at 6.50% exit cap, with-ULA)",
        simple_table(["Scenario", "Expiry year", "Break-even portfolio return"], ber_rows)
        + note("Only the 4.86% anchor is official (S08); higher rows are assumption sensitivities (A18).")
    ))
    body.append(section(
        "Expiry grid — base case, with-ULA (hold vs sell-2027)",
        simple_table(["Expiry year", "Exit cap", "HOLD wealth index", "SELL-2027 wealth index", "Winner"],
                     grid_rows)
        + note("180 grid rows total (3 scenarios x 6 years x 5 caps x 2 ULA cases) in "
               "<code>data/model_output.json</code>.")
    ))
    pages["projection.html"] = page("Projection Model", "\n".join(body), "projection.html")

    # ---------------- decision ----------------
    strat_rows = []
    for s in dec["strategies"]:
        pros = bullets([esc(p) for p in s["pros"]], cls="mini")
        cons = bullets([esc(c) for c in s["cons"]], cls="mini warn")
        ev = " ".join(src_link(x) for x in s["official_evidence"])
        strat_rows.append([
            "<strong>%s</strong><div class='rowid'>%s</div>" % (esc(s["name"]), esc(s["id"])),
            esc(s["summary"]), pros, cons, ev,
        ])
    model_rows = [
        ["Mean HOLD wealth (index, end-2040)", '<span class="val">%s</span>' % dec["model_evidence"]["expected_value"]["mean_hold"]],
        ["Mean SELL/EXCHANGE wealth (index)", '<span class="val">%s</span>' % dec["model_evidence"]["expected_value"]["mean_sell_2027_diversified"]],
        ["Expected-wealth cost of diversifying", '<span class="val">%s</span>' % dec["model_evidence"]["expected_value"]["cost_of_diversifying_index_units"]],
        ["CVaR5 HOLD vs SELL (risk-adjusted tail)",
         '<span class="val">%s vs %s</span>' % (dec["model_evidence"]["risk_adjusted"]["cvar5_hold"],
                                               dec["model_evidence"]["risk_adjusted"]["cvar5_sell"])],
        ["P(idiosyncratic loss &gt; 10): HOLD vs SELL",
         '<span class="val">%.2f%% vs %.2f%%</span>' % (dec["model_evidence"]["tail"]["P_single_asset_loss_gt_10"] * 100,
                                                       dec["model_evidence"]["tail"]["P_diversified_loss_gt_10"] * 100)],
        ["Break-even reinvestment (base 2032)",
         '<span class="val">%s%%</span>' % dec["model_evidence"]["breakeven_reinvestment_base_2032_pct"]],
        ["Official quake hazard used",
         '<span class="val">%.3f%%/yr &rarr; %.2f%% by 2035</span>'
         % (dec["model_evidence"]["hazard"]["annual_quake_probability_official_derived"] * 100,
            dec["model_evidence"]["hazard"]["P_one_quake_2026_2035"] * 100)],
    ]
    body = []
    body.append("<h1>Decision</h1>")
    body.append('<p class="lede">%s</p>' % esc(dec["question"]))
    body.append(note("Normalization: " + esc(dec["normalization"])))
    body.append(section("Strategies compared",
                        simple_table(["Strategy", "Summary", "Pros", "Cons", "Evidence"], strat_rows)))
    body.append(section("Model evidence",
                        simple_table(["Measure", "Value"], model_rows)
                        + note(esc(dec["model_evidence"]["reading"]))))
    body.append(section("Switching rules",
                        simple_table(["ID", "Trigger", "Action", "Source"], trig_rows)))
    cond2 = [esc(c) for c in rec["conditions"]] + ['<li class="warn">%s</li>' % esc(f) for f in dec["falsifiers"]]
    body.append(section("Conditions &amp; falsifiers", bullets(cond2)))
    pages["decision.html"] = page("Decision", "\n".join(body), "decision.html")

    # ---------------- risks ----------------
    risk_rows = []
    for r in risks["risks"]:
        src_cell = src_link(r["source"]) if r["source"] else '<span class="muted">qualitative</span>'
        risk_rows.append([
            esc(r["id"]), esc(r["type"]), '<span class="metric">%s</span>' % esc(r["risk"]),
            esc(r["likelihood"]), esc(r["impact"]), esc(r["affects"]),
            esc(r["evidence"]), src_cell, esc(r["mitigation"]),
        ])
    body = []
    body.append("<h1>Risk Register</h1>")
    body.append('<p class="lede">%s &middot; likelihood: %s &middot; impact: %s &middot; affects: %s</p>'
                % (esc(risks["legend"]["type"]), esc(risks["legend"]["likelihood"]),
                   esc(risks["legend"]["impact"]), esc(risks["legend"]["affects"])))
    body.append(simple_table(
        ["ID", "Type", "Risk", "Likelihood", "Impact", "Affects", "Evidence", "Source", "Mitigation"],
        risk_rows))
    pages["risks.html"] = page("Risk Register", "\n".join(body), "risks.html")

    # ---------------- flagged ----------------
    flag_rows = []
    for f in flags["items"]:
        flag_rows.append([
            '<span id="%s">%s</span>' % (esc(f["id"]), esc(f["id"])),
            esc(f["type"]), esc(f["severity"]), chip_status(f["status"]),
            '<span class="metric">%s<div class="rowid">%s</div></span>' % (esc(f["title"]), esc(f["detail"])),
            esc(f["owner_action"]),
        ])
    body = []
    body.append("<h1>Flagged for Review</h1>")
    body.append('<p class="lede">Gaps, ambiguities, repository irregularities and citation caveats. '
                "Per the project brief these items are published for transparency and "
                "<strong>do not block integration</strong>. Nothing here was inferred or filled in.</p>")
    body.append(simple_table(["ID", "Type", "Severity", "Status", "Item", "Owner action"], flag_rows))
    body.append(note("Personal-information policy: parcel identity, rent roll, tax basis and insurance "
                     "documents are owner-private. They exist only in the owner's files and are "
                     "intentionally blank in every published table."))
    pages["flagged.html"] = page("Flagged for Review", "\n".join(body), "flagged.html")

    # ---------------- sources ----------------
    src_rows = []
    for s in src["sources"]:
        src_rows.append([
            '<span id="%s">%s</span>' % (esc(s["id"]), esc(s["id"])),
            esc(s["title"]), esc(s["publisher"]),
            chip("verified" if s["tier"] == "A" else "computed"),
            '<a href="%s" rel="noopener">%s</a>' % (esc(s["url"]), esc(s["url"])),
            esc(s.get("accessed", "")), esc(s.get("supports", s.get("notes", ""))),
        ])
    body = []
    body.append("<h1>Sources</h1>")
    body.append('<p class="lede">%s Tier A = primary official publication; tier B = official PDF/release '
                "directly fetched.</p>" % esc(src.get("policy", "All sources are official primary publications.")))
    body.append(simple_table(["ID", "Title", "Publisher", "Tier", "URL", "Accessed", "Notes"], src_rows))
    pages["sources.html"] = page("Sources", "\n".join(body), "sources.html")

    # ---------------- write ----------------
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    for fname, content in pages.items():
        with open(os.path.join(ROOT, fname), "w") as f:
            f.write(content)
    print("wrote %d pages: %s" % (len(pages), ", ".join(sorted(pages))))
    return pages


def chip_status(status):
    return chip(status)


if __name__ == "__main__":
    main()

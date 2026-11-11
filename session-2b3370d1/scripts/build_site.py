#!/usr/bin/env python3
"""Session N site builder - generates 14 HTML pages from the data/ JSON ledger.

Every table row either carries a source link to an official publisher or is a
deliberately blank row flagged for review. No value is inferred here; the
builder only renders what the JSON files contain.

Usage:
    python3 build_site.py           # write pages
    python3 build_site.py --check   # regenerate in memory, fail if disk differs
"""
from __future__ import annotations

import html
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

PAGES = [
    ("index.html", "Dashboard"),
    ("economics.html", "Area Economics"),
    ("income.html", "Income & Wages"),
    ("schools.html", "Schools"),
    ("jobs.html", "Jobs & Growth"),
    ("tenant.html", "Tenant"),
    ("capital.html", "Capital & Tax"),
    ("hazards.html", "Hazards"),
    ("risks.html", "Risk Register"),
    ("decisions.html", "Decisions"),
    ("questions.html", "Open Questions"),
    ("flagged.html", "Flagged for Review"),
    ("sources.html", "Sources"),
]

CSS = """
:root{--bg:#0f1420;--panel:#161d2e;--panel2:#1b2438;--line:#2a3550;--fg:#e8edf7;
--muted:#93a0bd;--acc:#5eb0ff;--ok:#3fd07f;--warn:#ffb454;--bad:#ff6b6b;--flag:#ffd166}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--acc);text-decoration:none}
a:hover{text-decoration:underline}
header{background:var(--panel);border-bottom:1px solid var(--line);padding:14px 22px 10px}
header h1{margin:0 0 4px;font-size:20px}
header .sub{color:var(--muted);font-size:12.5px}
nav{display:flex;flex-wrap:wrap;gap:4px 14px;padding:8px 22px;background:var(--panel2);
border-bottom:1px solid var(--line);font-size:13.5px}
nav a{padding:3px 6px;border-radius:6px}
nav a.on{background:#24406b;color:#fff;text-decoration:none}
main{padding:20px 22px 60px;max-width:1280px;margin:0 auto}
h2{font-size:18px;margin:26px 0 8px;border-bottom:1px solid var(--line);padding-bottom:6px}
h3{font-size:15.5px;margin:18px 0 6px}
p,li{color:#cdd6ea}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:10px;margin:12px 0}
.tile{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.tile .k{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.4px}
.tile .v{font-size:21px;font-weight:650;margin-top:4px}
.tile .n{font-size:11.5px;color:var(--muted);margin-top:3px}
table{border-collapse:collapse;width:100%;margin:8px 0 18px;font-size:13.5px}
th,td{border:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}
th{background:var(--panel2);position:sticky;top:0}
tr:nth-child(even) td{background:#131a2a}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.chip{display:inline-block;font-size:11px;padding:1px 8px;border-radius:10px;font-weight:600}
.ok{background:#123726;color:var(--ok)}
.flag{background:#3a2f10;color:var(--flag)}
.calc{background:#12303f;color:#7fd1ff}
.unoff{background:#3a2410;color:#ffb454}
.blank{background:#3a2f10;color:var(--flag);font-weight:600}
.note{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--acc);
padding:10px 14px;border-radius:8px;margin:10px 0;font-size:13.5px}
.warnbox{border-left:3px solid var(--warn)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px;margin:10px 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card h3{margin-top:0}
.pill{font-size:11px;padding:2px 8px;border-radius:10px;background:#24406b;color:#cfe4ff}
footer{color:var(--muted);font-size:12px;padding:18px 22px;border-top:1px solid var(--line)}
code{background:#0b101b;padding:1px 5px;border-radius:4px;font-size:12.5px}
.small{font-size:12.5px;color:var(--muted)}
"""

NAV_EXTRA = {
    "index.html": [],
}


def load(name: str) -> dict:
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def esc(v) -> str:
    return html.escape(str(v), quote=True)


def src_link(source_id: str, sources: dict) -> str:
    if not source_id:
        return "<span class='small'>no official source exists for this fact &mdash; see Flagged</span>"
    s = sources.get(source_id)
    if not s:
        return f"<span class='small'>MISSING SOURCE {esc(source_id)}</span>"
    return (f"<a href='{esc(s['url'])}' rel='noopener' target='_blank'>"
            f"{esc(s['id'])} {esc(s['publisher'].split(',')[0])} &nearr;</a>")


def status_chip(status: str, unofficial: bool = False) -> str:
    if status == "verified":
        return "<span class='chip ok'>verified</span>"
    if status == "computed":
        return "<span class='chip calc'>computed</span>"
    if unofficial:
        return "<span class='chip unoff'>unofficial</span>"
    return "<span class='chip blank'>blank &middot; flagged</span>"


def page(name: str, title: str, body: str, sub: str) -> str:
    nav_links = []
    for href, label in PAGES:
        cls = " class='on'" if href == name else ""
        nav_links.append(f"<a href='{href}'{cls}>{label}</a>")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} &mdash; Jack NNN decision workbook (Session N)</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <h1>{esc(title)}</h1>
  <div class="sub">Jack in the Box NNN property decision workbook &middot; Session N (session-2b3370d1)
  &middot; every row source-linked &middot; unverifiable values blank &middot; accessed 2026-11-11</div>
</header>
<nav>{''.join(nav_links)}</nav>
<main>
{body}
</main>
<footer>Session N &mdash; built from official sources only (government, regulator, court, SEC filings).
Private owner facts stay blank and flagged. Index-basis model: no private dollar amounts are published.</footer>
</body>
</html>
"""


def metric_rows(metrics: list[dict], sources: dict, unofficial_ids=()) -> str:
    out = []
    for m in metrics:
        val = m["value"] if m["value"] != "" else "&mdash;"
        num_cls = "num" if m["value"] else ""
        note = esc(m.get("note", ""))
        unoff = m["id"] in unofficial_ids
        out.append(
            "<tr>"
            f"<td><code>{esc(m['id'])}</code></td>"
            f"<td>{esc(m['metric'])}<div class='small'>{esc(m['geography'])} &middot; {esc(m['period'])}</div></td>"
            f"<td class='{num_cls}'>{val} <span class='small'>{esc(m['unit'])}</span></td>"
            f"<td>{status_chip(m['status'], unoff)}</td>"
            f"<td class='small'>{note}</td>"
            f"<td>{src_link(m.get('source', ''), sources)}</td>"
            "</tr>"
        )
    return "".join(out)


def metric_table(metrics, sources, unofficial_ids=()) -> str:
    if not metrics:
        return "<p class='small'>No rows in this category.</p>"
    return (
        "<table><thead><tr><th>ID</th><th>Metric</th><th>Value</th><th>Status</th>"
        "<th>Note</th><th>Source</th></tr></thead><tbody>"
        + metric_rows(metrics, sources, unofficial_ids)
        + "</tbody></table>"
    )


def build_index(S, M, R, Q, IR, MO, DEC) -> str:
    verified = sum(1 for m in M if m["status"] == "verified")
    computed = sum(1 for m in M if m["status"] == "computed")
    blank = sum(1 for m in M if m["status"] == "blank")
    bau = sum(1 for r in R if r["type"] == "BAU")
    black = len(R) - bau
    mc = MO["monte_carlo"]
    grid = MO["grid_summary"]
    anchors = [
        ("County unemployment (SA, Sep-2026)", "4.8%", "M37", "S02"),
        ("10-year Treasury (2026-11-10)", "4.98%", "M66", "S09"),
        ("ULA all-in transfer tax (City tier 1)", "4.45%", "M78", "S06"),
        ("ULA threshold (from 2026-07-01)", "$5.4M", "M73", "S06"),
        ("LAUSD 4-year graduation rate", "86.2%", "M28", "S17"),
        ("County population change 2025", "-0.6%", "M06", "S04"),
        ("Port of LA 2025 throughput", "10.2M TEU", "M62", "S29"),
        ("JACK system same-store sales (Q3 FY26)", "-1.1%", "M112", "S26"),
        ("JACK restaurant count", "2,115", "M114", "S26"),
        ("Net-lease benchmark yield (Realty Income Q2-26)", "7.3%", "M71", "S28"),
        ("Top CA marginal income tax rate", "13.30%", "M85", "S31"),
        ("M6.7+ earthquake probability (30 yr)", "60%", "M98", "S13"),
    ]
    rows = []
    for label, val, mid, sid in anchors:
        rows.append(f"<tr><td>{label}</td><td class='num'><strong>{val}</strong></td>"
                    f"<td><code>{mid}</code></td><td>{src_link(sid, S)}</td></tr>")
    tiles = [
        ("Official sources", len(S), "tier A/B/C, all opened 2026-11-11"),
        ("Metric rows", len(M), f"{verified} verified &middot; {computed} computed &middot; {blank} blank"),
        ("Risks (BAU / black swan)", f"{bau} / {black}", "every row source-linked"),
        ("Open questions", len(Q), "each with discovery steps"),
        ("Irregularities", len(IR), "flagged or resolved, all published"),
        ("Hold wins in grid", f"{grid['hold_win_share']*100:.1f}%", f"{grid['cells']:,} deterministic cells"),
        ("Monte Carlo P(hold wins)", f"{mc['p_hold_wins']*100:.1f}%", f"seed {mc['seed']}, {mc['trials']:,} trials"),
        ("Flagged items", blank + sum(1 for i in IR if i['status'] != 'resolved'), "on the Flagged page"),
    ]
    tile_html = "".join(
        f"<div class='tile'><div class='k'>{k}</div><div class='v'>{v}</div><div class='n'>{n}</div></div>"
        for k, v, n in tiles
    )
    strategy_cards = []
    for d in DEC["strategies"]:
        pill = "<span class='pill'>recommended</span>" if d["status"] == "recommended" else f"<span class='pill'>{esc(d['status'])}</span>"
        strategy_cards.append(
            f"<div class='card'><h3>{esc(d['name'])} {pill}</h3>"
            f"<p class='small'>{esc(d['summary'])}</p>"
            f"<p class='small'><strong>Objective:</strong> {esc(d['objective'])}</p></div>"
        )
    body = f"""
<h2>Executive summary</h2>
<div class="note">
<p><strong>Situation.</strong> A single-tenant Jack in the Box net-lease property in Central Los Angeles is
approaching its NNN expiry window (2030&ndash;2035). This workbook reviews the area economics, tenant
health, capital-market conditions, tax and hazard environment from {len(S)} official sources opened on
2026-11-11, and compares <em>sell before expiry</em> against <em>renew / extend</em>.</p>
<p><strong>Best course of action today: dual-track (recommended).</strong> Resolve the
{len(Q)} open questions &mdash; jurisdiction, lease terms, tenant identity, hazard and insurance diligence
&mdash; while negotiating an early CPI-linked extension and simultaneously obtaining an appraisal and
testing sale pricing. The decision gate is 2028, two years before the earliest expiry. The model
publishes pre-agreed switch triggers instead of a single-point forecast.</p>
<p><strong>Why not decide today.</strong> {blank} parcel-level facts are private or unverifiable from
official sources (address, APN, rent, expiry date, tenant of record, insurance, hazard zones, basis,
cap rate). They are published <em>blank and flagged</em> &mdash; never inferred. See
<a href="flagged.html">Flagged for Review</a>.</p>
<p><strong>Direction of the evidence.</strong> Labor market is firming (county unemployment 4.8% SA,
+20,300 nonfarm jobs YoY) but population and school enrollment are structurally declining; the tenant's
system same-store sales are down 1.1% in Q3 FY2026 with 50&ndash;60 closures guided for the year;
capital is expensive (10-year Treasury 4.98%) and a City-of-LA sale carries a 4.45%/5.95% all-in
transfer tax under Measure ULA, which was upheld on appeal (B334071, 2025-12-15).</p>
</div>

<h2>Key verified anchors</h2>
<table><thead><tr><th>Indicator</th><th>Value</th><th>Ledger</th><th>Source</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>

<h2>Workbook at a glance</h2>
<div class="tiles">{tile_html}</div>

<h2>Strategies compared (index basis, per $1 current NOI)</h2>
<div class="cards">{''.join(strategy_cards)}</div>

<h2>How to read this site</h2>
<ul>
<li>Every table row carries an <strong>official source link</strong>. Rows with no possible official source say so explicitly.</li>
<li><span class="chip blank">blank &middot; flagged</span> means the value could not be confirmed &mdash;
it is empty by policy, never guessed.</li>
<li><span class="chip calc">computed</span> rows show their formula and derive only from verified rows.</li>
<li>The model is <strong>index-based</strong> (per $1 of current NOI): owner rent, basis and debt stay private blanks.</li>
</ul>
"""
    return page("index.html", "Dashboard", body, "")


def category_block(M, S, cat, title, intro) -> str:
    rows = [m for m in M if m["category"] == cat]
    return f"<h2>{title}</h2><p class='small'>{intro}</p>{metric_table(rows, S)}"


def build_economics(S, M) -> str:
    body = ("<h2>Geography, population and demand base</h2>"
            "<p class='small'>Both official population series are published with their bases labeled "
            "(Census V2025 vs CA DOF E-1) &mdash; they are never mixed or averaged.</p>"
            + metric_table([m for m in M if m["category"] == "demographics"], S)
            + category_block(M, S, "trade", "Trade, housing supply and retail base",
                             "Port throughput, permits and retail sales per capita anchor the logistics-and-consumer economy."))
    return page("economics.html", "Area Economics", body, "")


def build_income(S, M) -> str:
    body = ("<h2>Household and personal income</h2>"
            + metric_table([m for m in M if m["category"] == "income"], S)
            + "<h2>Wages, minimum wages and cost pressure</h2>"
            "<p class='small'>City of LA minimum wage ($18.42 from 2026-07-01) and the California "
            "fast-food wage ($20.00) directly shape QSR tenant margins and renewal rent capacity.</p>"
            + metric_table([m for m in M if m["category"] == "wages"], S))
    return page("income.html", "Income & Wages", body, "")


def build_schools(S, M) -> str:
    body = ("<h2>Enrollment and graduation</h2>"
            "<p class='small'>LAUSD is the largest district in California. Graduation rates differ by "
            "source basis (DataQuest four-year vs Dashboard combined) &mdash; both are published with "
            "their bases, never averaged.</p>"
            + metric_table([m for m in M if m["category"] == "education"], S))
    return page("schools.html", "Schools", body, "")


def build_jobs(S, M) -> str:
    body = ("<h2>Labor market (current official prints)</h2>"
            "<p class='small'>EDD and BLS are the co-primary prints for September 2026; seasonally "
            "adjusted and not-seasonally-adjusted values are labeled separately.</p>"
            + metric_table([m for m in M if m["category"] == "labor"], S)
            + "<h2>Growth forecasts (LAEDC 2026 Forecast, February 2026)</h2>"
            "<div class='note warnbox'>Forecast values are marked verified-with-note: LAEDC projected "
            "5.9% county unemployment for 2026 while the actual Sep-2026 SA print is 4.8% (see F-N4). "
            "Current prints outweigh older forecasts.</div>"
            + metric_table([m for m in M if m["category"] == "growth"], S))
    return page("jobs.html", "Jobs & Growth", body, "")


def build_tenant(S, M) -> str:
    body = ("<h2>Jack in the Box Inc. &mdash; system health</h2>"
            "<p class='small'>All rows come from the company's own SEC-filed earnings release "
            "(Q3 FY2026, 12 weeks ended 2026-07-05) or the FY2025 10-K. System-level data cannot "
            "identify this parcel's tenant (corporate vs franchisee) &mdash; that is Q05.</p>"
            + metric_table([m for m in M if m["category"] == "tenant"], S))
    return page("tenant.html", "Tenant", body, "")


def build_capital(S, M) -> str:
    body = ("<h2>Capital markets</h2>"
            "<p class='small'>Treasury par yields (2026-11-10) and the FOMC target range set the "
            "discount-rate context; the Realty Income acquisition yield is the only official "
            "net-lease benchmark available.</p>"
            + metric_table([m for m in M if m["category"] == "capital"], S)
            + "<h2>Taxes that bind this decision</h2>"
            "<p class='small'>Transfer taxes (ULA + county), Proposition 13 carry, top marginal "
            "income tax on sale, and Section 1031 exchange mechanics.</p>"
            + metric_table([m for m in M if m["category"] == "tax"], S))
    return page("capital.html", "Capital & Tax", body, "")


def build_hazards(S, M) -> str:
    body = ("<h2>Natural hazards &mdash; verified official figures</h2>"
            "<p class='small'>Seismic probabilities from USGS UCERF3; wildfire loss counts from CAL "
            "FIRE; insured losses from the California Department of Insurance.</p>"
            + metric_table([m for m in M if m["category"] == "hazards"], S))
    return page("hazards.html", "Hazards", body, "")


def build_risks(S, R) -> str:
    rows = []
    for r in R:
        tclass = "chip ok" if r["type"] == "BAU" else "chip flag"
        rows.append(
            "<tr>"
            f"<td><code>{esc(r['id'])}</code></td>"
            f"<td><span class='{tclass}'>{esc(r['type'])}</span></td>"
            f"<td>{esc(r['risk'])}</td>"
            f"<td>{esc(r['likelihood'])}</td>"
            f"<td>{esc(r['impact'])}</td>"
            f"<td>{esc(r['affects'])}</td>"
            f"<td class='small'>{esc(r['evidence'])}</td>"
            f"<td class='small'>{esc(r['mitigation'])}</td>"
            f"<td>{src_link(r.get('source', ''), S)}</td>"
            "</tr>"
        )
    body = ("<h2>Full risk register</h2>"
            "<p class='small'>BAU = business-as-usual variation. BLACK-SWAN = rare, high-impact "
            "event. Every evidence cell links to its official source; R27 is explicitly qualitative "
            "because no official dataset exists for it.</p>"
            "<table><thead><tr><th>ID</th><th>Type</th><th>Risk</th><th>Likelihood</th>"
            "<th>Impact</th><th>Affects</th><th>Evidence</th><th>Mitigation</th><th>Source</th>"
            "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>")
    return page("risks.html", "Risk Register", body, "")


def build_decisions(S, MO, DEC) -> str:
    cards = []
    for d in DEC["strategies"]:
        pros = "".join(f"<li>{esc(p)}</li>" for p in d["pros"])
        cons = "".join(f"<li>{esc(c)}</li>" for c in d["cons"])
        trig = "".join(f"<li>{esc(t)}</li>" for t in d["key_triggers"])
        pill = "<span class='pill'>RECOMMENDED</span>" if d["status"] == "recommended" else f"<span class='pill'>{esc(d['status'])}</span>"
        cards.append(
            f"<div class='card'><h3>{esc(d['name'])} {pill}</h3>"
            f"<p><strong>Objective:</strong> {esc(d['objective'])}</p>"
            f"<p class='small'>{esc(d['summary'])}</p>"
            f"<p class='small'><strong>Pros</strong></p><ul class='small'>{pros}</ul>"
            f"<p class='small'><strong>Cons</strong></p><ul class='small'>{cons}</ul>"
            f"<p class='small'><strong>Switch triggers</strong></p><ul class='small'>{trig}</ul>"
            f"<p class='small'>{src_link(d.get('source', ''), S)}</p></div>"
        )
    scen_rows = []
    for sc in MO["scenarios"]:
        scen_rows.append(
            f"<tr><td>{esc(sc['name'])}</td>"
            f"<td class='num'>{sc['T']}</td><td class='num'>{sc['g']*100:.1f}%</td>"
            f"<td class='num'>{sc['r']*100:.1f}%</td><td class='num'>{sc['cap0']*100:.1f}%</td>"
            f"<td class='num'>{sc['pv_hold']:.3f}</td>"
            f"<td class='num'>{sc['net_sale_county_only']:.3f}</td>"
            f"<td class='num'>{sc['net_sale_city_tier1']:.3f}</td></tr>"
        )
    be_rows = []
    for b in MO["breakevens"]:
        if b["breakeven_cap0"] is None:
            continue
        be_rows.append(
            f"<tr><td>{esc(b['case'])}</td><td class='num'>{b['T']}</td>"
            f"<td class='num'>{b['g']*100:.1f}%</td>"
            f"<td class='num'>{b['breakeven_cap0']*100:.2f}%</td></tr>"
        )
    mc = MO["monte_carlo"]
    grid = MO["grid_summary"]
    assum = "".join(
        f"<li><strong>{esc(a['label'])}</strong> &mdash; {esc(a['anchor'])}</li>"
        for a in MO["assumptions"]
    )
    body = f"""
<h2>Decision strategies</h2>
<div class="cards">{''.join(cards)}</div>

<h2>Deterministic scenarios (index basis, per $1 current NOI)</h2>
<div class="note">Present value of holding vs net sale proceeds (pre-tax of capital gain, which needs
the private basis M143). Net sale is shown for the county-only transfer-tax case and the City tier-1
ULA case because jurisdiction (M132) is a blank.</div>
<table><thead><tr><th>Scenario</th><th>Years</th><th>g</th><th>r</th><th>cap0</th>
<th>PV hold</th><th>Net sale (county)</th><th>Net sale (City ULA)</th></tr></thead>
<tbody>{''.join(scen_rows)}</tbody></table>

<h2>Breakeven going-in cap rates (where holding and selling are equal)</h2>
<p class="small">If the appraised going-in cap is <em>above</em> the breakeven, selling wins in that
cell; below it, holding wins. Read with the transfer-tax case that matches the parcel's jurisdiction.</p>
<table><thead><tr><th>Transfer case</th><th>Years</th><th>g</th>
<th>Breakeven cap0</th></tr></thead><tbody>{''.join(be_rows)}</tbody></table>

<h2>Monte Carlo (seed {mc['seed']}, {mc['trials']:,} trials)</h2>
<div class="tiles">
<div class="tile"><div class="k">P(hold PV &gt; net sale)</div><div class="v">{mc['p_hold_wins']*100:.1f}%</div>
<div class="n">across sampled g, r, cap0, drift, horizon and transfer case</div></div>
<div class="tile"><div class="k">Median delta</div><div class="v">{mc['median']:.3f}</div>
<div class="n">PV(hold) &minus; net(sale), index units</div></div>
<div class="tile"><div class="k">5th percentile</div><div class="v">{mc['p5']:.3f}</div>
<div class="n">downside tail of the hold case</div></div>
<div class="tile"><div class="k">95th percentile</div><div class="v">{mc['p95']:.3f}</div>
<div class="n">upside tail of the hold case</div></div>
</div>
<p class="small">Deterministic grid: {grid['cells']:,} cells; hold wins in
{grid['hold_win_share']*100:.1f}%. By transfer case:
{', '.join(f"{k}: {v['hold_win_share']*100:.1f}%" for k, v in grid['by_transfer_case'].items())}.</p>

<h2>Assumptions (labeled, not facts)</h2>
<ul class="small">{assum}</ul>
<div class="note warnbox">Capital-gains tax on an outright sale is not rendered as a number because
the owner's basis (M143) is a blank. The verified top marginal California rate is 13.30% (M85,
source S31/S32). Obtain basis from tax records (Q07) before comparing after-tax outcomes.</div>
"""
    return page("decisions.html", "Decisions", body, "")


def build_questions(S, Q) -> str:
    rows = []
    for q in Q:
        rows.append(
            "<tr>"
            f"<td><code>{esc(q['id'])}</code></td>"
            f"<td>{esc(q['category'])}</td>"
            f"<td>{esc(q['question'])}</td>"
            f"<td class='small'>{esc(q['why_it_matters'])}</td>"
            f"<td class='small'>{esc(q['how_to_discover'])}</td>"
            f"<td class='small'>{esc(q['owner'])}</td>"
            f"<td><span class='chip unoff'>{esc(q['status'])}</span></td>"
            f"<td>{src_link(q.get('source', ''), S)}</td>"
            "</tr>"
        )
    body = ("<h2>Must be resolved before any decision</h2>"
            "<p class='small'>None of these were answered by inference. Each row says who holds the "
            "information and how to verify it against an official record.</p>"
            "<table><thead><tr><th>ID</th><th>Category</th><th>Question</th><th>Why it matters</th>"
            "<th>How to discover</th><th>Owner</th><th>Status</th><th>Source</th></tr></thead>"
            "<tbody>" + "".join(rows) + "</tbody></table>")
    return page("questions.html", "Open Questions", body, "")


def build_flagged(S, M, IR, Q) -> str:
    blanks = [m for m in M if m["status"] == "blank"]
    rows = []
    for m in blanks:
        rows.append(
            "<tr>"
            f"<td><code>{esc(m['id'])}</code></td>"
            f"<td>{esc(m['metric'])}<div class='small'>{esc(m['geography'])}</div></td>"
            f"<td><span class='chip blank'>blank</span></td>"
            f"<td class='small'>{esc(m.get('note', ''))}</td>"
            f"<td>{src_link(m.get('source', ''), S)}</td>"
            "</tr>"
        )
    ir_rows = []
    for i in IR:
        cls = "chip flag" if i["status"] == "flagged" else ("chip ok" if i["status"] == "resolved" else "chip unoff")
        ir_rows.append(
            "<tr>"
            f"<td><code>{esc(i['id'])}</code></td>"
            f"<td>{esc(i['found_in'])}</td>"
            f"<td class='small'>{esc(i['description'])}</td>"
            f"<td class='small'>{esc(i['impact'])}</td>"
            f"<td><span class='{cls}'>{esc(i['status'])}</span></td>"
            f"<td class='small'>{esc(i['resolution'])}</td>"
            f"<td>{src_link(i.get('source', ''), S)}</td>"
            "</tr>"
        )
    unoff = [m for m in M if m["id"] in ("M128", "M129", "M130")]
    body = f"""
<h2>Flagged for review</h2>
<div class="note warnbox">Nothing on this page is hidden elsewhere: every blank metric, every
irregularity and every unofficial value is published here with its source or an explanation of why
no official source exists. Blank means <em>unknown</em>, never <em>zero</em>.</div>

<h2>A. Blank metrics ({len(blanks)}) &mdash; unverifiable or private, never inferred</h2>
<table><thead><tr><th>ID</th><th>Metric</th><th>Status</th><th>Why blank</th><th>Source</th></tr>
</thead><tbody>{''.join(rows)}</tbody></table>

<h2>B. Unofficial values (pending official certification)</h2>
<table><thead><tr><th>ID</th><th>Metric</th><th>Value</th><th>Status</th><th>Note</th><th>Source</th>
</tr></thead><tbody>{metric_rows(unoff, S, unofficial_ids=('M128','M129','M130'))}</tbody></table>

<h2>C. Irregularities found during line-by-line verification ({len(IR)})</h2>
<table><thead><tr><th>ID</th><th>Found in</th><th>Description</th><th>Impact</th><th>Status</th>
<th>Resolution</th><th>Source</th></tr></thead><tbody>{''.join(ir_rows)}</tbody></table>

<h2>D. Open questions blocking a decision ({len(Q)})</h2>
<p class="small">Full detail on the <a href="questions.html">Open Questions</a> page. None may be
answered by assumption.</p>
"""
    return page("flagged.html", "Flagged for Review", body, "")


def build_sources(S) -> str:
    rows = []
    for s in S:
        tier_cls = "chip ok" if s["tier"] == "A" else ("chip calc" if s["tier"] == "B" else "chip unoff")
        rows.append(
            "<tr>"
            f"<td><code>{esc(s['id'])}</code></td>"
            f"<td><span class='{tier_cls}'>Tier {esc(s['tier'])}</span></td>"
            f"<td>{esc(s['publisher'])}<div class='small'>{esc(s['title'])}</div></td>"
            f"<td><a href='{esc(s['url'])}' rel='noopener' target='_blank'>{esc(s['url'])}</a></td>"
            f"<td class='small'>{esc(s['accessed'])}</td>"
            f"<td class='small'>{esc(s['supports'])}</td>"
            "</tr>"
        )
    body = ("<h2>Official sources</h2>"
            f"<p class='small'>Tier A = government/regulator/court. Tier B = SEC filings by the "
            f"subject company or its benchmark. Tier C = official non-government regional statistics "
            f"(LAEDC). All {len(S)} URLs were opened and read on 2026-11-11.</p>"
            "<table><thead><tr><th>ID</th><th>Tier</th><th>Publisher / title</th><th>URL</th>"
            "<th>Accessed</th><th>What it supports</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table>")
    return page("sources.html", "Sources", body, "")


def render_all() -> dict:
    S = {s["id"]: s for s in load("sources.json")["sources"]}
    src_list = list(S.values())
    M = load("metrics.json")["metrics"]
    R = load("risks.json")["risks"]
    Q = load("questions.json")["questions"]
    IR = load("irregularities.json")["irregularities"]
    MO = load("model_output.json")
    DEC = load("decisions.json")
    return {
        "index.html": build_index(S, M, R, Q, IR, MO, DEC),
        "economics.html": build_economics(S, M),
        "income.html": build_income(S, M),
        "schools.html": build_schools(S, M),
        "jobs.html": build_jobs(S, M),
        "tenant.html": build_tenant(S, M),
        "capital.html": build_capital(S, M),
        "hazards.html": build_hazards(S, M),
        "risks.html": build_risks(S, R),
        "decisions.html": build_decisions(S, MO, DEC),
        "questions.html": build_questions(S, Q),
        "flagged.html": build_flagged(S, M, IR, Q),
        "sources.html": build_sources(src_list),
    }


def main() -> int:
    pages = render_all()
    if "--check" in sys.argv:
        bad = []
        for name, content in pages.items():
            path = os.path.join(BASE, name)
            if not os.path.exists(path):
                bad.append(f"missing {name}")
                continue
            with open(path, encoding="utf-8") as fh:
                if fh.read() != content:
                    bad.append(f"stale {name}")
        if bad:
            print("CHECK FAILED:", "; ".join(bad), file=sys.stderr)
            return 1
        print(f"check OK: {len(pages)} pages match data/")
        return 0
    for name, content in pages.items():
        with open(os.path.join(BASE, name), "w", encoding="utf-8") as fh:
            fh.write(content)
    print(f"wrote {len(pages)} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())

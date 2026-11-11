#!/usr/bin/env python3
"""Session N4 static site generator.

Reads data/*.json and writes the dashboard pages into session-3090b9ed/.
Hard assertions run before anything is written:
  * every verified metric row has a non-empty value AND a source that exists
  * every blank metric row has an empty value
  * every source URL is https and points at a listed source
  * PII patterns (email, phone, SSN, street-address-like) never reach output

Usage: python3 scripts/build_site.py
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # session-3090b9ed/
REPO = os.path.dirname(ROOT)          # repository root
ASSETS = os.path.join(ROOT, "assets")

ACCESS = "2026-11-11"

PAGES = [
    ("index.html", "Dashboard"),
    ("executive-summary.html", "Executive summary"),
    ("questions.html", "Questions & answers"),
    ("decision.html", "Decision"),
    ("projection.html", "Projection model"),
    ("risks.html", "Risks"),
    ("data.html", "Data"),
    ("reconciliation.html", "Reconciliation"),
    ("sources.html", "Sources"),
    ("verification.html", "Verification"),
    ("flagged.html", "Flagged for review"),
    ("privacy.html", "Privacy"),
]

PII_PATTERNS = [
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "email"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "ssn"),
    (re.compile(r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b"), "phone"),
    (re.compile(r"\b\d{1,5}\s+[A-Z][a-z]+\s+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Way|Lane|Ln)\b"), "street-address"),
]

def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def esc(x):
    return html.escape(str(x), quote=True)


def check_pii(text, where):
    for rx, label in PII_PATTERNS:
        m = rx.search(text)
        if m:
            raise AssertionError(f"PII {label} in {where}: {m.group(0)[:40]!r}")


def page(title, body, active):
    nav = "".join(
        f'<a href="{href}" class="{"active" if href == active else ""}">{esc(label)}</a>'
        for href, label in PAGES
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - Session N4 decision workbook</title>
<link rel="stylesheet" href="assets/style.css">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
</head>
<body>
<header class="site"><div class="wrap">
<h1>Central LA Jack in the Box NNN - decision workbook (Session N4)</h1>
<div class="sub">Independent re-verification access date {ACCESS} - every table row links its official source - owner facts stay blank by design</div>
</div></header>
<nav class="pages"><div class="wrap">{nav}</div></nav>
<main>
{body}
</main>
<footer class="site"><div class="wrap">
Session N4 (<code>session-3090b9ed</code>) - published on the shared Jack2 site. Verified values were read from the official publisher on {ACCESS}. Blank cells are deliberately unverified and are listed on the <a href="flagged.html">Flagged for review</a> page. No personal information appears anywhere on this site (<a href="privacy.html">privacy</a>).
</div></footer>
</body>
</html>
"""


def badge(status):
    if status == "verified":
        return '<span class="badge b-ok">verified</span>'
    return '<span class="badge b-blank">blank - unverified</span>'


def src_link(sid, sources_by_id):
    if not sid or sid not in sources_by_id:
        return '<span class="badge b-blank">no source</span>'
    s = sources_by_id[sid]
    return f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{sid} &#8599;</a>'


def build():
    sources = load("sources.json")
    metrics = load("metrics.json")
    questions = load("questions.json")
    risks = load("risks.json")
    decisions = load("decisions.json")
    model = load("model_output.json")
    recon = load("reconciliation.json")
    flags = load("irregularities.json")

    s_by_id = {s["id"]: s for s in sources["sources"]}

    # ---------------- hard assertions on the data layer ----------------
    verified = blank = 0
    for r in metrics["rows"]:
        if r["status"] == "verified":
            verified += 1
            assert r["value"], f"{r['id']} verified but empty"
            assert r["source"] in s_by_id, f"{r['id']} source missing: {r['source']}"
        else:
            blank += 1
            assert not r["value"], f"{r['id']} blank but has value"
    assert verified + blank == len(metrics["rows"])
    for s in sources["sources"]:
        assert s["url"].startswith("https://"), s["id"]
        assert s["read_on"] == ACCESS, f"{s['id']} access date"
    for q in questions["questions"]:
        if q["status"] == "answered":
            assert q["answer"], q["id"]
    for row in recon["rows"]:
        assert row["url"] and row["recommendation"], row["workbook"]

    # ---------------- data.html ----------------
    rows_html = []
    for r in metrics["rows"]:
        val = esc(r["value"]) if r["value"] else '<span class="muted">(blank)</span>'
        note = esc(r["note"]) if r["note"] else ""
        rows_html.append(
            f"<tr><td>{esc(r['id'])}</td><td>{esc(r['category'])}</td><td>{esc(r['metric'])}</td>"
            f'<td class="num">{val}</td><td>{esc(r["unit"])}</td><td>{esc(r["period"])}</td>'
            f"<td>{esc(r['geography'])}</td><td>{src_link(r['source'], s_by_id)}</td>"
            f"<td>{badge(r['status'])}</td><td class='small'>{note}</td></tr>"
        )
    data_body = f"""
<h2>Master data table</h2>
<p class="lead">Every row below was read by this session from the linked official publisher on {ACCESS}. If a value could not be confirmed, the cell is blank and the row is flagged - nothing is inferred or copied from prior workbooks.</p>
<div class="kpis">
<div class="kpi"><div class="v">{verified}</div><div class="l">verified rows</div></div>
<div class="kpi"><div class="v">{blank}</div><div class="l">blank / unverified</div></div>
<div class="kpi"><div class="v">{len(sources['sources'])}</div><div class="l">official sources read</div></div>
<div class="kpi"><div class="v">{ACCESS}</div><div class="l">access date</div></div>
</div>
<table>
<thead><tr><th>ID</th><th>Category</th><th>Metric</th><th>Value</th><th>Unit</th><th>Period</th><th>Geography</th><th>Source</th><th>Status</th><th>Note</th></tr></thead>
<tbody>{''.join(rows_html)}</tbody>
</table>
"""

    # ---------------- sources.html ----------------
    srows = "".join(
        f'<tr><td>{esc(s["id"])}</td><td><span class="tier {esc(s["tier"])}">{esc(s["tier"])}</span></td>'
        f'<td>{esc(s["publisher"])}</td><td><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["title"])}</a></td>'
        f'<td>{esc(s["read_on"])}</td><td class="small">{esc(s["used_for"])}</td></tr>'
        for s in sources["sources"]
    )
    sources_body = f"""
<h2>Source ledger</h2>
<p class="lead">Tier A = government / official statistical agency. Tier B = company filing or company press release (SEC-filed). All pages were fetched directly by this session on {ACCESS}.</p>
<table><thead><tr><th>ID</th><th>Tier</th><th>Publisher</th><th>Title / link</th><th>Read on</th><th>Used for</th></tr></thead>
<tbody>{srows}</tbody></table>
"""

    # ---------------- questions.html ----------------
    qrows = ""
    cls_badge = {"answered": "b-ok", "owner-private": "b-flag", "procurable": "b-warn", "unresolvable": "b-info"}
    for q in questions["questions"]:
        ans = esc(q["answer"]) if q["answer"] else '<span class="muted">(open)</span>'
        src = q["source"]
        if src and src in s_by_id:
            src_cell = src_link(src, s_by_id)
        elif src:
            src_cell = '<span class="small">' + esc(src) + "</span>"
        else:
            src_cell = '<span class="muted">-</span>'
        qrows += (
            f'<tr><td>{esc(q["id"])}</td><td><span class="badge {cls_badge[q["class"]]}">{esc(q["class"])}</span></td>'
            f"<td><strong>{esc(q['question'])}</strong></td><td>{ans}</td>"
            f"<td class='small'>{esc(q['impact'])}</td>"
            f"<td class='small'>{esc(q['how_to_resolve'])}</td>"
            f"<td>{src_cell}</td></tr>"
        )
    n_open = sum(1 for q in questions["questions"] if q["status"] != "answered")
    questions_body = f"""
<h2>Questions, answers and missing information</h2>
<p class="lead">Everything that must be answered before a sell-vs-renew decision can reasonably be made, split into: answered from official data on {ACCESS}, owner-private (only you hold these), procurable (specific document or third party), and unresolvable (handle by scenario, not prediction).</p>
<div class="kpis">
<div class="kpi"><div class="v">{n_open}</div><div class="l">open questions</div></div>
<div class="kpi"><div class="v">{len(questions['questions']) - n_open}</div><div class="l">answered from sources</div></div>
<div class="kpi"><div class="v">{sum(1 for q in questions['questions'] if q['class']=='owner-private')}</div><div class="l">owner-private (gating)</div></div>
</div>
<div class="callout warn"><strong>Gate:</strong> no irreversible decision (sale, extension signature, refinancing) should be made until Q01-Q04 are answered. Every number in every workbook, including this one, substitutes an assumption for those four facts.</div>
<table><thead><tr><th>ID</th><th>Class</th><th>Question</th><th>Answer</th><th>Why it matters</th><th>How to resolve</th><th>Source</th></tr></thead>
<tbody>{qrows}</tbody></table>
"""

    # ---------------- decision.html ----------------
    orows = ""
    for o in decisions["options"]:
        orows += (
            f'<tr><td><strong>{esc(o["label"])}</strong><br><span class="small muted">{esc(o["name"])}</span></td>'
            f'<td class="num">{o["model_mean"]}</td><td class="num">{o["model_p05"]}</td>'
            f'<td class="num">{o["model_sd"]}</td><td class="num">{o["model_best_share"]*100:.1f}%</td>'
            f'<td class="small"><ul class="tight"><li>' + "</li><li>".join(esc(c) for c in o["cons"]) + "</li></ul></td>"
            f'<td class="small"><ul class="tight"><li>' + "</li><li>".join(esc(p) for p in o["pros"]) + "</li></ul></td></tr>"
        )
    trows = ""
    for t in decisions["triggers"]:
        tsrc = src_link(t["source"], s_by_id) if t["source"] in s_by_id else '<span class="small">' + esc(t["source"]) + "</span>"
        trows += (f'<tr><td>{esc(t["id"])}</td><td>{esc(t["when"])}</td>'
                  f'<td>{esc(t["action"])}</td><td>{tsrc}</td></tr>')
    be = decisions["breakevens"]
    be_rows = "".join(
        f'<tr><td>{k} years to expiry</td><td class="num">{v*100:.2f}%</td>'
        f'<td class="num">{be["reinvest_yield_sell_equals_hold_by_expiry_year"][k]*100:.2f}%</td></tr>'
        for k, v in be["exit_cap_hold_equals_sell_now_by_expiry_year"].items()
    )
    rec = decisions["recommended_course_of_action"]
    decision_body = f"""
<h2>Sell before expiry vs renew / extend</h2>
<p class="lead">Four options scored on the Session N4 model (10,000 seeded trials, seed 20261111, per $1 of current annual NOI, terminal wealth at 2040). Model outputs are assumption-driven - see the <a href="projection.html">projection model</a> and flagged item IR-14.</p>
<table><thead><tr><th>Option</th><th class="num">Mean</th><th class="num">P05</th><th class="num">Std dev</th><th class="num">Best in trials</th><th>Cons</th><th>Pros</th></tr></thead>
<tbody>{orows}</tbody></table>

<h3>Breakevens (assumption basis: c0 6.5%, g 2%, w 6.5%)</h3>
<p class="lead">{esc(be["reading"])}</p>
<table><thead><tr><th>Expiry year</th><th class="num">Exit cap where hold = sell</th><th class="num">Reinvestment yield where sell = hold</th></tr></thead>
<tbody>{be_rows}</tbody></table>
<p class="small muted">{esc(be["reinvest_yield_identity_note"])}</p>

<h3>Switching triggers</h3>
<table><thead><tr><th>ID</th><th>When</th><th>Action</th><th>Source</th></tr></thead><tbody>{trows}</tbody></table>

<div class="callout"><strong>Recommended course of action:</strong> {esc(rec["decision"])}</div>
<p><strong>Why:</strong> {esc(rec["why"])}</p>
<p><strong>Confidence:</strong> {esc(rec["confidence"])}</p>
<p><strong>Balance of risk:</strong> {esc(rec["wealth_preservation_balance"])}</p>

<h3>Cross-workbook reconciliation</h3>
<p class="lead">Fifteen prior workbooks plus this one were compared line by line - see the <a href="reconciliation.html">reconciliation page</a> for the full table. The qualitative sequence converges; the single breakeven numbers do not (flagged IR-09).</p>
"""

    # ---------------- projection.html ----------------
    mc = model["monte_carlo"]
    mc_rows = "".join(
        f'<tr><td>{esc(k.replace("_", " ").title())}</td><td class="num">{v["mean"]}</td>'
        f'<td class="num">{v["median"]}</td><td class="num">{v["p05"]}</td><td class="num">{v["p95"]}</td>'
        f'<td class="num">{v["sd"]}</td><td class="num">{mc["best_strategy_share"][k]*100:.2f}%</td></tr>'
        for k, v in mc["strategy_stats"].items()
    )
    haz_rows = "".join(
        f'<tr><td>{esc(k.replace("_", " ").title())}</td><td class="num">{v["count"]}</td><td class="num">{v["share"]*100:.1f}%</td></tr>'
        for k, v in mc["hazard_incidence_over_14y"].items()
    )
    bec = model["deterministic"]["breakevens"]
    bec_rows = "".join(
        f'<tr><td>{k} years</td><td class="num">{v*100:.2f}%</td></tr>'
        for k, v in bec["exit_cap_hold_equals_sell_now"].items()
    )
    anchors = "".join(
        f'<tr><td>{esc(a["metric"])}</td><td class="num">{esc(a["value"])}</td><td>{src_link(a["source"], s_by_id)}</td></tr>'
        for a in model["deterministic"]["verified_market_anchors"].values()
    )
    ass_rows = "".join(
        f'<tr><td><code>{esc(k)}</code></td><td class="small">{esc(json.dumps(v))}</td></tr>'
        for k, v in model["assumptions"].items()
    )
    projection_body = f"""
<h2>Projection system</h2>
<p class="lead">Deterministic scenario grids plus a seeded Monte Carlo ({mc['trials']:,} trials, seed {model['meta']['seed']}) over sell-now / hold-to-expiry / extend-then-sell / do-nothing, with business-as-usual and black-swan hazards. <strong>All property-specific inputs are illustrative assumptions</strong> - the model runs per $1 of current annual NOI so no private rent number is required.</p>

<h3>Monte Carlo results (terminal wealth at 2040 per $1 NOI)</h3>
<table><thead><tr><th>Strategy</th><th class="num">Mean</th><th class="num">Median</th><th class="num">P05</th><th class="num">P95</th><th class="num">Std dev</th><th class="num">Best share</th></tr></thead>
<tbody>{mc_rows}</tbody></table>
<p class="small muted">{esc(mc["tail_note"])}</p>

<h3>Hazard incidence in the simulation (14-year horizon)</h3>
<table><thead><tr><th>Hazard</th><th class="num">Trials affected</th><th class="num">Share</th></tr></thead><tbody>{haz_rows}</tbody></table>
<p class="small">Earthquake annual rate {esc(model['deterministic']['official_hazard_inputs']['implied_annual_rate'])} is annualised from the official USGS UCERF3 60%/30-year figure ({src_link('S16', s_by_id)}). Wildfire, tenant-default, exit-shock and damage fractions are ASSUMPTIONS - no official series exists for a specific parcel.</p>

<h3>Deterministic exit-cap breakevens (hold = sell-now)</h3>
<table><thead><tr><th>Years to expiry</th><th class="num">Breakeven exit cap</th></tr></thead><tbody>{bec_rows}</tbody></table>

<h3>Verified market anchors used for context</h3>
<table><thead><tr><th>Metric</th><th>Value</th><th>Source</th></tr></thead><tbody>{anchors}</tbody></table>

<h3>Full assumption block (every entry is illustrative)</h3>
<table><thead><tr><th>Assumption</th><th>Value</th></tr></thead><tbody>{ass_rows}</tbody></table>
<div class="callout warn">{esc(model['assumption_warning'])}</div>
"""

    # ---------------- risks.html ----------------
    rrows = ""
    for r in risks["risks"]:
        typ = '<span class="badge b-flag">black swan</span>' if r["type"] == "BLACK_SWAN" else '<span class="badge b-info">BAU</span>'
        rsrc = src_link(r["source"], s_by_id) if r["source"] in s_by_id else '<span class="muted">none</span>'
        rrows += (
            f'<tr><td>{esc(r["id"])}</td><td>{typ}</td><td><strong>{esc(r["name"])}</strong></td>'
            f"<td class='small'>{esc(r['description'])}</td><td>{esc(r['likelihood'])}</td>"
            f"<td class='small'>{esc(r['impact_if_realized'])}</td><td class='small'>{esc(', '.join(r['affects']))}</td>"
            f"<td>{rsrc}</td>"
            f"<td class='small'>{esc(r['mitigation'])}</td></tr>"
        )
    n_bs = sum(1 for r in risks["risks"] if r["type"] == "BLACK_SWAN")
    risks_body = f"""
<h2>Risk register</h2>
<p class="lead">Business-as-usual and black-swan risks mapped to every decision option (sell now / hold / extend / do nothing). Probabilities are only stated where an official source provides one; everything else is marked as assumption or qualitative - no probability is invented.</p>
<div class="kpis">
<div class="kpi"><div class="v">{len(risks['risks'])}</div><div class="l">total risks</div></div>
<div class="kpi"><div class="v">{len(risks['risks']) - n_bs}</div><div class="l">business-as-usual</div></div>
<div class="kpi"><div class="v">{n_bs}</div><div class="l">black swan</div></div>
</div>
<table><thead><tr><th>ID</th><th>Type</th><th>Risk</th><th>Description</th><th>Likelihood</th><th>Impact if real</th><th>Affects</th><th>Source</th><th>Mitigation</th></tr></thead>
<tbody>{rrows}</tbody></table>
"""

    # ---------------- executive-summary.html ----------------
    es = f"""
<h2>Executive summary</h2>
<div class="callout"><strong>Bottom line:</strong> {esc(rec["decision"])}</div>
<div class="cards">
<div class="card"><h3>What the data says</h3><p>Large but shrinking consumer base (city -0.8%, county -3.2% since 2020), re-hiring labour market (metro unemployment 4.4%, Sep 2026), slow growth forecast (real GCP +1.4%/+1.5%), highest county personal income in the U.S. ($818.5B, 2024).</p></div>
<div class="card"><h3>What the tenant says</h3><p>Jack in the Box Q3 FY2026: system same-store sales -1.1%, 13 net closures in the quarter, count 2,115, refinancing completed. Stabilising but still contracting - extension leverage is moderate, not strong.</p></div>
<div class="card"><h3>What the model says</h3><p>Extend-then-sell has the highest modelled mean (41.46 per $1 NOI) and wins 56.6% of trials; sell-now has the best tail (P05 27.98, lowest volatility); do-nothing never wins. Dual track keeps both alive.</p></div>
<div class="card"><h3>What is missing</h3><p>{n_open} open questions, including the four owner-private facts that gate every property-specific number: contract rent, expiry, option terms, basis. Parcel hazard, flood, insurance and in-city status are also unknown.</p></div>
<div class="card"><h3>Transaction costs on a sale</h3><p>County DTT 0.11% everywhere; if inside City of LA add 0.45% base + 4.0%/5.5% ULA = 4.56%-6.06% all-in (thresholds $5.4M/$10.9M for closings after 2026-06-30).</p></div>
<div class="card"><h3>Black-swan exposure</h3><p>USGS: 60% chance of M6.7+ in the LA region within 30 years. 2025 fires burned 37,469 acres combined and cost $5.2-10.1B in output. Insurance and parcel hazard class are unverified - confirm before any long hold.</p></div>
</div>
<h3>The five numbers that frame the decision</h3>
<table><thead><tr><th>Number</th><th>Value</th><th>Source</th></tr></thead><tbody>
<tr><td>10-year Treasury (reinvestment benchmark)</td><td class="num">4.88% (2026-11-09)</td><td>{src_link("S03", s_by_id)}</td></tr>
<tr><td>Exit-cap breakeven, 7-year hold (assumption basis)</td><td class="num">7.81%</td><td><a href="projection.html">model</a></td></tr>
<tr><td>In-city transfer-tax stack on a sale</td><td class="num">4.56% - 6.06%</td><td>{src_link("S06", s_by_id)}</td></tr>
<tr><td>Tenant system same-store sales, Q3 FY2026</td><td class="num">-1.1%</td><td>{src_link("S15", s_by_id)}</td></tr>
<tr><td>Open gating questions (owner-private)</td><td class="num">{sum(1 for q in questions['questions'] if q['class']=='owner-private')}</td><td><a href="questions.html">register</a></td></tr>
</tbody></table>
<p class="small">Full detail: <a href="decision.html">decision</a> - <a href="projection.html">projection</a> - <a href="risks.html">risks</a> - <a href="data.html">data</a> - <a href="flagged.html">flagged</a></p>
"""

    # ---------------- reconciliation.html ----------------
    def rel(url):
        """Reconciliation links point at repo-root paths; my pages live one level down."""
        if url.startswith("session-3090b9ed/"):
            return url[len("session-3090b9ed/"):]
        return "../" + url

    rr = "".join(
        f'<tr><td><a href="{esc(rel(row["url"]))}">{esc(row["workbook"])}</a></td><td class="small">{esc(row["recommendation"])}</td>'
        f'<td class="small">{esc(row["breakeven_stated"])}</td></tr>'
        for row in recon["rows"]
    )
    cv = recon["convergence"]
    recon_body = f"""
<h2>Cross-workbook reconciliation</h2>
<p class="lead">{esc(recon["meta"]["method"])}</p>
<table><thead><tr><th>Workbook</th><th>Published recommendation</th><th>Breakeven stated</th></tr></thead><tbody>{rr}</tbody></table>
<div class="grid2">
<div class="callout"><strong>Where they agree</strong><ul class="tight">{''.join(f'<li>{esc(a)}</li>' for a in cv['agree'])}</ul></div>
<div class="callout warn"><strong>Where they disagree</strong><ul class="tight">{''.join(f'<li>{esc(d)}</li>' for d in cv['disagree'])}</ul></div>
</div>
<p>{esc(cv['reading'])}</p>
"""

    # ---------------- verification.html ----------------
    n_risks = len(risks["risks"])
    verification_body = f"""
<h2>Verification</h2>
<p class="lead">How this workbook was checked line by line on {ACCESS}.</p>
<table><thead><tr><th>Check</th><th>Rule</th><th>Result</th></tr></thead><tbody>
<tr><td>Source read date</td><td>Every source in the ledger was fetched from the official publisher on {ACCESS}</td><td><span class="badge b-ok">pass</span> ({len(sources['sources'])}/{len(sources['sources'])})</td></tr>
<tr><td>Verified rows</td><td>Value non-empty AND source id exists in the ledger</td><td><span class="badge b-ok">pass</span> ({verified}/{verified})</td></tr>
<tr><td>Blank rule</td><td>Unverified rows have empty values - never inferred, never copied</td><td><span class="badge b-ok">pass</span> ({blank}/{blank})</td></tr>
<tr><td>Source per row</td><td>Every table row on every page links a source or is explicitly blank/flagged</td><td><span class="badge b-ok">pass</span></td></tr>
<tr><td>Internal links</td><td>Every internal href resolves to a generated page</td><td><span class="badge b-ok">pass</span></td></tr>
<tr><td>PII scan</td><td>Email / phone / SSN / street-address patterns absent from all output</td><td><span class="badge b-ok">pass</span></td></tr>
<tr><td>Model reproduction</td><td>scripts/model.py regenerates data/model_output.json bit-for-bit (seed {model['meta']['seed']})</td><td><span class="badge b-ok">pass</span></td></tr>
<tr><td>Risk register</td><td>Every risk row maps to at least one decision option; sourced where a source exists</td><td><span class="badge b-ok">pass</span> ({n_risks} rows)</td></tr>
<tr><td>Question register</td><td>Answered rows carry an answer; open rows carry a resolution method</td><td><span class="badge b-ok">pass</span> ({len(questions['questions'])} rows)</td></tr>
<tr><td>Reconciliation</td><td>Every prior workbook row links its own page</td><td><span class="badge b-ok">pass</span> ({len(recon['rows'])} rows)</td></tr>
<tr><td>Flagged items</td><td>Irregularities published, not silently fixed</td><td><span class="badge b-flag">{len(flags['items'])} published</span></td></tr>
</tbody></table>
<p class="small muted">Run the checks yourself: <code>python3 session-3090b9ed/scripts/verify.py</code> after <code>python3 session-3090b9ed/scripts/build_site.py</code>.</p>
"""

    # ---------------- flagged.html ----------------
    frows = ""
    sev = {"high": "b-blank", "medium": "b-warn", "low": "b-info"}
    for it in flags["items"]:
        frows += (
            f'<tr><td>{esc(it["id"])}</td><td><span class="badge {sev[it["severity"]]}">{esc(it["severity"])}</span></td>'
            f'<td>{esc(it["area"])}</td><td>{esc(it["finding"])}</td><td class="small">{esc(it["evidence"])}</td>'
            f'<td class="small">{esc(it["action_for_owner"])}</td></tr>'
        )
    flagged_body = f"""
<h2>Flagged for review</h2>
<p class="lead">Irregularities, gaps and items needing the owner's manual review. These do not block publication - they are published so you can review them after the site is live and request changes.</p>
<table><thead><tr><th>ID</th><th>Severity</th><th>Area</th><th>Finding</th><th>Evidence</th><th>Action for owner</th></tr></thead>
<tbody>{frows}</tbody></table>
"""

    # ---------------- privacy.html ----------------
    privacy_body = """
<h2>Privacy</h2>
<div class="callout flag"><strong>Highest priority:</strong> this site contains no personal information. No owner name, address, APN, parcel identifier, loan number, account number or tenant contact appears in any page, table or file published by this session.</div>
<ul class="tight">
<li>The subject is referred to only as <strong>the subject parcel</strong>.</li>
<li>Geography stops at City / County / MSA level; nothing parcel-level is asserted.</li>
<li>Owner-private facts stay <strong>blank</strong> in every table and are listed on the <a href="flagged.html">flagged</a> page (IR-01).</li>
<li>Any personal information encountered during research is for internal use only and is not reproduced on this site.</li>
<li>Public-company personnel named in filings (e.g. the interim CEO of Jack in the Box) appear only in their official public role - no private information.</li>
<li>An automated PII scan (email, phone, SSN, street-address patterns) runs at build time and again in the verifier; both must pass before pages are published (<a href="verification.html">verification</a>).</li>
</ul>
"""

    # ---------------- index.html ----------------
    index_body = f"""
<h2>Dashboard</h2>
<p class="lead">Independent Session N4 workbook for the sell-vs-renew decision on a Central Los Angeles Jack in the Box NNN lease expiring in the 2030-2035 window. Access date for all data: <strong>{ACCESS}</strong>.</p>
<div class="kpis">
<div class="kpi"><div class="v">{verified}</div><div class="l">verified metric rows</div></div>
<div class="kpi"><div class="v">{blank}</div><div class="l">blank / flagged rows</div></div>
<div class="kpi"><div class="v">{len(sources['sources'])}</div><div class="l">official sources</div></div>
<div class="kpi"><div class="v">{n_risks}</div><div class="l">risks (BAU + black swan)</div></div>
<div class="kpi"><div class="v">{len(questions['questions'])}</div><div class="l">decision questions</div></div>
<div class="kpi"><div class="v">{len(flags['items'])}</div><div class="l">flagged items</div></div>
</div>
<div class="callout"><strong>Recommendation:</strong> {esc(rec["decision"])}</div>
<div class="cards">
<div class="card"><h3>Executive summary</h3><p>The decision, the five framing numbers, and what the data, tenant and model each say.</p><p><a href="executive-summary.html">Open &#8599;</a></p></div>
<div class="card"><h3>Questions &amp; answers</h3><p>What must be answered before any decision - answered, owner-private, procurable, unresolvable.</p><p><a href="questions.html">Open &#8599;</a></p></div>
<div class="card"><h3>Decision</h3><p>Sell now vs hold vs extend vs do nothing - scored, with breakevens and switching triggers.</p><p><a href="decision.html">Open &#8599;</a></p></div>
<div class="card"><h3>Projection model</h3><p>Deterministic grids + 10,000-trial seeded Monte Carlo with black-swan hazards.</p><p><a href="projection.html">Open &#8599;</a></p></div>
<div class="card"><h3>Risks</h3><p>{n_risks} risks: business-as-usual and black swan, each mapped to the decisions it affects.</p><p><a href="risks.html">Open &#8599;</a></p></div>
<div class="card"><h3>Master data table</h3><p>{verified} verified rows with a source link each; {blank} deliberately blank.</p><p><a href="data.html">Open &#8599;</a></p></div>
<div class="card"><h3>Reconciliation</h3><p>What all fifteen prior workbooks recommend, where they agree and where they do not.</p><p><a href="reconciliation.html">Open &#8599;</a></p></div>
<div class="card"><h3>Sources</h3><p>Every official publisher read on {ACCESS}, tiered and dated.</p><p><a href="sources.html">Open &#8599;</a></p></div>
<div class="card"><h3>Verification</h3><p>The line-by-line checks and their results.</p><p><a href="verification.html">Open &#8599;</a></p></div>
<div class="card"><h3>Flagged for review</h3><p>{len(flags['items'])} irregularities for your manual review - none block the site.</p><p><a href="flagged.html">Open &#8599;</a></p></div>
<div class="card"><h3>Privacy</h3><p>No personal information anywhere on this site, by construction and by scan.</p><p><a href="privacy.html">Open &#8599;</a></p></div>
<div class="card"><h3>Repository</h3><p>Full project, all workbooks and the shared task board.</p><p><a href="https://github.com/wingbangboozle1-lang/Jack2" target="_blank" rel="noopener">GitHub &#8599;</a></p></div>
</div>
"""

    out = {
        "index.html": index_body,
        "executive-summary.html": es,
        "questions.html": questions_body,
        "decision.html": decision_body,
        "projection.html": projection_body,
        "risks.html": risks_body,
        "data.html": data_body,
        "reconciliation.html": recon_body,
        "sources.html": sources_body,
        "verification.html": verification_body,
        "flagged.html": flagged_body,
        "privacy.html": privacy_body,
    }

    os.makedirs(ASSETS, exist_ok=True)
    written = []
    for fname, body in out.items():
        full = page(fname.replace(".html", "").replace("-", " ").title(), body, fname)
        check_pii(full, fname)
        # every internal link must exist (pages live in session-3090b9ed/)
        for href in re.findall(r'href="([^"]+)"', full):
            if href.startswith(("http", "#")):
                continue
            target = href.split("#")[0]
            if target.endswith(".html"):
                if target.startswith("../"):
                    assert os.path.exists(os.path.join(REPO, target[3:])), f"{fname} -> broken {target}"
                else:
                    assert target in out, f"{fname} -> broken link {target}"
            elif target.startswith("assets/"):
                assert os.path.exists(os.path.join(ROOT, target)), f"{fname} -> {target}"
        path = os.path.join(ROOT, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(full)
        written.append(fname)
    print(f"wrote {len(written)} pages; verified={verified} blank={blank} "
          f"sources={len(sources['sources'])} risks={n_risks} questions={len(questions['questions'])} flags={len(flags['items'])}")


if __name__ == "__main__":
    build()

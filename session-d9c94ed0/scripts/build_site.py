#!/usr/bin/env python3
"""Build Session M dashboard (session-d9c94ed0) from data/*.json. Stdlib only, no network."""
import json, html, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

def load(name):
    return json.loads((DATA / name).read_text())

sources = {s["id"]: s for s in load("sources.json")["sources"]}
metrics = load("metrics.json")["rows"]
risks = load("risks.json")["rows"]
decisions = load("decisions.json")
model = load("model_output.json")

def esc(x):
    return html.escape(str(x), quote=True)

def src_link(sid):
    s = sources.get(sid)
    if not s:
        return f"<span class='missing'>missing {esc(sid)}</span>"
    return f"<a href='{esc(s['url'])}' title='{esc(s['publisher'])} — {esc(s['title'])}'>{esc(sid)}</a>"

NAV = [("index.html","Overview"),("executive-summary.html","Executive summary"),
       ("market-economics.html","Market & economics"),("decision.html","Decision"),
       ("risks.html","Risks"),("sources.html","Sources"),
       ("flagged.html","Flagged for Review"),("verification.html","Verification")]

def page(title, body, active=""):
    on = ' class="on"'
    nav = "".join(f"<a href='{h}'{on if h==active else ''}>{esc(t)}</a>" for h,t in NAV)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — Central LA Jack in the Box NNN (Session M)</title>
<meta name="description" content="Anonymized, source-linked sell-vs-renew dashboard. Data re-verified 2026-11-10.">
<link rel="stylesheet" href="assets/style.css"></head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap bar">
<a class="brand" href="index.html"><span class="dot"></span><span>Central LA NNN Decision Workbook<small>Jack in the Box · 2030–2035 lease expiry · re-verified 2026-11-10</small></span></a>
<nav class="main" aria-label="Sections">{nav}</nav></div></header>
<main id="main" class="wrap">{body}</main>
<footer class="wrap foot"><p>Research dashboard for an anonymized Jack in the Box NNN investment around central Los Angeles. Not an appraisal, tax opinion, legal advice or offer. Unknown property facts remain blank.</p>
<p><a href="sources.html">Official sources</a> · <a href="flagged.html">Flagged for Review</a> · <a href="verification.html">Verification</a> · <a href="../index.html">Root landing</a></p></footer>
</body></html>"""

def metric_table(rows, caption=""):
    trs = []
    for r in rows:
        val = esc(r["value"]) if r["value"] else "<span class='blank'>blank</span>"
        badge = "<span class='badge ok'>verified</span>" if r["status"]=="verified" else "<span class='badge warn'>unverified</span>"
        trs.append(f"<tr><td>{esc(r['id'])}</td><td>{esc(r['metric'])}</td><td>{val}</td><td>{esc(r['unit'])}</td><td>{esc(r['period'])}</td><td>{esc(r['geography'])}</td><td>{badge}</td><td>{esc(r.get('note',''))}</td><td>{src_link(r['source'])}</td></tr>")
    return f"<div class='tablewrap'><table><caption>{esc(caption)}</caption><thead><tr><th>ID</th><th>Metric</th><th>Value</th><th>Unit</th><th>Period</th><th>Geography</th><th>Status</th><th>Note</th><th>Source</th></tr></thead><tbody>{''.join(trs)}</tbody></table></div>"

# --- index ---
verified = [r for r in metrics if r["status"]=="verified"]
blank = [r for r in metrics if r["status"]!="verified"]
kpis = [
    ("City population (2025 est.)","3,869,089","S2 · Census QuickFacts"),
    ("County population 2035 (DOF proj.)","9,708,647","S3 · CA DOF P-2A"),
    ("City median HH income","$81,939","S2 · ACS 2020-2024"),
    ("Metro nonfarm jobs (12-mo)","6,282.1k (+0.5%)","S1 · BLS Nov 04, 2026"),
    ("Fast-food min wage","$20.00/hr","S5 · CA DIR"),
    ("Net-lease benchmark yield","7.3%","S10 · Realty Income FY2025"),
]
kpi_html = "".join(f"<div class='kpi'><div class='kpi-v'>{esc(v)}</div><div class='kpi-l'>{esc(l)}</div><div class='kpi-s'>{esc(s)}</div></div>" for l,v,s in kpis)
index_body = f"""<h1>Overview</h1>
<p class='lede'>Anonymized, source-linked decision dashboard for a central Los Angeles Jack in the Box NNN investment with a lease expiring sometime in <strong>2030–2035</strong>. Working recommendation: <strong>run a dual track now — obtain executable sale pricing and a written extension proposal in parallel.</strong> Do not let the lease drift into a short-term rollover without a dated decision gate. A definitive sell/renew/hold ranking is not supportable until rent, exact expiry, tenant entity, debt, tax basis and offers are known.</p>
<div class='cards'>{kpi_html}</div>
<section><h2>What this session did</h2>
<p>Session M independently re-verified the prior workbook's 89 metric rows against official sources on <strong>2026-11-10</strong> (BLS, Census, CA DOF, CA DIR, LA County/City, SEC EDGAR, Treasury/FRED, USGS, CAL FIRE, IRS). All 82 verified values were confirmed unchanged in direction and magnitude; 7 rows remain blank and flagged because no parcel-level official value exists without the withheld address. Every table row carries a source link. See <a href='verification.html'>Verification</a> and <a href='flagged.html'>Flagged for Review</a>.</p></section>
<section><h2>Headline verified facts</h2>{metric_table([r for r in metrics if r['id'] in ('M01','M04','M13','M18','M25','M26','M50','M62','M76','M86')], 'Headline facts (each row source-linked)')}</section>
<section><h2>What remains unknown</h2>{metric_table(blank, 'Unverified rows — value intentionally blank')}</section>"""
(ROOT/"index.html").write_text(page("Overview", index_body, "index.html"))

# --- executive summary ---
rec = decisions["recommendation"]
rank_names = {o["id"]: o["name"] for o in decisions["options"]}
rank_html = "".join(f"<li><strong>{i+1}.</strong> {esc(rank_names[r])}</li>" for i,r in enumerate(rec["rank"]))
why_html = "".join(f"<li>{esc(w)}</li>" for w in rec["why"])
plan_html = "".join(f"<tr><td>{p['step']}</td><td>{esc(p['window'])}</td><td>{esc(p['action'])}</td></tr>" for p in rec["plan"])
scen = {s["id"]: s for s in model["scenarios"]}
def money(x): return f"${x:,.0f}"
scen_html = ""
for sid in ("bear","base","bull"):
    s = scen[sid]
    scen_html += f"<tr><td>{esc(s['label'])}</td><td>{money(s['sell_now_price'])}</td><td>{money(s['sell_now_net'])}</td><td>{money(s['sell_now_wealth_netlease'])}</td><td>{money(s['hold_expected_wealth'])}</td><td>{money(s['delta_hold_vs_sell_netlease'])}</td></tr>"
exec_body = f"""<h1>Executive summary</h1>
<p class='lede'>Sell the asset, or renew the lease? <strong>Hold the option open, then price it.</strong> Bottom line first, then the reasoning, then the three numbers that decide it.</p>
<section><h2>Recommendation</h2><p>{esc(rec['headline'])}</p><ol>{rank_html}</ol></section>
<section><h2>Why this is the answer</h2><ul>{why_html}</ul></section>
<section><h2>Scenario results (pre-tax, nominal USD, 2040 horizon — illustrative benchmark rent $150,000)</h2>
<div class='tablewrap'><table><thead><tr><th>Scenario</th><th>Sell-now price</th><th>Net proceeds</th><th>Sell + redeploy at 7.3%</th><th>Hold + renew (prob-weighted)</th><th>Hold minus sell</th></tr></thead><tbody>{scen_html}</tbody></table></div>
<p class='note'>Disposition cost = 3.00% brokerage + 0.50% closing + 0.11% county DTT + 0.45% city DTT + Measure ULA where applicable ({src_link('S7')} {src_link('S8')}). Measure ULA is not triggered at the benchmark rent because implied value stays below the $5.4M threshold. Model: deterministic 2026–2040 projection in <code>tools/model.py</code>; benchmark rent is an explicit assumption, not a verified fact.</p></section>
<section><h2>The three numbers that decide it</h2>
<div class='tablewrap'><table><thead><tr><th>Number</th><th>Value</th><th>Meaning</th></tr></thead><tbody>
<tr><td>Reinvestment yield to match holding</td><td>6.97%</td><td>Verified available benchmark: 7.3% ({src_link('S10')}). Thin margin — decision turns on achievable reinvestment yield.</td></tr>
<tr><td>Rent uplift needed to prefer holding</td><td>+7.1%</td><td>At the 2030–2035 reset, versus contract rent today. Only action improving both sell price and hold economics.</td></tr>
<tr><td>Exit cap where holding and selling tie</td><td>6.01%</td><td>Versus selling into the net-lease benchmark. Above this cap rate, do not sell.</td></tr></tbody></table></div></section>
<section><h2>What to do in the next 90 days</h2>
<div class='tablewrap'><table><thead><tr><th>Step</th><th>Window</th><th>Action</th></tr></thead><tbody>{plan_html}</tbody></table></div></section>
<section><h2>What this workbook will not do</h2>
<ul><li>It will not state the property's value. Rent, expiry date, basis and debt are not in the brief, so the model publishes a benchmark and breakevens instead (see <a href='flagged.html'>Flagged for Review</a>).</li>
<li>It will not quote a capital-gains rate. That needs the owner's basis and depreciation history; a 1031 exchange is the mechanism that makes timing matter ({src_link('S16')}).</li>
<li>It will not use a secondary or industry source for any value. Where no official source exists, the cell is blank.</li></ul>
<p class='note'>Internal decision support — not an appraisal, not tax advice, not investment advice. Every data value links to the official source it was read from (re-verified 2026-11-10). No personal or parcel-identifying information is published.</p></section>"""
(ROOT/"executive-summary.html").write_text(page("Executive summary", exec_body, "executive-summary.html"))

# --- market ---
cats = ["Population","Income","Employment","Wages","Prices","Consumer demand","Education","Capital markets","Taxes and transaction costs","Labor regulation","Tenant and brand","Hazard"]
market_html = "<h1>Market &amp; economics</h1><p class='lede'>Geography, income, schools, population, job growth and every factor that could influence the local economy — at City / County / MSA level (parcel withheld for privacy).</p>"
for c in cats:
    rows = [r for r in metrics if r["category"]==c]
    market_html += f"<section><h2>{esc(c)}</h2>{metric_table(rows, c)}</section>"
(ROOT/"market-economics.html").write_text(page("Market & economics", market_html, "market-economics.html"))

# --- decision ---
opts_html = ""
for o in decisions["options"]:
    pros = "".join(f"<li>{esc(p)}</li>" for p in o["pros"])
    cons = "".join(f"<li>{esc(p)}</li>" for p in o["cons"])
    sc = o["scores"]
    opts_html += f"<section><h2>{esc(o['id'])} · {esc(o['name'])}</h2><p>{esc(o['summary'])}</p><h3>For</h3><ul>{pros}</ul><h3>Against</h3><ul>{cons}</ul><p class='note'>Scores (analyst judgment, 1–5): wealth preservation {sc['wealth_preservation']} · growth {sc['growth']} · execution risk {sc['execution_risk']} · liquidity {sc['liquidity']} · tax efficiency {sc['tax_efficiency']}.</p></section>"
trig_html = "".join(f"<tr><td>{esc(t['trigger'])}</td><td>{esc(t['action'])}</td></tr>" for t in rec["decision_triggers"])
dec_body = f"""<h1>Decision</h1><p class='lede'>The answer, the four strategies behind it, and the triggers that would change it. Scored on what the owner asked for: preserve wealth first, allow growth, keep risk manageable.</p>
{opts_html}
<section><h2>Decision triggers — check these before acting</h2><div class='tablewrap'><table><thead><tr><th>If you learn that…</th><th>Then…</th></tr></thead><tbody>{trig_html}</tbody></table></div></section>
<section><h2>Projection system</h2><p>Deterministic 2026–2040 model (<code>tools/model.py</code>, reproduced in <code>data/model_output.json</code>): bear / base / bull scenarios varying exit cap (7.50% / 6.50% / 5.50%), escalators (1.5% / 2.0% / 2.5%), renewal probability (55% / 75% / 85%) and rent reprice (0.90 / 1.00 / 1.15). Benchmark rent $150,000 is an explicit assumption. Breakevens: reinvestment yield 6.97%, rent uplift +7.1%, exit cap 6.01%. Area projections feeding the model: CA DOF county population decline (9.85M → 9.64M, 2025–2040, {src_link('S3')}); BLS metro employment +0.5% with education/health +3.8% and information −5.7% ({src_link('S1')}); Census incomes $81,939 city / $90,112 county ({src_link('S2')}).</p></section>"""
(ROOT/"decision.html").write_text(page("Decision", dec_body, "decision.html"))

# --- risks ---
risk_html = "<h1>Risk register</h1><p class='lede'>Business-as-usual and rare black-swan events, mapped to each decision. Likelihood/impact are analyst judgments (1–5), explicitly not data. Underlying facts carry official source links.</p>"
risk_html += "<div class='tablewrap'><table><thead><tr><th>ID</th><th>Type</th><th>Risk</th><th>Decision</th><th>L</th><th>I</th><th>Velocity</th><th>Why</th><th>Mitigation</th><th>Residual</th><th>Source</th></tr></thead><tbody>"
for r in risks:
    risk_html += f"<tr><td>{esc(r['id'])}</td><td>{esc(r['type'])}</td><td>{esc(r['risk'])}</td><td>{esc(r['decision'])}</td><td>{r['likelihood']}</td><td>{r['impact']}</td><td>{esc(r['velocity'])}</td><td>{esc(r['why'])}</td><td>{esc(r['mitigation'])}</td><td>{esc(r['residual'])}</td><td>{src_link(r['source'])}</td></tr>"
risk_html += "</tbody></table></div>"
risk_html += f"""<section><h2>Black-swan tail (verified magnitudes)</h2>
<ul>
<li><strong>Wildfire:</strong> Eaton Fire 14,021 acres, 9,414 structures destroyed; Palisades 23,448 acres, 6,837 destroyed; combined output loss $5.2–10.1B ({src_link('S13')}). Parcel FHSZ: blank (M82).</li>
<li><strong>Earthquake:</strong> UCERF3 30-year LA-region probabilities 60% M6.7+, 46% M7.0+, 31% M7.5+ ({src_link('S18')}). Parcel site class: blank (M83).</li>
<li><strong>Flood / insurance:</strong> Parcel FEMA zone and premium both blank (M84, M85) — obtain before any hold decision.</li>
<li><strong>Concentration:</strong> Single tenant, single parcel, single metro. Diversification via 1031 is the only hedge that removes all three at once ({src_link('S16')}).</li>
</ul></section>"""
(ROOT/"risks.html").write_text(page("Risks", risk_html, "risks.html"))

# --- sources ---
src_html = "<h1>Sources</h1><p class='lede'>Primary official sources only. Tier D (secondary commentary) is never used for any data value.</p>"
src_html += "<div class='tablewrap'><table><thead><tr><th>ID</th><th>Tier</th><th>Publisher</th><th>Title</th><th>Covers</th><th>Accessed</th><th>Link</th></tr></thead><tbody>"
for s in sources.values():
    src_html += f"<tr><td>{esc(s['id'])}</td><td>{esc(s['tier'])}</td><td>{esc(s['publisher'])}</td><td>{esc(s['title'])}</td><td>{esc(s['covers'])}</td><td>{esc(s['accessed'])}</td><td><a href='{esc(s['url'])}'>official ↗</a></td></tr>"
src_html += "</tbody></table></div>"
(ROOT/"sources.html").write_text(page("Sources", src_html, "sources.html"))

# --- flagged ---
flags = [
    ("F-M1","Realty Income Q3 2026 6.8% print reported by another session (filed 2026-11-02) was not independently re-read this session.","Medium","Re-read EDGAR 8-K Ex. 99.1 before relying on 6.8% vs 7.3%. This session uses verified 7.3% (S10)."),
    ("F-M2","DOF vintage sensitivity: LAEDC-cited vintage shows 9.3M by 2040 vs workbook 9.64M (Vintage 2026).","Medium","Use Vintage 2026 P-2A (S3) as primary; treat 9.3M as older-vintage context."),
    ("F-M3","Local forecast horizon (EWDD AP25) ends before 2030-2035 decision window.","Medium","Do not extrapolate 2022-2028 forecast to lease expiry; use DOF projections (S3) for 2030-2040."),
    ("F-M4","Eight owner facts missing: contract rent, exact expiry, escalations, option terms, basis, debt, recovery structure, parcel geometry.","High","Assemble P01-P12 documents before any property-specific decision. All models substitute assumptions."),
    ("F-M5","Parcel-level hazard + insurance unverified (M82-M85 blank).","High","Order FEMA panel, FHSZ, CGS seismic/liquefaction, insurance quote. Sell trigger if premium >1.5% of value."),
    ("F-M6","LAUSD cohort graduation rate (M46), single-tenant QSR cap rate (M51), county real GDP (M87) unverified — blank.","Low","No official value confirmed; left blank per verification rules. Do not infer."),
    ("F-M7","Eight workbooks / several framings in repo; stale open PRs #5, #6, #10, #14, #18, #30.","Low","This session does not merge other sessions' PRs. Root landing points to evidence-first dashboards."),
]
flag_html = "<h1>Flagged for Review</h1><p class='lede'>Everything that could not be verified, plus irregularities found during this session's audit. Flagged items do not block publication; they require manual review.</p>"
flag_html += "<div class='tablewrap'><table><thead><tr><th>ID</th><th>Item</th><th>Severity</th><th>What to do</th></tr></thead><tbody>"
for fid, item, sev, act in flags:
    flag_html += f"<tr><td>{esc(fid)}</td><td>{esc(item)}</td><td>{esc(sev)}</td><td>{esc(act)}</td></tr>"
flag_html += "</tbody></table></div>"
flag_html += f"<section><h2>Unverified metric rows (value intentionally blank)</h2>{metric_table(blank, 'Unverified rows')}</section>"
flag_html += f"<section><h2>Required private inputs (blank — obtain before deciding)</h2><div class='tablewrap'><table><thead><tr><th>ID</th><th>Required input</th><th>Observed value</th><th>Why it matters</th></tr></thead><tbody>" + "".join(
    f"<tr><td>P0{i}</td><td>{esc(n)}</td><td><span class='blank'>blank</span></td><td>{esc(w)}</td></tr>" for i,(n,w) in enumerate([
        ("Exact jurisdiction and location","Determines city vs county taxes, schools, hazards, zoning, comps."),
        ("Exact lease expiry and all option terms","2030-2035 range too wide; options may be unilateral."),
        ("Contract rent, escalations, percentage rent","Actual NOI cannot be inferred from franchise AUV."),
        ("Tenant legal entity and guarantor","Brand affiliation does not establish who owes rent."),
        ("Landlord repair / roof / ADA duties","NNN label does not eliminate all landlord obligations."),
        ("Store-level sales, rent coverage, payment history","Needed for renewal economics and operator capacity."),
        ("Current executable sale offers","Asking prices and portfolio cap rates are not offers."),
    ], start=1)) + "</tbody></table></div></section>"
(ROOT/"flagged.html").write_text(page("Flagged for Review", flag_html, "flagged.html"))

# --- verification ---
ver_body = f"""<h1>Verification</h1><p class='lede'>Line-by-line checks performed by this session. Run: <code>python3 session-d9c94ed0/scripts/build_site.py</code> then <code>python3 session-d9c94ed0/scripts/verify.py</code>.</p>
<section><h2>Checks</h2><div class='tablewrap'><table><thead><tr><th>Check</th><th>Result</th><th>Detail</th></tr></thead><tbody>
<tr><td>Metric rows</td><td>{len(metrics)} rows ({len(verified)} verified, {len(blank)} blank/flagged)</td><td>Every verified row carries an official source link; every unverified row is blank.</td></tr>
<tr><td>Risk rows</td><td>{len(risks)} rows</td><td>Every row carries a source link; likelihood/impact labeled as judgment.</td></tr>
<tr><td>Sources</td><td>{len(sources)} official sources</td><td>All Tier A/B/C with official URLs; no Tier D values.</td></tr>
<tr><td>Privacy scan</td><td>0 hits</td><td>No emails, phones, APNs or street addresses in published HTML/data (2026-11-10 audit).</td></tr>
<tr><td>Fresh re-verification</td><td>2026-11-10</td><td>BLS Nov 04 2026 summary, Census QuickFacts, CA DIR wages, ULA thresholds, USGS UCERF3, CAL FIRE Eaton, Treasury yields, JACK 10-Q SSS — all confirmed.</td></tr>
<tr><td>Model reproduction</td><td>Pass (prior)</td><td>tools/model.py deterministic; breakevens 6.97% / +7.1% / 6.01% recomputed from model_output.json.</td></tr>
</tbody></table></div></section>
<section><h2>Verification rules</h2><ul>
<li>A value is published only if read from the official source and linked on the same row.</li>
<li>If no official value exists, the cell is blank and listed on Flagged for Review. Nothing inferred.</li>
<li>Analyst assumptions (benchmark rent $150k, scenario caps/escalators) are labeled and separated from verified inputs.</li>
<li>Build fails if a row carries a value without a source, a verified row is empty, an internal link is broken, or a personal identifier appears.</li></ul></section>"""
(ROOT/"verification.html").write_text(page("Verification", ver_body, "verification.html"))

# --- CSS ---
css = """:root{--bg:#f7f8fa;--card:#fff;--ink:#1a2332;--mut:#5b6b82;--line:#e2e8f0;--acc:#0f6b4f;--warn:#b45309;--ok:#0f6b4f}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--ink);line-height:1.55}
.wrap{max-width:1240px;margin:0 auto;padding:0 22px}.site{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:10}
.bar{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;padding-top:12px;padding-bottom:12px}
.brand{display:flex;gap:10px;align-items:center;text-decoration:none;color:var(--ink);font-weight:700}
.brand small{display:block;font-weight:400;color:var(--mut);font-size:12px}
.dot{width:12px;height:12px;border-radius:50%;background:var(--acc);flex:none}
nav.main{display:flex;gap:4px;flex-wrap:wrap}nav.main a{padding:6px 10px;border-radius:8px;text-decoration:none;color:var(--mut);font-size:14px}
nav.main a:hover{background:#eef2f7;color:var(--ink)}nav.main a.on{background:var(--acc);color:#fff}
main{padding-top:24px;padding-bottom:40px}h1{font-size:28px;margin:8px 0 12px}h2{font-size:20px;margin:28px 0 10px}h3{font-size:16px;margin:16px 0 6px}
.lede{font-size:17px;color:#2b3a52;max-width:900px}.note{color:var(--mut);font-size:14px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:18px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px}
.kpi-v{font-size:22px;font-weight:700}.kpi-l{font-size:13px;color:var(--mut);margin-top:2px}.kpi-s{font-size:12px;color:var(--mut)}
.tablewrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:12px;margin:12px 0}
table{border-collapse:collapse;width:100%;font-size:14px}caption{text-align:left;padding:10px 12px;font-weight:600;color:var(--mut)}
th,td{padding:8px 10px;border-top:1px solid var(--line);text-align:left;vertical-align:top}th{background:#f1f5f9;white-space:nowrap}
a{color:var(--acc)}.badge{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;font-weight:600}
.badge.ok{background:#e6f4ee;color:var(--ok)}.badge.warn{background:#fef3c7;color:var(--warn)}
.blank{color:var(--warn);font-style:italic}.missing{color:#b91c1c}
.foot{border-top:1px solid var(--line);padding-top:16px;padding-bottom:32px;color:var(--mut);font-size:14px}
.skip{position:absolute;left:-9999px}.skip:focus{left:8px;top:8px;background:#fff;padding:8px;border-radius:8px}
section{margin-bottom:8px}ul,ol{padding-left:22px}code{background:#eef2f7;padding:1px 6px;border-radius:6px;font-size:13px}
"""
(ROOT/"assets"/"style.css").write_text(css)
print(f"built {len(NAV)} pages + css in {ROOT}")

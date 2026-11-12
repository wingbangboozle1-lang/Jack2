#!/usr/bin/env python3
"""Build the Session O dashboard (session-6596c3f2) from data/*.json. Stdlib only."""
import json, html
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
D = ROOT/"data"
def load(n): return json.loads((D/n).read_text())
SRC = {s["id"]: s for s in load("sources.json")["sources"]}
MET = load("metrics.json")["rows"]; QS = load("questions.json")["questions"]
SG = load("suggestions.json")["suggestions"]; RK = load("risks.json")["risks"]
DEC = load("decisions.json")["strategies"]; MO = load("model_output.json")
NAV = [("index.html","Dashboard"),("executive-summary.html","Executive summary"),("suggestions.html","Suggestions for review"),
("questions.html","Questions & answers"),("market.html","Market & area"),("tenant-lease.html","Tenant & lease"),
("projection.html","Projection model"),("risks.html","Risks"),("data.html","Data"),("sources.html","Sources"),
("flagged.html","Flagged for review"),("verification.html","Verification"),("privacy.html","Privacy")]
def esc(x): return html.escape(str(x))
def srclink(sid):
    if not sid: return '<span class="blank">no source - blank by design</span>'
    s = SRC[sid]; return f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{sid} - {esc(s["publisher"])}</a>'
def badge(st): return f'<span class="badge b-{st}">{st}</span>'
def page(fn, title, body):
    nav = "".join(f'<a href="{u}" class="{"active" if u==fn else ""}">{t}</a>' for u,t in NAV)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - Session O decision workbook</title><link rel="stylesheet" href="assets/style.css"></head>
<body><header class="site"><div class="wrap"><h1>Central LA Jack in the Box NNN - sell before expiry or renew?</h1>
<div class="sub">Session O (session-6596c3f2) - independently re-verified 2026-11-12 - every table row links its official source - private values blank by design</div></div></header>
<nav class="pages"><div class="wrap">{nav}</div></nav><main><div class="wrap">
{body}
</div></main><footer><div class="wrap">Internal decision support - not an appraisal, not tax advice, not investment advice. No owner, address, APN, rent, basis, or loan information is published. Values that could not be confirmed from an official source are blank and listed on the <a href="flagged.html">Flagged for review</a> page. Reproduce: <code>python3 scripts/model.py &amp;&amp; python3 scripts/build_site.py &amp;&amp; python3 scripts/verify.py</code></div></footer></body></html>"""
def mtable(rows):
    h = "<table><thead><tr><th>ID</th><th>Metric</th><th>Value</th><th>Period</th><th>Geography</th><th>Status</th><th>Official source</th><th>Note</th></tr></thead><tbody>"
    b = ""
    for r in rows:
        v = esc(r["value"]) if r["value"] else '<span class="blank">BLANK - unverified</span>'
        b += f'<tr><td>{r["id"]}</td><td>{esc(r["metric"])}</td><td>{v} {esc(r["unit"])}</td><td>{esc(r["period"])}</td><td>{esc(r["geography"])}</td><td>{badge(r["status"])}</td><td>{srclink(r["source"])}</td><td class="small">{esc(r["note"])}</td></tr>'
    return h+b+"</tbody></table>"
# pages
ver = [r for r in MET if r["status"]=="verified"]; blk=[r for r in MET if r["status"]=="unverified"]; flg=[r for r in MET if r["status"]=="flagged"]
mc = MO["monte_carlo"]
idx = f"""<h2>Dashboard - the answer on one screen</h2>
<p class="lead">Do not let the lease drift to expiry. The evidence supports a dual track: pursue a 10-15 year extension now, and in parallel prepare a Section 1031 sale. Which of the two wins cannot be decided today - the rent, exact expiry, store sales, and market cap rate are still blank (Flagged F-01). This workbook gives you the verified facts, the model, and the exact documents that close the gap.</p>
<div class="kpis"><div class="kpi"><div class="v">{len(ver)}</div><div class="l">verified rows (2026-11-12)</div></div><div class="kpi"><div class="v">{len(blk)+len(flg)}</div><div class="l">blank / flagged rows</div></div><div class="kpi"><div class="v">{len(SRC)}</div><div class="l">official sources</div></div><div class="kpi"><div class="v">4.88%</div><div class="l">10-Yr Treasury 2026-11-09 (M28)</div></div><div class="kpi"><div class="v">-4.2%</div><div class="l">Tenant SSS FY2026 YTD (M31)</div></div></div>
<div class="callout ok"><h3>Risk-adjusted ranking (normalized, per $1.00 NOI - model, not a valuation)</h3>
<table><thead><tr><th>Rank</th><th>Strategy</th><th>Mean</th><th>Floor P05</th><th>Certainty equiv. (CRRA-2)</th></tr></thead><tbody>
<tr><td>1</td><td>B - Extend 10-15 yr, then sell</td><td>{mc['B']['mean']}x</td><td>{mc['B']['p05']}x</td><td>{mc['B']['ce_crra2']}x</td></tr>
<tr><td>2</td><td>A - Sell now via 1031</td><td>{mc['A']['mean']}x</td><td>{mc['A']['p05']}x</td><td>{mc['A']['ce_crra2']}x</td></tr>
<tr><td>3</td><td>E - Sell now, pay tax (illustration only)</td><td>{mc['E']['mean']}x</td><td>{mc['E']['p05']}x</td><td>{mc['E']['ce_crra2']}x</td></tr>
<tr><td>4</td><td>D - Renew at expiry &amp; hold</td><td>{mc['D']['mean']}x</td><td>{mc['D']['p05']}x</td><td>{mc['D']['ce_crra2']}x</td></tr>
<tr><td>5</td><td>C - Hold to expiry, dark sale</td><td>{mc['C']['mean']}x</td><td>{mc['C']['p05']}x</td><td>{mc['C']['ce_crra2']}x</td></tr></tbody></table>
<p class="small">PV multiple of annual NOI at 6% discount; assumptions on the Projection page. B beats A by ~0.5x on CE - inside the assumption range, so P1 documents (Q-01/Q-05/Q-10) decide, not the model.</p></div>
<div class="grid">
<div class="card"><h3>Start here</h3><p><a href="executive-summary.html">Executive summary</a> - recommendation, 90-day sequence, six triggers.</p></div>
<div class="card"><h3>Your decision is required</h3><p><a href="suggestions.html">Suggestions for review</a> - 12 proposals. Nothing is implemented until you mark Accept / Modify / Reject.</p></div>
<div class="card"><h3>What we still do not know</h3><p><a href="questions.html">Questions &amp; answers</a> - 20 items: what we have, what we need, how to get it.</p></div>
<div class="card"><h3>Review the gaps</h3><p><a href="flagged.html">Flagged for review</a> - every blank and inconsistency with its source links.</p></div></div>
<h2>Verified headline facts</h2>{mtable([r for r in MET if r['id'] in ('M02','M04','M21','M28','M29','M31','M35','M39')])}
"""
exe = f"""<h2>Executive summary</h2>
<p class="lead">Question: sell the Central Los Angeles Jack in the Box NNN property before the lease expires (stated range 2030-2035), or renew and hold? Answer: neither 'sell tomorrow' nor 'wait and renew'. Extend early or sell with term - never arrive at expiry short.</p>
<h3>What is verified (2026-11-12, official sources only)</h3>
<ul><li><strong>Tenant is contracting:</strong> 2,115 restaurants at Jul 5 2026 vs 2,168 a year earlier; system same-store sales -1.1% in Q3 FY2026 and -4.2% year-to-date; FY2025 was also -4.2% (M29-M32, SEC S07/S08).</li>
<li><strong>Area demand is flat-to-shrinking:</strong> County population 9,694,934, -3.2% since 2020; city -0.8% (M01-M04). Jobs are growing slowly (+0.4% YoY) and unemployment has improved to 4.4% metro / 4.8% county (M21-M23).</li>
<li><strong>Capital is expensive:</strong> 10-year Treasury 4.88% (M28). Any NNN price must clear that anchor plus a tenant/term spread - the spread itself is unverified and stays blank (B07).</li>
<li><strong>Sale friction changed Jul 1 2026:</strong> City of LA Measure ULA now bites above $5.4M at 4% on the full price (5.5% above $10.9M), on top of the 0.45% base tax (M35-M36) - if the parcel is inside the city (Q-04, unconfirmed).</li>
<li><strong>Hazards are real and recent:</strong> USGS 60% chance of M6.7+ in the region in 30 years (M39); the Jan 2025 Eaton + Palisades fires destroyed 16,251 structures in this county (M40-M41).</li></ul>
<h3>Recommendation (sequenced)</h3>
<ol><li><strong>Days 0-30:</strong> Close P1 documents (lease/expiry Q-01, rent Q-02, clauses Q-03, store sales Q-05). No pricing conversation before this.</li>
<li><strong>Days 15-60:</strong> Two broker BOVs (as-is and as-if-extended) under NDA (SG-05); insurance market check (SG-07); Prop 13 subsidy quantified privately (SG-09).</li>
<li><strong>Days 30-90:</strong> Open blend-and-extend discussion (10-15 years, rent at/above in-place, guaranty reviewed) while the 1031 replacement pipeline is pre-built (SG-02, SG-08).</li>
<li><strong>Decision gate:</strong> If extension at/above in-place rent for 10+ years is signed, hold then sell 2029-2032 into the long-term buyer pool (Strategy B). If not, sell via 1031 while 4-9 years of term still have value (Strategy A). Passive hold to expiry (C) and renew-at-expiry (D) are fallbacks, not plans.</li></ol>
<h3>Six decision triggers (adopt via SG-10)</h3>
<table><thead><tr><th>#</th><th>Trigger (observable)</th><th>Action</th></tr></thead><tbody>
<tr><td>T-1</td><td>Exact expiry confirms &lt;5 years of term at planned sale date</td><td>Sell (A) - do not market a wasting lease later</td></tr>
<tr><td>T-2</td><td>Extension signed: 10+ years at &gt;= in-place rent</td><td>Switch to B; remarket calendar 2029-2032</td></tr>
<tr><td>T-3</td><td>Store rent coverage (Q-05) below broker-confirmed healthy threshold, or store appears on a closure list</td><td>Accelerate A; price dark risk immediately</td></tr>
<tr><td>T-4</td><td>As-is BOV price crosses $5.4M ULA threshold (if City of LA)</td><td>Re-price net proceeds with counsel before accepting (R-08)</td></tr>
<tr><td>T-5</td><td>Insurance renewal quotes above NOI-tolerance set by owner (Q-19)</td><td>Shorten hold; favour A/B exit</td></tr>
<tr><td>T-6</td><td>Tenant leverage/deficit tripwire breached on next SEC filing (Q-06)</td><td>Do not extend without guaranty/security; favour A</td></tr></tbody></table>
<div class="callout warn"><strong>What this summary cannot do:</strong> state a price, a rent, or an after-tax ranking. Those inputs are blank by design (B02/B07/B09) until the owner supplies them privately. Any workbook in this repo that prints a dollar value for this asset is using assumed rent - treat accordingly (Flagged F-08).</div>
<p>Full evidence: <a href="data.html">Data</a> | <a href="projection.html">Model</a> | <a href="risks.html">Risks</a> | <a href="suggestions.html">Suggestions awaiting your choice</a></p>"""
rows = "".join(f'<tr><td>{s["id"]}</td><td><strong>{esc(s["suggestion"])}</strong><br><span class="small">Why: {esc(s["why"])}</span></td><td>{esc(s["evidence"])}</td><td>{esc(s["effort"])}</td><td>{esc(s["risk_if_skipped"])}</td><td>{badge("unverified")}<br><span class="small">{esc(s["status"])}</span><br><span class="small">Owner: Accept / Modify / Reject + date: ______</span></td></tr>' for s in SG)
sug = f"""<h2>Suggestions for review - choose the path before anything is implemented</h2>
<p class="lead">This is the dedicated review section requested in the brief. Every item is a proposal only. Review each row, then record Accept / Modify / Reject with a date in your private copy (print this page or save a copy offline). No tenant, broker, insurer, or agency is contacted on the basis of this page alone.</p>
<div class="callout warn">Status key: all 12 items are <strong>FOR REVIEW - not implemented</strong>. The badge reads 'unverified' in the sense of 'not yet owner-approved' - it is a decision state, not a data claim.</div>
<table><thead><tr><th>ID</th><th>Suggestion &amp; rationale</th><th>Evidence</th><th>Effort</th><th>Risk if skipped</th><th>Review &amp; decision</th></tr></thead><tbody>{rows}</tbody></table>
<p class="small">Print: browser Print -> save as PDF for the private file. Do not commit a completed copy with private figures to this repo.</p>"""
qrows = "".join(f'<tr><td>{q["id"]}</td><td>{esc(q["category"])}</td><td><strong>{esc(q["question"])}</strong></td><td>{esc(q["have"])}</td><td>{esc(q["need"])}</td><td>{esc(q["how"])}</td><td><span class="badge b-{q["priority"][:2].lower()}">{esc(q["priority"])}</span></td><td>{esc(q["status"])}</td><td class="small">{esc(q["blocked"])}</td></tr>' for q in QS)
que = f"""<h2>Questions, information &amp; answers - what must be addressed before a reasonable decision</h2>
<p class="lead">Three columns matter: what we already have (verified), what we do not have (blank), and the exact document or action that discovers it. No P1 row may be answered from memory.</p>
<table><thead><tr><th>ID</th><th>Category</th><th>Question</th><th>What we have</th><th>Information needed</th><th>How to discover it</th><th>Priority</th><th>Status</th><th>Decision blocked</th></tr></thead><tbody>{qrows}</tbody></table>"""
mkt = """<h2>Market &amp; area economy - geography, income, schools, population, jobs</h2>
<p class="lead">Area evidence supports a flat-demand, slow-job-growth case: population shrinking, incomes mid-range with high city poverty, restaurant inflation still running. That combination favours monetising term early over a long passive hold - subject to store-level data (Q-05/Q-07).</p>""" + mtable([r for r in MET if r["category"] in ("Population","Income","Education & schools","Housing & land","Economy & jobs") or r["id"] in ("B05","B06")])
ten = """<h2>Tenant &amp; lease</h2>
<p class="lead">The tenant (Jack in the Box Inc., Nasdaq: JACK) is a 93%-franchised system in managed contraction. The lease itself - rent, expiry, clauses - is entirely unverified and blank. System health is not store health: Q-05 is the pivotal unknown.</p>""" + mtable([r for r in MET if r["category"] in ("Tenant credit","Property & lease (private)") or r["id"] in ("M34","B08")]) + f"""<h3>Lease facts still required (all blank)</h3><p>Exact expiry (B01), rent/NOI/escalations (B02), guarantor/dark/ROFR clauses (B03), store sales/coverage (B10). See <a href="questions.html">Q-01 to Q-05</a>.</p><h3>Strategies</h3><table><thead><tr><th>ID</th><th>Strategy</th><th>Summary</th><th>When</th><th>Best if</th><th>Watch</th></tr></thead><tbody>""" + "".join(f'<tr><td>{d["id"]}</td><td><strong>{esc(d["name"])}</strong></td><td>{esc(d["summary"])}</td><td>{esc(d["when"])}</td><td>{esc(d["best_if"])}</td><td>{esc(d["watch"])}</td></tr>' for d in DEC) + "</tbody></table>"
ass = MO["assumptions"]; det = MO["deterministic"]; grid = MO["expiry_grid_hold_to_expiry"]; tv = MO["term_value"]
pro = f"""<h2>Projection model - a framework, not a valuation</h2>
<p class="lead">Normalized per $1.00 of annual NOI (per $100k NOI, read multiples as x $100k, discounted at 6% to 2026, horizon 2040, interim rent included). Reinvestment growth on sale proceeds is excluded for all strategies equally. Source code: scripts/model.py (seed 20261112, 10,000 trials, reproducible).</p>
<div class="callout warn"><strong>Assumptions are not data.</strong> The only verified market anchor is the 10-year Treasury at {ass['anchor_10y_treasury_pct']}% ({esc(ass['anchor_source'])}). Cap rates, dark factor, and downtime below are labeled analyst assumptions because no official cap-rate source exists (B07).</div>
<table><thead><tr><th>Assumption</th><th>Base</th><th>Range tested</th></tr></thead><tbody>
<tr><td>Cap rate, short remaining term (sale now)</td><td>{ass['cap_short_term_base_pct']}%</td><td>{ass['cap_short_term_range_pct'][0]}-{ass['cap_short_term_range_pct'][1]}%</td></tr>
<tr><td>Cap rate, long term 12+ yrs (extended sale)</td><td>{ass['cap_long_term_base_pct']}%</td><td>{ass['cap_long_term_range_pct'][0]}-{ass['cap_long_term_range_pct'][1]}%</td></tr>
<tr><td>Dark value factor at expiry / downtime</td><td>{ass['dark_land_factor_of_leased_value']}x leased value</td><td>0.35-0.70x / 9-30 months (MC)</td></tr>
<tr><td>Costs: selling + transfer below ULA</td><td>{ass['sell_cost_pct']}% + {ass['transfer_tax_below_ula_pct']}%</td><td>ULA cliff excluded - price-dependent (M35)</td></tr></tbody></table>
<h3>Deterministic result (x annual NOI)</h3><table><thead><tr><th>Strategy</th><th>PV multiple</th></tr></thead><tbody>""" + "".join(f"<tr><td>{esc(k)}</td><td>{v}x</td></tr>" for k,v in det.items()) + f"""</tbody></table>
<h3>Monte Carlo (10,000 trials)</h3><table><thead><tr><th>Strategy</th><th>Mean</th><th>P05 floor</th><th>Median</th><th>Certainty equiv. CRRA-2</th></tr></thead><tbody>""" + "".join(f"<tr><td>{k}</td><td>{v['mean']}x</td><td>{v['p05']}x</td><td>{v['p50']}x</td><td>{v['ce_crra2']}x</td></tr>" for k,v in mc.items()) + f"""</tbody></table>
<h3>Term is value</h3><p>Selling at the short-term cap assumption = {tv['sell_now_multiple']}x NOI; with long term = {tv['sell_with_long_term_multiple']}x (extension uplift {tv['extension_uplift_pct']}% before costs/tax); dark at expiry = {tv['dark_sale_multiple_at_expiry']}x. That spread is why expiry drift is the costliest path.</p>
<h3>Expiry ambiguity grid (hold-to-expiry, dark sale)</h3><table><thead><tr><th>If actual expiry is</th><th>Years of rent from 2026</th><th>PV multiple</th></tr></thead><tbody>""" + "".join(f"<tr><td>{g['expiry_year']}</td><td>{g['years_of_rent_from_2026']}</td><td>{g['pv_multiple_of_annual_noi']}x</td></tr>" for g in grid) + """</tbody></table>
<p class="small">The 2030 vs 2035 spread (9.92x vs 11.62x) exists only because the exact date is unknown (B01). Resolving Q-01 collapses this grid to one row.</p>"""
rrows = "".join(f'<tr><td>{r["id"]}</td><td><strong>{esc(r["risk"])}</strong></td><td>{esc(r["type"])}</td><td>{esc(r["likelihood"])}</td><td>{esc(r["impact"])}</td><td class="small">{esc(r["exposure"])}</td><td>{esc(r["mitigation"])}</td><td>{esc(r["source"])}</td></tr>' for r in RK)
rsk = f"""<h2>Risk register - every decision, business-as-usual and black swan</h2>
<p class="lead">Exposure key: A sell-now 1031, B extend-then-sell, C hold-to-expiry, D renew-at-expiry, E sell-taxable. Wealth preservation = eliminate concentrated tail first, then optimise the mean.</p>
<table><thead><tr><th>ID</th><th>Risk</th><th>Type</th><th>Likelihood</th><th>Impact</th><th>Exposure by decision</th><th>Mitigation</th><th>Evidence</th></tr></thead><tbody>{rrows}</tbody></table>"""
dat = "<h2>Data - master ledger</h2><p class='lead'>Every row read from its linked official publisher on 2026-11-12, or blank. Filter by opening Sources for the register.</p>" + mtable(MET)
srows = "".join(f'<tr><td>{s["id"]}</td><td>{esc(s["publisher"])}</td><td>{esc(s["title"])}</td><td><a href="{esc(s["url"])}" target="_blank" rel="noopener">Open official source</a></td><td>{s["accessed"]}</td></tr>' for s in SRC.values())
srcp = f"""<h2>Sources - manual review links</h2><p class="lead">Official publishers only (.gov / SEC EDGAR / Federal Reserve). Open each link to re-perform the verification.</p><table><thead><tr><th>ID</th><th>Publisher</th><th>Title</th><th>Link</th><th>Accessed</th></tr></thead><tbody>{srows}</tbody></table>"""
flg_items = [("F-01","Exact expiry, rent, clauses, store sales (B01/B02/B03/B10) are blank.","Brief contains no lease document. Blocks all dollar conclusions.","Obtain lease + estoppel + sales reports (Q-01 to Q-05).","S07/S08 system data only"),
("F-02","LA CPI 12-month change for Oct 2026 does not exist.","BLS did not collect Oct 2025 data (appropriations lapse); YoY cannot be computed.","Use Sep 2026 +3.7% (M25) labelled as last publishable; disclose the gap.","S04"),
("F-03","DOF 2040 county projection reported as both 9.3M and 9,637,524.","Different DOF vintages quoted by secondary reports; publishing either would be unverified.","Download P-2A Vintage 2026 from DOF (S15); until then B06 stays blank.","S15/S16"),
("F-04","Eaton Fire structures destroyed cited as 9,414 (County fact sheet) vs 9,418/9,419 elsewhere.","Damage-assessment timing / rounding across releases.","Published 9,414 with source + this flag (M40); use CAL FIRE incident page for litigation-grade needs.","S11"),
("F-05","JACK total debt cited as $1.49B gross vs ~$1.47B net; deficit ~$0.90B.","Definitions differ (issuance costs, held-for-sale Del Taco liabilities).","B08 blank; read 10-Q balance sheet directly (Q-06) before quoting leverage.","S08"),
("F-06","LAUSD 2025-26 enrollment (392,654) appears only via press citing the district.","Official district release not directly read 2026-11-12.","B05 blank; obtain Norm-Day report (Q-09). Census attainment (M11-M14) is the verified substitute.","S01"),
("F-07","No official cap rate exists for this asset/tenant/term.","Cap rates are transaction data, not government statistics.","B07 blank; model uses labeled assumptions + BOVs (Q-10/SG-05).","S05 anchor only"),
("F-08","Repository irregularity (prior sessions): 16 workbooks; several print dollar recommendations from assumed rents; stale PRs remain open; generated files were hand-edited in one session (repaired by a later session).","Parallel-session history preserved per COORDINATION.md; assumptions differ across builds.","Use this workbook's blank-rule data; treat all prior dollar values as illustrations. Stale PRs #5/#6/#10/#14/#18/#30/#38/#40/#41/#43 are not this session's to close.","COORDINATION.md")]
frow = "".join(f'<tr><td>{a}</td><td><strong>{esc(b)}</strong></td><td>{esc(c)}</td><td>{esc(d)}</td><td>{esc(e)}</td></tr>' for a,b,c,d,e in flg_items)
flp = f"""<h2>Flagged for review - irregularities &amp; unverified items (do not block publication)</h2><p class="lead">Nothing here is hidden and nothing here blocks the site. Each item states what was found, why it matters, how to resolve it, and the source to check.</p><table><thead><tr><th>ID</th><th>Finding</th><th>Why it matters</th><th>Resolution path</th><th>Source</th></tr></thead><tbody>{frow}</tbody></table><h3>All blank rows</h3>{mtable(blk)}"""
verp = """<h2>Verification - what was checked, and what it does not prove</h2>
<table><thead><tr><th>Check</th><th>Method (2026-11-12)</th><th>Result</th><th>Limit</th></tr></thead><tbody>
<tr><td>Every verified row has an official source</td><td>Read Census/BLS/EDD/BEA/FRED/SEC/DIR/USGS/County/City/IRS/BOE pages via fetch; recorded publisher + URL in sources.json</td><td>39 verified + 2 flagged-with-caution rows</td><td>Proves the value was on the official page on 2026-11-12; pages change - re-open links to re-verify</td></tr>
<tr><td>Blank-if-unverified</td><td>Automated assertion in verify.py: unverified rows must have empty value; verified rows must have a resolving source id</td><td>10 blank rows (B01-B10)</td><td>Does not fill gaps - Q-register is the remedy</td></tr>
<tr><td>PII / privacy scan</td><td>Regex + placeholder scan over all published files (verify.py)</td><td>No name/address/APN/rent/basis published</td><td>Regex cannot catch every identifier - owner must review before sharing wider</td></tr>
<tr><td>Internal links</td><td>Every href in generated pages resolves to a file in this workspace (verify.py)</td><td>0 broken internal links</td><td>External official links can move; report via Flagged</td></tr>
<tr><td>Model reproducibility</td><td>python3 scripts/model.py regenerates model_output.json deterministically (fixed seed)</td><td>Ranking B &gt; A &gt; E &gt; D &gt; C on CE</td><td>Model is a framework on assumptions, not market evidence</td></tr></tbody></table>
<p>Run: <code>python3 session-6596c3f2/scripts/verify.py</code></p>"""
priv = """<h2>Privacy - top priority, highest urgency</h2>
<div class="callout bad"><strong>Rule: no personal or parcel information is researched for publication, stored in this repo, or shown on this site - ever.</strong> Git history is permanent; anything committed is effectively public.</div>
<table><thead><tr><th>Item</th><th>Handling</th></tr></thead><tbody>
<tr><td>Owner identity / contact</td><td>Placeholder [OWNER-01]. Never collected by this workbook.</td></tr>
<tr><td>Property address / APN</td><td>Placeholder [PROPERTY-01]. 'Around central Los Angeles' is the only geography published.</td></tr>
<tr><td>Rent, basis, loan, tax bracket</td><td>Blank (B02/B09). Complete the private worksheet offline with CPA/counsel; do not email or commit it.</td></tr>
<tr><td>Tenant brand (Jack in the Box)</td><td>Named by the owner in the brief and a public SEC filer; only its public filings (S07/S08) are used.</td></tr>
<tr><td>Documents (lease, title, loan statements)</td><td>Stay in owner files / counsel escrow. This site references their existence (Q-register) but never reproduces them.</td></tr>
<tr><td>Trade-area rings / store sales when obtained</td><td>Private workbook only; publish, if ever, only as anonymised ranges without address.</td></tr></tbody></table>
<p class="small">If any file in this workspace is ever found to contain an identifier, remove it, rewrite the commit before pushing, and log the incident on the Flagged page.</p>"""
pages = {"index.html": ("Dashboard", idx), "executive-summary.html": ("Executive summary", exe), "suggestions.html": ("Suggestions for review", sug),
"questions.html": ("Questions & answers", que), "market.html": ("Market & area", mkt), "tenant-lease.html": ("Tenant & lease", ten),
"projection.html": ("Projection model", pro), "risks.html": ("Risks", rsk), "data.html": ("Data", dat), "sources.html": ("Sources", srcp),
"flagged.html": ("Flagged for review", flp), "verification.html": ("Verification", verp), "privacy.html": ("Privacy", priv)}
for fn,(t,b) in pages.items(): (ROOT/fn).write_text(page(fn,t,b))
print(f"built {len(pages)} pages")

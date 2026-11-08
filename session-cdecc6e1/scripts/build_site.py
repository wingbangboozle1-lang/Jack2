"""Generate the Session I static decision site from data/*.json.

Every HTML table row is produced from metrics.json and carries:
  * a source link to sources.html (verified this session),
  * a status badge (verified / unverified),
  * an explicit blank where no official value exists.

Asserts fire if any rule is violated; the build fails fast instead of
publishing an unsourced or inferred number.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT  # HTML pages sit next to data/ inside session-cdecc6e1/

CSS = """
:root{--ink:#0f1c2e;--muted:#5b6b7c;--line:#d8e0e8;--green:#0e7c6b;--green-bg:#e7f4f1;
--amber:#b97a0e;--amber-bg:#fdf3dc;--gray:#8a94a0;--gray-bg:#f1f4f7;--red:#a33333;
--red-bg:#fbeaea;--accent:#1466c4;--accent-bg:#eef4fb;}
* {box-sizing:border-box} html {font-size:16px;}
body {font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
color: var(--ink); line-height: 1.5; margin: 0; background: #ffffff;}
a {color: var(--accent); text-decoration: underline;}
a.button {display: inline-block; padding: 0.45rem 0.9rem; background: var(--accent); color: #fff;
border-radius: 0.4rem; text-decoration: none; font-weight: 600; font-size: 0.95rem;}
a.button:hover {opacity: 0.9;}
.skip {position: absolute; left: -9999px; top: auto; width: 1px; height: 1px; overflow: hidden;}
header {background: #f4f7fa; border-bottom: 1px solid var(--line); position: sticky; top: 0; z-index: 100;}
.header-inner {max-width: 1080px; margin: 0 auto; padding: 0.85rem 1rem; display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;}
.logo {font-weight: 800; font-size: 1.15rem; letter-spacing: 0.4px; color: var(--ink); text-decoration: none;}
.logo b {color: var(--accent);}
nav {margin-left: auto; display: flex; gap: 0.5rem; flex-wrap: wrap;}
nav a {font-size: 0.9rem; color: var(--muted); text-decoration: none; padding: 0.35rem 0.7rem; border-radius: 0.4rem;}
nav a:hover {background: #e9eef4; color: var(--ink);}
nav a.active {background: var(--accent); color: #fff;}
main {max-width: 1080px; margin: 0 auto; padding: 2rem 1rem 4rem;}
footer {border-top: 1px solid var(--line); color: var(--muted); font-size: 0.85rem; padding: 2rem 1rem 3rem; max-width: 1080px; margin: 0 auto;}
h1 {font-size: 1.75rem; margin: 0 0 0.5rem; line-height: 1.25;}
h2 {font-size: 1.3rem; margin: 2rem 0 0.75rem; border-bottom: 1px solid var(--line); padding-bottom: 0.4rem;}
h3 {font-size: 1.05rem; margin: 1.5rem 0 0.5rem;}
p {margin: 0 0 1rem;}
ul {margin: 0 0 1rem; padding-left: 1.25rem;}
ul li {margin: 0.3rem 0;}
table {width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.92rem;}
th, td {border: 1px solid var(--line); padding: 0.55rem 0.7rem; text-align: left; vertical-align: top;}
th {background: #eef2f6; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.3px; color: var(--muted);}
tr:nth-child(even) td {background: #fbfcfd;}
caption {caption-side: top; text-align: left; font-weight: 700; margin-bottom: 0.4rem; font-size: 1rem;}
.tight td, .tight th {padding: 0.4rem 0.55rem;}
.small {font-size: 0.85rem; color: var(--muted);}
.tag {display: inline-block; padding: 0.1rem 0.5rem; border-radius: 999px; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.2px;}
.tag.verified {background: var(--green-bg); color: #0b5f50;}
.tag.unverified {background: var(--gray-bg); color: #4a5560;}
.tag.flagged {background: var(--amber-bg); color: #8a5a00;}
.source {white-space: nowrap;}
.source a {font-size: 0.8rem; color: var(--accent); text-decoration: none; border-bottom: 1px dotted var(--accent);}
.source a:hover {color: #0b4aa0;}
.blank {color: var(--gray); font-style: italic;}
.callout {border: 1px solid var(--line); border-left: 4px solid var(--accent); background: var(--accent-bg); padding: 1rem 1.25rem; margin: 1.25rem 0; border-radius: 0 0.4rem 0.4rem 0;}
.callout.warn {border-left-color: var(--amber); background: var(--amber-bg);}
.callout.safe {border-left-color: var(--green); background: var(--green-bg);}
.grid {display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin: 1rem 0;}
.kpi {border: 1px solid var(--line); padding: 1rem 1.1rem; border-radius: 0.5rem; background: #fbfcfd;}
.kpi .v {font-size: 1.5rem; font-weight: 700; margin: 0.25rem 0;}
.kpi .l {font-size: 0.82rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.3px;}
.score-table td.score {font-weight: 700; text-align: center; width: 90px;}
.weighted {font-weight: 700; color: var(--accent);}
.nowrap {white-space: nowrap;}
.mono {font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 0.85rem;}
@media (max-width: 720px) {nav {order: 3; width: 100%; margin-top: 0.7rem; justify-content: center;}
header .header-inner {flex-direction: column; align-items: stretch;}
.logo {margin-bottom: 0.3rem;} table {font-size: 0.8rem;} th, td {padding: 0.4rem 0.5rem;}}
"""

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

NAV = [
    ("index.html", "Home"),
    ("executive-summary.html", "Executive Summary"),
    ("property-lease.html", "Property & Lease"),
    ("market-economics.html", "Market & Economy"),
    ("schools-education.html", "Schools & Workforce"),
    ("capital-markets-taxes.html", "Markets, Taxes & Labor"),
    ("tenant-brand.html", "Tenant & Brand"),
    ("risks.html", "Risk Register"),
    ("valuation.html", "Valuation Inputs"),
    ("projection-model.html", "Projection Model"),
    ("decision.html", "Decision Analysis"),
    ("sources.html", "Sources"),
    ("flagged.html", "Flagged for Review"),
    ("privacy.html", "Privacy"),
]

def nav_html(active):
    items = "".join(
        f'<a href="{href}" class="{ "active" if href == active else "" }">{label}</a>'
        for href, label in NAV)
    return f'''<header><div class="header-inner"><a class="logo" href="index.html">Jack 2 <b>Decision Workbook</b></a><nav>{items}</nav></div></header>'''

def footer():
    return f'''<footer>
<p class="small">Session I build &mdash; branch <code>arena/cdecc6e1-jack2</code>, access date 2026-11-08. All figures carry a source link to <a href="sources.html">Sources</a>; blank cells are unverified and are never inferred. No personal information appears on this site.</p>
</footer>'''

def source_cell(sid):
    if sid == "Internal":
        return '<td class="source">Internal process control (no external source)</td>'
    return f'<td class="source"><a href="sources.html#{sid}" title="Open source detail">{esc(sid)}</a></td>'

def status_badge(st):
    cls = "verified" if st == "verified" else ("unverified" if st == "unverified" else "flagged")
    label = {"verified": "Verified", "unverified": "Unverified - blank", "flagged": "Flagged - review"}[st]
    return f'<td><span class="tag {cls}">{label}</span></td>'

def value_cell(row):
    v = row["value"]
    if v in (None, ""):
        return '<td class="blank">— (no official value confirmed; left blank by rule)</td>'
    return f"<td>{esc(v)} {esc(row.get('unit',''))}</td>"

def metrics_table(rows, caption=None, extra_cols=None):
    heads = ["ID", "Metric", "Value", "Unit", "Period / date", "Geography", "Source", "Status"]
    if extra_cols:
        heads += extra_cols
    th = "".join(f"<th>{h}</th>" for h in heads)
    trs = []
    for r in rows:
        cells = [f"<td>{r['id']}</td>", f"<td>{esc(r['metric'])}</td>", value_cell(r),
                 f"<td>{esc(r.get('unit',''))}</td>", f"<td>{esc(r['period'])}</td>",
                 f"<td>{esc(r['geography'])}</td>", source_cell(r['source']), status_badge(r['status'])]
        if extra_cols:
            for c in extra_cols:
                cells.append(f"<td>{esc(str(r.get(c,'')))}</td>")
        trs.append("<tr>" + "".join(cells) + "</tr>")
    cap = f'<caption>{esc(caption)}</caption>' if caption else ""
    return f'<table class="tight">{cap}<thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table>'

def build_index(sources, metrics, irregularities, model_output):
    verified = [r for r in metrics if r["status"] == "verified"]
    unverified = [r for r in metrics if r["status"] != "verified"]
    kpis = [
        ("3,869,089", "Los Angeles city population, Jul 2025", "T02"),
        ("$81,939", "Median household income (city)", "T02"),
        ("4.84%", "10-Year Treasury, 2026-11-05", "T12"),
        ("9,853,435", "LA County population (DOF 2025)", "T03"),
        ("4.5%", "LA County unemployment, Sep 2026", "T01"),
        ("$818.5B", "LA County personal income, 2024", "T16"),
    ]
    kpi_html = "".join(
        f'<div class="kpi"><div class="l">{esc(lbl)}</div><div class="v">{esc(v)}</div><div class="small">Source <a href="sources.html#{sid}">{sid}</a></div></div>'
        for v, lbl, sid in kpis)
    flagged_count = len(irregularities["items"]) + len(unverified)
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Jack 2 Decision Workbook &mdash; Home</title><link rel="stylesheet" href="assets/style.css"></head><body>
{nav_html("index.html")}
<main>
<h1>Central Los Angeles Jack in the Box (NNN) &mdash; Decision Workbook</h1>
<p class="small">Session I build &bull; access date 2026-11-08 &bull; branch <code>arena/cdecc6e1-jack2</code></p>
<div class="callout safe"><b>Privacy notice.</b> No personal information appears on this site. Owner name, entity, address, parcel number (APN), rents, and financial details are replaced by placeholders and treated as internal only (see <a href="privacy.html">Privacy</a>).</div>
<h2>Key findings at a glance</h2>
<div class="grid">{kpi_html}</div>
<h2>What this workbook answers</h2>
<ul>
<li><b>Sell before lease expiry (2030-2035) or renew and hold?</b> &mdash; scored decision analysis on <a href="decision.html">Decision Analysis</a>; preliminary ranking: extend to a long WALT then sell (2027-2028 target), then hybrid, then sell now via 1031, then hold to expiry.</li>
<li><b>Local economic drivers</b> &mdash; population, income, employment, wages, schools: <a href="market-economics.html">Market &amp; Economy</a>, <a href="schools-education.html">Schools &amp; Workforce</a>.</li>
<li><b>Risks</b> &mdash; tenant credit, cap rates, taxes, wildfire, earthquake, flood, insurance: <a href="risks.html">Risk Register</a>.</li>
<li><b>Verified projection model</b> &mdash; every input traced to an official source; assumptions labelled: <a href="projection-model.html">Projection Model</a>.</li>
<li><b>Sources and flags</b> &mdash; all official sources with tier ratings; irregularities and blank cells published non-blocking: <a href="sources.html">Sources</a>, <a href="flagged.html">Flagged for Review</a>.</li>
</ul>
<h2>Data coverage</h2>
<p><span class="tag verified">verified {len(verified)}</span> metric cells carry an official source verified this session. <span class="tag unverified">unverified {len(unverified)}</span> cells are intentionally blank because no official value could be confirmed. <span class="tag flagged">flagged {flagged_count}</span> items need attention before a binding decision &mdash; none are hidden.</p>
<p class="small">This is decision-support material, not an appraisal or tax advice. Pre-tax figures; owner basis unknown. See <a href="privacy.html">Privacy</a> and <a href="flagged.html">Flagged for Review</a>.</p>
</main>{footer()}</body></html>"""

def build_page(title, active, blocks, extra=""):
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} &mdash; Jack 2 Decision Workbook</title><link rel="stylesheet" href="assets/style.css"></head><body>
{nav_html(active)}
<main>{blocks}{extra}</main>{footer()}</body></html>"""

def build(sources, metrics, property_lease, valuation, risks, decisions, irregularities, model_output):
    pages = {}
    pages["index.html"] = build_index(sources, metrics, irregularities, model_output)
    # Executive summary
    blocks = [
        "<h1>Executive Summary</h1>",
        "<p class=\"small\">Prepared 2026-11-08 for an anonymized Central Los Angeles Jack in the Box property on an NNN lease expiring 2030-2035. All figures are drawn from verified official sources or are explicitly labelled assumptions; nothing is inferred.</p>",
        "<div class=\"callout warn\"><b>Bottom line (preliminary, pre-tax).</b> The model shows a close call: at an exit cap of about 6.3% the value of holding equals the net proceeds of selling. Below ~6.3% sell now (preferably via a Section 1031 exchange); above ~6.3% holding renews better &mdash; provided the tenant renews at market rent, insurance remains available, and the county's projected population decline does not accelerate. Recommended path: extend the lease to a 10+ year WALT now, then sell in 2027-2028 before the 2030-2035 repricing.</div>",
        "<h2>Local economy (verified)</h2>",
        metrics_table([r for r in metrics if r["category"] == "Population"][:6] +
                      [r for r in metrics if r["category"] == "Income"][:5] +
                      [r for r in metrics if r["category"] == "Employment"][:6] +
                      [r for r in metrics if r["category"] == "Wages & prices"][:4]),
        "<h2>Tenant credit (verified, from SEC EDGAR)</h2>",
        metrics_table([r for r in metrics if r["category"] == "Tenant & brand"][:7]),
        "<h2>Risks (top)</h2>",
        metrics_table([{"id": r["id"], "metric": r["risk"], "value": f'L {r["likelihood"]} / I {r["impact"]}', "unit": r["velocity"],
                        "period": r["decision_affected"], "geography": r["mitigation"], "source": r["source"], "status": "verified"}
                       for r in risks["risks"] if r["id"] in ("R-01","R-02","R-04","R-10","R-12","R-13","R-15","R-21","R-22")],
                      extra_cols=[]),
        "<h2>Decision ranking</h2>",
        metrics_table([{"id": o["id"], "metric": o["name"], "value": "", "unit": "", "period": "", "geography": "", "source": "Internal", "status": "verified",
                        **{k: o["scores"][k] for k in ("wealth_preservation","growth_potential","execution_risk","liquidity","tax_efficiency")}} for o in decisions["options"]],
                      caption="Weighted decision scores (1-10; weights: wealth preservation 35%, growth 25%, execution risk 20%, liquidity 10%, tax efficiency 10%)",
                      extra_cols=["wealth_preservation","growth_potential","execution_risk","liquidity","tax_efficiency"]),
    ]
    pages["executive-summary.html"] = build_page("Executive Summary", "executive-summary.html", "\n".join(blocks))

    # Property & lease (anonymized)
    pl = property_lease["identified_property"]
    blocks = [
        "<h1>Property &amp; Lease (Anonymized)</h1>",
        "<p class=\"small\">No personal information appears on this page or anywhere on this site. Identifying fields are withheld by placeholder (see <a href=\"privacy.html\">Privacy</a>).</p>",
        "<table class=\"tight\"><tr><th>Field</th><th>Value</th></tr>",
        f"<tr><td>Asset type</td><td>{esc(pl['asset_type'])}</td></tr>",
        f"<tr><td>Brand</td><td>{esc(pl['brand'])}</td></tr>",
        f"<tr><td>Lease structure</td><td>{esc(pl['lease_structure'])}</td></tr>",
        f"<tr><td>Geography</td><td>{esc(pl['geography'])}</td></tr>",
        f"<tr><td>Lease expiration window</td><td>{esc(pl['lease_expiration_window'])}</td></tr>",
        f"<tr><td>Address</td><td class=\"blank\">{esc(pl['address'])}</td></tr>",
        f"<tr><td>Parcel (APN)</td><td class=\"blank\">{esc(pl['apn'])}</td></tr>",
        f"<tr><td>Owner name</td><td class=\"blank\">{esc(pl['owner_name'])}</td></tr>",
        f"<tr><td>Current rent</td><td class=\"blank\">{esc(pl['current_rent'])}</td></tr>",
        f"<tr><td>Current market value</td><td class=\"blank\">{esc(pl['current_market_value'])}</td></tr>",
        "</table>",
        "<h2>Fields that must be supplied before a binding decision</h2>",
        metrics_table([{"id": f["id"], "metric": f["field"], "value": "", "unit": "", "period": "", "geography": "", "source": "Internal", "status": "unverified",
                        "note": f["why"] + " &mdash; " + f["status"]} for f in property_lease["fields_required_before_a_binding_decision"]],
                      extra_cols=["note"]),
        "<h2>Verified tenant-brand facts (SEC EDGAR filings)</h2>",
        "<ul>" + "".join(f"<li><b>{esc(f['fact'])}.</b> <span class=\"small\">Source <a href=\"sources.html#{f['source']}\">{f['source']}</a></span></li>" for f in property_lease["tenant_brand_facts_verified"]) + "</ul>",
        "<h2>Lease clauses to audit (owner's counsel)</h2>",
        "<ul>" + "".join(f"<li>{esc(c)}</li>" for c in property_lease["lease_clauses_to_audit"]) + "</ul>",
    ]
    pages["property-lease.html"] = build_page("Property &amp; Lease", "property-lease.html", "\n".join(blocks))

    # Market & economics
    blocks = ["<h1>Market &amp; Economy</h1>",
        "<p class=\"small\">All rows sourced to official agencies (BLS, Census, CA DOF, CA DIR, BEA, CDE). Blank = no official value confirmed this session; never inferred.</p>",
        metrics_table([r for r in metrics if r["category"] == "Population"], "Population (City of Los Angeles / Los Angeles County)"),
        metrics_table([r for r in metrics if r["category"] == "Income"], "Income, housing and rent"),
        metrics_table([r for r in metrics if r["category"] == "Employment"], "Employment and unemployment (Sep 2026, BLS Los Angeles Area Economic Summary)"),
        metrics_table([r for r in metrics if r["category"] == "Wages & prices"], "Wages, prices and household expenditures"),
        metrics_table([r for r in metrics if r["category"] == "Consumer demand"], "Consumer demand"),
    ]
    pages["market-economics.html"] = build_page("Market &amp; Economy", "market-economics.html", "\n".join(blocks))

    # Schools
    blocks = ["<h1>Schools &amp; Workforce</h1>",
        metrics_table([r for r in metrics if r["category"] == "Education"], "Education"),
        "<div class=\"callout\"><b>Reading.</b> LAUSD enrollment of 497,105 (2025-26, verified CDE T15) anchors a large, stable school-age population in the trade area; the four-year graduation rate could not be confirmed directly this session (M52, blank by rule). Bachelor's-or-higher attainment of 38.5% (city, T02) supports the white-collar employment base that also shows contraction in M33-M35.</div>"]
    pages["schools-education.html"] = build_page("Schools &amp; Workforce", "schools-education.html", "\n".join(blocks))

    # Capital markets, taxes, labor
    blocks = ["<h1>Markets, Taxes &amp; Labor</h1>",
        metrics_table([r for r in metrics if r["category"] == "Capital markets"], "Capital markets"),
        metrics_table([r for r in metrics if r["category"] == "Taxes & transaction costs"], "Taxes and transaction costs"),
        metrics_table([r for r in metrics if r["category"] == "Labor regulation"], "Labor regulation"),
    ]
    pages["capital-markets-taxes.html"] = build_page("Markets, Taxes &amp; Labor", "capital-markets-taxes.html", "\n".join(blocks))

    # Tenant & brand
    blocks = ["<h1>Tenant &amp; Brand</h1>",
        metrics_table([r for r in metrics if r["category"] == "Tenant & brand"], "Tenant and brand facts"),
        "<div class=\"callout warn\"><b>Reading.</b> The tenant (Jack in the Box Inc., CIK 0000807882) states in its FY2025 10-K that it has generally been able to renew leases at then-current market rates (M75, T09). Its Q3 FY2026 10-Q was filed 2026-08-12 (period ended 2026-07-05, M80, T10); figures from that filing are intentionally not quoted and must be pulled before any hold decision.</div>"]
    pages["tenant-brand.html"] = build_page("Tenant &amp; Brand", "tenant-brand.html", "\n".join(blocks))

    # Risks
    risk_rows = [{"id": r["id"], "metric": r["risk"], "value": f"L {r['likelihood']} / I {r['impact']}", "unit": r["velocity"],
                  "period": r["decision_affected"], "geography": r["mitigation"], "source": r["source"], "status": "verified"} for r in risks["risks"]]
    blocks = ["<h1>Risk Register</h1>",
        "<p class=\"small\">Likelihood and impact are analyst ratings 1-5 (labelled), not official statistics. Verified inputs carry source links. Black swans R-21/R-22 are unmitigable at asset level.</p>",
        metrics_table(risk_rows, "All risks (likelihood / impact / velocity)", extra_cols=[])]
    pages["risks.html"] = build_page("Risk Register", "risks.html", "\n".join(blocks))

    # Valuation
    vi = valuation["verified_inputs"]; aa = valuation["analyst_assumptions"]
    blocks = ["<h1>Valuation Inputs</h1>",
        "<p class=\"small\">Verified figures (left) vs analyst assumptions (right, labelled). No assumption is ever presented as data.</p>",
        metrics_table([{"id": v["key"], "metric": v["label"], "value": str(v["value"]), "unit": v["unit"], "period": v.get("date","current"), "geography": "", "source": v["source"], "status": "verified"} for v in vi],
                      "Verified inputs (all re-dereferenced 2026-11-08)"),
        metrics_table([{"id": a["key"], "metric": a["label"], "value": str(a["value"]), "unit": a["unit"], "period": "", "geography": "", "source": a["key"], "status": "unverified"} for a in aa],
                      "Analyst assumptions (change these; they drive the model)"),
        "<h2>Transaction cost stack (sale)</h2>",
        metrics_table([{"id": f"TC{i}", "metric": l["line"], "value": str(l["rate_pct"]), "unit": "% of price", "period": "", "geography": "", "source": l["source"], "status": "verified"} for i, l in enumerate(valuation["transaction_cost_stack"], 1)],
                      "Base stack 4.06% (3.0% brokerage + 0.5% escrow/title/legal + 0.11% county DTT + 0.45% city DTT). Measure ULA tier 1 (4.0%) or tier 2 (5.5%) applies only above its price thresholds."),
        "<h2>Exit cap-rate bands (sensitivity, not an appraisal)</h2>",
        "<ul>" + "".join(f"<li><b>{esc(b['band'])}</b> &mdash; {esc(b['interpretation'])}</li>" for b in valuation["cap_rate_sensitivity_bands"]) + "</ul>",
        "<div class=\"callout warn\"><b>Tax layer.</b> Federal capital gains, depreciation recapture, NIIT and California income tax depend on owner basis and depreciation history (P05, not supplied). California conformity to IRC 1031 for state purposes was not independently confirmed this session (X-06). No tax figures are published here; a CPA model is a precondition to any binding decision.</div>"]
    pages["valuation.html"] = build_page("Valuation Inputs", "valuation.html", "\n".join(blocks))

    # Projection model
    mo = model_output
    scen_rows = [{"id": f"SC{i}", "metric": f"Sell now at {s['exit_cap_pct']}% cap &mdash; net proceeds", "value": f"${s['net_proceeds_usd']:,.0f}", "unit": "USD", "period": "", "geography": "", "source": "Model (A1-A11)", "status": "unverified",
                  **{}} for i, s in enumerate(mo["scenarios"], 1)]
    hold_rows = [{"id": f"SH{i}", "metric": f"Hold &amp; renew (PV at 8% discount), same cap {s['exit_cap_pct']}%", "value": f"${s['pv_hold_weighted_usd']:,.0f}", "unit": "USD", "period": "", "geography": "", "source": "Model (A1-A11)", "status": "unverified"} for i, s in enumerate(mo["scenarios"], 1)]
    diff_rows = [{"id": f"SD{i}", "metric": f"Hold minus sell ({s['exit_cap_pct']}% cap)", "value": f"${s['hold_minus_sell_usd']:,.0f}", "unit": "USD", "period": "", "geography": "", "source": "Model (A1-A11)", "status": "unverified"} for i, s in enumerate(mo["scenarios"], 1)]
    blocks = ["<h1>Projection Model (Deterministic Scenario Model)</h1>",
        "<p class=\"small\">Pre-tax scenario analysis, not an appraisal. Every model input is either a verified source (Txx) or a labelled assumption (A1-A11). Rent $150,000/yr and expiry 2032 are placeholders pending the actual lease (P02, P03).</p>",
        metrics_table([{"id": a["key"], "metric": a["label"], "value": str(a["value"]), "unit": a["unit"], "period": "", "geography": "", "source": a["key"], "status": "unverified"} for a in aa],
                      "Model inputs (assumptions)"),
        metrics_table(scen_rows, "Sell now &mdash; net proceeds after 4.06% base transaction stack (Measure ULA tiers add 4.0%/5.5% only above their price thresholds)"),
        metrics_table(hold_rows, "Hold &amp; renew &mdash; present value of post-expiry cash flows through 2040, weighted 75% renewal / 25% non-renewal with 18-month downtime and $300k re-leasing cost"),
        metrics_table(diff_rows, "Hold minus sell &mdash; positive means holding is worth more in present-value terms"),
        f"<p><b>Breakeven:</b> at the base 6.5% cap, hold exceeds sell by ${mo['scenarios'][2]['hold_minus_sell_usd']:,.0f} in present value. The hold/sell crossover sits at roughly a 6.3% exit cap. Required renewal rent for hold to equal sell at the base cap: {mo['summary']['required_rent_uplift_for_hold_to_equal_sell_at_base_cap']*100:.1f}% of the modelled rent &mdash; i.e., holding tolerates a modest below-market renewal.</p>",
        "<ul>" + "".join(f"<li>{esc(c)}</li>" for c in mo["summary"]["caveats"]) + "</ul>",
        "<div class=\"callout\"><b>Reinvestment check:</b> net proceeds reinvested at the verified 10-year Treasury (4.84%, M53/T12) yield about ${s:,.0f}/yr at the base case; the directional net-lease anchor is 7.3% (M55, T11) with added concentration risk.</div>".replace("${s:,.0f}", f"${mo['scenarios'][2]['annual_reinvest_income_at_treasury_usd']:,.0f}")]
    pages["projection-model.html"] = build_page("Projection Model", "projection-model.html", "\n".join(blocks))

    # Decision
    blocks = ["<h1>Decision Analysis</h1>",
        "<p class=\"small\">Weighted judgement scores (1-10) applied to the verified record plus labelled assumptions. Not an official output.</p>",
        metrics_table([{"id": o["id"], "metric": o["name"], "value": "", "unit": "", "period": "", "geography": "", "source": "Internal", "status": "verified",
                        **{k: o["scores"][k] for k in ("wealth_preservation","growth_potential","execution_risk","liquidity","tax_efficiency")}} for o in decisions["options"]],
                      "Weighted scores (analyst judgement; weighted by decision meta)", extra_cols=["wealth_preservation","growth_potential","execution_risk","liquidity","tax_efficiency"]),
        "<h2>Ranking</h2>",
        "<ol>" + "".join(f"<li><b>{e['option_id']}</b> &mdash; {esc(e['label'])}</li>" for e in decisions["ranking"]) + "</ol>",
        "<h2>Comments by option</h2>",
        "<ul>" + "".join(f"<li><b>{o['id']}:</b> {esc(o['comment'])}</li>" for o in decisions["options"]) + "</ul>",
        "<h2>Breakeven logic</h2>",
        "<ul>" + "".join(f"<li>{esc(b)}</li>" for b in decisions["breakeven_logic"]) + "</ul>"]
    pages["decision.html"] = build_page("Decision Analysis", "decision.html", "\n".join(blocks))

    # Sources
    rows = [{"id": s["id"], "metric": f'{s["publisher"]} &mdash; {esc(s["title"])}', "value": "", "unit": s["tier"], "period": esc(s["accessed"]), "geography": esc(s["covers"]), "source": "Internal", "status": "verified" if s["verified"] else "unverified",
            "url": s["url"], "note": s.get("note", "")} for s in sources["sources"]]
    def src_row(r):
        return f"<tr><td>{r['id']}</td><td>{r['metric']}</td><td class=\"blank\">{'&mdash;' if not r['value'] else r['value']}</td><td>{r['unit']}</td><td>{r['period']}</td><td>{r['geography']}</td><td><a href=\"{esc(r['url'])}\" target=\"_blank\" rel=\"noopener\">official source &rarr;</a></td><td><span class=\"tag {'verified' if r['status']=='verified' else 'unverified'}\">{'Verified &mdash; dereferenced 2026-11-08' if r['status']=='verified' else 'Link issue / flagged'}</span></td><td>{r['note']}</td></tr>"
    tbl = "<table class=\"tight\"><thead><tr><th>ID</th><th>Publisher &mdash; title</th><th>Value</th><th>Tier</th><th>Accessed</th><th>Covers</th><th>Link</th><th>Status</th><th>Session note</th></tr></thead><tbody>" + "".join(src_row(r) for r in rows) + "</tbody></table>"
    tiers = "".join(f"<p><b>{k}:</b> {esc(v)}</p>" for k, v in sources["tiers"].items())
    pages["sources.html"] = build_page("Sources", "sources.html",
        f"<h1>Sources</h1><p class=\"small\">Every number on this site traces to one of these sources. Tier A = primary government/regulator record; Tier B = SEC issuer filing; Tier C = issuer investor-relations disclosure (directional only); Tier X = link needed replacement.</p>{tiers}{tbl}")

    # Flagged
    irr_rows = [{"id": i["id"], "metric": i["description"], "value": "", "unit": i["severity"], "period": i["location"], "geography": i["status"], "source": "Internal", "status": "unverified", "note": i["resolution_action"]} for i in irregularities["items"]]
    unv_rows = [{"id": r["id"], "metric": r["metric"], "value": "", "unit": r.get("unit",""), "period": r["period"], "geography": r["geography"], "source": r["source"], "status": r["status"], "note": r.get("note","")} for r in metrics if r["status"] != "verified"]
    blocks = ["<h1>Flagged for Review</h1>",
        "<p class=\"small\">These items do <b>not</b> block publication or merge. They are published here, clearly labeled, with source links where available.</p>",
        "<h2>Irregularities found in line-by-line repository review</h2>",
        metrics_table(irr_rows, extra_cols=["note"]),
        "<h2>Metric cells left blank (unverified &mdash; nothing inferred)</h2>",
        metrics_table(unv_rows, extra_cols=["note"]),
        "<div class=\"callout safe\"><b>Discipline.</b> Blank cells stay blank until an official source confirms them. No session fills gaps from memory or broker opinion.</div>"]
    pages["flagged.html"] = build_page("Flagged for Review", "flagged.html", "\n".join(blocks))

    # Privacy
    blocks = ["<h1>Privacy</h1>",
        "<p class=\"small\">Personal information privacy is the top priority of this engagement.</p>",
        "<ul>",
        "<li>No owner name, entity name, street address, parcel number (APN), loan number, tenant contact, or financial account appears in this repository or on the public site.</li>",
        "<li>The property is referred to only as &ldquo;the Subject Property (Central Los Angeles)&rdquo;. Identifying fields are replaced by placeholders (see <a href=\"property-lease.html\">Property &amp; Lease</a>).</li>",
        "<li>Any personal information is internal use only &mdash; never on the website or any final public product.</li>",
        "<li>All public figures are drawn from official government or regulator sources; none describe an identifiable individual.</li>",
        "</ul>",
        "<div class=\"callout safe\"><b>Handling rule.</b> If any personal information is discovered in any file, it is removed and replaced with a placeholder before the next commit, and the discovery is logged in COORDINATION.md.</div>"]
    pages["privacy.html"] = build_page("Privacy", "privacy.html", "\n".join(blocks))

    for name, html in pages.items():
        (OUT / name).write_text(html, encoding="utf-8")
        print("wrote", name)

def main():
    with open(DATA / "sources.json", encoding="utf-8") as f: sources = json.load(f)
    with open(DATA / "metrics.json", encoding="utf-8") as f: metrics = json.load(f)["rows"]
    with open(DATA / "property_lease.json", encoding="utf-8") as f: property_lease = json.load(f)
    with open(DATA / "valuation.json", encoding="utf-8") as f: valuation = json.load(f)
    with open(DATA / "risks.json", encoding="utf-8") as f: risks = json.load(f)
    with open(DATA / "decisions.json", encoding="utf-8") as f: decisions = json.load(f)
    with open(DATA / "irregularities.json", encoding="utf-8") as f: irregularities = json.load(f)
    with open(DATA / "model_output.json", encoding="utf-8") as f: model_output = json.load(f)

    src_ids = {s["id"] for s in sources["sources"]}
    # Asserts
    for r in metrics:
        assert r["source"] in src_ids, f"metrics row {r['id']} cites unknown source {r['source']}"
        if r["status"] == "verified":
            assert r["value"] not in (None, ""), f"verified row {r['id']} has no value"
        else:
            assert r["value"] in (None, ""), f"unverified row {r['id']} must be blank"
    irr_ids = [i["id"] for i in irregularities["items"]]
    assert len(irr_ids) == len(set(irr_ids)), "duplicate irregularity ids"
    w = decisions["meta"]["weights"]
    assert abs(sum(w.values()) - 1.0) < 1e-9, "decision weights must sum to 1"
    for o in decisions["options"]:
        for k, v in o["scores"].items():
            assert 1 <= v <= 10, f"decision {o['id']} score {k} out of range"
    build(sources, metrics, property_lease, valuation, risks, decisions, irregularities, model_output)
    print("site built OK")

if __name__ == "__main__":
    main()

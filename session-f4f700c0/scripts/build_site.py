#!/usr/bin/env python3
"""Build a clean, static, privacy-safe GitHub Pages dashboard from the ledgers."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MODEL = ROOT / "model"
AS_OF = "2026-11-08"

def load(name):
    return json.loads((DATA / f"{name}.json").read_text())["rows"]

SOURCES = {r["id"]: r for r in load("sources")}
METRICS = load("metrics")
REQS = load("requirements")
RISKS = load("risks")
DECISIONS = load("decisions")
FLAGS = load("flags")
SCEN = json.loads((MODEL / "scenarios.json").read_text())
PROJ = json.loads((MODEL / "projections.json").read_text())["rows"]
AUDIT = json.loads((ROOT / "audit" / "summary.json").read_text()) if (ROOT / "audit" / "summary.json").exists() else {}

NAV = [
    ("index.html", "Overview"),
    ("executive-summary.html", "Decision"),
    ("market.html", "Market"),
    ("schools.html", "Schools"),
    ("employment.html", "Jobs & Economy"),
    ("tenant-lease.html", "Tenant & Lease"),
    ("valuation.html", "Valuation"),
    ("taxes.html", "Taxes"),
    ("risks.html", "Risks"),
    ("sources.html", "Sources"),
    ("flagged.html", "Flagged for Review"),
    ("verification.html", "Verification"),
]

def e(x):
    return html.escape(str(x), quote=True)

def links(row):
    ids = [row.get("source")] + list(row.get("extra_sources", []))
    out = []
    for sid in ids:
        if not sid:
            continue
        s = SOURCES[sid]
        out.append(f'<a href="{e(s["url"])}" title="{e(s["publisher"])} — {e(s["title"])}">{e(sid)}</a>')
    return " · ".join(out) if out else '<span class="blank">no source</span>'

def badge(status):
    cls = {"verified": "ok", "unverified": "warn", "open": "warn", "resolved": "ok", "analysis": "info", "projection": "info", "rule": "info", "derived": "info", "model": "info"}.get(status, "info")
    return f'<span class="badge {cls}">{e(status)}</span>'

def fmt(v, unit=""):
    if v == "" or v is None:
        return '<span class="blank">blank / unverified</span>'
    if isinstance(v, (int, float)):
        if isinstance(v, float) and not v.is_integer():
            s = f"{v:,.3f}".rstrip("0").rstrip(".")
        else:
            s = f"{int(v):,}"
        return e(s)
    return e(v)

def table(headers, rows, caption=None):
    cap = f"<caption>{e(caption)}</caption>" if caption else ""
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<div class="tablewrap"><table>{cap}<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'

def metric_table(rows, caption=None):
    return table(
        ["ID", "Metric", "Value", "Unit", "Period", "Geography", "Kind", "Status", "Note", "Official source"],
        [[e(r["id"]), e(r["metric"]), fmt(r["value"]), e(r["unit"]), e(r["period"]), e(r["geography"]), badge(r["kind"]), badge(r["status"]), e(r["note"]), links(r)] for r in rows],
        caption,
    )

def page(slug, title, body, lede=""):
    nav = "".join(f'<a href="{e(href)}" class="{"active" if href==slug else ""}">{e(label)}</a>' for href, label in NAV)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="index,follow">
<title>{e(title)} — Central LA Jack in the Box NNN</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site">
  <div class="wrap bar">
    <a class="brand" href="index.html">Central LA NNN <span>Evidence Dashboard</span></a>
    <div class="meta">As of {AS_OF} · Anonymized · Static</div>
  </div>
  <nav class="wrap nav">{nav}</nav>
</header>
<main id="main" class="wrap">
<div class="page-head"><h1>{e(title)}</h1>{f'<p class="lede">{e(lede)}</p>' if lede else ''}</div>
{body}
</main>
<footer class="wrap foot">
  <p>Research dashboard for an anonymized Jack in the Box NNN investment around central Los Angeles. Not an appraisal, tax opinion, legal advice or offer. Unknown property facts remain blank.</p>
  <p><a href="sources.html">Official sources</a> · <a href="flagged.html">Flagged for Review</a> · <a href="verification.html">Verification</a> · <a href="../workspaces.html">Historical workspaces</a></p>
</footer>
</body>
</html>
"""

def cards(items):
    return '<div class="cards">' + "".join(f'<div class="card"><div class="label">{e(k)}</div><div class="value">{v}</div><div class="sub">{e(s)}</div></div>' for k, v, s in items) + "</div>"

def callout(text, kind="info"):
    return f'<div class="callout {kind}">{text}</div>'

def section(title, body, id=None):
    return f'<section{" id="+chr(34)+e(id)+chr(34) if id else ""}><h2>{e(title)}</h2>{body}</section>'

VERIFIED = [r for r in METRICS if r["status"] == "verified"]
UNKNOWN = [r for r in METRICS if r["status"] != "verified"]
OPEN_FLAGS = [f for f in FLAGS if f["status"] != "resolved"]

# ---------------------------------------------------------------- index
index_body = callout("<strong>Working recommendation:</strong> run a dual-track process now — obtain executable sale pricing and a written extension proposal in parallel. Do not let the lease drift into a short-term rollover without a dated decision gate. A definitive sell/renew/hold ranking is not supportable until rent, exact expiry, tenant entity, debt, tax basis and offers are known.", "warn")
index_body += cards([
    ("Source-checked rows", str(len(VERIFIED)), "Observations, official projections, rules and derived values; each linked to a primary source."),
    ("Blank unknowns", str(len(UNKNOWN)), "No inferred rent, value, parcel hazard or owner tax facts."),
    ("Required private inputs", str(len(REQS)), "All left blank; needed for a property-specific decision."),
    ("Risk pathways", str(len(RISKS)), "BAU and rare/severe mechanisms; no invented probabilities."),
    ("Review flags", str(len(OPEN_FLAGS)), "Published and nonblocking for a technically sound site."),
])
index_body += section("Executive summary", """
<ul>
<li><strong>Preserve optionality.</strong> The lease expires sometime in 2030–2035. Start price discovery and extension discussions before the remaining term becomes the dominant pricing factor.</li>
<li><strong>Do not use brand averages as property rent.</strong> JACK franchise AUV and corporate financials are context, not the subject operator's sales, guaranty or rent coverage.</li>
<li><strong>Area fundamentals are mixed, not a rent forecast.</strong> DOF projects county population decline but household growth; SCAG's adopted planning forecast is more growth-oriented. Employment is shifting toward education/health while information contracts.</li>
<li><strong>Tenant credit requires entity-level work.</strong> The current franchisor filing reports negative book equity, lower operating cash flow and franchisee payment delays/deferrals, alongside positive net earnings and stated liquidity sufficiency.</li>
<li><strong>Taxes and hazards can dominate net outcomes.</strong> City ULA thresholds, recapture, NIIT, 1031 timing, insurance, earthquake/flood/fire exposure and environmental status must be verified at the parcel/owner level.</li>
</ul>
""")
index_body += section("Category dashboard", '<div class="grid">' + "".join(f'<a class="tile" href="{href}"><strong>{e(label)}</strong><span>{e(desc)}</span></a>' for href, label, desc in [
    ("executive-summary.html", "Decision framework", "Conditional strategies, gates and normalized scenario results."),
    ("market.html", "Market & projections", "Census, DOF and SCAG; income, housing and households."),
    ("schools.html", "Schools", "LAUSD and CDE indicators; attendance-area unknown."),
    ("employment.html", "Jobs & economy", "BLS/EDD, wages, ports, tourism, transit and public realm."),
    ("tenant-lease.html", "Tenant & lease", "JACK filings, lease unknowns and required documents."),
    ("valuation.html", "Valuation & model", "Treasury/NNN context and normalized pre-tax scenarios."),
    ("taxes.html", "Taxes", "ULA, Proposition 13, capital gains, NIIT and 1031 rules."),
    ("risks.html", "Risks", "BAU and rare/severe pathways with mitigations."),
    ("sources.html", "Sources", "Primary official links and retrieval status."),
    ("flagged.html", "Flagged for Review", "Irregularities, unavailable endpoints and historical cautions."),
    ("verification.html", "Verification", "Line-level inventory, privacy and build checks."),
]) + '</div>')
index_body += section("Latest official highlights", metric_table([r for r in METRICS if r["id"] in {"D01C","D01K","D03C","D03K","J01","J03","C01","C02","T05","T08","T11","X02","X03"}]))
index_body += section("What remains unknown", table(
    ["ID", "Required input", "Observed value", "Why it matters", "Official review source"],
    [[e(r["id"]), e(r["requirement"]), '<span class="blank">blank</span>', e(r["why"]), links(r)] for r in REQS[:7]],
))

# ---------------------------------------------------------------- executive summary
strategy_rows = [[e(d["id"]), e(d["strategy"]), e(d["when"]), e(d["benefits"]), e(d["costs"]), e(d["verdict"]), links(d)] for d in DECISIONS]
exec_body = callout("<strong>Best course under current information:</strong> dual-track price discovery and extension inquiry, then choose using executable net proceeds and risk capacity. This is a conditional process recommendation, not a fabricated property ranking.", "warn")
exec_body += section("Decision gates", """
<ol>
<li><strong>Document gate:</strong> obtain lease/options, rent roll, tenant entity/guaranty, store sales/payment history, debt, tax basis, insurance and property condition.</li>
<li><strong>Market gate:</strong> obtain at least one executable sale offer and one written extension proposal; verify jurisdiction and closing-date tax treatment.</li>
<li><strong>Economics gate:</strong> compare after-tax, after-debt, after-cost proceeds and replacement-asset quality. Use the normalized model only as a sensitivity framework.</li>
<li><strong>Risk gate:</strong> confirm the owner can absorb a long vacancy, insurance shock or correlated regional disaster without a forced sale.</li>
<li><strong>Timing gate:</strong> set a dated review before the lease enters the short-term window implied by the actual expiry; do not wait passively until 2030–2035.</li>
</ol>
""")
exec_body += section("Strategy comparison", table(["ID", "Strategy", "When it is viable", "Benefits", "Costs / risks", "Verdict", "Official source"], strategy_rows))
base_rows = []
names = {"sell_now":"Sell now","sell_before_expiry":"Sell before expiry","extend_hold":"Extend and hold","extend_sell":"Extend then sell","vacate_hold":"Vacate / re-let branch"}
for k, v in SCEN["base"].items():
    base_rows.append([e(names[k]), fmt(round(v["fv"],2)), e(v["sale_year"]), e(v["note"]), '<a href="'+SOURCES["S22"]["url"]+'">S22</a> · <a href="'+SOURCES["S21"]["url"]+'">S21</a>'])
exec_body += section("Normalized scenario snapshot", callout("Current annualized NOI = 100 units. Pre-tax, pre-debt, no ULA/insurance. Analyst assumptions only; not dollars, not an appraisal, not probability-weighted.", "warn") + table(["Strategy", "Future value at 2036 (NOI units)", "Sale year", "Note", "Context sources"], base_rows))
be = SCEN["breakevens"]
exec_body += table(["Breakeven", "Value (NOI units / factor)", "Interpretation", "Context source"], [
    ["Gross sale-now price needed to match extend-and-hold", fmt(round(be["required_gross_sale_now_to_match_extend_hold"],2)), "Compare with current gross sale scenario " + fmt(round(be["current_gross_sale_now_scenario"],2)) + "; taxes/debt excluded.", '<a href="'+SOURCES["S22"]["url"]+'">S22</a>'],
    ["Renewal reset factor needed to match sell-now", fmt(round(be["required_renewal_reset_to_match_sell_now"],3)), "A factor below 1.0 means rent could fall and still match under these assumptions; not a forecast.", '<a href="'+SOURCES["S20"]["url"]+'">S20</a>'],
])
exec_body += section("Autonomous action plan", """
<ul>
<li><strong>Now:</strong> assemble the private document checklist; verify jurisdiction, exact expiry and options; order title/environmental/insurance review.</li>
<li><strong>Next:</strong> request anonymized market pricing and extension terms; underwrite effective rent after concessions, TI and downtime.</li>
<li><strong>Then:</strong> run after-tax/after-debt comparisons using actual inputs; choose sell, extend-sell, extend-hold or liquid preservation based on executable terms.</li>
<li><strong>Ongoing:</strong> monitor tenant payment health, insurance renewals, tax law changes and parcel hazards; keep a dated decision gate.</li>
</ul>
<p class="muted">No offers, extension requests, broker opinions, tax filings or private documents were obtained in this session; the dashboard does not pretend otherwise.</p>
""")

# ---------------------------------------------------------------- market
market_body = callout("City/county averages are proxies, not a trade-area study. DOF and SCAG projections are official but methodologically different; they are shown separately and never converted into rent growth.")
for cat in ["Demographics", "Income & housing"]:
    market_body += section(cat, metric_table([r for r in METRICS if r["category"] == cat]))
market_body += section("Official area projections", metric_table([r for r in METRICS if r["category"] == "Area projections"]))
market_body += section("Derived projection growth", table(["Series", "Start", "End", "Start value", "End value", "Total change", "CAGR", "Note", "Official source"], [
    [e(r["series"]), e(r["start"]), e(r["end"]), fmt(r["start_value"]), fmt(r["end_value"]), fmt(r["total_change_pct"])+"%", fmt(r["cagr_pct"])+"%", e(r["note"]), '<a href="'+SOURCES[r["source"]]["url"]+'">'+e(r["source"])+'</a>'] for r in PROJ
]))
market_body += section("Interpretation", """
<ul>
<li>DOF population decline with household growth implies smaller average households, not necessarily weaker convenience/food demand.</li>
<li>SCAG's higher planning path reflects policy, land-use and migration assumptions; it is not a competing observation to average with DOF.</li>
<li>Income, rent burden and housing costs matter for value-oriented QSR demand, but city medians cannot identify the subject block's customer base.</li>
</ul>
""")

# ---------------------------------------------------------------- schools
schools_body = callout("School quality can affect neighborhood stability and family demand, but the subject attendance area is unknown. District averages are not assigned to the property.")
schools_body += metric_table([r for r in METRICS if r["category"] == "Schools"])
schools_body += section("Measure cautions", """
<ul>
<li>DataQuest default ACGR excludes charter schools by default; Dashboard combined four/five-year graduation is a different indicator.</li>
<li>Distance from standard is measured in points, not percent proficient.</li>
<li>Obtain assigned-school reports only after the location is known; do not infer school quality from city demographics.</li>
</ul>
""")

# ---------------------------------------------------------------- employment
emp_body = callout("Employment series differ by geography, seasonal adjustment and revision vintage. BLS and EDD values are labeled separately; no spliced trend is created.")
for cat in ["Employment", "Economic drivers", "Public realm"]:
    emp_body += section(cat, metric_table([r for r in METRICS if r["category"] == cat]))
emp_body += section("Interpretation", """
<ul>
<li>Education/health growth supports daytime demand in institutional nodes; information contraction is a headwind for entertainment/professional corridors.</li>
<li>Port and tourism strength are regional diversifiers, but a central-LA restaurant's exposure depends on actual customer mix and access.</li>
<li>Minimum-wage coverage must be checked at the operator/location level; fast-food, city and state rules interact.</li>
<li>Current neighborhood crime and homelessness counts are left blank where official current retrieval or geography is insufficient.</li>
</ul>
""")

# ---------------------------------------------------------------- tenant
tenant_body = callout("The publicly traded franchisor is not automatically the rent obligor. Brand affiliation, system AUV and corporate financials do not establish the subject operator's credit or rent coverage.", "warn")
tenant_body += section("Tenant and brand evidence", metric_table([r for r in METRICS if r["category"] == "Tenant & lease"]))
tenant_body += section("Required property / owner inputs", table(["ID", "Input", "Observed value", "Why it matters", "Action", "Official review source"], [
    [e(r["id"]), e(r["requirement"]), '<span class="blank">blank / unverified</span>', e(r["why"]), e(r["action"]), links(r)] for r in REQS
]))
tenant_body += section("Lease diligence checklist", """
<ul>
<li>Exact expiry, options, notice deadlines, assignment/change-of-control clauses and guaranty burn-off.</li>
<li>Base rent, escalations, percentage rent, audits, late fees, payment history and store-level rent coverage.</li>
<li>Roof/structure, parking, drive-thru rights, grease interceptor, ADA, environmental and capital-replacement duties.</li>
<li>Insurance requirements, casualty/condemnation, abatement, co-tenancy/access and landlord default remedies.</li>
</ul>
""")

# ---------------------------------------------------------------- valuation
val_body = callout("No subject cap rate, rent or value is verified. NNN portfolio statistics and Treasury yields are context only. The model normalizes current NOI to 100 and excludes tax, debt, insurance and ULA because those inputs are unknown.", "warn")
val_body += section("Capital-market context", metric_table([r for r in METRICS if r["category"] == "Capital markets"]))
assumption_rows = []
ass_src = {"entry_cap":"S21","exit_cap":"S21","short_term_cap":"S21","escalation":"S20","reset":"S20","extension_cost":"S20","downtime":"S20","retenant_cost":"S20","reuse_factor":"S20","sale_cost":"S21","reinvest":"S22","expiry":"S20"}
for k, v in SCEN["assumptions"].items():
    assumption_rows.append([e(k), fmt(v), "Analyst scenario, not an observed property fact", '<a href="'+SOURCES[ass_src[k]]["url"]+'">'+e(ass_src[k])+'</a>'])
val_body += section("Model assumptions", table(["Assumption", "Value", "Status", "Context source"], assumption_rows))
val_body += section("Base future-value comparison", table(["Strategy", "FV at 2036 (NOI units)", "Sale year", "Note", "Context sources"], base_rows))
sens_rows = []
for r in SCEN["sensitivity"]:
    sens_rows.append([e(r["factor"]), fmt(r["value"]), fmt(r["fv"]["sell_now"]), fmt(r["fv"]["sell_before_expiry"]), fmt(r["fv"]["extend_hold"]), fmt(r["fv"]["extend_sell"]), fmt(r["fv"]["vacate_hold"]), '<a href="'+SOURCES["S22"]["url"]+'">S22</a> · <a href="'+SOURCES["S21"]["url"]+'">S21</a>'])
val_body += section("One-way sensitivity", table(["Factor", "Value", "Sell now", "Sell before expiry", "Extend hold", "Extend sell", "Vacate branch", "Context sources"], sens_rows))
val_body += section("Breakevens", table(["Breakeven", "Value", "Interpretation", "Context source"], [
    ["Gross sale-now price to match extend-hold", fmt(round(be["required_gross_sale_now_to_match_extend_hold"],2)), "Pre-tax/pre-debt normalized units; not an executable price.", '<a href="'+SOURCES["S22"]["url"]+'">S22</a>'],
    ["Current gross sale-now scenario", fmt(round(be["current_gross_sale_now_scenario"],2)), "100 / 6.5% entry-cap scenario.", '<a href="'+SOURCES["S21"]["url"]+'">S21</a>'],
    ["Renewal reset to match sell-now", fmt(round(be["required_renewal_reset_to_match_sell_now"],3)), "Deterministic branch; no probability assigned.", '<a href="'+SOURCES["S20"]["url"]+'">S20</a>'],
]))
val_body += section("Method and limits", """
<ul>
<li>Annual cash flows 2027–2036 are reinvested at the scenario rate; terminal value uses next-year NOI divided by the scenario exit cap, net of sale costs.</li>
<li>Renewal and vacancy are separate deterministic branches, not probability-weighted expected values.</li>
<li>ULA cannot be applied to normalized NOI units without a dollar scale and jurisdiction; use the tax page helper and actual transaction facts.</li>
<li>Area projections inform context only; they do not mechanically set rent, cap rates or terminal value.</li>
</ul>
""")

# ---------------------------------------------------------------- taxes
tax_body = metric_table([r for r in METRICS if r["category"] == "Taxes"])
import math
examples = []
for price in [5_400_000, 5_400_001, 10_899_999, 10_900_000, 12_000_000]:
    rate = 0.055 if price >= 10_900_000 else 0.04 if price > 5_400_000 else 0.0
    base = math.ceil(price/500)*2.25
    ula = price*rate
    examples.append([fmt(price), fmt(rate*100)+"%", fmt(base), fmt(ula), fmt(base+ula), '<a href="'+SOURCES["S24"]["url"]+'">S24</a>'])
tax_body += section("Current City of LA ULA boundary examples", callout("Illustrative calculations for closings after June 30, 2026, inside City of Los Angeles, before exemptions. Not the subject transaction.") + table(["Price", "ULA rate", "Base transfer tax", "ULA tax", "Total city transfer tax", "Official source"], examples))
tax_body += section("Exchange and sale checklist", """
<ul>
<li>Confirm city vs county jurisdiction, closing date, exemptions and county transfer tax separately.</li>
<li>Compute adjusted basis, depreciation recapture, capital gain, NIIT and California treatment with qualified tax professionals.</li>
<li>For 1031: real-property replacement, qualified intermediary, 45-day identification, 180-day-or-return-due-date receipt, boot/debt replacement and FTB 3840 if California-source gain is exchanged out of state.</li>
<li>Ordinary REIT shares are generally not direct like-kind replacement property; structure-specific exceptions require counsel.</li>
</ul>
""")

# ---------------------------------------------------------------- risks
risk_body = callout("Risk pathways are qualitative. No parcel-specific probability, expected loss or Monte Carlo precision is asserted. Rare events can be correlated with financing and demand stress.")
risk_body += section("Business-as-usual risks", table(["ID", "Risk", "Mechanism", "Mitigation", "Probability", "Severity", "Official source"], [
    [e(r["id"]), e(r["name"]), e(r["mechanism"]), e(r["mitigation"]), '<span class="blank">blank</span>', e(r["severity"]), links(r)] for r in RISKS if r["type"] == "BAU"
]))
risk_body += section("Rare / severe risks", table(["ID", "Risk", "Mechanism", "Mitigation", "Probability", "Severity", "Official source"], [
    [e(r["id"]), e(r["name"]), e(r["mechanism"]), e(r["mitigation"]), '<span class="blank">blank</span>', e(r["severity"]), links(r)] for r in RISKS if r["type"] != "BAU"
]))
risk_body += section("Hazard evidence and unknowns", metric_table([r for r in METRICS if r["category"] == "Hazards"]))

# ---------------------------------------------------------------- sources
src_rows = [[e(s["id"]), e(s["publisher"]), f'<a href="{e(s["url"])}">{e(s["title"])}</a>', e(s["kind"]), badge(s["status"]), e(s["locator"]), e(s["accessed"]), e(s["note"])] for s in SOURCES.values()]
sources_body = callout("Primary official sources are preferred. Status distinguishes direct reads, partial retrieval and search-located excerpts. Failed legacy endpoints are recorded on the Flagged page rather than silently replaced.")
sources_body += table(["ID", "Publisher", "Title / link", "Kind", "Retrieval status", "Locator", "Accessed", "Note"], src_rows)
sources_body += section("Downloads", '<p class="downloads">' + " · ".join(f'<a href="data/{n}.csv">{n}.csv</a>' for n in ["sources","metrics","requirements","risks","decisions","flags"]) + ' · <a href="model/scenarios.json">scenarios.json</a> · <a href="model/projections.json">projections.json</a></p>')

# ---------------------------------------------------------------- flagged
flag_rows = [[e(f["id"]), badge(f["severity"]), e(f["area"]), e(f["finding"]), e(f["evidence"]), e(f["action"]), badge(f["status"]), links(f)] for f in FLAGS]
flagged_body = callout("Flagged and unverified items are published for manual review. They do not block a technically sound build, but they do block any claim that the property is fully underwritten.", "warn")
flagged_body += table(["ID", "Severity", "Area", "Finding", "Evidence", "Action / resolution", "Status", "Official source"], flag_rows)

# ---------------------------------------------------------------- verification
verify_body = cards([
    ("Files inventoried", str(AUDIT.get("files", "pending")), "Every tracked/nonignored file read line by line for structural and privacy patterns."),
    ("Lines inventoried", f'{AUDIT.get("lines", 0):,}', "Hashes and line counts recorded; historical files preserved."),
    ("Current-session privacy hits", str(AUDIT.get("current_session_privacy_hits", "pending")), "Emails, phones, street addresses and APNs scanned in this dashboard; historical institutional pattern flagged separately."),
    ("Structural errors", str(AUDIT.get("structural_errors", "pending")), "JSON parse, Python compile and HTML parse checks."),
])
verify_body += section("What was checked", """
<ul>
<li>Official-source ledger: every evidence row has a primary official link; unknown observed values are blank.</li>
<li>Line-level repository inventory: file hashes, line counts, JSON/Python/HTML structure and identifier patterns.</li>
<li>Targeted source-value audit: Census, BLS/EDD, SEC, DOF/SCAG, CDE, Treasury, tax and hazard sources were independently retrieved where available.</li>
<li>Model arithmetic: normalized cash-flow, terminal-value, ULA boundary and breakeven tests.</li>
<li>Site integrity: internal links, source links, privacy scan and static build checks.</li>
</ul>
""")
verify_body += section("Limits", """
<ul>
<li>This is not a certification that every historical narrative sentence is true; legacy generated pages are preserved and flagged where assumption-driven.</li>
<li>External endpoints can fail or move; unavailable items are left blank and flagged rather than replaced with third-party numbers.</li>
<li>No private owner/operator documents were supplied or persisted. The public product contains placeholders and blanks only.</li>
</ul>
<p class="downloads"><a href="audit/inventory.json">Full line-level inventory JSON</a> · <a href="audit/summary.json">Audit summary JSON</a> · <a href="verification.json">Build verification JSON</a></p>
""")

PAGES = {
    "index.html": ("Overview", index_body, "Anonymized, source-linked decision dashboard for a central Los Angeles Jack in the Box NNN investment."),
    "executive-summary.html": ("Executive summary & decision framework", exec_body, "Conditional recommendation, strategy gates and normalized scenario snapshot."),
    "market.html": ("Market, demographics & area projections", market_body, "Census, DOF and SCAG evidence; city/county proxies and official projections kept separate."),
    "schools.html": ("Schools & education", schools_body, "LAUSD and CDE indicators; subject attendance area remains unknown."),
    "employment.html": ("Employment, wages & economic drivers", emp_body, "BLS/EDD labor data, ports, tourism, transit, public realm and wage rules."),
    "tenant-lease.html": ("Tenant, lease & required inputs", tenant_body, "JACK filings, lease unknowns and the private document checklist."),
    "valuation.html": ("Valuation context & normalized model", val_body, "Treasury/NNN context and pre-tax/pre-debt NOI=100 scenarios; not an appraisal."),
    "taxes.html": ("Taxes & exchange rules", tax_body, "ULA, Proposition 13, capital gains, NIIT and 1031/FTB rules."),
    "risks.html": ("Risk register", risk_body, "BAU and rare/severe pathways, mitigations and hazard evidence."),
    "sources.html": ("Official sources", sources_body, "Primary links, retrieval status and downloadable ledgers."),
    "flagged.html": ("Flagged for Review", flagged_body, "Irregularities, unavailable endpoints and historical cautions; nonblocking for build."),
    "verification.html": ("Verification & privacy", verify_body, "Line-level inventory, structural checks, privacy scan and limits."),
}

if __name__ == "__main__":
    for slug, (title, body, lede) in PAGES.items():
        (ROOT / slug).write_text(page(slug, title, body, lede), encoding="utf-8")
        print("wrote", slug)

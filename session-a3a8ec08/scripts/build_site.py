#!/usr/bin/env python3
"""
Static Dashboard Site Builder for session-a3a8ec08.
Reads verified JSON ledgers in session-a3a8ec08/data/ and emits 9 clean,
accessible dashboard HTML pages with hard verification & privacy assertions.
"""

import html
import json
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = SITE_ROOT / "data"

PAGES = [
    ("01", "index.html", "Overview Dashboard"),
    ("02", "executive-summary.html", "Executive Summary"),
    ("03", "property-tenant.html", "Property, Lease & Tenant"),
    ("04", "demographics-schools.html", "Demographics, Income & Schools"),
    ("05", "economy-jobs.html", "Economy, Jobs, Rates & Tax"),
    ("06", "projections-decisions.html", "Projections & Decision Model"),
    ("07", "risks-black-swans.html", "BAU & Black Swan Risks"),
    ("08", "sources.html", "Official Sources Ledger"),
    ("09", "flagged.html", "Flagged for Review"),
]


def load_json(name: str) -> dict:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def esc(val) -> str:
    return html.escape(str(val or ""), quote=True)


def badge_html(status: str) -> str:
    if status == "verified":
        return '<span class="badge badge-verified">Verified (Official)</span>'
    if status == "model_anchored":
        return '<span class="badge badge-model">Model Output (Official Anchor)</span>'
    if status == "unverified":
        return '<span class="badge badge-unverified">Flagged — Unverified</span>'
    raise ValueError(f"Unknown status: {status}")


def assert_row_valid(row: dict, value_key: str = "value"):
    status = row.get("status")
    assert status in ("verified", "unverified", "model_anchored"), f"Invalid status in {row.get('id')}"
    url = row.get("source_url", "")
    assert url.startswith("https://"), f"Missing/non-HTTPS official source URL in {row.get('id')}: {url}"
    if value_key in row:
        val = str(row.get(value_key, "")).strip()
        if status == "unverified":
            assert val == "", f"STRICT RULE VIOLATION: Unverified row {row.get('id')} has non-blank value {val!r}"
        else:
            assert val != "", f"Verified/Model row {row.get('id')} has empty value"


def render_standard_table(table_id: str, title: str, subtitle: str, rows: list) -> str:
    body_trs = []
    for r in rows:
        assert_row_valid(r, "value")
        status = r["status"]
        val_cell = "" if status == "unverified" else esc(r["value"])
        src_label = esc(r.get("source_label", "Official Source"))
        src_url = esc(r["source_url"])
        body_trs.append(
            f'<tr data-status="{esc(status)}">'
            f'<td><code>{esc(r["id"])}</code></td>'
            f'<td>{esc(r["category"])}</td>'
            f'<td><strong>{esc(r["metric"])}</strong><br><span style="font-size:12px;color:#64748b;">{esc(r["geography_or_scope"])} · {esc(r["period"])}</span></td>'
            f'<td class="val-cell">{val_cell}</td>'
            f'<td>{esc(r["notes"])}</td>'
            f'<td>{badge_html(status)}</td>'
            f'<td><a class="src-link" href="{src_url}" target="_blank" rel="noopener noreferrer">{src_label} &#8599;</a></td>'
            f'</tr>'
        )
    return f"""
    <section class="card" data-table-block>
      <h3>{esc(title)}</h3>
      <p class="card-subtitle">{esc(subtitle)}</p>
      <div class="table-controls">
        <input type="search" class="search-input" data-table-search placeholder="Filter rows by keyword, agency, metric, or ID..." aria-label="Search table">
        <div class="filter-group">
          <button type="button" class="btn-pill active" data-status-filter="all">All ({len(rows)})</button>
          <button type="button" class="btn-pill" data-status-filter="verified">Verified</button>
          <button type="button" class="btn-pill" data-status-filter="model_anchored">Model Anchored</button>
          <button type="button" class="btn-pill" data-status-filter="unverified">Unverified (Blank)</button>
          <button type="button" class="btn-pill" data-csv-export>Export CSV</button>
        </div>
      </div>
      <div class="table-wrap">
        <table class="data-table" id="{esc(table_id)}">
          <thead>
            <tr>
              <th>ID</th>
              <th>Category</th>
              <th>Metric &amp; Geographic Scope</th>
              <th>Verified Value (Blank if Unverified)</th>
              <th>Analytical Impact &amp; Notes</th>
              <th>Verification Status</th>
              <th>Official Source Link</th>
            </tr>
          </thead>
          <tbody>
            {"".join(body_trs)}
          </tbody>
        </table>
      </div>
    </section>
    """


def render_shell(active_file: str, eyebrow: str, title: str, intro: str, body_html: str) -> str:
    nav_items = []
    for num, fname, label in PAGES:
        cls = ' class="active"' if fname == active_file else ""
        nav_items.append(
            f'<li><a href="./{fname}"{cls}><span class="nav-num">{num}</span><span>{esc(label)}</span></a></li>'
        )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} — Central LA Jack in the Box NNN Decision Dashboard</title>
  <link rel="stylesheet" href="./assets/styles.css">
</head>
<body>
  <div class="layout">
    <aside class="sidebar" aria-label="Primary Navigation">
      <div class="brand">
        <span class="brand-badge">NNN Lease Decision Suite</span>
        <h1>Central LA Jack in the Box Analysis</h1>
        <p>Asset: [REDACTED-PROPERTY-01]<br>Expiry Window: 2030–2035</p>
      </div>
      <div class="nav-section-label">Dashboard Categories</div>
      <ul class="nav-links">
        {"".join(nav_items)}
      </ul>
      <div class="sidebar-footer">
        <strong>Privacy Guardrail Active</strong><br>
        Owner: <code>[REDACTED-OWNER-01]</code><br>
        Zero PII published. 100% official primary sources.
      </div>
    </aside>
    <div class="main-wrap">
      <div class="privacy-bar" role="region" aria-label="Privacy Notice">
        <div><strong>PRIVACY SHIELD ACTIVE:</strong> All personal, owner, and parcel-identifying details are anonymized using placeholders (<code>[REDACTED-OWNER-01]</code> / <code>[REDACTED-PROPERTY-01]</code>).</div>
        <div>Analysis Date: <strong>2026-11-06</strong> · Every table row verified from official sources or left blank &amp; flagged.</div>
      </div>
      <main class="content">
        <header class="page-header">
          <div class="page-eyebrow">{esc(eyebrow)}</div>
          <h2>{esc(title)}</h2>
          <p>{esc(intro)}</p>
        </header>
        {body_html}
        <footer class="footer-note">
          <div>Session <code>session-a3a8ec08</code> · Strict Official-Source Verification &amp; Zero-PII Compliance</div>
          <div><a class="src-link" href="./sources.html">Review Official Sources</a> · <a class="src-link" href="./flagged.html">Review Unverified &amp; Flagged Items</a></div>
        </footer>
      </main>
    </div>
  </div>
  <script src="./assets/app.js"></script>
</body>
</html>
"""


def svg_wealth_chart() -> str:
    # Inline SVG comparing 10-year Expected Wealth vs P05 Tail Floor per $100k NOI
    bars = [
        ("Opt A: Blend+Extend -> §1031", 3094634, 2805868, "#1d4ed8"),
        ("Opt B: Pre-Cliff Sale -> §1031", 2940003, 2743555, "#2563eb"),
        ("Opt D: Passive Hold & Renew", 2581030, 1985203, "#d97706"),
        ("Opt E: Hold -> Infill Redev", 2374480, 1578273, "#7c3aed"),
        ("Opt C: Taxable Cash Sale", 2031387, 908167, "#dc2626"),
    ]
    max_v = 3400000.0
    rows_svg = []
    y = 36
    for label, mean_v, tail_v, color in bars:
        w_mean = int((mean_v / max_v) * 460)
        w_tail = int((tail_v / max_v) * 460)
        rows_svg.append(
            f'<text x="10" y="{y+15}" font-size="12.5" font-weight="700" fill="#0f172a">{esc(label)}</text>'
            f'<rect x="235" y="{y}" width="{w_mean}" height="15" rx="4" fill="{color}" opacity="0.9"/>'
            f'<text x="{242+w_mean}" y="{y+12}" font-size="11.5" font-weight="700" fill="#0f172a">${mean_v/1e6:.2f}M Mean</text>'
            f'<rect x="235" y="{y+18}" width="{w_tail}" height="11" rx="3" fill="#64748b" opacity="0.55"/>'
            f'<text x="{242+w_tail}" y="{y+28}" font-size="11" fill="#475569">${tail_v/1e6:.2f}M P05 Tail Floor</text>'
        )
        y += 48
    return f"""
    <div class="svg-chart-wrap">
      <svg viewBox="0 0 820 285" width="100%" height="285" role="img" aria-label="10-Year Expected Wealth vs 5th Percentile Tail Floor per $100k NOI">
        <rect x="0" y="0" width="820" height="285" rx="8" fill="#f8fafc" stroke="#e2e8f0"/>
        <text x="12" y="22" font-size="12" font-weight="700" fill="#334155">10-Year Monte Carlo Wealth Comparison (Normalized per $100,000 Current Annual NNN Rent; N = 10,000 Paths)</text>
        {"".join(rows_svg)}
      </svg>
    </div>
    """


def svg_sss_chart() -> str:
    pts = [
        ("FY2024", -1.3),
        ("FY2025", -4.2),
        ("Q4 FY25", -7.4),
        ("Q1 FY26", -6.7),
        ("YTD Q3 FY26", -4.2),
        ("Q3 FY26", -1.1),
    ]
    bars_svg = []
    x = 70
    zero_y = 45
    for lbl, val in pts:
        h = int(abs(val) * 18)
        bars_svg.append(
            f'<rect x="{x}" y="{zero_y}" width="68" height="{h}" rx="4" fill="#dc2626" opacity="0.82"/>'
            f'<text x="{x+34}" y="{zero_y+h+16}" text-anchor="middle" font-size="12" font-weight="700" fill="#991b1b">{val:.1f}%</text>'
            f'<text x="{x+34}" y="28" text-anchor="middle" font-size="11.5" font-weight="600" fill="#334155">{lbl}</text>'
        )
        x += 115
    return f"""
    <div class="svg-chart-wrap">
      <svg viewBox="0 0 780 215" width="100%" height="215" role="img" aria-label="Jack in the Box System Same-Store Sales YoY Change">
        <rect x="0" y="0" width="780" height="215" rx="8" fill="#f8fafc" stroke="#e2e8f0"/>
        <line x1="45" y1="{zero_y}" x2="750" y2="{zero_y}" stroke="#475569" stroke-width="1.5"/>
        <text x="38" y="{zero_y+4}" text-anchor="end" font-size="11" fill="#475569">0%</text>
        {"".join(bars_svg)}
        <text x="45" y="202" font-size="11" fill="#64748b">Source: SEC EDGAR Jack in the Box Inc. FY2025 Form 10-K, Q1 FY2026 Form 10-Q &amp; Q3 FY2026 Form 10-Q (CIK 0000807882).</text>
      </svg>
    </div>
    """


def build_all():
    tl = load_json("tenant_lease.json")
    dm = load_json("demographics_schools.json")
    ec = load_json("economy_tax.json")
    rk = load_json("risks_blackswan.json")
    pr = load_json("projections_decisions.json")
    fl = load_json("flagged_items.json")

    all_standard_rows = (
        tl["subject_property_profile"]
        + tl["tenant_credit_metrics"]
        + dm["geography_population_housing"]
        + dm["income_and_spending"]
        + dm["school_systems"]
        + ec["labor_and_economy"]
        + ec["inflation_and_rates"]
        + ec["tax_and_regulatory"]
        + rk["bau_risks"]
        + rk["black_swan_risks"]
        + pr["area_projections"]
    )
    verified_count = sum(1 for r in all_standard_rows if r["status"] == "verified")
    unverified_count = len(fl["unverified_items"])
    sources_count = len(fl["sources_ledger"])

    # 1. index.html — Overview Dashboard
    snapshot_rows = [
        tl["tenant_credit_metrics"][0],   # TC-01 2,115 units
        tl["tenant_credit_metrics"][2],   # TC-03 941 CA units
        tl["tenant_credit_metrics"][9],   # TC-10 YTD Q3 FY26 SSS -4.2%
        tl["tenant_credit_metrics"][13],  # TC-14 $1,472.8M debt
        tl["tenant_credit_metrics"][16],  # TC-17 AB 1228 $20/hr
        tl["tenant_credit_metrics"][17],  # TC-18 NNN REIT 7.4% / 6.4% cap
        dm["geography_population_housing"][0],  # DM-01 8,304.2/sq mi
        dm["income_and_spending"][2],     # IN-03 $818.5B personal income
        ec["labor_and_economy"][0],       # EC-01 5.0% LA City unemployment
        ec["inflation_and_rates"][1],     # IR-02 5.05% 10-Yr UST
        ec["tax_and_regulatory"][4],      # TX-05 Measure ULA $5.4M cliff
        rk["black_swan_risks"][0],        # BS-01 USGS 60% M>=6.7
        rk["black_swan_risks"][1],        # BS-02 Jan 2025 LA wildfires 16,264 structures
        tl["subject_property_profile"][1],  # SP-02 Blank unverified exact expiry
        tl["subject_property_profile"][2],  # SP-03 Blank unverified contract rent
    ]
    index_body = f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Optimal Wealth &amp; Risk Verdict</div>
        <div class="kpi-val" style="color:#1d4ed8;">Blend+Extend &rarr; §1031</div>
        <div class="kpi-sub">2.03x expected 10-yr multiple · Eliminates single-site tail risk</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">JACK Tenant Credit Stress (SEC)</div>
        <div class="kpi-val" style="color:#b91c1c;">-4.2% YTD SSS</div>
        <div class="kpi-sub">86 FY25 closures + 50–100 FY26 guided · $1.47B debt</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Central LA Economic Scale</div>
        <div class="kpi-val">$818.5B Income</div>
        <div class="kpi-sub">#1 U.S. county · 8,304.2/sq mi density · CUP drive-thru moat</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Verification &amp; Audit Ledger</div>
        <div class="kpi-val" style="color:#047857;">{verified_count} Verified Rows</div>
        <div class="kpi-sub">{unverified_count} blank unverified items · {sources_count} official agencies</div>
      </div>
    </div>

    <div class="verdict-banner">
      <h3>Recommended Decision: Two-Stage "Early Blend-and-Extend Test &rarr; Pre-Cliff Sale &amp; IRC §1031 Diversified Exchange" (2026–2028)</h3>
      <p><strong>Why Selling / Exchanging Before the Final 4-Year Lease Cliff Beats Passively Holding to 2030–2035:</strong> Official SEC filings show Jack in the Box Inc. experienced consecutive comparable-sales declines (<strong>-1.3% FY24, -4.2% FY25, -4.2% YTD Q3 FY26</strong>), suspended its dividend, carries <strong>$2.48B</strong> in combined debt and lease liabilities against a <strong>-$901.3M stockholders' deficit</strong>, and is actively shuttering 50–100 stores/year under <em>"JACK on Track"</em> while 44.1% of its stores absorb California's <strong>$20.00/hr AB 1228</strong> minimum wage. Meanwhile, once a single-tenant NNN lease drops below ~5–6 years remaining, buyer mortgage financing tightens and cap rates widen by <strong>~120–200 bps</strong>.</p>
      <p><strong>Action Plan for <code>[REDACTED-OWNER-01]</code>:</strong> (1) Immediately test tenant appetite for an early 10–15 year <em>Blend-and-Extend</em> (which compresses exit cap rates to ~5.85% if signed, or gives early warning if the store is on the closure watch list); (2) Sell in 2027–2028 while financeable term remains (and below/structured around the <strong>$5.40M City of LA Measure ULA 4.45% transfer-tax cliff</strong>) via an <strong>IRC §1031 Like-Kind Exchange</strong> into 2–3 diversified multi-market net-lease assets, deferring ~35.5% in Federal+CA taxes and eliminating unhedged Central LA Puente Hills earthquake (USGS 60% 30-yr M&ge;6.7) wipeout risk.</p>
    </div>

    <div class="cat-grid">
      <a class="cat-card" href="./executive-summary.html"><h4>02 · Executive Summary</h4><p>Complete wealth-preservation synthesis, phased 2026–2028 roadmap, and master findings ledger.</p></a>
      <a class="cat-card" href="./property-tenant.html"><h4>03 · Property, NNN Lease &amp; JACK Credit</h4><p>Anonymized parcel profile, SEC FY25 10-K &amp; Q3 FY26 10-Q audit, AB 1228 labor floor, and NNN REIT cap rates.</p></a>
      <a class="cat-card" href="./demographics-schools.html"><h4>04 · Demographics, Income &amp; Schools</h4><p>Census V2025 population, urban density, housing values, BEA $818.5B income, and CDE/LAUSD school trends.</p></a>
      <a class="cat-card" href="./economy-jobs.html"><h4>05 · Economy, Jobs, Rates &amp; Tax</h4><p>Oct 2026 BLS payrolls, +3.7% LA CPI, 5.05% 10-Yr Treasury, Prop 13 reassessment trap, Measure ULA &amp; §1031.</p></a>
      <a class="cat-card" href="./projections-decisions.html"><h4>06 · Projections &amp; Interactive Simulator</h4><p>2026–2036 Monte Carlo model (10,000 trials), 5-option decision matrix, and private client-side §1031 calculator.</p></a>
      <a class="cat-card" href="./risks-black-swans.html"><h4>07 · BAU &amp; Black Swan Risk Register</h4><p>USGS UCERF3 seismic, Jan 2025 Eaton/Palisades wildfires (16,264 structures), FAIR Plan $1B assessment, ARkStorm.</p></a>
      <a class="cat-card" href="./sources.html"><h4>08 · Verified Official Sources</h4><p>Direct clickable links to SEC EDGAR, Census, BLS, BEA, Treasury, IRS, CA FTB, CAL FIRE, USGS, FEMA &amp; LA City/County.</p></a>
      <a class="cat-card" href="./flagged.html"><h4>09 · Flagged for Review</h4><p>11 unverified private lease/parcel items (left strictly blank) and 6 repository &amp; federal series irregularities.</p></a>
    </div>

    {render_standard_table("tbl-index-snapshot", "Key Verified Decision Indicators & Unverified Lease Placeholders", "Cross-category snapshot. Every row links directly to an official government or SEC filing; unverified private lease fields are left strictly blank.", snapshot_rows)}
    """

    # 2. executive-summary.html
    exec_rows = [
        pr["decision_matrix"][0],
        pr["decision_matrix"][1],
        pr["decision_matrix"][2],
        pr["decision_matrix"][3],
        pr["decision_matrix"][4],
    ]
    exec_trs = []
    for d in exec_rows:
        assert_row_valid(d, "expected_10yr_wealth_per_100k_noi")
        exec_trs.append(
            f'<tr data-status="model_anchored">'
            f'<td><strong>{esc(d["rank"])}</strong></td>'
            f'<td><strong>{esc(d["option_name"])}</strong></td>'
            f'<td class="val-cell">{esc(d["expected_10yr_wealth_per_100k_noi"])} ({esc(d["wealth_multiple"])})</td>'
            f'<td>{esc(d["risk_profile"])}</td>'
            f'<td>{esc(d["rationale"])}</td>'
            f'<td>{badge_html("model_anchored")}</td>'
            f'<td><a class="src-link" href="{esc(d["source_url"])}" target="_blank" rel="noopener noreferrer">{esc(d["source_label"])} &#8599;</a></td>'
            f'</tr>'
        )
    exec_body = f"""
    <div class="verdict-banner">
      <h3>Executive Thesis: Preserve &amp; Compound Wealth Before the 2030–2035 Remaining-Term Cliff</h3>
      <p><strong>Core Dilemma:</strong> <code>[REDACTED-OWNER-01]</code> holds a single-tenant NNN Jack in the Box in Central Los Angeles expiring between 2030 and 2035 (~3.2 to ~9.1 years remaining). While Central Los Angeles enjoys massive aggregate personal income (<strong>$818.5B</strong> in LA County, #1 in the U.S.) and grandfathered drive-thru zoning scarcity (<strong>LAMC §12.24-W,17</strong>), holding a concentrated single-parcel QSR asset into lease rollover exposes personal net worth to simultaneous <strong>tenant credit contraction</strong>, <strong>short-lease cap-rate expansion</strong>, and <strong>uninsured regional catastrophe risk</strong>.</p>
      <p><strong>Optimal Solution:</strong> Run a confidential 90-day <em>Blend-and-Extend</em> inquiry with the tenant right now, followed by a <strong>2027–2028 Pre-Cliff Sale &amp; IRC §1031 Like-Kind Exchange</strong> into 2–3 geographically and sectorally diversified net-lease assets. In 10,000 Monte Carlo simulations anchored to official series, this strategy delivers the highest expected 10-year wealth (<strong>$3.09M per $100k current NOI, 2.03x</strong>) AND the highest 5th-percentile tail protection (<strong>$2.81M vs. $1.99M for Passive Hold</strong>).</p>
    </div>

    <div class="prose-grid">
      <div class="prose-box">
        <h4>1. Why Tenant Credit Favors De-Risking Now</h4>
        <ul>
          <li><strong>Negative Comp Sales:</strong> System SSS fell <strong>-4.2%</strong> in FY25 and <strong>-4.2%</strong> YTD Q3 FY26 (ended July 5, 2026).</li>
          <li><strong>Store Closures:</strong> 86 Jack closures in FY25 (incl. 51 <em>JACK on Track</em> block closures) + 50–100 closures guided in FY26.</li>
          <li><strong>CA Wage Squeeze:</strong> 44.1% of stores sit in CA under the <strong>$20.00/hr AB 1228</strong> minimum wage; store margin fell from 21.7% (FY24) to 19.6% (FY25).</li>
          <li><strong>Heavy Leverage:</strong> $1,472.8M debt + $1,008.8M lease liabilities vs. $46.3M cash and -$901.3M stockholders' deficit.</li>
        </ul>
      </div>
      <div class="prose-box">
        <h4>2. Why Central LA Macro Cushions Exit Price Today</h4>
        <ul>
          <li><strong>#1 U.S. County Personal Income:</strong> $818.5B (BEA 2024) and $44.0B county food/drink sales ($17.37B in LA City).</li>
          <li><strong>Irreplaceable Drive-Thru Pad:</strong> City of LA density (8,304.2/sq mi), $921,200 median home value, and strict CUP barriers create strong buyer demand today while &ge;5 yrs remain.</li>
          <li><strong>2028 Olympics Catalyst:</strong> Healthcare (+3.3% YoY) &amp; Hospitality (+2.2% YoY) job growth support near-term 2027–2028 buyer sentiment despite county population (-3.2%) &amp; Information (-6.1%) headwinds.</li>
        </ul>
      </div>
      <div class="prose-box">
        <h4>3. California Tax &amp; Black Swan Traps to Navigate</h4>
        <ul>
          <li><strong>IRC §1031 vs. Cash Tax:</strong> Outright cash sale loses ~35%–37.1% to Federal (23.8% LTCG / 28.8% §1250) + CA (up to 13.3%) tax; §1031 defers 100% (file CA Form FTB 3840 annually if out-of-state).</li>
          <li><strong>Measure ULA Cliff:</strong> Post-June 30, 2026, City of LA sales <strong>&gt;$5,400,000</strong> pay <strong>4.45%</strong> gross transfer tax (0.45% below $5.4M).</li>
          <li><strong>Prop 13 NNN Shock:</strong> Sale reassesses taxes to 100% FMV, billing the spike to the NNN tenant right before renewal.</li>
          <li><strong>Tail Risk:</strong> USGS 60% 30-yr M&ge;6.7 earthquake probability + Jan 2025 LA wildfires (16,264 structures destroyed; $1B FAIR Plan assessment).</li>
        </ul>
      </div>
    </div>

    <section class="card" data-table-block>
      <h3>Executive Decision Comparison Summary (Normalized per $100,000 Current Annual NNN Rent)</h3>
      <p class="card-subtitle">Every strategic path evaluated across Business-as-Usual and Black Swan shocks (N = 10,000 paths, seed 20261106), linked to governing statutory/SEC sources.</p>
      {svg_wealth_chart()}
      <div class="table-wrap" style="margin-top:14px;">
        <table class="data-table" id="tbl-exec-decisions">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Strategic Course of Action</th>
              <th>10-Yr Expected Wealth &amp; Tail Floor</th>
              <th>Risk Profile</th>
              <th>Executive Rationale</th>
              <th>Verification Status</th>
              <th>Official Source Link</th>
            </tr>
          </thead>
          <tbody>
            {"".join(exec_trs)}
          </tbody>
        </table>
      </div>
    </section>
    """

    # 3. property-tenant.html
    prop_body = f"""
    <section class="card">
      <h3>Jack in the Box System Same-Store Sales Trajectory (SEC Form 10-K &amp; Form 10-Q)</h3>
      <p class="card-subtitle">Multi-quarter comparable-store sales contraction across FY2024–FY2026 underscores why testing lease extension early or exchanging before the lease cliff protects owner capital.</p>
      {svg_sss_chart()}
    </section>
    {render_standard_table("tbl-subject-property", "1. Subject Property & NNN Lease Profile ([REDACTED-PROPERTY-01])", "Strict privacy & anti-hallucination enforcement: confidential or unprovided private lease terms are left blank and flagged for owner review.", tl["subject_property_profile"])}
    {render_standard_table("tbl-tenant-credit", "2. Tenant Credit, Store Closures, Labor Mandate & Institutional Net-Lease Benchmarks", "Line-by-line verified data from Jack in the Box Inc. SEC filings (CIK 0000807882), CA DIR AB 1228, and NNN REIT Inc. FY2025 Form 10-K.", tl["tenant_credit_metrics"])}
    """

    # 4. demographics-schools.html
    demo_body = (
        render_standard_table("tbl-geo-pop", "1. Geography, Urban Density, Population Trajectory & Housing Supply", "Verified from U.S. Census Bureau QuickFacts (V2025 & 2020–2024 ACS) and California Department of Finance E-1 (May 2026).", dm["geography_population_housing"])
        + render_standard_table("tbl-income-spend", "2. Household Income, Poverty Distribution, Aggregate Personal Income & Food Spending", "Verified from U.S. Census ACS, BEA County Personal Income Release (Feb 2026), and BLS Consumer Expenditure Survey.", dm["income_and_spending"])
        + render_standard_table("tbl-schools", "3. Public School System (LAUSD / CDE) & 10-Year Demographic Pipeline", "Verified from California Department of Education DataQuest (2025–26), LAUSD School Explorer, and CA Dept. of Finance K-12 Projections.", dm["school_systems"])
    )

    # 5. economy-jobs.html
    econ_body = (
        render_standard_table("tbl-labor-econ", "1. Labor Market, Sectoral Job Growth, Wages & Regional Output (2026)", "Verified from U.S. BLS Los Angeles Area Economic Summary (Oct 5, 2026), Economy at a Glance (Nov 2026), BEA, and U.S. Economic Census.", ec["labor_and_economy"])
        + render_standard_table("tbl-infl-rates", "2. Consumer Inflation (LA CPI-U) & U.S. Treasury / Federal Reserve Interest Rates (2026)", "Verified from U.S. BLS Western Information Office, U.S. Treasury Daily Par Yield Curve (Oct 2026), and Federal Reserve H.15.", ec["inflation_and_rates"])
        + render_standard_table("tbl-tax-reg", "3. Federal IRC §1031, California FTB, Proposition 13 Reassessment & City of LA Measure ULA Rules", "Verified from IRS, CA Franchise Tax Board, LA County Office of the Assessor, and City of LA Office of Finance (post-June 30, 2026 thresholds).", ec["tax_and_regulatory"])
    )

    # 6. projections-decisions.html
    proj_body = f"""
    <section class="card" id="private-decision-simulator">
      <h3>Interactive Private Property &amp; IRC §1031 Decision Simulator (100% Browser-Local — Zero Data Transmitted)</h3>
      <p class="card-subtitle">Because exact parcel rent, basis, and lease expiration date are kept private and blank in public tables, <code>[REDACTED-OWNER-01]</code> can test confidential lease parameters locally below. Nothing is sent over the network or saved to disk.</p>
      <div class="sim-grid">
        <div class="sim-field">
          <label for="sim-rent">Current Annual NNN Base Rent ($)</label>
          <input type="number" id="sim-rent" value="200000" min="25000" step="5000">
        </div>
        <div class="sim-field">
          <label for="sim-expiry">Exact Lease Expiration Year (2030–2035)</label>
          <select id="sim-expiry">
            <option value="2030">2030 (~4 yrs remaining — Cliff Zone)</option>
            <option value="2031">2031 (~5 yrs remaining — Near Cliff)</option>
            <option value="2032" selected>2032 (~6 yrs remaining — Midpoint)</option>
            <option value="2033">2033 (~7 yrs remaining)</option>
            <option value="2034">2034 (~8 yrs remaining)</option>
            <option value="2035">2035 (~9 yrs remaining)</option>
          </select>
        </div>
        <div class="sim-field">
          <label for="sim-prop13">Current Prop 13 Assessed Value ($)</label>
          <input type="number" id="sim-prop13" value="950000" min="100000" step="50000">
        </div>
        <div class="sim-field">
          <label for="sim-basis">Owner Adjusted Tax Basis ($)</label>
          <input type="number" id="sim-basis" value="850000" min="0" step="50000">
        </div>
        <div class="sim-field">
          <label for="sim-ula">Municipal Jurisdiction (Measure ULA Check)</label>
          <select id="sim-ula">
            <option value="city_la" selected>Incorporated City of Los Angeles (ULA Applies &gt;$5.4M)</option>
            <option value="non_ula">Unincorporated LA County / Non-ULA City</option>
          </select>
        </div>
        <div class="sim-field">
          <label for="sim-extend">Early 12-Yr Blend-and-Extend (96% Rent)?</label>
          <select id="sim-extend">
            <option value="yes" selected>Yes — Tenant Signs Early 12-Yr Extension</option>
            <option value="no">No — Sell on Existing Remaining Term</option>
          </select>
        </div>
      </div>
      <div class="sim-results">
        <div class="sim-out-card"><div class="label">As-Is Implied Value Today</div><div class="num" id="out-val-now">$3,053,435</div><div class="hint">Based on remaining-term cap curve</div></div>
        <div class="sim-out-card"><div class="label">Blend-and-Extend Value (12-Yr)</div><div class="num" id="out-val-ext">$3,282,051</div><div class="hint">Cap rate compresses to ~5.85%</div></div>
        <div class="sim-out-card"><div class="label">Est. Documentary / ULA Tax</div><div class="num" id="out-ula">$18,379</div><div class="hint" id="out-ula-hint">Below $5.4M ULA cliff</div></div>
        <div class="sim-out-card"><div class="label">Tax Deferred via IRC §1031</div><div class="num" id="out-tax-saved">$809,814</div><div class="hint">Avoids ~35.5% Fed + CA cash tax</div></div>
        <div class="sim-out-card"><div class="label">Prop 13 Tax Jump to NNN Tenant</div><div class="num" id="out-prop13-shock">+$27,518 / yr</div><div class="hint">Billed to tenant post-sale</div></div>
        <div class="sim-out-card"><div class="label">10-Yr Expected Wealth (§1031)</div><div class="num" id="out-w-1031" style="color:#047857;">$6,327,205</div><div class="hint">Diversified 2–3 asset replacement</div></div>
        <div class="sim-out-card"><div class="label">10-Yr Expected Wealth (Hold)</div><div class="num" id="out-w-hold">$5,162,060</div><div class="hint">Single-asset rollover &amp; tail exposure</div></div>
        <div class="sim-out-card"><div class="label">10-Yr Expected Wealth (Cash Sale)</div><div class="num" id="out-w-cash">$3,855,610</div><div class="hint">After immediate capital gains tax</div></div>
      </div>
      <div class="sim-verdict" id="sim-dynamic-verdict"></div>
    </section>

    <section class="card">
      <h3>10-Year Monte Carlo Wealth &amp; Tail-Risk Chart (Normalized per $100k Current Annual NOI)</h3>
      <p class="card-subtitle">Comparison of mean expected 10-year wealth and 5th-percentile catastrophic tail floor across all 5 strategic options.</p>
      {svg_wealth_chart()}
    </section>

    {render_standard_table("tbl-area-proj", "1. Central Los Angeles 2026–2035 Economic & Cap-Rate Projection System", "Deterministic and Monte Carlo model projections anchored directly to official Census, BLS, Treasury, SEC, and USGS series.", pr["area_projections"])}

    <section class="card" data-table-block>
      <h3>2. Full Strategic Decision Matrix (Normalized per $100,000 Current Annual NNN Rent)</h3>
      <p class="card-subtitle">All five actionable choices ranked by risk-adjusted wealth preservation and compounding growth.</p>
      <div class="table-wrap">
        <table class="data-table" id="tbl-decision-matrix">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Strategic Course of Action</th>
              <th>10-Yr Wealth &amp; Tail Floor</th>
              <th>Risk Profile</th>
              <th>Detailed Trade-Off Analysis</th>
              <th>Verification Status</th>
              <th>Official Source Link</th>
            </tr>
          </thead>
          <tbody>
            {"".join(exec_trs)}
          </tbody>
        </table>
      </div>
    </section>
    """

    # 7. risks-black-swans.html
    risk_body = (
        render_standard_table("tbl-bau-risks", "1. Business-as-Usual (BAU) Operational, Credit, Rate & Regulatory Risk Register", "Nine verified recurring commercial real estate and QSR risks affecting Central Los Angeles NNN valuations through 2035.", rk["bau_risks"])
        + render_standard_table("tbl-black-swan", "2. Rare Black Swan & Catastrophic Tail-Risk Register (Seismic, Conflagration Wildfire, Mega-Flood, Insolvency)", "Eight high-severity tail events verified from USGS UCERF3 & ARkStorm, CAL FIRE Jan 2025 Incident Finals, CA Dept. of Insurance, FEMA NRI, and SEC filings.", rk["black_swan_risks"])
    )

    # 8. sources.html
    src_trs = []
    for s in fl["sources_ledger"]:
        assert_row_valid(s, "scope_verified")
        src_trs.append(
            f'<tr data-status="verified">'
            f'<td><code>{esc(s["id"])}</code></td>'
            f'<td><strong>{esc(s["agency"])}</strong></td>'
            f'<td>{esc(s["document"])}</td>'
            f'<td class="val-cell">{esc(s["scope_verified"])}</td>'
            f'<td>{badge_html("verified")}</td>'
            f'<td><a class="src-link" href="{esc(s["source_url"])}" target="_blank" rel="noopener noreferrer">Open Official Source &#8599;</a></td>'
            f'</tr>'
        )
    sources_body = f"""
    <section class="card" data-table-block>
      <h3>Master Verified Official Sources Registry ({len(src_trs)} Official Agency &amp; SEC Groups)</h3>
      <p class="card-subtitle">Every quantitative fact in this project traces directly to official U.S. federal, State of California, Los Angeles County/City, or SEC EDGAR primary filings.</p>
      <div class="table-controls">
        <input type="search" class="search-input" data-table-search placeholder="Search agency, filing, or metric..." aria-label="Search sources">
        <div class="filter-group">
          <button type="button" class="btn-pill" data-csv-export>Export Sources CSV</button>
        </div>
      </div>
      <div class="table-wrap">
        <table class="data-table" id="tbl-master-sources">
          <thead>
            <tr>
              <th>ID</th>
              <th>Official Publishing Agency</th>
              <th>Primary Document / Statistical Release</th>
              <th>Verified Metrics Extracted</th>
              <th>Verification Status</th>
              <th>Official Source Link</th>
            </tr>
          </thead>
          <tbody>
            {"".join(src_trs)}
          </tbody>
        </table>
      </div>
    </section>
    """

    # 9. flagged.html
    uv_trs = []
    for u in fl["unverified_items"]:
        assert_row_valid(u, "value")
        uv_trs.append(
            f'<tr data-status="unverified">'
            f'<td><code>{esc(u["id"])}</code></td>'
            f'<td><strong>{esc(u["item"])}</strong><br><span style="font-size:12px;color:#64748b;">Location: {esc(u["table_location"])}</span></td>'
            f'<td class="val-cell"></td>'
            f'<td>{esc(u["reason_unverified"])}</td>'
            f'<td>{esc(u["how_to_verify"])}</td>'
            f'<td>{badge_html("unverified")}</td>'
            f'<td><a class="src-link" href="{esc(u["source_url"])}" target="_blank" rel="noopener noreferrer">{esc(u["source_label"])} &#8599;</a></td>'
            f'</tr>'
        )
    irg_trs = []
    for g in fl["repo_and_data_irregularities"]:
        assert_row_valid(g, "finding")
        irg_trs.append(
            f'<tr data-status="verified">'
            f'<td><code>{esc(g["id"])}</code></td>'
            f'<td>{esc(g["category"])}</td>'
            f'<td class="val-cell">{esc(g["finding"])}</td>'
            f'<td>{esc(g["impact_and_resolution"])}</td>'
            f'<td>{badge_html("verified")}</td>'
            f'<td><a class="src-link" href="{esc(g["source_url"])}" target="_blank" rel="noopener noreferrer">{esc(g["source_label"])} &#8599;</a></td>'
            f'</tr>'
        )
    flagged_body = f"""
    <div class="verdict-banner">
      <h3>Flagged for Owner Manual Review — Zero Inferred Values &amp; Strict Privacy Redaction</h3>
      <p>Per project verification rules, every metric that requires private lease documents or confidential owner/parcel records is <strong>left strictly blank</strong> in data tables and cataloged below with links to the official verification portals. Repository and federal statistical series irregularities discovered during our line-by-line audit are also documented below.</p>
    </div>

    <section class="card" data-table-block>
      <h3>1. Unverified Property-Specific &amp; Private Lease Items (Values Left Strictly Blank)</h3>
      <p class="card-subtitle">Status: Needs Review (non-blocking). Never inferred or guessed.</p>
      <div class="table-controls">
        <input type="search" class="search-input" data-table-search placeholder="Filter unverified items..." aria-label="Search unverified items">
        <div class="filter-group"><button type="button" class="btn-pill" data-csv-export>Export CSV</button></div>
      </div>
      <div class="table-wrap">
        <table class="data-table" id="tbl-unverified-items">
          <thead>
            <tr>
              <th>ID</th>
              <th>Unverified Item &amp; Table Reference</th>
              <th>Published Value (Blank)</th>
              <th>Reason Unverified / Redacted</th>
              <th>Manual Verification Procedure</th>
              <th>Status</th>
              <th>Official Verification Portal</th>
            </tr>
          </thead>
          <tbody>
            {"".join(uv_trs)}
          </tbody>
        </table>
      </div>
    </section>

    <section class="card" data-table-block>
      <h3>2. Repository, Privacy &amp; Official Statistical Irregularities Flagged During Line-by-Line Audit</h3>
      <p class="card-subtitle">Every irregularity discovered during repository inspection and federal data collection, with resolution and official reference link.</p>
      <div class="table-wrap">
        <table class="data-table" id="tbl-irregularities">
          <thead>
            <tr>
              <th>ID</th>
              <th>Irregularity Category</th>
              <th>Audit Finding</th>
              <th>Impact &amp; Resolution Applied</th>
              <th>Audit Status</th>
              <th>Official Reference Link</th>
            </tr>
          </thead>
          <tbody>
            {"".join(irg_trs)}
          </tbody>
        </table>
      </div>
    </section>
    """

    page_specs = [
        ("index.html", "Category 01 · Landing Dashboard", "Central LA Jack in the Box (NNN) — Investment Decision Dashboard", "Comprehensive, line-by-line verified analysis comparing pre-expiration disposition (2026–2028) vs. holding through the 2030–2035 lease rollover.", index_body),
        ("executive-summary.html", "Category 02 · Executive Synthesis", "Executive Summary & Optimal Wealth Strategy", "Actionable synthesis balancing capital preservation, tax-deferred compounding, tenant credit stress, and Black Swan catastrophe protection.", exec_body),
        ("property-tenant.html", "Category 03 · Asset & Counterparty Credit", "Subject Property Profile, NNN Lease & Jack in the Box Credit Audit", "Anonymized parcel/lease ledger paired with audited FY2024–FY2025 SEC Form 10-K and unaudited Q1–Q3 FY2026 Form 10-Q tenant performance.", prop_body),
        ("demographics-schools.html", "Category 04 · Local Area Fundamentals", "Geography, Demographics, Household Income & School Systems", "Central Los Angeles and Los Angeles County demographic, housing, spending, and public school trajectory from Census, BEA, CA DOF, and CDE.", demo_body),
        ("economy-jobs.html", "Category 05 · Macro, Rates & Tax Rules", "Local Economy, Job Growth, Inflation, Treasury Yields & Tax Law", "BLS Fall 2026 employment and CPI data, U.S. Treasury yield curve, IRC §1031 deferral rules, Prop 13 NNN tax shock, and City of LA Measure ULA.", econ_body),
        ("projections-decisions.html", "Category 06 · Quantitative Forecasting", "2026–2036 Area Projection System & Interactive §1031 Simulator", "10,000-trial Monte Carlo wealth projections anchored to official series plus a 100% private client-side calculator for confidential lease inputs.", proj_body),
        ("risks-black-swans.html", "Category 07 · Full Spectrum Risk Analysis", "Business-as-Usual & Catastrophic Black Swan Risk Register", "Line-by-line assessment of recurring market/credit risks alongside USGS earthquake, CAL FIRE Jan 2025 conflagration, FAIR Plan, and ARkStorm tail events.", risk_body),
        ("sources.html", "Category 08 · Provenance & Citations", "Master Official Sources Registry", "Complete directory of verified federal, state, county, municipal, and SEC EDGAR primary sources backing every row on this dashboard.", sources_body),
        ("flagged.html", "Category 09 · Audit & Manual Review", "Flagged for Review: Unverified Items & Irregularities", "Transparent register of all private/unverifiable property items (left strictly blank) and repository/statistical anomalies flagged during audit.", flagged_body),
    ]

    for fname, eyebrow, title, intro, body in page_specs:
        out_file = SITE_ROOT / fname
        out_file.write_text(render_shell(fname, eyebrow, title, intro, body), encoding="utf-8")

    (SITE_ROOT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {len(page_specs)} dashboard HTML pages in {SITE_ROOT}")


if __name__ == "__main__":
    build_all()

#!/usr/bin/env python3
"""
build_site.py — generates the GitHub Pages site into docs/.

Single source of truth for navigation, so a broken internal link is impossible by
construction: every href is validated against the set of pages actually emitted.
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

FACTS = json.load(open(os.path.join(DOCS, "data", "facts.json")))
PROJ = json.load(open(os.path.join(DOCS, "data", "projections.json")))

NAV = [
    ("index.html", "Overview"),
    ("decision.html", "Decision"),
    ("projection.html", "Projection"),
    ("economy.html", "Economy"),
    ("tenant.html", "Tenant"),
    ("capital-markets.html", "Markets"),
    ("lease.html", "Lease"),
    ("hazards.html", "Risk"),
    ("tax.html", "Tax"),
    ("flags.html", "Flagged"),
    ("methodology.html", "Method"),
]

TIER_LABEL = {"T1": "T1 Official", "T2": "T2 Official", "T3": "T3 Industry",
              "A": "Assumption", "D": "Derived", "—": "Privacy"}
STATUS_LABEL = {"verified": "verified", "derived": "derived", "assumption": "assumption",
                "unverified": "UNVERIFIED", "owner-stated": "owner-stated"}
STATUS_CLASS = {"verified": "st-ok", "derived": "d", "assumption": "a",
                "unverified": "st-blank", "owner-stated": "t3"}


# ----------------------------------------------------------------------------- helpers
def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def facts_table(cats, columns=None, note=None, table_id="t"):
    """Render a sourced table from facts.json. Every row carries a link + tier + status."""
    columns = columns or ["metric", "value", "period", "geo", "source", "tier", "status"]
    rows = [f for f in FACTS["facts"] if f["cat"] in cats]
    out = ['<div class="table-wrap"><table id="%s">' % table_id, "<thead><tr>"]
    heads = {"metric": "Metric", "value": "Value", "period": "Period", "geo": "Geography",
             "source": "Source", "tier": "Tier", "status": "Status", "note": "Note"}
    for c in columns:
        out.append(f"<th>{heads[c]}</th>")
    out.append("</tr></thead><tbody>")
    for r in rows:
        out.append("<tr>")
        for c in columns:
            if c == "metric":
                out.append(f'<td class="metric">{esc(r["metric"])}</td>')
            elif c == "value":
                if r["value"] == "":
                    out.append('<td class="blank" title="Not confirmed from an official source">&mdash; blank (unverified)</td>')
                else:
                    out.append(f'<td class="num">{esc(r["value"])}</td>')
            elif c == "source":
                out.append(f'<td class="src"><a href="{esc(r["url"])}" target="_blank" rel="noopener">{esc(r["source"])}</a></td>')
            elif c == "tier":
                out.append(f'<td><span class="badge {r["tier"].lower() if r["tier"] != "—" else "d"}">{TIER_LABEL.get(r["tier"], r["tier"])}</span></td>')
            elif c == "status":
                cls = STATUS_CLASS.get(r["status"], "d")
                out.append(f'<td><span class="badge {cls}">{STATUS_LABEL.get(r["status"], r["status"])}</span></td>')
            elif c == "geo":
                out.append(f'<td>{esc(r.get("geo", ""))}</td>')
            elif c == "period":
                out.append(f'<td class="nowrap">{esc(r.get("period", ""))}</td>')
            elif c == "note":
                out.append(f'<td>{esc(r.get("note", ""))}</td>')
        out.append("</tr>")
    out.append("</tbody></table></div>")
    if note:
        out.append(f'<p class="tbl-note">{note}</p>')
    return "\n".join(out)


def bar_chart(items, unit="", colour_key="c"):
    """items: list of (label, value, display, colour)"""
    mx = max(abs(v) for _, v, _, _ in items) or 1
    out = ['<div class="bars">']
    for label, v, disp, col in items:
        w = max(2, abs(v) / mx * 100)
        out.append(
            f'<div class="bar-row"><div>{label}</div>'
            f'<div class="bar-track"><div class="bar-fill {col}" style="width:{w:.1f}%"></div></div>'
            f'<div class="bar-val">{disp}</div></div>')
    out.append("</div>")
    return "\n".join(out)


def kpi(value, label, sub, cls=""):
    return (f'<div class="card {cls}"><h3>{label}</h3><div class="big">{value}</div>'
            f'<div class="sub">{sub}</div></div>')


# ----------------------------------------------------------------------------- shell
SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Jack2 — PROP-001 hold / renew / sell analysis</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="site-head">
  <div class="site-head-inner">
    <a class="brand" href="index.html">
      <span class="brand-mark">J2</span>
      <span class="brand-txt"><strong>PROP-001</strong><span>NNN Jack in the Box · central Los Angeles</span></span>
    </a>
    <nav class="nav" aria-label="Site sections">
{nav}
    </nav>
  </div>
</header>
<main>
  <div class="wrap">
{body}
  </div>
</main>
<footer>
  <div class="wrap">
    <div>
      <strong>Jack2</strong> · analytical dossier for <code>PROP-001</code> · data cut-off 2026-11-06<br>
      All identifiers anonymised. No personal or parcel information is stored or published.
    </div>
    <div>
      <a href="methodology.html">Method &amp; sources</a> &middot;
      <a href="flags.html">Flagged for review</a> &middot;
      <a href="https://github.com/wingbangboozle1-lang/Jack2" target="_blank" rel="noopener">Repository</a>
    </div>
  </div>
</footer>
<script src="assets/app.js"></script>
</body>
</html>
"""

PAGES = {}


def page(slug, title, desc, body):
    nav = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == slug else ""
        nav.append(f'      <a href="{href}"{cur}>{label}</a>')
    PAGES[slug] = SHELL.format(title=title, desc=desc, nav="\n".join(nav), body=body)


def pager(slug):
    idx = [h for h, _ in NAV].index(slug)
    out = ['<div class="pager">']
    if idx > 0:
        h, l = NAV[idx - 1]
        out.append(f'<a href="{h}"><div class="dir">&larr; Previous</div><div class="ttl">{l}</div></a>')
    else:
        out.append("<span></span>")
    if idx < len(NAV) - 1:
        h, l = NAV[idx + 1]
        out.append(f'<a href="{h}" style="text-align:right"><div class="dir">Next &rarr;</div><div class="ttl">{l}</div></a>')
    else:
        out.append("<span></span>")
    out.append("</div>")
    return "\n".join(out)


R = PROJ["results"]
UP = PROJ["extension_uplift"]
VOI = PROJ["value_of_information"]
SC = PROJ["scenarios"]
STRATS = ["A_sell_now", "A1_sell_now_1031", "B_expire_sell_vacant", "C_renew_hold", "D_extend_sell_2028"]
SHORT = {"A_sell_now": "A · Sell now, pay tax",
         "A1_sell_now_1031": "A1 · Sell now via §1031",
         "B_expire_sell_vacant": "B · Hold to expiry, sell vacant",
         "C_renew_hold": "C · Renew, hold to 2040",
         "D_extend_sell_2028": "D · Extend now, sell 2028"}
COLOUR = {"A_sell_now": "a", "A1_sell_now_1031": "g", "B_expire_sell_vacant": "r",
          "C_renew_hold": "v", "D_extend_sell_2028": ""}

# ============================================================================= INDEX
strategy_rows = "\n".join(
    f'<tr><td class="metric">{SHORT[k]}</td>'
    f'<td class="num">{R[k]["mean"]:.2f}</td>'
    f'<td class="num">{R[k]["cvar_10pct"]:.2f}</td>'
    f'<td class="num">{R[k]["certainty_equiv_crra3"]:.2f}</td>'
    f'<td class="num">{R[k]["win_rate_pct"]:.1f}%</td>'
    f'<td>{R[k]["vs_A_pct"]:+.1f}%</td></tr>' for k in sorted(STRATS, key=lambda z: -R[z]["certainty_equiv_crra3"]))

index_body = f"""
<section class="hero">
  <div class="eyebrow">Investment decision dossier · anonymised · {FACTS['count']} sourced data points</div>
  <h1>Hold, renew, or sell? A single-tenant NNN Jack in the Box in central Los Angeles</h1>
  <p>Lease described as expiring between 2030 and 2035. This dossier verifies the local economy from official
  sources, prices the lease-term and interest-rate risk, models five courses of action under
  business-as-usual and black-swan conditions, and recommends one.</p>
  <div class="verdict">
    <b>Recommendation:</b> do not let the lease run to expiry. Run a <b>dual track for 6–12 months</b> —
    pursue an early 10–15 year extension <i>and</i> prepare a §1031 sale simultaneously.
    Sell either way; the only question is whether you sell with 13–15 years of term or with 4–9.
  </div>
  <div class="metrics">
    <div><span class="n">{UP['uplift_pct']:.1f}%</span><span class="l">Value from an extension</span></div>
    <div><span class="n">−24.9%</span><span class="l">Value lost to term decay</span></div>
    <div><span class="n">4.90%</span><span class="l">10-yr Treasury</span></div>
    <div><span class="n">+3.72%</span><span class="l">CPI, year over year</span></div>
  </div>
</section>

<h2>At a glance</h2>
<div class="grid g4">
  {kpi("4.90%", "10-year Treasury", "2026-11-04 · up from 4.06% a year ago", "warn")}
  {kpi("3.88%", "Fed funds", "Raised 2026-09-17 · policy easing is over", "warn")}
  {kpi("+0.10%/yr", "LA metro job growth", "Seven-year compound rate · +0.73% total since 2019", "neg")}
  {kpi("−3.2%", "LA County population", "Since the 2020 census base · −322,480 residents", "neg")}
  {kpi("6.85%", "QSR franchisee cap rate", "Q2 2026 · vs 5.85% corporate credit", "warn")}
  {kpi("−4.2%", "JACK system same-store sales", "FY2025 · −7.4% in Q4 FY2025", "neg")}
  {kpi("4.5%", "LA County unemployment", "Sep 2026 · back to 2019 levels", "")}
  {kpi("16,627", "CA structures lost to fire", "2025 · 4 LA County fires ≥5,000 acres", "neg")}
</div>
<p class="small">Every figure above is a link on its detail page. All are Tier 1 official sources
(FRED/BLS, U.S. Census, SEC, CAL FIRE) except the cap rates, which are Tier 3 industry data from
The Boulder Group and are labelled as such.</p>

<h2>The five courses of action, scored</h2>
<p class="lede">Monte-Carlo, 20,000 trials, seed 20261106. Figures are the present value of <b>after-tax</b>
wealth at a common 2040 horizon, per $1.00 of current annual NOI. Multiply by actual NOI for dollars.
Higher is better in every column except the last.</p>
<div class="table-wrap"><table>
<thead><tr><th>Strategy</th><th>Mean</th><th>Worst-decile (CVaR₁₀)</th><th>Risk-adjusted (CE)</th><th>Win rate</th><th>vs. sell &amp; pay tax</th></tr></thead>
<tbody>{strategy_rows}</tbody>
</table></div>
<p class="tbl-note">CVaR₁₀ = average of the worst 10% of outcomes. CE = certainty equivalent under
constant relative risk aversion of 3 — the metric that answers "what certain amount is this risky bet worth to me?"</p>

<div class="callout danger">
  <p><strong>Read the shape, not just the average.</strong> "Renew and hold" wins most often (52.6%) and has the
  highest median. It also has a <strong>worst-decile outcome of 1.88× NOI</strong> against <strong>10.96×</strong> for selling
  via §1031 — <strong>five times worse in the bad state</strong>. That is what a single parcel, single tenant,
  single metro bet looks like. The brief asked for manageable risk and wealth preservation, so the
  risk-adjusted ranking governs, and selling via §1031 wins it.</p>
</div>

<h2>Five findings that drive the answer</h2>
<div class="grid g2">
  <div class="card">
    <h3>01 · Time destroys value mechanically</h3>
    <div class="big">−24.9%</div>
    <div class="sub">Value per $1 of NOI falls from $12.83 today to $9.64 once the lease is inside its final year.
    No rent change, no tenant change, no market change — just the passage of time. Every month the lease runs
    down, that is given away for free.</div>
  </div>
  <div class="card">
    <h3>02 · A signature is worth more than a rate cut</h3>
    <div class="big pos">+{UP['uplift_pct']:.1f}%</div>
    <div class="sub">Extending from ~6.5 years to ~15 years moves the model cap rate from 7.91% to 6.40%:
    the same NOI goes from ${UP['value_now_per_1_noi']:.2f} to ${UP['value_after_per_1_noi']:.2f} per $1 —
    about ${UP['uplift_dollars_at_200k_noi']:,.0f} on a $200,000-NOI asset.</div>
  </div>
  <div class="card">
    <h3>03 · The trade area will not bail it out</h3>
    <div class="big neg">+0.10%/yr</div>
    <div class="sub">LA metro payrolls have grown 0.10% a year for seven years and are 1.2% below their
    October 2024 peak. The county has lost 322,480 residents since 2020. Underwrite <b>zero real NOI growth</b>.</div>
  </div>
  <div class="card">
    <h3>04 · The tenant is retrenching</h3>
    <div class="big neg">2,168 → 2,115</div>
    <div class="sub">Jack in the Box's store count fell across four quarters, with 51 closures in a branded
    block-closure programme. Del Taco was bought for ~$585m and sold for ~$119m. A corporate guaranty is the
    most valuable fact not yet known.</div>
  </div>
  <div class="card">
    <h3>05 · Rates are moving against holding</h3>
    <div class="big warn">4.06% → 5.13%</div>
    <div class="sub">The 10-year Treasury's monthly average rose 107 bp in twelve months; the Fed hiked on
    2026-09-17; the 30-year mortgage is 7.18%. Net-lease cap rates rose to 6.92% in Q3 2026 and the market is
    "resetting to a higher cost of capital rather than waiting for relief."</div>
  </div>
  <div class="card">
    <h3>The $500,000 phone call</h3>
    <div class="big warn">${VOI['value_spread_from_expiry_dollars_at_200k_noi']:,.0f}</div>
    <div class="sub">Moving the assumed expiry from 2030 to 2035 changes value from $11.57 to $14.07 per $1 of
    NOI — a {VOI['value_spread_from_expiry_pct_of_value']:.1f}% swing. Reading the lease costs nothing and is
    worth more than any decision in this dossier.</div>
  </div>
</div>

<h2>Start here</h2>
<div class="grid g3">
  <a class="card" href="decision.html" style="text-decoration:none;color:inherit">
    <h3>Decision</h3><div class="big" style="font-size:18px">The recommendation, in sequence</div>
    <div class="sub">Four steps, a 15-item risk register, a black-swan stress test, and the conditions that would
    make this recommendation wrong.</div></a>
  <a class="card" href="projection.html" style="text-decoration:none;color:inherit">
    <h3>Projection</h3><div class="big" style="font-size:18px">The engine and its distributions</div>
    <div class="sub">Full Monte-Carlo output, scenario replay, term decay, discount-rate and Treasury
    sensitivity, and every assumption written down.</div></a>
  <a class="card" href="economy.html" style="text-decoration:none;color:inherit">
    <h3>Economy</h3><div class="big" style="font-size:18px">Central LA, verified</div>
    <div class="sub">Population, income, jobs, unemployment, retail depth and education — each row linked to
    Census, BLS or FRED.</div></a>
</div>

<div class="callout warn" style="margin-top:26px">
  <p><strong>What this dossier does not know.</strong> No street address, APN, lease document, rent roll or basis
  was supplied, and none is stored — the address was deliberately withheld for privacy. As a result 25 items are
  published as <b>blank and flagged</b> rather than guessed, including the parcel's fire-hazard zone, flood zone,
  seismic class, school assignment, exact expiry, escalations, guarantor and current NOI.
  <a href="flags.html">See everything flagged &rarr;</a></p>
</div>
"""
page("index.html", "Overview",
     "Hold, renew or sell analysis for a single-tenant NNN Jack in the Box in central Los Angeles, built from verified official sources.",
     index_body + pager("index.html"))

# ============================================================================= DECISION
risk_rows = [
    ("R1", "Lease terms unknown — wrong expiry, below-market option, tenant renewal at fixed rent", "Structural", "Certain", "High (~21.6% of value)", "Read the lease; obtain an estoppel", "Do first — blocking"),
    ("R2", "Tenant / franchisee default or non-renewal", "Credit", "Medium (3.5%/yr modelled)", "High", "Corporate or personal guaranty; sell before expiry", "Underwrite the franchisee"),
    ("R3", "Term decay — value falls as the lease shortens", "Structural", "Certain", "High (−24.9% mechanical)", "Extend, or sell before decay compounds", "Timing decision now"),
    ("R4", "Cap-rate expansion from rising rates", "Market", "Elevated", "High (~−6.5% per +55 bp)", "Sell into the move, not after it", "Now"),
    ("R5", "Brand retrenchment at Jack in the Box", "Credit", "Observed, ongoing", "Medium–High", "Price it in; prefer corporate guaranty", "Now"),
    ("R6", "Trade-area stagnation", "Market", "Observed", "Medium", "Underwrite zero real NOI growth", "Now"),
    ("R7", "Wildfire / smoke / power shut-offs", "Catastrophe", "Medium (4%/yr modelled)", "Medium–High", "Insurance covenant; exit exposure", "Verify hazard zone"),
    ("R8", "Seismic event (correlated, region-wide)", "Catastrophe", "Low–Medium (3%/yr)", "High", "Retrofit status; insurance; diversify", "Verify seismic zone"),
    ("R9", "Insurance repricing or non-renewal", "Market", "Medium (6%/yr modelled)", "Medium", "Confirm who bears premium escalation", "Verify lease clause"),
    ("R10", "§1031 execution failure — miss 45/180 days, disqualified QI, touch proceeds", "Tax / process", "Low–Medium", "Very high (full tax acceleration)", "QI engaged before closing; realistic timeline", "Engage QI early"),
    ("R11", "California tax on an out-of-state replacement", "Tax", "Medium if relocating capital", "Medium", "FTB 3840 undertaking; CA opinion", "Unverified — confirm"),
    ("R12", "Concentration — one parcel, one tenant, one metro", "Portfolio", "Certain", "High", "Spread the exchange across ≥2 assets", "Structure the 1031"),
    ("R13", "Entity form, step-up basis, estate plan", "Legal", "Unknown", "Medium–High", "Counsel", "Unverified"),
    ("R14", "Environmental / ADA / entitlement at re-leasing", "Legal", "Low", "Medium", "Phase I ESA; ADA survey", "At exit diligence"),
    ("R15", "Measurement risk in this analysis itself", "Model", "Certain", "Medium", "Every assumption published; sensitivities shown", "Supply the documents"),
]
risk_html = "\n".join(
    f'<tr><td class="num">{i}</td><td class="metric">{m}</td><td>{c}</td><td>{l}</td><td>{s}</td><td>{mit}</td><td>{o}</td></tr>'
    for i, m, c, l, s, mit, o in risk_rows)

bs = SC["black_swan"]["mean"]
sc_rows = "\n".join(
    f'<tr><td class="metric">{SHORT[k]}</td><td class="num">{SC["base"]["mean"][k]:.2f}</td>'
    f'<td class="num">{SC["upside_for_holding"]["mean"][k]:.2f}</td>'
    f'<td class="num">{SC["downside"]["mean"][k]:.2f}</td>'
    f'<td class="num"><b>{bs[k]:.2f}</b></td>'
    f'<td class="num">{SC["black_swan"]["vs_A_pct"][k]:+.1f}%</td></tr>' for k in STRATS)

be_rows = "\n".join(
    f'<tr><td class="num">{b["tsy_terminal_pct"]:.2f}%</td><td class="num">{b["implied_cap_shift_bp"]:+.0f} bp</td>'
    f'<td class="num">{b["A_sell_now"]:.2f}</td><td class="num">{b["C_renew_hold"]:.2f}</td>'
    f'<td class="num">{b["D_extend_sell_2028"]:.2f}</td><td>{SHORT[b["best"]]}</td></tr>'
    for b in PROJ["breakeven"])

decision_body = f"""
<section class="hero">
  <div class="eyebrow">Decision</div>
  <h1>Sell — after trying to buy the term first</h1>
  <p>Do not let this lease run to expiry. Spend four weeks reading the lease and confirming the guarantor,
  six months trying to buy 10–15 more years of term from the franchisor, then go to market — with an extension
  if you got one, without it if you did not. Execute through a §1031 exchange.</p>
  <div class="verdict"><b>Why:</b> the passage of time alone costs about a quarter of the asset's value, the trade
  area is shrinking, the tenant is closing stores, and rates are rising against you.
  The expected cost of doing nothing is larger than the tax bill you are trying to avoid.</div>
</section>

<h2>Why "renew and hold" is not the answer, even though it wins most often</h2>
{bar_chart([(SHORT[k], R[k]["certainty_equiv_crra3"], f"{R[k]['certainty_equiv_crra3']:.2f}", COLOUR[k]) for k in sorted(STRATS, key=lambda z: -R[z]["certainty_equiv_crra3"])])}
<p class="tbl-note">Risk-adjusted score (certainty equivalent, CRRA = 3) per $1.00 of current annual NOI, after all taxes.</p>

<div class="table-wrap"><table>
<thead><tr><th>Strategy</th><th>Mean</th><th>Worst-decile</th><th>Risk-adjusted (CE)</th><th>Win rate</th><th>vs. sell &amp; pay tax</th></tr></thead>
<tbody>{strategy_rows}</tbody></table></div>

<div class="callout">
  <p><strong>The barbell.</strong> Strategy C has the <b>highest median (12.45)</b> and the highest win rate
  (52.6%), and the <b>worst tail by a factor of five</b> (1.88 vs 10.96). It is the correct answer only if the
  Owner can absorb the bottom decile without changing their standard of living. If not, it is the wrong
  answer, and the certainty-equivalent ranking — which is what "preservation of wealth with manageable risk"
  means in arithmetic — selects A1.</p>
</div>

<h2>Four steps, in order</h2>
<h3>Step 0 — Resolve the unknowns (weeks 0–4, cost ≈ $0)</h3>
<ol class="tight">
  <li><b>The lease</b>, redacted. Exact expiry, escalations, options (who holds them and at what rent), guarantor,
  landlord obligations, and any kick-out right.</li>
  <li><b>The estoppel certificate</b> from the tenant — the same document a buyer will demand.</li>
  <li><b>The franchisee's</b> identity and financial standing, and whether a Jack in the Box Inc. corporate
  guaranty exists.</li>
  <li>Current <b>rent roll, CAM reconciliations, tax bill and insurance binder</b>.</li>
</ol>
<div class="callout ok"><p><strong>Expected value of this step: ~${VOI['value_spread_from_expiry_dollars_at_200k_noi']:,.0f}</strong>
({VOI['value_spread_from_expiry_pct_of_value']:.1f}% of the 2030-expiry value, on a $200,000-NOI asset).
It is the highest-return action available by an enormous margin.</p></div>

<h3>Step 1 — Test the extension (months 1–6)</h3>
<p>Propose a <b>10–15 year extension</b> and expect to pay for it. The model assumes a 4% rent concession and only a
<b>{VOI['extend_agreement_rate_pct']:.0f}% probability</b> the franchisor agrees at all; both are assumptions and both
are the swing factors in strategy D.</p>
<ul class="tight">
  <li>If achievable at <b>≤ 8% rent concession</b>, take it. That is still a large net gain against the
  {UP['uplift_pct']:.1f}% term premium.</li>
  <li>If the franchisor wants <b>&gt; 15%</b>, or a below-market option, walk. You would be transferring the
  premium to the tenant rather than creating it for the Owner.</li>
</ul>

<h3>Step 2 — Sell, in either case (months 6–18)</h3>
<p>With an extension signed, market the asset with <b>~13–15 years of term</b> (strategy D, the second-best
risk-adjusted outcome at {R['D_extend_sell_2028']['certainty_equiv_crra3']:.2f}). Without one, market it <b>as-is</b> into the
private-capital and §1031 buyer pool — the deepest bid for sub-$10m net-lease product.</p>

<h3>Step 3 — Execute the §1031 exchange properly</h3>
<ul class="tight">
  <li>Engage a <b>qualified intermediary before closing</b>. Under IRC §1031 the Owner cannot touch proceeds and
  cannot act as their own facilitator.</li>
  <li><b>45-day identification / 180-day completion.</b> Not extendable except in a presidentially declared
  disaster. A missed deadline converts the entire deferred gain into a fully taxable one.</li>
  <li><b>California caution (flagged):</b> California does not defer California-source gain when replacement
  property sits outside California without an undertaking to file a California return when the replacement is later
  sold (FTB Form 3840). <b>Not verified in this session</b> — get an opinion before identifying replacement property
  if the plan is to leave California.</li>
  <li>Spread proceeds across <b>at least two assets</b> to break the single-parcel concentration.</li>
</ul>

<h3>Step 4 — Hold only if every one of these is true</h3>
<ul class="checklist">
  <li>The lease is <b>absolute net</b> with a <b>corporate guaranty</b></li>
  <li>Escalations are <b>≥ 2%/yr</b> — a flat lease during 3.72% inflation is a guaranteed real-terms loss</li>
  <li>The extension is <b>≥ 15 years at market rent</b> with no tenant-held renewal option</li>
  <li>This asset is a <b>small fraction</b> of the Owner's net worth</li>
  <li>The Owner can absorb a worst-decile outcome (≈ <b>1.88× NOI</b> vs ≈ 11× if selling)</li>
</ul>
<p>If even one box is unchecked, the hold case fails on the model's own numbers.</p>

<hr>

<h2>Risk register</h2>
<p class="lede">Fifteen risks, each with a likelihood judged from the verified evidence in the other sections,
a severity measured in the model, and the action that actually mitigates it.</p>
<div class="table-wrap"><table>
<thead><tr><th>#</th><th>Risk</th><th>Category</th><th>Likelihood</th><th>Severity</th><th>Mitigation</th><th>Owner action</th></tr></thead>
<tbody>{risk_html}</tbody></table></div>

<h2>Scenario replay</h2>
<div class="table-wrap"><table>
<thead><tr><th>Strategy</th><th>Base</th><th>Upside for holding</th><th>Downside</th><th>Black swan</th><th>Black swan vs sell-and-pay-tax</th></tr></thead>
<tbody>{sc_rows}</tbody></table></div>
<p class="tbl-note">Each scenario replays 5,000 Monte-Carlo paths. The black swan is a joint shock: 10-year
Treasury to 6.90%, zero rent growth, 25% renewal probability, 4.5% sale costs and land value at 6.5× NOI.</p>

<div class="callout danger">
  <p><strong>The ranking survives the bad state of the world.</strong> In the black-swan replay, holding loses
  <b>{abs(SC['black_swan']['vs_A_pct']['C_renew_hold']):.1f}%</b> relative to selling and paying the tax.
  The recommendation does not flip — and it survives precisely <i>because</i> it removes exposure early.</p>
</div>

<div class="callout warn">
  <p><strong>Control test.</strong> With the catastrophe and default priors switched off, renew-and-hold rises to
  {PROJ['no_hazard']['C_renew_hold']:.2f} from {R['C_renew_hold']['mean']:.2f}. Its apparent attractiveness comes entirely from the
  benign half of the distribution. That is the definition of tail risk, and it is why the certainty-equivalent
  ranking, not the mean, is the right basis for this decision.</p>
</div>

<h2>Break-even: what would have to be true for holding to win?</h2>
<div class="table-wrap"><table>
<thead><tr><th>Terminal 10-yr Treasury</th><th>Implied cap-rate shift</th><th>A · Sell now</th><th>C · Renew &amp; hold</th><th>D · Extend &amp; sell</th><th>Best</th></tr></thead>
<tbody>{be_rows}</tbody></table></div>
<div class="callout ok">
  <p><strong>This is not a rates call.</strong> Across a 350 bp range of terminal 10-year Treasury — 3.50% to 7.00%
  — selling via §1031 ranks first every time. The dominant terms are the <i>term premium capture</i> and the
  <i>removal of single-asset tail risk</i>, not the discount rate.</p>
</div>
<p>Where the answer does flip is the Owner's <b>discount rate</b>: at 6% the best strategy becomes
<b>D — extend, then sell</b>, because an Owner with a low opportunity cost of capital should keep the asset long
enough to capture the extension premium before selling. At 7% and above, A1 leads.</p>

<h2>What would make this recommendation wrong</h2>
<ol class="tight">
  <li><b>The lease is absolute-net, corporate-guaranteed, with 3%/yr bumps and a market-rent renewal option.</b>
  Then the asset is better than modelled — and that strengthens <i>extend-then-sell</i>, not hold-to-expiry.</li>
  <li><b>The true basis is much higher than assumed.</b> A high basis lowers the tax on sale toward zero, which
  raises plain selling (A) above the §1031 route and makes selling outright even more attractive.</li>
  <li><b>There is a below-market strategic buyer</b> — the franchisee, or an adjacent owner — willing to pay well
  above market. The model assumes an arm's-length sale.</li>
  <li><b>There is a genuine redevelopment play.</b> A central-LA infill drive-thru parcel can be worth more as
  land for housing under current state law than as a 6.5%-cap QSR. <b>This is the largest un-quantified upside in
  the dossier</b> and could not be tested without an address. Long-term renewal would extinguish the option, so it
  must be tested <i>before</i> signing anything.</li>
  <li><b>An estate-planning reason to hold to death</b> for a basis step-up. Not modelled, and appropriately so —
  it depends on facts this dossier should not hold.</li>
</ol>
"""
page("decision.html", "Decision",
     "The recommendation, a 15-item risk register, black-swan stress test and break-even analysis.",
     decision_body + pager("decision.html"))

# ============================================================================= PROJECTION
curve_rows = "\n".join(
    f'<tr><td class="num">{c["term_years"]:.1f} yr</td><td class="num">{c["cap_pct"]:.2f}%</td>'
    f'<td class="num">${c["value_per_1_noi"]:.2f}</td></tr>' for c in PROJ["cap_term_curve"])

decay_rows = "\n".join(
    f'<tr><td class="num">{d["year"]}</td><td class="num">{d["remaining_term_years"]:.2f}</td>'
    f'<td class="num">{d["cap_pct"]:.2f}%</td><td class="num">${d["value_per_1_noi"]:.2f}</td></tr>'
    for d in PROJ["term_decay"])

exp_rows = "\n".join(
    f'<tr><td class="num">{e["expiry_year"]}</td><td class="num">{e["remaining_term_years"]:.2f}</td>'
    f'<td class="num">{e["cap_now_pct"]:.2f}%</td><td class="num">${e["value_now_per_1_noi"]:.2f}</td>'
    f'<td class="num">{e["mean"]["A_sell_now"]:.2f}</td><td class="num">{e["mean"]["C_renew_hold"]:.2f}</td>'
    f'<td class="num">{e["mean"]["D_extend_sell_2028"]:.2f}</td></tr>' for e in PROJ["expiry_sensitivity"])

disc_rows = "\n".join(
    f'<tr><td class="num">{d["discount_rate_pct"]:.0f}%</td>'
    + "".join(f'<td class="num">{d[k]:.2f}</td>' for k in STRATS)
    + f'<td>{SHORT[d["best"]]}</td></tr>' for d in PROJ["discount_sensitivity"])

dist_items = [(SHORT[k], R[k]["p50"], f"{R[k]['p10']:.1f} – {R[k]['p90']:.1f}", COLOUR[k]) for k in sorted(STRATS, key=lambda z: -R[z]["p50"])]

assump_rows = [
    ("Lease expiry (Owner-stated range)", "2030 – 2035, drawn uniform", "The range is the Owner's description, not a document"),
    ("Rent escalation", "0% / 1% / 1.5% / 2% / 2.5% / 3%, drawn", "Lease not supplied — drawn from a plausible set"),
    ("Renewal probability at expiry", "70%", "Franchised JACK unit in a viable trade area"),
    ("Renewal rent concession", "4%", "Concession a franchisor extracts for signing"),
    ("Market rent growth after expiry", f"2.5% ± 1.0%", "Long-run central-LA retail rent growth"),
    ("Vacancy if not renewed", "1.5 years", "Re-leasing time for a second-generation QSR box"),
    ("Re-leasing cost", "6% of new annual rent + 3 months free", "Commission plus tenant improvement"),
    ("Sale costs", "2.5% – 4.5%, drawn", "Commission, closing costs, transfer taxes"),
    ("Cap-rate beta to the 10-year", "0.35 – 0.75, drawn", "Empirical sensitivity of cap rates to rates"),
    ("Terminal 10-yr Treasury", "4.60% ± 0.90%, drawn", "Base case; the break-even table spans 3.5%–7.0%"),
    ("Discount rate", "8.0%", "Owner's after-tax opportunity cost; sensitivity at 6%–10%"),
    ("Reinvestment return", "= discount rate", "Deliberately no free lunch"),
    ("Original basis", "6.0 × current NOI", "Not supplied — stated so it can be replaced"),
    ("Accumulated depreciation", "22% of basis", "Not supplied"),
    ("California state tax rate", "13.3%", "Assumption — flagged, not re-verified this session"),
    ("Extension probability", "55%", "Will the franchisor sign 10–15 years now?"),
    ("Extension rent change", "−2% ± 2.5%, drawn", "Typical concession"),
    ("Land / vacant value", "6 – 10 × current NOI, drawn", "Not verified — no parcel data"),
]
assump_html = "\n".join(f'<tr><td class="metric">{a}</td><td class="num">{b}</td><td>{c}</td></tr>' for a, b, c in assump_rows)

hz = PROJ["hazard_assumptions"]
hazard_html = f"""
<tr><td class="metric">Regional wildfire / smoke / power shut-off</td><td class="num">{hz['wildfire_annual_prob']*100:.0f}% / yr</td>
<td>NOI −{hz['wildfire_noi_hit'][0]*100:.0f}% to −{hz['wildfire_noi_hit'][1]*100:.0f}% in the event year; cap rate +{hz['wildfire_cap_add_bp'][0]:.0f}–{hz['wildfire_cap_add_bp'][1]:.0f} bp for 2 years</td></tr>
<tr><td class="metric">Significant seismic event felt in the metro</td><td class="num">{hz['seismic_annual_prob']*100:.0f}% / yr</td>
<td>{hz['seismic_abate_share'][0]*100:.0f}–{hz['seismic_abate_share'][1]*100:.0f}% of gross rent abated for {hz['seismic_months'][0]}–{hz['seismic_months'][1]} months</td></tr>
<tr><td class="metric">Insurance shock (premium doubling / non-renewal)</td><td class="num">{hz['insurance_shock_annual_prob']*100:.0f}% / yr</td>
<td>Cap rate +{hz['insurance_shock_cap_add_bp']:.0f} bp for 3 years</td></tr>
<tr><td class="metric">Tenant default / franchisee insolvency (while leased)</td><td class="num">{hz['tenant_default_annual_rate']*100:.1f}% / yr</td>
<td>Rent stops; no renewal follows</td></tr>
"""

projection_body = f"""
<section class="hero">
  <div class="eyebrow">Projection engine</div>
  <h1>20,000 paths, five strategies, every assumption published</h1>
  <p><code>model/projection_model.py</code> · Python 3 standard library only · seed <code>{PROJ['results']['_meta']['seed']}</code>
  · term of art: all outputs are multiples of <b>current annual NOI</b>, after all federal and California taxes,
  so the Owner's actual rent never has to be disclosed.</p>
</section>

<h2>The core identity</h2>
<p class="lede"><b>Value = NOI ÷ cap rate.</b> Only two things can move value. For this asset the NOI is
contractually fixed by a NNN lease, so the landlord has almost no lever there. The cap rate is therefore the
dominant variable — and remaining lease term feeds directly into it, because net-lease buyers pay for the
durability of cash flow. That is why time itself is a cost here.</p>

<h2>The cap-rate term curve</h2>
<p class="lede">No Jack-in-the-Box-specific cap rate could be verified, so the curve is <b>derived</b> from The
Boulder Group's QSR observations and labelled as derived everywhere it appears. The 10-year point is a direct
anchor: the franchisee-QSR average of 6.85%.</p>
<div class="table-wrap"><table>
<thead><tr><th>Remaining term</th><th>Model cap rate</th><th>Value per $1.00 of NOI</th></tr></thead>
<tbody>{curve_rows}</tbody></table></div>
<p class="tbl-note" id="cap-curve">Construction: (0 yr, 10.50%) → (3, 9.00%) → (7, 7.75%) → (10, 6.85%, direct
Boulder anchor) → (15, 6.40%) → (30, 6.20%), piecewise-linear. The 15-year point sits 45 bp inside the
franchisee average for full-term durability, but well outside premium-brand 15-year comps (Raising Cane's
4.90–5.20%, Whataburger 4.85–5.25%) because JACK is a materially weaker credit than either.</p>

<h2>Term decay: the cost of waiting, with nothing else changing</h2>
{bar_chart([(str(d['year']), d['value_per_1_noi'], f"${d['value_per_1_noi']:.2f}", "r") for d in PROJ['term_decay']])}
<div class="table-wrap"><table>
<thead><tr><th>Year</th><th>Remaining term (to midpoint expiry)</th><th>Model cap rate</th><th>Value per $1.00 of NOI</th></tr></thead>
<tbody>{decay_rows}</tbody></table></div>
<div class="callout danger"><p><strong>−24.9% from pure passage of time.</strong> $12.83 today, $9.64 once the lease
is inside its final year. No rent change, no tenant change, no market change. This is the single largest
self-inflicted cost in every "hold" strategy, and it is why strategy B is dominated.</p></div>

<h2>Result distribution</h2>
<p class="lede">Bars show the median; the range shown is the 10th to 90th percentile.</p>
{bar_chart(dist_items)}
<div class="table-wrap"><table>
<thead><tr><th>Strategy</th><th>Mean</th><th>p10</th><th>Median</th><th>p90</th><th>Worst-decile</th><th>Risk-adjusted (CE)</th><th>Win rate</th></tr></thead>
<tbody>
{''.join(f'<tr><td class="metric">{SHORT[k]}</td><td class="num">{R[k]["mean"]:.2f}</td><td class="num">{R[k]["p10"]:.2f}</td><td class="num">{R[k]["p50"]:.2f}</td><td class="num">{R[k]["p90"]:.2f}</td><td class="num">{R[k]["cvar_10pct"]:.2f}</td><td class="num">{R[k]["certainty_equiv_crra3"]:.2f}</td><td class="num">{R[k]["win_rate_pct"]:.1f}%</td></tr>' for k in STRATS)}
</tbody></table></div>

<h2>The extension premium</h2>
<div class="grid g3">
  {kpi(f"{UP['cap_now_pct']:.2f}% → {UP['cap_after_extension_pct']:.2f}%", "Cap rate", "Same NOI, same tenant, more term")}
  {kpi(f"${UP['value_now_per_1_noi']:.2f} → ${UP['value_after_per_1_noi']:.2f}", "Value per $1 of NOI", f"+{UP['uplift_pct']:.1f}%", "pos")}
  {kpi(f"${UP['uplift_dollars_at_200k_noi']:,.0f}", "Uplift at $200k NOI", "Created by a signature", "pos")}
</div>
<div class="callout ok"><p>A <b>{UP['uplift_pct']:.1f}%</b> uplift from negotiation is worth more than any plausible
interest-rate move. That is the whole argument for strategy D.</p></div>

<h2>Expiry-date sensitivity</h2>
<p class="lede">The Owner gave a five-year range. This is what that ambiguity is worth.</p>
<div class="table-wrap"><table>
<thead><tr><th>Expiry</th><th>Remaining term</th><th>Cap rate today</th><th>Value per $1 NOI</th><th>A · Sell now</th><th>C · Renew &amp; hold</th><th>D · Extend &amp; sell</th></tr></thead>
<tbody>{exp_rows}</tbody></table></div>
<div class="callout warn"><p><strong>${VOI['value_spread_from_expiry_dollars_at_200k_noi']:,.0f} of value
({VOI['value_spread_from_expiry_pct_of_value']:.1f}%) rides on a date nobody has looked up.</strong> Note also that a
shorter remaining term makes selling <i>more</i> attractive, not less — because the hold has less term left to
harvest and the same tail risk.</p></div>

<h2>Discount-rate sensitivity</h2>
<div class="table-wrap"><table>
<thead><tr><th>Discount rate</th>{''.join(f'<th>{SHORT[k].split(" · ")[0]}</th>' for k in STRATS)}<th>Best</th></tr></thead>
<tbody>{disc_rows}</tbody></table></div>
<p class="tbl-note">At a low opportunity cost of capital (6%), an Owner should capture the extension premium before
selling. At 7% and above, selling via §1031 leads. This is the one input that changes the ranking.</p>

<h2>Assumptions</h2>
<p class="lede">Everything below is an <b>assumption</b>, not a fact. They are published so they can be
challenged and replaced with the real lease.</p>
<div class="table-wrap"><table>
<thead><tr><th>Input</th><th>Value used</th><th>Rationale / status</th></tr></thead>
<tbody>{assump_html}</tbody></table></div>

<h3 id="hazard-model">Catastrophe and black-swan priors</h3>
<div class="table-wrap"><table>
<thead><tr><th>Event</th><th>Annual probability</th><th>Modelled impact</th></tr></thead>
<tbody>{hazard_html}</tbody></table></div>
<p class="tbl-note">These are the model's stated priors, <b>not official statistics</b>, and are drawn from the
hazard profile documented on the <a href="hazards.html">Risk</a> page. Every run is reported both with and without
this layer so its influence is visible.</p>

<h2>Illustrative tax waterfall on a sale at today's value</h2>
<div class="table-wrap"><table>
<thead><tr><th>Line</th><th>Per $1.00 of current NOI</th><th>Note</th></tr></thead>
<tbody>
<tr><td class="metric">Gross sale price</td><td class="num">{PROJ['tax_waterfall_example']['price']:.4f}</td><td>NOI ÷ cap rate at ~6.5 years remaining</td></tr>
<tr><td class="metric">Less sale costs</td><td class="num">3.0%</td><td>Commission, closing, transfer taxes</td></tr>
<tr><td class="metric">Adjusted basis</td><td class="num">{PROJ['tax_waterfall_example']['adjusted_basis']:.4f}</td><td>Basis 6.00 less 22% accumulated depreciation</td></tr>
<tr><td class="metric">Total gain</td><td class="num">{PROJ['tax_waterfall_example']['total_gain']:.4f}</td><td></td></tr>
<tr><td class="metric">— of which unrecaptured §1250 recapture</td><td class="num">{PROJ['tax_waterfall_example']['recapture_1250']:.4f}</td><td>Federal max 25% (IRS Topic 409)</td></tr>
<tr><td class="metric">Federal tax on recapture</td><td class="num">{PROJ['tax_waterfall_example']['fed_recapture_tax']:.4f}</td><td>1.32 × 25%</td></tr>
<tr><td class="metric">— of which long-term appreciation</td><td class="num">{PROJ['tax_waterfall_example']['appreciation_gain']:.4f}</td><td>Federal 20% + 3.8% NIIT</td></tr>
<tr><td class="metric">Federal tax on appreciation</td><td class="num">{PROJ['tax_waterfall_example']['fed_appreciation_tax']:.4f}</td><td></td></tr>
<tr><td class="metric">California tax</td><td class="num">{PROJ['tax_waterfall_example']['ca_tax']:.4f}</td><td>13.3% assumption — flagged</td></tr>
<tr><td class="metric"><b>Total tax</b></td><td class="num"><b>{PROJ['tax_waterfall_example']['total_tax']:.4f}</b></td><td><b>{PROJ['tax_waterfall_example']['effective_rate_on_price_pct']:.1f}% of price</b></td></tr>
</tbody></table></div>

<h2>Reproducibility</h2>
<p>Run <code>python3 model/projection_model.py</code>. The RNG seed is fixed at {PROJ['results']['_meta']['seed']},
so the output JSON is byte-identical on every run. The engine uses no third-party libraries and no network access.</p>
"""
page("projection.html", "Projection Model",
     "Monte-Carlo projection engine: cap-rate term curve, term decay, scenarios, sensitivity and assumptions.",
     projection_body + pager("projection.html"))

# ============================================================================= ECONOMY
econ_body = f"""
<section class="hero">
  <div class="eyebrow">Local economy &amp; demographics</div>
  <h1>Central Los Angeles: a deep, mature, <em>shrinking</em> market</h1>
  <p>The brief asked for population growth, income levels, school systems, job growth and every factor that could
  influence the local economy. The verified answer contradicts the usual assumption: population is falling and job
  growth has been flat for seven years. Every row below links to its official source.</p>
  <div class="verdict"><b>Underwrite zero real NOI growth.</b> This market is deep enough to keep a well-located QSR
  box productive, and too stagnant to justify holding a decaying lease for a premium.</div>
</section>

<h2>Employment: flat for seven years, and falling for two</h2>
<div class="grid g4">
  {kpi("6,282.1k", "Metro payrolls", "Sep 2026 · seasonally adjusted", "")}
  {kpi("+0.48%", "Year over year", "vs Sep 2025", "")}
  {kpi("−1.22%", "From the Oct-2024 peak", "−77,500 jobs", "neg")}
  {kpi("+0.10%/yr", "Seven-year compound", "Sep 2019 → Sep 2026", "neg")}
</div>
<div class="callout danger">
  <p><strong>The most important economic finding in this dossier.</strong> The Los Angeles metro has added
  <b>45,400 jobs in seven years — 0.10% per year.</b> With a labour force of roughly five million, that is
  effectively full stall for most of a decade, and employment is now <b>1.2% below its October 2024 peak</b>.</p>
</div>
<p>The unemployment rate of 4.5% in September 2026 looks healthy in isolation — and is back to its 2019 level.
Read alongside a declining population and flat payrolls, the benign interpretation is that people have left the
labour force, not that hiring is strong.</p>
{facts_table(["economy"], note="Source: FRED series SMU06310800000000001 (BLS Current Employment Statistics) and CALOSA7URN (BLS LAUS); Census QuickFacts for County Business Patterns.", table_id="tbl-econ")}

<h2>Population: declining, not growing</h2>
<div class="grid g4">
  {kpi("9,694,934", "LA County population", "1 Jul 2025 estimate", "")}
  {kpi("−3.2%", "Since the 2020 base", "−322,480 residents", "neg")}
  {kpi("3,869,089", "LA city population", "1 Jul 2025 estimate", "")}
  {kpi("−0.8%", "City, since 2020 base", "", "neg")}
</div>
<div class="callout warn">
  <p><strong>QSR revenue is roughly traffic × ticket × capture rate.</strong> A county that has shed 322,480
  residents is a county shedding customers, before any price effect. This is a mature, slowly contracting market —
  not a growth market.</p>
</div>

<h2>Income, affordability and the customer</h2>
<p class="lede">A $90,112 county median household income looks strong until it is set against an $834,200 median
home value — a <b>~9.3× price-to-income ratio</b> — and $1,954 median monthly rent. Households in the lower half of
the distribution are structurally squeezed, and those households are the Jack in the Box customer. JACK's own
management attributed FY2025 sales weakness to lower-income and Hispanic consumers pulling back.</p>

<h2>Spending depth</h2>
<p class="lede">Los Angeles County recorded <b>$213.9 billion</b> of retail sales in 2022 — <b>$22,010 per
resident</b> — and <b>$44.0 billion</b> of accommodation and food services sales. That is a deep market: a single
unit doing $1.5–2.5 million is a rounding error, which is why a departing tenant can eventually be replaced. It
also means the market will not grow the box for you.</p>

{bar_chart([("LA County", 22010, "$22,010", ""), ("LA city", 21281, "$21,281", "v")])}
<p class="tbl-note">Retail sales per capita, 2022 Economic Census. Bars are absolute values.</p>

<h2>Education</h2>
<p class="lede">36.0% of county adults hold a bachelor's degree or higher — above the national figure, and positive
for daytime professional traffic. <b>School quality is deliberately not assessed:</b> the assigned attendance area
cannot be determined without the address, so no claim is made. For a QSR the more relevant education-linked
number is household formation, which is why the 19.2% under-18 share is reported.</p>

<h2>All demographic rows</h2>
{facts_table(["demographics"], note="Vintage matters: the population rows are Census Vintage-2025 estimates as of 1 July 2025; income, education and housing rows are 2020–2024 five-year ACS. They are not directly comparable to each other.", table_id="tbl-demo")}

<h2>Reading the trade area honestly</h2>
<div class="table-wrap"><table>
<thead><tr><th>Driver</th><th>Verified direction</th><th>Weight in QSR demand</th><th>Verdict for PROP-001</th></tr></thead>
<tbody>
<tr><td class="metric">Population</td><td>Declining (county −3.2%, city −0.8% since 2020)</td><td>Very high</td><td>Negative</td></tr>
<tr><td class="metric">Job growth</td><td>Flat (+0.10%/yr over seven years; −1.2% from peak)</td><td>High</td><td>Negative</td></tr>
<tr><td class="metric">Unemployment</td><td>4.5% — back to 2019 levels</td><td>Medium</td><td>Neutral</td></tr>
<tr><td class="metric">Household income</td><td>$90,112 median, but ~9.3× price-to-income</td><td>High</td><td>Neutral</td></tr>
<tr><td class="metric">Retail depth</td><td>$22,010 retail sales per capita</td><td>High</td><td>Positive</td></tr>
<tr><td class="metric">Educational attainment</td><td>36.0% bachelor's or higher</td><td>Low</td><td>Mild positive</td></tr>
<tr><td class="metric">Household size</td><td>2.81 persons per household</td><td>Low</td><td>Neutral</td></tr>
<tr><td class="metric">Daytime employment density</td><td class="blank">— requires address</td><td>High</td><td>Unverified</td></tr>
</tbody></table></div>
<div class="callout"><p><strong>Net verdict:</strong> the trade area does not support a growth thesis. It supports a
<em>stability</em> thesis — a mature, deep market that will keep a well-located box productive but will not lift
sales enough to justify holding a decaying lease for a premium. This is the analytical hinge for the
recommendation.</p></div>
"""
page("economy.html", "Economy",
     "Verified Central Los Angeles economy and demographics: jobs, population, income, retail depth, education.",
     econ_body + pager("economy.html"))

# ============================================================================= TENANT
tenant_body = f"""
<section class="hero">
  <div class="eyebrow">Tenant &amp; brand</div>
  <h1>Jack in the Box Inc.: a deleveraging brand that is closing stores</h1>
  <p>SEC filings only. In a single-tenant NNN deal the landlord does not run a restaurant — it owns a claim on one
  operator's rent, and that claim fails in two ways: the store stops working, or the operator runs out of money.
  JACK's own filings show both modes are currently live.</p>
  <div class="verdict"><b>This does not make the asset unsellable.</b> It sets the price and the probability of
  renewal. It is also a reason to price the asset against the <b>franchisee-QSR</b> cap rate (6.85%) rather than
  the corporate rate (5.85%).</div>
</section>

<div class="grid g4">
  {kpi("−4.2%", "FY2025 system same-store sales", "vs −1.3% in FY2024", "neg")}
  {kpi("−7.4%", "Q4 FY2025 same-store sales", "Worst since the Great Recession", "neg")}
  {kpi("2,168 → 2,115", "Store count in four quarters", "51 closures in one block programme", "neg")}
  {kpi("−$470m", "Del Taco round trip", "Bought ~$585m, sold ~$119m", "neg")}
</div>

<h2>The trend turned, but did not recover</h2>
<p class="lede">Same-store sales fell more than 7% in two consecutive FY2025 quarters, then stabilised to roughly
−1% in FY2026. Q3 FY2026 system same-store sales were −1.1% with systemwide sales −1.4%. The store base continues
to contract every quarter, and guidance is for it to contract again for the full year.</p>
{bar_chart([("FY2024 system SSS", 1.3, "−1.3%", "a"), ("FY2025 system SSS", 4.2, "−4.2%", "r"), ("Q4 FY2025 SSS", 7.4, "−7.4%", "r"), ("Q3 FY2026 SSS", 1.1, "−1.1%", "a")])}
<p class="tbl-note">Absolute magnitude of same-store sales declines. Directional only — these are declines, not gains.</p>

<h2>Store base and guidance</h2>
{facts_table(["tenant"], note="Source: Form 10-K for the fiscal year ended 2025-09-28 (filed 2025-11-19); Q4 &amp; FY2025 earnings release; Q3 FY2026 results on Form 8-K.", table_id="tbl-tenant")}

<h2>What the corporate actions tell you</h2>
<p class="lede">The Del Taco round trip is the cleanest read on management's priorities: a ~$585 million
acquisition liquidated for ~$119 million three years later, alongside eliminated dividends and a shrinking store
base. That is a <b>deleveraging, retrenching</b> strategy, executed under a programme called "JACK on Track" that
explicitly included block restaurant closures.</p>
<div class="grid g2">
  <div class="card pos">
    <h3>Why retrenchment helps the landlord</h3>
    <div class="sub">An asset-light JACK needs <em>franchised</em> units to generate royalty streams. Closing a
    profitable, rent-paying central-LA store is value-destructive to the franchisor too, so a rational franchisor
    protects viable urban units.</div>
  </div>
  <div class="card neg">
    <h3>Why it hurts the landlord</h3>
    <div class="sub">The block-closure programme proves the company will close stores in bulk when unit economics
    disappoint — and closures are decided at brand level, not by the landlord. The store base fell 2.4% in four
    quarters.</div>
  </div>
</div>

<div class="callout danger">
  <p><strong>The most valuable unknown: is there a corporate guaranty?</strong> 93.0% of the system is franchised
  (1,966 of 2,115 units), so the tenant of record is <em>likely</em> a franchisee — but that is an inference, not a
  verified fact for this parcel. Boulder Group prices franchisee QSR paper at <b>6.85%</b> against <b>5.85%</b> for
  corporate credit: a 100 bp spread worth roughly 15% of value. Confirm this before pricing the asset.</p>
</div>

<h2>Not verifiable in this session</h2>
<ul class="tight">
  <li><b>Site-level AUV and P&amp;L</b> for PROP-001 — the single best predictor of whether the store renews. Requires
  the franchisee's redacted P&amp;L or franchisor site data.</li>
  <li><b>Whether the tenant of record is corporate or franchisee.</b></li>
  <li><b>Whether a corporate guaranty exists.</b></li>
  <li><b>The franchisee's own financial condition</b> — franchisee distress is the modal default path in QSR net lease.</li>
  <li><b>A Jack-in-the-Box-specific net-lease cap rate</b> — Boulder's Q3 2026 Tenant Profiles covers 88 operators but
  a JACK-specific range was not retrieved.</li>
</ul>
<p>All five are listed on the <a href="flags.html">Flagged for Review</a> page.</p>
"""
page("tenant.html", "Tenant",
     "Jack in the Box Inc. from SEC filings: same-store sales, store count, guidance, Del Taco divestiture.",
     tenant_body + pager("tenant.html"))

# ============================================================================= CAPITAL MARKETS
cm_body = f"""
<section class="hero">
  <div class="eyebrow">Capital markets</div>
  <h1>Rates rising, inflation re-accelerating, cap rates resetting upward</h1>
  <p>A net-lease asset is a bond with a building attached. The 10-year Treasury has risen 107 bp in twelve months,
  the Federal Reserve has stopped cutting and hiked, the 30-year mortgage is above 7%, and net-lease cap rates rose
  to 6.92% in Q3 2026. This is not an environment to wait for relief in.</p>
  <div class="verdict"><b>Every +55 bp of cap-rate expansion costs about 6.5% of value.</b> The market is moving in
  that direction, not away from it.</div>
</section>

<h2>Rates</h2>
<div class="grid g4">
  {kpi("4.90%", "10-year Treasury", "2026-11-04", "warn")}
  {kpi("5.13%", "10-yr monthly average", "Oct 2026 · 4.06% a year earlier", "warn")}
  {kpi("3.88%", "Fed funds", "Hiked 2026-09-17", "warn")}
  {kpi("7.18%", "30-year mortgage", "Week of 2026-11-05 · 6.16% in January", "warn")}
</div>
{bar_chart([("Jul 2020 low", 62, "0.62%", "g"), ("2019 average", 214, "2.14%", "g"), ("Oct 2025", 406, "4.06%", "a"), ("Oct 2026", 513, "5.13%", "r")])}
<p class="tbl-note">10-year Treasury constant-maturity, monthly averages in basis points. The series has moved from
a 0.62% cycle low to 5.13%.</p>

<div class="callout warn">
  <p><strong>The policy turn.</strong> The effective funds rate went 4.33% (May 2025) → 4.08% (Sep 2025) → 3.87%
  (Oct 2025) → 3.64% (Dec 2025), then <b>held for eight months and was raised to 3.88% on 2026-09-17</b>. CPI is
  running at <b>+3.72% year over year</b> on the September 2026 print, up from a disinflationary trend.
  The easing cycle is over.</p>
</div>

<h2>Cap rates</h2>
<div class="callout">
  <p><strong>Source note.</strong> The cap-rate data below is <span class="badge t3">T3 Industry</span> — The Boulder
  Group, a brokerage. It is the best available <em>market pricing</em> signal and it is <b>not</b> an official
  statistic. Every row is badged accordingly. No cap rate is asserted as a fact about this asset.</p>
</div>
{facts_table(["capital-markets"], note="Tier 1 rows are official (FRED, U.S. Treasury, BLS). Tier 3 rows are Boulder Group research and are directional only.", table_id="tbl-cm")}

<h2>The four facts that matter most</h2>
<div class="grid g2">
  <div class="card">
    <h3>1 · Corporate vs franchisee is ~100 bp</h3>
    <div class="big" style="font-size:22px">5.85% vs 6.85%</div>
    <div class="sub">If PROP-001's tenant is a franchisee without a corporate guaranty, its pricing anchor is the
    6.85% line — not 5.85%. That is roughly 15% of value.</div>
  </div>
  <div class="card">
    <h3>2 · Term is worth a lot</h3>
    <div class="big" style="font-size:22px">~105 bp</div>
    <div class="sub">7-Eleven prices 5.90–6.20% at 5 years and 4.80–5.15% at 15 years. Identical credit, ~17% more
    value for the same NOI, purely from term.</div>
  </div>
  <div class="card">
    <h3>3 · Weakness is repriced brutally and fast</h3>
    <div class="big" style="font-size:22px">8.50–8.90%</div>
    <div class="sub">Family Dollar moved from investment grade to unrated on its sale and repriced immediately.
    Burger King widened 25 bp at 10-year. The market does not wait for confirmations.</div>
  </div>
  <div class="card">
    <h3>4 · The market is bifurcating, not falling</h3>
    <div class="big" style="font-size:22px">25 bp</div>
    <div class="sub">Bid–ask spreads in retail widened to 25 bp in Q3 2026. Premium long-term credit trades tight;
    short-term and unrated product trades wide and selectively.</div>
  </div>
</div>

<div class="callout danger">
  <p><strong>PROP-001 sits on the wrong side of that line today</strong> — short-term and probably unrated — and
  moves further out on it every year it is not extended. That is the entire valuation argument in one sentence.</p>
</div>

<h2>Cap-rate sensitivity</h2>
<div class="table-wrap"><table>
<thead><tr><th>Cap rate</th><th>Value per $1.00 of NOI</th><th>Change vs 7.91%</th></tr></thead>
<tbody>
<tr><td class="num">6.40%</td><td class="num">$15.62</td><td class="num">+23.5%</td></tr>
<tr><td class="num">6.85%</td><td class="num">$14.60</td><td class="num">+15.4%</td></tr>
<tr><td class="num">7.50%</td><td class="num">$13.33</td><td class="num">+5.4%</td></tr>
<tr><td class="num"><b>7.91%</b></td><td class="num"><b>$12.65</b></td><td class="num"><b>base</b></td></tr>
<tr><td class="num">8.46%</td><td class="num">$11.82</td><td class="num">−6.6%</td></tr>
<tr><td class="num">9.00%</td><td class="num">$11.11</td><td class="num">−12.2%</td></tr>
<tr><td class="num">10.50%</td><td class="num">$9.52</td><td class="num">−24.7%</td></tr>
</tbody></table></div>
<p class="tbl-note">Derived arithmetic (NOI ÷ cap rate), consistent with the model's curve and with the same
multiples published on the Projection page.</p>
"""
page("capital-markets.html", "Markets",
     "Verified interest rates, inflation and net-lease cap rates, with the term premium quantified.",
     cm_body + pager("capital-markets.html"))

# ============================================================================= LEASE
lease_body = f"""
<section class="hero">
  <div class="eyebrow">Lease &amp; term</div>
  <h1>The lease is the asset — and nobody has read it</h1>
  <p>The Owner describes an NNN lease expiring between 2030 and 2035. That description is the entire basis for
  every valuation assumption in this dossier, and it has not been verified. Eight specific clauses change the
  answer, and six of them are worth more than a percentage point of cap rate each.</p>
  <div class="verdict"><b>Reading the lease is worth ~${VOI['value_spread_from_expiry_dollars_at_200k_noi']:,.0f}</b>
  ({VOI['value_spread_from_expiry_pct_of_value']:.1f}% of value, on a $200,000-NOI asset) and costs nothing. Nothing
  else in this dossier should be acted on before it is done.</div>
</section>

<h2>The pricing identity</h2>
<div class="callout">
  <p><code>Value = NOI ÷ Cap Rate</code>. Only two things can move value: NOI, or the cap rate. A NNN lease fixes
  the landlord's NOI contractually, so before expiry there is almost no lever on the numerator. <b>Remaining term
  feeds directly into the denominator</b> — net-lease buyers pay for durability of cash flow. Time is therefore a
  cost, not neutral.</p>
</div>

<h2>What "NNN" does and does not guarantee</h2>
<p class="lede">Triple-net typically obliges the tenant to pay base rent plus its share of property taxes, insurance
and common-area maintenance. What materially changes value — and what is unverified here — is everything below.</p>
<div class="table-wrap"><table>
<thead><tr><th>Clause</th><th>Why it matters</th><th>Value at stake</th><th>Status</th></tr></thead>
<tbody>
<tr><td class="metric">Corporate guaranty vs franchisee only</td><td>Sets credit quality and the cap-rate anchor</td><td class="num">~100 bp / ~15% of value</td><td><span class="badge st-blank">UNVERIFIED</span></td></tr>
<tr><td class="metric">Escalations: flat, fixed or CPI</td><td>A flat lease loses ~3.7%/yr real value at current CPI</td><td class="num">Up to ~30% over 10 years</td><td><span class="badge st-blank">UNVERIFIED</span></td></tr>
<tr><td class="metric">Renewal options — who holds them, at what rent</td><td>A below-market tenant option caps upside and depresses sale price</td><td class="num">High</td><td><span class="badge st-blank">UNVERIFIED</span></td></tr>
<tr><td class="metric">Absolute net vs roof/structure carve-out</td><td>Capital-replacement exposure to the landlord</td><td class="num">~0.15–0.30% of value / yr</td><td><span class="badge st-blank">UNVERIFIED</span></td></tr>
<tr><td class="metric">Early termination / kick-out right</td><td>Turns a "leased" asset into an option the tenant owns</td><td class="num">High</td><td><span class="badge st-blank">UNVERIFIED</span></td></tr>
<tr><td class="metric">Radius / use restrictions</td><td>Shrinks the re-leasing pool after expiry</td><td class="num">Medium</td><td><span class="badge st-blank">UNVERIFIED</span></td></tr>
<tr><td class="metric">Assignment &amp; subletting consent standard</td><td>Affects the liquidity of the tenant's own position</td><td class="num">Medium</td><td><span class="badge st-blank">UNVERIFIED</span></td></tr>
<tr><td class="metric">Insurance covenant — who bears premium escalation</td><td>In a repricing market this can be the difference between renewal and default</td><td class="num">High</td><td><span class="badge st-blank">UNVERIFIED</span></td></tr>
</tbody></table></div>

<h2>The expiry question, as arithmetic</h2>
<p class="lede">"2030 to 2035" is not a date. Measured from 2026-11-06 that is anywhere from ~3.5 to ~9.2 years of
remaining term — and in single-tenant net lease, remaining term is the largest pricing variable after credit.</p>
{facts_table(["asset"], table_id="tbl-asset")}

<h2>Remaining term and value</h2>
<div class="table-wrap"><table>
<thead><tr><th>Assumed expiry</th><th>Remaining term at 2026-11-06</th><th>Model cap rate</th><th>Value per $1.00 of NOI</th><th>vs 2035 expiry</th></tr></thead>
<tbody>
{''.join(f'<tr><td class="num">{e["expiry_year"]}-12-31</td><td class="num">{e["remaining_term_years"]:.2f} yr</td><td class="num">{e["cap_now_pct"]:.2f}%</td><td class="num">${e["value_now_per_1_noi"]:.2f}</td><td class="num">{100*(e["value_now_per_1_noi"]/PROJ["expiry_sensitivity"][-1]["value_now_per_1_noi"]-1):+.1f}%</td></tr>' for e in PROJ["expiry_sensitivity"])}
</tbody></table></div>
<div class="callout danger"><p><strong>${VOI['value_spread_from_expiry_dollars_at_200k_noi']:,.0f} rides on a date
nobody has looked up.</strong> {VOI['value_spread_from_expiry_pct_of_value']:.1f}% of value, from a five-year
ambiguity in a single sentence.</p></div>

<h2>The extension premium</h2>
<div class="grid g3">
  {kpi(f"{UP['cap_now_pct']:.2f}%", "Cap rate today", "~6.5 years remaining")}
  {kpi(f"{UP['cap_after_extension_pct']:.2f}%", "Cap rate after extension", "~15 years remaining", "pos")}
  {kpi(f"+{UP['uplift_pct']:.1f}%", "Value uplift", f"${UP['uplift_dollars_at_200k_noi']:,.0f} at $200k NOI", "pos")}
</div>
<p>A tenant extension is not a courtesy — it is the single largest value-creation event available. It is also the
one thing the tenant will charge for. The model assumes a <b>4% rent concession</b> and only a
<b>{VOI['extend_agreement_rate_pct']:.0f}% chance</b> the franchisor signs at all; negotiate against the
{UP['uplift_pct']:.1f}% it creates, and walk away from demands above roughly 15%.</p>

<h2>What to obtain, in order</h2>
<ol class="tight">
  <li>Lease and all amendments (redacted is fine — no personal information needs to enter this repository).</li>
  <li>Estoppel certificate from the tenant.</li>
  <li>Current rent roll and CAM reconciliations.</li>
  <li>Most recent property tax bill and insurance binder (confirm who pays).</li>
  <li>Guaranty and any franchisee financial statements.</li>
</ol>
"""
page("lease.html", "Lease",
     "NNN lease mechanics: what is verified, what is not, and the value at stake in each clause.",
     lease_body + pager("lease.html"))

# ============================================================================= HAZARDS
haz_body = f"""
<section class="hero">
  <div class="eyebrow">Geography &amp; catastrophe risk</div>
  <h1>The black-swan layer is not hypothetical — it happened nine months ago</h1>
  <p>California lost <b>16,627 structures</b> to wildfire in 2025. Four Los Angeles County incidents exceeded 5,000
  acres, two of them starting on the same day. This page separates what is verified from what cannot be determined
  without a parcel identifier, and explains how each hazard actually reaches a net-lease landlord.</p>
  <div class="verdict"><b>The asymmetry:</b> selling transfers catastrophe exposure to the buyer at closing. Holding
  retains it in full, while the recovery upside stays with the buyer either way.</div>
</section>

<div class="grid g4">
  {kpi("8,232", "CA wildfires, 2025", "Statewide", "neg")}
  {kpi("507,817", "Acres burned, 2025", "Statewide", "neg")}
  {kpi("16,627", "Structures destroyed", "2025, statewide", "neg")}
  {kpi("31", "Fatalities", "2025, preliminary", "neg")}
</div>

<h2>Los Angeles County, 2025</h2>
{bar_chart([("Palisades Fire", 23448, "23,448 ac", "r"), ("Eaton Fire", 14021, "14,021 ac", "r"), ("Hughes Fire", 10425, "10,425 ac", "a"), ("Canyon Fire", 5370, "5,370 ac", "a")])}
<p class="tbl-note">Acres burned, CAL FIRE 2025 Incident Archive. Palisades 23,448 ac and Eaton 14,021 ac both
started 2025-01-07; Hughes 10,425 ac started 2025-01-22; Canyon 5,370 ac started 2025-08-07.</p>

<h2>Why a NNN landlord should care at all</h2>
<p class="lede">A common error: <em>"it's NNN, the tenant pays insurance and taxes, so hazards are the tenant's
problem."</em> That is wrong in four specific ways.</p>
<div class="table-wrap"><table>
<thead><tr><th>Transmission channel</th><th>How it reaches the landlord</th><th>Mitigation</th></tr></thead>
<tbody>
<tr><td class="metric">Insurance availability and price</td><td>Even where the tenant pays, a doubling of premium is a direct hit to the tenant's P&amp;L and therefore to its willingness and ability to renew at the same rent. In severe cases coverage becomes unobtainable, making the site uninsurable and unfinanceable.</td><td>Confirm the lease's insurance covenant and who bears premium escalation</td></tr>
<tr><td class="metric">Post-event demand destruction</td><td>A regional fire or earthquake displaces households and closes roads for months. QSR sales fall immediately; a marginal store can go cash-negative.</td><td>Trade-area diversification; no single-asset concentration</td></tr>
<tr><td class="metric">Physical loss / business interruption</td><td>If the landlord owns roof and structure, rebuild is a landlord cost and rent abatement runs concurrently.</td><td>Confirm absolute-net vs modified; confirm landlord insurance</td></tr>
<tr><td class="metric">Buyer-pool contraction</td><td>After a visible catastrophe, buyers underwrite the whole submarket wider. Cap rates move even for undamaged buildings.</td><td>Sell before the repricing, or into a market that has already repriced</td></tr>
</tbody></table></div>

<h2>What is verified, and what is not</h2>
{facts_table(["hazards"], note="CAL FIRE and the Office of the State Fire Marshal are Tier 1. The final four rows are the model's stated priors and are labelled as assumptions — they are not official statistics.", table_id="tbl-haz")}

<div class="callout warn">
  <p><strong>Hazard is not risk.</strong> A Fire Hazard Severity Zone measures physical conditions producing
  likelihood and expected fire behaviour over a <b>30–50 year</b> horizon, <em>ignoring</em> mitigation such as home
  hardening or fuel reduction. A dense, flat, urban central-LA parcel is typically in the Local Responsibility Area
  and usually Moderate or unclassified, whereas hillside parcels in the same county are Very High. That is an
  <b>inference</b>, not a verified fact for this parcel — and it is not zero, because smoke, power shut-offs,
  insurance repricing and buyer sentiment are county-wide.</p>
</div>

<h2>Earthquake: the risk diversification inside LA cannot fix</h2>
<p class="lede">Southern California's seismic exposure is <b>regional and correlated</b>: one event affects the
entire buyer pool, the tenant's whole store fleet and the entire insurance market simultaneously. That is the
definition of a risk that diversifying <em>inside the region</em> cannot remove — which is an argument about the
portfolio, independent of this parcel.</p>
<p>The specific fault proximity, seismic design category, and liquefaction zone <b>cannot be determined without the
address</b> and are left blank on the Flagged page. The authoritative sources are the USGS Earthquake Hazards
Program and the California Geological Survey.</p>

<h2>The asymmetry that decides the hold-versus-sell question</h2>
<div class="table-wrap"><table>
<thead><tr><th></th><th>Sell now</th><th>Hold 4–9 years to expiry</th></tr></thead>
<tbody>
<tr><td class="metric">Exposure to a catastrophe</td><td>Transferred to the buyer at closing</td><td>Retained in full</td></tr>
<tr><td class="metric">Who bears insurance repricing</td><td>Buyer</td><td>Owner</td></tr>
<tr><td class="metric">Who bears the demand shock</td><td>Buyer</td><td>Owner</td></tr>
<tr><td class="metric">Who keeps the recovery upside if the event is benign</td><td>Buyer</td><td>Owner</td></tr>
</tbody></table></div>
<div class="callout danger">
  <p><strong>Holding is a long position in the survival of one parcel's cash flow</strong> through a period in which
  the historical frequency of severe LA County events is visibly rising. That is defensible only if it is paid for —
  i.e. only if the value of waiting, plus the tax deferral from not selling, exceeds the option value of de-risking
  now. The projection engine quantifies exactly that trade-off, and the answer is no.</p>
</div>

<h2>Hazards that were not quantified here</h2>
<ul class="tight">
  <li><b>FEMA National Risk Index</b> county score — API returned HTTP 500 on 2026-11-06.</li>
  <li><b>Flood zone, drought, extreme heat, power shut-offs (PSPS)</b> — no number is asserted. Blank is deliberate.</li>
  <li><b>Parcel-level determinations of any kind</b> — require the address, which was deliberately not retained.</li>
</ul>
"""
page("hazards.html", "Risk",
     "Wildfire, seismic, insurance and catastrophe risk for a central Los Angeles net-lease asset.",
     haz_body + pager("hazards.html"))

# ============================================================================= TAX
tax_body = f"""
<section class="hero">
  <div class="eyebrow">Tax &amp; personal wealth</div>
  <h1>The tax tail should not wag the decision</h1>
  <p>A sale at today's value would trigger roughly <b>{PROJ['tax_waterfall_example']['effective_rate_on_price_pct']:.1f}% of the
  price</b> in combined federal and California tax under the model's assumptions. That is a real number and it is
  the main reason Owners hold. It is also smaller than the cost of doing nothing.</p>
  <div class="verdict"><b>A §1031 exchange defers the tax — it does not eliminate it.</b> This model deducts the
  deferred liability rather than pretending the deferral is free, and §1031 still wins on a risk-adjusted basis.</div>
</section>

<h2>The rates, from the IRS</h2>
{facts_table(["legal-tax"], note="Federal rates are from IRS Topic No. 409 and the §1031 guidance. California and local items are flagged where they could not be verified in this session.", table_id="tbl-tax")}

<h2>How the sale tax is built</h2>
<ol class="tight">
  <li><b>Gain</b> = net sale price − adjusted basis (original basis less accumulated depreciation).</li>
  <li><b>Unrecaptured IRC §1250 gain</b> — the depreciation taken — is taxed at a <b>maximum 25%</b> federal rate.
  This is the most commonly underestimated line.</li>
  <li><b>Remaining long-term capital gain</b> is taxed at <b>20%</b> federal plus the <b>3.8%</b> net investment
  income tax where applicable.</li>
  <li><b>California</b> taxes the whole gain at ordinary rates with no preferential rate and no out-of-state
  deferral mechanism without an undertaking.</li>
</ol>

<div class="table-wrap"><table>
<thead><tr><th>Line (per $1.00 of current NOI)</th><th>Amount</th></tr></thead>
<tbody>
<tr><td class="metric">Gross sale price</td><td class="num">{PROJ['tax_waterfall_example']['price']:.4f}</td></tr>
<tr><td class="metric">Adjusted basis</td><td class="num">{PROJ['tax_waterfall_example']['adjusted_basis']:.4f}</td></tr>
<tr><td class="metric">Total gain</td><td class="num">{PROJ['tax_waterfall_example']['total_gain']:.4f}</td></tr>
<tr><td class="metric">Unrecaptured §1250 recapture</td><td class="num">{PROJ['tax_waterfall_example']['recapture_1250']:.4f}</td></tr>
<tr><td class="metric">Federal tax on recapture (25%)</td><td class="num">{PROJ['tax_waterfall_example']['fed_recapture_tax']:.4f}</td></tr>
<tr><td class="metric">Federal tax on appreciation (23.8%)</td><td class="num">{PROJ['tax_waterfall_example']['fed_appreciation_tax']:.4f}</td></tr>
<tr><td class="metric">California tax (13.3%, assumption)</td><td class="num">{PROJ['tax_waterfall_example']['ca_tax']:.4f}</td></tr>
<tr><td class="metric"><b>Total tax</b></td><td class="num"><b>{PROJ['tax_waterfall_example']['total_tax']:.4f}</b></td></tr>
<tr><td class="metric">Effective rate on price</td><td class="num"><b>{PROJ['tax_waterfall_example']['effective_rate_on_price_pct']:.1f}%</b></td></tr>
</tbody></table></div>
<p class="tbl-note">Basis of 6.00× NOI and 22% accumulated depreciation are <b>assumptions</b>, stated so they can be
replaced with the real depreciation schedule. The California rate of 13.3% is used as an assumption and is
<b>flagged as not re-verified</b> in this session.</p>

<h2>The §1031 exchange: rules that are not negotiable</h2>
<div class="grid g2">
  <div class="card"><h3>45 days</h3><div class="big" style="font-size:20px">Identify replacement property</div>
    <div class="sub">In writing, signed, delivered to a person involved in the exchange — notice to your attorney or
    accountant is not sufficient.</div></div>
  <div class="card"><h3>180 days</h3><div class="big" style="font-size:20px">Complete the exchange</div>
    <div class="sub">Or the due date of the return for the year of sale, whichever is earlier. Not extendable
    except in a presidentially declared disaster.</div></div>
  <div class="card"><h3>Qualified intermediary</h3><div class="big" style="font-size:20px">Before closing</div>
    <div class="sub">You cannot act as your own facilitator, and neither can your agent or anyone who worked for
    you in that capacity in the previous two years. Taking control of proceeds can disqualify the entire
    transaction.</div></div>
  <div class="card"><h3>Deferral ≠ elimination</h3><div class="big" style="font-size:20px">Liability carries forward</div>
    <div class="sub">The deferred gain reduces the basis of the replacement property. This model deducts the deferred
    liability from the §1031 strategy's economic net worth for exactly that reason.</div></div>
</div>

<div class="callout warn">
  <p><strong>Two California items that must be resolved before an exchange is structured</strong> — both flagged,
  neither verified here:</p>
  <p>1. <b>Out-of-state replacement.</b> California does not defer California-source gain when replacement property
  sits outside California without an undertaking to file a California return when the replacement is later sold
  (FTB Form 3840). Get an opinion <em>before</em> identifying replacement property if the plan is to leave the state.</p>
  <p>2. <b>Local transfer taxes.</b> LA city and county documentary transfer taxes, and the Measure ULA surcharge on
  higher-value transfers, were not verified in this session. They affect net proceeds and, at the margin, the
  timing decision. Confirm with the LA County Registrar-Recorder and the City before pricing a sale.</p>
</div>

<h2>Wealth preservation: the portfolio view</h2>
<p class="lede">The brief asked for the best decision "for the property and myself as an individual for the
preservation of wealth and opportunity for growth, maintaining a balance that outlines risk factors and maintains a
manageable level of risk." Four portfolio observations follow from the data, not from the property:</p>
<ul class="tight">
  <li><b>Concentration is the dominant risk, not the cap rate.</b> One parcel, one tenant, one brand, one metro,
  one catastrophe zone. The model's worst-decile outcome for holding (1.88× NOI) is a concentration outcome.</li>
  <li><b>Deferral compounds only if the replacement is better.</b> A §1031 into a single similar asset reproduces the
  same concentration with a new address. Spread proceeds across at least two assets and, ideally, two metros.</li>
  <li><b>Basis and entity structure are unsolved here.</b> Step-up at death, trust ownership, and installment-sale
  mechanics can each dominate the arithmetic above, and each depends on facts this repository deliberately does not
  hold. That is a job for counsel, with the numbers in this dossier as inputs.</li>
  <li><b>Liquidity has value that NPV does not capture.</b> A sub-$5 million single-tenant asset in a thin,
  rising-rate market can take 6–12 months to sell. Planning the exit now buys the option to be patient.</li>
</ul>
"""
page("tax.html", "Tax",
     "Federal and California tax on sale, §1031 mechanics, and portfolio-level wealth preservation.",
     tax_body + pager("tax.html"))

# ============================================================================= FLAGS
unv = [f for f in FACTS["facts"] if f["status"] == "unverified"]
own = [f for f in FACTS["facts"] if f["status"] == "owner-stated"]
asm = [f for f in FACTS["facts"] if f["status"] == "assumption"]

unv_rows = "\n".join(
    f'<tr><td class="metric">{esc(f["metric"])}</td><td>{esc(f.get("geo",""))}</td>'
    f'<td>{esc(f.get("note",""))}</td>'
    f'<td class="src"><a href="{esc(f["url"])}" target="_blank" rel="noopener">{esc(f["source"])}</a></td>'
    f'<td><span class="badge st-blank">unverified</span></td></tr>' for f in unv)

own_rows = "\n".join(
    f'<tr><td class="metric">{esc(f["metric"])}</td><td class="num">{esc(f["value"])}</td>'
    f'<td>{esc(f.get("note",""))}</td><td><span class="badge t3">owner-stated</span></td></tr>' for f in own)

asm_rows = "\n".join(
    f'<tr><td class="metric">{esc(f["metric"])}</td><td class="num">{esc(f["value"])}</td>'
    f'<td>{esc(f.get("note",""))}</td><td><span class="badge a">assumption</span></td></tr>' for f in asm)

irregular = [
    ("IR-1", "No street address, APN or legal description was supplied, and none is stored.",
     "Parcel-level facts — fire-hazard-severity zone, FEMA flood zone, seismic site class, assessed value, school "
     "attendance area, zoning and redevelopment potential — cannot be verified. 12 rows are published blank.",
     "Supply the APN or address to a private channel; the parcel checks then take minutes at CAL FIRE, FEMA and CGS."),
    ("IR-2", "The lease was described only as 'NNN, expiring 2030–2035'. No document, rent roll or basis was supplied.",
     "The five-year expiry range alone is worth ~21.6% of value. Escalations, options, guarantor and landlord "
     "obligations are all unknown, and each is worth more than a percentage point of cap rate.",
     "Upload a redacted lease. Redaction is sufficient — no personal data needs to enter this analysis."),
    ("IR-3", "The tenant of record may be a franchisee rather than Jack in the Box Inc.",
     "93.0% of the system is franchised (1,966 of 2,115 units, Q3 FY2026). This is an inference from the corporate "
     "filings, not a fact about this lease. It matters by ~100 bp of cap rate (~15% of value).",
     "Confirm from the lease and any guaranty."),
    ("IR-4", "No Jack-in-the-Box-specific net-lease cap rate could be retrieved.",
     "Boulder Group's Q3 2026 Tenant Profiles covers 88 operators but a JACK-specific range was not available. The "
     "model therefore derives a term curve from the QSR corporate and franchisee anchors and labels every output as "
     "derived.", "Obtain a JACK-specific comp set from a broker before pricing."),
    ("IR-5", "California DOF county population projections are distributed only as .xlsx.",
     "The 2040 population projection could not be machine-verified, so Census Vintage-2025 estimates are used instead "
     "and no projection is asserted.", "Download P-2A from dof.ca.gov and verify manually."),
    ("IR-6", "The FEMA National Risk Index API returned HTTP 500 on 2026-11-06.",
     "County hazard scores are not reported. Only CAL FIRE figures that resolved are used.", "Retry NRI later."),
    ("IR-7", "The LA County Assessor's Proposition 13 page did not render content.",
     "The 2% annual assessed-value cap is not asserted. The Assessor's decline-in-value window IS verified "
     "(applications from 2026-07-02, deadline 2026-11-30).",
     "Confirm Prop 13 status with the Assessor or Cal. Rev. & Tax. Code §51."),
    ("IR-8", "California top marginal rate of 13.3% and the FTB 3840 out-of-state exchange rule are used as "
             "assumptions and are not re-verified this session.",
     "Both feed the tax module. An error here moves the tax line, not the strategy ranking.",
     "Confirm with a California tax adviser."),
    ("IR-9", "Measure ULA and LA local transfer taxes were not verified.",
     "These affect net sale proceeds and can affect the timing decision.", "Confirm with the City and County."),
    ("IR-10", "Cap-rate data are Tier 3 industry data (The Boulder Group), not official statistics.",
     "They are the best available market pricing signal but are directional. Every cap-rate row is badged T3.",
     "Cross-check with a second research house before pricing."),
    ("IR-11", "The catastrophe and default priors in the model are stated assumptions, not official frequencies.",
     "Wildfire 4%/yr, seismic 3%/yr, insurance shock 6%/yr, tenant default 3.5%/yr. The model reports results both "
     "with and without this layer so its influence is visible.",
     "Challenge the priors; the recommendation's direction does not depend on them (see the no-hazard control)."),
    ("IR-12", "The brief asked about school systems. School quality is deliberately not assessed.",
     "The assigned attendance area cannot be determined without the address, so no claim is made rather than a "
     "guessed one. For a QSR, household formation matters more than school ratings anyway.",
     "Provide the address; then use CDE DataQuest / CAASPP."),
]
irr_rows = "\n".join(
    f'<tr><td class="num">{i}</td><td class="metric">{t}</td><td>{w}</td><td>{n}</td></tr>'
    for i, t, w, n in irregular)

flags_body = f"""
<section class="hero">
  <div class="eyebrow">Flagged for review</div>
  <h1>Everything this dossier could not verify</h1>
  <p>Nothing here was inferred, estimated or filled in. Where an official source could not be reached or a document
  was not supplied, the value is left <b>blank</b> and published here with the source that should settle it.
  {len(unv)} items are blank and flagged, {len(own)} are reported as the Owner stated them, and {len(asm)} are
  disclosed assumptions.</p>
  <div class="verdict">None of this blocks publication or the recommendation — but <b>IR-1 through IR-3 do block a
  transaction</b>. Do not price, market, extend or sell this asset before those three are closed.</div>
</section>

<h2>Irregularities requiring a decision</h2>
<div class="table-wrap"><table>
<thead><tr><th>#</th><th>Irregularity</th><th>Why it matters</th><th>How to close it</th></tr></thead>
<tbody>{irr_rows}</tbody></table></div>

<h2>Blank and flagged — no value asserted</h2>
<p class="lede">Each row is a field this analysis deliberately left empty rather than guessing. The source column is
where the answer actually lives.</p>
<div class="table-wrap"><table>
<thead><tr><th>Item</th><th>Geography</th><th>Why it is blank</th><th>Authoritative source</th><th>Status</th></tr></thead>
<tbody>{unv_rows}</tbody></table></div>

<h2>Owner-stated, not verified</h2>
<div class="table-wrap"><table>
<thead><tr><th>Item</th><th>As stated</th><th>Note</th><th>Status</th></tr></thead>
<tbody>{own_rows}</tbody></table></div>

<h2>Disclosed assumptions used by the model</h2>
<p class="lede">These are not errors — they are the model's inputs, published so they can be challenged and
replaced.</p>
<div class="table-wrap"><table>
<thead><tr><th>Assumption</th><th>Value</th><th>Note</th><th>Status</th></tr></thead>
<tbody>{asm_rows}</tbody></table></div>

<h2>What was deliberately withheld</h2>
<div class="table-wrap"><table>
<thead><tr><th>Field</th><th>Published as</th><th>Why</th></tr></thead>
<tbody>
<tr><td class="metric">Owner identity</td><td class="num">PARTY-OWNER</td><td>Privacy protocol — no personal or entity information is stored or published</td></tr>
<tr><td class="metric">Tenant identity</td><td class="num">PARTY-TENANT</td><td>Privacy protocol</td></tr>
<tr><td class="metric">Street address</td><td class="num">[ADDRESS REDACTED]</td><td>Privacy protocol</td></tr>
<tr><td class="metric">Assessor's parcel number</td><td class="num">APN [REDACTED]</td><td>Privacy protocol</td></tr>
<tr><td class="metric">Legal description</td><td class="num">[LEGAL DESC REDACTED]</td><td>Privacy protocol</td></tr>
<tr><td class="metric">Owner's income, net worth, tax bracket, basis</td><td class="num">not collected</td><td>Privacy protocol — the model is normalised per $1 of NOI so none of it is needed</td></tr>
<tr><td class="metric">Parcel coordinates / geolocation</td><td class="num">not collected</td><td>Privacy protocol</td></tr>
</tbody></table></div>
<div class="callout ok"><p><strong>The trade-off, stated plainly.</strong> Withholding the address protects privacy and
costs analytical precision. That cost is quantified on the <a href="lease.html">Lease</a> page at roughly
${VOI['value_spread_from_expiry_dollars_at_200k_noi']:,.0f} of value tied to the unresolved expiry date alone. The
correct resolution is to verify the parcel privately and publish only the anonymised conclusions — which is what
this site does.</p></div>
"""
page("flags.html", "Flagged for Review",
     "Every unverified, owner-stated and assumed item, each with the official source that would settle it.",
     flags_body + pager("flags.html"))

# ============================================================================= METHODOLOGY
by_tier = {}
for f in FACTS["facts"]:
    by_tier[f["tier"]] = by_tier.get(f["tier"], 0) + 1
tier_rows = "\n".join(
    f'<tr><td><span class="badge {t.lower() if t != "—" else "d"}">{TIER_LABEL.get(t,t)}</span></td>'
    f'<td class="num">{by_tier[t]}</td><td>{d}</td></tr>'
    for t, d in [("T1", "Government or central-bank primary source. Authoritative."),
                 ("T2", "Primary-source data hosted on the issuing institution's own site."),
                 ("T3", "Named commercial research house. Directional only, never authoritative."),
                 ("D", "Arithmetic performed by this model on T1/T2 inputs, with the formula shown."),
                 ("A", "Analytical input chosen by this model. Never presented as fact."),
                 ("—", "Privacy placeholder — a value deliberately withheld.")] if t in by_tier)

SRC = [
    ("Federal Reserve Bank of St. Louis (FRED)", "Interest rates, inflation, employment, unemployment",
     "https://fred.stlouisfed.org/series/DGS10"),
    ("U.S. Treasury — 10-Year Constant Maturity (DGS10)", "Risk-free rate", "https://fred.stlouisfed.org/series/DGS10"),
    ("Freddie Mac — Primary Mortgage Market Survey", "30-year mortgage rate", "https://fred.stlouisfed.org/series/MORTGAGE30US"),
    ("U.S. Bureau of Labor Statistics — Current Employment Statistics", "LA metro payrolls", "https://fred.stlouisfed.org/series/SMU06310800000000001"),
    ("U.S. Bureau of Labor Statistics — Local Area Unemployment Statistics", "LA County unemployment", "https://www.bls.gov/lau/laufaq.htm"),
    ("U.S. Bureau of Labor Statistics — CPI", "Inflation", "https://fred.stlouisfed.org/series/CPIAUCSL"),
    ("U.S. Census Bureau — QuickFacts (Population Estimates V2025, ACS 2020–2024, Economic Census, CBP, Building Permits)", "Population, income, housing, education, retail sales", "https://www.census.gov/quickfacts/fact/table/losangelescountycalifornia,losangelescitycalifornia/PST045224"),
    ("U.S. Securities and Exchange Commission — EDGAR", "Jack in the Box Form 10-K FY2025, Form 8-K Q3 FY2026", "https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm"),
    ("Internal Revenue Service — Topic No. 409", "Capital gains rates, §1250 recapture, NIIT", "https://www.irs.gov/taxtopics/tc409"),
    ("Internal Revenue Service — IRC §1031 guidance", "Like-kind exchange rules", "https://www.irs.gov/newsroom/like-kind-exchanges-under-irc-code-section-1031"),
    ("CAL FIRE — 2025 Incident Archive", "Wildfire frequency, acreage, structures lost", "https://www.fire.ca.gov/incidents/2025"),
    ("CAL FIRE / Office of the State Fire Marshal — Fire Hazard Severity Zones", "Hazard classification methodology", "https://osfm.fire.ca.gov/what-we-do/community-wildfire-preparedness-and-mitigation/fire-hazard-severity-zones"),
    ("California Legislative Information — AB 1228 (Ch. 262, Stats. 2023)", "Fast-food minimum wage", "https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202320240AB1228"),
    ("California Department of Industrial Relations — Minimum Wage FAQ", "State minimum wage", "https://www.dir.ca.gov/dlse/faq_minimumwage.htm"),
    ("Los Angeles County Assessor", "Decline-in-value window; property tax", "https://assessor.lacounty.gov/tax-relief/decline-in-value"),
    ("The Boulder Group — Net Lease Research Q2/Q3 2026 and Tenant Profiles Q3 2026", "Cap rates (Tier 3 industry data)", "https://www.bouldergroup.com/blog/"),
]
src_rows = "\n".join(f'<tr><td class="metric"><a href="{u}" target="_blank" rel="noopener">{n}</a></td><td>{d}</td></tr>'
                     for n, d, u in SRC)

method_body = f"""
<section class="hero">
  <div class="eyebrow">Method, sources &amp; verification</div>
  <h1>How every number on this site was checked</h1>
  <p>{FACTS['count']} sourced data points. Each carries a source link, a source tier and a status. Nothing is
  marked verified without a resolving official source; nothing unconfirmed is filled in.</p>
  <div class="verdict"><b>Reproducible.</b> <code>python3 model/build_facts.py</code> regenerates the dataset and
  asserts that every unverified row is genuinely blank. <code>python3 model/projection_model.py</code> regenerates
  the model with a fixed seed. <code>python3 model/build_site.py</code> rebuilds this site and fails if any internal
  link is broken.</div>
</section>

<h2>Privacy protocol</h2>
<div class="table-wrap"><table>
<thead><tr><th>Rule</th><th>Implementation</th></tr></thead>
<tbody>
<tr><td class="metric">No owner identity</td><td>Referred to only as "the Owner" or <code>PARTY-OWNER</code>. No name, entity, address, phone or email appears anywhere.</td></tr>
<tr><td class="metric">No tenant-contact identity</td><td>Referred to only as "the Tenant" or <code>PARTY-TENANT</code>.</td></tr>
<tr><td class="metric">No parcel identity</td><td>Address, APN and legal description are placeholders.</td></tr>
<tr><td class="metric">No personal financial data</td><td>The Owner's income, net worth, tax bracket and basis are <b>not collected</b>. The model is normalised per $1.00 of NOI so none of it is needed.</td></tr>
<tr><td class="metric">No geolocation</td><td>No street address, cross-streets or coordinates are published. Trade-area analysis is at county / city / metro level.</td></tr>
<tr><td class="metric">Research hygiene</td><td>Raw page captures are never committed. <code>.gitignore</code> blocks <code>private/</code>, <code>*.private</code>, <code>*.pii</code>, <code>*.csv.raw</code>.</td></tr>
</tbody></table></div>

<h2>Source tiers</h2>
<div class="table-wrap"><table>
<thead><tr><th>Tier</th><th>Rows</th><th>Meaning</th></tr></thead>
<tbody>{tier_rows}</tbody></table></div>

<h2>Verification procedure actually performed</h2>
<ol class="tight">
  <li>Each metric was retrieved from a resolving official page or CSV endpoint on <b>2026-11-06</b>.</li>
  <li>The <b>period or vintage</b> is recorded per row (e.g. "Sep 2026", "V2025", "FY2025", "ACS 2020–2024"). Rows are
  never compared across incompatible vintages without saying so.</li>
  <li>Percentages were <b>recomputed from the raw series</b>, not copied from commentary:
    <ul class="tight">
      <li>CPI year over year = 336.298 / 324.245 − 1 = <b>+3.72%</b></li>
      <li>LA metro payrolls, Sep 2019 → Sep 2026 = 6,282.1 / 6,236.7 − 1 = <b>+0.73%</b> over seven years</li>
      <li>LA metro payrolls, Oct 2024 peak → Sep 2026 = 6,282.1 / 6,359.6 − 1 = <b>−1.22%</b></li>
      <li>Franchised share = 1,966 / 2,115 = <b>93.0%</b></li>
    </ul>
  </li>
  <li>Automated assertions in <code>build_facts.py</code>: every <code>verified</code> row must carry a URL, and every
  <code>unverified</code> row must have an empty value. The build fails otherwise.</li>
  <li>Automated assertions in <code>build_site.py</code>: every internal link must resolve to a page that was actually
  emitted.</li>
</ol>

<h2>Known limitations</h2>
<div class="table-wrap"><table>
<thead><tr><th>#</th><th>Limitation</th><th>Consequence</th></tr></thead>
<tbody>
<tr><td class="num">L1</td><td>No street address or APN supplied, by design.</td><td>Parcel-level hazard, zoning, assessed value and school assignment are unverified.</td></tr>
<tr><td class="num">L2</td><td>The lease document was not supplied. "NNN" and "expiring 2030–2035" are as described, not verified.</td><td>The model parameterises these and shows sensitivity instead of asserting them.</td></tr>
<tr><td class="num">L3</td><td>Current rent, NOI and basis were not supplied.</td><td>The model is normalised per $1.00 of current NOI so no disclosure is required.</td></tr>
<tr><td class="num">L4</td><td><code>api.census.gov</code> required a key that was not available.</td><td>ACS data were taken from Census QuickFacts (same source data, different access path).</td></tr>
<tr><td class="num">L5</td><td>California DOF projections are distributed as .xlsx.</td><td>Projections were not machine-verified; Census V2025 estimates are used instead.</td></tr>
<tr><td class="num">L6</td><td>FEMA National Risk Index API returned HTTP 500.</td><td>County hazard scores are not reported.</td></tr>
<tr><td class="num">L7</td><td>Cap-rate data are Tier 3 (a brokerage).</td><td>Treated as directional and badged on every row.</td></tr>
</tbody></table></div>

<h2>Sources used</h2>
<div class="table-wrap"><table>
<thead><tr><th>Source</th><th>What it was used for</th></tr></thead>
<tbody>{src_rows}</tbody></table></div>

<h2>The asset record (anonymised)</h2>
{facts_table(["asset"], table_id="tbl-asset2")}

<h2>Repository layout</h2>
<div class="table-wrap"><table>
<thead><tr><th>Path</th><th>Contents</th></tr></thead>
<tbody>
<tr><td class="mono">COORDINATION.md</td><td>Shared task board, session claims, verification ledger</td></tr>
<tr><td class="mono">research/00-methodology.md</td><td>This method, in full</td></tr>
<tr><td class="mono">research/01-asset-profile.md</td><td>Anonymised asset record and open lease questions</td></tr>
<tr><td class="mono">research/02-jack-in-the-box.md</td><td>Tenant and brand from SEC filings</td></tr>
<tr><td class="mono">research/03-nnn-lease-and-cap-rates.md</td><td>Lease mechanics, cap rates, rates regime</td></tr>
<tr><td class="mono">research/04-central-la-economy.md</td><td>Economy and demographics</td></tr>
<tr><td class="mono">research/05-hazard-risk.md</td><td>Geography and catastrophe risk</td></tr>
<tr><td class="mono">research/06-decision-and-risk.md</td><td>Decision framework and risk register</td></tr>
<tr><td class="mono">research/07-executive-summary.md</td><td>Executive summary</td></tr>
<tr><td class="mono">model/build_facts.py</td><td>Emits <code>docs/data/facts.json</code> with assertions</td></tr>
<tr><td class="mono">model/projection_model.py</td><td>Monte-Carlo engine, emits <code>docs/data/projections.json</code></td></tr>
<tr><td class="mono">model/build_site.py</td><td>Generates this site, validates every internal link</td></tr>
<tr><td class="mono">docs/</td><td>The published GitHub Pages site</td></tr>
</tbody></table></div>
"""
page("methodology.html", "Method",
     "Privacy protocol, source tiers, verification procedure, limitations and full source list.",
     method_body + pager("methodology.html"))

# ============================================================================= WRITE + LINK CHECK
os.makedirs(DOCS, exist_ok=True)
emitted = set(PAGES.keys())
link_re = re.compile(r'href="([^"#:]+\.html)"')
errors = []
for slug, html in PAGES.items():
    for target in link_re.findall(html):
        t = target.split("#")[0]
        if t and t not in emitted:
            errors.append(f"{slug} -> {target}")
    with open(os.path.join(DOCS, slug), "w") as f:
        f.write(html)

# also validate NAV targets
for href, _ in NAV:
    if href not in emitted:
        errors.append(f"NAV -> {href}")

print(f"pages written: {len(PAGES)} -> {', '.join(sorted(PAGES))}")
print(f"internal .html links checked: {sum(len(link_re.findall(h)) for h in PAGES.values())}")
if errors:
    print("BROKEN LINKS:")
    for e in errors:
        print("  ", e)
    raise SystemExit(1)
print("OK — no broken internal links.")

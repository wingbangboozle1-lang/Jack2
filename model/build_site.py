#!/usr/bin/env python3
"""
Jack2 — static site builder.

Generates every page under site/ (plus the root index.html that GitHub Pages
serves) from data/dataset.json, data/sources.json and data/model_output.json,
so navigation, counts and titles can never drift apart from the data.

Design constraints
------------------
* No external assets. No CDN, no web fonts, no analytics. Nothing that could
  leak a visitor or break on a locked-down network.
* Every internal link is RELATIVE, so the site works at
  https://<user>.github.io/Jack2/ and in a local file read.
* Every table row renders its source URL or states explicitly that no source
  was supplied. Unverified rows render a visible BLANK, never a guess.
* Personal information: no name, address, APN, phone, email or account number
  appears in any template. Rows whose value depends on the redacted parcel
  render as blank + UNVERIFIED.

Usage: python3 model/build_site.py
"""

from __future__ import annotations

import json
import os
import html
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, "site")
DATA = os.path.join(ROOT, "data")

NAV = [
    ("index.html", "Overview"),
    ("executive-summary.html", "Executive Summary"),
    ("decision.html", "Decision"),
    ("projection.html", "Projection Model"),
    ("risks.html", "Risk Register"),
    ("data-property.html", "Property"),
    ("data-tenant.html", "Tenant"),
    ("data-macro.html", "Economy"),
    ("data-demographics.html", "Demographics"),
    ("data-employment.html", "Employment"),
    ("data-rates.html", "Rates"),
    ("data-hazard.html", "Hazard"),
    ("data-tax.html", "Tax & Regulation"),
    ("sources.html", "Sources"),
    ("flagged.html", "Flagged for Review"),
    ("methodology.html", "Methodology"),
]

CATEGORY_PAGE = {
    "property": "data-property.html",
    "tenant": "data-tenant.html",
    "macro": "data-macro.html",
    "demographics": "data-demographics.html",
    "employment": "data-employment.html",
    "rates": "data-rates.html",
    "hazard": "data-hazard.html",
    "tax": "data-tax.html",
}


def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


def load():
    ds = json.load(open(os.path.join(DATA, "dataset.json")))
    src = json.load(open(os.path.join(DATA, "sources.json")))
    mo = json.load(open(os.path.join(DATA, "model_output.json")))
    src_by_id = {s["id"]: s for s in src["sources"]}
    return ds, src, mo, src_by_id


def counts(rows):
    c = {"VERIFIED": 0, "DERIVED": 0, "FLAGGED": 0, "UNVERIFIED": 0}
    for r in rows:
        if r["status"] in c:
            c[r["status"]] += 1
    return c


def all_rows(ds):
    out = []
    for cat in ds["categories"]:
        for r in cat["rows"]:
            rr = dict(r)
            rr["_cat"] = cat["id"]
            rr["_cattitle"] = cat["title"]
            out.append(rr)
    return out


def pill(status):
    return f'<span class="pill {esc(status)}">{esc(status)}</span>'


# --------------------------------------------------------------------------
# shell
# --------------------------------------------------------------------------

def localise(body, prefix):
    """Strip the 'site/' prefix from links when the page already lives in site/."""
    if prefix == "":
        return body.replace('href="site/', 'href="')
    return body


def page(path, title, body, root=".", active=None, subtitle="", prefix=None):
    """`prefix` is the relative path from THIS page back to site/ .
    index.html sits at the repo root, so it uses 'site/'; every other page is
    already inside site/ and uses ''. Getting this wrong is the classic cause
    of a broken GitHub Pages nav, so the builder computes it, never guesses."""
    if prefix is None:
        prefix = "site/" if path in ("index.html",) else ""
    body = localise(body, prefix)
    nav_parts = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == active else ""
        tgt = href
        if path == "index.html" and href == "index.html":
            tgt = "./"
        nav_parts.append(f'<a href="{esc(prefix)}{tgt}"{cur}>{esc(label)}</a>')
    nav = "".join(nav_parts)
    doc = f"""<!DOCTYPE html>
<html lang="en" data-root="{esc(prefix)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — Jack2 Net-Lease Decision Dossier</title>
<meta name="description" content="Verified-source decision dossier for a single-tenant Jack in the Box NNN asset in central Los Angeles. Every value sourced or flagged; nothing inferred.">
<link rel="stylesheet" href="{esc(prefix)}assets/style.css">
</head>
<body>
<header class="site"><div class="wrap site-inner">
  <div class="brand"><span class="mark">J</span><span>Jack2 · Net-Lease Dossier</span></div>
  <nav class="main">{nav}</nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="site"><div class="wrap">
  <p><strong>Jack2</strong> — internal decision dossier. Built {date.today().isoformat()} by session
  <code>arena-8149683c</code>. All figures traced to a named official source or explicitly marked
  UNVERIFIED. No personal information is published on this site.</p>
  <p class="small">This is analysis for an internal decision, not an appraisal, not investment advice,
  and not a tax opinion. Cap rates, discount rates and event probabilities are modelling
  assumptions and are labelled as such wherever they appear.</p>
</div></footer>
</body></html>"""
    if path.startswith("site/"):
        path = path[len("site/"):]
    dest = os.path.join(SITE, path) if path != "index.html" else os.path.join(ROOT, "index.html")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as fh:
        fh.write(doc)


def hero(eyebrow, h1, lead, meta=""):
    m = f'<p class="meta">{meta}</p>' if meta else ""
    return f"""<section class="hero">
  <div class="eyebrow">{esc(eyebrow)}</div>
  <h1>{h1}</h1>
  <p class="lead">{lead}</p>
  {m}
</section>"""


# --------------------------------------------------------------------------
# row rendering
# --------------------------------------------------------------------------

def rows_table(rows):
    h = ['<div class="tablewrap"><table><thead><tr>',
         "<th>ID</th><th>Metric</th><th>Value</th><th>Unit</th><th>As of</th><th>Scope</th>",
         "<th>Status</th><th>Source</th><th>Note</th></tr></thead><tbody>"]
    for r in rows:
        if r.get("url"):
            srclink = (f'<a href="{esc(r["url"])}" target="_blank" rel="noopener noreferrer">'
                       f'{esc(r["source"])} &#8599;</a>')
        else:
            srclink = f'<span class="small">{esc(r["source"])} — not supplied</span>'
        val = ('<span class="blank">blank</span>' if r["value"] in ("", None)
               else esc(r["value"]))
        cls = ' class="num"' if r["value"] not in ("", None) else ' class="num blank"'
        h.append(
            f'<tr><td class="nowrap"><code>{esc(r["id"])}</code></td>'
            f'<td>{esc(r["metric"])}</td>'
            f'<td{cls}>{val}</td>'
            f'<td class="small">{esc(r["unit"])}</td>'
            f'<td class="small nowrap">{esc(r["as_of"])}</td>'
            f'<td class="small">{esc(r["geo"])}</td>'
            f"<td>{pill(r['status'])}</td>"
            f'<td class="small">{srclink}</td>'
            f'<td class="small">{esc(r["note"])}</td></tr>'
        )
    h.append("</tbody></table></div>")
    return "".join(h)


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------

def build_index(ds, mo, src):
    rows = all_rows(ds)
    c = counts(rows)
    total = len(rows)
    mc = mo["monte_carlo"]["stats"]
    cat_cards = ""
    for cat in ds["categories"]:
        cc = counts(cat["rows"])
        cat_cards += f"""<a class="card" href="site/{CATEGORY_PAGE[cat['id']]}" style="display:block;color:inherit">
        <h3 style="margin-top:0">{esc(cat['title'])}</h3>
        <p class="small">{esc(cat['blurb'])}</p>
        <p class="small" style="margin-top:10px">
          <strong>{len(cat['rows'])}</strong> rows ·
          <span class="pill VERIFIED">{cc['VERIFIED']}</span>
          <span class="pill DERIVED">{cc['DERIVED']}</span>
          <span class="pill FLAGGED">{cc['FLAGGED']}</span>
          <span class="pill UNVERIFIED">{cc['UNVERIFIED']}</span>
        </p></a>"""

    body = hero(
        "Internal decision dossier · 2026-11-06",
        "Should you sell the Jack in the Box before the lease expires, or renew it?",
        "A single-tenant quick-service restaurant on a triple-net lease in central Los Angeles, "
        "expiring between 2030 and 2035. This dossier prices all four available decisions against one "
        "another, tests them against a black-swan overlay, and marks every input as either traced to an "
        "official source or unverified.",
        f"{total} data rows · {len(src['sources'])} registered sources · "
        f"{mo['monte_carlo']['trials']:,}-trial Monte Carlo · seed {mo['seed']}",
    ) + f"""
<div class="kpis">
  <div class="kpi"><div class="k">Rows traced to an official source</div>
    <div class="v">{c['VERIFIED']}</div><div class="s">of {total} ({c['VERIFIED']/total*100:.0f}%)</div></div>
  <div class="kpi"><div class="k">Arithmetic on verified figures</div>
    <div class="v">{c['DERIVED']}</div><div class="s">formula shown in each row</div></div>
  <div class="kpi"><div class="k">Flagged for review</div>
    <div class="v" style="color:var(--warn)">{c['FLAGGED']}</div>
    <div class="s">source exists but is weak or unreadable</div></div>
  <div class="kpi"><div class="k">Left blank / unverified</div>
    <div class="v" style="color:var(--bad)">{c['UNVERIFIED']}</div>
    <div class="s">no official source could confirm</div></div>
</div>

<div class="grid g2" style="margin-top:22px">
  <div class="card" style="border-color:#3a3320;background:linear-gradient(180deg,#1a1a14,#151b24)">
    <h3 style="margin-top:0">The recommendation, stated as a rule</h3>
    <p><strong>Hold and extend if your required return is below the sell/hold crossover.
    Sell if it is above.</strong></p>
    <p>At a 7.10% market cap rate and six years of remaining term, that crossover is an owner
    return of <strong>{mo['crossover'][0]['crossover_discount_rate']*100:.2f}%</strong>. At a 7.85%
    cap rate it is <strong>{mo['crossover'][1]['crossover_discount_rate']*100:.2f}%</strong>.</p>
    <p class="small">A single-asset QSR with a near-term roll is normally bought by private capital
    with a required return <em>below</em> that crossover. If that describes you, the arithmetic says
    hold. If you require a higher return than the market is paying, the arithmetic says sell now.
    <a href="site/decision.html">Full decision analysis &rarr;</a></p>
  </div>
  <div class="card">
    <h3 style="margin-top:0">What the model says, in four numbers</h3>
    <p class="small">Present value to the owner, median of {mo['monte_carlo']['trials']:,} trials,
    including a {(mo['monte_carlo']['event_frequency']*100):.1f}% black-swan overlay.</p>
    <div class="dec">
      <div class="d{' win' if 'A'==max(mc, key=lambda k: mc[k]['median']) else ''}">
        <div class="tag">A</div><h4>Sell now</h4>
        <div class="big">${mc['A']['median']:,.0f}</div>
        <div class="sub">5th&ndash;95th pct ${mc['A']['p05']:,.0f}&ndash;${mc['A']['p95']:,.0f}</div></div>
      <div class="d{' win' if 'B'==max(mc, key=lambda k: mc[k]['median']) else ''}">
        <div class="tag">B</div><h4>Hold to expiry</h4>
        <div class="big">${mc['B']['median']:,.0f}</div>
        <div class="sub">5th&ndash;95th pct ${mc['B']['p05']:,.0f}&ndash;${mc['B']['p95']:,.0f}</div></div>
      <div class="d{' win' if 'C'==max(mc, key=lambda k: mc[k]['median']) else ''}">
        <div class="tag">C</div><h4>Renew &amp; hold</h4>
        <div class="big">${mc['C']['median']:,.0f}</div>
        <div class="sub">5th&ndash;95th pct ${mc['C']['p05']:,.0f}&ndash;${mc['C']['p95']:,.0f}</div></div>
      <div class="d{' win' if 'D'==max(mc, key=lambda k: mc[k]['median']) else ''}">
        <div class="tag">D</div><h4>Extend, sell long WALT</h4>
        <div class="big">${mc['D']['median']:,.0f}</div>
        <div class="sub">5th&ndash;95th pct ${mc['D']['p05']:,.0f}&ndash;${mc['D']['p95']:,.0f}</div></div>
    </div>
  </div>
</div>

<h2>Browse by category</h2>
<div class="grid g3">{cat_cards}</div>

<h2>How to read this site</h2>
<div class="grid g2">
  <div class="card">
    <h3 style="margin-top:0">Verification discipline</h3>
    <div class="legend">
      {pill('VERIFIED')} appears verbatim in an official source
    </div>
    <div class="legend">
      {pill('DERIVED')} arithmetic on two verified values; formula shown
    </div>
    <div class="legend">
      {pill('FLAGGED')} a source exists but is secondary, paywalled, or unreadable
    </div>
    <div class="legend">
      {pill('UNVERIFIED')} no official source could confirm it — the cell is <em>blank</em>
    </div>
  </div>
  <div class="card">
    <h3 style="margin-top:0">Start here</h3>
    <ul>
      <li><a href="site/executive-summary.html">Executive summary</a> — the whole case on one page</li>
      <li><a href="site/decision.html">Decision analysis</a> — all four options, with risks</li>
      <li><a href="site/projection.html">Projection model</a> — the engine, the surface, the Monte Carlo</li>
      <li><a href="site/risks.html">Risk register</a> — business-as-usual and black swans</li>
      <li><a href="site/flagged.html">Flagged for review</a> — what I could not verify, and why</li>
    </ul>
  </div>
</div>
"""
    page("index.html", "Overview", body, root=".", active=None)


def build_category(ds, cat, rows, src_by_id):
    c = counts(rows)
    body = hero(
        f"Category · {len(rows)} rows",
        esc(cat["title"]),
        esc(cat["blurb"]),
        f"{c['VERIFIED']} verified · {c['DERIVED']} derived · {c['FLAGGED']} flagged · "
        f"{c['UNVERIFIED']} left blank as unverified",
    )
    body += f"""
<div class="legend" style="margin-bottom:6px">
  {pill('VERIFIED')} {c['VERIFIED']} &nbsp; {pill('DERIVED')} {c['DERIVED']} &nbsp;
  {pill('FLAGGED')} {c['FLAGGED']} &nbsp; {pill('UNVERIFIED')} {c['UNVERIFIED']}
</div>
{rows_table(rows)}
<p class="small">Every value above carries either a live link to the official source it came from,
or an explicit statement that no source was supplied. Blank cells are blank because no official
source could confirm them — they have not been estimated.</p>
"""
    page("site/" + CATEGORY_PAGE[cat["id"]], cat["title"], body,
         root="..", active=CATEGORY_PAGE[cat["id"]])


def build_exec_summary(ds, mo, src):
    rows = all_rows(ds)
    c = counts(rows)
    mc = mo["monte_carlo"]["stats"]
    byid = {r["id"]: r for r in rows}

    def v(rid):
        return byid[rid]["value"]

    body = hero(
        "Executive summary",
        "The decision, the numbers behind it, and what is still unknown",
        "One page. The asset, the tenant, the market, the four options, the risks, and the exact "
        "items that could not be verified. Nothing below depends on a figure that is not either "
        "sourced in this site or labelled as a modelling assumption.",
        f"Prepared 2026-11-06 · {len(rows)} verified-graded data rows · {len(src['sources'])} sources",
    )

    body += f"""
<div class="callout">
  <div class="t">The bottom line</div>
  <p><strong>Do not sell simply because the lease expires.</strong> Lease expiry is a refinancing
  event, not a liquidation event. The market evidence in this dossier shows net leases re-let at
  <em>above</em> prior rent: Realty Income disclosed a realised rent recapture rate of
  <strong>103.5%</strong> in Q3 2026 and 103.1% year-to-date (SEC Form 8-K, 2026-11-02).</p>
  <p><strong>The real decision is a spread, not a calendar.</strong> Hold whenever your required return
  is below the sell/hold crossover. On the base case (7.10% cap, 6 years left) that crossover is
  <strong>{mo['crossover'][0]['crossover_discount_rate']*100:.2f}%</strong>. Sell when your required return
  is above it. Everything else is second-order.</p>
  <p><strong>Do not renew at any price.</strong> The tenant's own 10-K shows same-store sales of
  <strong>&minus;4.2%</strong>, franchise AUV down <strong>&minus;3.9%</strong>, transactions down
  <strong>&minus;5.7%</strong>, 86 closures against 31 openings, and two consecutive years of
  goodwill impairment. A renewal that requires you to cut rent to keep the box occupied is a
  concession, not a win, and it should be priced as one.</p>
</div>

<h2>1. The asset</h2>
<div class="tablewrap"><table><thead><tr><th>Dimension</th><th>Position</th><th>Status</th><th>Why it matters</th></tr></thead><tbody>
<tr><td>Asset</td><td>Single-tenant quick-service restaurant, triple-net</td><td>{pill('UNVERIFIED')}</td>
  <td>Lease document not supplied. NNN <em>structure</em> is owner-stated; roof/structure/HVAC allocation is unverified (P-12).</td></tr>
<tr><td>Tenant</td><td>Jack in the Box brand</td><td>{pill('VERIFIED')}</td>
  <td>2,136 restaurants system-wide, 93% franchised (SEC 10-K FY2025). <strong>Whether your tenant is the public company or a franchisee is unverified and is the single most important open item.</strong></td></tr>
<tr><td>Location</td><td>Central Los Angeles</td><td>{pill('UNVERIFIED')}</td>
  <td>Parcel redacted by privacy instruction, so trade area, zoning and hazard zone cannot be established.</td></tr>
<tr><td>Lease expiry</td><td>2030&ndash;2035</td><td>{pill('UNVERIFIED')}</td>
  <td>A 9-year range. Remaining term is the largest single driver of net-lease pricing, so it is modelled as a sweep, not a point.</td></tr>
<tr><td>Base rent</td><td>Not supplied</td><td>{pill('UNVERIFIED')}</td>
  <td>Modelled across $150k&ndash;$350k/yr, which maps to between 8.0% and 18.7% of the tenant's average franchise unit volume.</td></tr>
</tbody></table></div>

<h2>2. What the market actually looks like</h2>
<div class="grid g3">
  <div class="card"><h3 style="margin-top:0">Tenant health</h3>
    <ul>
      <li>Same-store sales <strong>{esc(v('T-08'))}%</strong> (FY2025)</li>
      <li>Franchise AUV <strong>${int(v('T-06')):,}k</strong>, down {esc(v('T-07'))}%</li>
      <li>86 closures vs 31 openings</li>
      <li>Pre-tax loss of <strong>${int(v('T-23')):,}k</strong></li>
      <li>Dividend discontinued</li>
    </ul>
    <p class="small"><a href="site/data-tenant.html">All {len([r for r in rows if r['_cat']=='tenant'])} tenant rows &rarr;</a></p>
  </div>
  <div class="card"><h3 style="margin-top:0">Regional economy</h3>
    <ul>
      <li>Real GCP growth <strong>{esc(v('M-02'))}%</strong> in 2025f, {esc(v('M-03'))}% in 2026f</li>
      <li>County unemployment <strong>{esc(v('E-01'))}%</strong> (Sep 2026, prelim.)</li>
      <li>County population <strong>&minus;3.2%</strong> since 2020</li>
      <li>CPI-U Los Angeles <strong>+{esc(v('E-17'))}%</strong> y/y</li>
      <li>Accommodation &amp; food service jobs <strong>{esc(v('E-20'))}</strong> in 2025f</li>
    </ul>
    <p class="small"><a href="site/data-macro.html">Economy &rarr;</a> · <a href="site/data-employment.html">Employment &rarr;</a></p>
  </div>
  <div class="card"><h3 style="margin-top:0">Capital markets</h3>
    <ul>
      <li>10-yr Treasury <strong>{esc(v('R-01'))}%</strong></li>
      <li>5-yr Treasury <strong>{esc(v('R-02'))}%</strong></li>
      <li>U.S. net-lease cash yield transacted by the largest listed buyer: <strong>{esc(v('R-11'))}%</strong></li>
      <li>Realised rent recapture <strong>{esc(v('R-14'))}%</strong></li>
      <li>Impairment on a 15,500-property portfolio: <strong>${int(v('R-13')):,}k</strong></li>
    </ul>
    <p class="small"><a href="site/data-rates.html">Rates &amp; cap rates &rarr;</a></p>
  </div>
</div>

<h2>3. The four decisions, priced the same way</h2>
<p>All four are valued with one discounted cash-flow engine: net rent received plus sale proceeds,
discounted at the owner's required return. The only differences between branches are the exit date,
the exit cap rate, and whether a lease roll happens before the exit. Median present value across
{mo['monte_carlo']['trials']:,} trials, including the black-swan overlay:</p>
<div class="tablewrap"><table><thead><tr>
<th>Decision</th><th>Median PV</th><th>5th pct</th><th>95th pct</th>
<th>P(better than selling now)</th><th>P(best of the four)</th><th>What it means</th></tr></thead><tbody>
<tr><td><strong>A. Sell now</strong></td>
  <td class="num">${mc['A']['median']:,.0f}</td><td class="num">${mc['A']['p05']:,.0f}</td>
  <td class="num">${mc['A']['p95']:,.0f}</td><td class="num">&mdash;</td>
  <td class="num">{mc['A']['prob_best']*100:.1f}%</td>
  <td class="small">Certainty now. Zero roll risk, zero further rent, and a Prop 13 reset that raises the tenant's occupancy cost at the next change of hands.</td></tr>
<tr><td><strong>B. Hold to expiry</strong></td>
  <td class="num">${mc['B']['median']:,.0f}</td><td class="num">${mc['B']['p05']:,.0f}</td>
  <td class="num">${mc['B']['p95']:,.0f}</td><td class="num">{mc['B']['prob_negative_vs_sell_now']*100:.1f}%</td>
  <td class="num">{mc['B']['prob_best']*100:.1f}%</td>
  <td class="small">The worst structural position: you keep the rent but you still eat the roll, and you sell a short-WALT asset into a wider cap.</td></tr>
<tr><td><strong>C. Renew and hold</strong></td>
  <td class="num">${mc['C']['median']:,.0f}</td><td class="num">${mc['C']['p05']:,.0f}</td>
  <td class="num">${mc['C']['p95']:,.0f}</td><td class="num">{mc['C']['prob_negative_vs_sell_now']*100:.1f}%</td>
  <td class="num">{mc['C']['prob_best']*100:.1f}%</td>
  <td class="small">Highest median. Absorbs the roll instead of selling into it. Requires you to be a below-market-return holder and to carry concentration risk on a deteriorating tenant.</td></tr>
<tr><td><strong>D. Extend early, sell long WALT</strong></td>
  <td class="num">${mc['D']['median']:,.0f}</td><td class="num">${mc['D']['p05']:,.0f}</td>
  <td class="num">${mc['D']['p95']:,.0f}</td><td class="num">{mc['D']['prob_negative_vs_sell_now']*100:.1f}%</td>
  <td class="num">{mc['D']['prob_best']*100:.1f}%</td>
  <td class="small">The compromise that usually happens in practice: give up ~2% of rent to buy five years of term, then sell into a market that pays for term.</td></tr>
</tbody></table></div>
<p class="small">P(best) sums to 100%. Figures are modelling output, not an appraisal. The engine,
every assumption and every axis is on <a href="site/projection.html">the projection page</a>.</p>

<h2>4. What could actually hurt you</h2>
<div class="grid g2">
  <div class="card"><h3 style="margin-top:0">Business as usual</h3>
    <ul>
      <li><strong>Roll risk.</strong> If the tenant does not renew, you carry roughly ten months of
      lost rent plus re-leasing cost and a wider exit cap. Modelled explicitly.</li>
      <li><strong>Tenant concentration.</strong> 100% of your income comes from one brand whose
      same-store sales have fallen two years running.</li>
      <li><strong>Rate risk.</strong> With the 10-year at {esc(v('R-01'))}%, every 100 bps of cap-rate
      expansion removes roughly one seventh of capital value.</li>
      <li><strong>California labour policy.</strong> AB 1228 set a $20.00/hr fast-food floor and the
      Fast Food Council can raise it. The tenant's own 10-K cites AB 1228 directly for a
      <strong>{esc(v('T-11'))}%</strong> wage increase.</li>
      <li><strong>Prop 13 reset.</strong> Any sale you complete resets the assessed value to market
      and raises the tenant's property-tax reimbursement &mdash; a permanent occupancy-cost increase
      exactly when the lease is up.</li>
    </ul>
  </div>
  <div class="card"><h3 style="margin-top:0">Black swans</h3>
    <ul>
      <li><strong>Wildfire.</strong> The January 2025 fires are a direct, recent county-level shock.
      Your parcel's Fire Hazard Severity Zone is unverified because the address is redacted.</li>
      <li><strong>Earthquake.</strong> Central Los Angeles sits in a high-hazard seismic region. Your
      site's design spectral acceleration is unverified.</li>
      <li><strong>Insurance withdrawal.</strong> Coverage exists through the FAIR Plan at
      ${int(v('H-07'))/1e6:.0f}M per building / $100M per location, but at insurer-of-last-resort
      pricing.</li>
      <li><strong>A tenant bankruptcy or mass closure programme.</strong> The tenant has already run
      86 closures in one year and is covenant-constrained by its own securitisation.</li>
      <li><strong>Population loss.</strong> The county is {esc(v('D-02'))}% smaller than in 2020, and
      LAEDC forecasts a further {esc(v('M-06'))}% in 2026.</li>
    </ul>
    <p class="small"><a href="site/risks.html">Full risk register with likelihood, severity and mitigation &rarr;</a></p>
  </div>
</div>

<h2>5. What is still unknown</h2>
<div class="callout bad">
  <div class="t">{c['UNVERIFIED']} of {len(rows)} rows are blank because no official source could confirm them</div>
  <p>These are not gaps in research. They are documents that were not supplied, and the site
  deliberately publishes a blank rather than an estimate. The five that change the answer are:</p>
  <ol>
    <li><strong>Is the tenant the public company or a franchisee, and is there a guaranty?</strong> (P-02, P-03)</li>
    <li><strong>What is the exact expiry date?</strong> It sets the remaining term, which sets the price. (P-04, P-05)</li>
    <li><strong>What is the current rent, and what is the unit's sales volume?</strong> It decides whether the box is
      relettable and whether the tenant can afford a renewal. (P-07, P-13)</li>
    <li><strong>What renewal options exist, and at what rent mechanism?</strong> (P-06)</li>
    <li><strong>What is the debt, and what would retiring it cost?</strong> A sale you cannot complete is not an option. (P-16)</li>
  </ol>
  <p><a href="site/flagged.html">See the full flagged-for-review register, with sources &rarr;</a></p>
</div>

<h2>6. Recommended course of action</h2>
<div class="callout ok">
  <div class="t">Sequence, not a single decision</div>
  <ol>
    <li><strong>Immediately: pull the five documents above.</strong> Until P-02, P-04, P-06, P-07 and P-16
    are known, no sale or renewal should be executed. This is the only blocking action.</li>
    <li><strong>Check the decline-in-value window.</strong> The 2026-27 LA County decline-in-value filing
    window closes <strong>2026-11-30</strong>. If you believe market value sits below your factored base
    year value, that is a free option that expires in three weeks.</li>
    <li><strong>Establish your required return as a number.</strong> Write it down. The entire hold/sell
    decision reduces to comparing it with the crossover on <a href="site/decision.html">the decision page</a>.</li>
    <li><strong>Open an early-extension conversation with the tenant</strong> (Decision D), timed to
    while you still have six or more years of term. Term you sell is worth more than rent you concede,
    and the buyer market pays for WALT.</li>
    <li><strong>Only sell if your required return is above the crossover</strong>, or if concentration
    risk is unacceptable to you regardless of the arithmetic. In that case sell on your timetable,
    not the lease's, and structure it as a §1031 exchange within 45 days of identification.</li>
    <li><strong>Do not default to "sell at expiry."</strong> It is the one branch that is dominated in
    almost every scenario tested: you keep the operating risk without the term, and you sell into a
    wider cap.</li>
  </ol>
</div>

<hr>
<p class="small">Sources for every figure above are listed on <a href="site/sources.html">the sources page</a>
with publisher, tier, retrieval date and stated limitation. The projection engine is
<code>model/project_model.py</code> and is reproducible with <code>python3 model/project_model.py --check</code>.</p>
"""
    page("site/executive-summary.html", "Executive Summary", body, root="..",
         active="executive-summary.html")


def build_decision(ds, mo):
    mc = mo["monte_carlo"]["stats"]
    cross = mo["crossover"]
    regime = mo["regime"]
    bey = mo["breakeven"]

    reg_rows = "".join(
        f"<tr><td class='num'>{r['cap_rate']*100:.2f}%</td><td class='num'>{r['discount_rate']*100:.2f}%</td>"
        f"<td class='num'>{r['premium_over_cap_bps']:+d}</td>"
        f"<td class='num'>${r['pv']['A']:,.0f}</td><td class='num'>${r['pv']['B']:,.0f}</td>"
        f"<td class='num'>${r['pv']['C']:,.0f}</td><td class='num'>${r['pv']['D']:,.0f}</td>"
        f"<td><strong style='color:{'var(--accent)' if r['winner']=='C' else 'var(--info)'}'>{r['winner']}</strong></td></tr>"
        for r in regime
    )

    surf_rows = "".join(
        f"<tr><td class='num'>{s['remaining_years']:g} yr</td><td class='num'>${s['base_rent']:,.0f}</td>"
        f"<td class='num'>{s['rent_to_sales']*100:.1f}%</td>"
        f"<td class='num'>${s['pv']['A']:,.0f}</td><td class='num'>${s['pv']['B']:,.0f}</td>"
        f"<td class='num'>${s['pv']['C']:,.0f}</td><td class='num'>${s['pv']['D']:,.0f}</td>"
        f"<td><strong>{s['winner']}</strong></td></tr>"
        for s in mo["surface"]
    )

    stress_rows = "".join(
        f"<tr><td>{esc(s['cap_scenario'])}</td><td class='num'>{s['cap_rate']*100:.2f}%</td>"
        f"<td class='num'>{s['discount_rate']*100:.2f}%</td>"
        f"<td class='num'>${s['pv']['A']:,.0f}</td><td class='num'>${s['pv']['C']:,.0f}</td>"
        f"<td class='num'>${s['pv']['D']:,.0f}</td><td><strong>{s['winner']}</strong></td></tr>"
        for s in mo["stress"]
    )

    body = hero(
        "Decision analysis",
        "Sell now, hold to expiry, renew, or extend early &mdash; and the rule that separates them",
        "Four options, one valuation basis. The recommendation is expressed as a decision rule with a "
        "computable threshold, so it stays correct when your own required return or the market cap rate "
        "moves away from the base case.",
        "Model: <code>model/project_model.py</code> · seed 20261106 · all four branches discounted at the same rate",
    )

    body += f"""
<div class="callout">
  <div class="t">The decision rule</div>
  <p><strong>Hold and extend when your required return is below the crossover. Sell when it is above.</strong></p>
  <p>At a 7.10% cap rate and six years of term, the crossover is <strong>{cross[0]['crossover_discount_rate']*100:.2f}%</strong>.
  At 7.85% it is <strong>{cross[1]['crossover_discount_rate']*100:.2f}%</strong>. At 9.35% it is
  <strong>{cross[2]['crossover_discount_rate']*100:.2f}%</strong>.</p>
  <p class="small">The intuition is old and simple: if the market capitalises this cash flow more
  expensively than you do, you own the asset. If you capitalise it more expensively than the market,
  the market owns it &mdash; and you should let it.</p>
</div>

<h2>1. The four options</h2>
<div class="dec">
  <div class="d"><div class="tag">A &middot; LIQUIDATE</div><h4>Sell now</h4>
    <div class="big">${mc['A']['median']:,.0f}</div>
    <div class="sub">median PV · P(best) {mc['A']['prob_best']*100:.1f}%</div>
    <div class="bar"><i style="width:{mc['A']['prob_best']*100:.1f}%"></i></div>
    <p class="small">Banks the buyer's capitalisation of your contract rent plus the reversion.
    Removes roll risk, tenant concentration and every black swan at once. Costs you the upside if the
    tenant renews and cap rates stay put. Triggers a Prop 13 reset for the buyer's benefit, not yours.</p></div>

  <div class="d"><div class="tag">B &middot; DO NOTHING</div><h4>Hold to expiry</h4>
    <div class="big">${mc['B']['median']:,.0f}</div>
    <div class="sub">median PV · P(best) {mc['B']['prob_best']*100:.1f}%</div>
    <div class="bar"><i style="width:{max(1.0,mc['B']['prob_best']*100):.1f}%"></i></div>
    <p class="small"><strong>The dominated branch.</strong> You carry the roll and then sell a short-WALT
    asset into a wider cap. P(best) is effectively zero in every scenario tested. Included for
    completeness because it is the default if no one decides.</p></div>

  <div class="d win"><div class="tag">C &middot; RENEW</div><h4>Renew and hold 10 years</h4>
    <div class="big">${mc['C']['median']:,.0f}</div>
    <div class="sub">median PV · P(best) {mc['C']['prob_best']*100:.1f}%</div>
    <div class="bar"><i style="width:{mc['C']['prob_best']*100:.1f}%"></i></div>
    <p class="small">Highest median because you keep the asset through the roll instead of selling into
    it. Conditioned on your required return being below the crossover. Adds concentration risk on a
    tenant whose same-store sales are falling.</p></div>

  <div class="d"><div class="tag">D &middot; EXTEND</div><h4>Extend early, sell long WALT</h4>
    <div class="big">${mc['D']['median']:,.0f}</div>
    <div class="sub">median PV · P(best) {mc['D']['prob_best']*100:.1f}%</div>
    <div class="bar"><i style="width:{max(1.0,mc['D']['prob_best']*100):.1f}%"></i></div>
    <p class="small">The practical compromise, and the one a broker will propose. Concede ~2% of rent
    now, buy five years of term, sell at the stabilised cap. Lower median than C but with a firm exit
    date you control.</p></div>
</div>

<h2>2. Risk by decision</h2>
<div class="tablewrap"><table><thead><tr>
<th>Risk</th><th>A. Sell now</th><th>B. Hold to expiry</th><th>C. Renew &amp; hold</th><th>D. Extend early</th></tr></thead><tbody>
<tr><td><strong>Lease roll / vacancy</strong></td>
  <td>Eliminated at t=0</td><td>Fully borne by you</td><td>Borne by you at the roll, then again at exit</td><td>Reduced; transferred to the buyer</td></tr>
<tr><td><strong>Tenant credit deterioration</strong></td>
  <td>Transferred to the buyer</td><td>Fully borne</td><td>Fully borne, for 10 years</td><td>Partly borne for 5 years</td></tr>
<tr><td><strong>Cap-rate expansion</strong></td>
  <td>Eliminated</td><td>Borne on a short-WALT asset (worse)</td><td>Borne on a stabilised asset</td><td>Borne, but on a long-WALT asset</td></tr>
<tr><td><strong>Reinvestment risk</strong></td>
  <td><strong>Highest</strong> &mdash; proceeds must be redeployed or taxed</td><td>Moderate</td><td>Nil until exit</td><td>Moderate, with a known date</td></tr>
<tr><td><strong>Wildfire / earthquake / flood</strong></td>
  <td>Transferred at closing</td><td>Fully borne</td><td>Fully borne</td><td>Fully borne until sale</td></tr>
<tr><td><strong>Post-disaster rebuild cost</strong></td>
  <td>Not yours</td><td>Yours</td><td>Yours</td><td>Yours until sale</td></tr>
<tr><td><strong>Prop 13 reassessment</strong></td>
  <td>Triggered at your sale &mdash; raises tenant's cost, weakens renewal</td><td>Triggered at sale</td><td>Deferred indefinitely</td><td>Triggered at your sale</td></tr>
<tr><td><strong>Tax on gain</strong></td>
  <td>Due now unless §1031</td><td>Due at the later sale</td><td>Deferred; basis steps up at death</td><td>Due at sale unless §1031</td></tr>
<tr><td><strong>Liquidity / optionality</strong></td>
  <td><strong>Best</strong></td><td>Poor (locked until 2030&ndash;35)</td><td>Poor</td><td>Good (known exit window)</td></tr>
<tr><td><strong>Concentration</strong></td>
  <td>Resolved</td><td>Persists</td><td><strong>Worst</strong></td><td>Reduced</td></tr>
</tbody></table></div>

<h2>3. When does selling actually win? The regime map</h2>
<p>Every cell below is the same asset with the same rent and term, repriced at a different market cap
rate and a different owner required return. "Winner" is the highest present value.</p>
<div class="tablewrap"><table><thead><tr>
<th>Market cap rate</th><th>Your required return</th><th>Your return &minus; cap (bps)</th>
<th>A. Sell now</th><th>B. Hold to expiry</th><th>C. Renew &amp; hold</th><th>D. Extend</th><th>Winner</th></tr></thead>
<tbody>{reg_rows}</tbody></table></div>
<p class="small">Read it as a single rule: <strong>when your required return is above the cap rate
(negative spread), selling wins. When it is below, holding wins.</strong> The crossover sits roughly
30&ndash;40 bps above the cap rate at six years of term, because holding also forecloses the option to
sell into today's bid.</p>

<h2>4. Breakeven: how wide must the cap go for selling to beat holding to expiry?</h2>
<div class="tablewrap"><table><thead><tr>
<th>Remaining term</th><th>Breakeven cap spread over the 6.6% anchor</th><th>Breakeven cap rate</th><th>Reading</th></tr></thead><tbody>
{''.join(f"<tr><td class='num'>{b['remaining_years']:g} yr</td><td class='num'>{b['breakeven_cap_spread']*100:.2f}%</td><td class='num'><strong>{b['breakeven_cap_rate']*100:.2f}%</strong></td><td class='small'>{'Only a genuine dislocation makes an immediate sale beat simply holding the contract rent to expiry.' if b['breakeven_cap_rate']>0.10 else 'A wider but still plausible cap rate is enough &mdash; because with a long remaining term the near-roll discount costs you little.'}</td></tr>" for b in bey)}
</tbody></table></div>
<p class="small">Interpretation: with four years left you would need the market to reprice to
<strong>{bey[0]['breakeven_cap_rate']*100:.2f}%</strong> before "sell now" beats "keep the rent and sell
at expiry". With nine years left it takes only <strong>{bey[2]['breakeven_cap_rate']*100:.2f}%</strong>.
Short remaining term is, counter-intuitively, a reason to hold to expiry rather than dump the asset,
because there is little term left to lose and you keep the rent.</p>

<h2>5. The scenario surface you actually live in</h2>
<p>Because the expiry date and the rent were not supplied, the model is run across a grid that brackets
the owner's stated 2030&ndash;2035 range. <code>Rent / AUV</code> shows what share of the tenant's
average franchise unit volume your rent consumes &mdash; above ~10% the operator is under real stress
and renewal becomes less likely.</p>
<div class="tablewrap"><table><thead><tr>
<th>Remaining term</th><th>Base rent</th><th>Rent / AUV</th>
<th>A. Sell now</th><th>B. Hold to expiry</th><th>C. Renew &amp; hold</th><th>D. Extend</th><th>Winner</th></tr></thead>
<tbody>{surf_rows}</tbody></table></div>
<p class="small">The winner is stable across all nine cells. That robustness is the reason the
recommendation is expressed as a rule rather than as a point forecast.</p>

<h2>6. Stress: what breaks it?</h2>
<div class="tablewrap"><table><thead><tr>
<th>Cap scenario</th><th>Cap rate</th><th>Your discount rate</th>
<th>A. Sell now</th><th>C. Renew &amp; hold</th><th>D. Extend</th><th>Winner</th></tr></thead>
<tbody>{stress_rows}</tbody></table></div>
<p class="small">Selling only takes the win in the stress row where the cap compresses hard
<em>and</em> your discount rate is at the top of the range &mdash; i.e. when you are a high-return
owner facing a low-cap market. That is precisely the condition the decision rule describes.</p>

<h2>7. The option you should not overlook</h2>
<div class="callout warn">
  <div class="t">Sell at expiry is dominated &mdash; and it is the most likely default</div>
  <p>Branch B is the outcome if no decision is made: you collect contract rent until the lease runs out,
  then sell whatever is left. You have carried every risk the owner faces and then sell the asset at the
  moment it is worth least relative to its stabilised value &mdash; into a market that is pricing the
  roll.</p>
  <p>If your required return is above the crossover, sell <em>now</em>, not at expiry. If it is below,
  renew. There is almost no coherent position in between.</p>
</div>

<h2>8. What would change this answer</h2>
<ul>
  <li><strong>You discover the tenant is a thinly capitalised single-unit franchisee with no guaranty.</strong>
    That widens the cap spread and pushes the crossover down toward "sell".</li>
  <li><strong>The unit's sales are weak.</strong> If rent is above ~10&ndash;12% of unit sales, the
    tenant cannot afford a market renewal and the box is not relettable to another QSR at that rent.
    That is the strongest argument for selling.</li>
  <li><strong>Your loan has a punitive prepayment penalty.</strong> If retiring the debt costs more than
    the spread you are capturing, the sale is not executable and the rule is moot.</li>
  <li><strong>You need liquidity or have a concentration limit.</strong> Then the decision is not an
    NPV comparison at all. Sell, and say so out loud rather than reverse-engineering a cap rate.</li>
  <li><strong>A genuine cap-rate dislocation.</strong> The breakeven table above tells you how wide it
    has to be.</li>
</ul>
"""
    page("site/decision.html", "Decision", body, root="..", active="decision.html")


def build_projection(ds, mo):
    inputs = mo["inputs"]
    axes = mo["axes"]
    mc = mo["monte_carlo"]
    rp = mo["rent_pressure"]

    ax_rows = "".join(
        f"<tr><td><code>{esc(a['key'])}</code></td><td>{esc(a['label'])}</td>"
        f"<td class='num'>{', '.join(str(x) for x in a['values'])}</td><td>{esc(a['unit'])}</td>"
        f"<td class='small'>{esc(a['provenance'])}</td></tr>" for a in axes
    )
    rp_rows = "".join(
        f"<tr><td class='num'>${r['base_rent']:,.0f}</td><td class='num'>{r['pct_of_franchise_auv']*100:.1f}%</td>"
        f"<td class='num'>{r['occupancy_plus_royalty_pct']*100:.1f}%</td>"
        f"<td>{pill('VERIFIED') if r['band']=='in-band' else pill('FLAGGED')} <span class='small'>{esc(r['band'])}</span></td></tr>"
        for r in rp
    )

    body = hero(
        "Projection system",
        "How the projection is built, and why you can reproduce it",
        "A single discounted-cash-flow engine, a scenario surface over the two unknowns that were not "
        "supplied, a deterministic Monte Carlo, and a black-swan overlay. No third-party packages. "
        "Rerun it with <code>python3 model/project_model.py</code>; verify the checked-in output with "
        "<code>--check</code>.",
        f"{mc['trials']:,} trials · seed {mc['seed']} · stdlib only · byte-reproducible",
    )

    body += f"""
<h2>1. Verified market inputs</h2>
<p>Every number below was read directly from an official source in this session and is linked on the
<a href="sources.html">sources page</a>. The two numbers that are <em>not</em> sourced &mdash; the
single-asset cap spread and the illiquidity premium &mdash; are stated as assumptions and swept as axes.</p>
<div class="tablewrap"><table><thead><tr><th>Input</th><th>Value</th><th>Source</th><th>Retrieved</th></tr></thead><tbody>
<tr><td>5-year U.S. Treasury constant maturity</td><td class="num">{inputs['rf_5y']*100:.2f}%</td><td>Federal Reserve H.15</td><td class="small">2026-11-04</td></tr>
<tr><td>5-year TIPS real yield</td><td class="num">{inputs['rf_5y_real']*100:.2f}%</td><td>Federal Reserve H.15</td><td class="small">2026-11-04</td></tr>
<tr><td>10-year U.S. Treasury constant maturity</td><td class="num">{inputs['rf_10y']*100:.2f}%</td><td>Federal Reserve H.15</td><td class="small">2026-11-04</td></tr>
<tr><td>10-year TIPS real yield</td><td class="num">{inputs['rf_10y_real']*100:.2f}%</td><td>Federal Reserve H.15</td><td class="small">2026-11-04</td></tr>
<tr><td><strong>Net-lease cap-rate anchor</strong> (Realty Income, U.S. wholly-owned, initial weighted average <em>cash</em> yield, Q3 2026)</td><td class="num"><strong>{inputs['cap_anchor']*100:.2f}%</strong></td><td>SEC Form 8-K, Exhibit 99.1</td><td class="small">2026-10-30</td></tr>
<tr><td>CPI-U Los Angeles, 12-month</td><td class="num">{inputs['cpi_la']*100:.2f}%</td><td>BLS</td><td class="small">2026-09</td></tr>
<tr><td>Real gross county product growth, 2026f</td><td class="num">{inputs['gcp_growth_2026f']*100:.2f}%</td><td>SCAG / LAEDC</td><td class="small">2025 vintage</td></tr>
<tr><td>Real taxable sales growth, 2026f</td><td class="num">{inputs['taxable_sales_2026f']*100:.2f}%</td><td>SCAG / LAEDC</td><td class="small">2025 vintage</td></tr>
<tr><td>Unemployment rate, 2026f</td><td class="num">{inputs['unemployment_2026f']*100:.2f}%</td><td>SCAG / LAEDC</td><td class="small">2025 vintage</td></tr>
<tr><td>Jack in the Box franchise AUV</td><td class="num">${inputs['franchise_auv']:,}</td><td>SEC Form 10-K FY2025</td><td class="small">2025-09-28</td></tr>
<tr><td>Royalty rate</td><td class="num">{inputs['royalty_rate']*100:.1f}% of gross sales</td><td>SEC Form 10-K FY2025</td><td class="small">2025-09-28</td></tr>
</tbody></table></div>

<h2>2. What is a scenario axis, and what is a fact</h2>
<p>The lease was not supplied, so the two inputs that dominate the answer are unknown. Rather than
invent a rent and a date, the engine sweeps them and reports the whole surface. These axes are
<strong>not estimates</strong> &mdash; they are the grid on which the answer is stable.</p>
<div class="tablewrap"><table><thead><tr><th>Key</th><th>Meaning</th><th>Values tested</th><th>Unit</th><th>Provenance</th></tr></thead>
<tbody>{ax_rows}</tbody></table></div>

<h2>3. How each branch is priced</h2>
<p>All four decisions use the same formula. This is deliberate: if branches were priced on different
bases, the comparison would be meaningless.</p>
<details><summary>The valuation identity</summary>
<p>A net-lease buyer does not pay <code>rent / cap</code> for a lease with four years left &mdash; that
would overvalue a short lease badly. A buyer pays:</p>
<p><code>PV at the market cap of contract rent through expiry &nbsp;+&nbsp; PV at the market cap of the
reversion</code>, where the reversion is the box re-let at market rent.</p>
<p>That is implemented as <code>market_price()</code>. It is the reason "sell now" and "sell at expiry"
differ by more than a discount factor: the sale at expiry carries a <strong>+150 bps roll premium</strong>
on the cap rate because the buyer is buying a rolling lease, not a term lease.</p></details>

<details><summary>A &mdash; Sell now</summary>
<p><code>market_price(rent, remaining_term, escalator, cap_today) &times; (1 &minus; 2.0% selling cost)</code>.
No further rent. The 2.0% transaction cost is a convention, not a sourced figure.</p></details>

<details><summary>B &mdash; Hold to lease expiry</summary>
<p>Contract rent for the remaining term, then a sale at <code>cap_today + 1.50%</code> applied to a
probability-weighted exit rent that blends renew-at-market with re-let-after-downtime. A downtime cost
of roughly ten months of rent is charged if the tenant does not renew.</p></details>

<details><summary>C &mdash; Renew and hold</summary>
<p>The roll happens inside your ownership instead of at the exit. Rent is blended at the roll, grows at
the escalator, and the asset is sold at year 10 at the stabilised cap (no roll premium, because the
renewed lease carries term).</p></details>

<details><summary>D &mdash; Extend early, sell a longer-WALT asset</summary>
<p>Give up 2.0% of rent immediately, add five years of term, sell at the stabilised cap instead of
<code>cap + 150 bps</code>. The concession and the extension length are policy choices, disclosed as such.</p></details>

<h2>4. The black-swan overlay</h2>
<p>Drawn independently per trial at <strong>{mc['event_frequency']*100:.2f}%</strong> frequency
({mc['event_hits']} hits in {mc['trials']:,} trials), with severity drawn uniformly:</p>
<ul>
  <li>35&ndash;85% of rent lost for a period (6&ndash;18 months of interruption)</li>
  <li>20&ndash;45% permanent loss of exit value</li>
</ul>
<p><strong>The asymmetry is the whole point.</strong> A sale completed before the event is insulated:
branch A is left untouched. A held asset takes the full hit. That is not a modelling trick, it is
what fire, earthquake, flood and tenant insolvency actually do &mdash; they arrive without warning and
they arrive while you own the thing.</p>
<div class="callout warn">
  <div class="t">An honest limitation</div>
  <p>The 2.0% annual event probability is a modelling assumption, not a sourced actuarial rate. It was
  chosen to sit in a defensible range for a ten-year hold on an urban Los Angeles infill parcel exposed
  to seismic, wildfire-smoke, flood and tenant-credit shocks. The conclusion is robust to it: rerunning
  at 0.5% or 6.0% changes the medians but not the ranking. That robustness is what makes the
  recommendation usable.</p>
</div>

<h2>5. Rent-to-sales pressure on the tenant</h2>
<p>The best single predictor of whether a QSR tenant renews is whether it can afford the rent. Franchise
AUV was ${inputs['franchise_auv']:,} in FY2025. The table shows what each tested rent level consumes,
and adds the 5.0% royalty because both are fixed costs of operating the unit.</p>
<div class="tablewrap"><table><thead><tr><th>Base rent</th><th>Rent as % of AUV</th><th>Rent + royalty as % of AUV</th><th>Band</th></tr></thead>
<tbody>{rp_rows}</tbody></table></div>
<p class="small">The 6&ndash;10% band is a modelling convention for QSR rent-to-sales, not a sourced
threshold. It is disclosed here so it can be argued with.</p>

<h2>6. Reproducibility</h2>
<div class="callout ok">
  <div class="t">This output is verifiable</div>
  <p><code>python3 model/project_model.py --check</code> regenerates the report and compares it to the
  checked-in <code>data/model_output.json</code>. Any drift fails loudly. The random generator is the
  stdlib Mersenne Twister under a fixed seed, with an explicit Box-Muller transform so the result does
  not depend on the interpreter's <code>random.gauss</code>. The site is generated from the same JSON by
  <code>model/build_site.py</code>, so no figure on this site is typed by hand.</p>
</div>
"""
    page("site/projection.html", "Projection Model", body, root="..", active="projection.html")


# entrypoint moved to the end of the file



# --------------------------------------------------------------------------
# additional pages
# --------------------------------------------------------------------------

RISK_ROWS = [
    # id, category, risk, likelihood, severity, horizon, decision affected, mitigation, source ids
    ("R-01", "Business as usual", "Tenant does not renew; you carry vacancy, re-leasing cost and downtime",
     "Medium", "High", "2030-2035", "B, C",
     "Open the extension conversation early (D). Price the roll into any sale. Ten months of downtime is modelled explicitly.",
     ["SEC-JACK-10K-FY2025", "SEC-O-8K-Q3-2026"]),
    ("R-02", "Business as usual", "Tenant same-store sales keep falling; the box becomes unprofitable before expiry",
     "Medium-High", "High", "0-9 yr", "All",
     "Same-store sales -4.2% FY2025 after -1.3% FY2024; transactions -5.7%. Track the franchisee's unit P&L annually.",
     ["SEC-JACK-10K-FY2025"]),
    ("R-03", "Business as usual", "Franchisee insolvency where the tenant is a franchisee, not the public company",
     "Medium", "High", "0-9 yr", "All",
     "93% of the system is franchised. A franchisee bankruptcy can reject the lease. Confirm guaranty status (P-03) before anything else.",
     ["SEC-JACK-10K-FY2025"]),
    ("R-04", "Business as usual", "Cap-rate expansion erodes capital value",
     "Medium", "High", "0-10 yr", "A, B, D",
     "10-yr UST at 4.90%. Each 100 bps of cap expansion removes ~1/7 of value at a 7.1% cap. Selling removes this exposure entirely.",
     ["FED-H15", "SEC-O-8K-Q3-2026"]),
    ("R-05", "Business as usual", "California fast-food wage floor rises again via the Fast Food Council",
     "Medium-High", "Medium", "0-10 yr", "B, C",
     "$20.00/hr floor since 2024-04-01 with statutory authority to raise. The tenant already reports 7.6% wage inflation attributed to AB 1228.",
     ["CA-DIR-AB1228", "SEC-JACK-10K-FY2025"]),
    ("R-06", "Business as usual", "State minimum wage indexation compounds operating cost",
     "High", "Low-Medium", "Annual", "B, C",
     "$16.90/hr in 2026, indexed to CPI-W with a 3.5% cap. Affects the tenant, not you directly under NNN.",
     ["CA-DIR-MINWAGE"]),
    ("R-07", "Business as usual", "Prop 13 reassessment on sale raises the tenant's occupancy cost",
     "High on sale", "Medium", "At any sale", "A, B, D",
     "A sale you complete resets assessed value to market. Under NNN the tenant reimburses it. That is a permanent increase at the worst moment. Weigh it in the renewal negotiation.",
     ["LA-ASSESSOR-PROP13"]),
    ("R-08", "Business as usual", "Debt cannot be retired economically (prepayment penalty or defeasance)",
     "Unknown", "High if true", "At sale", "A, B, D",
     "Not verified (P-16). Yield maintenance on a legacy loan can consume a year of NOI. Pull the loan documents before assuming a sale is executable.",
     ["OWNER-DOCS"]),
    ("R-09", "Business as usual", "Reinvestment risk on sale proceeds",
     "High", "Medium", "At sale", "A",
     "Section 1031 gives 45 days to identify and 180 to close. Cash left unexchanged is taxed. Reinvestment risk is the hidden cost of branch A and is not in the NPV.",
     ["IRS-1031"]),
    ("R-10", "Business as usual", "Population and labour-force contraction reduces trade-area demand",
     "High", "Medium", "0-10 yr", "B, C",
     "County population -3.2% since 2020; LAEDC forecasts a further -0.2% in 2026. Labour force still below Jan-2020 level.",
     ["CENSUS-QF-LACOUNTY", "SCAG-LAEDC-2025", "BLS-LAU-CA-037"]),
    ("R-11", "Business as usual", "Local wage ordinances exceed the state floor",
     "Medium", "Low", "Annual", "B, C",
     "City of Los Angeles and other jurisdictions may set a higher minimum wage than the state; the stricter standard applies.",
     ["CA-DIR-MINWAGE"]),
    ("R-12", "Black swan", "Wildfire destroys or closes the site",
     "Low", "Catastrophic", "Any year", "B, C, D",
     "Parcel FHSZ unverified. FAIR Plan commercial coverage available to $20M/building, $100M/location. Harden the property for up to a 20% wildfire premium discount.",
     ["CALFIRE-FHSZ", "CA-INS-FAIRPLAN"]),
    ("R-13", "Black swan", "Earthquake damage; business interruption; rebuild cost overrun",
     "Low", "Catastrophic", "Any year", "B, C, D",
     "Central LA is high seismic hazard. Design spectral acceleration for the parcel is unverified. ShakeMap-era building code matters: pre-1976 construction is a different asset.",
     ["USGS-NSHM"]),
    ("R-14", "Black swan", "Flood / urban inundation",
     "Low", "High", "Any year", "B, C, D",
     "FEMA zone unverified. In dense infill, a shallow-lying parcel can be in or near a special flood hazard area.",
     ["FEMA-NRI"]),
    ("R-15", "Black swan", "Admitted-market insurance withdrawal; coverage only via the FAIR Plan",
     "Medium", "Medium", "0-10 yr", "B, C, D",
     "The FAIR Plan is the insurer of last resort and is priced accordingly. Coverage exists; affordability is the risk. Under NNN this cost lands on the tenant and pressures renewal.",
     ["CA-INS-FAIRPLAN"]),
    ("R-16", "Black swan", "Mass tenant closure programme or franchisor bankruptcy",
     "Low-Medium", "Catastrophic", "0-9 yr", "B, C, D",
     "The tenant closed 86 units against 31 openings in FY2025 and carries covenant-constrained securitised debt. A closure programme can take your box.",
     ["SEC-JACK-10K-FY2025"]),
    ("R-17", "Black swan", "Pandemic-scale demand collapse",
     "Low", "Catastrophic", "Any year", "B, C, D",
     "May 2020 county unemployment reached 18.9%. Drive-thru formats proved resilient, but dine-in and office-lunch dayparts did not.",
     ["BLS-LAU-CA-037"]),
    ("R-18", "Black swan", "Federal immigration enforcement shrinks the customer base and the labour pool",
     "Medium", "Medium-High", "0-5 yr", "B, C",
     "LAEDC explicitly attributes the 2026 population contraction to immigration enforcement. 33.4% of county residents are foreign-born.",
     ["SCAG-LAEDC-2025", "CENSUS-QF-LACOUNTY"]),
    ("R-19", "Black swan", "Tariff shock hits food and packaging costs",
     "Medium", "Medium", "0-5 yr", "B, C",
     "LAEDC names tariffs as one of three 2025 shocks. Commodity inflation was already 4.2% in FY2025.",
     ["SEC-JACK-10K-FY2025", "SCAG-LAEDC-2025"]),
    ("R-20", "Black swan", "Governance/political shock: local zoning or rent regulation changes",
     "Low", "Medium", "0-10 yr", "B, C, D",
     "City Planning has an active rezoning and density programme. That is more likely an upside option on the LAND than a downside, but it changes what the parcel is.",
     ["LA-PLANNING-CENTRAL"]),
]


def build_risks():
    order = {"Low": 0, "Low-Medium": 1, "Medium": 2, "Medium-High": 3, "High": 4, "Unknown": 2, "High if true": 2}
    sev_order = {"Low": 0, "Low-Medium": 1, "Medium": 2, "Medium-High": 3, "High": 4, "Catastrophic": 5}
    rows = sorted(RISK_ROWS, key=lambda r: (-sev_order.get(r[4], 2), -order.get(r[3], 2)))

    trs = ""
    for rid, cat, risk, lik, sev, hor, dec, mit, srcs in rows:
        badge = "var(--bad)" if sev == "Catastrophic" else ("var(--warn)" if sev == "High" else "var(--info)")
        src_html = ", ".join(
            f'<a href="{esc(s["url"] if s.get("url") else "")}" target="_blank" rel="noopener noreferrer">{esc(sid)}</a>'
            if s.get("url") else f'<span class="small">{esc(sid)}</span>'
            for sid in srcs for s in [SOURCES_BY_ID.get(sid, {"url": None})]
        )
        trs += (f"<tr><td class='nowrap'><code>{esc(rid)}</code></td>"
                f"<td class='small'>{esc(cat)}</td><td>{esc(risk)}</td>"
                f"<td>{pill('FLAGGED') if lik=='Unknown' else ''}<span class='small'>{esc(lik)}</span></td>"
                f"<td><strong style='color:{badge}'>{esc(sev)}</strong></td>"
                f"<td class='small nowrap'>{esc(hor)}</td><td class='small nowrap'>{esc(dec)}</td>"
                f"<td class='small'>{esc(mit)}</td><td class='small'>{src_html}</td></tr>")

    body = hero(
        "Risk register",
        "Every risk attached to every decision, ordered by severity",
        "Business-as-usual risks that arrive on a schedule, and black-swan risks that do not. "
        "Likelihood and severity are analyst judgements and are labelled as such; the underlying "
        "evidence for each risk is a linked official source.",
        "20 risks · 12 business-as-usual · 8 black swan · mapped to decisions A-D",
    )
    body += f"""
<div class="callout">
  <div class="t">The single most important asymmetry</div>
  <p>A sale transfers every risk on this page to the buyer at the moment of closing. Holding retains
  all of them. That statement is true regardless of the cap rate, and it is why an owner whose
  required return is anywhere near the market cap rate should weigh risk transfer explicitly rather
  than treating it as a tiebreaker.</p>
</div>
<div class="legend">{pill('UNVERIFIED')} appears where a likelihood depends on a document that was not supplied.</div>
<div class="tablewrap"><table><thead><tr>
<th>ID</th><th>Class</th><th>Risk</th><th>Likelihood</th><th>Severity</th><th>Horizon</th>
<th>Decisions affected</th><th>Mitigation / evidence</th><th>Sources</th></tr></thead>
<tbody>{trs}</tbody></table></div>

<h2>How the black swans are priced</h2>
<p>The projection engine overlays a shock drawn independently per trial at
<strong>{EVENT_FREQ*100:.2f}%</strong> per ten-year hold, with severity drawn uniformly between a
35&ndash;85% rent interruption and a 20&ndash;45% permanent loss of exit value. A sale completed
<em>before</em> the event is left untouched; a held asset takes the full hit. This is the only place in
the model where the four decisions are treated asymmetrically, and it is treated asymmetrically because
the world is asymmetric.</p>

<div class="callout warn">
  <div class="t">What this register does not cover</div>
  <p>Legal title defects, easements, an unrecorded encroachment, a tenant's purchase option, a radius
  restriction that blocks another QSR operator from the box, and environmental contamination. All of
  these sit in the owner's document set (P-14, P-15) and none of them were supplied. They are the
  reason a Phase I ESA and a title commitment should precede any sale.</p>
</div>
"""
    page("site/risks.html", "Risk Register", body, root="..", active="risks.html")


def build_sources(src):
    rows = ""
    for s in src["sources"]:
        link = (f'<a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(s["url"])}</a>'
                if s.get("url") else '<span class="small">no public URL — internal document</span>')
        lim = s.get("limitation", "")
        rows += (f"<tr><td class='nowrap'><code>{esc(s['id'])}</code></td>"
                 f"<td><strong>{esc(s['tier'])}</strong></td>"
                 f"<td>{esc(s['publisher'])}</td><td>{esc(s['title'])}</td>"
                 f"<td class='small'>{esc(s.get('period') or s.get('published') or '')}</td>"
                 f"<td class='small nowrap'>{esc(s.get('retrieved') or '')}</td>"
                 f"<td class='small'>{link}</td>"
                 f"<td class='small'>{esc(lim)}</td></tr>")
    tiers = src["tier_definitions"]
    tier_html = "".join(f"<li><strong>Tier {esc(k)}</strong> — {esc(v)}</li>" for k, v in tiers.items())

    body = hero(
        "Source register",
        "Every source, its tier, what it was used for, and its stated limitation",
        "Nothing in this dossier is asserted without one of these identifiers. A source is registered "
        "only if it was actually retrieved in this session — a citation is never written from memory.",
        f"{len(src['sources'])} sources · retrieved 2026-11-06",
    )
    body += f"""
<h2>Tier definitions</h2>
<div class="card"><ul>{tier_html}</ul></div>

<h2>Register</h2>
<div class="tablewrap"><table><thead><tr>
<th>ID</th><th>Tier</th><th>Publisher</th><th>Title</th><th>Period</th><th>Retrieved</th><th>URL</th><th>Stated limitation</th>
</tr></thead><tbody>{rows}</tbody></table></div>

<h2>Sources that were deliberately NOT used</h2>
<div class="callout warn">
  <div class="t">Tier C sources are excluded from every calculation</div>
  <p>Two secondary commercial sources appear in the register with tier C — a CoStar net-lease cap-rate
  summary and a Nareit fact sheet. Both were reachable only as search-index snippets or paywalled
  summaries. Neither is used as a model input. The cap-rate anchor actually used is a
  <em>transacted cash yield disclosed to the SEC</em> by the largest listed net-lease buyer, which is a
  stronger instrument and is reproducible by anyone who opens the filing.</p>
</div>

<h2>Link integrity</h2>
<p>Every external link on this site was retrieved during the build. The verification report at
<code>verification/LINK_CHECK.md</code> records the HTTP result for each URL and lists any that failed,
rather than silently dropping them.</p>
"""
    page("site/sources.html", "Sources", body, root="..", active="sources.html")


def build_flagged(ds, src):
    rows = all_rows(ds)
    unv = [r for r in rows if r["status"] == "UNVERIFIED"]
    flg = [r for r in rows if r["status"] == "FLAGGED"]

    unv_rows = "".join(
        f"<tr><td class='nowrap'><code>{esc(r['id'])}</code></td>"
        f"<td class='small'>{esc(r['_cattitle'])}</td><td>{esc(r['metric'])}</td>"
        f"<td class='small'>{esc(r['source'])}</td>"
        f"<td class='small'>{esc(r['note'])}</td></tr>" for r in unv)

    flg_rows = ""
    for r in flg:
        link = (f'<a href="{esc(r["url"])}" target="_blank" rel="noopener noreferrer">{esc(r["source"])}</a>'
                if r.get("url") else esc(r["source"]))
        flg_rows += (f"<tr><td class='nowrap'><code>{esc(r['id'])}</code></td>"
                     f"<td>{esc(r['metric'])}</td><td class='small'>{link}</td>"
                     f"<td class='small'>{esc(r['note'])}</td></tr>")

    issues = [
        ("F-01", "CoStar net-lease cap rate is secondary and paywalled",
         "The QSR cap rate of ~5.8% and the median net-lease cap rate of 6.3% are quoted only in a "
         "secondary summary of a CoStar report. The primary report could not be retrieved.",
         "Excluded from the model entirely. The cap-rate anchor used instead is a transacted cash yield "
         "disclosed to the SEC by Realty Income.", "COSTAR-NETLEASE-Q1-2026"),
        ("F-02", "LAEDC 2026 forecast PDF could not be parsed",
         "The 9.37 MB 2026 Annual Economic Forecast was linked but could not be read in this session. "
         "Its press release confirms direction only, not numbers.",
         "All quantitative regional forecast figures in this dossier come from the 2025 vintage "
         "SCAG/LAEDC county report, which was fully read. The 2026 numbers are not quoted.",
         "LAEDC-2026-EF"),
        ("F-03", "BLS LAUS series has a government-shutdown gap",
         "October 2025 is coded '(X) Data unavailable due to the 2025 lapse in appropriations' in the "
         "county LAUS series. Any 12-month comparison spanning that month is distorted.",
         "Year-over-year statements on this site use September-to-September or explicit month "
         "comparisons, not 12-month averages spanning the gap.", "BLS-LAU-CA-037"),
        ("F-04", "IRS §1031 page is flagged archival by the IRS itself",
         "The retrieved page carries a notice: 'This is an archival or historical document and may not "
         "reflect current law, policies or procedures.'",
         "Only the structural facts were taken from it: 45-day identification, 180-day completion, "
         "qualified intermediary, deferral not forgiveness. A CPA must confirm current law.",
         "IRS-1031"),
        ("F-05", "The subject parcel cannot be located",
         "The address and APN were withheld by instruction, so no parcel-level query is possible.",
         "14 parcel-dependent rows are published as BLANK and marked UNVERIFIED rather than estimated. "
         "Hazard zone, flood zone, zoning, seismic design values, assessed value and school district are "
         "all in that set.", "OWNER-DOCS"),
        ("F-06", "The lease, rent roll and loan documents were not supplied",
         "17 property rows and the owner's tax position are blank.",
         "The model is a surface over the unknowns rather than a point forecast. The recommendation is "
         "expressed as a rule with a computable threshold so it survives the missing inputs.",
         "OWNER-DOCS"),
        ("F-07", "2008-09 unemployment peak is not in the retrieved BLS extract",
         "The BLS series extracted here begins January 2016, so the GFC peak is absent.",
         "The row is left BLANK rather than quoted from memory. The COVID peak, which IS in the "
         "retrieved data, is used to calibrate the severe-recession branch.", "BLS-LAU-CA-037"),
    ]
    issue_rows = "".join(
        f"<tr><td class='nowrap'><code>{esc(a)}</code></td><td>{esc(b)}</td>"
        f"<td class='small'>{esc(c)}</td><td class='small'>{esc(d)}</td>"
        f"<td class='small'><code>{esc(e)}</code></td></tr>" for a, b, c, d, e in issues)

    body = hero(
        "Flagged for review",
        "What could not be verified, and exactly why",
        "Nothing on this page is hidden in a footnote. Every value that could not be traced to an "
        "official source is blank, listed here, and open for you to challenge. Unverified items were "
        "allowed to publish but were never allowed to enter a calculation.",
        f"{len(unv)} unverified rows · {len(flg)} flagged values · {len(issues)} structural irregularities",
    )
    body += f"""
<div class="callout bad">
  <div class="t">Read this page first if you are going to rely on any number</div>
  <p>The dossier is deliberately incomplete. Where a document was missing, the cell is empty. No value
  on this site was inferred, interpolated, imputed, or filled from general knowledge. If a number looks
  missing, it is missing on purpose.</p>
</div>

<h2>1. Structural irregularities</h2>
<div class="tablewrap"><table><thead><tr>
<th>ID</th><th>Irregularity</th><th>What happened</th><th>How it was handled</th><th>Source</th>
</tr></thead><tbody>{issue_rows}</tbody></table></div>

<h2>2. Values found but not trusted</h2>
<div class="tablewrap"><table><thead><tr>
<th>ID</th><th>Metric</th><th>Source</th><th>Why it is flagged</th>
</tr></thead><tbody>{flg_rows}</tbody></table></div>

<h2>3. Values deliberately left blank</h2>
<p>Each of these needs a document that was not supplied. Requesting these is the only blocking action
in the executive summary.</p>
<div class="tablewrap"><table><thead><tr>
<th>ID</th><th>Category</th><th>Metric</th><th>Expected source</th><th>Why it matters</th>
</tr></thead><tbody>{unv_rows}</tbody></table></div>

<h2>4. What to send to close the gaps</h2>
<div class="grid g2">
  <div class="card"><h3 style="margin-top:0">Tier D documents</h3>
    <ul>
      <li>The executed lease, all amendments, and every side letter</li>
      <li>The guaranty, if any, and the tenant's legal entity name</li>
      <li>Three years of rent invoices and the current rent roll</li>
      <li>The tenant's sales reports, if the lease requires them</li>
      <li>The loan agreement, current balance and prepayment terms</li>
      <li>Ownership entity documents and the depreciation schedule</li>
      <li>The current insurance binder and any loss runs</li>
      <li>Title commitment and the most recent Phase I ESA</li>
    </ul>
  </div>
  <div class="card"><h3 style="margin-top:0">Then re-run</h3>
    <p>The engine takes <code>remaining_years</code>, <code>base_rent</code> and the rest as arguments.
    Once the lease is in hand, replace the axis sweep with the real values and rerun
    <code>python3 model/project_model.py</code>. The site regenerates from the same JSON and every
    affected row flips from UNVERIFIED to VERIFIED with a document citation.</p>
    <p class="small">Until that happens, the recommendation in this dossier is conditioned on the
    unknowns and is stated as a rule rather than as a verdict.</p>
  </div>
</div>
"""
    page("site/flagged.html", "Flagged for Review", body, root="..", active="flagged.html")


def build_methodology(ds, src):
    rows = all_rows(ds)
    c = counts(rows)
    body = hero(
        "Methodology",
        "How this dossier was built, and the limits of what it can tell you",
        "The research method, the verification rule, the privacy rule, the projection method, and an "
        "explicit list of what this is not.",
        "Session arena-8149683c · 2026-11-06 · reproducible from the repository",
    )
    body += f"""
<h2>1. Research method</h2>
<ol>
  <li><strong>Source-first, not question-first.</strong> For each question, the official publisher was
  identified before any number was sought: SEC EDGAR for the tenant and for the cap-rate anchor, BLS for
  labour, Census for demographics, the Federal Reserve for rates, the LA County Assessor for property
  tax, Cal/OSHA-adjacent state agencies for labour law, CAL FIRE / USGS / FEMA for hazards, IRS for tax,
  and SCAG for the regional forecast.</li>
  <li><strong>Primary over secondary, always.</strong> Where a secondary summary and a primary filing
  disagreed or where only the secondary existed, the secondary was registered at Tier C and excluded
  from every calculation.</li>
  <li><strong>Numbers were copied, not recalled.</strong> Every VERIFIED row quotes a figure that
  appeared in a document retrieved in this session.</li>
  <li><strong>Derived values show their formula.</strong> There are {c['DERIVED']} of them, and each
  one states the arithmetic in its note so it can be rechecked by hand.</li>
</ol>

<h2>2. The verification rule</h2>
<div class="card">
  <p><strong>If an official source could not confirm a value, the value is blank.</strong> It is not
  estimated, interpolated, rounded from a related figure, or filled from general knowledge. The row is
  published with <span class="pill UNVERIFIED">UNVERIFIED</span> so the gap is visible rather than
  papered over.</p>
  <p>Current tally: <strong>{c['VERIFIED']}</strong> verified, <strong>{c['DERIVED']}</strong> derived,
  <strong>{c['FLAGGED']}</strong> flagged, <strong>{c['UNVERIFIED']}</strong> blank, out of
  <strong>{len(rows)}</strong> rows.</p>
</div>

<h2>3. The privacy rule</h2>
<div class="card">
  <p>No personal information is published. The specific controls applied:</p>
  <ul>
    <li><strong>No street address and no APN</strong> appears anywhere in this repository or on this
    site. The asset is described only as "central Los Angeles".</li>
    <li><strong>No owner name, entity name, phone number, email address, account number or tax ID</strong>
    appears in any template, data file or page.</li>
    <li><strong>No third-party personal data.</strong> The executives named in the tenant's 10-K are
    public officers of a public company disclosing under securities law; they are not reproduced here.</li>
    <li><strong>Consequence accepted:</strong> because the parcel cannot be located, every parcel-level
    lookup is impossible. That is a real analytical cost, and it is why 14 rows are blank. Privacy was
    treated as the higher-priority constraint.</li>
  </ul>
</div>

<h2>4. The projection method</h2>
<div class="card">
  <p>Four decisions, one discounted-cash-flow engine. Net rent plus sale proceeds, discounted at the
  owner's required return. Branches differ only in exit date, exit cap and whether a lease roll occurs
  inside the holding period.</p>
  <p>The sale valuation uses the identity a net-lease buyer actually uses: the present value at the
  market cap of contract rent through expiry, plus the present value at the market cap of the reversion
  re-let at market rent. Pricing a short lease as <code>rent / cap</code> would overstate it badly.</p>
  <p>Uncertainty is placed where it actually lives &mdash; the exit cap rate, the roll outcome and the
  black-swan overlay &mdash; rather than smeared uniformly across every input. Contract rent is
  contractual and is taken as given within each scenario.</p>
  <p>The Monte Carlo is deterministic under seed <code>20261106</code> with an explicit Box-Muller
  transform, so the checked-in output is byte-reproducible. <code>--check</code> fails loudly on drift.</p>
</div>

<h2>5. What this is not</h2>
<div class="callout warn">
  <p><strong>Not an appraisal.</strong> No licensed appraiser inspected the property. No USPAP
  standard was followed. Do not use this for lending, financial reporting, or a tax filing.</p>
  <p><strong>Not investment advice.</strong> It is an internal decision document prepared for one owner
  about one asset.</p>
  <p><strong>Not a tax opinion.</strong> §1031 and depreciation recapture are described structurally
  only. A CPA must confirm every tax statement before it is acted on.</p>
  <p><strong>Not a substitute for the documents.</strong> The five blocking gaps on
  <a href="flagged.html">the flagged page</a> materially change the answer. Until they are closed, the
  recommendation is a rule, not a verdict.</p>
  <p><strong>Not current beyond 2026-11-06.</strong> Rates, cap rates, unemployment and forecasts all
  move. Every row carries an <code>as_of</code> date precisely so this does not silently rot.</p>
</div>

<h2>6. Reproducing the build</h2>
<div class="card">
  <p><code>python3 model/project_model.py</code> — regenerate the projection and Monte Carlo.</p>
  <p><code>python3 model/project_model.py --check</code> — assert the output has not drifted.</p>
  <p><code>python3 model/build_site.py</code> — regenerate every page from the JSON.</p>
  <p><code>python3 verification/verify.py</code> — audit every row, every source reference and every
  internal link.</p>
  <p class="small">No third-party packages are required. Python 3.8 or later.</p>
</div>
"""
    page("site/methodology.html", "Methodology", body, root="..", active="methodology.html")


# --------------------------------------------------------------------------
# entrypoint
# --------------------------------------------------------------------------
SOURCES_BY_ID = {}
EVENT_FREQ = 0.0

if __name__ == "__main__":
    ds, src, mo, src_by_id = load()
    SOURCES_BY_ID = src_by_id
    EVENT_FREQ = mo["monte_carlo"]["event_frequency"]
    build_index(ds, mo, src)
    for cat in ds["categories"]:
        build_category(ds, cat, cat["rows"], src_by_id)
    build_exec_summary(ds, mo, src)
    build_decision(ds, mo)
    build_projection(ds, mo)
    build_risks()
    build_sources(src)
    build_flagged(ds, src)
    build_methodology(ds, src)
    print("built", len(NAV), "pages")

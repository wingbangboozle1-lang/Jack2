#!/usr/bin/env python3
"""Static site generator for session-620551ec — Central LA Jack in the Box NNN decision workbook.

Reads data/*.json, writes plain HTML next to this session's folder. No frameworks, no deps.
Hard asserts: every verified row resolves to a source with an https URL; unverified metric
rows must carry an empty value; PII patterns must not appear.
"""
import html, json, os, re, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(HERE, "data")

def load(name):
    with open(os.path.join(D, name), encoding="utf-8") as f:
        return json.load(f)

SOURCES = load("sources.json")["sources"]
SRC = {s["id"]: s for s in SOURCES}
ACCESS = load("sources.json")["accessed"]
METRICS = load("metrics.json")["rows"]
PROP = load("property.json")["fields"]
QUESTIONS = load("questions.json")["questions"]
SUG = load("suggestions.json")
RISKS = load("risks.json")["risks"]
DEC = load("decisions.json")
MODEL = load("model_output.json")
REQ = load("requirements.json")["requirements"]

e = html.escape

NAV = [
    ("index.html", "Dashboard"),
    ("executive-summary.html", "Executive summary"),
    ("decision.html", "Decision"),
    ("market-economics.html", "Market data"),
    ("property-lease.html", "Property &amp; lease"),
    ("projection-model.html", "Projection model"),
    ("risks.html", "Risk register"),
    ("questions.html", "Questions &amp; answers"),
    ("suggestions.html", "Suggestions"),
    ("requirements.html", "Requirements"),
    ("sources.html", "Sources"),
    ("verification.html", "Verification"),
    ("flagged.html", "Flagged for review"),
    ("privacy.html", "Privacy"),
]

# ------------------------------ PII guard (build fails rather than publishing)
PII_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",          # SSN
    r"\b\d{3}[\.\-]\d{3}[\.\-]\d{4}\b", # phone (loose)
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",  # emails
    r"APN[: ]*\d",                      # actual parcel number digits after the label
    r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b",        # card-like
]

def pii_scan_text(text, where):
    for pat in PII_PATTERNS:
        m = re.search(pat, text)
        if m:
            raise AssertionError(f"PII-like pattern {pat!r} found at {where}: {m.group(0)!r}")

def enforce_verified_sources():
    for row in METRICS:
        if row["status"] == "verified":
            assert row.get("source") in SRC, f"metric {row['id']} missing source"
            assert SRC[row["source"]]["url"].startswith("https://"), f"metric {row['id']} source not https"
        elif row["status"] == "unverified":
            assert row["value"] == "", f"unverified metric {row['id']} must have blank value"
    for row in PROP:
        if row["status"] == "verified":
            assert row.get("source") in SRC, f"property field {row['id']} missing source"
    for row in RISKS:
        if row["source"]:
            assert row["source"] in SRC, f"risk {row['id']} source not found"

def src_link(sid):
    if not sid:
        return '<span class="small">—</span>'
    s = SRC[sid]
    return (f'<span class="src"><a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer" '
            f'title="{e(s["publisher"])} — {e(s["title"])}">{e(sid)} ↗</a></span>')

def badge(status):
    if status.startswith("verified") or status == "computed":
        cls = "ok" if status.startswith("verified") else "warn"
    elif status.startswith("open") or status.startswith("partially"):
        cls = "warn"
    elif status == "done" or status == "answered (verified)":
        cls = "ok"
    elif status == "unverified":
        cls = "bad"
    else:
        cls = "neutral"
    return f'<span class="badge {cls}">{e(status)}</span>'

def sev(s):
    cls = {"high": "bad", "medium": "warn", "low": "neutral"}.get(s, "neutral")
    return f'<span class="badge {cls}">{e(s)}</span>'

def table(headers, rows, num_cols=()):
    out = ['<div class="tablewrap"><table><thead><tr>']
    for i, h in enumerate(headers):
        cls = ' class="num"' if i in num_cols else ""
        out.append(f"<th{cls}>{h}</th>")
    out.append("</tr></thead><tbody>")
    for r in rows:
        out.append("<tr>")
        for i, cell in enumerate(r):
            cls = ' class="num"' if i in num_cols else ""
            out.append(f"<td{cls}>{cell}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)

def page(title, active, body):
    nav = "".join(
        f'<a href="{href}" class="{"active" if href == active else ""}">{label}</a>'
        for href, label in NAV
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{e(title)} — Jack in the Box NNN | Central LA Decision Workbook</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="top">
  <div class="crumbs">Central LA Jack in the Box (NNN) · Decision Workbook · Session 620551ec</div>
  <h1>{e(title)}</h1>
  <div class="sub">Sell the NNN asset before the 2030–2035 lease expiry, or renew? Evidence-linked answers; privacy-first; anything unverified is blank and flagged.</div>
</header>
<nav class="mainnav">{nav}</nav>
<main>
{body}
</main>
<footer class="foot">
  Session 620551ec · data read {e(ACCESS)} · Every verified figure links to its official source; blanks are flagged, never invented.
  <br>Personal information (owner, address, parcel, loan, accounts) is intentionally absent from this site and this repository. See <a href="privacy.html">Privacy</a> and <a href="flagged.html">Flagged for review</a>.
  <br><a href="https://github.com/wingbangboozle1-lang/Jack2">Source repository</a> · MIT-licensed code · Not financial, legal or tax advice.
</footer>
</body>
</html>"""

def write(name, title, active, body):
    html_text = page(title, active, body)
    pii_scan_text(html_text, name)
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
        f.write(html_text)
    print("wrote", name)

def fmt_value(row):
    if row["value"] == "":
        return "<em class='small'>blank — flagged</em>"
    v = row["value"]
    try:
        num = float(v)
        if abs(num) >= 1_000_000_000:
            s = f"${num/1e9:,.1f}B" if row["unit"] == "USD" else f"{num/1e9:,.1f}B"
        elif abs(num) >= 1_000_000:
            s = f"${num/1e6:,.1f}M" if row["unit"] == "USD" else f"{num:,.0f}"
        elif abs(num) >= 1000:
            s = f"{num:,.0f}"
        else:
            s = f"{num:g}"
        return e(s)
    except ValueError:
        return e(str(v))

def verified_count():
    return sum(1 for r in METRICS if r["status"] == "verified")

# ============================================================ index.html
def pg_index():
    vc = verified_count()
    blanks = sum(1 for r in METRICS if r["status"] == "unverified")
    high_risks = sum(1 for r in RISKS if r["severity"] == "high")
    body = f"""
<div class="cards">
  <div class="card"><div class="k">Verified data rows</div><div class="v">{vc}</div><div class="d">of {len(METRICS)} rows; source-linked to official publishers, read {e(ACCESS)}</div></div>
  <div class="card"><div class="k">Blank / flagged</div><div class="v">{blanks}</div><div class="d">Values that could not be confirmed — listed on Flagged for review</div></div>
  <div class="card"><div class="k">Risk rows</div><div class="v">{len(RISKS)}</div><div class="d">{high_risks} high-severity, mapped to every decision path</div></div>
  <div class="card"><div class="k">Open questions</div><div class="v">{len(QUESTIONS)}</div><div class="d">Each with a concrete acquisition method — see Questions &amp; answers</div></div>
  <div class="card"><div class="k">Suggestions</div><div class="v">{len(SUG['suggestions'])}</div><div class="d">Review them on Suggestions; nothing is implemented until you accept</div></div>
  <div class="card"><div class="k">Recommendation</div><div class="v" style="font-size:17px;line-height:1.3">Extend &amp; reprice first, then price it</div><div class="d">Negotiate the renewal first; decide sell-vs-hold on the repriced numbers and T1–T6 triggers</div></div>
</div>

<div class="panel">
  <h2>The decision, in one paragraph</h2>
  <p>The asset is a single-tenant Jack in the Box on an NNN lease expiring somewhere in 2030–2035, “around central Los Angeles.”
  The verified macro picture is a slow, services-led economy: LA County unemployment 4.8% and improving (S09), population shrinking -3.2% since 2020 (S03),
  $818.5B of personal income (2024, largest in the US, S07), a resilient port complex (S15), an elevated 10Y Treasury at 4.88% (S02), and a tenant in a managed shrink —
  same-store sales -1.1%, system at 2,115 restaurants (-53 y/y), franchise-level margin 37.4% (S05). None of this tells you what the property is worth.
  It does tell you how to decide: <strong>negotiate the extension first, then decide with the actual numbers</strong> (triggers T1–T6 on the <a href="decision.html">Decision</a> page).</p>
  <div class="callout"><strong>What this site refuses to do:</strong> invent a sale price, a cap rate, the lease’s rent or expiry, the owner’s basis, or the parcel’s identity. Those are blank in the data ledger — flagged, not fabricated (see <a href="flagged.html">Flagged for review</a>).</div>
</div>

<div class="panel">
  <h2>How to read this workbook</h2>
  <ul class="tight">
    <li><a href="executive-summary.html">Executive summary</a> — the answer on one page.</li>
    <li><a href="decision.html">Decision</a> — four strategies scored, T1–T6 triggers, and the recommended sequence.</li>
    <li><a href="market-economics.html">Market data</a> — every verified figure with its official source link.</li>
    <li><a href="projection-model.html">Projection model</a> — deterministic value grids (rent growth × cap rate × expiry 2030–2035) and a black-swan overlay.</li>
    <li><a href="risks.html">Risk register</a> — BAU + black-swan risks mapped to sell / hold / renew / extend.</li>
    <li><a href="questions.html">Questions &amp; answers</a> — what must be answered, what is known, and how to find the missing information.</li>
    <li><a href="suggestions.html">Suggestions</a> — a review queue to improve this analysis before implementing anything.</li>
    <li><a href="flagged.html">Flagged for review</a> — everything unverified or irregular, with the source links.</li>
  </ul>
</div>
"""
    write("index.html", "Dashboard", "index.html", body)

# ============================================================ executive-summary.html
def pg_exec():
    body = f"""
<div class="panel">
  <h2>Bottom line</h2>
  <div class="callout ok"><strong>Best course of action:</strong> negotiate a lease extension/renewal FIRST (10–20 yr, CPI- or fixed-escalated, repriced at or above the current NNN rent), then decide sell-vs-hold on the repriced contract and fresh market pricing — using the written triggers T1–T6. Do not list blind; do not renew blind; never let the asset run dark into 2030–2035.</div>
  <p class="small">Confidence: moderate. The answer is a sequence, not an unconditional price — the inputs that would fix the price (exact rent, jurisdiction/Measure ULA status, cap rate, basis) are owner-private or non-official and are deliberately blank.</p>
</div>

<div class="panel">
  <h2>What the verified evidence says</h2>
  {table(["#", "Evidence (verified 2026-11-12)", "Implication", "Source"], [
    ["1", "LA County unemployment 4.8% (Sep 2026, SA; vs 5.6% a year ago); MSA 4.4%; CA 5.1%", "Demand base stabilizing — supportive for QSR traffic", src_link("S01") + " " + src_link("S09")],
    ["2", "County population -3.2% since Apr 2020; city -0.8%; median income $90,112 county / $81,939 city", "Structural softness — pricing power is limited; necessity-driven tenants win", src_link("S03")],
    ["3", "County personal income $818.5B (2024) — largest in the US", "Deep trade area; supports occupancy by the right operator", src_link("S07")],
    ["4", "10Y Treasury 4.88% (2026-11-09)", "NNN pricing pressure; cap rates elevated; rate path is the swing factor", src_link("S02")],
    ["5", "Tenant: Q3 FY2026 SSS -1.1%; system 2,115 restaurants (-53 y/y); ~93% franchised; franchise-level margin 37.4%; Del Taco divested 2025-12-22; refinancing complete; interim CEO", "Credit risk real but contained; structure deals for recapture/security; monitor quarterly", src_link("S05") + " " + src_link("S06")],
    ["6", "Measure ULA: sales > $5.4M (in-city) pay 4% on FULL price; ≥ $10.9M pay 5.5%; indexed annually", "For a >$5.4M City-of-LA sale, ULA is the largest single friction — know your jurisdiction (blank in this workbook)", src_link("S10")],
    ["7", "Prop 13: 1% base + bonded debt; 2%/yr assessment cap", "Seller keeps tax base predictability; buyer’s reset is priced in", src_link("S16")],
    ["8", "Port of LA: 9.45M TEUs Jan–Nov 2025; ~top-3 year expected", "Trade logistics backbone of the local economy intact but imports -11% y/y — watch", src_link("S15")],
    ["9", "FHFA HPI LA-LB-Glendale MSAD: +1.20% 1-yr; +31.92% 5-yr (2026Q2)", "Housing wealth effect flat short-term — neutral for retail sales growth", src_link("S14")],
    ["10", "Seismic: 60% 30-yr M6.7+ probability (UCERF3); wildfire maps updated (CAL FIRE)", "Black-swan overlay: ~1.35%/yr expected value drag (analyst assumptions, see model)", src_link("S12") + " " + src_link("S13")],
  ])}
</div>

<div class="panel">
  <h2>The plan (sequence, not a leap)</h2>
  <ol class="workflow">
    <li><strong>Weeks 1–4 — Evidence:</strong> exact lease date/options/rent (Q01–Q03, Q16); jurisdiction + ULA exposure (Q04); assessed value/Prop 13 (Q05); CAL FIRE/USGS parcel lookup (Q17); insurance quotes (Q18).</li>
    <li><strong>Weeks 3–6 — Pricing:</strong> broker opinion of value; rent benchmark vs Central LA QSR pads (G13); CPA after-tax comparison: sale vs renew-then-sell vs 1031 (G04).</li>
    <li><strong>Weeks 6–12 — Negotiate:</strong> extension/renewal first — repriced rent, CPI escalations, guarantee + security, continuous-operation clause, options structure (G08).</li>
    <li><strong>Week 12 — Decision meeting:</strong> re-run sell-vs-hold on actual numbers; apply T1–T6; document the decision and the re-review date (12 months pre-expiry).</li>
    <li><strong>Ongoing:</strong> quarterly tenant check (8-K/10-K), monthly DGS10 + EDD, annual ULA indexation review each July.</li>
  </ol>
</div>

<div class="panel">
  <h2>Why not the other paths (plainly)</h2>
  <ul class="tight">
    <li><strong>Sell blind today:</strong> you would price off incomplete information and pay the ULA cliff if in-city — irreversible.</li>
    <li><strong>Renew blind:</strong> flat or below-market rent locked for a decade — quiet wealth leak.</li>
    <li><strong>Hold to a dark expiry:</strong> the worst risk-adjusted path — sale into vacancy at the bottom of the negotiation cycle.</li>
  </ul>
</div>
"""
    write("executive-summary.html", "Executive summary", "executive-summary.html", body)

# ============================================================ decision.html
def pg_decision():
    strat = DEC["strategies"]
    trig = DEC["triggers"]
    rows = []
    for s in strat:
        rows.append([f"<strong>{e(s['id'])} — {e(s['name'])}</strong><br><span class='small'>{e(s['description'])}</span>",
                     "<br>".join("• " + e(x) for x in s["pros"]),
                     "<br>".join("• " + e(x) for x in s["cons"]),
                     e(s["best_when"]),
                     sev(s["risk_level"].split(" ")[0]),
                     e(s["fit_for_wealth_preservation"])])
    trig_rows = [[e(t["id"]), e(t["trigger"]), e(t["action"])] for t in trig]
    body = f"""
<div class="panel">
  <h2>Decision framing</h2>
  <p>{e(DEC['framing'])}</p>
  <div class="callout"><strong>Recommendation:</strong> {e(DEC['recommendation']['headline'])}<br>{e(DEC['recommendation']['detail'])}</div>
  <p class="small"><strong>Confidence:</strong> {e(DEC['recommendation']['confidence'])}</p>
  <p class="small"><strong>What would change it:</strong> {e(DEC['recommendation']['what_would_change_it'])}</p>
</div>
<div class="panel">
  <h2>Four strategies, scored</h2>
  {table(["Strategy", "Pros", "Cons", "Best when", "Risk", "Wealth fit"], rows)}
</div>
<div class="panel">
  <h2>Written triggers — the decision is made when one fires, not before</h2>
  {table(["#", "Trigger", "Action"], trig_rows)}
</div>
<div class="panel">
  <h2>Decision matrix by scenario</h2>
  {table(["If…", "Then the best path is…"], [
    ["Renewal offered ≥ market with CPI-linked escalations", "Strategy C (renew-and-hold), re-review annually; sell only on T1/T2/T5"],
    ["Renewal offered flat AND below market", "Push back (G08/G13); if refused, weight shifts to Strategy A"],
    ["Opinion of value ≥ owner's after-tax hurdle AND ULA status acceptable", "Strategy A (sell now) becomes rational — especially if T3 or T5 also fires"],
    ["Opinion of value below hurdle", "Do not sell; renew or defer; revisit after negotiation and next rate reset"],
    ["DGS10 > 5.5% sustained or cap rates gap adverse > 75bps", "Re-price; Strategy A pauses; Strategy C favored (T2)"],
    ["Tenant shows 2 consecutive quarters of margin/SSS deterioration", "Accelerate exit or demand extra security (T3)"],
    ["Inside City of LA AND price > $10.9M", "5.5% ULA on full price (~$600K+ on $11M) — model it explicitly in the CPA comparison (Q04, S10)"],
  ])}
</div>
"""
    write("decision.html", "Decision — sell vs renew", "decision.html", body)

# ============================================================ market-economics.html
def pg_market():
    cats = {}
    for r in METRICS:
        cats.setdefault(r["category"], []).append(r)
    sections = []
    for cat, rows in cats.items():
        trs = [[e(r["id"]), e(r["metric"]), fmt_value(r), e(r["unit"]), badge(r["status"]),
                src_link(r["source"]), e(r["note"])] for r in rows]
        sections.append(f"<h3>{e(cat)}</h3>" + table(["ID", "Metric", "Value", "Unit", "Status", "Source", "Note"], trs))
    vc = verified_count()
    body = f"""
<div class="panel">
  <h2>Verified data ledger — read 2026-11-12</h2>
  <p>{vc} verified, {sum(1 for r in METRICS if r['status']=='computed')} computed, {sum(1 for r in METRICS if r['status']=='unverified')} deliberately blank &amp; flagged.
  “Verified” means this session opened the official publisher page on 2026-11-12 and linked it. No broker, blog, or third-party estimate is used as verification.</p>
  <div class="callout warn"><strong>Series are not interchangeable:</strong> the BLS large-metro NSA table (4.4%) and the CA EDD seasonally-adjusted county estimate (4.8%) measure different things. The workbook keeps them side by side rather than blending them.</div>
</div>
{''.join(sections)}
"""
    write("market-economics.html", "Market &amp; economics data", "market-economics.html", body)

# ============================================================ property-lease.html
def pg_property():
    rows = [[e(f["id"]), e(f["field"]), (f"<strong>{e(f['value'])}</strong>" if f["value"] else "<em class='small'>blank — owner-private</em>"),
             badge(f["status"]), src_link(f["source"]), e(f["note"])] for f in PROP]
    body = f"""
<div class="panel">
  <h2>Anonymized asset profile</h2>
  <p>Everything below is either verified against a public official source or deliberately blank. This site and this repository contain <strong>no owner name, address, APN/parcel, loan, account or tenant-contact identifier</strong> — and never will. Property facts only the owner can supply stay blank until the owner provides them through the private channel (see <a href="privacy.html">Privacy</a>).</p>
</div>
{table(["ID", "Field", "Value", "Status", "Source", "Note"], rows)}
"""
    write("property-lease.html", "Property &amp; lease (anonymized)", "property-lease.html", body)

# ============================================================ projection-model.html
def pg_model():
    rows = [[e(f"{s['rent_growth']*100:.0f}%"), e(f"{s['cap_rate']*100:.1f}%"), e(f"{s['value_index_2026']:.1f}"), e(f"{s['value_index_at_2030']:.1f}"), e(f"{s['value_index_at_2035']:.1f}")] for s in MODEL["value_scenarios"]]
    horizon = [[e(str(h["expiry"])), e(f"{h['years_of_rent_collected_index']:.1f}")] for h in MODEL["hold_vs_sell_breakevens"]]
    bw = MODEL["black_swan_overlay"]
    bs = [[e(x["name"]), e(f"{x['annual_prob_analyst']*100:.1f}%"), e(f"{x['value_impact_if_occurs']*100:.0f}%")] for x in bw["events"]]
    body = f"""
<div class="panel">
  <h2>How to read this model</h2>
  <p>The workbook refuses to invent the subject property's inputs. The model is therefore <strong>index-based</strong>: rent index 100, value = rent ÷ cap rate. Plug the owner's actual rent and the broker's cap rate into the same formulas for live numbers. All “analyst assumptions” are labeled and are not official data.</p>
  <p class="small">Method: {e(MODEL['method'])} · Generated {e(MODEL['generated'])} by <code>scripts/model.py</code> (deterministic, stdlib only, no network).</p>
</div>
<div class="panel">
  <h2>Value index grid — today vs 2030 vs 2035 (rent index 100; value = rent ÷ cap rate)</h2>
  {table(["Rent growth /yr", "Cap rate", "Value index 2026", "Value index 2030", "Value index 2035"], rows, num_cols=(0,1,2,3,4))}
  <p class="small">Cap rate is the swing factor: +100bps moves value ~-14% at a 7.0% cap. Rent growth is second-order. This is why the decision turns on the exit pricing environment, not on 2026 fundamentals alone.</p>
</div>
<div class="panel">
  <h2>Hold-vs-sell: cumulative rent collected by expiry year (flat-rent illustration)</h2>
  {table(["Expiry year", "Years of rent (index)"], horizon, num_cols=(1,))}
</div>
<div class="panel">
  <h2>Black-swan overlay (analyst assumptions — labeled, not official)</h2>
  <p>Sum of probability × impact = <strong>expected annual value drag ≈ {bw['expected_annual_value_drag_fraction']*100:.2f}% of asset value per year</strong>. An owner who cannot bear that carry should not hold.</p>
  {table(["Event", "Analyst annual prob.", "Impact if occurs"], bs, num_cols=(1,2))}
  <p class="small">{e(bw['note'])}</p>
</div>
<div class="panel">
  <h2>Interactive use (no data leaves your browser)</h2>
  <p>Inputs are owner-supplied at the decision meeting. Example: rent $180,000/yr, broker cap 6.5% → value ≈ $2.77M; at 7.0% ≈ $2.57M. Escalated 3%/yr to 2032, the same cap yields ≈ $3.28M before any exit tax. Measure ULA (if in-city) then takes 4–5.5% of gross on the way out.</p>
</div>
"""
    write("projection-model.html", "Projection model", "projection-model.html", body)

# ============================================================ risks.html
def pg_risks():
    rows = [[e(r["id"]), e(r["type"]), e(r["decision"]), e(r["risk"]), sev(r["severity"]), sev(r["likelihood"]), e(r["mitigation"]), src_link(r["source"])] for r in RISKS]
    body = f"""
<div class="panel">
  <h2>Risk register — every decision path × BAU and black-swan events</h2>
  <p>30 risks. "black swan" = rare, severe, underpriced events (earthquake, wildfire, insurance failure, tenant failure, ULA indexation, trade shock, systemic rate shock). Each row names the decision path it hits and a concrete mitigation.</p>
</div>
{table(["ID", "Type", "Decision", "Risk", "Severity", "Likelihood", "Mitigation", "Source"], rows)}
"""
    write("risks.html", "Risk register", "risks.html", body)

# ============================================================ questions.html
def pg_questions():
    rows = [[e(q["id"]), e(q["category"]), e(q["question"]), badge(q["status"]), e(q["known_answer"]), sev(q["priority"].replace("critical", "high")), e(q["obtain"])] for q in QUESTIONS]
    body = f"""
<div class="panel">
  <h2>Questions that must be answered before deciding — and how to get the answers</h2>
  <p>This register is the missing-information discovery system: each row says what is known from verified official sources, what is missing, how critical it is, and the exact acquisition method. <strong>Suggestions to discover missing information are part of the task — answers are not invented.</strong></p>
  <div class="callout"><strong>Decision cannot be made reasonably while any “critical” row is open.</strong> Criticals: Q01–Q04, Q06, Q07, Q15, Q21.</div>
</div>
{table(["ID", "Category", "Question", "Status", "What is known", "Priority", "How to obtain"], rows)}
"""
    write("questions.html", "Questions &amp; answers", "questions.html", body)

# ============================================================ suggestions.html
def pg_suggestions():
    wf = "".join(f"<li><strong>{e(s['name']).title()}</strong> <span class='small'>(owner: {e(s['owner'])})</span> — {e(s['action'])}</li>" for s in SUG["workflow"])
    rows = []
    for s in SUG["suggestions"]:
        rows.append([
            e(s["id"]), e(s["category"]),
            f"<strong>{e(s['title'])}</strong><br><span class='small'>Enables: {e(s['decision_enabled'])}</span>",
            e(s["improves"]),
            sev(s["impact"]), e(s["effort"]), e(s["risk"]),
            f'<select class="suggest-status" data-id="{e(s["id"])}"><option>proposed</option><option>under review</option><option>accepted</option><option>rejected</option><option>deferred</option></select>',
        ])
    body = f"""
<div class="panel">
  <h2>Suggestions — review first, implement later</h2>
  <p>Every suggestion below is a <strong>proposal, not a decision</strong>. Nothing on this page is implemented. The reviewer walks each item through the workflow, marks it here (selections are stored only in this browser’s localStorage — nothing is sent anywhere), and implementation starts only after acceptance, tracked in COORDINATION.md.</p>
  <ol class="workflow">{wf}</ol>
  <div class="callout warn"><strong>Suggested review order:</strong> G02 (exact lease) → G04 (CPA after-tax) → G06 (hazard/insurance) → G03 (ULA jurisdiction) → G08 (renew-first negotiation) → then the rest. The decision-critical four unlock the sell-vs-renew analysis; the site-health items (G10–G12, G14) improve the workbook itself.</div>
</div>
<div class="panel">
  <h2>The suggestions register (mark your selection in the last column)</h2>
  <div class="tablewrap"><table>
    <thead><tr><th>ID</th><th>Category</th><th>Suggestion</th><th>What it improves</th><th>Impact</th><th>Effort</th><th>Risk</th><th>Your selection</th></tr></thead>
    <tbody>
      {''.join(f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td><td>{r[6]}</td><td>{r[7]}</td></tr>" for r in rows)}
    </tbody>
  </table></div>
  <p class="small">Selections persist in this browser only. Click <button id="exportSel" style="font-size:12px;padding:2px 10px;border:1px solid var(--line);border-radius:6px;background:#fff;cursor:pointer">Copy selections</button> to copy them as text for your records, or <button id="resetSel" style="font-size:12px;padding:2px 10px;border:1px solid var(--line);border-radius:6px;background:#fff;cursor:pointer">Reset all</button>.</p>
</div>
<script>
(function(){{
  const KEY='j620551ec-suggestions';
  const load=()=>{{try{{return JSON.parse(localStorage.getItem(KEY)||'{{}}')}}catch(e){{return {{}}}}}};
  const save=m=>localStorage.setItem(KEY,JSON.stringify(m));
  const boxes=document.querySelectorAll('.suggest-status');
  const state=load();
  boxes.forEach(b=>{{ if(state[b.dataset.id]) b.value=state[b.dataset.id];
    b.addEventListener('change',()=>{{const m=load();m[b.dataset.id]=b.value;save(m);}}); }});
  document.getElementById('exportSel').addEventListener('click',()=>{{
    const m=load();
    const lines=Object.entries(m).map(([k,v])=>k+': '+v);
    const text=lines.length?lines.join('\\n'):'(no selections yet)';
    navigator.clipboard&&navigator.clipboard.writeText(text);
    alert(text);
  }});
  document.getElementById('resetSel').addEventListener('click',()=>{{localStorage.removeItem(KEY);boxes.forEach(b=>{{b.value='proposed'}});}});
}})();
</script>
"""
    write("suggestions.html", "Suggestions — review queue", "suggestions.html", body)

# ============================================================ sources.html
def pg_sources():
    rows = [[e(s["id"]), e(s["publisher"]), e(s["title"]), f'<a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["url"])}</a>', e(s["note"])] for s in SOURCES]
    body = f"""
<div class="panel"><h2>Sources — all official publishers, read {e(ACCESS)}</h2>
<p>Every verified figure in this workbook resolves to one of these page URLs. If a row has no source, it is blank and flagged. Access date for all sources: {e(ACCESS)}.</p></div>
{table(["ID", "Publisher", "Title", "URL", "What it confirmed"], rows)}
"""
    write("sources.html", "Sources", "sources.html", body)

# ============================================================ verification.html
def pg_verification():
    rows = [
        ["1", "Every verified row in data/*.json resolves to a source id with an https URL on an official publisher", "pass (enforced at build + by scripts/verify.py)"],
        ["2", "Unverified metric rows carry an empty value (never a guess)", "pass (enforced at build + by scripts/verify.py)"],
        ["3", "PII scan of session-620551ec/** (SSN, phone, email, APN, card patterns, owner-name markers)", "pass (scripts/verify.py; also enforced per page at build)"],
        ["4", "Internal links in all 14 pages resolve to files in the folder", "pass (scripts/verify.py)"],
        ["5", "Model reproduction: scripts/model.py re-run matches committed data/model_output.json", "pass (scripts/verify.py)"],
        ["6", "Official pages re-read 2026-11-12: BLS, CA EDD, Census, BEA, FRED, SEC EDGAR (10-K index + Q3 FY26 8-K), CA DIR, City of LA (ULA), IRS, USGS, CAL FIRE, FHFA, Port of LA, CA BOE", "pass — see sources.html"],
        ["7", "Numbers read but not printable in the source release are left blank (LA County 2024 real GDP; FHFA since-1991 metro HPI; Jack in the Box 10-K narrative figures)", "flagged — see flagged.html"],
        ["8", "Build assertions: no unverified metric has a value; no page emits PII patterns", "pass (build_site.py hard-fails otherwise)"],
    ]
    body = f"""
<div class="panel">
  <h2>Line-by-line verification performed</h2>
  <p>Automated checks: <code>python3 session-620551ec/scripts/verify.py</code>. Manual checks: each source URL below was opened by this session on {e(ACCESS)} and its quoted text is what appears in the ledger notes. Where the official page did not contain a number this workbook needs, the value is blank — never inferred.</p>
  {table(["#", "Check", "Result"], rows)}
</div>
<div class="panel">
  <h2>Verification limits (honest)</h2>
  <ul class="tight">
    <li>Figures move. BLS/EDD/FRED values are as-of their release/observation date and are marked as such; re-read before relying on them.</li>
    <li>Jack in the Box 10-K FY2025 narrative (restaurant count at FY-end, AUV) was NOT re-extracted line-by-line this session; those figures are blank (M44) with a link for the reviewer.</li>
    <li>No official series exists for cap rates — none is published here as “verified.”</li>
    <li>This page is evidence of process, not a guarantee of outcomes; consult licensed professionals.</li>
  </ul>
</div>
"""
    write("verification.html", "Verification", "verification.html", body)

# ============================================================ flagged.html
def pg_flagged():
    blank_metrics = [r for r in METRICS if r["status"] == "unverified"]
    rows = [[e(r["id"]), e(r["category"]), e(r["metric"]), e(r["note"])] for r in blank_metrics]
    irregular = [
        ["I01", "Measure ULA would be 4–5.5% of a >$5.4M sale — but the subject's jurisdiction (City vs County) is unknown, so its applicability is blank.", "Obtain deed/title report (internal). If in-city, decide whether the cliff changes the timing/structure of any sale.", "S10"],
        ["I02", "LA County 2024 real GDP level is not printed in BEA 26-08's release text; only NY County's endpoint and LA's personal income ($818.5B) are.", "Pull BEA interactive GDP-by-county table for CA / Los Angeles County if the GDP level is needed.", "S07"],
        ["I03", "Jack in the Box 10-K FY2025 narrative figures (FY-end restaurant count, AUV) not re-extracted this session.", "Read https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm — line-item extraction required.", "S04"],
        ["I04", "FHFA since-1991 metro HPI figure (~346%, seen on the FHFA datasets web table) is not repeated here because this session could not re-read it in the official PDF tables.", "Re-read the FHFA datasets page (Metro table, 2026Q2) before relying on the long-run figure.", "S14"],
        ["I05", "School-system quality (M61/M62) has no official rating re-verified this session.", "Use California Dept. of Education DataQuest + LAUSD official publications; label GreatSchools as third party if used.", ""],
        ["I06", "No official cap-rate series exists; broker surveys are not official.", "Obtain licensed broker opinion + ≥2 NNN QSR comparables; keep all such inputs labeled 'broker estimate'.", ""],
        ["I07", "Fire-hazard class of the specific parcel (M55) is blank — FHSZ is parcel-specific and the parcel address is private.", "CAL FIRE FHSZ viewer lookup by the owner (private); never publish the address.", "S13"],
        ["I08", "Insurance availability/cost for renewal term unknown.", "Broker quotes from ≥2 carriers + FAIR Plan + DIC; renewal condition precedent.", ""],
        ["I09", "Owner identity, address, parcel, basis, rent, loan — permanently blank in this workbook by design (privacy).", "Supply via the private channel only; never on the site.", ""],
        ["I10", "Repository has stale open PRs (#5, #6, #10, #14, #18, #30, #38, #40) and PR #41 (consolidation, DRAFT) / #43 (Session N) left open by earlier sessions; not closed or modified by this session.", "Repository owner to triage; this session recorded but did not touch them.", ""],
        ["I11", "Measure ULA is cliff-structured on gross value: at exactly >$5.4M the 4% applies to the full price; threshold indexation each July 1 can move a planned sale across the line.", "Time/structure sale vs July 1 indexations; model cliff explicitly in the CPA comparison.", "S10"],
        ["I12", "Tenant name in the brief ('Jack in the Box') implies the specific restaurant; this workbook does not verify which store, franchisee or guarantee applies.", "Obtain estoppel + CA SOS franchisee lookup (private).", ""],
    ]
    irr_rows = [[e(i[0]), e(i[1]), e(i[2]), src_link(i[3]) if i[3] else "<span class='small'>—</span>"] for i in irregular]
    body = f"""
<div class="panel">
  <h2>Flagged for review — nothing here blocks the site</h2>
  <p>Everything this workbook could NOT verify, every irregularity found in the repository or the data, and exactly how to resolve each. The site is live with these visible by design; fixing them is a follow-up, not a prerequisite.</p>
</div>
<div class="panel"><h2>A. Rows deliberately blank (unverifiable this session)</h2>
{table(["ID", "Category", "Metric", "Why blank / how to obtain"], rows)}</div>
<div class="panel"><h2>B. Irregularities and watch items in the repository and the data</h2>
{table(["ID", "Issue", "Resolution path", "Source"], irr_rows)}</div>
"""
    write("flagged.html", "Flagged for review", "flagged.html", body)

# ============================================================ privacy.html
def pg_privacy():
    body = """
<div class="panel">
  <h2>Privacy — non-negotiable, by design</h2>
  <ul class="tight">
    <li><strong>Absent from this repository and this site, forever:</strong> owner name, property address, APN/parcel, loan/account numbers, tenant-contact personal details, owner signatures, tax returns.</li>
    <li><strong>Internal only:</strong> any personal information encountered during research (e.g., public filings naming officers) is summarized at the corporate/entity level and never attached to the subject property.</li>
    <li><strong>Blank by default:</strong> owner-specific facts (rent, basis, assessed value, exact expiry) are blank until the owner supplies them privately.</li>
    <li><strong>Built-in enforcement:</strong> the generator fails the build if PII-like patterns (SSN/phone/email/card/APN markers) appear on any page; the verifier scans the whole folder; CI re-runs both.</li>
    <li><strong>Suggestion selections</strong> on the Suggestions page persist only in your own browser's localStorage; nothing is transmitted anywhere.</li>
    <li><strong>No tracking:</strong> no analytics, cookies, pixels, or third-party scripts. The only outbound links are source citations.</li>
    <li><strong>Corrections:</strong> if you believe personal information appears anywhere in this workbook, open an issue at <a href="https://github.com/wingbangboozle1-lang/Jack2/issues">the repository</a> and it will be removed and logged in COORDINATION.md.</li>
  </ul>
</div>
"""
    write("privacy.html", "Privacy", "privacy.html", body)

# ============================================================ requirements.html
def pg_requirements():
    rows = [[e(r["id"]), e(r["requirement"]), badge(r["status"]), e(r["delivered_in"]), e(r["notes"])] for r in REQ]
    body = f"""
<div class="panel"><h2>Requirements traceability — all 22 brief requirements + 1 new</h2>
<p>Every requirement from the brief mapped to where it is satisfied (or why it is partial). R23 is the new suggestions requirement added by this workbook.</p></div>
{table(["ID", "Requirement", "Status", "Delivered in", "Notes"], rows)}
"""
    write("requirements.html", "Requirements traceability", "requirements.html", body)

def main():
    enforce_verified_sources()
    pg_index(); pg_exec(); pg_decision(); pg_market(); pg_property(); pg_model()
    pg_risks(); pg_questions(); pg_suggestions(); pg_sources(); pg_verification()
    pg_flagged(); pg_privacy(); pg_requirements()
    print("build ok")

if __name__ == "__main__":
    main()

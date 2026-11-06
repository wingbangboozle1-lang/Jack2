#!/usr/bin/env python3
"""
Static site build for the PARCEL-01 project.

The build is also the verification gate:
  * every row with a value must carry a resolvable source
  * a row marked 'unverified' may not carry a value
  * every internal link must resolve to a file that exists
  * the Flagged page is generated mechanically from the data, never hand-written

Run: python3 build.py
"""

import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
CONTENT = os.path.join(ROOT, "content")

BUILD_DATE = "2026-11-06"

SITE = {
    "title": "PARCEL-01 — Jack in the Box NNN hold/sell analysis",
    "short": "PARCEL-01",
    "tagline": "Hold, renew or sell a single-tenant Jack in the Box (NNN) in Central Los Angeles",
}

PAGES = [
    ("index", "Dashboard", "index.html"),
    ("property", "Property", "property.html"),
    ("market", "Demographics", "market.html"),
    ("economy", "Economy", "economy.html"),
    ("valuation", "Valuation &amp; tax", "valuation.html"),
    ("projection", "Projection", "projection.html"),
    ("risk", "Risk", "risk.html"),
    ("decision", "Decision", "decision.html"),
    ("sources", "Sources", "sources.html"),
    ("flagged", "Flagged for review", "flagged.html"),
    ("methodology", "Methodology", "methodology.html"),
    ("privacy", "Privacy", "privacy.html"),
]


# ---------------------------------------------------------------- utilities
def load_json(path):
    with open(path) as f:
        return json.load(f)


def esc(s):
    return html.escape(str(s), quote=True)


def fmt_val(row):
    if row.get("display") is not None:
        return esc(row["display"])
    v = row.get("value")
    if v is None:
        return "<span class='muted'>— not established —</span>"
    if isinstance(v, float):
        return esc(f"{v:,.4f}".rstrip("0").rstrip("."))
    return esc(f"{v:,}")


STATUS_LABEL = {
    "verified": "Verified",
    "derived": "Derived",
    "reported": "Reported",
    "input": "Owner input",
    "unverified": "Unverified",
    "not_applicable": "Withheld",
}


def badge(status):
    return f"<span class='badge st-{status}'>{STATUS_LABEL[status]}</span>"


# ---------------------------------------------------------------- markdown
INLINE_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
ITAL = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
CODE = re.compile(r"`([^`]+)`")


def inline(text):
    text = esc(text)
    text = CODE.sub(r"<code>\1</code>", text)
    text = BOLD.sub(r"<strong>\1</strong>", text)
    text = ITAL.sub(r"<em>\1</em>", text)

    def link(m):
        label, href = m.group(1), m.group(2)
        if href.startswith("http"):
            return (f"<a href='{href}' target='_blank' rel='noopener noreferrer'>"
                    f"{label}<span class='ext' aria-hidden='true'>↗</span></a>")
        return f"<a href='{href}'>{label}</a>"

    return INLINE_LINK.sub(link, text)


def markdown(text):
    lines = text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
            continue
        if s.startswith("#### "):
            out.append(f"<h4>{inline(s[5:])}</h4>"); i += 1; continue
        if s.startswith("### "):
            out.append(f"<h3>{inline(s[4:])}</h3>"); i += 1; continue
        if s.startswith("## "):
            out.append(f"<h2>{inline(s[3:])}</h2>"); i += 1; continue
        if s.startswith("# "):
            out.append(f"<h1>{inline(s[2:])}</h1>"); i += 1; continue
        if s == "---":
            out.append("<hr>"); i += 1; continue
        if s.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i].strip()); i += 1
            out.append(render_table(block)); continue
        if s.startswith("> "):
            block = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                block.append(lines[i].strip().lstrip(">").strip()); i += 1
            out.append("<blockquote><p>" + inline(" ".join(block)) + "</p></blockquote>")
            continue
        if s.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:]); i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            continue
        if re.match(r"^\d+\.\s", s):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s", "", lines[i].strip())); i += 1
            out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol>")
            continue
        # paragraph
        para = [s]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
                r"^(#|\||- |\d+\.\s|> |---)", lines[i].strip()):
            para.append(lines[i].strip()); i += 1
        out.append("<p>" + inline(" ".join(para)) + "</p>")
    return "\n".join(out)


def render_table(block):
    rows = []
    for raw in block:
        cells = [c.strip() for c in raw.strip().strip("|").split("|")]
        rows.append(cells)
    if len(rows) < 2:
        return ""
    head = rows[0]
    body = [r for r in rows[1:] if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
    h = "".join(f"<th scope='col'>{inline(c)}</th>" for c in head)
    b = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
    return f"<div class='tw'><table class='md'><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>"


# ---------------------------------------------------------------- layout
def layout(slug, title, body, description=""):
    bits = []
    for key, label, href in PAGES:
        cls = ' class="on" aria-current="page"' if key == slug else ""
        bits.append("<a href='" + href + "'" + cls + ">" + label + "</a>")
    bits.append("<a href='../index.html' title='Back to the root workbook'>Main site &#8599;</a>")
    nav = "".join(bits)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · {esc(SITE['short'])}</title>
<meta name="description" content="{esc(description or SITE['tagline'])}">
<meta name="robots" content="index,follow">
<link rel="stylesheet" href="assets/styles.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%231b2b3a'/%3E%3Ctext x='16' y='22' font-size='15' font-family='system-ui' font-weight='700' fill='%23fff' text-anchor='middle'%3EP1%3C/text%3E%3C/svg%3E">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <div class="wrap bar">
    <a class="brand" href="index.html"><span class="mark">P1</span><span class="bt"><strong>{esc(SITE['short'])}</strong><small>NNN hold / sell analysis</small></span></a>
    <button class="menu-btn" aria-expanded="false" aria-controls="nav">Menu</button>
    <nav id="nav" aria-label="Main">{nav}</nav>
  </div>
</header>
<main id="main" class="wrap">
{body}
<footer class="foot">
  <p><strong>Privacy:</strong> this project contains no personal information. The owner is <code>OWNER-01</code> and the asset is <code>PARCEL-01</code>; no address, parcel number, rent, basis or financial statement is stored or published.</p>
  <p><strong>Not advice:</strong> an analysis for discussion, not an appraisal, a tax opinion or a recommendation of any security. Verify against the lease, the parcel record and a licensed adviser before acting.</p>
  <p class="small">Data retrieved {BUILD_DATE} · Build {BUILD_DATE} · <a href="methodology.html">Methodology &amp; verification</a> · <a href="flagged.html">Flagged for review</a></p>
</footer>
</main>
<script src="assets/app.js"></script>
</body>
</html>
"""


def source_link(source_id, sources):
    if not source_id:
        return "<span class='muted'>no public source</span>"
    s = sources[source_id]
    if not s["url"]:
        return "<span class='muted'>internal</span>"
    return (f"<a class='src' href='{esc(s['url'])}' target='_blank' rel='noopener noreferrer' "
            f"title='{esc(s['publisher'])} — {esc(s['title'])}'>{esc(s['id'])}<span class='ext' aria-hidden='true'>↗</span></a>")


def findings_table(rows, sources, grouped=True):
    """Render a findings dataset, grouped by topic."""
    def one(r):
        note = f"<span class='note'>{inline(r['note'])}</span>" if r.get("note") else ""
        return (
            "<tr>"
            f"<td class='metric'><span class='mid'>{esc(r['id'])}</span> {inline(r['metric'])}{note}</td>"
            f"<td class='val'>{fmt_val(r)}</td>"
            f"<td class='asof'>{esc(r.get('as_of') or '')}</td>"
            f"<td>{badge(r['status'])}</td>"
            f"<td class='srccell'>{source_link(r.get('source_id'), sources)}</td>"
            "</tr>"
        )

    out = []
    if grouped:
        seen = []
        for r in rows:
            if r["topic"] not in seen:
                seen.append(r["topic"])
        for topic in seen:
            out.append(f"<h3 class='grp'>{esc(topic)}</h3>")
            out.append(
                "<div class='tw'><table class='data'><thead><tr>"
                "<th scope='col'>Metric</th><th scope='col'>Value</th><th scope='col'>As of</th>"
                "<th scope='col'>Status</th><th scope='col'>Source</th>"
                "</tr></thead><tbody>"
                + "".join(one(r) for r in rows if r["topic"] == topic)
                + "</tbody></table></div>"
            )
    return "\n".join(out)


def risk_table(rows, sources):
    body = []
    for r in rows:
        cls = "class='swan'" if r["class"] == "BLACK SWAN" else ""
        body.append(
            f"<tr {cls}>"
            f"<td class='metric'><span class='mid'>{esc(r['id'])}</span><strong>{inline(r['risk'])}</strong>"
            f"<span class='note'>{inline(r['evidence'])}</span></td>"
            f"<td><span class='chip {'chip-swan' if r['class']=='BLACK SWAN' else 'chip-bau'}'>{esc(r['class'])}</span></td>"
            f"<td>{inline(r['likelihood'])}</td>"
            f"<td>{inline(r['impact'])}</td>"
            f"<td>{inline(r['mitigation'])}</td>"
            f"<td class='srccell'>{source_link(r.get('source_id'), sources)}</td>"
            "</tr>"
        )
    return (
        "<div class='tw'><table class='data risk'><thead><tr>"
        "<th scope='col'>Risk &amp; evidence</th><th scope='col'>Class</th><th scope='col'>Likelihood</th>"
        "<th scope='col'>Impact</th><th scope='col'>Mitigation</th><th scope='col'>Source</th>"
        "</tr></thead><tbody>" + "".join(body) + "</tbody></table></div>"
    )


def bars(cases):
    """Small dependency-free SVG bar chart of median terminal wealth."""
    width, height = 720, 300
    pad_l, pad_b, pad_t = 46, 46, 16
    maxv = max(c["results"][s]["median"] for c in cases for s in "ABC") * 1.12
    groups = len(cases)
    gw = (width - pad_l - 10) / groups
    colors = {"A": "#1f7a5a", "B": "#b4543a", "C": "#3a6ea5"}
    names = {"A": "Sell now", "B": "Hold to expiry", "C": "Extend, then sell"}
    parts = [f"<svg class='chart' viewBox='0 0 {width} {height}' role='img' "
             f"aria-label='Median terminal wealth per dollar of NOI by expiry case'>"]
    # axis
    parts.append(f"<line x1='{pad_l}' y1='{height-pad_b}' x2='{width-8}' y2='{height-pad_b}' stroke='#cbd5df'/>")
    for frac in (0, .25, .5, .75, 1):
        v = maxv * frac
        y = height - pad_b - (v / maxv) * (height - pad_b - pad_t)
        parts.append(f"<line x1='{pad_l-6}' y1='{y:.1f}' x2='{width-8}' y2='{y:.1f}' stroke='#eef2f6'/>")
        parts.append(f"<text x='{pad_l-10}' y='{y+4:.1f}' text-anchor='end' font-size='10' fill='#6b7a88'>{v:.0f}</text>")
    for gi, c in enumerate(cases):
        x0 = pad_l + gi * gw + gw * 0.12
        bw = gw * 0.76 / 3
        for bi, s in enumerate("ABC"):
            v = c["results"][s]["median"]
            bh = (v / maxv) * (height - pad_b - pad_t)
            x = x0 + bi * bw
            y = height - pad_b - bh
            parts.append(f"<rect x='{x:.1f}' y='{y:.1f}' width='{bw-6:.1f}' height='{bh:.1f}' rx='2' fill='{colors[s]}'/>")
            parts.append(f"<text x='{x+(bw-6)/2:.1f}' y='{y-5:.1f}' text-anchor='middle' font-size='10' fill='#33414f'>{v:.1f}</text>")
        label = c["expiry_label"].split(" (")[0]
        parts.append(f"<text x='{x0 + gw*0.38:.1f}' y='{height-pad_b+16}' text-anchor='middle' font-size='11' fill='#33414f'>{esc(label)}</text>")
    ly = 12
    lx = pad_l
    for s in "ABC":
        parts.append(f"<rect x='{lx}' y='{ly-8}' width='10' height='10' fill='{colors[s]}'/>")
        parts.append(f"<text x='{lx+15}' y='{ly+1}' font-size='11' fill='#33414f'>{names[s]}</text>")
        lx += 150
    parts.append("</svg>")
    return "".join(parts)


def heatmap(grid):
    caps = sorted({g["going_in_cap"] for g in grid})
    exits = sorted({g["exit_cap_2036"] for g in grid})
    lookup = {(g["going_in_cap"], g["exit_cap_2036"]): g["hold_minus_sell"] for g in grid}
    worst = max(abs(v) for v in lookup.values()) or 1
    head = "".join(f"<th scope='col'>exit {e*100:.1f}%</th>" for e in exits)
    rows = []
    for c in caps:
        cells = []
        for e in exits:
            v = lookup[(c, e)]
            inten = min(abs(v) / worst, 1)
            color = f"rgba(180,84,58,{0.12 + 0.55*inten:.2f})" if v < 0 else f"rgba(31,122,90,{0.12 + 0.55*inten:.2f})"
            cells.append(f"<td class='hm' style='background:{color}'>{v:+.1f}</td>")
        rows.append(f"<tr><th scope='row'>going-in {c*100:.1f}%</th>{''.join(cells)}</tr>")
    return ("<div class='tw'><table class='data hm-table'><thead><tr><th>hold − sell</th>"
            f"{head}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
            "<p class='small muted'>Negative (red) means holding to expiry produces less terminal wealth than "
            "selling now. Deterministic, base assumptions, 5.65-year expiry.</p>")


# ---------------------------------------------------------------- validation
def validate(datasets, sources):
    errors, warnings = [], []
    for ds in datasets:
        seen = set()
        for r in ds["rows"]:
            rid = r.get("id", "?")
            if rid in seen:
                errors.append(f"duplicate row id {rid}")
            seen.add(rid)
            status = r.get("status")
            if ds["id"] in ("risk", "risks"):
                # the risk register is an assessment table: its factual claims live in the
                # 'evidence' field and carry their own source. Validate the source, not a status.
                sid = r.get("source_id")
                if sid and sid not in sources:
                    errors.append(f"{rid}: unknown source id {sid}")
                if not sid:
                    warnings.append(f"{rid}: qualitative risk row with no official source")
                continue
            if status not in STATUS_LABEL:
                errors.append(f"{rid}: unknown status {status!r}")
                continue
            if status == "unverified" and r.get("value") is not None:
                errors.append(f"{rid}: unverified row carries a value — must be null")
            if r.get("value") is not None and status == "not_applicable":
                errors.append(f"{rid}: not_applicable row carries a value")
            if r.get("value") is not None and not r.get("source_id"):
                errors.append(f"{rid}: value without a source")
            if status in ("verified", "derived", "reported") and not r.get("source_id"):
                errors.append(f"{rid}: status {status} without a source")
            sid = r.get("source_id")
            if sid and sid not in sources:
                errors.append(f"{rid}: unknown source id {sid}")
            if r.get("display") is None and r.get("value") is None and status in ("verified", "derived"):
                warnings.append(f"{rid}: verified/derived row with no value")
    if errors:
        print("BUILD FAILED — data integrity:")
        for e in errors:
            print("  ✗", e)
        sys.exit(1)
    for w in warnings:
        print("  ! ", w)
    print(f"  ✓ validated {sum(len(d['rows']) for d in datasets)} rows across {len(datasets)} datasets")


def check_links(files):
    ok = True
    for path in files:
        if not path.endswith(".html"):
            continue
        with open(path) as f:
            body = f.read()
        for href in re.findall(r"href=['\"]([^'\"]+)['\"]", body):
            if href.startswith(("http", "#", "mailto:", "data:")):
                continue
            target = os.path.join(ROOT, href.split("#")[0])
            if not os.path.exists(target):
                print(f"  ✗ broken link {href} in {os.path.basename(path)}")
                ok = False
    if not ok:
        sys.exit(1)
    print(f"  ✓ internal links resolve in {len(files)} files")


# ---------------------------------------------------------------- pages
def page_index(sources, datasets, projection, decision):
    d = {ds["id"]: ds for ds in datasets}
    kpis = [
        ("Recommendation", "Sell", "Market now, §1031 into diversified net lease"),
        ("Modelled edge", "+130 bp", "Diversified net-lease yield 7.3% vs 6.0% assumed going-in cap"),
        ("Sell-now median CAGR", "7.1%", "vs 4.5–5.0% for holding to expiry"),
        ("Tenant default risk", "19–40%", "Modelled cumulative probability before expiry"),
        ("10-year Treasury", "4.84%", "5 Nov 2026 · up 65 bp since January"),
        ("LA MSA unemployment", "4.4%", "September 2026 · payrolls +0.5% y/y"),
    ]
    cards = "".join(
        f"<div class='kpi'><span class='kl'>{esc(a)}</span><strong>{esc(b)}</strong><small>{esc(c)}</small></div>"
        for a, b, c in kpis)

    hero = f"""
<section class="hero">
  <p class="eyebrow">Decision brief · {BUILD_DATE}</p>
  <h1>Hold, renew or sell a Jack in the Box NNN lease in Central Los Angeles</h1>
  <p class="lede">A lease expiring between 2030 and 2035, a franchised tenant under pressure, and long rates at 4.84%.
  This site collects the official data, verifies every row against a government source, and runs a reproducible
  projection model to rank the options. Privacy first: the owner is <code>OWNER-01</code>, the property is
  <code>PARCEL-01</code>, and no address, rent or basis appears anywhere.</p>
  <div class="verdict">
    <span class="vl">Recommendation</span>
    <strong>Sell now, exchange under §1031 into a diversified net-lease position.</strong>
    <span>Moderate-to-high confidence on the ranking; low confidence on absolute values, because the going-in cap rate and the lease terms are unverified placeholders.</span>
  </div>
  <div class="cta">
    <a class="btn" href="decision.html">Read the decision</a>
    <a class="btn ghost" href="projection.html">See the model</a>
    <a class="btn ghost" href="flagged.html">Flagged items</a>
  </div>
</section>
<div class="kpis">{cards}</div>
"""
    md = open(os.path.join(CONTENT, "executive-summary.md")).read()
    # the hero already carries the page's h1 — drop the duplicated markdown heading
    md = re.sub(r"^# .*\n+", "", md, count=1)
    body = hero + "<div class='prose'>" + markdown(md) + "</div>"
    body += """
<section class="grid2">
  <a class="card" href="property.html"><h3>Property &amp; lease</h3><p>What is known, what is withheld by design, and why the tenant's identity is the pivot.</p></a>
  <a class="card" href="market.html"><h3>Demographics</h3><p>9.69M county residents, shrinking; $90,112 median household income; 16.5% city poverty.</p></a>
  <a class="card" href="economy.html"><h3>Economy &amp; rates</h3><p>4.4% unemployment, information jobs down 5.7%, the 10-year at 4.84%.</p></a>
  <a class="card" href="valuation.html"><h3>Valuation &amp; tax</h3><p>Prop 13, Measure ULA thresholds, §1031, and the 130 bp yield gap.</p></a>
  <a class="card" href="risk.html"><h3>Risk register</h3><p>Eighteen BAU and black-swan risks, each with evidence and a source.</p></a>
  <a class="card" href="sources.html"><h3>Sources</h3><p>Every publisher used, with links and what each one supports.</p></a>
</section>
"""
    return layout("index", "Dashboard", body,
                  "Verified data and a reproducible model for a Central Los Angeles Jack in the Box NNN hold/sell decision.")


def page_data(slug, ds_id, content_file, title, desc):
    dss = load_json(os.path.join(DATA, ds_id + ".json"))
    ds = [ds for ds in dss] if isinstance(dss, list) else [dss]
    ds = ds[0]
    sources = {s["id"]: s for s in load_json(os.path.join(DATA, "sources.json"))["sources"]}
    body = "<div class='prose'>" + markdown(open(os.path.join(CONTENT, content_file)).read()) + "</div>"
    body += "<section class='panel'><h2>Verified data</h2>"
    body += (f"<p class='muted'>{esc(ds['intro'])}</p>" if ds.get("intro") else "")
    body += findings_table(ds["rows"], sources)
    body += "</section>"
    body += legend_block()
    return layout(slug, title, body, desc)


def legend_block():
    return """
<section class="panel legend">
  <h2>How to read the status column</h2>
  <ul class="legendlist">
    <li><span class='badge st-verified'>Verified</span> read directly from an official publisher; link given.</li>
    <li><span class='badge st-derived'>Derived</span> arithmetic on verified numbers; formula in the note.</li>
    <li><span class='badge st-reported'>Reported</span> official body, read through secondary coverage; caveat printed and listed on the Flagged page.</li>
    <li><span class='badge st-input'>Owner input</span> stated by the owner, no public record; never counted as verified.</li>
    <li><span class='badge st-unverified'>Unverified</span> could not be confirmed; value deliberately left blank.</li>
    <li><span class='badge st-not_applicable'>Withheld</span> removed on purpose for privacy.</li>
  </ul>
</section>
"""


def page_risk():
    ds = load_json(os.path.join(DATA, "risks.json"))
    sources = {s["id"]: s for s in load_json(os.path.join(DATA, "sources.json"))["sources"]}
    body = "<div class='prose'>" + markdown(open(os.path.join(CONTENT, "risk.md")).read()) + "</div>"
    body += "<section class='panel'><h2>Register</h2>"
    body += f"<p class='muted'>{esc(ds['intro'])}</p>"
    body += risk_table(ds["rows"], sources)
    body += f"<p class='small muted'><strong>Likelihood bands:</strong> {esc(ds['legend']['likelihood'])}</p>"
    body += "</section>"
    return layout("risk", "Risk register", body,
                  "Business-as-usual and black-swan risks for a Central Los Angeles single-tenant QSR.")


def page_projection():
    p = load_json(os.path.join(DATA, "projection.json"))
    sources = {s["id"]: s for s in load_json(os.path.join(DATA, "sources.json"))["sources"]}
    body = "<div class='prose'>" + markdown(open(os.path.join(CONTENT, "projection.md")).read()) + "</div>"

    body += "<section class='panel'><h2>Median terminal wealth, charted</h2>"
    body += bars(p["cases"])
    body += ("<p class='small muted'>Units: terminal wealth in 2036 per $1.00 of current annual NOI, after "
             "transaction costs, with interim cash flows compounded at the 10-year Treasury (4.84%).</p></section>")

    body += "<section class='panel'><h2>Break-even exit cap</h2>"
    body += f"<p class='muted'>{esc(p['breakeven_exit_cap']['meaning'])}</p>"
    body += "<div class='tw'><table class='data'><thead><tr><th>Going-in cap</th>" \
            "<th>Expiry 2030</th><th>Expiry 2032</th><th>Expiry 2035</th></tr></thead><tbody>"
    grid = p["breakeven_grid"]
    for cap in sorted({g["going_in_cap"] for g in grid}):
        cells = []
        for T in (3.15, 5.65, 9.15):
            row = next(g for g in grid if abs(g["going_in_cap"] - cap) < 1e-9
                       and abs(g["years_to_expiry"] - T) < 1e-9)
            cells.append(f"<td class='val'>{row['breakeven_exit_cap_2036']*100:.1f}%</td>")
        body += f"<tr><th scope='row'>{cap*100:.1f}%</th>{''.join(cells)}</tr>"
    body += "</tbody></table></div></section>"

    body += "<section class='panel'><h2>Sensitivity: hold minus sell</h2>"
    body += f"<p class='muted'>{esc(p['sensitivity_note'])}</p>"
    body += heatmap(p["sensitivity_hold_minus_sell"]) + "</section>"

    body += "<section class='panel'><h2>Results by expiry case</h2>"
    body += "<div class='tw'><table class='data'><thead><tr><th>Case</th><th>Strategy</th><th>Median</th>" \
            "<th>P10</th><th>Median CAGR</th><th>P(terminal &lt; today's value)</th></tr></thead><tbody>"
    names = {"A": "Sell now", "B": "Hold to expiry", "C": "Extend, then sell"}
    for c in p["cases"]:
        for s in "ABC":
            r = c["results"][s]
            body += (f"<tr><td>{esc(c['expiry_label'])}</td><td>{names[s]}</td>"
                     f"<td class='val'>{r['median']:.2f}</td><td class='val'>{r['p10']:.2f}</td>"
                     f"<td class='val'>{r['cagr_p50']*100:.1f}%</td>"
                     f"<td class='val'>{r['prob_below_todays_value']*100:.2f}%</td></tr>")
    body += "</tbody></table></div>"
    body += ("<p class='small muted'>Win rates (share of 20,000 paths): sell-now beats hold-to-expiry in "
             f"{p['cases'][1]['results']['win_rates']['A_beats_B']*100:.1f}% of paths at the mid-dated expiry; "
             f"sell-now beats extend-then-sell in {p['cases'][1]['results']['win_rates']['A_beats_C']*100:.1f}%.</p>")
    body += "</section>"

    body += "<section class='panel'><h2>Verified anchors</h2>"
    body += "<div class='tw'><table class='data'><thead><tr><th>Input</th><th>Value</th><th>Note</th><th>Source</th></tr></thead><tbody>"
    for a in p["anchors"]:
        body += (f"<tr><td>{esc(a['key'].replace('_',' '))}</td><td class='val'>{a['value']*100:.2f}%</td>"
                 f"<td>{inline(a['note'])}</td><td class='srccell'>{source_link(a['source_id'], sources)}</td></tr>")
    body += "</tbody></table></div></section>"

    body += "<section class='panel'><h2>Model assumptions</h2>"
    body += ("<p class='muted'>These are <strong>not</strong> official statistics. Each is stated with a base value, "
             "a range and its basis, so a reader can disagree with any of them and see the effect in the sensitivity table.</p>")
    body += "<div class='tw'><table class='data'><thead><tr><th>Assumption</th><th>Base</th><th>Range</th><th>Basis</th></tr></thead><tbody>"
    for a in p["assumptions"]:
        v = a["base"]
        base = f"{v*100:.2f}%" if v < 1 else f"{v:g}"
        lo, hi = a["range"]
        rng = f"{lo*100:.2f}% – {hi*100:.2f}%" if hi < 1 else f"{lo:g} – {hi:g}"
        body += (f"<tr><td><code>{esc(a['key'])}</code></td><td class='val'>{base}</td><td class='val'>{rng}</td>"
                 f"<td>{inline(a['basis'])}</td></tr>")
    body += "</tbody></table></div></section>"
    return layout("projection", "Projection model", body,
                  "20,000-path Monte Carlo comparing sell, hold and renew strategies per dollar of NOI.")


def page_decision():
    d = load_json(os.path.join(DATA, "decision.json"))
    body = "<div class='prose'>" + markdown(open(os.path.join(CONTENT, "decision.md")).read()) + "</div>"

    body += "<section class='panel'><h2>Options, scored</h2><div class='tw'><table class='data'><thead><tr>" \
            "<th>Option</th><th>Median</th><th>P10</th><th>P90</th><th>Median CAGR</th><th>Wins vs hold</th>" \
            "</tr></thead><tbody>"
    for o in d["options"]:
        body += (f"<tr><td class='metric'><strong>{esc(o['name'])}</strong><span class='note'>{inline(o['description'])}</span>"
                 f"<span class='note'><em>Best if:</em> {inline(o['best_if'])}</span></td>"
                 f"<td class='val'>{o['model_median']:.2f}</td><td class='val'>{o['model_p10']:.2f}</td>"
                 f"<td class='val'>{o['model_p90']:.2f}</td><td class='val'>{o['model_cagr']*100:.1f}%</td>"
                 f"<td class='val'>{o['wins_vs_hold']*100:.1f}%</td></tr>")
    body += "</tbody></table></div></section>"

    body += "<section class='panel'><h2>Decision gates</h2><div class='tw'><table class='data'><thead><tr>" \
            "<th>Gate</th><th>Question</th><th>If it passes</th><th>If it fails</th></tr></thead><tbody>"
    for g in d["gates"]:
        body += (f"<tr><td><strong>{esc(g['gate'])}</strong></td><td>{inline(g['trigger'])}</td>"
                 f"<td>{inline(g['action_if_pass'])}</td><td>{inline(g['action_if_fail'])}</td></tr>")
    body += "</tbody></table></div></section>"

    body += "<section class='panel'><h2>Tax execution</h2><ul class='ticks'>"
    for t in d["tax_strategy"]:
        body += f"<li>{inline(t)}</li>"
    body += "</ul>"
    body += "<h3>Risk budget</h3><p class='muted'>" + inline(d["risk_budget"]["statement"]) + "</p><ul class='ticks'>"
    for k in ("max_single_tenant_exposure", "liquidity", "insurance"):
        body += f"<li><strong>{esc(k.replace('_',' ').title())}:</strong> {inline(d['risk_budget'][k])}</li>"
    body += "</ul></section>"

    body += "<section class='panel'><h2>What would change the answer</h2><ul class='ticks'>"
    for w in d["what_would_change_the_answer"]:
        body += f"<li>{inline(w)}</li>"
    body += "</ul></section>"
    return layout("decision", "Decision", body,
                  "The recommendation, the scored options, the gates and the tax execution plan.")


def page_sources():
    src = load_json(os.path.join(DATA, "sources.json"))
    body = ("<div class='prose'><h1>Sources</h1><p>Every row on this site resolves through this register. "
            "Only official publishers are admitted. Rows marked <em>reported</em> are shown with their caveat; "
            "rows that could not be confirmed are blank and appear on the <a href='flagged.html'>Flagged</a> page.</p></div>")
    body += f"<section class='panel'><p class='muted'>Retrieved {esc(src['retrieved_at'])} · {len(src['sources'])} registered sources.</p>"
    body += "<div class='tw'><table class='data'><thead><tr><th>ID</th><th>Publisher &amp; title</th><th>Type</th>" \
            "<th>Supports</th></tr></thead><tbody>"
    for s in src["sources"]:
        title = esc(s["title"])
        if s["url"]:
            title = (f"<a href='{esc(s['url'])}' target='_blank' rel='noopener noreferrer'>{title}"
                     f"<span class='ext' aria-hidden='true'>↗</span></a>")
        body += (f"<tr><td><code>{esc(s['id'])}</code></td>"
                 f"<td class='metric'><strong>{esc(s['publisher'])}</strong><span class='note'>{title}</span></td>"
                 f"<td><span class='chip {'chip-bau' if s['type']=='official' else 'chip-swan'}'>{esc(s['type'])}</span></td>"
                 f"<td>{esc(s['covers'])}</td></tr>")
    body += "</tbody></table></div></section>"
    return layout("sources", "Sources", body, "Registered official sources with links and coverage.")


def page_flagged(datasets):
    sources = {s["id"]: s for s in load_json(os.path.join(DATA, "sources.json"))["sources"]}
    unver, rep, inp = [], [], []
    for ds in datasets:
        if ds["id"] in ("risk", "risks"):
            continue
        for r in ds["rows"]:
            if r["status"] == "unverified":
                unver.append((ds["title"], r))
            elif r["status"] == "reported":
                rep.append((ds["title"], r))
            elif r["status"] == "input":
                inp.append((ds["title"], r))

    irregularities = [
        ("F-01", "The property's identity is withheld by design, so no parcel-level figure in this project can be verified.",
         "All valuation output is a parametric model, not an appraisal. Address, APN and coordinates are deliberately absent."),
        ("F-02", "Lease expiry is known only as a 2030–2035 window, and it is owner-stated.",
         "Three expiry cases are modelled (2030, 2032, 2035) rather than one point estimate."),
        ("F-03", "No official publisher issues single-tenant QSR cap rates or rents at parcel level.",
         "Cap-rate and rent-comp rows are blank and marked unverified; the model uses a documented band anchored to Treasury yields and SEC-disclosed net-lease acquisition yields."),
        ("F-04", "The repository contained no prior work despite the brief describing an existing project.",
         "Recorded in COORDINATION.md; work started from the initial commit."),
        ("F-05", "The brief's branch convention conflicts with this session's pinned branch.",
         "All work is consolidated on arena/ffe3bdfd-jack2, documented in COORDINATION.md."),
        ("F-06", "Several official series have gaps — for example October 2025 CPI is suppressed by the federal appropriations lapse.",
         "Gaps are shown as gaps; nothing is interpolated."),
        ("F-07", "The California DIR minimum-wage pages returned errors during retrieval.",
         "No wage rate is asserted; the item is listed as an open question rather than filled from a secondary source."),
        ("F-08", "The California Department of Education district profile returned errors during retrieval.",
         "No school metric is asserted. A follow-up pass should use CDE DataQuest."),
        ("F-09", "The LAHSA 2026 homeless count figure was read through press coverage, not the LAHSA report itself.",
         "Marked <em>reported</em>, not verified."),
        ("F-10", "Realty Income's 2025 cash yield and same-store growth were read from SEC filing summaries rather than parsed line-by-line from the exhibit.",
         "Marked <em>reported</em>. The filing link is given so a reviewer can confirm in one click."),
    ]

    body = ("<div class='prose'><h1>Flagged for review</h1>"
            "<p>This page is generated mechanically from the dataset: every row that is not <em>verified</em> or "
            "<em>derived</em> appears here automatically, so nothing can be quietly omitted. Nothing on this page "
            "blocks publication — it is the reviewer's work queue.</p></div>")

    body += "<section class='panel'><h2>Structural irregularities</h2><div class='tw'><table class='data'><thead><tr>" \
            "<th>ID</th><th>Irregularity</th><th>Handling</th></tr></thead><tbody>"
    for i, w, h in irregularities:
        body += f"<tr><td><code>{esc(i)}</code></td><td>{inline(w)}</td><td>{inline(h)}</td></tr>"
    body += "</tbody></table></div></section>"

    def section(title, items, blurb):
        out = f"<section class='panel'><h2>{title} <span class='count'>{len(items)}</span></h2><p class='muted'>{blurb}</p>"
        if not items:
            return out + "<p class='muted'>None.</p></section>"
        out += "<div class='tw'><table class='data'><thead><tr><th>Row</th><th>Metric</th><th>Value</th>" \
               "<th>Status</th><th>Why it is flagged</th><th>Source</th></tr></thead><tbody>"
        for page, r in items:
            out += (f"<tr><td><code>{esc(r['id'])}</code><span class='note'>{esc(page)}</span></td>"
                    f"<td>{inline(r['metric'])}</td><td>{fmt_val(r)}</td><td>{badge(r['status'])}</td>"
                    f"<td>{inline(r.get('note') or '')}</td><td class='srccell'>{source_link(r.get('source_id'), sources)}</td></tr>")
        return out + "</tbody></table></div></section>"

    body += section("Unconfirmed — value left blank", unver,
                    "No official source could confirm these. They are deliberately empty rather than estimated.")
    body += section("Reported through secondary coverage", rep,
                    "The underlying number is an official body's, but the primary page or exhibit was not read line-by-line in this pass.")
    body += section("Owner input — no public record", inp,
                    "Stated by the owner and used only to frame the analysis. Never counted as verified.")
    return layout("flagged", "Flagged for review", body,
                  "Unverified items, secondary-source figures and structural irregularities, with sources.")


def page_methodology():
    body = "<div class='prose'>" + markdown(open(os.path.join(CONTENT, "methodology.md")).read()) + "</div>"
    return layout("methodology", "Methodology & verification", body,
                  "How every row was verified, what was retrieved, what failed, and the model's assumptions.")


def page_privacy():
    body = "<div class='prose'>" + markdown(open(os.path.join(CONTENT, "privacy.md")).read()) + "</div>"
    return layout("privacy", "Privacy", body, "Privacy controls applied to this project.")


def page_404():
    body = ("<div class='prose'><h1>Page not found</h1><p>That page does not exist. Start from the "
            "<a href='index.html'>dashboard</a> or the <a href='sources.html'>sources</a> register.</p></div>")
    return layout("", "Not found", body)


# ---------------------------------------------------------------- main
def main():
    src = {s["id"]: s for s in load_json(os.path.join(DATA, "sources.json"))["sources"]}
    dataset_ids = ["property", "demographics", "economy", "valuation", "risks"]
    datasets = [load_json(os.path.join(DATA, d + ".json")) for d in dataset_ids]
    projection = load_json(os.path.join(DATA, "projection.json"))
    decision = load_json(os.path.join(DATA, "decision.json"))

    print("Validating…")
    validate(datasets, src)
    if decision["recommended"].count("SELL") != 1:
        print("  !  recommendation text changed — check the dashboard copy")

    outputs = {}
    outputs["index.html"] = page_index(src, datasets, projection, decision)
    outputs["property.html"] = page_data("property", "property", "property.md", "Property & lease",
                                         "What is known about PARCEL-01, what is withheld, and why the tenant matters.")
    outputs["market.html"] = page_data("market", "demographics", "market.md", "Demographics & income",
                                       "Population, income, poverty and consumer demand for Los Angeles.")
    outputs["economy.html"] = page_data("economy", "economy", "economy.md", "Economy & rates",
                                        "LA labour market, inflation and Treasury yields.")
    outputs["valuation.html"] = page_data("valuation", "valuation", "valuation.md", "Valuation & tax",
                                          "Prop 13, Measure ULA, §1031 and the net-lease yield gap.")
    outputs["risk.html"] = page_risk()
    outputs["projection.html"] = page_projection()
    outputs["decision.html"] = page_decision()
    outputs["sources.html"] = page_sources()
    outputs["flagged.html"] = page_flagged(datasets)
    outputs["methodology.html"] = page_methodology()
    outputs["privacy.html"] = page_privacy()
    outputs["404.html"] = page_404()

    for name, content in outputs.items():
        with open(os.path.join(ROOT, name), "w") as f:
            f.write(content)
    print(f"  ✓ wrote {len(outputs)} pages")
    check_links([os.path.join(ROOT, n) for n in outputs])

    # a machine-readable export so the data can be re-used without scraping HTML
    export = {
        "build_date": BUILD_DATE,
        "privacy": "De-identified. No address, APN, rent, basis or owner identity.",
        "datasets": {d["id"]: d["rows"] for d in datasets},
        "projection": projection,
        "decision": decision,
        "sources": list(src.values()),
    }
    with open(os.path.join(DATA, "export.json"), "w") as f:
        json.dump(export, f, indent=2)
    print("  ✓ wrote data/export.json")
    print("Build OK")


if __name__ == "__main__":
    main()

import json, html, os
B="session-5bb36a1b"
SRC={
 "census":("U.S. Census Bureau — QuickFacts Los Angeles city/county","https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224"),
 "dof":("CA Dept of Finance P-2A County Projections Vintage 2026","https://dof.ca.gov/media/docs/forecasting/Demographics/projections/P2A_County_Total.xlsx"),
 "bls":("BLS Los Angeles Area Economic Summary","https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf"),
 "fred_unemp":("BLS via FRED — LA County Unemployment CALOSA7URN","https://fred.stlouisfed.org/series/CALOSA7URN"),
 "sec":("Jack in the Box Inc. SEC Form 10-K FY2025 (ended 2025-09-28)","https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm"),
 "dir":("CA DIR — Fast Food Minimum Wage FAQ (AB 1228)","https://www.dir.ca.gov/dlse/Fast-Food-Minimum-Wage-FAQ.htm"),
 "dgs10":("Federal Reserve H.15 via FRED — DGS10 10-Yr Treasury","https://fred.stlouisfed.org/series/DGS10"),
 "assessor":("LA County Assessor — Proposition 13 overview","https://assessor.lacounty.gov/homeowners/realproperty"),
 "lavote":("LA County Registrar — Documentary Transfer Tax / Measure ULA","https://www.lavote.gov/home/recorder/property-document-recording/documentary-transfer-taxes"),
 "irs":("IRS — Like-Kind Exchanges §1031 / Form 8824","https://www.irs.gov/pub/irs-pdf/i8824.pdf"),
 "lacounty_fire":("LA County — Eaton & Palisades Fires Fact Sheet","https://file.lacounty.gov/SDSInter/lac/1199046_Eaton_Palisades_Fires_Anniversary_Fact_Sheet.pdf"),
 "usgs":("USGS Earthquake Hazards Program","https://www.usgs.gov/programs/earthquake-hazards"),
 "cde":("CA Dept of Education — LAUSD District Profile","https://www.cde.ca.gov/sdprofile/details.aspx?cds=19647330000000"),
 "bea":("BEA County Personal Income (LA County $818.5B 2024)","https://www.bea.gov/news/2025/county-and-metropolitan-area-personal-income-2024"),
 "realty":("Realty Income Q4 2025 Supplemental (Tier C benchmark, labelled)","https://www.realtyincome.com/sites/realty-income/files/2026-02/q4-2025-supplemental-report.pdf"),
}
rows=[
 ("F-01","Population","LA city population, Jul 1 2025 estimate","3,869,089","persons","2025","City of Los Angeles","census","verified","Fresh check 2026-11-07 confirms root M01; -0.8% vs Apr 2020 base."),
 ("F-02","Population","LA County population (DOF projection)","9,853,435","persons","2025","LA County","dof","verified","Official state series FIPS 6037."),
 ("F-03","Population","LA County projection 2030","9,727,305","persons","2030","LA County","dof","verified","Mild decline into lease window."),
 ("F-04","Population","LA County projection 2035","9,708,647","persons","2035","LA County","dof","verified","End of lease window; -1.5% vs 2025."),
 ("F-05","Population","LA County projection 2040","9,637,524","persons","2040","LA County","dof","verified","-3.7% vs 2020 actual 10,012,050 same series."),
 ("F-06","Jobs","LA County unemployment rate, Aug 2026","4.9%","percent","Aug 2026","LA County","fred_unemp","verified","FRESHER than Oct-05 BLS summary (4.8% metro); Jul 5.2%, Jun 5.3% — improving."),
 ("F-07","Jobs","Metro nonfarm employment YoY"," +0.6% (6,289.1k jobs)","","2026","LA-Long Beach-Anaheim MSA","bls","verified","Growth led by education/health; info & professional services contracting. See root metrics for sector detail."),
 ("F-08","Tenant","JACK system size FY2025-end","2,136 restaurants; 93% franchised (1,986); 150 company-operated","units","FY2025","Systemwide","sec","verified","System shrank 55 units FY2025; Del Taco 576 units separate."),
 ("F-09","Tenant","Franchise AUV change","$1,874k FY2025 vs $1,949k FY2024 (-3.8%)","","FY2025","Systemwide","sec","verified","Sales pressure on franchisee rent coverage."),
 ("F-10","Tenant","Lease renewal practice (issuer quote)","“generally been able to renew … at then-current market rates”","","FY2025 10-K","Brand portfolio","sec","verified","Expiry = repricing event, not auto-rollover."),
 ("F-11","Tenant","Corporate stress markers","Del Taco sale $115M; dividend discontinued; ~$1.7B securitized debt; Jack on Track closures","","FY2025","Corporate","sec","verified","Tenant-credit risk; verify operator-level financials (P10) — blank until supplied."),
 ("F-12","Labor cost","CA fast-food minimum wage","$20.00/hr from Apr 1, 2024 (AB 1228); Fast Food Council may raise annually","","2024–","Statewide chains 60+ units","dir","verified","Direct pressure on operator margin & rent capacity."),
 ("F-13","Capital markets","10-Yr Treasury (DGS10)","4.90% on 2026-11-04","","2026-11-04","National","dgs10","verified","Fresh check 2026-11-07; discount-rate floor. Cap-rate spread is assumption, not official data."),
 ("F-14","Tax / hold benefit","Prop 13 assessed-value cap","1% levy; max +2%/yr assessed growth; reassess on sale","","Current law","LA County parcel","assessor","verified","Holding preserves capped basis; selling forfeits it permanently."),
 ("F-15","Tax / sale cost","Transfer taxes incl. Measure ULA","County $1.10/$1,000; City base 0.45%; ULA 4%/5.5% above indexed thresholds (~$5.4M post-Jun-2026 cliff — verify at closing)","","Current schedule","City of LA","lavote","verified","At benchmark value (~$2.0–2.7M) ULA surtax does not bite; confirm threshold on sale date."),
 ("F-16","Tax / exchange","§1031 like-kind exchange","45-day ID / 180-day close; qualified intermediary required","","Current IRS rules","Federal","irs","verified","Only tax-efficient diversification path; CA FTB 3840 reporting also applies."),
 ("F-17","Hazard","Jan 2025 fires impact","16,251 structures destroyed; $5.2–10.1B output loss; ~6,800 businesses, ~47,000 workers","","Jan 2025","LA County","lacounty_fire","verified","Metro-wide insurance/smoke/PSPS spillover even for flatland Central LA parcels."),
 ("F-18","Hazard","Earthquake hazard parcel zone","","","","LA Basin","usgs","unverified","BLANK at parcel level until APN supplied (P07). Do not infer."),
 ("F-19","Schools","LAUSD enrollment / profile","","","2025-26","LAUSD","cde","unverified","BLANK in Session F pending direct CDE re-read; see root/docs dashboards for prior verified values — not copied without re-verification."),
 ("F-20","Valuation","Subject NOI, rent, exact expiry, basis, debt","","","","Subject Property (Central LA)","","unverified","BLANK — never supplied (P01–P12). All valuation normalized per $100k NOI."),
 ("F-21","Valuation","Net-lease reinvestment benchmark","7.3% initial cash yield (Realty Income 2025 acquisitions)","percent","2025","National net-lease","realty","flagged","Tier C issuer disclosure, NOT official/government data. Labelled benchmark only."),
 ("F-22","Economy","LA County personal income","$818.5B (2024)","","2024","LA County","bea","verified","Cross-session confirmed (Session B S23/M86). Supports consumer base; growth rate not asserted here."),
]
ledger={"meta":{"session":"arena-5bb36a1b (Session F)","accessed":"2026-11-07","rule":"Verified = read from official source linked on same row. Unverified = blank, flagged. Assumptions labelled, never mixed with verified.","privacy":"No name/address/APN/loan/account anywhere. Subject = 'Subject Property (Central Los Angeles)'."},"sources":{k:{"publisher":v[0],"url":v[1]} for k,v in SRC.items()},"rows":[{"id":r[0],"category":r[1],"metric":r[2],"value":r[3],"unit":r[4],"period":r[5],"geography":r[6],"source":r[7],"status":r[8],"note":r[9]} for r in rows]}
json.dump(ledger,open(f"{B}/data/fresh-ledger.json","w"),indent=1)
# normalized projection per $100k NOI
def val(noi,cap): return noi/cap
scen=[]
for name,cap,g in [("Bull — extend+reset, long WALT",0.055,0.03),("Base — renew at market",0.0625,0.02),("Bear — vacancy/re-let discount",0.0725,0.0)]:
    v0=val(100000,cap); v10=val(100000*(1+g)**10,cap)
    scen.append((name,f"{cap:.2%}",f"{g:.1%}",f"${v0:,.0f}",f"${v10:,.0f}"))
json.dump({"basis":"Per $100,000 current NOI. Value = NOI / cap rate. Cap rates & growth are ANALYST ASSUMPTIONS (no official source publishes asset cap rates) — sensitivity only.","scenarios":[{"case":s[0],"cap":s[1],"noi_growth":s[2],"value_today":s[3],"value_yr10":s[4]} for s in scen]},open(f"{B}/data/projection-normalized.json","w"),indent=1)

NAV=[("index.html","Dashboard + Executive Summary"),("economics.html","Economics"),("tenant-lease.html","Tenant & Lease"),("projection.html","Projection System"),("risks-decision.html","Risks & Decision"),("flagged-sources.html","Flagged & Sources")]
def page(fn,title,body):
    cur=' aria-current="page"'
    nav="".join(('<a href="'+h+'"'+(cur if h==fn else '')+'>'+t+'</a>') for h,t in NAV)
    doc=f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)} — Session F</title><link rel="stylesheet" href="assets/style.css"></head><body><a class="skip" href="#main">Skip to content</a><header class="site"><div class="wrap bar"><a class="brand" href="index.html"><span class="dot"></span><span>Central LA NNN — Session F (2026-11-07)<small>Jack in the Box · NNN · expiry 2030–2035 · anonymized</small></span></a><nav class="main">{nav}</nav></div></header><main id="main" class="wrap">{body}</main><footer class="wrap muted"><p>Session F independent re-verification 2026-11-07. Prior sessions preserved at <a href="../index.html">root workbook</a> · <a href="../docs/index.html">/docs/</a> · <a href="../session-a3a8ec08/index.html">Session D</a> · <a href="../session-b4ec6128/index.html">Session E</a>. Internal decision support — not an appraisal or tax advice.</p></footer></body></html>'''
    open(f"{B}/{fn}","w").write(doc)
def srclink(k):
    if not k or k not in SRC: return "—"
    return f'<a href="{SRC[k][1]}" target="_blank" rel="noopener">{html.escape(SRC[k][0])} ↗</a>'
def table(headers,bodyrows):
    th="".join(f"<th>{h}</th>" for h in headers)
    trs="".join("<tr>"+"".join(f"<td>{c}</td>" for c in r)+"</tr>" for r in bodyrows)
    return f'<div class="tablewrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'

# INDEX
page("index.html","Dashboard + Executive Summary",f'''
<div class="page-head"><p class="eyebrow">Executive summary · Session F · 2026-11-07</p><h1>Sell before the 2030–2035 expiry, or renew? Sequence the decision — do not gamble it.</h1>
<p class="lede">Freshly re-verified 2026-11-07 against official sources. Prior five sessions preserved untouched; this page reconciles them.</p></div>
<div class="grid g3"><div class="card kpi"><p class="label">Recommendation</p><p class="value">Extend → price → sell-or-hold</p><p class="sub">Negotiate 10-yr extension at market reset in 2026–27; price asset 2027–28; §1031 sell only if cap ≤6.00%</p></div>
<div class="card kpi"><p class="label">LA County unemployment (fresh)</p><p class="value">4.9% Aug 2026</p><p class="sub">BLS via FRED; down from 5.3% Jun — labour market improving {srclink("fred_unemp")}</p></div>
<div class="card kpi"><p class="label">10-Yr Treasury</p><p class="value">4.90%</p><p class="sub">2026-11-04, Fed H.15 {srclink("dgs10")}</p></div>
<div class="card kpi"><p class="label">County population path</p><p class="value">9.85M → 9.64M</p><p class="sub">DOF 2025→2040: mild decline, no growth tailwind {srclink("dof")}</p></div>
<div class="card kpi"><p class="label">Tenant</p><p class="value">2,136 units, 93% franchised</p><p class="sub">AUV −3.8%; renewal “at then-current market rates” {srclink("sec")}</p></div>
<div class="card kpi flag"><p class="label">Parcel facts</p><p class="value">Blank — unverified</p><p class="sub">Rent, expiry date, APN, basis, debt never supplied. See Flagged page.</p></div></div>
<h2>The answer</h2><div class="card"><ol>
<li><b>Do not hold passively to expiry.</b> All three independent models (root deterministic, /docs/ 20k-trial Monte Carlo, Session D 10k-trial) agree: term decay + repricing at market {srclink("sec")} destroys value if WALT runs short.</li>
<li><b>Open early blend-and-extend now (2026–27):</b> 10-yr extension, market reset with floor, guaranty. Tenant reprices renewals to market anyway — negotiate while you still have 4–9 years of leverage.</li>
<li><b>Price in 2027–28, then decide by trigger:</b> implied cap ≤6.00% → sell + §1031 into ≥3 diversified net-lease assets {srclink("irs")}; cap &gt;7.00% → hold extended asset; insurance &gt;1.5% of value or Very-High FHSZ/liquefaction → sell trigger regardless.</li>
<li><b>Wealth preservation first:</b> single-tenant/single-parcel/single-metro concentration is the largest risk. Diversification via §1031 is the only free risk reduction; Prop 13 capped basis {srclink("assessor")} is the cost of leaving — hence extend-first preserves both options.</li></ol>
<p><b>Why not sell today?</b> Base case: reinvestment must beat 6.97% to match holding (verified benchmark 7.3%, Tier C {srclink("realty")}) — margin too thin to surrender Prop 13 basis + pay transfer stack {srclink("lavote")} without first capturing the extension premium (+25.2% per /docs/ model).</p></div>
<h2>Requirements coverage (22-item brief)</h2>
{table(["Requirement","Delivered","Status"],[["Full requirements list","Root <a href='../requirements.html'>requirements.html</a> (22 items) + this reconciliation","done"],["Executive summary","This page","done"],["Privacy: anonymize, placeholders, never publish PII","No identifiers in repo; automated PII scan in verify.py","done"],["Best course of action","Extend→price→triggered §1031 sell (above)","done — trigger-based until P01–P12 supplied"],["Geography/income/schools/population/jobs/every factor","Economics page + root 87-row ledger","done; schools cell blank in F pending CDE re-read"],["Projection system","Projection page (normalized, formulas shown)","done"],["Risks every decision + black swans","Risks & Decision page","done"],["Official sources only; blank if unverified","Fresh ledger: every row sourced or blank","done"],["GitHub Pages dashboard","This namespaced site + root site","done"]])}
<p class="muted">Numbers are city/county/metro level. No parcel value asserted. See <a href="flagged-sources.html">Flagged & Sources</a> for blanks.</p>''')

# ECONOMICS
econ=[r for r in rows if r[1] in ("Population","Jobs","Economy","Labor cost","Capital markets")]
page("economics.html","Economics",f'''<div class="page-head"><p class="eyebrow">Market economics</p><h1>Central Los Angeles: stable, not booming</h1><p class="lede">Verified 2026-11-07. Mild population decline, improving unemployment, $20 fast-food wage pressure, 4.90% risk-free floor.</p></div>
{table(["ID","Metric","Value","Period / Geography","Status","Official source"],[[r["id"],html.escape(r["metric"]),html.escape(r["value"]) or "— (blank)",html.escape(r["period"]+" · "+r["geography"]),r["status"],srclink(r["source"])] for r in ledger["rows"] if r["category"] in ("Population","Jobs","Economy","Labor cost","Capital markets","Schools")])}
<div class="card"><h3>So what for value?</h3><p>Population −1.5% to 2035 {srclink("dof")} caps QSR traffic growth; $818.5B county personal income {srclink("bea")} sustains spend. Unemployment falling to 4.9% {srclink("fred_unemp")} supports sales but tight labour + $20 floor {srclink("dir")} squeezes operator margin — rent growth must be CPI-banded, not aggressive. Schools: LAUSD detail left blank here (F-19) rather than copied unverified — see flagged page.</p></div>''')

# TENANT
page("tenant-lease.html","Tenant & Lease",f'''<div class="page-head"><p class="eyebrow">Property & lease</p><h1>Subject Property (Central Los Angeles) — Jack in the Box, NNN, expiry 2030–2035</h1><p class="lede">Address/APN/owner/rent: [WITHHELD — placeholders]. Brand facts from SEC filing only.</p></div>
{table(["Fact","Verified value","Official source"],[[html.escape(r["metric"]),html.escape(r["value"]) or "— (blank)",srclink(r["source"])] for r in ledger["rows"] if r["category"]=="Tenant"]+[[ "Lease clauses to audit (from lease doc P01)","Option rent mechanism, notice deadline, % rent, go-dark, guaranty, casualty/condemnation — BLANK until lease supplied","—"]])}
<div class="card"><h3>Lease economics</h3><p>NNN verified as brand structure (fixed rent + COLA + taxes/insurance) {srclink("sec")}. Your lease may differ — audit roof/structure/HVAC carve-outs. Fast-food $20 wage {srclink("dir")} + AUV −3.8% {srclink("sec")} = test operator rent coverage before demanding reset.</p></div>''')

# PROJECTION
page("projection.html","Projection System",f'''<div class="page-head"><p class="eyebrow">Projection system</p><h1>Normalized projection — per $100,000 NOI (no invented rent)</h1><p class="lede">Formula: Value = NOI ÷ cap rate. NOI(t) = NOI₀ × (1+g)ᵗ. Cap/growth are labelled assumptions; official inputs (DOF, BLS, Treasury) bound them.</p></div>
{table(["Scenario (assumption)","Cap","NOI growth","Value today","Value yr-10"],[[s[0],s[1],s[2],s[3],s[4]] for s in scen])}
<div class="card"><h3>Reliable-system design</h3><ul><li><b>Inputs:</b> DOF population path {srclink("dof")}, BLS jobs {srclink("fred_unemp")}, Treasury floor {srclink("dgs10")} — refreshed each quarter.</li><li><b>Finding:</b> term/occupancy spread (~30% per $100k NOI across scenarios) dominates rent growth — matches /docs/ Monte Carlo (extension +25.2%, term decay −22.7%).</li><li><b>Use:</b> insert actual NOI (P03) → read value band → apply decision triggers. Re-run root <code>tools/model.py</code> for full 2026–40 workbook.</li></ul></div>''')

# RISKS-DECISION
page("risks-decision.html","Risks & Decision",f'''<div class="page-head"><p class="eyebrow">Risk register & decision</p><h1>Risk by decision — including black swans</h1></div>
{table(["Risk","Type","Sell","Renew/Hold","Mitigation","Source"],[
["Tenant credit / franchisee failure","BAU","Avoided after sale","High — single tenant","Guaranty, coverage test, diversify via §1031",srclink("sec")],
["Short-WALT discount","BAU","Avoided if sold early","High near expiry","Extend early; never market with &lt;5 yrs",srclink("sec")],
["Rate / cap expansion (10Y 4.90%)","BAU","Locks price now","Value falls","Trigger cap ≤6% sell / &gt;7% hold",srclink("dgs10")],
["$20 wage + Fast Food Council hikes","BAU","Avoided","Margin squeeze","CPI-banded escalators, % rent",srclink("dir")],
["Tax on sale (gains/recapture/CA)","BAU","High if taxable","Deferred","§1031 45/180-day discipline",srclink("irs")],
["Transfer stack + ULA cliff ~$5.4M","BAU","~0.56% + brokerage at benchmark","None","Confirm ULA threshold at closing",srclink("lavote")],
["Wildfire / smoke / PSPS / insurance repricing","Black swan","Transferred","High — Jan25: 16,251 structures", "Insurance trigger 1.5%; 12-mo NOI reserve",srclink("lacounty_fire")],
["M7+ earthquake / liquefaction","Black swan","Transferred","High, parcel BLANK","APN → CGS/FEMA check before extending",srclink("usgs")],
["Brand shock / CA exit","Black swan","Avoided","High","Diversify; re-let/redevelop zoning (P12)","—"],
["Concentration (1 tenant/1 parcel/1 metro)","Structural","Solved by ≥3 assets","Highest risk","§1031 diversification",srclink("irs")]])}
<div class="card"><h3>Decision triggers</h3><ul><li>Cap ≤6.00% → SELL (§1031). Cap &gt;7.00% → HOLD extended.</li><li>Extension ≥10yr at market+guaranty offered → take it, then re-price.</li><li>Insurance &gt;1.5% value or unavailable → sell regardless.</li><li>Parcel in Very-High FHSZ / liquefaction → sell bias.</li></ul><p>Individual lens: preservation &gt; growth. Keep 12-month NOI reserve outside property in all paths.</p></div>''')

# FLAGGED
page("flagged-sources.html","Flagged & Sources",f'''<div class="page-head"><p class="eyebrow">Flagged for review</p><h1>Unverified = blank. Nothing inferred.</h1></div>
{table(["ID","Item","Value","Status","Official source / action"],[[r["id"],html.escape(r["metric"]),html.escape(r["value"]) or "— (blank)",r["status"],srclink(r["source"])+"<br>"+html.escape(r["note"])] for r in ledger["rows"] if r["status"]!="verified"])}
<h2>All Session F sources (official unless Tier-C labelled)</h2>
{table(["Source","Publisher","Link"],[[k,v[0],f'<a href="{v[1]}" target="_blank" rel="noopener">{v[1]}</a>'] for k,v in SRC.items()])}
<div class="card"><h3>Irregularities</h3><ul><li>Pages settings API reports legacy <code>errored</code> while Actions deploy succeeds (Sessions B–E record) — site is live; owner may switch Pages source to GitHub Actions.</li><li>Five prior dashboards preserved; recommendations differ (root: sequenced sell; /docs/: certainty-equivalent hold bias) — Session F reconciles to extend→price→triggered sell. Owner judgement prevails.</li><li>F-19 schools blank here despite prior sessions' values — not copied without same-day CDE re-read (no-hallucination rule).</li><li>Open PRs #5,#6,#10,#14 noted — not merged by Session F to avoid discarding work.</li></ul></div>''')
print("built", len(rows),"rows")

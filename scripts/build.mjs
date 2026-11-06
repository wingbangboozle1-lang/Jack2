import fs from 'node:fs';
import path from 'node:path';
import { buildScenarioSuite } from './model.mjs';

const root = path.resolve(import.meta.dirname, '..');
const out = path.join(root, 'site');
const research = JSON.parse(fs.readFileSync(path.join(root, 'data/research.json'), 'utf8'));
const analysis = JSON.parse(fs.readFileSync(path.join(root, 'data/analysis.json'), 'utf8'));
const sources = Object.fromEntries(research.sources.map(s => [s.id, s]));
const suite = buildScenarioSuite();
fs.rmSync(out, { recursive: true, force: true });
fs.mkdirSync(path.join(out, 'data'), { recursive: true });
fs.mkdirSync(path.join(root, 'reports'), { recursive: true });

const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]));
const slug = v => v.toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const pct = v => `${(v * 100).toFixed(1)}%`;
const num = v => Number(v).toLocaleString('en-US', { maximumFractionDigits: 2, minimumFractionDigits: 2 });
const link = (href, text, cls = '') => `<a href="${esc(href)}"${/^https?:/.test(href) ? ' target="_blank" rel="noopener noreferrer"' : ''}${cls ? ` class="${cls}"` : ''}>${esc(text)}</a>`;
function sourceCell(id) {
  const s = sources[id];
  if (!s) throw new Error(`Unregistered source: ${id}`);
  const label = s.kind === 'Project source-control record' ? 'Project record' : 'Official source';
  return `<div class="source-cell">${link(s.url, label + ' ↗')}<small>${esc(s.publisher)}</small></div>`;
}
function badge(status) {
  const cls = /Flagged|Unverified|Hypothesis|Pending/i.test(status) ? 'warn' : /forecast|estimate|Analysis|Project|conditional/i.test(status) ? 'info' : 'ok';
  return `<span class="badge ${cls}">${esc(status)}</span>`;
}
const css = `
:root{--ink:#14213d;--muted:#526078;--paper:#f6f7f9;--card:#fff;--line:#d9dee7;--teal:#0f6b62;--teal-soft:#e5f2ef;--amber:#8a5200;--amber-soft:#fff3d6;--blue:#2456a6;--blue-soft:#eaf0fb;--red:#9b2c2c;--radius:14px;--shadow:0 1px 3px rgba(20,33,61,.08)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--paper)}a{color:var(--blue);text-underline-offset:3px}a:hover{color:var(--teal)}.skip{position:absolute;left:-9999px;top:0;background:#fff;padding:10px;z-index:10}.skip:focus{left:8px}.layout{display:grid;grid-template-columns:248px minmax(0,1fr);min-height:100vh}.side{background:var(--ink);color:#fff;padding:26px 18px;position:sticky;top:0;height:100vh;overflow:auto}.brand{font-weight:800;font-size:19px;letter-spacing:.02em;color:#fff;text-decoration:none;display:block;margin:0 8px 6px}.brand small{display:block;font-size:11px;font-weight:600;color:#b9c6db;letter-spacing:.12em;text-transform:uppercase;margin-top:4px}.side nav{margin-top:26px;display:grid;gap:4px}.side nav a{color:#dce5f2;text-decoration:none;padding:9px 12px;border-radius:8px;font-size:14px}.side nav a:hover,.side nav a[aria-current=page]{background:#2a3b5e;color:#fff}.side .foot{font-size:12px;color:#b9c6db;margin:28px 8px 0}.main{min-width:0;padding:34px clamp(18px,4vw,58px) 60px;max-width:1500px;width:100%}.topline{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;color:var(--muted);font-size:13px;margin-bottom:22px}.eyebrow{text-transform:uppercase;letter-spacing:.12em;font-size:12px;font-weight:800;color:var(--teal)}h1{font-size:clamp(28px,4vw,44px);line-height:1.12;margin:8px 0 14px;letter-spacing:-.025em}h2{font-size:24px;margin:34px 0 12px;letter-spacing:-.015em}h3{font-size:18px;margin:0 0 8px}.lead{font-size:18px;color:var(--muted);max-width:900px}.hero{background:linear-gradient(135deg,#14213d,#1d3a5f);color:#fff;border-radius:20px;padding:clamp(24px,4vw,48px);margin-bottom:24px}.hero .eyebrow{color:#8fd4c8}.hero .lead{color:#dce5f2}.hero h1{max-width:900px}.hero-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:22px}.btn{display:inline-block;padding:10px 16px;border-radius:9px;text-decoration:none;font-weight:700;font-size:14px;background:var(--teal);color:#fff;border:1px solid transparent}.btn:hover{color:#fff;filter:brightness(1.08)}.btn.secondary{background:#fff;color:var(--ink)}.btn.ghost{background:transparent;color:#fff;border-color:#7184a3}.grid{display:grid;gap:16px}.cards{grid-template-columns:repeat(auto-fit,minmax(210px,1fr))}.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:20px;box-shadow:var(--shadow)}.card p{margin:8px 0;color:var(--muted)}.metric{font-size:32px;font-weight:800;line-height:1.1}.metric-label{color:var(--muted);font-size:13px;margin-top:6px}.callout{border-left:5px solid var(--teal);background:var(--teal-soft);padding:18px 20px;border-radius:0 12px 12px 0;margin:18px 0}.callout.warn{border-color:#c47b00;background:var(--amber-soft)}.callout.info{border-color:var(--blue);background:var(--blue-soft)}.callout h3{margin-bottom:6px}.callout p:last-child{margin-bottom:0}.badge{display:inline-block;border-radius:999px;padding:3px 9px;font-size:11px;font-weight:800;line-height:1.35;white-space:normal}.badge.ok{background:var(--teal-soft);color:#0b574f}.badge.warn{background:var(--amber-soft);color:var(--amber)}.badge.info{background:var(--blue-soft);color:#234d91}.toolbar{display:flex;gap:12px;align-items:end;flex-wrap:wrap;margin:16px 0 10px}.toolbar label{display:grid;gap:5px;font-size:13px;font-weight:700;flex:1;min-width:240px}.toolbar input{font:inherit;padding:10px 12px;border:1px solid #aeb8c8;border-radius:8px;background:#fff;color:var(--ink);width:100%}.count{font-size:13px;color:var(--muted);padding-bottom:10px}.table-wrap{overflow:auto;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow)}table{border-collapse:collapse;width:100%;min-width:980px;font-size:13px}caption{text-align:left;padding:14px 16px;font-weight:800;font-size:14px;background:#fff;border-bottom:1px solid var(--line)}th,td{padding:12px 14px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}thead th{background:#eef1f5;color:#33415c;font-size:11px;text-transform:uppercase;letter-spacing:.06em;position:sticky;top:0;z-index:1}tbody tr:last-child td{border-bottom:0}tbody tr:hover{background:#fafbfd}.row-id{display:block;font-size:10px;color:var(--muted);font-weight:700;margin-bottom:3px}.metric-name{font-weight:750}.value{font-weight:750;font-variant-numeric:tabular-nums}.blank{background:repeating-linear-gradient(135deg,#fff,#fff 8px,#fbf7ec 8px,#fbf7ec 16px);min-width:90px}.sub{display:block;color:var(--muted);font-size:12px;margin-top:4px}.source-cell{font-size:12px;font-weight:700}.source-cell small{display:block;color:var(--muted);font-weight:500;margin-top:3px;max-width:190px}details{margin-top:7px}summary{cursor:pointer;color:var(--blue);font-size:12px;font-weight:700}blockquote{margin:8px 0;padding:8px 10px;border-left:3px solid var(--line);background:#f7f8fa;color:#33415c;font-size:12px}.note{font-size:12px;color:var(--muted);margin-top:6px}.chips{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}.chip{background:#fff;border:1px solid var(--line);border-radius:999px;padding:6px 12px;font-size:13px;text-decoration:none}.formula{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;background:#14213d;color:#e8f0fb;padding:16px;border-radius:10px;overflow:auto;font-size:13px}.steps{counter-reset:step;display:grid;gap:12px}.step{display:grid;grid-template-columns:34px 1fr;gap:12px}.step:before{counter-increment:step;content:counter(step);width:30px;height:30px;border-radius:50%;background:var(--teal);color:#fff;display:grid;place-items:center;font-weight:800}.chart{width:100%;height:auto;background:#fff;border:1px solid var(--line);border-radius:12px}.footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:12px}.two{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}ul{padding-left:20px}li{margin:6px 0}:focus-visible{outline:3px solid #f0a202;outline-offset:2px}[hidden]{display:none!important}@media(max-width:900px){.layout{display:block}.side{position:static;height:auto;padding:16px}.side nav{display:flex;flex-wrap:wrap;margin-top:14px;gap:4px}.side nav a{padding:6px 9px;font-size:12px}.side .foot{display:none}.main{padding:22px 16px 44px}.brand{font-size:17px}.hero{padding:24px}h1{font-size:30px}}@media print{.side,.toolbar,.hero-actions,.skip{display:none}.layout{display:block}.main{padding:0}.hero{background:#fff;color:#000;border:1px solid #999}.hero .lead,.hero .eyebrow{color:#333}.table-wrap{overflow:visible}table{min-width:0;font-size:10px}a{color:#000}.card{box-shadow:none}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
`;
const js = `
document.querySelectorAll('[data-filter]').forEach(input=>{const table=document.getElementById(input.dataset.filter);const count=document.querySelector('[data-count="'+input.dataset.filter+'"]');const rows=[...table.tBodies[0].rows];const apply=()=>{const q=input.value.trim().toLowerCase();let n=0;rows.forEach(r=>{const show=!q||r.textContent.toLowerCase().includes(q);r.hidden=!show;if(show)n++;});if(count)count.textContent=n+' of '+rows.length+' rows';};input.addEventListener('input',apply);apply();});
`;
const nav = [
  ['index.html','Overview'],['evidence.html','Regional evidence'],['property.html','Property & lease'],
  ['projections.html','Official projections'],['model.html','Scenario model'],['decisions.html','Decision paths'],
  ['risks.html','Risk register'],['tax.html','Tax & exit'],['review.html','Flagged for review'],
  ['sources.html','Source library'],['requirements.html','Requirements & audit'],
];
function page(file, title, body, eyebrow = 'Decision intelligence') {
  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Anonymous, source-linked conditional decision dashboard for a Jack in the Box NNN property. Not an appraisal."><meta name="referrer" content="no-referrer"><title>${esc(title)} | Jack2</title><style>${css}</style></head><body><a class="skip" href="#main">Skip to content</a><div class="layout"><aside class="side"><a class="brand" href="index.html">JACK2<small>Property decision brief</small></a><nav aria-label="Primary">${nav.map(([href,label])=>`<a href="${href}"${href===file?' aria-current="page"':''}>${label}</a>`).join('')}</nav><p class="foot">Anonymous by design.<br>Research cutoff ${esc(research.as_of)}.<br>No analytics, cookies or external runtime assets.</p></aside><main class="main" id="main"><div class="topline"><span>${esc(eyebrow)}</span><span>Source-checked ${esc(research.as_of)} · Conditional analysis, not an appraisal</span></div>${body}<footer class="footer">Public-safe research for [PROPERTY]. County, metropolitan and district figures are proxies, not parcel evidence. Scenario numbers are hypotheses, not verified property inputs. Missing facts remain blank and flagged. ${link('sources.html','Source library')} · ${link('review.html','Review flags')} · ${link('requirements.html','Audit record')}</footer></main></div><script>${js}</script></body></html>`;
  fs.writeFileSync(path.join(out, file), html);
}
let tableSeq = 0;
function dataTable(caption, rows, columns, options = {}) {
  const id = `table-${++tableSeq}`;
  const head = columns.map(c=>`<th scope="col"${c.width?` style="width:${c.width}"`:''}>${esc(c.label)}</th>`).join('');
  const body = rows.map(r=>`<tr data-row-id="${esc(r.id || '')}">${columns.map(c=>c.render(r)).join('')}</tr>`).join('');
  return `<div class="toolbar"><label>Filter this public table (optional)<input type="search" data-filter="${id}" placeholder="Search metric, source, status or note…" autocomplete="off"></label><span class="count" data-count="${id}" aria-live="polite">${rows.length} rows</span>${options.csv?link('data/'+options.csv,'Download CSV','',):''}</div><div class="table-wrap" tabindex="0" role="region" aria-label="${esc(caption)}"><table id="${id}"><caption>${esc(caption)}</caption><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}
const td = (html, cls='') => `<td${cls?` class="${cls}"`:''}>${html}</td>`;
const metricCell = r => td(`<span class="row-id">${esc(r.id)}</span><span class="metric-name">${esc(r.metric)}</span>`);
const valueCell = r => r.value === '' ? '<td class="blank" aria-label="Blank — unverified"></td>' : td(`<span class="value">${esc(r.value)}</span>`);
const contextCell = r => td(`${esc(r.period || '')}<span class="sub">${esc(r.geography || '')}</span>`);
const implicationCell = r => td(`${esc(r.implication)}${r.quote?`<details><summary>Checked excerpt</summary><blockquote>${esc(r.quote)}</blockquote></details>`:''}${r.note?`<div class="note">${esc(r.note)}</div>`:''}`);
const statusCell = r => td(badge(/Unverified/.test(r.status)?'Flagged for Review':r.status));
const srcCell = r => td(sourceCell(r.source_id));
const evidenceColumns = [
  {label:'Metric',render:metricCell,width:'17%'},
  {label:'Value',render:valueCell,width:'12%'},
  {label:'Period / geography',render:contextCell,width:'15%'},
  {label:'Evidence, implication & caveats',render:implicationCell,width:'30%'},
  {label:'Status',render:statusCell,width:'12%'},
  {label:'Issuing source',render:srcCell,width:'14%'},
];
function evidenceTable(rows, caption, csv) { return dataTable(caption, rows, evidenceColumns, {csv}); }
function csv(name, rows, cols) {
  const quote = v => `"${String(v ?? '').replace(/"/g,'""')}"`;
  const lines = [cols.map(c=>quote(c.label)).join(','), ...rows.map(r=>cols.map(c=>quote(c.value(r))).join(','))];
  fs.writeFileSync(path.join(out,'data',name), '\uFEFF'+lines.join('\r\n')+'\r\n');
}
const evidence = research.findings.filter(r=>!r.id.startsWith('P'));
const categories = [...new Set(evidence.map(r=>r.category))];
const csvCols = [
  {label:'ID',value:r=>r.id},{label:'Category',value:r=>r.category},{label:'Metric',value:r=>r.metric},{label:'Value',value:r=>r.value},
  {label:'Period',value:r=>r.period},{label:'Geography',value:r=>r.geography},{label:'Status',value:r=>r.status},
  {label:'Implication',value:r=>r.implication},{label:'Note',value:r=>r.note},{label:'Checked excerpt',value:r=>r.quote},
  {label:'Source publisher',value:r=>sources[r.source_id].publisher},{label:'Official source URL',value:r=>sources[r.source_id].url},{label:'Source checked',value:r=>sources[r.source_id].checked},
];
csv('evidence.csv', evidence, csvCols);
csv('projections.csv', research.projections, csvCols);
csv('property.csv', research.property, csvCols);
csv('risks.csv', research.risks, csvCols);
csv('decisions.csv', research.decisions, csvCols);
csv('flags.csv', research.flags, csvCols);
csv('scenarios.csv', suite.rows, [
  {label:'ID',value:r=>r.id},{label:'Family',value:r=>r.family},{label:'Scenario',value:r=>r.name},{label:'Lease years (hypothesis)',value:r=>r.leaseYears},
  {label:'Outcome',value:r=>r.outcome},{label:'PV multiple of initial rent',value:r=>r.presentValuePerUnitRent.toFixed(6)},
  {label:'Discount rate',value:r=>r.assumptions.discountRate},{label:'Escalation',value:r=>r.assumptions.escalation},{label:'Exit cap',value:r=>r.assumptions.exitCapRate},
  {label:'Downtime months',value:r=>r.assumptions.downtimeMonths},{label:'Releasing cost months',value:r=>r.assumptions.releasingCostMonths},
  {label:'Status',value:()=>'Hypothesis — not verified'},{label:'Method source',value:()=>sources.repo.url},
]);

// Overview
const keyIds = ['E02','E16','E43','E48'];
const keyCards = keyIds.map(id=>{const r=evidence.find(x=>x.id===id);return `<article class="card"><span class="eyebrow">${esc(r.category)}</span><div class="metric">${esc(r.value)}</div><h3>${esc(r.metric)}</h3><p>${esc(r.implication)}</p>${sourceCell(r.source_id)}</article>`;}).join('');
page('index.html','Overview',`
<section class="hero"><span class="eyebrow">Anonymous NNN property decision brief</span><h1>${esc(analysis.recommendation.headline)}</h1><p class="lead">${esc(analysis.recommendation.summary)}</p><div class="hero-actions">${link('decisions.html','Read the decision gates','btn secondary')}${link('model.html','Explore conditional scenarios','btn ghost')}${link('review.html','See what is still unknown','btn ghost')}</div></section>
<div class="callout warn"><h3>Best current answer: run both tracks; do not force a final hold/sell call.</h3><p>${esc(analysis.recommendation.status)} The expiry range 2030–2035 is a user claim. No rent, executable bid, executed option, guaranty or parcel record was supplied, so no actual best price is calculated.</p></div>
<section class="grid cards" aria-label="Research coverage"><div class="card"><div class="metric">${evidence.length}</div><div class="metric-label">regional & tenant evidence rows</div></div><div class="card"><div class="metric">${research.projections.length}</div><div class="metric-label">official forecast rows</div></div><div class="card"><div class="metric">${research.property.length}</div><div class="metric-label">critical property unknowns left blank</div></div><div class="card"><div class="metric">${research.risks.length}</div><div class="metric-label">risk pathways, including rare shocks</div></div><div class="card"><div class="metric">${research.flags.length}</div><div class="metric-label">visible review flags</div></div></section>
<h2>Signals that matter</h2><div class="grid cards">${keyCards}</div>
<h2>Why this is conditional</h2><div class="grid two"><div class="card"><h3>Regional resilience is uneven</h3><ul>${analysis.recommendation.rationale.slice(0,1).map(x=>`<li>${esc(x)}</li>`).join('')}</ul>${sourceCell('census')} ${sourceCell('dof')}</div><div class="card"><h3>Brand scale is not tenant credit</h3><p>${esc(analysis.recommendation.rationale[1])}</p>${sourceCell('jack-q3')}</div><div class="card"><h3>NNN is not risk-free</h3><p>${esc(analysis.recommendation.rationale[2])}</p>${sourceCell('jack-10k')}</div><div class="card"><h3>The lease is the missing foundation</h3><p>${esc(analysis.recommendation.rationale[3])}</p>${link('property.html','Open the blank-field register →')}</div></div>
<h2>Decision sequence</h2><div class="card steps">${analysis.recommendation.next_actions.map(x=>`<div class="step"><div>${esc(x)}</div></div>`).join('')}</div>
<h2>Explore the brief</h2><div class="chips">${nav.slice(1).map(([href,label])=>link(href,label,'chip')).join('')}</div>
`);

// Evidence index and category subpages
page('evidence.html','Regional evidence',`<span class="eyebrow">Source-checked context</span><h1>Regional & tenant evidence</h1><p class="lead">Every row carries its issuing-source link, period, geography and status. County, MSA and district data are proxies; none verifies the subject parcel or store.</p><div class="chips">${categories.map(c=>link(slug(c)+'.html',`${c} (${evidence.filter(r=>r.category===c).length})`,'chip')).join('')}</div>${evidenceTable(evidence,'All regional and tenant evidence','evidence.csv')}<div class="callout info"><h3>How to read status</h3><p>“Source-checked data” means the displayed value was checked against the registered issuing source; it may still be an estimate, preliminary release or commissioned study. “Official forecast” is not an observation. Analytical assumptions live only in the model and are flagged as hypotheses.</p></div>`);
for (const category of categories) {
  const rows = evidence.filter(r=>r.category===category);
  page(slug(category)+'.html',category,`<span class="eyebrow">Evidence category</span><h1>${esc(category)}</h1><p class="lead">${rows.length} source-checked rows. Geography and vintage are preserved; no neighborhood or parcel value is inferred.</p><div class="chips">${link('evidence.html','← All evidence','chip')}${categories.filter(c=>c!==category).map(c=>link(slug(c)+'.html',c,'chip')).join('')}</div>${evidenceTable(rows,category)}`);
}

// Property blanks
page('property.html','Property & lease',`<span class="eyebrow">Verification register</span><h1>Property & lease: what we do not know</h1><p class="lead">All ${research.property.length} property-specific values are deliberately blank. The linked official page is a lookup or topical authority only; it does not confirm a missing value. Each row is flagged for review.</p><div class="callout warn"><h3>Privacy guard</h3><p>No address, parcel number, owner name, contact, account data or identifying financial document is published. Keep diligence documents in a private channel; this public dashboard never asks you to upload them.</p></div>${evidenceTable(research.property,'Blank property inputs — official topic links are not value verification','property.csv')}`);

// Official projections
const forecastRows = research.projections;
const payroll = forecastRows.filter(r=>r.metric.includes('payroll') || r.metric.includes('Payroll'));
page('projections.html','Official projections',`<span class="eyebrow">Forecasts, not observations</span><h1>Official long-run projections</h1><p class="lead">California DOF county forecasts and UCLA statewide forecasts anchor the context. Five-year averages are not annual endpoints; no interpolation, rent elasticity or property uplift is inferred.</p><div class="callout warn"><h3>Methodology break and data-quality flag</h3><p>Caltrans states that forecasts from 2026 use a revised DOF methodology and are not fully comparable with older publications. The extracted county payroll-level series is internally inconsistent, so levels are excluded; published growth rates remain labeled forecasts pending raw-workbook review. ${link('review.html','See flags F02–F03 and F13 →')}</p></div>${evidenceTable(forecastRows,'Official forecast rows','projections.csv')}<h2>County payroll growth context</h2><p class="note">Five-year average annual growth rates as displayed; not this property's rent growth. Source: ${link(sources.dof.url,'California DOF / Caltrans ↗')}.</p>${barChart([{label:'2026–2030 avg',value:0.4},{label:'2031–2035 avg',value:0.6}],'Official county nonfarm payroll growth (%)','#0f6b62')}<div class="callout info"><h3>From regional context to property cash flow</h3><p>The scenario model does not mechanically convert population, income or CPI into rent. It uses explicit, flagged stress controls so the user can see how lease term, vacancy, costs, discount rates and terminal value change a normalized result. ${link('model.html','Open the scenario model →')}</p></div>`);

// Scenario model
const scenarioRows = suite.rows.map(r=>({
  id:r.id, category:'Scenario', metric:`${r.name} · ${r.outcome === 'renew' ? 'tenant-consented renewal' : r.outcome === 'relet' ? 're-let after expiry' : 'no re-let / residual only'}`,
  value:`${num(r.presentValuePerUnitRent)} × R0`, period:`${r.leaseYears}-year income term · 10-year horizon`, geography:r.family,
  source_id:'repo', quote:'', status:'Hypothesis · not verified',
  implication:`PV ${num(r.pv)} per 100 initial rent; terminal share ${pct(r.terminalShare)}. Discount ${pct(r.assumptions.discountRate)}, escalation ${pct(r.assumptions.escalation)}, exit cap ${pct(r.assumptions.exitCapRate)}, downtime ${r.assumptions.downtimeMonths} mo, re-let cost ${r.assumptions.releasingCostMonths} mo.`,
  note:'Dimensionless stress test, not an appraisal, market estimate or probability. Renewal requires tenant consent.',
}));
const assumptionRows = analysis.assumptions.map(a=>({id:a.id,category:'Model assumption',metric:a.parameter,value:a.value,period:'Stress control',geography:'Normalized model',source_id:a.source_id,quote:'',implication:a.basis,status:a.status,note:'Official link supports the mechanism/topic only, not the numeric test point.'}));
const sensitivityRows = suite.sensitivities.map((s,i)=>({id:`S${String(i+1).padStart(2,'0')}`,category:'Sensitivity',metric:s.parameter,value:String(s.value),period:'4-year term · re-let · other controls at reference',geography:'Normalized model',source_id:'repo',quote:'',implication:`PV ${num(s.pv)}; ${num(s.multiple)} × initial annual rent.`,status:'Hypothesis · not verified',note:'One-way mathematical test point, not a market observation.'}));
const expiryCases = suite.rows.filter(r=>r.family==='expiry' && r.outcome==='relet');
page('model.html','Scenario model',`<span class="eyebrow">Conditional projection system</span><h1>Scenario model, not a price target</h1><p class="lead">${esc(suite.disclaimer)}</p><div class="grid cards"><div class="card"><div class="metric">100</div><div class="metric-label">initial annual rent units (scale convention)</div></div><div class="card"><div class="metric">120</div><div class="metric-label">monthly cash flows</div></div><div class="card"><div class="metric">4 / 9</div><div class="metric-label">lease-year proxies for the unverified range</div></div><div class="card"><div class="metric">${suite.rows.length}</div><div class="metric-label">scenario and tail paths</div></div></div><div class="callout warn"><h3>No property-specific recommendation is computed</h3><p>Actual rent, sale value, debt, tax basis, market cap rate and tenant coverage are null in the model. The sale Decision function returns “insufficient-evidence” until same-basis values are supplied privately. Break-even multiples below are before debt payoff and owner income taxes.</p></div><h2>Reference re-let sensitivity by expiry proxy</h2>${barChart(expiryCases.map(r=>({label:r.leaseYears===4?'4-year term':'9-year term',value:r.presentValuePerUnitRent})),'PV multiple of initial annual rent (hypothesis)','#2456a6')}<p class="note">Method source: ${link(sources.repo.url,'project model source ↗')}. This chart is a mathematical stress result, not an official economic forecast.</p><h2>Scenario matrix</h2>${evidenceTable(scenarioRows,'Conditional paths — all values are hypotheses','scenarios.csv')}<h2>Renewal path premium vs re-letting</h2><div class="grid two">${suite.renewalPremiums.map(p=>`<div class="card"><h3>${p.leaseYears}-year proxy</h3><div class="metric">+${num(p.value)}</div><p>PV units per 100 initial rent, reference assumptions. This idealized premium assumes tenant consent, no downtime and no releasing cost; it is not an achievable offer.</p>${sourceCell('repo')}</div>`).join('')}</div><h2>One-way sensitivities</h2>${evidenceTable(sensitivityRows,'Change one control at a time','sensitivities.csv')}<h2>Assumption register</h2>${evidenceTable(assumptionRows,'Every numeric control is flagged as a hypothesis','assumptions.csv')}<h2>Methodology</h2><div class="card">${Object.entries(analysis.methodology).filter(([k])=>k!=='decision_rules').map(([k,v])=>`<h3>${esc(k.replace(/_/g,' '))}</h3><p>${esc(v)}</p>`).join('')}</div><h2>Limitations</h2><div class="card"><ul>${analysis.limitations.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div>`);
csv('sensitivities.csv', sensitivityRows, csvCols);
csv('assumptions.csv', assumptionRows, csvCols);

// Decisions
page('decisions.html','Decision paths',`<span class="eyebrow">Executive decision framework</span><h1>Sell, hold, extend—or change the asset</h1><p class="lead">${esc(analysis.recommendation.summary)}</p><div class="callout"><h3>Recommended process now</h3><p>Run a confidential price-discovery track and an extension negotiation track in parallel. Do not wait passively for expiry, and do not sign an extension merely because it is available.</p></div><h2>Decision thresholds</h2><div class="card">${analysis.methodology.decision_rules.map(x=>`<p>${esc(x)}</p>`).join('')}<div class="formula">Sell gate: net sale value (before debt / owner tax) ≥ conservative hold PV + explicit buffer<br>Extension gate: incremental extension value &gt; incremental costs + retained-risk burden, and competitive with sale</div><p class="note">Do not deduct the same risk twice. Owner-level after-tax, after-debt proceeds and reinvestment alternatives are a separate required comparison.</p></div><h2>Alternatives register</h2>${evidenceTable(research.decisions,'Decision alternatives and gates','decisions.csv')}<h2>Immediate next actions</h2><div class="card steps">${analysis.recommendation.next_actions.map(x=>`<div class="step"><div>${esc(x)}</div></div>`).join('')}</div>`);

// Risks
page('risks.html','Risk register',`<span class="eyebrow">Wealth preservation & growth</span><h1>Risk register: ordinary cycles and rare shocks</h1><p class="lead">${research.risks.length} qualitative pathways. Likelihood and loss are not quantified unless an official source explicitly provides a regional measure; no parcel-level probability is invented.</p><div class="callout warn"><h3>Tail risks are not diversified away by a NNN label</h3><p>Earthquake, wildfire, flood, insurance failure, pandemic, civil unrest, utility/cyber outage and compound macro shocks can interrupt rent or impair residual value even when the tenant survives. Test liquidity and rent-loss coverage, not just headline occupancy.</p></div>${evidenceTable(research.risks,'Risk pathways, exposure, mechanism and mitigation','risks.csv')}`);

// Tax & exit: curated from existing rows, no new factual claims
const taxEvidence = evidence.filter(r=>r.category==='Regulation & tax');
const taxRisks = research.risks.filter(r=>['R12','R13','R14'].includes(r.id));
const taxDecisions = research.decisions.filter(r=>/exchange|installment|sale|refinance/i.test(r.metric));
page('tax.html','Tax & exit',`<span class="eyebrow">Transaction mechanics</span><h1>Tax, reassessment and exit execution</h1><p class="lead">Official rules are jurisdiction- and fact-specific. The exact city, ownership structure, basis, lease terms and closing date are unknown; no tax liability or net proceeds are calculated.</p><div class="callout warn"><h3>Do not confuse “Los Angeles” with the City of Los Angeles</h3><p>Measure ULA is a City tax. An unincorporated-county or other-city property is not subject merely because a listing says Los Angeles. Confirm jurisdiction and closing-date rules before comparing bids.</p></div>${evidenceTable(taxEvidence,'Regulation and tax evidence')}${evidenceTable(taxRisks,'Tax and transfer risk pathways')}${evidenceTable(taxDecisions,'Exit and liquidity alternatives')}`);

// Review flags
page('review.html','Flagged for review',`<span class="eyebrow">Transparent uncertainty</span><h1>Flagged for review</h1><p class="lead">${research.flags.length} nonblocking flags: ${research.property.length} blank property inputs plus source, vintage, geography and interpretation issues. Flags do not block publication; they block false certainty.</p><div class="callout info"><h3>What a flag means</h3><p>A missing value stays blank. An official topic link tells the reader where verification would occur; it is not proof of the missing value. Scenario controls are hypotheses and are never presented as verified property facts.</p></div>${evidenceTable(research.flags,'Complete review-flag register','flags.csv')}`);

// Sources
const sourceRows = research.sources.map(s=>({id:s.id,category:s.kind,metric:s.publisher,value:`Checked ${s.checked}`,period:s.kind,geography:'Issuing-source record',source_id:s.id,quote:'',implication:s.note||'Issuing-source record for the linked evidence rows.',status:'Source record',note:`<details><summary>Curated excerpt</summary><blockquote>${esc(s.excerpt).replace(/\n/g,'<br>')}</blockquote></details>`}));
// Render source note as trusted generated HTML only after escaping its excerpt.
const sourceColumns = evidenceColumns.map(c=>c.label==='Evidence, implication & caveats'?{...c,render:r=>td(`${esc(r.implication)}${r.note}`)}:c);
page('sources.html','Source library',`<span class="eyebrow">Issuing organizations</span><h1>Source library</h1><p class="lead">${research.sources.length} registered sources. Excerpts are curated selections checked on ${esc(research.as_of)}, with whitespace/table formatting normalized; dynamic pages can roll forward. Original-issuer estimates are labeled separately from government statistics.</p>${dataTable('Registered issuing sources and curated excerpts',sourceRows,sourceColumns)}<div class="callout info"><h3>Verification boundary</h3><p>Automated checks confirm that each evidence quote appears in its registered excerpt and that every table row has a source link. They do not independently re-fetch live pages at build time or prove an investment thesis. Recheck live sources before a transaction.</p></div>`);

// Requirements / audit
page('requirements.html','Requirements & audit',`<span class="eyebrow">Implementation record</span><h1>Requirements & repository audit</h1><p class="lead">The initial repository contained only a two-line README. It was reviewed line by line; no personal information or existing evidence files were present. Generated code, data and pages are checked by schema, source-excerpt, privacy, model and internal-link tests.</p>${evidenceTable(research.requirements,'Requirement coverage and integration status','requirements.csv')}<h2>How to reproduce the checks</h2><div class="card"><div class="formula">python research/assemble.py<br>npm run check</div><p>Build is deterministic and dependency-free (Node 22+). The static site uses inline CSS/JS/SVG only. Verification reports are written to <code>reports/</code>; the published site is generated into <code>site/</code>. Neither generated directory is committed.</p>${sourceCell('repo')}</div><h2>Limitations</h2><div class="card"><ul>${analysis.limitations.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div>`);
csv('requirements.csv', research.requirements, csvCols);

// Machine-readable outputs and manifest
fs.writeFileSync(path.join(out,'data/research.json'), JSON.stringify(research,null,2)+'\n');
fs.writeFileSync(path.join(out,'data/analysis.json'), JSON.stringify(analysis,null,2)+'\n');
fs.writeFileSync(path.join(out,'data/model-output.json'), JSON.stringify(suite,null,2)+'\n');
const manifest = { as_of:research.as_of, pages:fs.readdirSync(out).filter(f=>f.endsWith('.html')).sort(), sources:research.sources.length, evidence:evidence.length, projections:research.projections.length, propertyBlanks:research.property.length, risks:research.risks.length, decisions:research.decisions.length, flags:research.flags.length, scenarios:suite.rows.length, sensitivities:suite.sensitivities.length };
fs.writeFileSync(path.join(out,'data/manifest.json'), JSON.stringify(manifest,null,2)+'\n');
fs.writeFileSync(path.join(root,'reports/build-manifest.json'), JSON.stringify(manifest,null,2)+'\n');
console.log(`Built ${manifest.pages.length} pages, ${manifest.sources} sources, ${manifest.evidence} evidence rows, ${manifest.scenarios} scenario paths.`);

function barChart(items, title, color) {
  const width=760,height=230,left=150,right=70,top=42,bottom=42;
  const max=Math.max(...items.map(i=>Math.abs(i.value)),1)*1.15;
  const plotW=width-left-right, rowH=(height-top-bottom)/items.length;
  const bars=items.map((it,i)=>{const y=top+i*rowH+8,w=Math.abs(it.value)/max*plotW;return `<text x="${left-12}" y="${y+15}" text-anchor="end" font-size="13" fill="#33415c">${esc(it.label)}</text><rect x="${left}" y="${y}" width="${w.toFixed(1)}" height="24" rx="5" fill="${color}"/><text x="${left+w+10}" y="${y+16}" font-size="13" font-weight="700" fill="#14213d">${num(it.value)}</text>`;}).join('');
  return `<svg class="chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(title)}"><title>${esc(title)}</title><text x="${left}" y="24" font-size="14" font-weight="700" fill="#14213d">${esc(title)}</text>${bars}<line x1="${left}" x2="${left}" y1="${top-4}" y2="${height-bottom+8}" stroke="#d9dee7"/></svg>`;
}

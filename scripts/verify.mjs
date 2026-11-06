import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { propertyInputs, buildScenarioSuite } from './model.mjs';

const root = path.resolve(import.meta.dirname, '..');
const norm = v => String(v ?? '').replace(/\s+/g, ' ').trim();
const fail = (msg) => { throw new Error(msg); };
const readJSON = p => JSON.parse(fs.readFileSync(p, 'utf8'));

export function validateResearch(data) {
  const errors = [];
  const sources = new Map((data.sources || []).map(s => [s.id, s]));
  if (!sources.size) errors.push('No sources registered');
  for (const s of sources.values()) {
    for (const k of ['id','publisher','url','checked','kind','excerpt']) if (!s[k]) errors.push(`Source ${s.id} missing ${k}`);
    try { const u = new URL(s.url); if (u.protocol !== 'https:') errors.push(`Source ${s.id} is not HTTPS`); } catch { errors.push(`Source ${s.id} invalid URL`); }
  }
  const sections = ['findings','property','projections','risks','decisions','flags','requirements'];
  const ids = new Map();
  let rowCount = 0, blankCount = 0;
  for (const section of sections) {
    if (!Array.isArray(data[section])) { errors.push(`Missing section ${section}`); continue; }
    const sectionIds = new Set();
    for (const r of data[section]) {
      for (const k of ['id','category','metric','period','geography','source_id','implication','status']) if (r[k] === undefined || r[k] === null) errors.push(`${section}/${r.id || '?'} missing ${k}`);
      if (sectionIds.has(r.id)) errors.push(`Duplicate row id ${r.id} within ${section}`);
      sectionIds.add(r.id);
      const prior = ids.get(r.id);
      if (prior && !(section === 'projections' && prior === 'findings')) errors.push(`Duplicate row id ${r.id} across ${prior}/${section}`);
      if (!prior) { ids.set(r.id, section); rowCount++; }
      const s = sources.get(r.source_id);
      if (!s) errors.push(`${r.id} has unregistered source ${r.source_id}`);
      if (r.quote && s && !norm(s.excerpt).includes(norm(r.quote))) errors.push(`${r.id} quote not found in registered excerpt`);
      if (section === 'property') {
        if (r.value !== '') errors.push(`${r.id} property value must remain blank`);
        else blankCount++;
        if (!/Unverified/.test(r.status || '')) errors.push(`${r.id} property row must be unverified`);
        if (!data.flags.some(f => f.id === `F-${r.id}`)) errors.push(`${r.id} missing review flag`);
      }
    }
  }
  const projectionIds = new Set(data.projections.map(r => r.id));
  for (const r of data.findings.filter(r => r.id.startsWith('P'))) if (!projectionIds.has(r.id)) errors.push(`${r.id} missing from projections`);
  if (errors.length) fail(errors.join('\n'));
  return { rows: rowCount, sources: sources.size, propertyBlanks: blankCount };
}

export function validateHTML(html, file, sourceURLs, exists) {
  const errors = [];
  if (!/<html lang="en">/.test(html)) errors.push(`${file}: missing lang`);
  if (!/<main\b[^>]*id="main"/.test(html)) errors.push(`${file}: missing main landmark`);
  if (!/<meta name="viewport"/.test(html)) errors.push(`${file}: missing viewport`);
  if (/<script\b[^>]*\bsrc\s*=|<link\b[^>]*rel=["']stylesheet|<iframe\b|\bfetch\s*\(|XMLHttpRequest|localStorage|document\.cookie/i.test(html)) errors.push(`${file}: external runtime asset, embedding or tracking detected`);
  const tables = [...html.matchAll(/<table\b[^>]*>([\s\S]*?)<\/table>/g)];
  let dataRows = 0;
  for (const t of tables) {
    if (!/<caption>/.test(t[1])) errors.push(`${file}: table missing caption`);
    const body = t[1].match(/<tbody>([\s\S]*?)<\/tbody>/)?.[1] || '';
    for (const row of body.matchAll(/<tr\b[^>]*>([\s\S]*?)<\/tr>/g)) {
      dataRows++;
      const hrefs = [...row[1].matchAll(/href="([^"]+)"/g)].map(m => m[1].replace(/&amp;/g,'&'));
      if (!hrefs.some(h => sourceURLs.has(h))) errors.push(`${file}: data row ${dataRows} lacks a registered official-source link`);
    }
  }
  const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]));
  for (const m of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    const href = m[1].replace(/&amp;/g,'&');
    if (/^(https?:|mailto:|tel:|data:)/.test(href)) continue;
    const [target, frag] = href.split('#');
    const resolved = target ? path.resolve(path.dirname(file), target) : file;
    if (!exists(resolved)) errors.push(`${file}: broken internal link ${href}`);
    else if (frag) {
      const targetHTML = resolved === file ? html : fs.readFileSync(resolved, 'utf8');
      if (!new RegExp(`\\bid="${frag.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}"`).test(targetHTML)) errors.push(`${file}: broken anchor ${href}`);
    }
  }
  const visible = html.replace(/<script\b[\s\S]*?<\/script>/g,' ').replace(/<style\b[\s\S]*?<\/style>/g,' ').replace(/<[^>]+>/g,' ');
  const privacyPatterns = [
    [/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i, 'email address'],
    [/\b\d{3}-\d{2}-\d{4}\b/, 'SSN-like identifier'],
    [/\b(?:\+1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b/, 'phone number'],
    [/\b\d{1,6}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}\s+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Lane|Ln|Way|Court|Ct)\b/, 'street address'],
  ];
  for (const [re, label] of privacyPatterns) if (re.test(visible)) errors.push(`${file}: possible ${label} in visible text`);
  if (errors.length) fail(errors.join('\n'));
  return { tables: tables.length, dataRows };
}

export function validateCSV(text, sourceURLs, requireBlankValue = false) {
  const lines = text.replace(/^\uFEFF/, '').trim().split(/\r?\n/);
  const parse = line => [...line.matchAll(/"((?:[^"]|"")*)"/g)].map(m => m[1].replace(/""/g,'"'));
  const header = parse(lines[0]);
  const sourceIndex = header.findIndex(h => /source URL|Method source/i.test(h));
  if (sourceIndex < 0) fail('CSV missing source URL column');
  const valueIndex = header.indexOf('Value');
  let rows = 0;
  for (const line of lines.slice(1)) {
    const cells = parse(line); rows++;
    if (cells.length !== header.length) fail(`CSV row ${rows} column mismatch`);
    if (!sourceURLs.has(cells[sourceIndex])) fail(`CSV row ${rows} missing registered source URL`);
    if (requireBlankValue && cells[valueIndex] !== '') fail(`CSV property row ${rows} has a populated value`);
  }
  return rows;
}

function hashTree(dir) {
  const result = {};
  const walk = d => { for (const e of fs.readdirSync(d, {withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))) { const p=path.join(d,e.name); if(e.isDirectory()) walk(p); else result[path.relative(dir,p)] = crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'); } };
  walk(dir); return result;
}

export function runVerification() {
  const data = readJSON(path.join(root,'data/research.json'));
  const analysis = readJSON(path.join(root,'data/analysis.json'));
  const researchStats = validateResearch(data);
  const sourceURLs = new Set(data.sources.map(s=>s.url));
  const site = path.join(root,'site');
  if (!fs.existsSync(site)) fail('site/ missing; run npm run build first');
  const before = hashTree(site);
  execFileSync(process.execPath, [path.join(root,'scripts/build.mjs')], {cwd:root, stdio:'pipe'});
  const after = hashTree(site);
  if (JSON.stringify(before) !== JSON.stringify(after)) fail('Build is not deterministic');
  const pages = fs.readdirSync(site).filter(f=>f.endsWith('.html')).sort();
  let tables=0, dataRows=0;
  for (const f of pages) { const stats=validateHTML(fs.readFileSync(path.join(site,f),'utf8'), path.join(site,f), sourceURLs, p=>fs.existsSync(p)); tables+=stats.tables; dataRows+=stats.dataRows; }
  let csvRows=0;
  for (const f of fs.readdirSync(path.join(site,'data')).filter(f=>f.endsWith('.csv'))) csvRows += validateCSV(fs.readFileSync(path.join(site,'data',f),'utf8'), sourceURLs, f==='property.csv');
  for (const f of ['research.json','analysis.json','model-output.json','manifest.json']) readJSON(path.join(site,'data',f));
  if (!Object.values(propertyInputs).every(v=>v===null)) fail('Real property inputs were populated');
  for (const a of analysis.assumptions) { if (!sourceURLs.has(data.sources.find(s=>s.id===a.source_id)?.url)) fail(`Assumption ${a.id} missing source`); if (!/Hypothesis/.test(a.status)) fail(`Assumption ${a.id} not flagged as hypothesis`); }
  const suite = buildScenarioSuite();
  if (suite.rows.length !== 16 || suite.sensitivities.length !== 15) fail('Unexpected scenario coverage');
  if (!suite.rows.every(r=>Number.isFinite(r.pv))) fail('Nonfinite scenario output');
  const manifest = readJSON(path.join(site,'data/manifest.json'));
  if (manifest.pages.length !== pages.length) fail('Manifest page count mismatch');
  const report = {
    status:'pass', as_of:data.as_of, pages:pages.length, tables, htmlDataRows:dataRows, csvRows,
    ...researchStats, scenarios:suite.rows.length, sensitivities:suite.sensitivities.length,
    deterministicBuild:true, internalLinks:'pass', rowSourceLinks:'pass', sourceExcerptSubstrings:'pass', privacyPatternScan:'pass', modelInputBlanks:'pass',
    externalLinkBoundary:'URLs were checked against issuing pages during research; automated verification validates HTTPS syntax and registry membership, not live HTTP availability at build time.',
    limitations:analysis.limitations,
  };
  fs.mkdirSync(path.join(root,'reports'), {recursive:true});
  fs.writeFileSync(path.join(root,'reports/verification.json'), JSON.stringify(report,null,2)+'\n');
  fs.writeFileSync(path.join(root,'reports/verification.md'), `# Verification report\n\n- Status: **PASS**\n- Research cutoff: ${report.as_of}\n- Pages: ${report.pages}\n- Tables: ${report.tables}\n- HTML data rows with registered source links: ${report.htmlDataRows}\n- CSV data rows with registered source URLs: ${report.csvRows}\n- Source records: ${report.sources}\n- Blank property fields: ${report.propertyBlanks}\n- Scenario paths / sensitivities: ${report.scenarios} / ${report.sensitivities}\n- Deterministic rebuild: pass\n- Internal links/anchors: pass\n- Source-excerpt substring checks: pass\n- Privacy pattern scan: pass\n- Model property inputs remain null: pass\n\n## Boundary\n\n${report.externalLinkBoundary}\n\n${report.limitations.map(x=>'- '+x).join('\n')}\n`);
  return report;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try { const r=runVerification(); console.log(`Verification PASS: ${r.pages} pages, ${r.htmlDataRows} sourced HTML rows, ${r.csvRows} sourced CSV rows, ${r.propertyBlanks} blank property fields.`); }
  catch (e) { console.error('Verification FAIL:\n'+e.message); process.exitCode=1; }
}

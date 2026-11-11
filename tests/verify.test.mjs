import test from 'node:test';
import assert from 'node:assert/strict';
import { validateResearch, validateHTML, validateCSV } from '../scripts/verify.mjs';

const source = {id:'s1',publisher:'Official issuer',url:'https://example.gov/data',checked:'2026-11-06',kind:'Government primary',excerpt:'Population 1000'};
const row = {id:'E01',category:'Test',metric:'Population',value:'1000',period:'2026',geography:'County',source_id:'s1',quote:'Population 1000',implication:'Context',status:'Source-checked data',note:''};
const base = {sources:[source],findings:[row],property:[],projections:[],risks:[],decisions:[],flags:[],requirements:[]};

test('research validator accepts a fully sourced row and excerpt', () => {
  assert.equal(validateResearch(base).rows,1);
});
test('unregistered source and mismatched quote fail closed', () => {
  assert.throws(()=>validateResearch({...base,findings:[{...row,source_id:'missing'}]}),/unregistered source/);
  assert.throws(()=>validateResearch({...base,findings:[{...row,quote:'Population 2000'}]}),/quote not found/);
});
test('populated property value and missing flag fail closed', () => {
  const p={...row,id:'U01',value:'secret',status:'Unverified'};
  assert.throws(()=>validateResearch({...base,property:[p]}),/must remain blank/);
  assert.throws(()=>validateResearch({...base,property:[{...p,value:''}]}),/missing review flag/);
});
test('blank property row with matching flag passes', () => {
  const p={...row,id:'U01',value:'',status:'Unverified'};
  const f={...row,id:'F-U01',source_id:'s1',quote:''};
  assert.equal(validateResearch({...base,property:[p],flags:[f]}).propertyBlanks,1);
});
const html = `<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width"></head><body><main id="main"><table><caption>T</caption><tbody><tr><td>1000</td><td><a href="https://example.gov/data">Official source</a></td></tr></tbody></table><a href="#main">top</a></main></body></html>`;
const urls = new Set([source.url]);
test('HTML validator requires a registered source on every data row', () => {
  assert.equal(validateHTML(html,'/tmp/index.html',urls,()=>true).dataRows,1);
  assert.throws(()=>validateHTML(html.replace('https://example.gov/data','https://other.example'),'/tmp/index.html',urls,()=>true),/lacks a registered official-source link/);
});
test('broken internal link and missing anchor fail', () => {
  assert.throws(()=>validateHTML(html.replace('href="#main"','href="missing.html"'),'/tmp/index.html',urls,()=>false),/broken internal link/);
  assert.throws(()=>validateHTML(html.replace('href="#main"','href="#missing"'),'/tmp/index.html',urls,()=>true),/broken anchor/);
});
test('external runtime assets, tracking and visible PII fail', () => {
  assert.throws(()=>validateHTML(html.replace('</head>','<script src="https://cdn.example/x.js"></script></head>'),'/tmp/index.html',urls,()=>true),/external runtime/);
  assert.throws(()=>validateHTML(html.replace('</main>','<p>owner@example.com</p></main>'),'/tmp/index.html',urls,()=>true),/email address/);
  assert.throws(()=>validateHTML(html.replace('</main>','<p>123 Main Street</p></main>'),'/tmp/index.html',urls,()=>true),/street address/);
});
test('CSV requires source URL on every row and blank property values', () => {
  const csv='﻿"ID","Value","Official source URL"\r\n"E01","1000","https://example.gov/data"\r\n';
  assert.equal(validateCSV(csv,urls),1);
  assert.throws(()=>validateCSV(csv,urls,true),/populated value/);
  assert.throws(()=>validateCSV(csv.replace('https://example.gov/data','https://other.example'),urls),/missing registered source/);
});

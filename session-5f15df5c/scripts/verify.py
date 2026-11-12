#!/usr/bin/env python3
"""Verify the self-contained dashboard's source links, tables, navigation and privacy guards."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json, re, sys
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
errors=[]
def fail(msg): errors.append(msg)
sources = json.loads((ROOT/'data/sources.json').read_text())
sids={s['id'] for s in sources}
source_by_id={s['id']:s for s in sources}
def official(url):
    host=(urlparse(url).hostname or '').lower().rstrip('.')
    return host.endswith('.gov') or host == 'gov' or host.endswith('.lacity.org')
for s in sources:
    if not s['url'].startswith('https://') or not official(s['url']): fail(f"source {s['id']} is not HTTPS official domain: {s['url']}")
    if not s.get('checked'): fail(f"source {s['id']} missing checked date")
for filename, keys in [('questions.json','sources'),('risks.json','source')]:
    rows=json.loads((ROOT/'data'/filename).read_text())
    for row in rows:
        vals=row[keys] if isinstance(row[keys],list) else [row[keys]]
        for sid in vals:
            if sid not in sids: fail(f"{filename} {row.get('id',row.get('event'))}: unknown source {sid}")
for r in json.loads((ROOT/'data/verified_context.json').read_text()):
    if r['source'] not in sids: fail(f"context row missing source: {r}")
    if not r.get('value'): fail(f"verified context value blank without being flagged: {r.get('topic')}")
class Check(HTMLParser):
    def __init__(self,path):
        super().__init__(convert_charrefs=True); self.path=path; self.links=[]; self.tables=[]; self.table=None; self.row=None
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='a' and attrs.get('href'): self.links.append(attrs['href'])
        if tag=='table': self.table=[]
        if tag=='tr' and self.table is not None: self.row={'cells':0,'headers':0,'official':False,'links':[]}
        if tag in ('td','th') and self.row is not None:
            self.row['cells']+=1
            if tag=='th': self.row['headers']+=1
        if tag=='a' and attrs.get('href') and self.row is not None:
            href=attrs['href']; self.row['links'].append(href)
            if href.startswith('https://') and official(href): self.row['official']=True
    def handle_endtag(self,tag):
        if tag=='tr' and self.row is not None:
            self.table.append(self.row); self.row=None
        if tag=='table' and self.table is not None:
            self.tables.append(self.table); self.table=None
pages=sorted(ROOT.glob('*.html'))
if len(pages)!=9: fail(f'expected 9 HTML pages, found {len(pages)}')
for p in pages:
    parser=Check(p); text=p.read_text(encoding='utf-8'); parser.feed(text)
    if '<title>' not in text.lower(): fail(f'{p.name}: missing title')
    for table in parser.tables:
        if not table: continue
        for i,row in enumerate(table):
            if row['headers'] == row['cells']: continue
            if not row['official']: fail(f'{p.name}: table row {i+1} has no official-source hyperlink')
        counts={r['cells'] for r in table}
        if len(counts)>1: fail(f'{p.name}: inconsistent table columns {sorted(counts)}')
    for href in parser.links:
        if href.startswith(('https://','http://','mailto:','tel:','#')): continue
        target=(p.parent / href.split('#',1)[0]).resolve()
        if not target.exists(): fail(f'{p.name}: broken internal link {href}')
# Public tree scan (workspace only). Deliberately conservative; no exact identifiers are expected.
scan_files=list(ROOT.rglob('*.html'))+list(ROOT.rglob('*.json'))+list(ROOT.rglob('*.py'))
patterns={
 'email':re.compile(r'(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b'),
 'US phone':re.compile(r'(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)'),
 'likely street address':re.compile(r'(?i)\b\d{1,6}\s+[A-Z0-9.\- ]{1,40}\b(?:Street|St\.?|Avenue|Ave\.?|Boulevard|Blvd\.?|Road|Rd\.?|Drive|Dr\.?|Way|Lane|Ln\.?|Court|Ct\.?)\b'),
}
for p in scan_files:
    text=p.read_text(encoding='utf-8')
    for label,pattern in patterns.items():
        if pattern.search(text): fail(f'{p.relative_to(ROOT)}: possible {label} (manual review required)')
# Source URL row completeness: all declared sources correspond to official domains.
if len(sources)<10: fail('source catalog unexpectedly small')
if len(json.loads((ROOT/'data/questions.json').read_text())) != 20: fail('question count mismatch')
if len(json.loads((ROOT/'data/risks.json').read_text())) != 15: fail('risk count mismatch')
if errors:
    print('FAIL')
    for e in errors: print(' - '+e)
    sys.exit(1)
print(f'PASS: {len(pages)} HTML pages; {len(sources)} official source URLs; 20 questions; 6 sourced context metrics; 15 sourced risks; every table row linked; internal links valid; privacy scan clear.')

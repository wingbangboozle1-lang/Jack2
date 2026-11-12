#!/usr/bin/env python3
"""Independent QA gate for the cfe293bd Pages workbook."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import json, re, sys
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
srcdoc=json.loads((DATA/'sources.json').read_text())
sources={s['id']:s for s in srcdoc['sources']}
metrics=json.loads((DATA/'metrics.json').read_text())['rows']
questions=json.loads((DATA/'questions.json').read_text())
suggestions=json.loads((DATA/'suggestions.json').read_text())
risks=json.loads((DATA/'risks.json').read_text())
errors=[]
def check(condition,message):
    if not condition: errors.append(message)

for s in sources.values():
    host=urlparse(s['url']).hostname or ''
    check(s['url'].startswith('https://') and host.endswith('.gov'),f"non-official/non-HTTPS source: {s['id']} {s['url']}")
for record in metrics+questions+suggestions+risks:
    for sid in [record.get('source')] + record.get('also_sources',[]):
        check(sid in sources,f"missing source id {sid}: {record.get('id')}")
for r in metrics:
    check(r['status'] in ('verified','unverified'),f"invalid status: {r['id']}")
    check(bool(r['value'].strip()) if r['status']=='verified' else r['value']=='',f"blank/value rule violation: {r['id']}")

class Links(HTMLParser):
    def __init__(self): super().__init__(); self.hrefs=[]; self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('href'): self.hrefs.append(a['href'])
        if a.get('id'): self.ids.add(a['id'])
        if tag=='a' and a.get('name'): self.ids.add(a['name'])

html_files=sorted(ROOT.glob('*.html'))
check(len(html_files)==11,f"expected 11 HTML pages, found {len(html_files)}")
for page in html_files:
    parser=Links(); parser.feed(page.read_text(errors='replace'))
    for href in parser.hrefs:
        parsed=urlparse(href)
        if parsed.scheme or href.startswith('//') or not parsed.path: continue
        target=(page.parent/unquote(parsed.path)).resolve()
        check(target.exists(),f"broken link {page.name} -> {href}")
        if parsed.fragment and target.suffix.lower() in ('.html','.htm') and target.exists():
            dest=Links(); dest.feed(target.read_text(errors='replace'))
            check(unquote(parsed.fragment) in dest.ids,f"broken fragment {page.name} -> {href}")

scan='\n'.join(p.read_text(errors='replace') for p in ROOT.rglob('*') if p.is_file() and p.suffix.lower() in ('.html','.json','.css','.js'))
for pattern,label in [
 (r'\bAPN\s*[:#]?\s*\d{4,}','parcel number'),
 (r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}','email'),
 (r'\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}','phone'),
 (r'\b\d{1,6}\s+(?:[A-Z][a-z]+\s+){1,3}(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr)\b','street address')]:
    check(re.search(pattern,scan) is None,f"possible PII pattern found: {label}")

checks={
 'all data rows resolve to official HTTPS .gov sources':not any('source id' in e or 'source:' in e for e in errors),
 'verified values populated / unverified values blank':not any('blank/value' in e for e in errors),
 'all local links and fragments resolve':not any('broken link' in e or 'broken fragment' in e for e in errors),
 'no common personal/parcel identifier patterns':not any('PII pattern' in e for e in errors),
 '11 HTML pages generated':not any('expected 11' in e for e in errors),
}
summary={'pages':len(html_files),'sources':len(sources),'metrics':len(metrics),'verified_metrics':sum(r['status']=='verified' for r in metrics),'blank_metrics':sum(r['status']=='unverified' for r in metrics),'questions':len(questions),'suggestions':len(suggestions),'risks':len(risks),'checks':checks,'errors':errors}
(ROOT/'verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
sys.exit(bool(errors))

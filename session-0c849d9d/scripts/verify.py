from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import re
root=Path(__file__).resolve().parents[1]
errors=[]
class Audit(HTMLParser):
 def __init__(self,path): super().__init__(); self.path=path; self.row=False; self.body=False; self.link=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='tbody': self.body=True
  if tag=='tr' and self.body: self.row=True; self.link=False
  if tag=='a':
   h=a.get('href','')
   if self.row and h.startswith('https://'): self.link=True
   if h and not h.startswith(('https://','http://','#','mailto:')):
    f=urlsplit(h).path
    if f and not (self.path.parent/f).resolve().exists(): errors.append(f'{self.path}: broken {h}')
 def handle_endtag(self,tag):
  if tag=='tr' and self.row:
   if not self.link: errors.append(f'{self.path}: row without source')
   self.row=False
  if tag=='tbody': self.body=False
for p in root.glob('*.html'):
 text=p.read_text(); a=Audit(p);a.feed(text)
 if re.search(r'\b\d{3}-\d{2}-\d{4}\b',text): errors.append(f'{p}: possible SSN')
print('\n'.join(errors) if errors else 'PASS: local links, table source links, limited SSN-pattern scan')
raise SystemExit(bool(errors))

import re,glob,json,sys
bad=[]
for f in glob.glob("session-5bb36a1b/*.html"):
    t=open(f).read()
    for h in re.findall(r'href="([^"]+)"',t):
        if h.startswith(("http","#","../")): continue
        import os
        if not os.path.exists(os.path.join("session-5bb36a1b",h.split("#")[0])): bad.append((f,h))
    if re.search(r'\b\d{3}-\d{2}-\d{4}\b|APN\s*[:#]?\s*\d{3}-\d{3}',t): bad.append((f,"PII?"))
d=json.load(open("session-5bb36a1b/data/fresh-ledger.json"))
for r in d["rows"]:
    if r["status"]=="verified" and not r["value"]: bad.append((r["id"],"verified blank"))
    if r["status"]=="verified" and r["source"] not in d["sources"]: bad.append((r["id"],"no source"))
    if r["status"]=="unverified" and r["value"]: bad.append((r["id"],"unverified filled"))
print("FAIL",bad) if bad else print(f"pass: {len(glob.glob('session-5bb36a1b/*.html'))} pages, {len(d['rows'])} rows")
sys.exit(1 if bad else 0)

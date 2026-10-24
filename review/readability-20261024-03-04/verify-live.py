#!/usr/bin/env python3
"""Compare this release with the HTTPS site, using curl's normal TLS checks."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
PAGES='1ac55e353511185c278267e2043dce86630d68b5'
FILES=['index.html','app.js','knowledge-links.js','knowledge-links.css','readable-lectures.css','cases.js','business-cases.js','content/01_intro.json','content/02_enterprise_data_model.json','content/03_sql_kpi.json','content/04_data_quality.json','content/concept-map.json','content/catalog.json','content/source-manifest.json','content/business-cases.json','content/case-cards.json','content/business-casebook.json','content/lecture-slides.json','CNAME']

def fetch(url):
 with tempfile.NamedTemporaryFile() as tmp:
  result=subprocess.run(['curl','--fail','--location','--silent','--show-error','--retry','2','--max-time','35','--output',tmp.name,'--write-out','%{http_code}\t%{url_effective}',url],capture_output=True,check=True)
  status,final=result.stdout.decode().split('\t',1)
  return tmp.read(),final,int(status)

def check(path):
 raw,url,status=fetch('https://datasci.biz/'+path+'?verify='+PAGES[:7])
 local=(ROOT/'dist'/path).read_bytes()
 return {'path':path,'status':status,'url':url,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'localMatches':raw==local}

def main():
 with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(check,FILES))
 redirects=[]
 for url in ['http://datasci.biz/','https://www.datasci.biz/','http://www.datasci.biz/','https://cosmos-1989.github.io/big-data-and-management-decision/']:
  raw,final,status=fetch(url);redirects.append({'requested':url,'final':final,'status':status,'canonical':final=='https://datasci.biz/'})
 home,_,_=fetch('https://datasci.biz/')
 home_matches=home==(ROOT/'dist/index.html').read_bytes()
 report={'canonicalHomeMatches':home_matches,'canonicalHomeSha256':hashlib.sha256(home).hexdigest(),'checkedAt':datetime.now(timezone.utc).isoformat(),'publishedRevision':PAGES,'tls':'curl default certificate validation enabled; no insecure override','files':results,'redirects':redirects,'passed':home_matches and all(r['localMatches'] for r in results) and all(r['canonical'] for r in redirects)}
 Path(__file__).with_name('live-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'passed':report['passed'],'files':len(results),'mismatches':[r['path'] for r in results if not r['localMatches']],'redirects':redirects},ensure_ascii=False,indent=2))
 raise SystemExit(0 if report['passed'] else 1)

if __name__=='__main__':main()

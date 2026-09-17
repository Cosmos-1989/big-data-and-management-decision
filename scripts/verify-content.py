from pathlib import Path
import json,re,urllib.parse
from bs4 import BeautifulSoup
OUT=Path(__file__).resolve().parents[1]/'dist'
docs={p.stem:json.loads(p.read_text()) for p in (OUT/'content').glob('*.json') if 'html' in json.loads(p.read_text())}
ids={k:{e['id'] for e in BeautifulSoup(d['html'],'html.parser').find_all(id=True)} for k,d in docs.items()}
errors=[];math=[];stats={'pages':len(docs),'tables':0,'figures':0,'equations':0}
for id,d in docs.items():
 s=BeautifulSoup(d['html'],'html.parser');stats['tables']+=len(s.find_all('table'));stats['figures']+=len(s.find_all('img'))
 for a in s.find_all('a',href=True):
  h=a['href']
  if h.startswith('#/chapter/'):
   path,_,q=h.partition('?');target=path[10:];anchor=urllib.parse.parse_qs(q).get('anchor',[None])[0]
   if target not in docs:errors.append([id,'missing chapter',h])
   elif anchor and anchor not in ids[target]:errors.append([id,'missing anchor',h])
  if h.startswith('/') and not (OUT/urllib.parse.unquote(h[1:])).exists():errors.append([id,'missing file',h])
 for im in s.find_all('img'):
  if not (OUT/im['src'].lstrip('/')).exists():errors.append([id,'missing image',im['src']])
 for m in s.select('.math'):math.append({'page':id,'tex':m.get_text()[2:-2],'display':'display' in m.get('class',[])})
 if 'BDMBOX' in d['html'] or 'REFROUTE' in d['html']:errors.append([id,'residual marker'])
stats['equations']=len(math)
(OUT.parent/'math-validation-input.json').write_text(json.dumps(math))
print(json.dumps({'stats':stats,'errors':errors},ensure_ascii=False,indent=2))
(OUT.parent/'content-validation.json').write_text(json.dumps({'stats':stats,'errors':errors},ensure_ascii=False,indent=2))

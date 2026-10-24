#!/usr/bin/env python3
"""Verify the third/fourth lecture reading edition against its fixed baseline."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from urllib.parse import parse_qs, unquote, urlsplit

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'content-source/readability-20261024-03-04'
CONTENT=ROOT/'dist/content'
REVIEW=ROOT/'review/readability-20261024-03-04'
BASELINE='aca345c'
CHAPTERS=['03_sql_kpi','04_data_quality']
spec=importlib.util.spec_from_file_location('reading_audit',ROOT/'scripts/verify-readable-lectures.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
read,parse=audit.read,audit.parse

def old_bytes(path):
 return subprocess.run(['git','show',f'{BASELINE}:{path}'],cwd=ROOT,capture_output=True,check=True).stdout

def old(name):return json.loads(old_bytes('dist/content/'+name))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
 errors=[];warnings=[];chapters={}
 config=read(SOURCE/'config.json')
 if config['baseline']!=BASELINE or config['chapters']!=CHAPTERS:errors.append('Unexpected author scope/baseline')
 soups={}
 for path in CONTENT.glob('*.json'):
  value=read(path)
  if isinstance(value,dict) and value.get('html'):soups[path.stem]=parse(value['html'])
 ids={key:Counter(n['id'] for n in s.find_all(id=True)) for key,s in soups.items()}
 for chapter in CHAPTERS:
  document=read(CONTENT/(chapter+'.json'));author=read(SOURCE/'chapters'/(chapter+'.json'))
  soup=soups[chapter];authored=parse(author['html']);original=parse(old(chapter+'.json')['html'])
  if str(soup)!=str(authored):errors.append(chapter+': published HTML differs from author source')
  for field in ('id','title','source','kind'):
   if document[field]!=author[field]:errors.append(chapter+': author metadata mismatch '+field)
  declared_changes=[]
  for edit in config.get('illustrationTextRevisions',[]):
   if edit['chapter']!=chapter:continue
   matches=[node for node in original.select('.math') if node.get_text()==edit['old']]
   if len(matches)!=1 or not any(node.get_text()==edit['new'] for node in soup.select('.math')):
    errors.append(chapter+': declared illustration wording does not match exact baseline/publication')
   else:
    matches[0].string=edit['new'];declared_changes.append(edit)
  protection=audit.check_protection(original,soup)
  for kind,result in protection.items():
   if not result['passed']:errors.append(chapter+': lost original '+kind)
  old_hrefs=Counter(n['href'] for n in original.find_all('a',href=True))
  new_hrefs=Counter(n['href'] for n in soup.find_all('a',href=True))
  if old_hrefs-new_hrefs:errors.append(chapter+': an original link was removed')
  lost=sorted({n['id'] for n in original.find_all(id=True)}-set(ids[chapter]))
  duplicates=[key for key,count in ids[chapter].items() if count>1]
  if lost or duplicates:errors.append(chapter+': lost/duplicated anchors')
  headings=[{'id':n['id'],'title':n.get_text('',strip=True),'level':int(n.name[1])} for n in soup.find_all(['h2','h3'],id=True)]
  if document['toc']!=headings:errors.append(chapter+': TOC differs from actual headings')
  entry=next(x for x in read(CONTENT/'catalog.json')['chapters'] if x['id']==chapter)
  if entry['toc']!=headings:errors.append(chapter+': catalogue TOC differs')
  bad_links=[]
  for link in soup.find_all('a',href=True):
   href=link['href']
   if href.startswith('#/chapter/'):
    parts=urlsplit(href[1:]);target=unquote(parts.path.removeprefix('/chapter/'));q=parse_qs(parts.query)
    anchor=q.get('anchor',[None])[0]
    if target not in ids or (anchor and anchor!='slides' and ids[target][anchor]!=1):bad_links.append(href)
    origin,at=q.get('from',[None])[0],q.get('at',[None])[0]
    if (origin or at) and (origin!=chapter or ids.get(origin,Counter())[at]!=1 or not any(p.get('id')==at for p in link.parents if hasattr(p,'attrs'))):bad_links.append(href+' [return]')
   elif href.startswith('#') and not href.startswith('#/') and ids[chapter][unquote(href[1:])]!=1:bad_links.append(href)
  if bad_links:errors.append(chapter+': invalid internal/return links')
  if soup.select('a a,pre a, .math a'):errors.append(chapter+': links nested inside protected elements')
  refs=soup.select('a[role="doc-noteref"]');notes=soup.select('li[role="doc-endnote"]')
  if [ref.get_text('',strip=True) for ref in refs]!=[str(i) for i in range(1,len(refs)+1)]:errors.append(chapter+': footnote display numbering differs from reading order')
  for ref in refs:
   if ref.get('aria-label')!='阅读注释 '+ref.get_text('',strip=True):errors.append(chapter+': footnote accessibility label differs from display')
   q=parse_qs(urlsplit(ref['href'][1:]).query);anchor=q.get('anchor',[None])[0]
   if ids[chapter][anchor]!=1:errors.append(chapter+': invalid footnote')
  for note in notes:
   if not note.select('a[role="doc-backlink"]'):errors.append(chapter+': footnote has no return')
  metrics,_=audit.readability(chapter,soup,authored)
  if metrics['forbiddenPatterns']:errors.append(chapter+': forbidden prose patterns')
  if metrics['longParagraphCandidates']:warnings.append(chapter+': long paragraphs require reading review')
  chapters[chapter]={'authorSourceMatches':str(soup)==str(authored),'declaredIllustrationTextChanges':declared_changes,'originalMaterial':protection,'originalAnchors':len({n['id'] for n in original.find_all(id=True)}),'lostAnchors':lost,'duplicateAnchors':duplicates,'invalidLinks':bad_links,'footnotes':len(notes),'readability':metrics}
 allowed={*(chapter+'.json' for chapter in CHAPTERS),'catalog.json','source-manifest.json','business-cases.json','case-cards.json','business-casebook.json','lecture-slides.json'}
 names=subprocess.run(['git','ls-tree','-r','--name-only',BASELINE,'dist/content'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.splitlines()
 baseline_names={str(Path(name).relative_to('dist/content')) for name in names}
 current_names={str(path.relative_to(CONTENT)) for path in CONTENT.rglob('*') if path.is_file()}
 if baseline_names!=current_names:errors.append('Published content file membership changed')
 unchanged=[]
 for name in names:
  rel=str(Path(name).relative_to('dist/content'))
  if rel in allowed:continue
  path=CONTENT/rel
  if not path.exists() or path.read_bytes()!=old_bytes(name):errors.append('Out-of-scope content changed: '+rel)
  else:unchanged.append(rel)
 # Catalog entries outside the two chapters remain exactly as released.
 prior_catalog,catalog=old('catalog.json'),read(CONTENT/'catalog.json')
 if set(prior_catalog)!=set(catalog) or [x['id'] for x in prior_catalog['chapters']]!=[x['id'] for x in catalog['chapters']]:errors.append('Catalog fields/chapter membership changed')
 for previous in prior_catalog['chapters']:
  if previous['id'] not in CHAPTERS and previous!=next(x for x in catalog['chapters'] if x['id']==previous['id']):errors.append('Out-of-scope catalog chapter changed: '+previous['id'])
 for field in set(prior_catalog)-{'chapters'}:
  if catalog.get(field)!=prior_catalog[field]:errors.append('Out-of-scope catalog field changed: '+field)
 cases,source_cases,old_cases=read(CONTENT/'business-cases.json'),read(SOURCE/'business-cases.json'),old('business-cases.json')
 allowed_cases={f'b{lesson:02d}-{i:02d}' for lesson in (3,4) for i in range(1,6)}
 if {x['id'] for x in source_cases}!=allowed_cases:errors.append('Exactly ten lesson 3/4 cases are required')
 if [x['id'] for x in old_cases]!=[x['id'] for x in cases]:errors.append('Case membership/order changed')
 old_by={x['id']:x for x in old_cases};by={x['id']:x for x in cases}
 for item in source_cases:
  if by[item['id']]!=item:errors.append('Case author mismatch: '+item['id'])
  for field in ('id','company','facts','sources','slideRefs','chapter','lesson'):
   if item[field]!=old_by[item['id']][field]:errors.append('Case fact/source changed: '+item['id']+':'+field)
  for field in ('title','context','decision','analysis','limits'):
   for label,pattern in audit.HARD_PATTERNS.items():
    if pattern.search(item[field]):errors.append('Case prose pattern: '+item['id']+':'+field+':'+label)
 for key in set(old_by)-allowed_cases:
  if old_by[key]!=by[key]:errors.append('Out-of-scope case changed: '+key)
 cards,source_cards,old_cards=read(CONTENT/'case-cards.json'),read(SOURCE/'case-cards.json'),old('case-cards.json')
 allowed_cards={x['caseId'] for x in old_cards if x['chapterId'] in CHAPTERS}
 if {x['caseId'] for x in source_cards}!=allowed_cards:errors.append('Case-card source scope differs')
 card_by={x['caseId']:x for x in cards};old_card_by={x['caseId']:x for x in old_cards}
 if [x['caseId'] for x in cards]!=[x['caseId'] for x in old_cards]:errors.append('Card membership/order changed')
 for item in source_cards:
  if card_by[item['caseId']]!=item:errors.append('Card author mismatch: '+item['caseId'])
  for field in ('caseId','chapterId','sourceRefs'):
   if item[field]!=old_card_by[item['caseId']][field]:errors.append('Card identity/source changed: '+item['caseId']+':'+field)
  if ids[item['chapterId']][item['targetAnchor']]!=1:errors.append('Invalid card heading: '+item['caseId'])
 for key in set(old_card_by)-allowed_cards:
  if card_by[key]!=old_card_by[key]:errors.append('Out-of-scope card changed: '+key)
 decks,old_decks=read(CONTENT/'lecture-slides.json'),old('lecture-slides.json')
 if list(decks)!=list(old_decks):errors.append('Slide deck membership/order changed')
 for key,prior in old_decks.items():
  new=decks[key]
  if key not in CHAPTERS:
   if new!=prior:errors.append('Out-of-scope slides changed: '+key)
  else:
   a,b=copy.deepcopy(prior),copy.deepcopy(new)
   for deck in (a,b):
    for slide in deck['slides']:
     slide['detailRef'].pop('section',None);slide['detailRef'].pop('subsection',None)
   if a!=b:errors.append('Slide prose changed beyond reading labels: '+key)
   headings={n['id']:n['title'] for n in read(CONTENT/(key+'.json'))['toc']}
   for slide in new['slides']:
    ref=slide['detailRef']
    if ref['anchor'] not in headings or ref['section']!=headings[ref['anchor']]:errors.append('Slide detail target/label invalid: '+key)
 book_data,old_book_data=read(CONTENT/'business-casebook.json'),old('business-casebook.json')
 book,old_book=parse(book_data['html']),parse(old_book_data['html'])
 for key in set(old_by)-allowed_cases:
  if str(book.find(id=key))!=str(old_book.find(id=key)):errors.append('Out-of-scope casebook section changed: '+key)
 if set(book_data)!=set(old_book_data):errors.append('Casebook metadata membership changed')
 for field in set(old_book_data)-{'html','toc'}:
  if book_data.get(field)!=old_book_data[field]:errors.append('Casebook metadata changed: '+field)
 if [x['id'] for x in book_data['toc']]!=[x['id'] for x in old_book_data['toc']]:errors.append('Casebook TOC membership/order changed')
 original_toc={x['id']:x for x in old_book_data['toc']}
 for entry in book_data['toc']:
  if entry['id'] not in allowed_cases and entry!=original_toc[entry['id']]:errors.append('Out-of-scope casebook TOC changed: '+entry['id'])
 for tree in (book,old_book):
  for key in allowed_cases:
   node=tree.find(id=key)
   if node is None:errors.append('Casebook article missing: '+key)
   else:node.decompose()
 if str(book)!=str(old_book):errors.append('Casebook HTML outside the ten approved articles changed')
 manifest=read(CONTENT/'source-manifest.json')
 prior_manifest=old('source-manifest.json')
 if {k:v for k,v in manifest.items() if k!='readabilityContinuation'}!=prior_manifest:errors.append('Prior source-manifest entries changed')
 paths=[SOURCE/'config.json',*(SOURCE/'chapters'/(c+'.json') for c in CHAPTERS),SOURCE/'business-cases.json',SOURCE/'case-cards.json',ROOT/config['conceptSource']]
 expected={str(p.relative_to(ROOT)):sha(p) for p in paths}
 record=manifest.get('readabilityContinuation',{})
 if {x['path']:x['sha256'] for x in record.get('sources',[])}!=expected or record.get('baseline')!=BASELINE or record.get('chapters')!=CHAPTERS:errors.append('Reading source manifest mismatch')
 # Repeat the actual builder against a copied publication tree.
 with tempfile.TemporaryDirectory(prefix='bdm-readable34-qa-') as tmp:
  tmp=Path(tmp);shutil.copytree(CONTENT,tmp/'content');before={p.name:sha(p) for p in (tmp/'content').glob('*.json')}
  subprocess.run([sys.executable,str(ROOT/'scripts/build-readable-lectures.py'),'--source-dir',str(SOURCE),'--content-dir',str(tmp/'content'),'--review-dir',str(tmp/'review')],cwd=ROOT,check=True,capture_output=True)
  idempotent=before=={p.name:sha(p) for p in (tmp/'content').glob('*.json')}
 if not idempotent:errors.append('Reading edition rebuild changes publication bytes')
 spec=importlib.util.spec_from_file_location('checks34',ROOT/'scripts/readability_34_checks.py');checks=importlib.util.module_from_spec(spec);spec.loader.exec_module(checks)
 technical=checks.run_checks()
 if not technical['passed']:errors.append('Independent SQL/arithmetic checks failed')
 result={'passed':not errors,'baseline':BASELINE,'chapters':chapters,'scope':{'otherContentFilesUnchanged':len(unchanged),'businessCases':len(allowed_cases),'otherBusinessCasesUnchanged':len(old_by)-len(allowed_cases),'caseCards':len(allowed_cards),'otherSlideDecksUnchanged':len(decks)-2},'sourceHashes':expected,'idempotent':idempotent,'independentChecks':technical,'warnings':warnings,'errors':errors}
 REVIEW.mkdir(parents=True,exist_ok=True);(REVIEW/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'passed':result['passed'],'chapters':list(chapters),'scope':result['scope'],'independentChecks':technical['passed'],'idempotent':idempotent,'warnings':warnings,'errors':errors},ensure_ascii=False,indent=2))
 raise SystemExit(0 if result['passed'] else 1)

if __name__=='__main__':main()

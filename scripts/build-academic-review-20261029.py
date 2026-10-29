#!/usr/bin/env python3
"""Apply the reviewed five-lecture edition and validate protected content."""
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'content-source/academic-review-20261029'
REVIEW = ROOT / 'review/academic-review-20261029'
CONTENT = ROOT / 'dist/content'

def read(path):
    return json.loads(path.read_text())

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

class Inventory(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.images = Counter(), Counter(), Counter()
        self.protected, self.active = Counter(), []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'): self.ids[a['id']] += 1
        if tag == 'a' and a.get('href'): self.links[a['href']] += 1
        if tag == 'img' and a.get('src'): self.images[a['src']] += 1
        if tag in ('pre', 'code') or 'math' in a.get('class', '').split():
            self.active.append([tag, []])
    def handle_data(self, data):
        for _, parts in self.active: parts.append(data)
    def handle_endtag(self, tag):
        if self.active and self.active[-1][0] == tag:
            kind, parts = self.active.pop()
            self.protected[(kind, ''.join(parts))] += 1

def check_preserved(old, new, label):
    a,b = Inventory(old),Inventory(new)
    for field in ('ids','links','images','protected'):
        missing = getattr(a,field) - getattr(b,field)
        if missing: raise ValueError(f'{label}: lost {field}: {list(missing.items())[:5]}')

before = read(REVIEW/'baseline-decks.json')
old_docs = read(REVIEW/'baseline-chapters.json')
base_terms = read(REVIEW/'baseline-terms.json')
decks, terms, catalog = (read(CONTENT/name) for name in ('lecture-slides.json','lecture-terms.json','catalog.json'))
documents, sources, report = {}, [], {}
for key, old in before.items():
    doc_file, deck_file = SOURCE/'chapters'/f'{key}.json', SOURCE/'slides'/f'{key}.json'
    doc, deck = read(doc_file), read(deck_file)
    if doc.get('id') != old_docs[key].get('id'): raise ValueError(f'{key}: chapter ID changed')
    check_preserved(old_docs[key]['html'], doc['html'], key)
    if len(deck['slides']) != len(old['slides']): raise ValueError(f'{key}: slide count changed')
    headings = {item['id']:item['title'] for item in doc['toc']}
    for i,(oldslide,slide) in enumerate(zip(old['slides'],deck['slides']),1):
        for field in ('equation','formula','codeBlock','sources','caseId','diagram'):
            if oldslide.get(field) != slide.get(field): raise ValueError(f'{key} page {i}: {field} changed')
        if oldslide['detailRef']['anchor'] != slide['detailRef']['anchor']: raise ValueError(f'{key} page {i}: reading anchor changed')
        ref=slide['detailRef']
        if ref['anchor'] not in headings: raise ValueError(f'{key} page {i}: missing heading')
        ref['section']=headings[ref['anchor']]
        if ref.get('subsection'): ref['subsection']=headings[ref['anchor']]
    renamed={a['title']:b['title'] for a,b in zip(old['slides'],deck['slides'])}
    for original in (t for t in base_terms if t.get('chapter')==key):
        updated=dict(original)
        for field in ('firstSlideTitle','definitionSlideTitle'):
            if updated.get(field) in renamed: updated[field]=renamed[updated[field]]
        index=next(i for i,t in enumerate(terms) if t.get('chapter')==key and t['term']==updated['term'])
        terms[index]=updated
    documents[key],decks[key]=doc,deck
    entry=next(item for item in catalog['chapters'] if item['id']==key)
    entry['toc']=doc['toc']
    for filename in (doc_file,deck_file): sources.append({'path':str(filename.relative_to(ROOT)),'sha256':sha256(filename.read_bytes()).hexdigest()})
    report[key]={'pages':len(deck['slides']),'changedPages':sum(a!=b for a,b in zip(old['slides'],deck['slides'])),'conclusions':sum(bool(s.get('takeaway')) for s in deck['slides'])}

case_file=SOURCE/'business-cases.json'
revised_cases=read(case_file)
original_cases={item['id']:item for item in read(REVIEW/'baseline-cases.json')}
if set(original_cases)!={item['id'] for item in revised_cases}: raise ValueError('Case inventory changed')
for item in revised_cases:
    old=original_cases[item['id']]
    for field in ('lesson','chapter','company','title','facts','sources','slideRefs'):
        if item.get(field)!=old.get(field): raise ValueError(f"{item['id']}: protected {field} changed")
cases=read(CONTENT/'business-cases.json')
replacements={item['id']:item for item in revised_cases}
cases=[replacements.get(item['id'],item) for item in cases]
render_js="""import {businessCaseHtml} from './dist/business-cases.js';let data='';for await(const chunk of process.stdin)data+=chunk;process.stdout.write(JSON.stringify(Object.fromEntries(JSON.parse(data).map(item=>[item.id,businessCaseHtml(item)]))));"""
rendered=json.loads(subprocess.run(['node','--input-type=module','-e',render_js],cwd=ROOT,input=json.dumps(revised_cases),capture_output=True,text=True,check=True).stdout)
casebook=read(CONTENT/'business-casebook.json')
for key,html in rendered.items():
    pattern=r'<section\b(?=[^>]*\bid="'+re.escape(key)+r'")[^>]*>[\s\S]*?</section>'
    casebook['html'],count=re.subn(pattern,lambda _:html,casebook['html'])
    if count!=1: raise ValueError(f'{key}: expected one casebook section, found {count}')
sources.append({'path':str(case_file.relative_to(ROOT)),'sha256':sha256(case_file.read_bytes()).hexdigest()})
for key, doc in documents.items(): save(CONTENT/f'{key}.json', doc)
save(CONTENT/'lecture-slides.json',decks)
save(CONTENT/'lecture-terms.json',terms)
save(CONTENT/'catalog.json',catalog)
save(CONTENT/'business-cases.json',cases)
save(CONTENT/'business-casebook.json',casebook)
manifest=read(CONTENT/'source-manifest.json')
manifest['academicReview20261029']={'date':'2026-10-29','sources':sources,'lectures':report,'build':'scripts/build-academic-review-20261029.py'}
save(CONTENT/'source-manifest.json',manifest)
save(REVIEW/'build.json',manifest['academicReview20261029'])
print(json.dumps(report,ensure_ascii=False,indent=2))

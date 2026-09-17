"""Complete bibliography, global citation links, source links and resource downloads."""
from pathlib import Path
import json,re,subprocess,os,shutil
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'website/dist';BOOK=ROOT/'docs/textbook'
pandoc=os.environ.get('PANDOC','pandoc')
cited=sorted(set(re.findall(r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}', ''.join(p.read_text() for p in list((BOOK/'chapters').glob('*.tex'))+[BOOK/'frontmatter.tex',BOOK/'appendices.tex']))))
cited=sorted(set(k for group in cited for k in group.split(',')))
html=subprocess.run([pandoc,'-f','markdown','-t','html5','--citeproc','--bibliography='+str(BOOK/'references.bib')],input='---\nnocite: "'+', '.join('@'+k for k in cited)+'"\n---\n',text=True,capture_output=True,check=True).stdout
bib=BeautifulSoup(html,'html.parser');numbers={e['id'].removeprefix('ref-'):i+1 for i,e in enumerate(bib.select('.csl-entry'))}
for e in bib.select('.csl-entry'):
    label=bib.new_tag('span',attrs={'class':'ref-number'});label.string='['+str(numbers[e['id'][4:]])+'] ';e.insert(0,label)
    for a in e.find_all('a'):a['target']='_blank';a['rel']='noopener noreferrer'
(OUT/'content/bibliography.json').write_text(json.dumps({'id':'bibliography','title':'参考文献','html':'<p>统一教材参考文献，共 '+str(len(numbers))+' 条。点击正文中的引用编号，可在本页查阅来源。</p>'+str(bib),'toc':[],'source':'docs/textbook/references.bib','kind':'textbook'},ensure_ascii=False))
meta=json.loads((OUT/'content/catalog.json').read_text());documents=[]
for p in sorted((OUT/'content').glob('*.json')):
    d=json.loads(p.read_text())
    if 'html' not in d:continue
    soup=BeautifulSoup(d['html'],'html.parser')
    for cite in soup.select('.citation[data-cites]'):
        keys=cite['data-cites'].split();cite.clear()
        for j,key in enumerate(keys):
            if j:cite.append(', ')
            a=soup.new_tag('a',href='#/chapter/bibliography?anchor=ref-'+key);a.string='['+str(numbers[key])+']';cite.append(a)
    if d['id']!='bibliography':
        for bibliography in soup.select('div.references.csl-bib-body'):bibliography.decompose()
    # Keep chapter references globally stable, including equations and chapter roots.
    tex_path=ROOT/d['source']
    if tex_path.suffix=='.tex':
        for key in re.findall(r'\\label\{([^}]+)\}',tex_path.read_text()):
            if soup.find(id=key):continue
            # Equation labels can be recovered directly from math spans.
            match=next((el for el in soup.select('.math') if '\\label{'+key+'}' in el.get_text()),None)
            marker=soup.new_tag('span',id=key)
            if match:match.insert_before(marker)
            else:soup.insert(0,marker)
    for a in soup.find_all('a',href=True):
        href=a['href']
        if href.startswith(('http:','https:','mailto:','#/','/')):continue
        if href.startswith('#'):
            a['href']='#/chapter/'+d['id']+'?anchor='+href[1:];continue
        # Resolve repository-relative teaching-resource links.
        target=(tex_path.parent/href).resolve()
        if target.exists() and ROOT in target.parents:
            if target.suffix=='.md':
                other=next((x for x in meta['extras'] if x['source']==str(target.relative_to(ROOT))),None)
                if other:a['href']='#/chapter/'+other['id'];continue
            dest=OUT/'downloads/source'/target.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,dest);a['href']='./'+str(dest.relative_to(OUT))
    d['html']=str(soup);p.write_text(json.dumps(d,ensure_ascii=False));documents.append(d)
# Use descriptive captions and unique numbering for code snippets.
for chapter in meta['chapters']:
    snippets=[s for s in meta['snippets'] if s['chapter']==chapter['id']]
    for i,s in enumerate(snippets):s['title']=chapter['title']+' · 代码 '+str(i+1)
meta['slides']=[];(OUT/'downloads/slides').mkdir(parents=True,exist_ok=True)
for p in sorted((ROOT/'slides').glob('*/*.pdf')):
    shutil.copy2(p,OUT/'downloads/slides'/p.name)
    meta['slides'].append({'file':p.name,'title':p.parent.name.replace('_',' ')})
meta['bibliographyCount']=len(numbers)
(OUT/'content/catalog.json').write_text(json.dumps(meta,ensure_ascii=False))
# Topic index anchors point to the nearest section containing the concept.
for item in meta['index']:
    d=next((d for d in documents if d['id']==item['chapter']),None)
    if d:
        soup=BeautifulSoup(d['html'],'html.parser');anchor=None
        for element in soup.find_all(['h2','h3','p']):
            if element.name in ['h2','h3']:anchor=element.get('id')
            if item['term'].split('（')[0] in element.get_text():break
        item['anchor']=anchor
(OUT/'content/catalog.json').write_text(json.dumps(meta,ensure_ascii=False))
print('Bibliography:',len(numbers),'slides:',len(meta['slides']))

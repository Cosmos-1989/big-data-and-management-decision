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
(OUT/'content/bibliography.json').write_text(json.dumps({'id':'bibliography','title':'参考文献','html':'<p>参考文献，共 '+str(len(numbers))+' 条。点击正文中的引用编号，可在本页查阅来源。</p>'+str(bib),'toc':[],'source':'docs/textbook/references.bib','kind':'textbook'},ensure_ascii=False))
meta=json.loads((OUT/'content/catalog.json').read_text());documents=[]
reading_guides={
    '12_mlops': {
        'readings': [('04_data_quality','数据质量与证据可信度','数据检查、缺失机制与结果核查'),('07_prediction','预测模型、泛化与不确定性','训练、验证、评价与模型漂移'),('11_modern_data_platform','现代数据平台与语义层','数据分层、指标口径与语义管理')],
        'labs': [('quality','数据质量诊断'),('prediction','流失预测与分类阈值')],
    },
    '13_ontology_action_scenario': {
        'readings': [('02_enterprise_data_model','企业数据模型与治理机制','业务对象、关系与治理责任'),('09_optimization','资源配置、优化与处方决策','目标、约束与方案比较'),('10_process_mining','流程挖掘与智能体执行','业务流程、行动权限与执行反馈')],
        'labs': [('ontology','业务对象、行动与情景'),('optimization','预算约束下的库存补货')],
    },
}
for p in sorted((OUT/'content').glob('*.json')):
    d=json.loads(p.read_text())
    if 'html' not in d:continue
    soup=BeautifulSoup(d['html'],'html.parser')
    for label in soup.select('.statement-title'):
        parts=label.get_text().split(' · ')
        if len(parts)==2 and parts[0]==parts[1]:label.string=parts[0]
    # Empty source outlines become reading guides to existing course material.
    # Keep the source files intact and never present unfinished prose as a lesson.
    if d['id'] in reading_guides and '待编写' in soup.get_text():
        guide=reading_guides[d['id']]
        readings=''.join(f'<a href="#/chapter/{slug}">{title}<small>{description}</small></a>' for slug,title,description in guide['readings'])
        labs=''.join(f'<a href="#/lab/{slug}">{title} →</a>' for slug,title in guide['labs'])
        soup=BeautifulSoup('<h2 id="readings">专题阅读</h2><div class="reading-links">'+readings+'</div><h2 id="practice">实验练习</h2><div class="reading-links">'+labs+'</div>','html.parser')
        d['toc']=[{'id':'readings','title':'专题阅读','level':2},{'id':'practice','title':'实验练习','level':2}]
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

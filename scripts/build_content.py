"""Build the course website from the authoritative textbook and repository assets.
Requires pandoc, Python markdown, beautifulsoup4; figure rebuild also needs XeLaTeX.
Run from any directory. No changes are made to course source files.
"""
from pathlib import Path
import os, re, json, subprocess, shutil, hashlib, ast, zipfile, argparse
import markdown
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
SITE=ROOT/'website'; OUT=SITE/'dist'; BOOK=ROOT/'docs/textbook'
PANDOC=os.environ.get('PANDOC','pandoc')
for d in ['content','figures','downloads','data']:(OUT/d).mkdir(parents=True,exist_ok=True)
chapters=list(sorted((BOOK/'chapters').glob('*.tex')))
front=(BOOK/'frontmatter.tex').read_text(); front=front[front.index('\\chapter*{前言}'):]
inputs=[('preface',front)]+[(p.stem,p.read_text()) for p in chapters]
appendices=re.split(r'(?=\\chapter\{)',(BOOK/'appendices.tex').read_text())
inputs += [('appendix-'+str(i+1),s) for i,s in enumerate([s for s in appendices if '\\chapter{' in s])]
aux=(BOOK/'bdm_textbook.aux').read_text() if (BOOK/'bdm_textbook.aux').exists() else ''
refs={k:v for k,v in re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}',aux)}
label_routes={k:slug for slug,s in inputs for k in re.findall(r'\\label\{([^}]+)\}',s)}
figures=[]; all_programs=[]; snippets=[]; index=[]
# Preserve math macros used by the source; KaTeX gets the same definitions in the client.
def prep(slug,s):
    def fig(m):
        body=m.group(0); pictures=re.findall(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}',body,re.S)
        if not pictures:return body
        n=len(figures)+1; figures.append(pictures[0])
        cap=re.search(r'\\caption\{',body); caption='教材图示'
        if cap:
            start=cap.end(); level=1; end=start
            while level and end<len(body):
                if body[end]=='{':level+=1
                if body[end]=='}':level-=1
                end+=1
            caption=body[start:end-1]
        labels=''.join(re.findall(r'\\label\{[^}]+\}',body))
        return '\n\\begin{figure}\\includegraphics{FIGURE'+str(n)+'}\\caption{'+caption+'}'+labels+'\\end{figure}\n'
    s=re.sub(r'\\begin\{figure\}.*?\\end\{figure\}',fig,s,flags=re.S)
    s=re.sub(r'\\subjectindex\{([^}]+)\}\{([^}]+)\}',lambda m:index.append({'term':m[2],'sort':m[1],'chapter':slug}) or '',s)
    s=re.sub(r'\\addcontentsline\{[^}]*\}\{[^}]*\}\{[^}]*\}','',s)
    s=re.sub(r'\\rowcolor\{[^}]+\}','',s)
    s=re.sub(r'P\{([\d.]+)\\linewidth\}',r'p{\1\\linewidth}',s)
    s=re.sub(r'\\chapterreading\{',r'\\subsection*{文献导读}\n{',s)
    def ref(m):
        key=m[2]; num=refs.get(key,key)
        dest=label_routes.get(key,slug)
        # custom href becomes a stable route after HTML conversion
        text='('+num+')' if m[1]=='eqref' else num
        return '\\href{REFROUTE'+dest+'REFANCHOR'+key+'}{'+text+'}'
    s=re.sub(r'\\(eqref|ref)\{([^}]+)\}',ref,s)
    # Numbered environments are retained as styled, accessible HTML containers.
    for env,label in {'definition':'定义','theorem':'定理','proposition':'命题','lemma':'引理','corollary':'推论','remark':'说明','example':'例','exercise':'思考与练习','modernbox':'管理解释','proof':'证明'}.items():
        s=re.sub(r'\\begin\{'+env+r'\}(?:\[([^\]]*)\])?',lambda m:'\nBDMBOXSTART'+env+'BDMTITLE'+label+(' · '+m[1] if m[1] else '')+'BDMENDTITLE\n\n',s)
        s=s.replace('\\end{'+env+'}','\n\nBDMBOXEND\n')
    return s
prepared=[(slug,prep(slug,s)) for slug,s in inputs]
# Figures are exported once, with the original fonts, geometry, labels and curves.
if not all((OUT/'figures'/f'figure-{i+1}.svg').exists() for i in range(len(figures))) or '--figures' in os.sys.argv:
    tmp=ROOT/'tmp/website-figures';tmp.mkdir(parents=True,exist_ok=True)
    tex=r'''\documentclass[UTF8,fontset=fandol]{ctexbook}
\input{book_preamble.tex}
\usepackage[active,tightpage]{preview}
\PreviewEnvironment{tikzpicture}
\setlength\PreviewBorder{8pt}
\begin{document}
'''+ '\n'.join(figures)+r'\end{document}'
    (tmp/'figures.tex').write_text(tex)
    r=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error',f'-output-directory={tmp}',str(tmp/'figures.tex')],cwd=BOOK,capture_output=True,text=True)
    if r.returncode:raise RuntimeError(r.stdout[-3500:])
    for i in range(len(figures)):
        subprocess.run(['pdftocairo','-svg','-f',str(i+1),'-l',str(i+1),str(tmp/'figures.pdf'),str(OUT/'figures'/f'figure-{i+1}.svg')],check=True)
# Convert each chapter separately to keep payloads small; use one bibliography corpus.
for slug,s in prepared:
    temp=ROOT/'tmp/website-content';temp.mkdir(parents=True,exist_ok=True)
    src=temp/(slug+'.tex');src.write_text(s)
    proc=subprocess.run([PANDOC,str(src),'-f','latex','-t','html5','--mathjax','--wrap=none','--citeproc','--bibliography='+str(BOOK/'references.bib')],capture_output=True,text=True)
    if proc.returncode:raise RuntimeError(proc.stderr)
    h=proc.stdout
    h=re.sub(r'REFROUTE([^" ]+?)REFANCHOR([^" ]+)',r'#/chapter/\1?anchor=\2',h)
    h=re.sub(r'FIGURE(\d+)',r'/figures/figure-\1.svg',h)
    h=re.sub(r'<p>BDMBOXSTART(\w+)BDMTITLE(.*?)BDMENDTITLE</p>',r'<aside class="statement \1"><div class="statement-title">\2</div>',h)
    h=h.replace('<p>BDMBOXEND</p>','</aside>')
    soup=BeautifulSoup(h,'html.parser')
    # Heading levels are h1 chapter / h2 section / h3 subsection.
    title=soup.find('h1'); title_text=title.get_text(' ',strip=True) if title else slug
    if title:title.decompose()
    for img in soup.find_all('img'):img['loading']='lazy';img['alt']=img.get('alt') or '教材原图'
    for i,heading in enumerate(soup.find_all(['h2','h3','h4'])):
        if not heading.get('id'):heading['id']=slug+'-s'+str(i)
    for tag in soup.find_all('a',class_='citation'):
        pass
    for pre in soup.find_all('pre'):
        code=pre.get_text();classes=pre.get('class',[])
        # Pandoc's lstlisting attribute may sit on the inner code node.
        lang='sql' if ('SELECT' in code or 'CREATE ' in code) else 'python' if ('import ' in code or 'class ' in code) else 'text'
        sid=slug+'-code-'+str(len(snippets)+1)
        snippets.append({'id':sid,'chapter':slug,'title':title_text+' · 程序片段 '+str(len(soup.find_all('pre',limit=0))),'language':lang,'code':code})
        pre['data-snippet']=sid;pre['data-language']=lang
    for a in soup.find_all('a',href=True):
        href=a['href']
        if href.startswith('#') and not href.startswith('#/'):
            a['href']='#/chapter/'+slug+'?anchor='+href[1:]
        elif href.startswith('http'):a['target']='_blank';a['rel']='noopener noreferrer'
    # Wrap wide tables; preserve captions, rows and cells.
    for table in soup.find_all('table'):
        table.wrap(soup.new_tag('div',attrs={'class':'table-scroll'}))
    toc=[{'id':x['id'],'title':x.get_text(' ',strip=True),'level':int(x.name[1])} for x in soup.find_all(['h2','h3'])]
    doc={'id':slug,'title':title_text,'html':str(soup),'toc':toc,'source':'docs/textbook/'+('chapters/'+slug+'.tex' if slug[0].isdigit() else 'frontmatter.tex' if slug=='preface' else 'appendices.tex'),'kind':'textbook'}
    (OUT/'content'/(slug+'.json')).write_text(json.dumps(doc,ensure_ascii=False))
# Supplementary teaching units, assignments and report templates retain their provenance.
extra=list(sorted((ROOT/'docs/lecture_notes').glob('1[1-4]_*.md')))+[ROOT/'docs/syllabus.md']+list(sorted((ROOT/'assignments').glob('*.md')))+list(sorted((ROOT/'reports').glob('*.md')))+list(sorted((ROOT/'docs/cases').glob('*.md')))+[ROOT/'data/sample/README.md']
extra_meta=[]
for p in extra:
    slug=('data-guide' if p.name=='README.md' else p.stem);s=p.read_text()
    soup=BeautifulSoup(markdown.markdown(s,extensions=['tables','fenced_code','toc']),'html.parser')
    title=soup.find('h1');t=title.get_text() if title else slug
    if title:title.decompose()
    for i,x in enumerate(soup.find_all(['h2','h3'])):x['id']=slug+'-s'+str(i)
    for tab in soup.find_all('table'):tab.wrap(soup.new_tag('div',attrs={'class':'table-scroll'}))
    doc={'id':slug,'title':t,'html':str(soup),'toc':[{'id':x['id'],'title':x.get_text(),'level':int(x.name[1])} for x in soup.find_all(['h2','h3'])],'source':str(p.relative_to(ROOT)),'kind':'supplement'}
    (OUT/'content'/(slug+'.json')).write_text(json.dumps(doc,ensure_ascii=False));extra_meta.append({k:doc[k] for k in ['id','title','source','kind']})
files={str(p.relative_to(ROOT)):p.read_text() for p in (ROOT/'src/bdm_decision').rglob('*') if p.suffix in ['.py','.sql','.yml']}
files.update({str(p.relative_to(ROOT)):p.read_text() for p in (ROOT/'data/sample').glob('*.csv')})
(OUT/'data/files.json').write_text(json.dumps(files,ensure_ascii=False))
for path,code in files.items():
    if not path.startswith('src/') or path.endswith('__init__.py'):continue
    active=bool(re.search(r'^(def |class |SELECT|CREATE)',code,re.M))
    all_programs.append({'id':Path(path).stem,'path':path,'language':'python' if path.endswith('.py') else 'sql' if path.endswith('.sql') else 'yaml','code':code,'status':'implemented' if active else 'template'})
for p in (ROOT/'data/sample').glob('*.csv'):shutil.copy2(p,OUT/'data'/p.name)
shutil.copy2(BOOK/'bdm_textbook.pdf',OUT/'downloads/bdm_textbook.pdf')
shutil.copy2(ROOT/'LICENSE',OUT/'downloads/LICENSE.txt')
with zipfile.ZipFile(OUT/'downloads/course-code-data.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p,s in files.items():z.writestr(p,s)
    z.write(ROOT/'pyproject.toml','pyproject.toml');z.write(ROOT/'LICENSE','LICENSE')
    z.writestr('README.txt','课程代码与教学数据，源自大数据与管理决策基础课程仓库。安装：pip install -e .\n运行：PYTHONPATH=src python -m bdm_decision.cases.week03_sql_kpi\n部分文件为课程建设中的模板，详见网站程序目录。\n')
meta={'edition':'2026年9月学术复校版','author':'孙振宇','institution':'东北大学数学与统计学院','chapters':[{'id':slug,'title':BeautifulSoup((OUT/'content'/(slug+'.json')).read_text(),'html.parser').get_text()} for slug,_ in []], 'extras':extra_meta,'programs':all_programs,'snippets':snippets,'index':index,'figures':len(figures),'sourceHash':hashlib.sha256(''.join(s for _,s in inputs).encode()).hexdigest()}
meta['chapters']=[{k:d[k] for k in ['id','title','source','kind']} for slug,_ in prepared for d in [json.loads((OUT/'content'/(slug+'.json')).read_text())]]
meta['datasets']=[{'name':p.name,'rows':len(p.read_text().splitlines())-1,'bytes':p.stat().st_size} for p in sorted((ROOT/'data/sample').glob('*.csv'))]
(OUT/'content/catalog.json').write_text(json.dumps(meta,ensure_ascii=False))
(OUT/'content/source-manifest.json').write_text(json.dumps({'edition':meta['edition'],'sources':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in chapters+[BOOK/'frontmatter.tex',BOOK/'appendices.tex',BOOK/'references.bib']],'counts':{'chapters':10,'appendices':3,'figures':len(figures),'programs':len(all_programs),'datasets':len(meta['datasets'])}},ensure_ascii=False,indent=2))
print(json.dumps({'chapters':len(prepared),'extras':len(extra),'figures':len(figures),'programs':len(all_programs),'snippets':len(snippets)},ensure_ascii=False))

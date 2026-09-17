import katex from './vendor/katex/katex.mjs';
import renderMathInElement from './vendor/katex/contrib/auto-render.mjs';
import {mountLab,cleanupLab,esc,tableHtml} from './lab.js';
import {experiments} from './experiments.js';
const main=document.querySelector('main'),sidebar=document.querySelector('.sidebar'),toc=document.querySelector('.toc');
const home=main.innerHTML;let catalog,currentRoute='',renderVersion=0;
const macros={'\\E':'\\mathbb E','\\Prob':'\\mathbb P','\\R':'\\mathbb R','\\N':'\\mathbb N','\\eps':'\\varepsilon','\\dd':'\\,\\mathrm d','\\argmin':'\\operatorname*{arg\\,min}','\\argmax':'\\operatorname*{arg\\,max}','\\abs':'\\left\\lvert #1\\right\\rvert','\\norm':'\\left\\lVert #1\\right\\rVert'};
const cached=new Map();
async function doc(id){if(!cached.has(id)){const r=await fetch('/content/'+encodeURIComponent(id)+'.json');if(!r.ok)throw new Error('找不到这份课程资料');cached.set(id,await r.json());}return cached.get(id);}
function chapterLink(c){return `<a href="#/chapter/${c.id}"><span class="chapter-number">${/^\d/.test(c.id)?c.id.slice(0,2):'↗'}</span><span>${esc(c.title)}</span><span class="row-arrow">→</span></a>`;}
function buildNav(){
 const core=catalog.chapters.filter(c=>/^\d/.test(c.id));
 sidebar.innerHTML=`<div class="side-title">课程目录</div><a href="#/">课程介绍与阅读指南</a><a href="#/chapter/preface">前言、全书结构与记号</a>${core.map((c,i)=>(i===0?'<p class="side-label">第一部分 · 决策与数据基础</p>':i===4?'<p class="side-label">第二部分 · 统计分析与效果评价</p>':i===8?'<p class="side-label">第三部分 · 优化与执行</p>':'')+`<a href="#/chapter/${c.id}"><span class="nav-num">${c.id.slice(0,2)}</span>${esc(c.title)}</a>`).join('')}<p class="side-label">扩展单元与综合项目</p>${catalog.extras.filter(c=>/^1[1-4]_/.test(c.id)).map(c=>`<a href="#/chapter/${c.id}">${esc(c.title.replace('第 ','').replace(' 章',''))}</a>`).join('')}<a href="#/chapter/final_project">15–16　综合项目与答辩</a><p class="side-label">附录与检索</p>${catalog.chapters.filter(c=>c.id.startsWith('appendix')).map((c,i)=>`<a href="#/chapter/${c.id}">${String.fromCharCode(65+i)}　${esc(c.title)}</a>`).join('')}<a href="#/index">主题索引</a><a href="#/chapter/bibliography">参考文献</a><a href="#/resources">数据、作业与课程资源</a><div class="side-bottom">孙振宇<br>东北大学 · 数学与统计学院<br><span>2026 年 9 月学术复校版</span></div>`;
}
function setToc(items=[]){toc.innerHTML=`<div>本页内容</div>${items.map(i=>`<a href="${esc(i.href)}" class="${i.level===3?'subtoc':''}">${esc(i.title)}</a>`).join('')}<div class="toc-download"><a href="/downloads/bdm_textbook.pdf" target="_blank">↓ 完整教材 PDF</a></div>`;}
function footer(){return `<footer class="page-footer"><span>《大数据与管理决策基础》 · 孙振宇</span><a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener noreferrer">CC BY 4.0</a></footer>`;}
function title(s){document.title=s+' · 大数据与管理决策基础';}
function jump(anchor){if(anchor){requestAnimationFrame(()=>{const el=document.getElementById(anchor);if(el)el.scrollIntoView({behavior:'instant',block:'start'});else main.scrollIntoView();});}else window.scrollTo(0,0);}
function homePage(){
 title('课程阅读指南');main.innerHTML=home;
 const hs=main.querySelectorAll('h2');['path','practice','chapters'].forEach((id,i)=>hs[i].id=id);
 main.insertAdjacentHTML('beforeend',`<div class="chapter-list">${catalog.chapters.filter(c=>/^\d/.test(c.id)).map(chapterLink).join('')}</div><h2 id="reading">如何使用本课程</h2><ol class="reading-steps"><li><strong>阅读问题、定义与算例。</strong>先界定业务对象、时间窗口、指标口径和可行行动，再选择方法。</li><li><strong>在实验室验证。</strong>修改参数或源代码，运行课程 Python 与 SQL，观察表格和图形如何变化。</li><li><strong>解释结果与边界。</strong>结合章末习题、作业和报告模板，说明统计证据、管理含义及假设条件。</li></ol><div class="notice"><b>内容范围</b><p>正式教材为 10 章、3 项附录；第 11–14 单元为扩展讲义，第 15–16 单元为综合项目。部分原有课件与模板尚未按新版教材同步修订，资源页已标明。</p></div><div class="home-links"><a href="#/chapter/syllabus">课程大纲 →</a><a href="#/resources">作业与数据 →</a><a href="/downloads/bdm_textbook.pdf" target="_blank">下载教材 PDF ↓</a></div>${footer()}`);
 setToc([{title:'课程主线',href:'#/?anchor=path'},{title:'阅读与实践',href:'#/?anchor=practice'},{title:'课程内容',href:'#/?anchor=chapters'},{title:'使用指南',href:'#/?anchor=reading'}]);
}
function typeset(){
 const options={throwOnError:false,strict:false,macros,trust:false};
 main.querySelectorAll('.math').forEach(el=>{const src=el.textContent.replace(/^\\[\[(]/,'').replace(/\\[\])]$/,'').replace(/\\label\{[^}]+\}/g,'');katex.render(src,el,{...options,displayMode:el.classList.contains('display')});});
 renderMathInElement(main,{...options,delimiters:[{left:'$$',right:'$$',display:true},{left:'\\[',right:'\\]',display:true},{left:'\\(',right:'\\)',display:false},{left:'$',right:'$',display:false}]});
}
async function chapterPage(id,version){
 const d=await doc(id);if(version!==renderVersion)return;
 title(d.title);const core=catalog.chapters.filter(c=>/^\d/.test(c.id));const idx=core.findIndex(c=>c.id===id);const labs=experiments.filter(e=>e.chapter===id);
 main.innerHTML=`<div class="breadcrumb"><a href="#/">课程讲义</a> / ${d.kind==='textbook'?'新版教材':'课程资料'}</div><div class="chapter-kicker">${/^\d/.test(id)?`第 ${Number(id.slice(0,2))} ${d.kind==='textbook'?'章':'单元'}`:'课程阅读'}</div><h1>${esc(d.title)}</h1><div class="article-actions"><span>${d.kind==='textbook'?catalog.edition:'配套教学资料'}</span>${labs.length?`<a href="#/lab/${labs[0].id}">▶ 运行本章实验</a>`:''}<button class="text-button print-page">打印本页</button></div>${d.kind==='supplement'?'<div class="notice compact">这是原课程的扩展或配套资料，修订进度独立于正式教材；术语与证据边界请以最新教材为准。</div>':''}<article class="prose">${d.html}</article>${labs.length?`<section class="chapter-labs"><h2>本章交互实验</h2>${labs.map(e=>`<a href="#/lab/${e.id}"><span>▶</span><div><strong>${esc(e.title)}</strong><p>${esc(e.description)}</p></div><span>→</span></a>`).join('')}</section>`:''}<div class="chapter-pagination">${idx>0?`<a href="#/chapter/${core[idx-1].id}"><small>上一章</small>${esc(core[idx-1].title)}</a>`:'<span></span>'}${idx>=0&&idx<core.length-1?`<a href="#/chapter/${core[idx+1].id}"><small>下一章 →</small>${esc(core[idx+1].title)}</a>`:''}</div><details class="source-note"><summary>内容来源</summary><code>${esc(d.source)}</code><p>网页保留正文、公式、图表与练习。完整排版与页码请查阅教材 PDF。</p></details>${footer()}`;
 typeset();main.querySelector('.print-page').onclick=()=>window.print();
 for(const pre of main.querySelectorAll('pre')){
  const tools=document.createElement('div');tools.className='code-tools';const copy=document.createElement('button');copy.className='text-button';copy.textContent='复制代码';copy.onclick=async()=>{try{await navigator.clipboard.writeText(pre.textContent);copy.textContent='已复制';setTimeout(()=>copy.textContent='复制代码',1500);}catch{copy.textContent='请选中代码复制';}};tools.append(copy);
  if(['python','sql'].includes(pre.dataset.language)){const link=document.createElement('a');link.href='#/lab/'+pre.dataset.snippet;link.textContent='在实验室运行 ↗';tools.append(link);}pre.before(tools);
 }
 setToc((d.toc||[]).filter(x=>x.level===2).map(s=>({title:s.title,href:`#/chapter/${id}?anchor=${encodeURIComponent(s.id)}`})));
}
function resourcesPage(){
 title('课程资源');
 const assignments=catalog.extras.filter(x=>x.source.startsWith('assignments/')),reports=catalog.extras.filter(x=>x.source.startsWith('reports/')),cases=catalog.extras.filter(x=>x.source.startsWith('docs/cases/'));
 main.innerHTML=`<div class="breadcrumb">课程资料 / 资源中心</div><p class="eyebrow">COURSE RESOURCES</p><h1>课程资源</h1><p class="lead">阅读、复现与完成项目所需的资料。</p><div class="download-row"><a class="primary" href="/downloads/bdm_textbook.pdf" target="_blank">↓ 正式教材 PDF</a><a class="secondary" href="/downloads/course-code-data.zip" download>↓ 全部课程代码与数据</a><a class="secondary" href="#/chapter/syllabus">课程大纲</a></div><h2 id="datasets">教学数据</h2><p>以下均为课程样例。点击数据集可预览，或下载 CSV 在本地复现。</p><div class="dataset-list">${catalog.datasets.map(d=>`<div><button class="dataset-preview" data-name="${d.name}">${esc(d.name)}</button><span>${d.rows} 行</span><a href="/data/${d.name}" download>下载 ↓</a></div>`).join('')}</div><div id="data-preview"></div><h2 id="assignments">作业与综合项目</h2><div class="resource-list">${assignments.map(chapterLink).join('')}</div><h2 id="reports">报告模板</h2><div class="resource-list">${reports.map(chapterLink).join('')}</div><h2 id="cases">行业案例</h2><div class="resource-list">${cases.map(chapterLink).join('')}</div><h2 id="programs">程序清单与实现范围</h2><p>所有课程程序均可查看源代码。已实现模块可在实验室运行；原仓库中仅有注释的模板标记为“待实现”。教材中的进阶方法论不自动等同于已实现算法。</p><div class="program-list">${catalog.programs.map(p=>`<a href="#/lab/source-${p.id}"><code>${esc(p.path.replace('src/bdm_decision/',''))}</code><span class="tag ${p.status==='implemented'?'':'muted'}">${p.language==='yaml'?'指标配置':p.status==='implemented'?'可运行':'待实现模板'}</span></a>`).join('')}</div><h2 id="slides">原有课堂课件</h2><p>以下课件保留原版内容，尚未按 2026 年 9 月统一教材完整更新。</p><div class="resource-list">${(catalog.slides||[]).map(s=>`<a target="_blank" href="/downloads/slides/${s.file}">${esc(s.title)} <span>PDF ↓</span></a>`).join('')}</div>${footer()}`;
 setToc(['datasets','assignments','reports','cases','programs','slides'].map((id,i)=>({title:['教学数据','作业与项目','报告模板','行业案例','程序清单','原有课件'][i],href:'#/resources?anchor='+id})));
 main.querySelectorAll('.dataset-preview').forEach(b=>b.onclick=async()=>{
  const text=await(await fetch('/data/'+b.dataset.name)).text();
  // These repository sample CSVs are simple CSV; support quoted fields and escaped quotes.
  const rows=parseCsv(text),heads=rows.shift();const data=rows.filter(r=>r.some(Boolean)).slice(0,30).map(r=>Object.fromEntries(heads.map((h,i)=>[h,r[i]])));
  const panel=document.querySelector('#data-preview');panel.innerHTML=`<h3>${esc(b.dataset.name)} <button class="text-button" id="close-preview">关闭预览</button></h3><p class="empty-note">前 ${data.length} 行</p>${tableHtml(data)}`;document.querySelector('#close-preview').onclick=()=>panel.innerHTML='';panel.scrollIntoView({block:'start',behavior:'smooth'});
 });
}
function parseCsv(text){const rows=[];let row=[],v='',quote=false;for(let i=0;i<text.length;i++){let c=text[i];if(c==='"'){if(quote&&text[i+1]==='"'){v+='"';i++;}else quote=!quote;}else if(c===','&&!quote){row.push(v);v='';}else if(c==='\n'&&!quote){row.push(v.replace(/\r$/,''));rows.push(row);row=[];v='';}else v+=c;}if(v||row.length){row.push(v);rows.push(row);}return rows;}
function indexPage(){title('主题索引');main.innerHTML=`<div class="breadcrumb">课程讲义 / 主题索引</div><h1>主题索引</h1><p>按拼音与英文字母排列，点击词目返回教材中的对应章节。</p><label class="index-filter">查找概念<input id="index-query" type="search" placeholder="例如：因果、KPI、风险…"></label><div id="index-results" class="index-grid"></div>${footer()}`;const render=()=>{const q=document.querySelector('#index-query').value.toLowerCase();const matches=catalog.index.filter(i=>i.term.toLowerCase().includes(q)||i.sort.toLowerCase().includes(q));document.querySelector('#index-results').innerHTML=matches.length?[...matches].sort((a,b)=>a.sort.localeCompare(b.sort)).map(i=>`<a href="#/chapter/${i.chapter}${i.anchor?'?anchor='+encodeURIComponent(i.anchor):''}">${esc(i.term)}<small>第 ${Number(i.chapter.slice(0,2))} 章 →</small></a>`).join(''):'<p>没有匹配的词目。</p>';};document.querySelector('#index-query').oninput=render;render();setToc([]);}
async function route(){
 const version=++renderVersion;const raw=location.hash.slice(1)||'/';const [path,query='']=raw.split('?');const anchor=new URLSearchParams(query).get('anchor');
 if(path===currentRoute){jump(anchor);return;}cleanupLab();currentRoute=path;sidebar.classList.remove('open');document.querySelector('.menu').setAttribute('aria-expanded','false');
 document.body.classList.toggle('lab-view',path.startsWith('/lab'));sidebar.querySelectorAll('a').forEach(a=>{const selected=a.getAttribute('href')==='#'+path;a.classList.toggle('active',selected);if(selected)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
 try{
 if(path==='/')homePage();else if(path.startsWith('/chapter/'))await chapterPage(decodeURIComponent(path.slice(9)),version);else if(path==='/resources')resourcesPage();else if(path==='/index')indexPage();else if(path.startsWith('/lab')){title('交互实验室');setToc([]);await mountLab(main,catalog,decodeURIComponent(path.split('/')[2]||'kpi'));}else throw new Error('页面不存在');
 if(version===renderVersion)jump(anchor);
 }catch(error){main.innerHTML=`<h1>暂时无法打开</h1><p>${esc(error.message)}</p><a href="#/">返回课程首页</a>`;currentRoute='';}
}
document.querySelector('#skip-link').onclick=e=>{e.preventDefault();main.tabIndex=-1;main.focus();};
document.querySelector('.menu').onclick=()=>{sidebar.classList.toggle('open');document.querySelector('.menu').setAttribute('aria-expanded',sidebar.classList.contains('open'));};
document.addEventListener('keydown',e=>{if(e.key==='Escape')sidebar.classList.remove('open');});
try{const r=await fetch('/content/catalog.json');if(!r.ok)throw new Error('课程目录加载失败，请刷新重试。');catalog=await r.json();buildNav();window.addEventListener('hashchange',route);await route();}catch(e){main.innerHTML=`<h1>课程内容暂时无法加载</h1><p>${esc(e.message)}</p><button onclick="location.reload()">重新加载</button>`;}
// Optional WebMCP navigation uses the same routes and visible state as the interface.
const context=document.modelContext;
if(context?.registerTool){
 const lifecycle=new AbortController();
 try{Promise.resolve(context.registerTool({name:'open_course_experiment',title:'打开课程实验',description:'选择并打开课程实验，不执行代码。',inputSchema:{type:'object',properties:{experimentId:{type:'string',enum:experiments.map(e=>e.id)}},required:['experimentId'],additionalProperties:false},annotations:{readOnlyHint:false,untrustedContentHint:false},async execute(input){if(!input||!experiments.some(e=>e.id===input.experimentId))throw new Error('无效的实验编号');location.hash='#/lab/'+input.experimentId;await route();return {experimentId:input.experimentId,title:experiments.find(e=>e.id===input.experimentId).title};}},{signal:lifecycle.signal})).catch(()=>{});}catch{}
 window.addEventListener('pagehide',()=>lifecycle.abort(),{once:true});
}

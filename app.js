import katex from './vendor/katex/katex.mjs';
import renderMathInElement from './vendor/katex/contrib/auto-render.mjs';
import {mountLab,cleanupLab,esc,tableHtml} from './lab.js';
import {experiments} from './experiments.js';
const main=document.querySelector('main'),sidebar=document.querySelector('.sidebar'),toc=document.querySelector('.toc');
const home=main.innerHTML;let catalog,currentRoute='',renderVersion=0;
const macros={'\\E':'\\mathbb E','\\Prob':'\\mathbb P','\\R':'\\mathbb R','\\N':'\\mathbb N','\\eps':'\\varepsilon','\\dd':'\\,\\mathrm d','\\argmin':'\\operatorname*{arg\\,min}','\\argmax':'\\operatorname*{arg\\,max}','\\abs':'\\left\\lvert #1\\right\\rvert','\\norm':'\\left\\lVert #1\\right\\rVert'};
const cached=new Map();
async function doc(id){if(!cached.has(id)){const r=await fetch('./content/'+encodeURIComponent(id)+'.json');if(!r.ok)throw new Error('找不到这份课程资料');cached.set(id,await r.json());}return cached.get(id);}
function chapterLink(c){return `<a href="#/chapter/${c.id}"><span class="chapter-number">${/^\d/.test(c.id)?c.id.slice(0,2):'↗'}</span><span>${esc(c.title)}</span><span class="row-arrow">→</span></a>`;}
function buildNav(){
 const core=catalog.chapters.filter(c=>/^\d/.test(c.id));
 sidebar.innerHTML=`<div class="side-title">课程目录</div><a href="#/">课程首页</a><a href="#/lab">交互实验室</a><a href="#/chapter/preface">前言、全书结构与记号</a>${core.map((c,i)=>(i===0?'<p class="side-label">第一部分 · 决策与数据基础</p>':i===4?'<p class="side-label">第二部分 · 统计分析与效果评价</p>':i===8?'<p class="side-label">第三部分 · 优化与执行</p>':'')+`<a href="#/chapter/${c.id}"><span class="nav-num">${c.id.slice(0,2)}</span>${esc(c.title)}</a>`).join('')}<p class="side-label">专题与综合项目</p>${catalog.extras.filter(c=>/^1[1-4]_/.test(c.id)).map(c=>`<a href="#/chapter/${c.id}">${esc(c.title.replace('第 ','').replace(' 章',''))}</a>`).join('')}<a href="#/chapter/final_project">15–16　综合项目与答辩</a><p class="side-label">附录与检索</p>${catalog.chapters.filter(c=>c.id.startsWith('appendix')).map((c,i)=>`<a href="#/chapter/${c.id}">${String.fromCharCode(65+i)}　${esc(c.title)}</a>`).join('')}<a href="#/index">主题索引</a><a href="#/chapter/bibliography">参考文献</a><a href="#/resources">数据、作业与课程资源</a><div class="side-bottom">数智化企业运营与优化微专业</div>`;
}
function setToc(items=[]){toc.innerHTML=`<div>本页内容</div>${items.map(i=>`<a href="${esc(i.href)}" class="${i.level===3?'subtoc':''}">${esc(i.title)}</a>`).join('')}<div class="toc-download"><a href="./downloads/bdm_textbook.pdf" target="_blank">↓ 完整教材 PDF</a></div>`;}
function footer(){return `<footer class="page-footer"><span>数智化企业运营与优化微专业</span><a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener noreferrer">CC BY 4.0</a></footer>`;}
function title(s){document.title=s+' · 大数据与管理决策基础';}
function jump(anchor){if(anchor){requestAnimationFrame(()=>{const el=document.getElementById(anchor);if(el)el.scrollIntoView({behavior:'instant',block:'start'});else main.scrollIntoView();});}else window.scrollTo(0,0);}
function homePage(){
 title('课程首页');main.innerHTML=home;
 const core=catalog.chapters.filter(c=>/^\d/.test(c.id));
 const groups=[{title:'决策与数据基础',chapters:core.slice(0,4)},{title:'统计分析与效果评价',chapters:core.slice(4,8)},{title:'优化与执行',chapters:core.slice(8)}];
 main.querySelector('#course-groups').innerHTML=groups.map((group,i)=>`<section class="course-group"><div class="group-heading"><span class="group-number">0${i+1}</span><h3>${group.title}</h3></div><div class="chapter-list">${group.chapters.map(chapterLink).join('')}</div></section>`).join('');
 main.insertAdjacentHTML('beforeend',`<section class="study-guide" id="reading"><div class="section-heading"><h2>阅读 · 实验 · 思考</h2></div><ol class="reading-steps"><li><span class="step-number">01</span><div><strong>从问题与定义开始</strong><p>界定业务对象、指标口径与可行行动，读懂假设与推导。</p></div></li><li><span class="step-number">02</span><div><strong>用实验检验理解</strong><p>修改参数或代码，比较不同条件下的计算结果。</p></div></li><li><span class="step-number">03</span><div><strong>把证据用于决策</strong><p>结合习题与案例，解释结果、管理含义与适用边界。</p></div></li></ol><div class="home-links"><a href="#/chapter/syllabus">课程大纲 ↗</a><a href="#/resources">作业与数据 ↗</a><a href="#/index">主题索引 ↗</a></div></section>${footer()}`);
 setToc([]);
}

function typeset(){
 const options={throwOnError:false,strict:false,macros,trust:false};
 main.querySelectorAll('.math').forEach(el=>{const src=el.textContent.replace(/^\\[\[(]/,'').replace(/\\[\])]$/,'').replace(/\\label\{[^}]+\}/g,'');katex.render(src,el,{...options,displayMode:el.classList.contains('display')});});
 renderMathInElement(main,{...options,delimiters:[{left:'$$',right:'$$',display:true},{left:'\\[',right:'\\]',display:true},{left:'\\(',right:'\\)',display:false},{left:'$',right:'$',display:false}]});
}
async function chapterPage(id,version){
 const d=await doc(id);if(version!==renderVersion)return;
 title(d.title);const core=catalog.chapters.filter(c=>/^\d/.test(c.id));const idx=core.findIndex(c=>c.id===id);const labs=experiments.filter(e=>e.chapter===id);
 main.innerHTML=`<div class="breadcrumb"><a href="#/">课程讲义</a> / ${d.kind==='textbook'?'课程章节':'课程资料'}</div><div class="chapter-kicker">${/^\d/.test(id)?`第 ${Number(id.slice(0,2))} ${d.kind==='textbook'?'章':'单元'}`:'课程阅读'}</div><h1>${esc(d.title)}</h1><div class="article-actions">${labs.length?`<a href="#/lab/${labs[0].id}">▶ 运行本章实验</a>`:''}<button class="text-button print-page">打印本页</button></div><article class="prose">${d.html}</article>${labs.length?`<section class="chapter-labs"><h2>本章交互实验</h2>${labs.map(e=>`<a href="#/lab/${e.id}"><span>▶</span><div><strong>${esc(e.title)}</strong><p>${esc(e.description)}</p></div><span>→</span></a>`).join('')}</section>`:''}<div class="chapter-pagination">${idx>0?`<a href="#/chapter/${core[idx-1].id}"><small>上一章</small>${esc(core[idx-1].title)}</a>`:'<span></span>'}${idx>=0&&idx<core.length-1?`<a href="#/chapter/${core[idx+1].id}"><small>下一章 →</small>${esc(core[idx+1].title)}</a>`:''}</div>${footer()}`;
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
 main.innerHTML=`<div class="breadcrumb">课程资料 / 资源中心</div><h1>课程资源</h1><p class="lead">阅读、复现与完成项目所需的资料。</p><div class="download-row"><a class="primary" href="./downloads/bdm_textbook.pdf" target="_blank">↓ 课程教材 PDF</a><a class="secondary" href="./downloads/course-code-data.zip" download>↓ 全部课程代码与数据</a><a class="secondary" href="#/chapter/syllabus">课程大纲</a></div><h2 id="datasets">教学数据</h2><p>以下均为课程样例。点击数据集可预览，或下载 CSV 在本地复现。</p><div class="dataset-list">${catalog.datasets.map(d=>`<div><button class="dataset-preview" data-name="${d.name}">${esc(d.name)}</button><span>${d.rows} 行</span><a href="./data/${d.name}" download>下载 ↓</a></div>`).join('')}</div><div id="data-preview"></div><h2 id="assignments">作业与综合项目</h2><div class="resource-list">${assignments.map(chapterLink).join('')}</div><h2 id="reports">报告模板</h2><div class="resource-list">${reports.map(chapterLink).join('')}</div><h2 id="cases">行业案例</h2><div class="resource-list">${cases.map(chapterLink).join('')}</div><h2 id="programs">课程程序</h2><p>选择程序，在实验室中阅读、修改与运行；练习文件供你补充代码。</p><div class="program-list">${catalog.programs.map(p=>`<a href="#/lab/source-${p.id}"><code>${esc(p.path.replace('src/bdm_decision/',''))}</code><span class="tag ${p.status==='implemented'?'':'muted'}">${p.language==='yaml'?'指标配置':p.status==='implemented'?'可运行':'练习文件'}</span></a>`).join('')}</div><h2 id="slides">课堂课件</h2><div class="resource-list">${(catalog.slides||[]).map(s=>`<a target="_blank" href="./downloads/slides/${s.file}">${esc(s.title)} <span>PDF ↓</span></a>`).join('')}</div>${footer()}`;
 setToc(['datasets','assignments','reports','cases','programs','slides'].map((id,i)=>({title:['教学数据','作业与项目','报告模板','行业案例','程序清单','课堂课件'][i],href:'#/resources?anchor='+id})));
 main.querySelectorAll('.dataset-preview').forEach(b=>b.onclick=async()=>{
  const text=await(await fetch('./data/'+b.dataset.name)).text();
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
 document.body.classList.toggle('home-view',path==='/');document.body.classList.toggle('lab-view',path.startsWith('/lab'));document.querySelectorAll('header nav a').forEach(a=>{const href=a.getAttribute('href');const selected=href==='#/lab'?path.startsWith('/lab'):href==='#/resources'?path==='/resources':!path.startsWith('/lab')&&path!=='/resources';if(selected)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});sidebar.querySelectorAll('a').forEach(a=>{const selected=a.getAttribute('href')==='#'+path||(a.getAttribute('href')==='#/lab'&&path.startsWith('/lab'));a.classList.toggle('active',selected);if(selected)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
 try{
 if(path==='/')homePage();else if(path.startsWith('/chapter/'))await chapterPage(decodeURIComponent(path.slice(9)),version);else if(path==='/resources')resourcesPage();else if(path==='/index')indexPage();else if(path.startsWith('/lab')){title('交互实验室');setToc([]);await mountLab(main,catalog,decodeURIComponent(path.split('/')[2]||'kpi'));}else throw new Error('页面不存在');
 if(version===renderVersion)jump(anchor);
 }catch(error){main.innerHTML=`<h1>暂时无法打开</h1><p>${esc(error.message)}</p><a href="#/">返回课程首页</a>`;currentRoute='';}
}
document.querySelector('#skip-link').onclick=e=>{e.preventDefault();main.tabIndex=-1;main.focus();};
document.querySelector('.menu').onclick=()=>{sidebar.classList.toggle('open');document.querySelector('.menu').setAttribute('aria-expanded',sidebar.classList.contains('open'));};
document.addEventListener('keydown',e=>{if(e.key==='Escape'){sidebar.classList.remove('open');document.querySelector('.menu').setAttribute('aria-expanded','false');}});
try{const r=await fetch('./content/catalog.json');if(!r.ok)throw new Error('课程目录加载失败，请刷新重试。');catalog=await r.json();buildNav();window.addEventListener('hashchange',route);await route();}catch(e){main.innerHTML=`<h1>课程内容暂时无法加载</h1><p>${esc(e.message)}</p><button onclick="location.reload()">重新加载</button>`;}
// Optional WebMCP navigation uses the same routes and visible state as the interface.
const context=document.modelContext;
if(context?.registerTool){
 const lifecycle=new AbortController();
 try{Promise.resolve(context.registerTool({name:'open_course_experiment',title:'打开课程实验',description:'选择并打开课程实验，不执行代码。',inputSchema:{type:'object',properties:{experimentId:{type:'string',enum:experiments.map(e=>e.id)}},required:['experimentId'],additionalProperties:false},annotations:{readOnlyHint:false,untrustedContentHint:false},async execute(input){if(!input||!experiments.some(e=>e.id===input.experimentId))throw new Error('无效的实验编号');location.hash='#/lab/'+input.experimentId;await route();return {experimentId:input.experimentId,title:experiments.find(e=>e.id===input.experimentId).title};}},{signal:lifecycle.signal})).catch(()=>{});}catch{}
 window.addEventListener('pagehide',()=>lifecycle.abort(),{once:true});
}

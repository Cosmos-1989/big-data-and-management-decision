/** Build only the enterprise Agent supplement; preserve the textbook corpus. */
import {readFile,writeFile,mkdir,copyFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {diagramHtml} from '../dist/slide-diagrams.js';
const site=path.resolve(fileURLToPath(new URL('..',import.meta.url))),root=path.dirname(site),input=path.join(site,'content-source/agent-course'),out=path.join(site,'dist');
const read=async p=>JSON.parse(await readFile(p,'utf8'));
const save=async(p,d)=>writeFile(p,JSON.stringify(d,null,2)+'\n');
const sha=s=>createHash('sha256').update(s).digest('hex');
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const plain=s=>s.replace(/<[^>]+>/g,'').replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').trim();
const figures=await read(path.join(input,'figures.json'));
const sectionIds=['agent-route','agent-architecture','agent-rag','agent-chatflow','agent-workflow','agent-multi','agent-deployment','agent-tools','agent-office-cases','agent-routing-case','agent-production-case','agent-evaluation','agent-rollout','agent-nl2sql','agent-project'];
function convert(source,id,isAgent=false){
 const formulas=[];
 source=source.replace(/\\\[([\s\S]*?)\\\]|\\\(([\s\S]*?)\\\)/g,(_,display,inline)=>{const n=formulas.length;formulas.push(`<span class="math ${display===undefined?'inline':'display'}">${display===undefined?'\\(':'\\['}${esc(display??inline)}${display===undefined?'\\)':'\\]'}</span>`);return `BDMAGENTMATH${n}TOKEN`;});
 let html=execFileSync(process.env.PYTHON||'python3',[path.join(site,'scripts/render-markdown.py')],{input:source,encoding:'utf8'}),title='',section=-1,sub=0;const toc=[];
 html=html.replace(/<h1[^>]*>([\s\S]*?)<\/h1>/,(_,t)=>{title=plain(t).replace(/^第\s*14\s*章\s*/,'');return '';});
 html=html.replace(/<h([23])[^>]*>([\s\S]*?)<\/h\1>/g,(_,level,text)=>{if(level==='2'){section++;sub=0;}else sub++;const anchor=isAgent?(level==='2'?sectionIds[section]:`${sectionIds[section]}-${sub}`):`${id}-s${toc.length}`;if(!anchor)throw Error('Unexpected section count');toc.push({id:anchor,title:plain(text),level:Number(level)});return `<h${level} id="${anchor}">${text}</h${level}>`;});
 html=html.replace(/BDMAGENTMATH(\d+)TOKEN/g,(_,n)=>formulas[Number(n)]);
 html=html.replace(/<!--\s*agent-figure:\s*([\w-]+)\s*-->/g,(_,key)=>{if(!figures[key])throw Error('Missing figure '+key);return `<div class="agent-figures">${diagramHtml(figures[key])}</div>`;});
 html=html.replace(/<table>/g,'<div class="table-scroll"><table>').replace(/<\/table>/g,'</table></div>');
 html=html.replace(/<a href="(https?:[^\"]+)"/g,'<a target="_blank" rel="noopener noreferrer" href="$1"');
 // The project source uses a repository-relative link; publish its course route.
 html=html.replaceAll('../docs/lecture_notes/14_ai_agent.md','#/chapter/14_ai_agent');
 if(isAgent&&section+1!==sectionIds.length)throw Error(`Expected 15 sections, got ${section+1}`);
 return JSON.parse(execFileSync(process.env.PYTHON||'python3',[path.join(site,'scripts/render-markdown.py'),'--normalize-document'],{input:JSON.stringify({id,title,html,toc,source:id==='14_ai_agent'?'docs/lecture_notes/14_ai_agent.md':'assignments/final_project.md',kind:'supplement'}),encoding:'utf8'}));
}
const agentSource=await readFile(path.join(input,'14_ai_agent.md'),'utf8');
const projectSource=await readFile(path.join(input,'final_project.md'),'utf8');
const agent=convert(agentSource,'14_ai_agent',true),project=convert(projectSource,'final_project');
await save(path.join(out,'content/14_ai_agent.json'),agent);await save(path.join(out,'content/final_project.json'),project);
const catalog=await read(path.join(out,'content/catalog.json'));
// Publish the new SQL example as a runnable snippet. The lecture explains
// binding; the browser workbench uses explicit, commented sample dates.
let snippetIndex=0;
catalog.snippets=catalog.snippets.filter(s=>s.chapter!=='14_ai_agent');
const sqlGuides=[];
agent.html=agent.html.replace(/<pre><code class="language-(sql|python)">([\s\S]*?)<\/code><\/pre>/g,(_,language,encoded)=>{
 const id=`14_ai_agent-code-${++snippetIndex}`;
 let code=encoded.replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&amp;/g,'&');
 if(language==='sql')code="-- 浏览器示例用样本日期替代绑定参数，查询左闭右开区间。\n"+code.replaceAll(':start_date',"'2026-04-03'").replaceAll(':end_date',"'2026-04-06'");
 catalog.snippets.push({id,chapter:agent.id,title:'企业Agent · AI问数口径审计',language,code});
 sqlGuides.push({id,chapter:agent.id,comment:'-- 日期、日事实粒度、分子分母和只读权限必须先核对。',annotatedCode:code});
 return `<pre data-snippet="${id}" data-language="${language}"><code class="language-${language}">${encoded}</code></pre>`;
});
await save(path.join(out,'content/14_ai_agent.json'),agent);
const slideSource=await read(path.join(input,'slides.json'));
const deck=slideSource[agent.id]||slideSource;
deck.title=agent.title;
deck.id=agent.id;
for(const slide of deck.slides){
 const section=agent.toc.find(t=>t.id===slide.detailRef?.anchor);
 if(!section)throw Error('Slide reference has no lecture section: '+slide.title);
 slide.detailRef={...slide.detailRef,chapter:agent.id,section:section.title};
}
const decks=await read(path.join(out,'content/lecture-slides.json'));
decks[agent.id]=deck;
await save(path.join(out,'content/lecture-slides.json'),decks);
for(const d of [agent,project]){const item=catalog.extras.find(e=>e.id===d.id);if(item)Object.assign(item,{title:d.title,source:d.source,kind:d.kind});}
catalog.extras.find(e=>e.id==='14_ai_agent').hasSlides=true;
const links={
 '10_process_mining':['enterprise-agent-path','从受控执行到企业智能体方案','运行环境管理知识检索、任务状态与可靠性。企业制度、办公协作、客户分流和生产线异常处理，还需明确业务对象、工具契约及试点验收条件；相应分析见企业AI Agent专题。','agent-route'],
 '11_modern_data_platform':['enterprise-agent-data','智能体知识与服务的数据基础','知识片段、向量索引和关系摘要须继承数据的权限、版本及有效期。受控工具采用语义层中已确认的指标定义，原始文档与可检索证据分别治理；具体方法见企业检索增强生成（RAG）与部署设计。','agent-rag'],
 '12_mlops':['enterprise-agent-lifecycle','智能体的版本、评测与运行维护','模型、提示词（Prompt）、任务技能（Skill）、检索配置、业务规则和工具服务均须登记版本。回归测试使用固定任务集，并记录轨迹、权限合规情况、延迟、人工复核时间与恢复行为；沙盒、灰度和回滚分别设置验收条件。','agent-evaluation'],
 '13_ontology_action_scenario':['enterprise-agent-actions','对象状态、行动契约与智能体编排','审批应绑定业务对象及版本，工具前后置条件决定允许的状态转移。模型及各角色提出的中间建议由运行环境核验，最终完成以业务系统状态为准；生产线异常处理中的分析、核查与维护审批具有不同职责。','agent-production-case']
};
for(const [id,[anchor,title,body,target]] of Object.entries(links)){
 const p=path.join(out,`content/${id}.json`),d=await read(p);
 d.html=d.html.replace(new RegExp(`<section class="agent-connection"[\\s\\S]*?<\\/section>`,'g'),'');
 d.toc=d.toc.filter(t=>t.id!==anchor);
 d.html+=`<section class="agent-connection"><h2 id="${anchor}">${title}</h2><p>${body}</p><a href="#/chapter/14_ai_agent?anchor=${target}">进入企业AI Agent专题 →</a></section>`;
 d.toc.push({id:anchor,title,level:2});await save(p,d);
}
const defs=await read(path.join(input,'experiments.json'));
const experiments=defs.map(({spec,...e})=>e);
await writeFile(path.join(out,'agent-experiments.js'),`/** Deterministic teaching simulations; no model or external business calls. */\nexport const agentExperiments=${JSON.stringify(experiments,null,2)};\n`);
const specs=await read(path.join(out,'content/lab-specs.json'));
specs.snippets=specs.snippets.filter(s=>s.chapter!=='14_ai_agent').concat(sqlGuides);
specs.experiments=specs.experiments.filter(e=>!e.id.startsWith('agent-')).concat(defs.map(e=>({...e.spec,id:e.id,title:e.title,chapter:e.chapter,language:'python',annotatedCode:e.spec.annotatedCode||e.code})));
const modulePath='src/bdm_decision/cases/week14_enterprise_agents.py',moduleCode=await readFile(path.join(input,'week14_enterprise_agents.py'),'utf8');
const program={id:'week14_enterprise_agents',path:modulePath,language:'python',code:moduleCode,status:'implemented'};
catalog.programs=catalog.programs.filter(p=>p.path!==modulePath).concat(program);
specs.programs=specs.programs.filter(p=>p.path!==modulePath).concat({path:modulePath,comment:'# 企业Agent教学规则：版本过滤、只读检索、分流、审批和幂等。无外部模型或业务操作。'});
await save(path.join(out,'content/lab-specs.json'),specs);
const files=await read(path.join(out,'data/files.json'));files[modulePath]=moduleCode;await save(path.join(out,'data/files.json'),files);
await save(path.join(out,'content/catalog.json'),catalog);
const coverage=await read(path.join(input,'coverage.json'));
catalog.index=catalog.index.filter(t=>t.chapter!==agent.id);
for(const item of coverage.items)catalog.index.push({term:item.topic,sort:item.topic.toLowerCase(),chapter:agent.id,anchor:item.section_refs[0].anchor});
// Explicit search vocabulary supplements the longer learning-outcome titles.
for(const [term,anchor] of [['Chatflow','agent-chatflow'],['Workflow','agent-workflow'],['RAG','agent-rag'],['Rerank','agent-rag'],['GraphRAG','agent-rag'],['Skills','agent-architecture'],['Harness Engineering','agent-architecture'],['多智能体','agent-multi'],['私有化部署','agent-deployment']])catalog.index.push({term,sort:term.toLowerCase(),chapter:agent.id,anchor});
const rows=coverage.items.map(item=>{
 const section=item.section_refs[0];
 const pages=item.slide_titles_confirmed.map(title=>deck.slides.findIndex(s=>s.title===title)+1).filter(Boolean);
 const reading=`<a href="#/chapter/${agent.id}?anchor=${section.anchor}">${esc(section.title)}</a>`;
 const labs=item.experiment_ids.map(id=>`<a href="#/lab/${id}">${esc(experiments.find(e=>e.id===id)?.title||id)}</a>`).join('、');
 return `<tr><td>${esc(item.topic)}</td><td>${reading}</td><td>${pages.join('、')||'参见相关章节'}</td><td>${labs?labs+'<br>':''}${esc(item.practical_limit)}</td></tr>`;
}).join('');
const learningMap={id:'agent-learning-map',title:'企业Agent专题：主题与实验导航',kind:'supplement',source:agent.source,toc:[{id:'agent-map',title:'主题、讲授与实践',level:2}],html:`<p>企业智能体专题讨论任务定义、知识检索、对话与工作流、运行控制及部署治理。配套资料包括55页授课幻灯片、四个教学实验和可编辑方案包。实验采用虚构资料与固定规则，不调用真实大模型或企业系统；产品与部署部分附官方资料和验收要求。</p><h2 id="agent-map">主题、讲授与实践</h2><p><a href="#/chapter/${agent.id}">阅读完整专题 →</a>　<a href="./downloads/enterprise-agent-kit.zip">下载方案与验收材料 ↓</a></p><div class="table-scroll"><table><thead><tr><th>学习主题</th><th>讲义位置</th><th>幻灯片页</th><th>实验与学习边界</th></tr></thead><tbody>${rows}</tbody></table></div>`};
await save(path.join(out,'content/agent-learning-map.json'),learningMap);
catalog.extras=catalog.extras.filter(e=>e.id!==learningMap.id).concat({id:learningMap.id,title:learningMap.title,kind:learningMap.kind,source:learningMap.source});
await save(path.join(out,'content/catalog.json'),catalog);
await copyFile(path.join(input,'14_ai_agent.md'),path.join(out,'downloads/enterprise-agent-course.md'));
await copyFile(path.join(input,'week14_enterprise_agents.py'),path.join(out,'downloads/enterprise-agent-experiments.py'));
const manifest=await read(path.join(out,'content/source-manifest.json'));
manifest.agentExtension={date:'2026-10-12',sourceFiles:[{path:agent.source,sha256:sha(agentSource)},{path:project.source,sha256:sha(projectSource)},{path:modulePath,sha256:sha(moduleCode)}],build:'scripts/build-agent-extension.mjs',experiments:experiments.map(e=>e.id)};
await save(path.join(out,'content/source-manifest.json'),manifest);
console.log(JSON.stringify({sections:agent.toc.filter(x=>x.level===2).length,figures:Object.keys(figures).length,experiments:experiments.length,programLines:moduleCode.split('\n').length}));

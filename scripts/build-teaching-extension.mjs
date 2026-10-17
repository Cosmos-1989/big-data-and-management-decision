/** Merge reviewed lecture sources, standalone terms and sourced business cases. */
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {businessCaseHtml} from '../dist/business-cases.js';

const site=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const input=path.join(site,'content-source/teaching-20261017');
const content=path.join(site,'dist/content');
const read=async p=>JSON.parse(await readFile(p,'utf8'));
const save=async(p,value)=>writeFile(p,JSON.stringify(value,null,2)+'\n');
const sha=value=>createHash('sha256').update(value).digest('hex');
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const groups=['01-05','06-10','11-16'];
const merged={},cases=[],terms=[],sourceFiles=[];
for(const group of groups){
 for(const name of ['decks.json','cases.json','term-audit.json']){
  const filename=path.join(input,group,name),bytes=await readFile(filename);
  sourceFiles.push({path:path.relative(site,filename),sha256:sha(bytes)});
  const value=JSON.parse(bytes);
  if(name==='decks.json')for(const [id,deck] of Object.entries(value)){
   if(merged[id])throw Error('Duplicate deck: '+id);
   merged[id]=deck;
  }
  else if(name==='cases.json')cases.push(...value);
  else terms.push(...(Array.isArray(value)?value:value.terms||[]));
 }
}
const seen=new Set();
for(const item of cases){
 if(!/^b\d{2}-\d{2}$/.test(item.id)||seen.has(item.id))throw Error('Invalid or duplicate case '+item.id);
 seen.add(item.id);
 if(!Number.isInteger(item.lesson)||item.lesson<1||item.lesson>16)throw Error('Invalid case lesson '+item.id);
 for(const field of ['chapter','company','title','context','decision','analysis','limits'])if(!item[field])throw Error(`${item.id}: missing ${field}`);
 if(item.facts?.length<2||!item.questions?.length||!item.sources?.length)throw Error('Incomplete case '+item.id);
 for(const s of item.sources)if(!/^https:\/\//.test(s.url)||!s.title||!s.publisher||!s.support||!s.accessed)throw Error('Incomplete evidence '+item.id);
}
for(let lesson=1;lesson<=16;lesson++)if(cases.filter(c=>c.lesson===lesson).length<5)throw Error('Fewer than five new cases for lesson '+lesson);

// Keep the Agent-specific exporter reproducible from the same reviewed deck.
await save(path.join(site,'content-source/agent-course/slides.json'),{'14_ai_agent':merged['14_ai_agent']});
execFileSync(process.execPath,[path.join(site,'scripts/build-agent-extension.mjs')],{cwd:site,stdio:'inherit'});
const decks=await read(path.join(content,'lecture-slides.json'));
for(const [id,deck] of Object.entries(merged)){
 if(id==='final_project')continue;
 const doc=await read(path.join(content,id+'.json'));
 decks[id]={...deck,id,chapter:id,title:doc.title,lectureNumber:Number(id.slice(0,2))};
 decks[id].slides.forEach(s=>{s.lessonNumber=decks[id].lectureNumber;});
}
const project=merged.final_project;
if(!project?.slides?.length)throw Error('Missing project lectures');
for(const [lesson,id,title] of [[15,'final_project','第15讲 · 综合项目工作坊'],[16,'final_project_defense','第16讲 · 项目答辩与证据审查']]){
 const slides=project.slides.filter(s=>s.lessonNumber===lesson);
 if(!slides.length)throw Error('Missing project lesson '+lesson);
 decks[id]={...project,id,chapter:'final_project',title,lectureNumber:lesson,slides};
}
if(project.slides.some(s=>![15,16].includes(s.lessonNumber)))throw Error('Project page has no explicit lecture number');
const ordered=Object.fromEntries(Object.entries(decks).sort(([,a],[,b])=>(a.lectureNumber||Number(a.id?.slice(0,2)))-(b.lectureNumber||Number(b.id?.slice(0,2)))));
if(Object.keys(ordered).length!==16)throw Error('Expected sixteen independently readable decks');
for(const item of cases){
 const refs=[];
 for(const [id,deck] of Object.entries(ordered))deck.slides.forEach((slide,i)=>{
  if(slide.caseId!==item.id)return;
  if(deck.lectureNumber!==item.lesson)throw Error('Case placed in another lesson: '+item.id);
  if(!slide.sources?.length)slide.sources=item.sources.map(({title,url})=>({title,url}));
  refs.push({deck:id,page:i+1,sectionId:item.lesson===16?'slides-16':'slides'});
 });
 if(!refs.length)throw Error('Case absent from lecture: '+item.id);
 if(!refs.some(ref=>{const slide=ordered[ref.deck].slides[ref.page-1];return slide.visual||slide.diagram;}))throw Error('Case lacks a mechanism diagram: '+item.id);
 item.slideRefs=refs;
}
cases.sort((a,b)=>a.lesson-b.lesson||a.id.localeCompare(b.id));
await save(path.join(content,'lecture-slides.json'),ordered);
await save(path.join(content,'business-cases.json'),cases);
await save(path.join(content,'lecture-terms.json'),terms);
const lessonTitles={...Object.fromEntries(Object.values(ordered).map(d=>[d.lectureNumber,d.title.replace(/^第\s*\d+\s*[章讲]\s*[·：:]?\s*/, '')]))};
const toc=[],parts=['<p>企业在数据、模型与组织约束之间作出具体选择。以下案例按课程主题编排；公开事实附一手资料，概念联系与讨论用于分析这些选择能够支持的判断。</p>'];
const markdown=['# 真实商业案例：企业的数据、分析与决策\n'];
for(let lesson=1;lesson<=16;lesson++){
 const title=`第${lesson}讲 · ${lessonTitles[lesson]}`,id=`case-lesson-${String(lesson).padStart(2,'0')}`;
 toc.push({id,title,level:2});parts.push(`<h2 id="${id}">${esc(title)}</h2>`);markdown.push(`\n## ${title}\n`);
 for(const item of cases.filter(c=>c.lesson===lesson)){
  parts.push(businessCaseHtml(item));toc.push({id:item.id,title:item.title,level:3});
  markdown.push(`\n### ${item.title}\n\n${item.company}\n\n${item.context}\n\n业务选择：${item.decision}\n\n公开事实：\n${item.facts.map(f=>'- '+f).join('\n')}\n\n概念联系：${item.analysis}\n\n证据范围：${item.limits}\n\n${item.questions.map(q=>q.question+'\n\n'+q.answer).join('\n\n')}\n\n资料：\n${item.sources.map(s=>`- [${s.title}](${s.url})，${s.publisher}，${s.date||'发布日期未标明'}。${s.support}`).join('\n')}\n`);
 }
}
await save(path.join(content,'business-casebook.json'),{id:'business-casebook',title:'真实商业案例：企业的数据、分析与决策',kind:'supplement',source:'website/content-source/teaching-20261017',toc,html:parts.join('\n')});
await writeFile(path.join(site,'dist/downloads/business-casebook.md'),markdown.join('\n'));
const catalog=await read(path.join(content,'catalog.json'));
for(const item of [...catalog.chapters,...catalog.extras])if(Object.values(ordered).some(d=>d.chapter===item.id))item.hasSlides=true;
catalog.extras=catalog.extras.filter(x=>x.id!=='business-casebook').concat({id:'business-casebook',title:'真实商业案例集',kind:'supplement',source:'website/content-source/teaching-20261017'});
catalog.index=catalog.index.filter(x=>!x.teachingCase);
for(const item of cases)catalog.index.push({term:item.company+'：'+item.title,sort:(item.company+' '+item.title).toLowerCase(),chapter:'business-casebook',anchor:item.id,teachingCase:true});
await save(path.join(content,'catalog.json'),catalog);
const manifest=await read(path.join(content,'source-manifest.json'));
manifest.teachingExtension={date:'2026-10-17',lectures:16,cases:cases.length,slides:Object.values(ordered).reduce((n,d)=>n+d.slides.length,0),sourceFiles};
await save(path.join(content,'source-manifest.json'),manifest);
await mkdir(path.join(site,'review/teaching-20261017'),{recursive:true});
await save(path.join(site,'review/teaching-20261017/build.json'),manifest.teachingExtension);
console.log(JSON.stringify(manifest.teachingExtension,null,2));

/** Apply the reviewed second/third lecture edition without rebuilding other decks. */
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=path.join(root,'content-source/slides-readability-20261024');
const content=path.join(root,'dist/content');
const review=path.join(root,'review/slides-readability-20261024');
const read=async file=>JSON.parse(await readFile(file,'utf8'));
const save=async(file,value)=>writeFile(file,JSON.stringify(value,null,2)+'\n');
const hash=value=>createHash('sha256').update(value).digest('hex');
const before=await read(path.join(review,'before.json'));
const decks=await read(path.join(content,'lecture-slides.json'));
const terms=await read(path.join(content,'lecture-terms.json'));
const originalTerms=await read(path.join(source,'term-audit.json'));
const files=[],counts={};
for(const [id,original] of Object.entries(before)){
 const filename=path.join(source,id+'.json'),raw=await readFile(filename);
 const deck=JSON.parse(raw);
 if(deck.slides.length!==original.slides.length)throw Error(id+': slide count must remain unchanged');
 const document=await read(path.join(content,id+'.json'));
 const headings=new Map(document.toc.map(item=>[item.id,item.title]));
 for(const [i,slide] of deck.slides.entries()){
  if(slide.caseId!==original.slides[i].caseId)throw Error(id+': case/page order changed at '+(i+1));
  if(!headings.has(slide.detailRef?.anchor))throw Error(id+': missing reading anchor at '+(i+1));
  slide.detailRef.section=headings.get(slide.detailRef.anchor);
  if(slide.detailRef.subsection)slide.detailRef.subsection=headings.get(slide.detailRef.anchor);
 }
 const renamed=new Map(original.slides.map((slide,i)=>[slide.title,deck.slides[i].title]));
 for(const originalTerm of originalTerms.filter(item=>item.chapter===id)){
  const term=structuredClone(originalTerm);
  for(const key of ['firstSlideTitle','definitionSlideTitle'])if(renamed.has(term[key]))term[key]=renamed.get(term[key]);
  const index=terms.findIndex(item=>item.chapter===id&&item.term===term.term);
  if(index<0)throw Error(id+': missing terminology record '+term.term);
  terms[index]=term;
 }
 decks[id]=deck;
 files.push({path:path.relative(root,filename),sha256:hash(raw)});
 counts[id]={pages:deck.slides.length,conclusionPanels:deck.slides.filter(slide=>slide.takeaway).length};
}
files.push({path:path.relative(root,path.join(source,'term-audit.json')),sha256:hash(await readFile(path.join(source,'term-audit.json')))});
await save(path.join(content,'lecture-slides.json'),decks);
await save(path.join(content,'lecture-terms.json'),terms);
const manifest=await read(path.join(content,'source-manifest.json'));
manifest.slideReadabilityEdition={date:'2026-10-24',build:'scripts/build-readable-slides.mjs',sourceFiles:files,decks:counts};
await save(path.join(content,'source-manifest.json'),manifest);
await mkdir(review,{recursive:true});
await save(path.join(review,'build.json'),manifest.slideReadabilityEdition);
console.log(JSON.stringify(counts,null,2));

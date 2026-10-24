/** Check the fixed-size slide edition and protect material outside its scope. */
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {lectureSlidesHtml} from '../dist/slides.js';

const read=async file=>JSON.parse(await readFile(new URL(file,import.meta.url),'utf8'));
const decks=await read('../dist/content/lecture-slides.json');
const baseline=await read('../content-source/slides-readability-20261024/baseline.json');
const before=await read('../review/slides-readability-20261024/before.json');
const normalize=value=>value&&typeof value==='object'?Array.isArray(value)?value.map(normalize):Object.fromEntries(Object.entries(value).sort(([a],[b])=>a<b?-1:a>b?1:0).map(([k,v])=>[k,normalize(v)])):value;
const numerical=value=>value&&typeof value==='object'?Array.isArray(value)?value.map(numerical):Object.fromEntries(Object.entries(value).filter(([,v])=>typeof v==='number'||typeof v==='object').map(([k,v])=>[k,numerical(v)])):value;
const result={decks:{},unmodifiedDecks:[],errors:[]};
for(const [id,deck] of Object.entries(decks)){
 assert.equal(deck.slides.length,baseline.pages[id],id+': page count changed');
 if(!before[id]){
  // Python's canonical JSON separates delimiters with spaces, hence mirror it.
  const json=JSON.stringify(normalize(deck)).replace(/"(?:[^"\\]|\\.)*"|[:,]/g,match=>match===','?', ':match===':'?': ':match);
  const digest=createHash('sha256').update(json).digest('hex');
  assert.equal(digest,baseline.unmodifiedDeckSha256[id],id+': another deck changed');
  result.unmodifiedDecks.push(id);continue;
 }
 const source=await read('../content-source/slides-readability-20261024/'+id+'.json');
 assert.deepEqual(deck,source,id+': published deck differs from reviewed source');
 let edited=0;
 for(const [i,slide] of deck.slides.entries()){
  const old=before[id].slides[i],label=id+' page '+(i+1);
  for(const field of ['equation','formula','sources','codeBlock']){
   if(field==='codeBlock'){
    const code=x=>typeof x==='string'?x:x?.code;
    assert.equal(code(slide[field]),code(old[field]),label+': code changed');
   }else assert.deepEqual(slide[field],old[field],label+': protected '+field+' changed');
  }
  assert.equal(slide.caseId,old.caseId,label+': case order changed');
  assert.equal(slide.detailRef.anchor,old.detailRef.anchor,label+': reading destination changed');
  assert.deepEqual(numerical(slide.diagram),numerical(old.diagram),label+': diagram values or geometry changed');
  assert.ok(slide.title&&slide.lead&&slide.body?.every(p=>typeof p==='string'&&p.trim()),label+': incomplete text');
  if(JSON.stringify(slide)!==JSON.stringify(old))edited++;
 }
 const html=lectureSlidesHtml(deck),panels=deck.slides.filter(s=>s.takeaway).length;
 assert.equal((html.match(/class="lecture-slide /g)||[]).length,deck.slides.length);
 assert.equal((html.match(/class="slide-takeaway"/g)||[]).length,panels);
 result.decks[id]={pages:deck.slides.length,editedPages:edited,conclusionPanels:panels,diagrams:deck.slides.filter(s=>s.diagram).length,cases:deck.slides.filter(s=>s.caseId).length};
}
// Omission is a deliberate renderer feature, without empty conclusion markup.
const small={title:'测试',slides:[{kind:'concept',title:'定义',lead:'引入',body:['正文。'],layout:'focus'}]};
assert.ok(!lectureSlidesHtml(small).includes('slide-takeaway'));
await writeFile(new URL('../review/slides-readability-20261024/verification.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));

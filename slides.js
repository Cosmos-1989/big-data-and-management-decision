/** A chapter is taught as a sequence of claims, explanations, and worked examples. */
const escapeHtml=value=>String(value??'').replace(/[&<>"']/g,ch=>({
 '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
}[ch]));
const cleanKind=value=>String(value||'concept').replace(/[^a-z0-9-]/gi,'');
const asArray=value=>Array.isArray(value)?value:value?[value]:[];
const paragraphs=value=>asArray(value).flatMap(item=>String(item).split(/\n\s*\n/)).filter(Boolean);
const inline=value=>escapeHtml(value).replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>').replace(/`([^`]+)`/g,'<code>$1</code>');

function formulaHtml(value,className='slide-equation'){
 return asArray(value).map(entry=>{
  const latex=typeof entry==='string'?entry:entry?.latex;
  if(!latex)return '';
  const label=typeof entry==='object'&&entry?.label?'<small>'+escapeHtml(entry.label)+'</small>':'';
  return `<div class="${className}">${label}<div class="math display">${escapeHtml(latex)}</div></div>`;
 }).join('');
}

function visualItems(visual){
 const raw=visual?.items||visual?.steps||visual?.nodes||visual?.columns||[];
 return Array.isArray(raw)?raw:[];
}
function visualHtml(visual){
 if(!visual)return '';
 const kind=cleanKind(visual.kind||'cards');
 if(kind==='table'){
  const headers=visual.headers||visual.columns||[];
  const rows=visual.rows||[];
  return `<div class="slide-visual slide-visual-table"><div class="slide-table-wrap"><table><thead><tr>${headers.map(x=>`<th>${inline(x)}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${(Array.isArray(row)?row:Object.values(row)).map(cell=>`<td>${inline(cell)}</td>`).join('')}</tr>`).join('')}</tbody></table></div></div>`;
 }
 const items=visualItems(visual);
 if(!items.length)return '';
 return `<div class="slide-visual slide-visual-${kind}">${items.map((item,i)=>{
  let entry;
  if(typeof item==='string'&&kind==='metric'&&item.includes('｜')){
   const [value,...label]=item.split('｜');
   entry={value,label:label.join('｜')};
  }else entry=typeof item==='string'?{label:item}:item||{};
  const title=entry.label||entry.title||entry.value||'';
  const detail=entry.detail||entry.description||entry.text||'';
  const value=entry.value&&entry.label?'<span class="visual-value">'+inline(entry.value)+'</span>':'';
  return `<div class="visual-node"><span class="visual-index">${String(i+1).padStart(2,'0')}</span><div><strong>${inline(title)}</strong>${value}${detail?`<p>${inline(detail)}</p>`:''}</div></div>`;
 }).join('')}</div>`;
}

function workedExampleHtml(example){
 if(!example)return '';
 if(typeof example==='string')return `<section class="slide-example"><div class="slide-side-label">课堂例题</div><p>${inline(example)}</p></section>`;
 const steps=asArray(example.steps);
 return `<section class="slide-example"><div class="slide-side-label">${inline(example.title||'逐步推演')}</div>${example.context?`<p class="example-context">${inline(example.context)}</p>`:''}${steps.length?`<ol>${steps.map(step=>{
  const item=typeof step==='string'?{text:step}:step||{};
  return `<li>${item.label?`<strong>${inline(item.label)}</strong>`:''}<span>${inline(item.text||item.detail||item.description||'')}</span>${item.formula?formulaHtml(item.formula,'example-formula'):''}</li>`;
 }).join('')}</ol>`:''}${example.result?`<p class="example-result"><span>得到</span>${inline(example.result)}</p>`:''}</section>`;
}

function slideHtml(slide,index,count,deck){
 const kind=cleanKind(slide.kind);
 const body=paragraphs(slide.body||slide.explanation);
 const points=asArray(slide.points);
 const formula=formulaHtml(slide.equation||slide.formula);
 const example=workedExampleHtml(slide.workedExample);
 const visual=visualHtml(slide.visual);
 const aside=example||visual;
 const dense=body.join('').length>390?' slide-dense':'';
 const styles=`slide-kind-${kind}${aside?' slide-has-aside':''}${dense}`;
 const labels={opener:'课程问题',goals:'学习路径',concept:'概念与机制',case:'企业情境',calculation:'推导与计算',experiment:'动手实验',discussion:'思考与辨析',summary:'本讲结论'};
 return `<article class="lecture-slide ${styles}" aria-hidden="${index?'true':'false'}"><div class="slide-page">
  <div class="slide-topline"><span class="slide-chapter">大数据与管理决策</span><span class="slide-section">${inline(slide.section||labels[kind]||'课程讲授')}</span></div>
  <div class="slide-grid"><div class="slide-copy"><span class="slide-kicker">${inline(slide.kicker||labels[kind]||'课程讲授')}</span>
  <h3>${inline(slide.title||'')}</h3>${slide.lead?`<p class="slide-lead">${inline(slide.lead)}</p>`:''}
  ${body.length?`<div class="slide-body">${body.map(p=>`<p>${inline(p)}</p>`).join('')}</div>`:''}
  ${formula}
  ${points.length?`<div class="slide-checkpoints"><span>接着检验</span><ul>${points.map(p=>`<li>${inline(p)}</li>`).join('')}</ul></div>`:''}
  </div>${aside?`<div class="slide-aside">${example}${visual}</div>`:''}</div>
  ${slide.takeaway?`<div class="slide-takeaway"><span>本页结论</span><strong>${inline(slide.takeaway)}</strong></div>`:''}
  <div class="slide-footer"><span>${slide.sourceSection?`相关主题 · ${inline(slide.sourceSection)}`:inline(deck.title)}</span><span>${String(index+1).padStart(2,'0')} / ${String(count).padStart(2,'0')}</span></div>
 </div></article>`;
}

export function lectureSlidesHtml(deck){
 if(!deck?.slides?.length)return '';
 const slides=deck.slides;
 const firstSection=slides[0]?.section||'课程问题';
 return `<section id="slides" class="lesson-slides" aria-label="${escapeHtml(deck.title)}授课课件" tabindex="0">
  <div class="slides-toolbar"><div><span class="slides-eyebrow">授课课件 / ${slides.length} 页</span><strong>${escapeHtml(deck.title)}</strong></div><button type="button" class="slides-fullscreen" aria-label="全屏显示授课课件">⛶ 全屏授课</button></div>
  <div class="slide-viewport"><div class="slide-track">${slides.map((s,i)=>slideHtml(s,i,slides.length,deck)).join('')}</div></div>
  <div class="slides-controls"><button class="slides-prev" type="button" aria-label="上一页" disabled>←</button><span class="slides-counter" aria-live="polite">1 / ${slides.length}</span><button class="slides-next" type="button" aria-label="下一页">→</button><span class="slides-current-section">${inline(firstSection)}</span><div class="slides-progress" aria-hidden="true"><span></span></div><select class="slides-jump" aria-label="跳转到课件页">${slides.map((s,i)=>`<option value="${i}">${String(i+1).padStart(2,'0')} · ${escapeHtml(s.title||'')}</option>`).join('')}</select></div>
 </section>`;
}

export function initLectureSlides(root){
 if(!root)return;
 const track=root.querySelector('.slide-track');
 const slides=[...root.querySelectorAll('.lecture-slide')];
 const viewport=root.querySelector('.slide-viewport');
 const jump=root.querySelector('.slides-jump');
 const count=slides.length;
 let index=0,start=null;
 const size=()=>{
  if(document.fullscreenElement===root)return;
  viewport.style.height=`${Math.ceil(slides[index].getBoundingClientRect().height)}px`;
 };
 const show=next=>{
  index=Math.min(count-1,Math.max(0,next));
  track.style.transform=`translateX(-${index*100}%)`;
  slides.forEach((slide,i)=>slide.setAttribute('aria-hidden',String(i!==index)));
  root.querySelector('.slides-counter').textContent=`${index+1} / ${count}`;
  root.querySelector('.slides-prev').disabled=index===0;
  root.querySelector('.slides-next').disabled=index===count-1;
  root.querySelector('.slides-progress span').style.width=`${((index+1)/count)*100}%`;
  root.querySelector('.slides-current-section').textContent=slides[index].querySelector('.slide-section')?.textContent||'';
  jump.value=String(index);
  size();
 };
 root.querySelector('.slides-prev').onclick=()=>show(index-1);
 root.querySelector('.slides-next').onclick=()=>show(index+1);
 jump.onchange=()=>show(Number(jump.value));
 root.addEventListener('keydown',event=>{
  if(event.key==='ArrowLeft'){event.preventDefault();show(index-1);}
  if(event.key==='ArrowRight'){event.preventDefault();show(index+1);}
  if(event.key==='Home'){event.preventDefault();show(0);}
  if(event.key==='End'){event.preventDefault();show(count-1);}
 });
 viewport.addEventListener('pointerdown',event=>{start={x:event.clientX,y:event.clientY};});
 viewport.addEventListener('pointerup',event=>{
  if(!start)return;
  const dx=event.clientX-start.x,dy=event.clientY-start.y;
  if(Math.abs(dx)>45&&Math.abs(dx)>Math.abs(dy)*1.2)show(index+(dx<0?1:-1));
  start=null;
 });
 viewport.addEventListener('pointercancel',()=>start=null);
 root.querySelector('.slides-fullscreen').onclick=async()=>{
  if(document.fullscreenElement===root)await document.exitFullscreen();
  else await root.requestFullscreen();
  size();
 };
 document.addEventListener('fullscreenchange',()=>{if(root.isConnected)size();});
 window.addEventListener('resize',()=>{if(root.isConnected)size();},{passive:true});
 requestAnimationFrame(size);
 show(0);
}

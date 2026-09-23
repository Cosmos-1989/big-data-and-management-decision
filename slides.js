/** Accessible, touch-friendly teaching deck for a course chapter. */
const escapeHtml=value=>String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));

function itemsOf(visual){
 const raw=visual?.items||visual?.steps||visual?.nodes||visual?.columns||[];
 return Array.isArray(raw)?raw:[];
}
function visualHtml(visual){
 if(!visual)return '';
 const kind=visual.kind||'cards';
 if(kind==='table'){
  const headers=visual.headers||visual.columns||[];
  const rows=visual.rows||[];
  return `<div class="slide-table-wrap"><table><thead><tr>${headers.map(x=>`<th>${escapeHtml(x)}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${(Array.isArray(row)?row:Object.values(row)).map(cell=>`<td>${escapeHtml(cell)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
 }
 const items=itemsOf(visual);
 if(!items.length)return '';
 return `<div class="slide-visual-content slide-visual-${escapeHtml(kind)}">${items.map((item,i)=>{
  const entry=typeof item==='string'&&kind==='metric'&&item.includes('｜')?{value:item.split('｜')[0],label:item.split('｜').slice(1).join('｜')}:typeof item==='string'?{label:item}:item;
  return `<div class="visual-node"><span class="visual-index">${String(i+1).padStart(2,'0')}</span><div><strong>${escapeHtml(entry.label||entry.title||entry.value||'')}</strong>${entry.value&&entry.label?`<em>${escapeHtml(entry.value)}</em>`:''}${entry.detail||entry.description||entry.text?`<p>${escapeHtml(entry.detail||entry.description||entry.text)}</p>`:''}</div></div>`;
 }).join('')}</div>`;
}
function slideHtml(slide,index,count){
 const points=Array.isArray(slide.points)?slide.points:[];
 const dark=index===0||index===count-1;
 const kinds={opener:'课程导入',goals:'学习目标',concept:'核心概念',case:'企业情境',calculation:'推导与计算',experiment:'课堂实验',discussion:'课堂讨论',summary:'本讲小结'};
 return `<article class="lecture-slide ${dark?'lecture-slide-dark':''} slide-kind-${escapeHtml(slide.kind||'concept')}" aria-hidden="${index?'true':'false'}"><div class="slide-grid"><div class="slide-copy"><span class="slide-kicker">${escapeHtml(slide.kicker||kinds[slide.kind]||'课程讲义')}</span><h3>${escapeHtml(slide.title||'')}</h3>${slide.lead?`<p class="slide-lead">${escapeHtml(slide.lead)}</p>`:''}${points.length?`<ul class="slide-points">${points.map(point=>`<li>${escapeHtml(point)}</li>`).join('')}</ul>`:''}</div><div class="slide-art">${visualHtml(slide.visual)}</div></div><span class="slide-page-number">${String(index+1).padStart(2,'0')} / ${String(count).padStart(2,'0')}</span></article>`;
}
export function lectureSlidesHtml(deck){
 if(!deck?.slides?.length)return '';
 const slides=deck.slides;
 return `<section id="slides" class="lesson-slides" aria-label="${escapeHtml(deck.title)}授课 Slides" tabindex="0"><div class="slides-toolbar"><div><span class="slides-eyebrow">LECTURE SLIDES</span><strong>${escapeHtml(deck.title)}</strong></div><button type="button" class="slides-fullscreen" aria-label="全屏显示授课 Slides">⛶ 全屏授课</button></div><div class="slide-viewport"><div class="slide-track">${slides.map((s,i)=>slideHtml(s,i,slides.length)).join('')}</div></div><div class="slides-controls"><button class="slides-prev" type="button" aria-label="上一页" disabled>←</button><span class="slides-counter" aria-live="polite">1 / ${slides.length}</span><button class="slides-next" type="button" aria-label="下一页">→</button><div class="slides-dots" aria-label="选择幻灯片">${slides.map((_,i)=>`<button type="button" aria-label="第 ${i+1} 页" aria-current="${i===0?'true':'false'}" data-slide="${i}"></button>`).join('')}</div><span class="slides-hint">左右滑动或使用方向键翻页</span></div></section>`;
}
export function initLectureSlides(root){
 if(!root)return;
 const track=root.querySelector('.slide-track');
 const slides=[...root.querySelectorAll('.lecture-slide')];
 const count=slides.length;
 let index=0,start=null;
 const show=next=>{
  index=Math.min(count-1,Math.max(0,next));
  track.style.transform=`translateX(-${index*100}%)`;
  slides.forEach((slide,i)=>slide.setAttribute('aria-hidden',String(i!==index)));
  root.querySelector('.slides-counter').textContent=`${index+1} / ${count}`;
  root.querySelector('.slides-prev').disabled=index===0;
  root.querySelector('.slides-next').disabled=index===count-1;
  root.querySelectorAll('.slides-dots button').forEach((button,i)=>button.setAttribute('aria-current',String(i===index)));
 };
 root.querySelector('.slides-prev').onclick=()=>show(index-1);
 root.querySelector('.slides-next').onclick=()=>show(index+1);
 root.querySelectorAll('.slides-dots button').forEach(button=>button.onclick=()=>show(Number(button.dataset.slide)));
 root.addEventListener('keydown',event=>{
  if(event.key==='ArrowLeft'){event.preventDefault();show(index-1);}
  if(event.key==='ArrowRight'){event.preventDefault();show(index+1);}
 });
 const viewport=root.querySelector('.slide-viewport');
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
 };
}

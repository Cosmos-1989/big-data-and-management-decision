/** Diagram-led reading cards for the enterprise applications in the textbook. */
const esc=value=>String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const normalize=value=>String(value||'').replace(/\s+/g,' ').trim();

export function decorateEnterpriseCases(article,chapterId,cases){
 const headings=[...article.querySelectorAll('h2,h3,h4')];
 for(const item of cases.filter(x=>x.chapterId===chapterId)){
  const target=headings.find(h=>normalize(h.textContent)===normalize(item.targetHeading));
  if(!target)continue;
  const flow=(item.flow||[]).map((line,i)=>{
   const [label,...rest]=line.split('｜');
   return `<div class="case-step"><span class="case-step-number">${String(i+1).padStart(2,'0')}</span><strong>${esc(rest.length?label:'步骤')}</strong><p>${esc(rest.length?rest.join('｜'):label)}</p></div>`;
  }).join('');
  const links=(item.sourceRefs||[]).map(key=>`<a href="#/chapter/bibliography?anchor=ref-${encodeURIComponent(key)}">[${esc(key)}]</a>`).join(' ');
  const section=document.createElement('section');section.className='enterprise-case';
  section.setAttribute('aria-label',`${item.organization} 案例图解`);
  section.innerHTML=`<div class="case-topline"><span class="case-type">企业案例 · 图解</span><span class="case-org">${esc(item.organization)}</span></div><p class="case-context">${esc(item.context)}</p><div class="case-flow">${flow}</div><div class="case-takeaway"><span>课堂观察</span><strong>${esc(item.takeaway)}</strong></div><details class="case-evidence"><summary>资料与案例边界</summary><p>${esc(item.sourceCaveat)} ${links}</p></details>`;
  target.after(section);
 }
}

export function initFigureZoom(article,main){
 const figures=[...article.querySelectorAll('figure')].filter(f=>f.querySelector('img'));
 if(!figures.length)return;
 const dialog=document.createElement('dialog');dialog.className='figure-dialog';
 dialog.innerHTML='<button class="figure-dialog-close" type="button" aria-label="关闭放大图示">×</button><div class="figure-dialog-scroller"><img alt=""></div><p class="figure-dialog-caption"></p>';
 main.append(dialog);
 dialog.querySelector('.figure-dialog-close').onclick=()=>dialog.close();
 dialog.onclick=event=>{if(event.target===dialog)dialog.close();};
 for(const figure of figures){
  const img=figure.querySelector('img');
  const caption=figure.querySelector('figcaption')?.textContent?.trim()||img.alt||'教材图示';
  const toolbar=document.createElement('div');toolbar.className='figure-toolbar';
  toolbar.innerHTML='<span>教材图示</span><button type="button">放大查看 ↗</button>';
  figure.prepend(toolbar);
  toolbar.querySelector('button').onclick=()=>{
   const enlarged=dialog.querySelector('img');enlarged.src=img.currentSrc||img.src;enlarged.alt=caption;
   dialog.querySelector('.figure-dialog-caption').textContent=caption;
   dialog.showModal();
  };
 }
}

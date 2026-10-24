/** Real business cases keep disclosed facts separate from course interpretation. */
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

export function businessCaseHtml(item,{includeHeading=true}={}){
 const questions=(item.questions||[]).map(q=>`<details class="business-case-question"><summary>${esc(q.question)}</summary><p>${esc(q.answer)}</p></details>`).join('');
 const evidence=(item.sources||[]).map(s=>`<li><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)}</a><span>${esc(s.publisher)} · ${esc(s.date||'发布日期未标明')}</span><p>${esc(s.support)}</p></li>`).join('');
 const lecture=item.slideRefs?.[0];
 const lectureLink=lecture?`<a href="#/chapter/${encodeURIComponent(item.chapter)}?anchor=${encodeURIComponent(lecture.sectionId)}&case=${encodeURIComponent(item.id)}">在本讲幻灯片中阅读 ↗</a>`:'';
 if(item.readabilityEdition)return `<section class="business-case-card readable-case" id="${esc(item.id)}" aria-label="${esc(item.title)}">
 <div class="business-case-heading"><span>${esc(item.company)}</span>${includeHeading?`<h3>${esc(item.title)}</h3>`:''}</div>
 <p class="business-case-context">${esc(item.context)}</p>
 <p class="business-case-analysis">${esc(item.analysis)}</p>
 ${questions}<details class="business-case-sources"><summary>案例资料</summary><ul>${item.facts.map(f=>`<li>${esc(f)}</li>`).join('')}</ul><p>${esc(item.limits)}</p><ol>${evidence}</ol></details>
 <div class="business-case-links">${lectureLink}<a href="#/chapter/business-casebook?anchor=${encodeURIComponent(item.id)}">查看案例资料 ↗</a></div>
 </section>`;
 return `<section class="business-case-card" id="${esc(item.id)}" aria-label="${esc(item.title)}">
 <div class="business-case-heading"><span>第 ${item.lesson} 讲 · ${esc(item.company)}</span>${includeHeading?`<h3>${esc(item.title)}</h3>`:''}</div>
 <p class="business-case-context">${esc(item.context)}</p>
 <div class="business-case-decision"><span>业务选择</span><p>${esc(item.decision)}</p></div>
 <div class="business-case-facts"><h4>公开事实</h4><ul>${item.facts.map(f=>`<li>${esc(f)}</li>`).join('')}</ul></div>
 <div class="business-case-analysis"><h4>概念联系</h4><p>${esc(item.analysis)}</p></div>
 <p class="business-case-limit"><strong>证据范围</strong>${esc(item.limits)}</p>
 ${questions}<details class="business-case-sources"><summary>一手资料与事实依据</summary><ol>${evidence}</ol><p class="business-case-accessed">资料核查日期：${esc(item.sources?.[0]?.accessed||'2026-10-17')}</p></details>
 <div class="business-case-links">${lectureLink}<a href="#/chapter/business-casebook?anchor=${encodeURIComponent(item.id)}">案例集中的固定位置 ↗</a></div>
 </section>`;
}

export function chapterBusinessCasesHtml(chapter,items){
 const matches=items.filter(item=>item.chapter===chapter);
 if(!matches.length)return '';
 return `<section class="chapter-business-cases" id="business-cases"><div class="business-cases-intro"><h2>真实商业案例</h2><a href="#/chapter/business-casebook">浏览全部案例 ↗</a></div>${matches.map(item=>businessCaseHtml(item)).join('')}</section>`;
}

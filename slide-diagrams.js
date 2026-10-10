/** Teaching figures: geometry is derived from source values, never from labels. */
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const text = value => esc(value).replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>').replace(/`([^`]+)`/g, '<code>$1</code>');
const colors = {blue:'#41789b',teal:'#3d8c89',muted:'#889baa',rose:'#ae687b'};
const color = tone => colors[tone] || colors.blue;
const num = value => Number(value).toLocaleString('zh-CN', {maximumFractionDigits:4});
let serial = 0;
const svg = contents => `<svg viewBox="0 0 1000 625" preserveAspectRatio="none" aria-hidden="true">${contents}</svg>`;
const label = (value, x, y, cls = '', style = '') => `<span class="diagram-label ${cls}" style="left:${x}%;top:${y}%;${style}">${text(value)}</span>`;
const pointLabel=(value,x,y)=>label(value,Math.max(12,Math.min(88,x)),Math.max(6,Math.min(92,y)),'diagram-point-label','width:max-content;max-width:24%;');
const tick = (x, y, value, anchor = 'middle') => `<text x="${x}" y="${y}" text-anchor="${anchor}" class="diagram-tick">${esc(num(value))}</text>`;
const map = (value, domain, start, end) => start + (value-domain[0])/(domain[1]-domain[0])*(end-start);

// Edges meet the actual rectangular or elliptical node boundary. Via points
// preserve branches and feedback paths without drawing through node labels.
function graph(d) {
 const id = `figure-arrow-${++serial}`;
 const nodes = new Map(d.nodes.map(n => [n.id, {...n,w:n.w||26,h:n.h||20}]));
 const xy = n => ({x:n.x*10,y:n.y*6.25});
 function boundary(n, toward, gap=4) {
  const c=xy(n),dx=toward.x-c.x,dy=toward.y-c.y,rx=n.w*5,ry=n.h*3.125;
  const f=n.shape==='circle'?1/Math.sqrt((dx/rx)**2+(dy/ry)**2):Math.min(dx?rx/Math.abs(dx):Infinity,dy?ry/Math.abs(dy):Infinity);
  const length=Math.hypot(dx,dy)||1;
  return {x:c.x+dx*f+dx/length*gap,y:c.y+dy*f+dy/length*gap};
 }
 const edges=(d.edges||[]).map(e=>{
  const a=nodes.get(e.from),b=nodes.get(e.to),via=(e.via||[]).map(p=>({x:p.x*10,y:p.y*6.25}));
  const start=boundary(a,via[0]||xy(b)),end=boundary(b,via.at(-1)||xy(a));
  const points=[start,...via,end],middle=points[Math.floor((points.length-1)/2)],next=points[Math.ceil((points.length-1)/2)];
  const x=e.labelX??(middle.x+next.x)/20,y=e.labelY??(middle.y+next.y)/12.5;
  return {line:`<polyline points="${points.map(p=>`${p.x},${p.y}`).join(' ')}" fill="none" stroke="${color(e.tone)}" stroke-width="3" ${e.dashed?'stroke-dasharray="9 7"':''} marker-end="url(#${id})"/>`,label:e.label?label(e.label,x,y,'diagram-edge-label'):''};
 });
 return svg(`<defs><marker id="${id}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M1 1L9 5L1 9" fill="none" stroke="#41789b" stroke-width="1.7"/></marker></defs>${edges.map(e=>e.line).join('')}`)+[...nodes.values()].map(n=>`<div class="diagram-node diagram-tone-${n.tone||'blue'} ${n.shape==='circle'?'diagram-node-circle':''}" style="left:${n.x}%;top:${n.y}%;width:${n.w}%;height:${n.h}%"><strong>${text(n.label)}</strong>${n.detail?`<span>${text(n.detail)}</span>`:''}</div>`).join('')+edges.map(e=>e.label).join('');
}

function bars(d) {
 const L=275,R=850,T=85,B=535,zero=map(0,d.domain,L,R),step=(B-T)/d.rows.length;
 let lines=`<line x1="${zero}" y1="45" x2="${zero}" y2="${B}" class="diagram-axis"/>`;
 let labels='';
 for(const [i,r] of d.rows.entries()) {
  const y=T+step*(i+.5),v=map(r.value,d.domain,L,R);
  lines+=`<line x1="${L}" x2="${R}" y1="${y}" y2="${y}" class="diagram-grid"/><rect x="${Math.min(v,zero)}" y="${y-20}" width="${Math.abs(v-zero)}" height="40" rx="4" fill="${color(r.tone)}"/>`;
  labels+=`<div class="diagram-row-label" style="top:${y/6.25}%"><strong>${text(r.label)}</strong>${r.detail?`<small>${text(r.detail)}</small>`:''}</div>`+label(num(r.value),91,y/6.25,'diagram-value');
 }
 const ticks=d.ticks||[d.domain[0],0,d.domain[1]];
 for(const t of new Set(ticks)){const x=map(t,d.domain,L,R);lines+=`<line x1="${x}" x2="${x}" y1="${B}" y2="${B+9}" class="diagram-axis"/>`+tick(x,B+48,t);}
 return svg(lines)+labels+`<span class="diagram-axis-unit">${text(d.unit||'')}</span>`;
}

function intervals(d) {
 const L=240,R=930,T=100,B=505,step=(B-T)/d.rows.length;
 let lines='',labels='';
 for(const t of d.ticks||d.domain){const x=map(t,d.domain,L,R);lines+=`<line x1="${x}" x2="${x}" y1="60" y2="${B+15}" class="diagram-grid"/>`+tick(x,B+58,t);}
 if(Number.isFinite(d.reference)){const x=map(d.reference,d.domain,L,R);lines+=`<line x1="${x}" x2="${x}" y1="45" y2="${B+15}" class="diagram-reference"/>`;}
 for(const [i,r] of d.rows.entries()){
  const y=T+step*(i+.5),low=map(r.low,d.domain,L,R),high=map(r.high,d.domain,L,R);
  lines+=`<line x1="${low}" x2="${high}" y1="${y}" y2="${y}" stroke="${color(r.tone)}" stroke-width="9"/><path d="M${low} ${y-18}V${y+18}M${high} ${y-18}V${y+18}" stroke="${color(r.tone)}" stroke-width="4"/>`;
  if(Number.isFinite(r.estimate))lines+=`<circle cx="${map(r.estimate,d.domain,L,R)}" cy="${y}" r="11" fill="${color(r.tone)}" stroke="white" stroke-width="3"/>`;
  labels+=`<div class="diagram-row-label" style="top:${y/6.25}%"><strong>${text(r.label)}</strong></div>`+label(r.detail||`[${num(r.low)}, ${num(r.high)}]`,(low+high)/20,y/6.25+9,'diagram-range-label');
 }
 return svg(lines)+labels+`<span class="diagram-axis-unit">${text(d.unit||'')}${d.referenceLabel?` · 虚线：${text(d.referenceLabel)}`:''}</span>`;
}

function matrix(d) {
 return `<table class="diagram-matrix"><thead><tr><th></th>${d.columns.map(c=>`<th scope="col">${text(c)}</th>`).join('')}</tr></thead><tbody>${d.cells.map((row,i)=>`<tr><th scope="row">${text(d.rowLabels[i])}</th>${row.map(c=>{
  const v=d.scale&&Number.isFinite(c.value)?Math.max(0,Math.min(1,(c.value-d.scale[0])/(d.scale[1]-d.scale[0]))):.25;
  return `<td class="diagram-tone-${c.tone||'blue'}" style="--cell-weight:${12+v*35}%"><strong>${text(c.text)}</strong>${c.detail?`<small>${text(c.detail)}</small>`:''}</td>`;
 }).join('')}</tr>`).join('')}</tbody></table>`;
}

function timeline(d) {
 const L=210,R=950,T=65,B=510,step=(B-T)/d.rows.length;
 let lines='',labels='';
 for(const t of d.ticks||d.domain){const x=map(t,d.domain,L,R);lines+=`<line x1="${x}" x2="${x}" y1="30" y2="${B+25}" class="diagram-grid"/>`+tick(x,B+70,t);}
 if(Number.isFinite(d.reference)){const x=map(d.reference,d.domain,L,R);lines+=`<line x1="${x}" x2="${x}" y1="25" y2="${B+25}" class="diagram-reference"/>`;}
 for(const [i,r] of d.rows.entries()){
  const y=T+step*(i+.5);lines+=`<line x1="${L}" x2="${R}" y1="${y}" y2="${y}" class="diagram-axis"/>`;
  labels+=`<div class="diagram-row-label" style="top:${y/6.25}%;width:18%"><strong>${text(r.label)}</strong></div>`;
  for(const s of r.segments||[]){const x=map(s.start,d.domain,L,R),end=map(s.end,d.domain,L,R);lines+=`<rect x="${x}" y="${y-23}" width="${end-x}" height="46" rx="5" fill="${color(s.tone)}" opacity=".2"/>`;labels+=label(s.label,(x+end)/20,y/6.25,'diagram-segment-label',`width:${(end-x)/10}%;`);}
  for(const p of r.points||[]){const x=map(p.at,d.domain,L,R);lines+=`<circle cx="${x}" cy="${y}" r="9" fill="${color(p.tone)}"/>`;labels+=pointLabel(p.label,p.labelX??x/10,p.labelY??y/6.25-12);}
 }
 return svg(lines)+labels+`<span class="diagram-axis-unit">${text(d.unit||'')}${d.referenceLabel?` · 虚线：${text(d.referenceLabel)}`:''}</span>`;
}

function plot(d) {
 const L=105,R=925,T=55,B=515,X=v=>map(v,d.xDomain,L,R),Y=v=>map(v,d.yDomain,B,T);
 let lines='',labels='';
 for(const t of d.xTicks||d.xDomain){const x=X(t);lines+=`<line x1="${x}" x2="${x}" y1="${T}" y2="${B}" class="diagram-grid"/>`+tick(x,B+48,t);}
 for(const t of d.yTicks||d.yDomain){const y=Y(t);lines+=`<line x1="${L}" x2="${R}" y1="${y}" y2="${y}" class="diagram-grid"/>`+tick(L-18,y+9,t,'end');}
 for(const r of d.regions||[]){lines+=`<polygon points="${r.points.map(([x,y])=>`${X(x)},${Y(y)}`).join(' ')}" fill="${color(r.tone)}" opacity=".17"/>`;if(r.label){const x=r.points.reduce((a,p)=>a+p[0],0)/r.points.length,y=r.points.reduce((a,p)=>a+p[1],0)/r.points.length;labels+=label(r.label,X(x)/10,Y(y)/6.25,'diagram-region-label');}}
 lines+=`<path d="M${L} ${T}V${B}H${R}" fill="none" class="diagram-axis"/>`;
 for(const s of d.series||[])lines+=`<polyline points="${s.points.map(([x,y])=>`${X(x)},${Y(y)}`).join(' ')}" fill="none" stroke="${color(s.tone)}" stroke-width="5" ${s.dashed?'stroke-dasharray="11 8"':''}/>`;
 for(const m of d.markers||[]){lines+=`<circle cx="${X(m.x)}" cy="${Y(m.y)}" r="10" fill="${color(m.tone)}" stroke="white" stroke-width="3"/>`;labels+=pointLabel(m.label,m.labelX??X(m.x)/10,m.labelY??Y(m.y)/6.25-9);}
 return svg(lines)+labels+`<span class="diagram-y-title">${text(d.yLabel)}</span><span class="diagram-x-title">${text(d.xLabel)}</span><div class="diagram-legend">${(d.series||[]).map(s=>`<span><i style="background:${color(s.tone)}"></i>${text(s.label)}</span>`).join('')}</div>`;
}

const renderers={graph,bars,intervals,matrix,timeline,plot};
export function diagramHtml(d) {
 if(!d||!renderers[d.type])return '';
 return `<figure class="slide-diagram diagram-${d.type}" aria-label="${esc(d.title)}"><header class="diagram-heading"><strong>${text(d.title)}</strong><span>${text(d.encoding)}</span></header><div class="diagram-canvas">${renderers[d.type](d)}</div><figcaption>${text(d.note||'')}</figcaption><p class="diagram-description">${text(d.description)}</p></figure>`;
}

import {readFileSync,writeFileSync} from 'node:fs';
import {diagramHtml} from '../dist/slide-diagrams.js';

const decks=JSON.parse(readFileSync(new URL('../dist/content/lecture-slides.json',import.meta.url),'utf8'));
const errors=[],chapters={},types={};
function crossesBox(a,b,n) {
 const w=n.w||26,h=n.h||20,box=[n.x-w/2,n.x+w/2,n.y-h/2,n.y+h/2];
 let lo=0,hi=1;
 for(const [p,q] of [[-(b.x-a.x),a.x-box[0]],[b.x-a.x,box[1]-a.x],[-(b.y-a.y),a.y-box[2]],[b.y-a.y,box[3]-a.y]]) {
  if(Math.abs(p)<1e-9){if(q<0)return false;continue;}
  const r=q/p;if(p<0)lo=Math.max(lo,r);else hi=Math.min(hi,r);if(lo>hi)return false;
 }
 return lo<hi-1e-9;
}
let figures=0;
for(const [chapter,deck] of Object.entries(decks)) {
 const counts={};
 for(const [i,s] of deck.slides.entries()) {
  const d=s.diagram;if(!d)continue;figures++;counts[d.type]=(counts[d.type]||0)+1;types[d.type]=(types[d.type]||0)+1;
  const fail=message=>errors.push(`${chapter} 第 ${i+1} 页：${message}`);
  const number=(v,name)=>{if(!Number.isFinite(v))fail(`${name} 非有限数值`);};
  const domain=(v,name)=>{if(!Array.isArray(v)||v.length!==2||!v.every(Number.isFinite)||v[0]>=v[1])fail(`${name} 无有效共同量尺`);};
  const inside=(v,range,name)=>{number(v,name);if(v<range[0]-1e-9||v>range[1]+1e-9)fail(`${name} 超出量尺`);};
  if(!d.title||!d.description||!d.encoding||!d.note)fail('缺少图名、完整文字解释、编码说明或解读');
  if(!['graph','bars','intervals','matrix','timeline','plot'].includes(d.type)){fail('未知图解类型');continue;}
  if(s.visual||s.workedExample)fail('图解与旧文字组件重叠，须审查重复内容和画面容量');
  if(d.type==='graph') {
   const ids=new Set();
   for(const n of d.nodes||[]){if(!n.id||ids.has(n.id))fail('节点标识重复或空缺');ids.add(n.id);if(!n.label)fail('节点缺少含义');const w=n.w??26,h=n.h??20;if(!Number.isFinite(w)||!Number.isFinite(h)||w<=0||h<=0)fail('节点尺寸非正值');inside(n.x,[w/2,100-w/2],'节点横坐标');inside(n.y,[h/2,100-h/2],'节点纵坐标');}
   for(const e of d.edges||[]){if(!ids.has(e.from)||!ids.has(e.to)||e.from===e.to){fail('边端点缺失或未经展开的自环');continue;}for(const p of e.via||[]){inside(p.x,[0,100],'路径横坐标');inside(p.y,[0,100],'路径纵坐标');}
    const path=[d.nodes.find(n=>n.id===e.from),...e.via||[],d.nodes.find(n=>n.id===e.to)];
    for(const n of d.nodes)if(n.id!==e.from&&n.id!==e.to&&path.slice(1).some((p,j)=>crossesBox(path[j],p,n)))fail(`边 ${e.from}→${e.to} 穿过节点 ${n.id}`);
   }
   for(const [j,a] of d.nodes.entries())for(const b of d.nodes.slice(j+1))if(Math.abs(a.x-b.x)<((a.w||26)+(b.w||26))/2&&Math.abs(a.y-b.y)<((a.h||20)+(b.h||20))/2)fail(`节点 ${a.id} 与 ${b.id} 重叠`);
  } else if(d.type==='bars') {
   domain(d.domain,'条形图');if(d.domain[0]>0||d.domain[1]<0)fail('条形图必须包含零点');for(const r of d.rows||[])inside(r.value,d.domain,'条形值');
  } else if(d.type==='intervals') {
   domain(d.domain,'区间图');for(const r of d.rows||[]){inside(r.low,d.domain,'下界');inside(r.high,d.domain,'上界');if(r.low>r.high)fail('上下界颠倒');if(r.estimate!==undefined)inside(r.estimate,[r.low,r.high],'点估计');}
  } else if(d.type==='matrix') {
   if(d.rowLabels?.length!==d.cells?.length||d.cells?.some(r=>r.length!==d.columns?.length))fail('矩阵行列语义不一致');if(d.scale){domain(d.scale,'色深量尺');for(const row of d.cells)for(const c of row)if(c.value!==undefined)inside(c.value,d.scale,'色深值');}
  } else if(d.type==='timeline') {
   domain(d.domain,'时间轴');for(const r of d.rows||[]){for(const s of r.segments||[]){inside(s.start,d.domain,'起点');inside(s.end,d.domain,'终点');if(s.start>=s.end)fail('时间段为空或倒置');}for(const p of r.points||[])inside(p.at,d.domain,'时点');}
  } else if(d.type==='plot') {
   domain(d.xDomain,'横坐标');domain(d.yDomain,'纵坐标');if(!d.xLabel||!d.yLabel)fail('坐标缺少含义/单位');
   for(const series of [...d.series||[],...d.regions||[]]){if(!series.points||series.points.length<2)fail('曲线或区域顶点不足');for(const [x,y] of series.points||[]){inside(x,d.xDomain,'曲线横坐标');inside(y,d.yDomain,'曲线纵坐标');}}
   for(const m of d.markers||[]){inside(m.x,d.xDomain,'标记横坐标');inside(m.y,d.yDomain,'标记纵坐标');}
  }
  if(d.reference!==undefined)inside(d.reference,d.domain,'参考线');
  for(const t of d.ticks||[])inside(t,d.domain,'刻度');
  for(const t of d.xTicks||[])inside(t,d.xDomain,'横刻度');
  for(const t of d.yTicks||[])inside(t,d.yDomain,'纵刻度');
  const html=diagramHtml(d);if(!html.includes('<figure')||html.includes('NaN')||html.includes('undefined'))fail('渲染输出无效');
 }
 chapters[chapter]={pages:deck.slides.length,figures:Object.values(counts).reduce((a,b)=>a+b,0),types:counts};
}
const report={figures,chapters,types,errors};
console.log(JSON.stringify(report,null,2));
if(process.argv[2])writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');
if(errors.length)process.exitCode=1;

import {diagramHtml} from '../dist/slide-diagrams.js';
import assert from 'node:assert/strict';
const meta={title:'核验图',description:'按明确数值核验输出坐标',encoding:'测试',note:'测试'};
function html(d){const h=diagramHtml({...meta,...d});assert(!/NaN|undefined/.test(h));return h;}
function close(a,b){assert(Math.abs(Number(a)-b)<1e-8,`${a} != ${b}`);}
let h=html({type:'bars',domain:[-2,4],unit:'x',ticks:[-2,0,4],rows:[{label:'负',value:-1},{label:'正',value:2}]});
let rects=[...h.matchAll(/<rect x="([^"]+)" y="([^"]+)" width="([^"]+)"/g)];
close(rects[0][1],370.8333333333333);close(rects[0][3],95.83333333333337);close(rects[1][1],466.6666666666667);close(rects[1][3],191.66666666666669);
h=html({type:'intervals',domain:[-1,3],unit:'x',ticks:[-1,3],reference:0,rows:[{label:'区间',low:0,high:2,estimate:1}]});
assert(h.includes('x1="412.5" x2="757.5"'));assert(h.includes('cx="585"'));
h=html({type:'timeline',domain:[0,10],unit:'x',ticks:[0,10],rows:[{label:'区间',segments:[{start:2,end:7,label:'窗'}],points:[{at:10,label:'截止'}]}]});
assert(h.includes('<rect x="358"'));assert(h.includes('width="370"'));assert(h.includes('cx="950"'));
h=html({type:'plot',xDomain:[0,10],yDomain:[-5,5],xLabel:'x',yLabel:'y',xTicks:[0,10],yTicks:[-5,5],series:[{label:'线',points:[[0,0],[10,5]]}],regions:[{points:[[0,0],[10,0],[10,5]]}],markers:[{x:5,y:0,label:'中点'}]});
assert(h.includes('points="105,285 925,285 925,55"'));assert(h.includes('points="105,285 925,55"'));assert(h.includes('cx="515" cy="285"'));
h=html({type:'matrix',columns:['列'],rowLabels:['行'],cells:[[{text:'值',value:1}]],scale:[0,2]});assert(h.includes('--cell-weight:29.5%'));
h=html({type:'graph',nodes:[{id:'a',x:20,y:50,w:20,h:20,label:'A'},{id:'b',x:80,y:50,w:20,h:20,label:'B'}],edges:[{from:'a',to:'b'}]});
assert(h.includes('points="304,312.5 696,312.5"'));
console.log('Six renderer types: coordinate, scale, negative baseline, interval, polygon, and boundary checks passed.');

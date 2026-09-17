import {experiments,sourceDemo} from './experiments.js';
import {marked} from './vendor/marked.js';
export const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let worker,sqlWorker,db,sqlConnection,active=false,timer,runGeneration=0;
let editor,output,status,runButton,current,program,mode,files,stdout='',results=[],runtimeReady=false;
const number=v=>typeof v==='number'?Number(v.toPrecision(6)).toLocaleString('zh-CN',{maximumFractionDigits:6}):typeof v==='object'?JSON.stringify(v):String(v??'—');
export function tableHtml(rows){
 if(!Array.isArray(rows)||!rows.length)return '<p class="empty-note">没有符合条件的记录。</p>';
 if(typeof rows[0]!=='object') rows=rows.map((v,i)=>({'序号':i+1,'数值':v}));
 const cols=[...new Set(rows.flatMap(Object.keys))];
 return `<div class="table-scroll"><table><thead><tr>${cols.map(c=>`<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>${rows.slice(0,500).map(r=>`<tr>${cols.map(c=>`<td>${esc(number(r[c]))}</td>`).join('')}</tr>`).join('')}</tbody></table></div>${rows.length>500?`<p class="empty-note">显示前 500 行，共 ${rows.length} 行；下载结果可获取全部数据。</p>`:''}`;
}
function chartSvg(rows,x,y,type){
 const data=rows.filter(r=>r[y]!==null&&r[y]!==''&&Number.isFinite(Number(r[y]))).slice(0,80);
 if(!data.length)return '<p class="empty-note">当前列没有可绘制的数值。</p>';
 const W=760,H=310,L=85,R=22,T=20,B=70,pw=W-L-R,ph=H-T-B;
 let low=Math.min(0,...data.map(r=>+r[y])),high=Math.max(0,...data.map(r=>+r[y]));if(high===low)high=low+1;
 const numericX=type==='line' && data.every(r=>typeof r[x]==='number');
 const xmin=numericX?Math.min(...data.map(r=>r[x])):0, xmax=numericX?Math.max(...data.map(r=>r[x])):1;
 const sy=v=>T+ph-(v-low)/(high-low)*ph, sx=i=>numericX?(xmin===xmax?L+pw/2:L+20+(data[i][x]-xmin)/(xmax-xmin)*(pw-40)):L+(i+.5)/data.length*pw;
 let s=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(y)}，按 ${esc(x)} 绘制"><title>${esc(y)} / ${esc(x)}</title>`;
 for(let k=0;k<=4;k++){let v=low+(high-low)*k/4;s+=`<line x1="${L}" x2="${W-R}" y1="${sy(v)}" y2="${sy(v)}" stroke="#e4ebf1"/><text x="${L-12}" y="${sy(v)+4}" text-anchor="end" fill="#657c8e" font-size="12">${esc(number(v))}</text>`;}
 if(type==='line')s+=`<polyline points="${data.map((r,i)=>`${sx(i)},${sy(+r[y])}`).join(' ')}" fill="none" stroke="#2b7da5" stroke-width="2.5"/>`;
 data.forEach((r,i)=>{const label=number(r[x]??i+1);s+=type==='line'?`<circle cx="${sx(i)}" cy="${sy(+r[y])}" r="3.5" fill="#1a758c"><title>${esc(label)}：${esc(number(r[y]))}</title></circle>`:`<rect x="${sx(i)-pw/data.length*.34}" y="${Math.min(sy(+r[y]),sy(0))}" width="${pw/data.length*.68}" height="${Math.max(1,Math.abs(sy(+r[y])-sy(0)))}" rx="2" fill="#397da5"><title>${esc(label)}：${esc(number(r[y]))}</title></rect>`;
 if(i%Math.max(1,Math.ceil(data.length/10))===0)s+=`<text x="${sx(i)}" y="${H-B+20}" text-anchor="end" transform="rotate(-24 ${sx(i)} ${H-B+20})" fill="#657c8e" font-size="12">${esc(label.length>18?label.slice(0,17)+'…':label)}</text>`;});
 return s+`<text x="${L}" y="${H-5}" fill="#657c8e" font-size="12">${esc(x)}　/　${esc(y)}${rows.length>80?'（前 80 条）':''}</text></svg>`;
}
function appendResult(payload){
 results.push(payload);document.querySelector('.waiting-result')?.remove();
 const section=document.createElement('section');section.className='result-block';
 section.innerHTML=`<h3>${esc(payload.title||'结果')}</h3>`;
 if(payload.kind==='html'){
  const frame=document.createElement('iframe');frame.title=payload.title||'程序生成的网页';frame.setAttribute('sandbox','');frame.srcdoc=payload.html;frame.className='html-result';section.append(frame);
 }else{
  let rows=payload.data;if(!Array.isArray(rows))rows=[rows];rows=rows.filter(v=>v&&typeof v==='object');
  const keys=[...new Set(rows.flatMap(Object.keys))];const nums=keys.filter(k=>rows.some(r=>typeof r[k]==='number'&&Number.isFinite(r[k])));
  if(rows.length&&nums.length){
   const controls=document.createElement('div');controls.className='chart-controls';
   controls.innerHTML=`<label>横轴 <select aria-label="${esc(payload.title)} 横轴">${keys.map(k=>`<option ${k===(payload.x||keys[0])?'selected':''}>${esc(k)}</option>`).join('')}</select></label><label>数值 <select aria-label="${esc(payload.title)} 数值">${nums.map(k=>`<option ${k===(payload.y||nums[0])?'selected':''}>${esc(k)}</option>`).join('')}</select></label><label>图形 <select aria-label="${esc(payload.title)} 图形"><option value="bar">柱状图</option><option value="line" ${payload.chartType==='line'?'selected':''}>折线图</option></select></label>`;
   const chart=document.createElement('div');chart.className='result-chart';
   const selects=controls.querySelectorAll('select');const draw=()=>chart.innerHTML=chartSvg(rows,selects[0].value,selects[1].value,selects[2].value);
   selects.forEach(s=>s.onchange=draw);section.append(controls,chart);draw();
  }
  const table=document.createElement('div');table.innerHTML=tableHtml(rows);section.append(table);
 }
 output.append(section);
}
function finish(message,error=false){active=false;clearTimeout(timer);runButton.disabled=false;document.querySelector('#stop-run').disabled=true;status.textContent=message;status.classList.toggle('error',error);document.querySelector('#export-result').disabled=!results.length&&!stdout;}
function stop(){runGeneration++;worker?.terminate();worker=null;runtimeReady=false;sqlWorker?.terminate();sqlWorker=null;db=null;sqlConnection=null;finish('运行已停止，运行环境已重置。');}
export function cleanupLab(){if(active)stop();}
async function runSql(code,gen){
 if(!db){
  status.textContent='正在加载 DuckDB（首次约 39 MB）…';
  const duckdb=await import('./vendor/duckdb/duckdb.js');
  const myWorker=new Worker('/vendor/duckdb/duckdb-browser-mvp.worker.js');sqlWorker=myWorker;
  const nextDb=new duckdb.AsyncDuckDB(new duckdb.ConsoleLogger(duckdb.LogLevel.ERROR),myWorker);
  const chunks=await Promise.all([0,1,2].map(async n=>{const r=await fetch('/vendor/duckdb/duckdb-mvp.part'+n);if(!r.ok)throw new Error('SQL 运行环境加载失败');return r.arrayBuffer();}));
  const wasmUrl=URL.createObjectURL(new Blob(chunks,{type:'application/wasm'}));
  try{await nextDb.instantiate(wasmUrl);}finally{URL.revokeObjectURL(wasmUrl);}if(gen!==runGeneration){myWorker.terminate();return;}
  await nextDb.open({query:{castBigIntToDouble:true,castDecimalToDouble:true,castTimestampToDate:true}});
  for(const [path,text] of Object.entries(files).filter(([p])=>p.endsWith('.csv')))await nextDb.registerFileText(path,text);
  const connection=await nextDb.connect();
  for(const [path] of Object.entries(files).filter(([p])=>p.endsWith('.csv'))){const name=path.split('/').at(-1).replace('.csv','');await connection.query(`CREATE VIEW "${name}" AS SELECT * FROM read_csv_auto('${path}', header=true)`);}
  await connection.query(files['src/bdm_decision/warehouse/build_kpi_tables.sql']);
  if(gen!==runGeneration){await nextDb.terminate();return;}db=nextDb;sqlConnection=connection;
 }
 status.textContent='正在执行查询…';
 const table=await sqlConnection.query(code);if(gen!==runGeneration)return;
 const rows=table.toArray().map(r=>Object.fromEntries(table.schema.fields.map(f=>{let v=r[f.name];if(v!==null&&v!==undefined){if(typeof v==='bigint')v=Number.isSafeInteger(Number(v))?Number(v):v.toString();else if(f.type.toString().startsWith('Date'))v=new Date(Number(v)).toISOString().slice(0,10);}return[f.name,v];})));
 appendResult({kind:'table',data:rows,title:`查询结果 · ${rows.length} 行`});finish('查询完成');
}
export async function runCurrent(){
 if(active||current.language==='yaml')return;active=true;stdout='';results=[];output.innerHTML='';status.classList.remove('error');runButton.disabled=true;document.querySelector('#stop-run').disabled=false;
 const gen=++runGeneration;timer=setTimeout(()=>{if(gen===runGeneration){stop();status.textContent='超过 120 秒，已停止。可减少计算量后重试。';}},120000);
 try{
  if(current.language==='sql'){await runSql(editor.value,gen);return;}
  if(!worker){worker=new Worker('/python-worker.js');worker.onerror=e=>finish('运行环境加载失败：'+e.message,true);}
  worker.onmessage=({data})=>{
   if(gen!==runGeneration)return;
   if(data.type==='status')status.textContent=data.text;
   if(data.type==='stdout'||data.type==='stderr'){stdout+=data.text;let log=document.querySelector('#run-log');if(!log){log=document.createElement('pre');log.id='run-log';output.append(log);}log.textContent=stdout;}
   if(data.type==='display')appendResult(data.payload);
   if(data.type==='error'){const err=document.createElement('pre');err.className='error-output';err.textContent=data.text;output.append(err);finish('程序出错，请查看错误信息并修改代码。',true);}
   if(data.type==='done'){
    runtimeReady=true;
    // Original case entrypoints print Markdown reports. Turn their tables into real visual results.
    if(!results.length&&stdout.includes('|')){
     const html=marked.parse(esc(stdout));const scratch=document.createElement('div');scratch.innerHTML=html;
     scratch.querySelectorAll('table').forEach((t,i)=>{const cols=[...t.querySelectorAll('thead th')].map(x=>x.textContent);const rows=[...t.querySelectorAll('tbody tr')].map(tr=>Object.fromEntries([...tr.children].map((td,j)=>{const value=td.textContent.trim();return[cols[j],/^-?\d+(\.\d+)?$/.test(value)?+value:value];})));appendResult({kind:'table',title:'程序输出表 '+(i+1),data:rows});});
    }
    if(!results.length&&!stdout)output.innerHTML='<p class="empty-note">代码已执行完成。使用 print() 输出文字，或 display() 显示表格与图形。</p>';
    finish('运行完成');
   }
  };
  const isSource=mode==='source';
  const demo=isSource&&sourceDemo[program?.id]?experiments.find(e=>e.id===sourceDemo[program.id]):null;
  // Source edits are written into the virtual package, then exercised by a visible companion example.
  const code=isSource?(demo?demo.code:editor.value):editor.value;
  worker.postMessage({code,path:isSource?'/course/'+program.path:'/course/experiment.py',source:isSource?editor.value:''});
 }catch(e){if(gen===runGeneration){const pre=document.createElement('pre');pre.className='error-output';pre.textContent=String(e.message||e);output.append(pre);finish('运行失败，可以修改代码或重置后重试。',true);}}
}
export async function mountLab(container,catalog,id='kpi'){
 cleanupLab();files ||= await(await fetch('/data/files.json')).json();
 const source=catalog.programs.find(p=>'source-'+p.id===id);
 const snippet=catalog.snippets.find(p=>p.id===id);
 program=source;mode=source?'source':snippet?'snippet':'experiment';
 current=source?{...source,title:source.path,params:[],description:source.status==='template'?'原仓库中的待实现模板，可编辑学习。没有已实现的算法或服务。':'编辑原始程序后，运行其配套课程示例。改动仅作用于当前浏览器。'}:snippet?{...snippet,params:[],description:'来自最新版教材的代码片段，可修改后运行。'}:experiments.find(e=>e.id===id)||experiments[2];
 container.innerHTML=`<div class="breadcrumb">课程实践 / 交互实验室</div><div class="lab-heading"><div><p class="eyebrow">LEARN BY DOING</p><h1>交互实验室</h1></div><a class="small-link" href="#/chapter/${esc(current.chapter||'03_sql_kpi')}">返回相关讲义 ↗</a></div><p class="lab-intro">修改参数或代码，运行真实课程程序。数据与计算保留在你的浏览器中。</p><div class="lab-selector"><label for="experiment">选择实验或源程序</label><select id="experiment"><optgroup label="课程交互实验">${experiments.map(e=>`<option value="${e.id}">${esc(e.title)}</option>`).join('')}</optgroup><optgroup label="全部课程源程序">${catalog.programs.map(p=>`<option value="source-${p.id}">${esc(p.path.replace('src/bdm_decision/',''))}${p.status==='template'?' · 模板':''}</option>`).join('')}</optgroup><optgroup label="教材中的 Python / SQL 片段">${catalog.snippets.filter(s=>['python','sql'].includes(s.language)).map(s=>`<option value="${s.id}">${esc(s.title)}</option>`).join('')}</optgroup></select></div><p class="experiment-description">${esc(current.description)}</p>${current.params.length?`<div class="parameters">${current.params.map(p=>p.type==='bool'?`<label class="bool-param"><input type="checkbox" data-param="${p.name}" ${p.value?'checked':''}>${p.label}</label>`:`<label>${p.label}<output>${p.value}</output><input aria-label="${p.label}" type="range" data-param="${p.name}" min="${p.min}" max="${p.max}" step="${p.step}" value="${p.value}"></label>`).join('')}</div>`:''}<div class="workspace"><section class="code-pane"><div class="pane-heading"><span>${esc(current.language==='sql'?'DuckDB SQL':current.language==='yaml'?'YAML 配置':'Python 3.12')}</span><div><button id="reset-code" class="text-button">恢复示例</button><button id="download-code" class="text-button">下载代码</button></div></div><textarea id="code-editor" aria-label="程序代码编辑器" spellcheck="false" autocapitalize="off" autocomplete="off"></textarea><div class="run-toolbar"><button id="run-code" class="primary">▶ 运行${mode==='source'&&sourceDemo[program?.id]?'配套示例':'代码'}</button><button id="stop-run" class="secondary" disabled>停止</button><span class="keyboard-hint">⌘ / Ctrl + Enter</span></div><details class="runtime-help"><summary>运行说明与数据表</summary><p>Python 标准库与课程包已就绪。可用 <code>display(rows, '标题', x='列名', y='数值列')</code> 生成表格和图形。首次运行会下载本地托管的运行环境；无需安装软件。运行超时可停止。</p><p>SQL 工作台使用 DuckDB，提供以下表：</p><code>${catalog.datasets.map(d=>d.name.replace('.csv','')).join(', ')}</code><p>SQL 脚本包含多个查询时显示最后一个结果；可选中所需查询复制到编辑器单独执行。</p>${mode==='source'&&sourceDemo[program?.id]?`<p>本文件通过“${esc(experiments.find(e=>e.id===sourceDemo[program.id]).title)}”示例调用。</p>`:''}</details></section><section class="output-pane"><div class="pane-heading"><span>运行结果</span><button id="export-result" class="text-button" disabled>下载结果</button></div><div id="run-status" class="run-status" role="status" aria-live="polite">${current.language==='yaml'?'配置文件可编辑和下载，不作为程序执行。':'准备就绪，点击运行开始计算。'}</div><div id="result-output"><div class="waiting-result"><div class="result-symbol">▥</div><h3>在这里观察结果</h3><p>运行后展示表格、图形与程序输出。<br>修改参数，再次运行即可比较。</p></div></div></section></div><p class="lab-footnote">课程样例为教学数据。补货与行动建议仅在模拟环境中计算，不连接真实业务系统。</p>`;
 editor=document.querySelector('#code-editor');output=document.querySelector('#result-output');status=document.querySelector('#run-status');runButton=document.querySelector('#run-code');editor.value=current.code;
 document.querySelector('#experiment').value=source?'source-'+source.id:current.id;
 document.querySelector('#experiment').onchange=e=>{runButton.disabled=true;location.hash='#/lab/'+e.target.value;};
 runButton.onclick=runCurrent;runButton.disabled=current.language==='yaml';
 document.querySelector('#stop-run').onclick=stop;
 document.querySelector('#reset-code').onclick=()=>{stop();editor.value=current.code;container.querySelectorAll('[data-param]').forEach(input=>{const p=current.params.find(p=>p.name===input.dataset.param);if(p.type==='bool')input.checked=p.value;else{input.value=p.value;input.previousElementSibling.textContent=p.value;}});status.textContent='已恢复原始代码和参数';if(current.language==='yaml')runButton.disabled=true;};
 editor.onkeydown=e=>{if(e.key==='Enter'&&(e.metaKey||e.ctrlKey)){e.preventDefault();runCurrent();}if(e.key==='Tab'){e.preventDefault();const s=editor.selectionStart;editor.setRangeText('    ',s,editor.selectionEnd,'end');}};
 container.querySelectorAll('[data-param]').forEach(input=>input.oninput=()=>{const value=input.type==='checkbox'?(input.checked?'True':'False'):input.value;if(input.type!=='checkbox')input.previousElementSibling.textContent=value;const re=new RegExp('^'+input.dataset.param+' = .+$','m');if(re.test(editor.value))editor.value=editor.value.replace(re,input.dataset.param+' = '+value);status.textContent='参数已更新，点击运行重新计算。';});
 document.querySelector('#download-code').onclick=()=>download(current.id+'.'+(current.language==='sql'?'sql':current.language==='yaml'?'yml':'py'),editor.value,'text/plain');
 document.querySelector('#export-result').onclick=()=>download(current.id+'-results.json',JSON.stringify({experiment:current.id,code:editor.value,stdout,results},null,2),'application/json');
}
export function download(name,content,type){const u=URL.createObjectURL(new Blob([content],{type}));const a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}

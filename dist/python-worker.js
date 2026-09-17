/* Each visitor gets an isolated, disposable Python process in a Web Worker. */
importScripts('./vendor/pyodide/pyodide.js');
let runtime;
let written=0;
function send(type,data){postMessage({type,...data});}
async function initialize(){
  if(runtime)return runtime;
  send('status',{text:'正在启动 Python，首次加载约 12 MB…'});
  runtime=await loadPyodide({indexURL:new URL('./vendor/pyodide/',self.location.href).href});
  const response=await fetch('./data/files.json');if(!response.ok)throw new Error('课程程序和数据加载失败');
  const files=await response.json();
  for(const [name,source] of Object.entries(files)){
    const p='/course/'+name;runtime.FS.mkdirTree(p.slice(0,p.lastIndexOf('/')));runtime.FS.writeFile(p,source);
  }
  runtime.FS.chdir('/course');
  runtime.setStdout({batched:line=>{written+=line.length+1;if(written<300000)send('stdout',{text:line+'\n'});}});
  runtime.setStderr({batched:line=>{written+=line.length+1;if(written<300000)send('stderr',{text:line+'\n'});}});
  runtime.registerJsModule('course_ui',{emit:payload=>{if(payload.length<2000000)send('display',{payload:JSON.parse(payload)});else throw new Error('输出超过 2 MB，请减少显示行数');}});
  await runtime.runPythonAsync(`import sys\nsys.path.insert(0, '/course/src')`);
  return runtime;
}
onmessage=async({data})=>{
  written=0;
  try{
    const py=await initialize();send('status',{text:'正在运行…'});
    // Restore source and sample data on every run: edits only affect this execution.
    const files=await(await fetch('./data/files.json')).json();
    for(const [name,source] of Object.entries(files))py.FS.writeFile('/course/'+name,source);
    py.globals.set('_bdm_code',data.code);py.globals.set('_bdm_path',data.path||'/course/experiment.py');py.globals.set('_bdm_source',data.source||'');
    await py.runPythonAsync(`
import sys, json, dataclasses, types
from datetime import date, datetime
from course_ui import emit
for _name in list(sys.modules):
    if _name.startswith('bdm_decision'): del sys.modules[_name]
def _json_default(v):
    if dataclasses.is_dataclass(v): return dataclasses.asdict(v)
    if isinstance(v, (date, datetime)): return v.isoformat()
    if isinstance(v, (set, tuple)): return list(v)
    if hasattr(v, 'tolist'): return v.tolist()
    return str(v)
def display(data, title='结果', x=None, y=None, kind='bar'):
    if dataclasses.is_dataclass(data): data=dataclasses.asdict(data)
    if isinstance(data, dict): data=[{'指标':k,'数值':v} for k,v in data.items()]
    if isinstance(data, (list,tuple)):
        data=[dataclasses.asdict(v) if dataclasses.is_dataclass(v) else v for v in data]
    emit(json.dumps({'kind':'table','data':data,'title':title,'x':x,'y':y,'chartType':kind}, default=_json_default, ensure_ascii=False))
def display_html(html, title='网页输出'):
    emit(json.dumps({'kind':'html','html':html,'title':title}))
if _bdm_source:
    with open(_bdm_path, 'w') as _file: _file.write(_bdm_source)
_main=types.ModuleType('__main__')
_main.__dict__.update({'__file__':_bdm_path,'display':display,'display_html':display_html})
sys.modules['__main__']=_main
exec(compile(_bdm_code, _bdm_path, 'exec'), _main.__dict__)
`);
    send('done',{text:'运行完成'});
  }catch(error){send('error',{text:String(error.message||error)});}
};

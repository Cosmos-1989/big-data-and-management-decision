import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {loadPyodide} from 'pyodide';
import {experiments,sourceDemo} from '../dist/experiments.js';
const py=await loadPyodide();const files=JSON.parse(await fs.readFile('dist/data/files.json','utf8'));
for(const [name,source] of Object.entries(files)){const p='/course/'+name;py.FS.mkdirTree(p.slice(0,p.lastIndexOf('/')));py.FS.writeFile(p,source);}
py.FS.chdir('/course');py.setStdout({batched:()=>{}});
await py.runPythonAsync(`import sys,json,dataclasses\nsys.path.insert(0,'/course/src')\n_results=[]\ndef display(data,title='结果',x=None,y=None,kind='bar'):\n    if dataclasses.is_dataclass(data): data=dataclasses.asdict(data)\n    if isinstance(data,dict): data=[{'指标':k,'数值':v} for k,v in data.items()]\n    if isinstance(data,(list,tuple)): data=[dataclasses.asdict(r) if dataclasses.is_dataclass(r) else r for r in data]\n    if x and data: assert x in data[0], f'{title}: missing x column {x}'\n    if y and data: assert y in data[0], f'{title}: missing y column {y}'\n    _results.append({'title':title,'data':data})\ndef display_html(html,title='结果'):\n    assert '<svg' in html\n    _results.append({'title':title,'html':html})`);
const outcome=[];
for(const e of experiments.filter(e=>e.language==='python')){
 try{await py.runPythonAsync('_results=[]\n'+e.code);const count=py.runPython('len(_results)');assert(count>0);outcome.push({id:e.id,status:'passed',outputs:count});}
 catch(error){outcome.push({id:e.id,status:'failed',error:String(error.message).slice(-1600)});}
}
// Every implemented Python module has a companion demonstration and is importable.
const catalog=JSON.parse(await fs.readFile('dist/content/catalog.json','utf8'));
for(const p of catalog.programs.filter(p=>p.language==='python'&&p.status==='implemented')){
 assert(sourceDemo[p.id],`Missing demo for ${p.path}`);
 await py.runPythonAsync('import '+p.path.replace('src/','').replace('.py','').replaceAll('/','.'));
}
// Meaningful parameter boundary checks against the course's actual implementations.
await py.runPythonAsync(`
from bdm_decision.optimization.inventory_optimization import load_product_policies,optimize_replenishment
policies=load_product_policies()
for budget,space in [(0,0),(2600,95),(5000,150)]:
    p=optimize_replenishment(policies,budget,space)
    assert p.total_budget_used <= budget+1e-8 and p.total_storage_used <= space+1e-8
from bdm_decision.cases.week07_prediction import train_week07_churn_model
from bdm_decision.models.evaluate import confusion_matrix
model,train,test=train_week07_churn_model()
labels=[r.churned for r in test];pred=[model.probability(r) for r in test]
lo=confusion_matrix(labels,pred,.1);hi=confusion_matrix(labels,pred,.9)
assert lo.true_positive+lo.false_positive > hi.true_positive+hi.false_positive
from bdm_decision.cases.week06_ab_testing import load_checkout_experiment
from bdm_decision.causal.ab_test import difference_in_means
a=difference_in_means(load_checkout_experiment(),'converted',confidence_level=.8)
b=difference_in_means(load_checkout_experiment(),'converted',confidence_level=.99)
assert b.ci_high-b.ci_low > a.ci_high-a.ci_low
`);
console.log(JSON.stringify(outcome,null,2));assert(outcome.every(r=>r.status==='passed'),'A runtime demo failed');
console.log('All implemented Python modules import successfully; parameter sensitivity and constraint checks passed.');
await fs.writeFile('runtime-validation.json',JSON.stringify({runtime:'Pyodide 0.27.7 / CPython 3.12',experiments:outcome,implementedPythonModules:catalog.programs.filter(p=>p.language==='python'&&p.status==='implemented').length,parameterChecks:['zero budget and capacity','feasible optimized plans','classification threshold sensitivity','confidence interval width']},null,2));

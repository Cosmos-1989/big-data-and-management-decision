import { mkdir, cp, copyFile, readFile, writeFile, rm } from 'node:fs/promises';
import { build } from 'esbuild';
await mkdir('dist/vendor',{recursive:true});
await cp('node_modules/katex/dist','dist/vendor/katex',{recursive:true});
await copyFile('node_modules/marked/lib/marked.esm.js','dist/vendor/marked.js');
await mkdir('dist/vendor/pyodide',{recursive:true});
for (const f of ['pyodide.js','pyodide.mjs','pyodide.asm.js','pyodide.asm.wasm','python_stdlib.zip','pyodide-lock.json']) await copyFile('node_modules/pyodide/'+f,'dist/vendor/pyodide/'+f);
await mkdir('dist/vendor/duckdb',{recursive:true});
for (const f of ['duckdb-browser-mvp.worker.js']) await copyFile('node_modules/@duckdb/duckdb-wasm/dist/'+f,'dist/vendor/duckdb/'+f);
await build({entryPoints:['node_modules/@duckdb/duckdb-wasm/dist/duckdb-browser.mjs'],bundle:true,format:'esm',outfile:'dist/vendor/duckdb/duckdb.js',minify:true});
console.log('Browser Python, DuckDB, Markdown and math assets bundled locally.');

const wasm=await readFile('node_modules/@duckdb/duckdb-wasm/dist/duckdb-mvp.wasm');
const size=16*1024*1024;
for(let n=0;n<3;n++)await writeFile('dist/vendor/duckdb/duckdb-mvp.part'+n,wasm.subarray(n*size,Math.min((n+1)*size,wasm.length)));
await rm('dist/vendor/duckdb/duckdb-mvp.wasm',{force:true});
await mkdir('dist/vendor/licenses',{recursive:true});
for(const [src,name] of [['node_modules/katex/LICENSE','KaTeX.txt'],['node_modules/marked/LICENSE.md','Marked.txt'],['node_modules/@duckdb/duckdb-wasm/LICENSE','DuckDB-WASM.txt'],['node_modules/apache-arrow/LICENSE.txt','Apache-Arrow.txt'],['node_modules/apache-arrow/NOTICE.txt','Apache-Arrow-NOTICE.txt'],['node_modules/tslib/LICENSE.txt','tslib.txt']]){try{await copyFile(src,'dist/vendor/licenses/'+name);}catch(e){if(e.code!=='ENOENT')throw e;}}

import katex from 'katex';import fs from 'node:fs';
const formulas=JSON.parse(fs.readFileSync('math-validation-input.json'));
const macros={'\\E':'\\mathbb E','\\Prob':'\\mathbb P','\\R':'\\mathbb R','\\N':'\\mathbb N','\\eps':'\\varepsilon','\\dd':'\\,\\mathrm d','\\argmin':'\\operatorname*{arg\\,min}','\\argmax':'\\operatorname*{arg\\,max}','\\abs':'\\left\\lvert #1\\right\\rvert','\\norm':'\\left\\lVert #1\\right\\rVert'};
const errors=[];for(const f of formulas)try{katex.renderToString(f.tex.replace(/\\label\{[^}]+\}/g,''),{macros,strict:false,displayMode:f.display,throwOnError:true})}catch(e){errors.push({page:f.page,tex:f.tex,error:e.message});}
console.log(JSON.stringify({formulas:formulas.length,errors},null,2));if(errors.length)process.exitCode=1;

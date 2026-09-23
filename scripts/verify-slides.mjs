import { readFileSync } from 'node:fs';
import katex from '../dist/vendor/katex/katex.mjs';

const read = path => JSON.parse(readFileSync(new URL(path, import.meta.url), 'utf8'));
const decks = read('../dist/content/lecture-slides.json');
const chapters = [
  '01_intro', '02_enterprise_data_model', '03_sql_kpi', '04_data_quality',
  '05_statistics_dashboard', '06_ab_testing', '07_prediction', '08_causality',
  '09_optimization', '10_process_mining'
];
const macros = {
  '\\E':'\\mathbb E', '\\Prob':'\\mathbb P', '\\R':'\\mathbb R',
  '\\N':'\\mathbb N', '\\eps':'\\varepsilon', '\\dd':'\\,\\mathrm d',
  '\\argmin':'\\operatorname*{arg\\,min}',
  '\\argmax':'\\operatorname*{arg\\,max}',
  '\\abs':'\\left\\lvert #1\\right\\rvert',
  '\\norm':'\\left\\lVert #1\\right\\rVert'
};
const errors = [];
let formulaCount = 0;
let pageCount = 0;
const report = (chapter, page, message) => errors.push(`${chapter} 第 ${page} 页：${message}`);

function checkFormula(value, chapter, page) {
  if (!value) return;
  for (const item of Array.isArray(value) ? value : [value]) {
    const source = typeof item === 'string' ? item : item?.latex;
    if (!source) continue;
    formulaCount += 1;
    try { katex.renderToString(source, { throwOnError:true, strict:false, trust:false, macros }); }
    catch (error) { report(chapter, page, `TeX 解析失败：${error.message}`); }
  }
}

function checkInline(value, chapter, page) {
  if (typeof value === 'string') {
    const opens = (value.match(/\\\(/g) || []).length;
    const closes = (value.match(/\\\)/g) || []).length;
    if (opens !== closes) report(chapter, page, '行内 TeX 的 \\( 与 \\) 数量不一致');
    const plain = value.replace(/\\\([\s\S]*?\\\)|(?<![\\$])\$[^$\n]+\$(?!\$)/g, '');
    if (/[∑∫√≈≠≤≥∞₀-₉α-ωΑ-Ω]/u.test(plain)) {
      report(chapter, page, '可见正文仍含未由 TeX 排版的数学符号');
    }
    for (const match of value.matchAll(/\\\(([\s\S]*?)\\\)|(?<![\\$])\$([^$\n]+)\$(?!\$)/g)) {
      checkFormula(match[1] ?? match[2], chapter, page);
    }
  } else if (Array.isArray(value)) {
    value.forEach(item => checkInline(item, chapter, page));
  } else if (value && typeof value === 'object') {
    Object.values(value).forEach(item => checkInline(item, chapter, page));
  }
}

for (const chapter of chapters) {
  const deck = decks[chapter];
  const doc = read(`../dist/content/${chapter}.json`);
  if (!deck?.slides?.length) { report(chapter, 0, '缺少幻灯片'); continue; }
  if (deck.title !== doc.title) report(chapter, 0, '幻灯片标题与讲义章节不一致');
  const anchors = new Set((doc.toc || []).map(item => item.id));
  for (const [index, slide] of deck.slides.entries()) {
    const page = index + 1;
    pageCount += 1;
    if (!slide.title || !slide.lead || !slide.takeaway || !slide.body?.length) {
      report(chapter, page, '缺少标题、引入、正文或结论');
    }
    const ref = slide.detailRef;
    if (!ref || ref.chapter !== chapter || !anchors.has(ref.anchor) || !ref.section) {
      report(chapter, page, '讲义延伸位置缺失或锚点无效');
    } else {
      const targetIndex = doc.toc.findIndex(item => item.id === ref.anchor);
      const target = doc.toc[targetIndex];
      const parent = [...doc.toc.slice(0, targetIndex)].reverse().find(item => item.level === 2);
      if (ref.section !== target.title && ref.section !== parent?.title) {
        report(chapter, page, '讲义小节名称与目标锚点不一致');
      }
      if (ref.subsection && ref.subsection !== target.title) {
        report(chapter, page, '讲义子节名称与目标锚点不一致');
      }
    }
    if (slide.visual && !['flow','cards','compare','metric','table'].includes(slide.visual.kind)) {
      report(chapter, page, '视觉组件类型未被渲染器支持');
    }
    if (slide.visual?.kind === 'table') {
      const width = (slide.visual.headers || slide.visual.columns || []).length;
      if (!width || (slide.visual.rows || []).some(row => !Array.isArray(row) || row.length !== width)) {
        report(chapter, page, '表格列数不一致');
      }
    }
    if (slide.codeBlock && !String(typeof slide.codeBlock === 'string' ? slide.codeBlock : slide.codeBlock.code).trimStart().startsWith('--')) {
      report(chapter, page, '示范 SQL 缺少开头注释');
    }
    checkFormula(slide.equation || slide.formula, chapter, page);
    for (const step of slide.workedExample?.steps || []) checkFormula(step.formula, chapter, page);
    checkInline([
      slide.title, slide.lead, slide.body, slide.points, slide.takeaway,
      slide.visual, slide.workedExample?.title, slide.workedExample?.context,
      slide.workedExample?.steps?.map(step => [step.label, step.text]),
      slide.workedExample?.result, slide.codeBlock?.caption, ref?.note
    ], chapter, page);
  }
}

console.log(JSON.stringify({ lectures:chapters.length, pages:pageCount, formulas:formulaCount, errors }, null, 2));
if (errors.length) process.exitCode = 1;

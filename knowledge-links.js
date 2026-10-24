/** Concept references for the first two lectures, including rendered case cards. */
const chapters = ['01_intro', '02_enterprise_data_model'];
let registryPromise;

export function loadKnowledgeMap(chapter) {
  if (!chapters.includes(chapter)) return null;
  return registryPromise ||= fetch('./content/concept-map.json?v=20261024-1').then(response => {
    if (!response.ok) throw new Error('概念释义暂时无法加载，请刷新重试。');
    return response.json();
  });
}

const escapeRegExp = text => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const excluded = 'a,code,pre,svg,math,.math,.katex,h1,h2,h3,h4,h5,h6,dt,th,caption,.citation,.statement-title,.knowledge-background,.business-case-sources,.lesson-slides';

export function decorateKnowledgeCases(main, chapter, registry) {
  if (!registry) return;
  const aliases = new Map();
  for (const item of registry.concepts) {
    if (chapters.indexOf(item.chapter) > chapters.indexOf(chapter)) continue;
    for (const term of new Set(item.linkAliases || [item.term, ...item.aliases])) aliases.set(term, {item, kind:'course'});
  }
  for (const item of registry.background.filter(item => item.chapters.includes(chapter))) {
    for (const term of new Set(item.linkAliases || [item.term, ...item.aliases])) aliases.set(term, {item, kind:'background'});
  }
  const patterns = [...aliases.keys()].sort((a,b) => b.length-a.length || a.localeCompare(b)).map(term => {
    let left = /^[A-Za-z0-9_]/.test(term) ? '(?<![A-Za-z0-9_])' : '';
    let right = /[A-Za-z0-9_]$/.test(term) ? '(?![A-Za-z0-9_])' : '';
    if (/^[\u3400-\u9fff]$/.test(term)) { left='(?<![\u3400-\u9fff])'; right='(?![\u3400-\u9fff])'; }
    return left + escapeRegExp(term) + right;
  });
  const matcher = new RegExp(patterns.join('|'), 'g');
  const scopes = [...main.querySelectorAll('.enterprise-case, .chapter-business-cases')];
  for (const [scopeIndex, scope] of scopes.entries()) {
    const walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) if (!walker.currentNode.parentElement.closest(excluded)) nodes.push(walker.currentNode);
    const seen = new WeakMap();
    let number = 0;
    for (const node of nodes) {
      const container = node.parentElement.closest('p,td,li,dd,.case-org,.business-case-heading>span');
      if (!container || !scope.contains(container)) continue;
      const used = seen.get(container) || new Set();
      seen.set(container, used);
      const fragment = document.createDocumentFragment();
      const text = node.textContent;
      let end = 0, changed = false;
      for (const match of text.matchAll(matcher)) {
        const {item,kind} = aliases.get(match[0]);
        if (used.has(item.id)) continue;
        used.add(item.id);
        if (!container.id) container.id = `knowledge-runtime-${scopeIndex}-${++number}`;
        const query = new URLSearchParams({anchor:kind==='course'?item.anchor:'term-'+item.id, from:chapter, at:container.id});
        const link = document.createElement('a');
        link.className = 'knowledge-link';
        link.dataset.knowledgeId = item.id;
        link.dataset.knowledgeKind = kind;
        link.href = `#/chapter/${kind==='course'?item.chapter:chapter}?${query}`;
        link.title = `${kind==='course'?`第${chapters.indexOf(item.chapter)+1}讲定义`:'文末释义'}：${item.definition}`;
        link.textContent = match[0];
        fragment.append(document.createTextNode(text.slice(end,match.index)),link);
        end = match.index+match[0].length;
        changed = true;
      }
      if (changed) { fragment.append(document.createTextNode(text.slice(end))); node.replaceWith(fragment); }
    }
  }
}

/** Preserve a visible way back after following either a definition or an endnote. */
export function focusKnowledgeTarget(main, target) {
  main.querySelectorAll('.knowledge-target').forEach(node => node.classList.remove('knowledge-target'));
  main.querySelector('.knowledge-return')?.remove();
  const query = new URLSearchParams(location.hash.split('?')[1] || '');
  const from = query.get('from'), at = query.get('at');
  if (!chapters.includes(from) || !at || !/^[\w:.-]+$/.test(at)) return target;
  const current = location.hash.split('?')[0].slice('#/chapter/'.length);
  if (!chapters.includes(current)) return target;
  const box = target.closest('.knowledge-definitions>div,aside.statement,li[role="doc-endnote"],p') || target;
  const row = document.createElement('div');
  row.className = 'knowledge-return';
  const link = document.createElement('a');
  link.href = `#/chapter/${from}?${new URLSearchParams({anchor:at})}`;
  link.textContent = `← 返回第${chapters.indexOf(from)+1}讲阅读位置`;
  row.append(link);
  box.before(row);
  target.classList.add('knowledge-target');
  if (!target.matches('a,button,[tabindex]')) target.tabIndex = -1;
  target.focus({preventScroll:true});
  return row;
}

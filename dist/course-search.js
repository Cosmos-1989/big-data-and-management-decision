let disposeSearch;

const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, character => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[character]));
const normalize = value => String(value ?? '').normalize('NFKC').toLocaleLowerCase().trim();
const chapterHref = (id, anchor) => `#/chapter/${encodeURIComponent(id)}${anchor ? `?anchor=${encodeURIComponent(anchor)}` : ''}`;

export function initCourseSearch(catalog) {
  disposeSearch?.();
  const button = document.querySelector('#course-search-button');
  if (!button) return () => {};

  const lifetime = new AbortController();
  const chapters = catalog.chapters ?? [];
  const titles = new Map([...chapters, ...(catalog.extras ?? [])].map(item => [item.id, item.title]));
  const seen = new Set();
  const documents = [
    ...chapters.map(item => ({ ...item, group: '课程讲义' })),
    ...(catalog.extras ?? []).map(item => ({ ...item, group: '课程资料' })),
  ].filter(item => item.id && !seen.has(item.id) && seen.add(item.id)).map(item => ({
    title: item.title,
    group: item.group,
    description: /^\d/.test(item.id) ? `第 ${Number(item.id.slice(0, 2))} 章` : '课程资料',
    href: chapterHref(item.id),
    searchText: normalize(`${item.title} ${item.id}`),
  }));
  const terms = (catalog.index ?? []).filter(item => item.term && item.chapter).map(item => ({
    title: item.term,
    group: '主题词条',
    description: titles.get(item.chapter) ?? '课程讲义',
    href: chapterHref(item.chapter, item.anchor),
    searchText: normalize(`${item.term} ${item.sort ?? ''}`),
  }));
  const shortcuts = [
    { title: '交互实验室', description: '运行 Python 与 SQL 实验', href: '#/lab', group: '常用入口' },
    { title: '课程资源', description: '教材、数据与作业', href: '#/resources', group: '常用入口' },
    { title: '主题索引', description: '按概念查找课程内容', href: '#/index', group: '常用入口' },
  ];

  const dialog = document.createElement('dialog');
  dialog.className = 'course-search-dialog';
  dialog.setAttribute('aria-labelledby', 'course-search-title');
  dialog.innerHTML = `<div class="course-search-shell">
    <div class="course-search-heading"><strong id="course-search-title">搜索课程</strong><button type="button" class="course-search-close" aria-label="关闭搜索">关闭 <span aria-hidden="true">Esc</span></button></div>
    <div class="course-search-input-wrap"><svg aria-hidden="true" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4.5 4.5"/></svg><input id="course-search-input" type="search" autocomplete="off" placeholder="搜索章节、课程资料或概念…" aria-label="搜索章节、课程资料或概念" autofocus></div>
    <div id="course-search-results" class="course-search-results" aria-live="polite"></div>
    <div class="sr-only" role="status" id="course-search-selection"></div><div class="course-search-footer"><span>↑ ↓ 选择 · Enter 打开</span><span>Esc 关闭</span></div>
  </div>`;
  document.body.append(dialog);
  const input = dialog.querySelector('input');
  const results = dialog.querySelector('#course-search-results');
  let previousFocus;
  let selectedIndex = -1;

  function resultHtml(item) {
    return `<a class="course-search-result" href="${escapeHtml(item.href)}"><span><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.description)}</small></span><span class="course-search-arrow" aria-hidden="true">→</span></a>`;
  }

  function render() {
    selectedIndex = -1;
    dialog.querySelector('#course-search-selection').textContent='';
    const query = normalize(input.value);
    const tokens = query.split(/\s+/).filter(Boolean);
    let groups;
    if (!query) {
      const core = chapters.filter(item => /^\d/.test(item.id));
      const initial = (core.length ? core : chapters).slice(0, 8).map(item => documents.find(document => document.href === chapterHref(item.id))).filter(Boolean);
      groups = [['课程讲义', initial], ['常用入口', shortcuts]];
    } else {
      const matches = [...documents, ...terms].filter(item => tokens.every(token => item.searchText.includes(token)));
      matches.sort((left, right) => Number(normalize(right.title).startsWith(query)) - Number(normalize(left.title).startsWith(query)));
      groups = ['课程讲义', '课程资料', '主题词条'].map(group => [group, matches.filter(item => item.group === group).slice(0, 12)]);
    }
    const shown = groups.filter(([, items]) => items.length);
    results.innerHTML = shown.length ? shown.map(([label, items]) => `<section class="course-search-group"><h2>${escapeHtml(label)}</h2>${items.map(resultHtml).join('')}</section>`).join('') : '<p class="course-search-empty">没有找到匹配内容。请尝试章节名称或相关概念。</p>';
    results.scrollTop = 0;
  }

  function open() {
    if (dialog.open) {
      input.focus();
      return;
    }
    previousFocus = document.activeElement;
    input.value = '';
    render();
    dialog.showModal();
    input.focus();
  }

  button.addEventListener('click', open, { signal: lifetime.signal });
  document.addEventListener('keydown', event => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k' && !event.isComposing) {
      event.preventDefault();
      if (!event.repeat) open();
    }
  }, { signal: lifetime.signal });
  input.addEventListener('input', render, { signal: lifetime.signal });
  input.addEventListener('keydown', event => {
    if (event.isComposing) return;
    const links = [...results.querySelectorAll('a')];
    if ((event.key === 'ArrowDown' || event.key === 'ArrowUp') && links.length) {
      event.preventDefault();
      selectedIndex = event.key === 'ArrowDown' ? (selectedIndex + 1) % links.length : (selectedIndex < 0 ? links.length - 1 : (selectedIndex - 1 + links.length) % links.length);
      links.forEach((link, index) => link.classList.toggle('is-selected', index === selectedIndex));
      links[selectedIndex].scrollIntoView({ block: 'nearest' });
      dialog.querySelector('#course-search-selection').textContent=`已选择 ${selectedIndex+1} / ${links.length}：${links[selectedIndex].querySelector('strong').textContent}`;
    } else if (event.key === 'Enter' && links.length) {
      event.preventDefault();
      links[selectedIndex < 0 ? 0 : selectedIndex].click();
    }
  }, { signal: lifetime.signal });
  dialog.addEventListener('click', event => {
    if (event.target === dialog || event.target.closest('.course-search-close, .course-search-result')) dialog.close();
  }, { signal: lifetime.signal });
  dialog.addEventListener('close', () => {
    if (previousFocus?.isConnected) previousFocus.focus({ preventScroll: true });
  }, { signal: lifetime.signal });

  disposeSearch = () => {
    if (dialog.open) dialog.close();
    lifetime.abort();
    dialog.remove();
  };
  return disposeSearch;
}

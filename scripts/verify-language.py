"""Check Chinese typography, source-authored notes and protected course content.

These structural regressions supplement editorial review; they do not score the
quality of academic language. Set BDM_BASELINE_DIR to an exported pre-edit dist.
"""
from collections import Counter
import json
import os
from pathlib import Path

from bs4 import BeautifulSoup, Comment

from content_typography import anchor_id, normalize_soup, protected

SITE = Path(__file__).resolve().parents[1]
CONTENT = SITE / "dist/content"
baseline = Path(os.environ["BDM_BASELINE_DIR"]) if os.environ.get("BDM_BASELINE_DIR") else None
errors, documents, all_notes = [], [], []


def preserved(before, after):
    stream = iter(after)
    return all(any(value == item for value in stream) for item in before)


for path in sorted(CONTENT.glob("*.json")):
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or not data.get("html"):
        continue
    soup = BeautifulSoup(data["html"], "html.parser")
    unnormalized = normalize_soup(soup)
    if unnormalized:
        errors.append([path.stem, "Chinese prose gaps remain", unnormalized])
    refs = soup.select('a[role="doc-noteref"]')
    notes = soup.select('.course-notes ol > li[id]')
    ids = Counter(item["id"] for item in soup.find_all(id=True))
    for ref in refs + soup.select('a[role="doc-backlink"]'):
        href = ref.get("href", "")
        target = anchor_id(href)
        if not href.startswith("#/chapter/" + path.stem + "?anchor=") or ids[target] != 1:
            errors.append([path.stem, "Invalid note destination", href, ids[target]])
    referenced = {anchor_id(ref["href"]) for ref in refs}
    for note in notes:
        if note["id"] not in referenced or not note.select('a[role="doc-backlink"]'):
            errors.append([path.stem, "Note lacks a reference or return link", note["id"]])
        all_notes.append({"document": path.stem, "id": note["id"], "definition": note.get_text(" ", strip=True)})
    for node in soup.find_all(string=True):
        if isinstance(node, Comment) or protected(node):
            continue
        if "[^" in str(node):
            errors.append([path.stem, "Unrendered Markdown footnote", str(node)])
    if baseline and (baseline / path.name).exists():
        old = json.loads((baseline / path.name).read_text())
        old_soup = BeautifulSoup(old["html"], "html.parser")
        if [node.get_text() for node in old_soup.find_all("pre")] != [node.get_text() for node in soup.find_all("pre")]:
            errors.append([path.stem, "Source program block changed"])
        old_math = [node.get_text() for node in old_soup.select(".math")]
        new_math = [node.get_text() for node in soup.select(".math")]
        if path.stem == "bibliography":
            # Former Pandoc HTML used <em>L</em> and Unicode spacing here;
            # --mathjax now preserves the exact TeX in references.bib instead.
            old_math = [r"\(L=\lambda W\)" if value == "L\u2004=\u2004λW" else value for value in old_math]
        if not preserved(old_math, new_math):
            errors.append([path.stem, "Original math was changed or removed"])
    documents.append({"id": path.stem, "footnotes": len(notes), "references": len(refs)})

intro = BeautifulSoup(json.loads((CONTENT / "01_intro.json").read_text())["html"], "html.parser")
bi = next(paragraph for paragraph in intro.find_all("p") if "经典 BI" in paragraph.get_text())
definitions = [intro.find(id=anchor_id(ref["href"])).get_text() for ref in bi.select('a[role="doc-noteref"]')]
for name in ["数据仓库", "ETL", "OLAP", "报表系统"]:
    if not any(name in definition for definition in definitions):
        errors.append(["01_intro", "Requested concept lacks its introductory note", name])
for name in ["设备 状态", "估计 各方案"]:
    if name in intro.get_text():
        errors.append(["01_intro", "Requested spacing regression", name])

report = {"documents": len(documents), "footnotes": len(all_notes),
          "footnoteReferences": sum(item["references"] for item in documents),
          "pages": documents, "terms": all_notes, "errors": errors}
target = Path(os.environ.get("BDM_LANGUAGE_REPORT", SITE / "review/language-20261017/language-validation.json"))
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({key: value for key, value in report.items() if key not in {"pages", "terms"}}, ensure_ascii=False, indent=2))
if errors:
    raise SystemExit(1)

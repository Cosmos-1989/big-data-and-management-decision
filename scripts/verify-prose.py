"""Guard reviewed reader-facing content against specific editorial residues.

This is a regression check, not a linguistic quality score. Formal references,
model assumptions, evidence limits, exercises and reproduction steps are valid.
Run with the same BeautifulSoup dependency as build_content.py.
"""
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

SITE = Path(__file__).resolve().parents[1]
PATTERNS = [
    r"建议按.{0,6}组织教学",
    r"将这一教学思想",
    r"本案例用于升级",
    r"教学上",
    r"告诉读者",
    r"本讲依次",
    r"为下一(?:章|讲)",
    r"教材(?:把|将).{0,18}(?:迁移|重构|构造)",
    r"真正重要",
    r"本版沿用",
]
errors = []
documents = 0
decks = 0
slide_pages = 0


def check(text, location):
    for pattern in PATTERNS:
        for match in re.finditer(pattern, text):
            errors.append({
                "location": location,
                "pattern": pattern,
                "context": text[max(0, match.start() - 20):match.end() + 40],
            })


for path in sorted((SITE / "dist/content").glob("*.json")):
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        continue
    if data.get("html"):
        documents += 1
        soup = BeautifulSoup(data["html"], "html.parser")
        for element in soup.find_all(["pre", "code"]):
            element.decompose()
        check(soup.get_text(" ", strip=True), path.name)
    elif path.name == "lecture-slides.json":
        decks = len(data)
        for chapter, deck in data.items():
            for page, slide in enumerate(deck["slides"], 1):
                slide_pages += 1
                prose = {key: value for key, value in slide.items()
                         if key not in {"codeBlock", "equation", "formula"}}
                check(json.dumps(prose, ensure_ascii=False), f"{chapter}:{page}")

report = {"documents": documents, "decks": decks, "slidePages": slide_pages,
          "patterns": PATTERNS, "errors": errors}
target = SITE / "review/prose-cleanup/residual-scan.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({key: value for key, value in report.items() if key != "patterns"},
                 ensure_ascii=False, indent=2))
if errors:
    raise SystemExit(1)

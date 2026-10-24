"""Check lecture independence, first-use terminology and business-case coverage.

These checks complement source and visual review; a valid URL alone is not
evidence that a business claim is supported. Primary-source review is recorded
separately in content-source/teaching-20261017/*/review.md.
"""
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "dist/content"
decks = json.loads((CONTENT / "lecture-slides.json").read_text())
cases = json.loads((CONTENT / "business-cases.json").read_text())
terms = json.loads((CONTENT / "lecture-terms.json").read_text())
errors, term_report, case_report = [], [], []


def strings(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [text for item in value for text in strings(item)]
    if isinstance(value, dict):
        return [text for item in value.values() for text in strings(item)]
    return []


def visible(slide):
    keys = ["title", "lead", "body", "points", "takeaway", "visual", "diagram", "workedExample", "prompts"]
    return " ".join(strings([slide.get(key) for key in keys]))


def contains(text, alias):
    if not alias:
        return False
    if re.fullmatch(r"[A-Za-z0-9 /-]+", alias):
        return bool(re.search(r"(?<![A-Za-z0-9])" + re.escape(alias) + r"(?![A-Za-z0-9])", text))
    return alias in text


by_lesson = {deck["lectureNumber"]: (key, deck) for key, deck in decks.items()}
if sorted(by_lesson) != list(range(1, 17)) or len(decks) != 16:
    errors.append("The course must contain sixteen distinct lecture decks")
term_lessons = set()
for term in terms:
    lesson = int(term["lesson"])
    term_lessons.add(lesson)
    if lesson not in by_lesson:
        errors.append([term["term"], "Unknown lecture", lesson])
        continue
    deck_id, deck = by_lesson[lesson]
    slides = deck["slides"]
    aliases = [term["term"], *term.get("aliases", [])]
    first = next((i for i, s in enumerate(slides) if any(contains(visible(s), a) for a in aliases)), None)
    definition = next((i for i, s in enumerate(slides) if s["title"] == term["definitionSlideTitle"]), None)
    if first is None or definition is None or definition > first:
        errors.append({"term": term["term"], "lesson": lesson, "first": first, "definition": definition,
                       "firstTitle": slides[first]["title"] if first is not None else None,
                       "definitionTitle": term["definitionSlideTitle"]})
    if definition is not None and not slides[definition].get("body"):
        errors.append([term["term"], "Definition page has no explanation"])
    term_report.append({"lesson": lesson, "deck": deck_id, "term": term["term"],
                        "firstPage": None if first is None else first + 1,
                        "definitionPage": None if definition is None else definition + 1,
                        "explanation": term.get("explanation", "")})
for missing in set(range(1, 17)) - term_lessons:
    errors.append([missing, "Missing first-use terminology review"])

counts = Counter(c["lesson"] for c in cases)
for lesson in range(1, 17):
    if counts[lesson] < 5:
        errors.append([lesson, "Fewer than five new business cases"])
if len({c["id"] for c in cases}) != len(cases):
    errors.append("Duplicate case IDs")
source_uses = defaultdict(list)
for case in cases:
    lesson = case["lesson"]
    deck_id, deck = by_lesson[lesson]
    matches = [(i, s) for i, s in enumerate(deck["slides"], 1) if s.get("caseId") == case["id"]]
    if not matches or not any(s.get("diagram") or s.get("visual") for _, s in matches):
        errors.append([case["id"], "Missing case pages or mechanism visual"])
    if len(case.get("facts", [])) < 2 or not case.get("analysis") or not case.get("limits"):
        errors.append([case["id"], "Facts, interpretation or evidence scope missing"])
    if not case.get("questions") or any(not q.get("question") or not q.get("answer") for q in case["questions"]):
        errors.append([case["id"], "Discussion lacks a question or answer"])
    for source in case.get("sources", []):
        if not source.get("url", "").startswith("https://") or not all(source.get(k) for k in ["title", "publisher", "support", "accessed"]):
            errors.append([case["id"], "Source record is incomplete"])
        source_uses[source["url"]].append(case["id"])
    for _, slide in matches:
        if not slide.get("sources"):
            errors.append([case["id"], "Slide omits direct evidence links"])
    case_report.append({"id": case["id"], "lesson": lesson, "company": case["company"],
                        "deck": deck_id, "pages": [i for i, _ in matches], "sources": len(case["sources"])})

# Original theoretical material is a protected baseline, not a pool to replace
# with case summaries. Splitting a slide can duplicate a formula but not lose it.
baseline = os.environ.get("BDM_SLIDES_BASELINE")
baseline_report = {}
if baseline:
    old = json.loads(Path(baseline).read_text())
    def math_content(deck):
        result = []
        for s in deck["slides"]:
            for value in strings(s):
                result += [m.group(1) for m in re.finditer(r"\\\(([\s\S]*?)\\\)", value)]
            for key in ["equation", "formula"]:
                for entry in s.get(key, []) if isinstance(s.get(key), list) else [s.get(key)]:
                    if isinstance(entry, str): result.append(entry)
                    elif isinstance(entry, dict) and entry.get("latex"): result.append(entry["latex"])
            for step in (s.get("workedExample") or {}).get("steps", []) if isinstance(s.get("workedExample"), dict) else []:
                if isinstance(step, dict) and step.get("formula"):
                    for f in step["formula"] if isinstance(step["formula"], list) else [step["formula"]]:
                        result.append(f if isinstance(f, str) else f.get("latex"))
        return Counter(result)
    for chapter, before in old.items():
        after = decks[chapter]
        missing_math = math_content(before) - math_content(after)
        diagrams_before = Counter(json.dumps(s["diagram"], ensure_ascii=False, sort_keys=True) for s in before["slides"] if s.get("diagram"))
        diagrams_after = Counter(json.dumps(s["diagram"], ensure_ascii=False, sort_keys=True) for s in after["slides"] if s.get("diagram"))
        codes_before = Counter(json.dumps(s["codeBlock"], ensure_ascii=False, sort_keys=True) for s in before["slides"] if s.get("codeBlock"))
        codes_after = Counter(json.dumps(s["codeBlock"], ensure_ascii=False, sort_keys=True) for s in after["slides"] if s.get("codeBlock"))
        if missing_math: errors.append([chapter, "Original formulas missing", list(missing_math)])
        if diagrams_before - diagrams_after: errors.append([chapter, "Original diagrams changed or missing"])
        if codes_before - codes_after: errors.append([chapter, "Original code blocks changed or missing"])
        baseline_report[chapter] = {"previousPages": len(before["slides"]), "currentPages": len(after["slides"]),
                                    "missingOriginalMath": sum(missing_math.values()),
                                    "originalDiagrams": sum(diagrams_before.values()), "originalCodeBlocks": sum(codes_before.values())}

report = {"decks": len(decks), "slides": sum(len(d["slides"]) for d in decks.values()),
          "cases": len(cases), "caseCountsByLesson": dict(sorted(counts.items())),
          "uniqueSourceUrls": len(source_uses), "reusedSourcesForHumanReview": {u: ids for u, ids in source_uses.items() if len(ids) > 1},
          "terms": term_report, "casePages": case_report, "baseline": baseline_report, "errors": errors}
target = Path(os.environ.get("BDM_TEACHING_REPORT", ROOT / "review/teaching-20261017/teaching-validation.json"))
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({k: report[k] for k in ["decks", "slides", "cases", "caseCountsByLesson", "uniqueSourceUrls", "errors"]}, ensure_ascii=False, indent=2))
if errors:
    raise SystemExit(1)

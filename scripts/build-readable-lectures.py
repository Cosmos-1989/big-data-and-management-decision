#!/usr/bin/env python3
"""Publish the reviewed prose edition without rebuilding unrelated lectures."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content-source/readability-20261024"
REVIEW = ROOT / "review/readability-20261024"
CONTENT = ROOT / "dist/content"
spec = importlib.util.spec_from_file_location("concepts", ROOT / "scripts/build-concept-links.py")
concepts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(concepts)


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_cases(items):
    script = """import {businessCaseHtml} from './dist/business-cases.js';
let input=''; for await(const chunk of process.stdin)input+=chunk;
process.stdout.write(JSON.stringify(Object.fromEntries(JSON.parse(input).map(item=>[item.id,businessCaseHtml(item)]))));"""
    result = subprocess.run(["node", "--input-type=module", "-e", script], cwd=ROOT,
                            input=json.dumps(items), text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def main():
    config = read(SOURCE / "config.json")
    chapters = config["chapters"]
    knowledge = ROOT / config["conceptSource"]
    REVIEW.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="bdm-readable-") as directory:
        stage = Path(directory) / "content"
        shutil.copytree(CONTENT, stage)
        catalog = read(stage / "catalog.json")
        for chapter in chapters:
            document = read(SOURCE / "chapters" / (chapter + ".json"))
            soup = BeautifulSoup(document["html"], "html.parser")
            document["toc"] = [{"id": node["id"], "title": node.get_text("", strip=True), "level": int(node.name[1])}
                               for node in soup.find_all(["h2", "h3"], id=True)]
            save(stage / (chapter + ".json"), document)
            entry = next(item for item in catalog["chapters"] if item["id"] == chapter)
            entry["toc"] = document["toc"]
        save(stage / "catalog.json", catalog)
        concept_report = concepts.build(knowledge, stage, REVIEW / "concepts")
        if concept_report["counts"]["forwardReferences"]:
            raise ValueError("An earlier lecture uses a concept defined only in a later lecture")
        cases = read(stage / "business-cases.json")
        changed_cases = read(SOURCE / "business-cases.json")
        replacements = {item["id"]: item for item in changed_cases}
        cases = [replacements.get(item["id"], item) for item in cases]
        save(stage / "business-cases.json", cases)
        cards = read(stage / "case-cards.json")
        replacements = {item["caseId"]: item for item in read(SOURCE / "case-cards.json")}
        save(stage / "case-cards.json", [replacements.get(item["caseId"], item) for item in cards])
        casebook = read(stage / "business-casebook.json")
        soup = BeautifulSoup(casebook["html"], "html.parser")
        rendered = render_cases(changed_cases)
        for item in changed_cases:
            target = soup.find(id=item["id"])
            if target is None:
                raise ValueError("Missing original case: " + item["id"])
            target.replace_with(BeautifulSoup(rendered[item["id"]], "html.parser"))
        casebook["html"] = str(soup)
        for entry in casebook["toc"]:
            if entry["id"] in rendered:
                entry["title"] = next(item["title"] for item in changed_cases if item["id"] == entry["id"])
        save(stage / "business-casebook.json", casebook)
        # Only the labels attached to reading links follow renamed headings.
        decks = read(stage / "lecture-slides.json")
        for chapter in chapters:
            headings = {item["id"]: item["title"] for item in read(stage / (chapter + ".json"))["toc"]}
            for slide in decks[chapter]["slides"]:
                ref = slide["detailRef"]
                ref["section"] = headings[ref["anchor"]]
                if ref.get("subsection"):
                    ref["subsection"] = headings[ref["anchor"]]
        save(stage / "lecture-slides.json", decks)
        manifest = read(stage / "source-manifest.json")
        paths = [SOURCE / "config.json", *sorted((SOURCE / "chapters").glob("*.json")),
                 SOURCE / "business-cases.json", SOURCE / "case-cards.json", knowledge]
        manifest["readabilityEdition"] = {"date": config["date"], "baseline": config["baseline"],
            "chapters": chapters, "build": "scripts/build-readable-lectures.py",
            "sources": [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for path in paths]}
        save(stage / "source-manifest.json", manifest)
        outputs = [*(chapter + ".json" for chapter in chapters), "concept-map.json", "catalog.json",
                   "source-manifest.json", "business-cases.json", "case-cards.json", "business-casebook.json", "lecture-slides.json"]
        for filename in outputs:
            shutil.copy2(stage / filename, CONTENT / filename)
    save(REVIEW / "build.json", {"chapters": chapters, "concepts": concept_report["counts"],
        "businessCases": len(changed_cases), "caseDiagrams": len(replacements), "outputs": outputs})
    print(json.dumps({"chapters": chapters, "businessCases": len(changed_cases), "publishedFiles": len(outputs)}))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Verify concept targets, return navigation and preservation of course content."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("concept_builder", ROOT / "scripts/build-concept-links.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def git_bytes(path, revision):
    result = subprocess.run(["git", "show", f"{revision}:{path}"], cwd=ROOT, capture_output=True)
    return result.stdout if result.returncode == 0 else None


def stable_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(source, content_dir, review_dir, baseline_ref, check_idempotence):
    knowledge = builder.read_json(source)
    chapters = knowledge["chapters"]
    registry = builder.read_json(content_dir / "concept-map.json")
    errors = []
    observations = {}
    if registry != {key: knowledge[key] for key in ("chapters", "concepts", "background")}:
        errors.append("Published registry differs from its authoritative source")
    manifest = builder.read_json(content_dir / "source-manifest.json")
    if manifest.get("conceptLinks", {}).get("sha256") != stable_hash(source):
        errors.append("Concept source hash differs from the source manifest")
    soups = {chapter: BeautifulSoup(builder.read_json(content_dir / (chapter + ".json"))["html"], "html.parser") for chapter in chapters}
    ids = {chapter: Counter(node["id"] for node in soup.find_all(id=True)) for chapter, soup in soups.items()}
    entries = {entry["id"]: ("course", entry) for entry in knowledge["concepts"]}
    entries.update({entry["id"]: ("background", entry) for entry in knowledge["background"]})
    for chapter, soup in soups.items():
        duplicates = [anchor for anchor, count in ids[chapter].items() if count > 1]
        if duplicates:
            errors.append(f"{chapter}: duplicate anchors {duplicates}")
        if soup.select("a a"):
            errors.append(f"{chapter}: nested links")
        if soup.select("pre .knowledge-link, code .knowledge-link, .math .knowledge-link, svg .knowledge-link, .citation .knowledge-link"):
            errors.append(f"{chapter}: a protected element contains a concept link")
        links = soup.select("a.knowledge-link")
        seen_in_unit = set()
        for link in links:
            concept_id = link.get("data-knowledge-id")
            kind = link.get("data-knowledge-kind")
            if concept_id not in entries:
                errors.append(f"{chapter}: unknown concept {concept_id}")
                continue
            expected_kind, entry = entries[concept_id]
            if kind != expected_kind:
                errors.append(f"{chapter}: wrong link kind {concept_id}")
            parts = urlsplit(link.get("href", "").lstrip("#"))
            target_chapter = parts.path.removeprefix("/chapter/")
            query = parse_qs(parts.query)
            target_anchor = query.get("anchor", [None])[0]
            source_chapter = query.get("from", [None])[0]
            reference = query.get("at", [None])[0]
            expected_chapter = entry["chapter"] if kind == "course" else chapter
            expected_anchor = entry["anchor"] if kind == "course" else "term-" + concept_id
            if (target_chapter, target_anchor) != (expected_chapter, expected_anchor):
                errors.append(f"{chapter}: wrong target for {concept_id}")
            if target_chapter not in ids or ids[target_chapter][target_anchor] != 1:
                errors.append(f"{chapter}: target is absent or ambiguous: {target_chapter}#{target_anchor}")
            if source_chapter != chapter or ids[chapter][reference] != 1:
                errors.append(f"{chapter}: return anchor is absent or ambiguous: {reference}")
            unit = link.find_parent(["p", "td", "li", "dd"])
            if unit is None or unit.get("id") != reference:
                errors.append(f"{chapter}: return anchor does not identify its reading unit: {concept_id}")
            unit_key = (id(unit), concept_id)
            if unit_key in seen_in_unit:
                errors.append(f"{chapter}: repeated concept link in one reading unit: {concept_id}")
            seen_in_unit.add(unit_key)
            if kind == "course" and chapters.index(target_chapter) > chapters.index(chapter):
                errors.append(f"{chapter}: forward reference to later lecture: {concept_id}")
            if not link.get("title") or entry["definition"] not in link["title"]:
                errors.append(f"{chapter}: missing concise explanation: {concept_id}")
        for entry in knowledge["background"]:
            if chapter in entry["chapters"]:
                dt = soup.find(id="term-" + entry["id"])
                if dt is None or dt.name != "dt" or dt.find_next_sibling("dd") is None:
                    errors.append(f"{chapter}: malformed background definition {entry['id']}")
        current = builder.read_json(content_dir / (chapter + ".json"))
        for item in current["toc"]:
            if ids[chapter][item["id"]] != 1:
                errors.append(f"{chapter}: TOC target absent/ambiguous: {item['id']}")
        baseline = git_bytes("dist/content/" + chapter + ".json", baseline_ref)
        if baseline:
            old_soup = BeautifulSoup(json.loads(baseline)["html"], "html.parser")
            builder.clean_generated(old_soup)
            before_protected = builder.protected(old_soup)
            if before_protected != builder.original_protected(soup):
                errors.append(f"{chapter}: code, formula, image or citation differs from {baseline_ref}")
            missing = set(node["id"] for node in old_soup.find_all(id=True)) - set(ids[chapter])
            if missing:
                errors.append(f"{chapter}: original anchors lost: {sorted(missing)}")
            expected_html = str(old_soup)
            for edit in knowledge.get("edits", []):
                if edit["chapter"] == chapter:
                    expected_html = expected_html.replace(edit["old"], edit["new"])
            original_current = BeautifulSoup(str(soup), "html.parser")
            builder.clean_generated(original_current)
            if str(BeautifulSoup(expected_html, "html.parser")) != str(original_current):
                errors.append(f"{chapter}: original content differs beyond declared text edits")
        observations[chapter] = {"links": len(links), "referenceAnchors": len(soup.select("[data-knowledge-reference]")), "targets": len(ids[chapter]), "protectedNodes": len(builder.protected(soup))}
    for concept in knowledge["concepts"]:
        if ids[concept["chapter"]][concept["anchor"]] != 1:
            errors.append(f"Missing unique definition: {concept['id']}")
    # User's concrete example is an acceptance condition, not just a smoke test.
    second = soups.get("02_enterprise_data_model")
    if second:
        opening = next((node for node in second.find_all("p") if node.get_text("", strip=True).startswith("数据模型规定")), None)
        if opening is None:
            errors.append("Second lecture opening data-model paragraph is missing")
        else:
            for term in ("业务对象", "关系约束", "事实粒度"):
                matching = [a for a in opening.select("a.knowledge-link") if a.get_text() == term]
                if len(matching) != 1 or not matching[0]["href"].startswith("#/chapter/01_intro?"):
                    errors.append(f"Second lecture opening must link {term} to first lecture")
    nl2sql = [entry for entry in knowledge["background"] if "NL2SQL" in [entry["term"], *entry.get("aliases", [])]]
    if not nl2sql:
        errors.append("NL2SQL has no background entry")
    else:
        count = sum(len(soup.select(f'a.knowledge-link[data-knowledge-id="{entry["id"]}"][data-knowledge-kind="background"]')) for soup in soups.values() for entry in nl2sql)
        if not count:
            errors.append("NL2SQL has no navigable background reference")
    build_report = builder.read_json(review_dir / "build.json")
    if build_report["counts"].get("forwardReferences"):
        errors.append("Build reports concepts used in first lecture but defined only in second")
    unchanged = []
    tracked = subprocess.run(["git", "ls-tree", "-r", "--name-only", baseline_ref, "dist/content"], cwd=ROOT, capture_output=True, text=True)
    if tracked.returncode:
        errors.append(f"Cannot inspect baseline {baseline_ref}")
    else:
        allowed = {"concept-map.json", "catalog.json", "source-manifest.json", *(chapter + ".json" for chapter in chapters)}
        for name in tracked.stdout.splitlines():
            relative = Path(name).relative_to("dist/content")
            if str(relative) in allowed:
                continue
            current = content_dir / relative
            baseline = git_bytes(name, baseline_ref)
            if not current.exists() or current.read_bytes() != baseline:
                errors.append(f"Out-of-scope content changed: {name}")
            else:
                unchanged.append(str(relative))
    idempotent = None
    if check_idempotence:
        import shutil
        with tempfile.TemporaryDirectory(prefix="bdm-concept-links-") as temp:
            temp = Path(temp)
            shutil.copytree(content_dir, temp / "content")
            before = {p.name: stable_hash(p) for p in (temp / "content").glob("*.json")}
            builder.build(source, temp / "content", temp / "review")
            after = {p.name: stable_hash(p) for p in (temp / "content").glob("*.json")}
            idempotent = before == after
            if not idempotent:
                errors.append("Rebuilding concept navigation changes published bytes")
    result = {"passed": not errors, "chapters": observations, "outOfScopeFilesUnchanged": len(unchanged), "idempotent": idempotent, "errors": errors}
    builder.write_json(review_dir / "verify.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "content-source/concept-links/knowledge.json")
    parser.add_argument("--content-dir", type=Path, default=ROOT / "dist/content")
    parser.add_argument("--review-dir", type=Path, default=ROOT / "review/concept-links-20261024")
    parser.add_argument("--baseline-ref", default="HEAD")
    parser.add_argument("--skip-idempotence", action="store_true")
    args = parser.parse_args()
    result = verify(args.source, args.content_dir, args.review_dir, args.baseline_ref, not args.skip_idempotence)
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()

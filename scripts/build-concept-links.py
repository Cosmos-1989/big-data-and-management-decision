#!/usr/bin/env python3
"""Build the course's explicit, source-controlled concept navigation.

Usage: python scripts/build-concept-links.py
The builder only rewrites the two chapters named in knowledge.json, their
catalogue entries, the concept registry and its source-manifest entry.  It can
also operate on a copied content directory for a non-destructive rehearsal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlencode

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "content-source/concept-links/knowledge.json"
EXCLUDED_TAGS = {"a", "code", "pre", "svg", "script", "style", "h1", "h2", "h3", "h4", "h5", "h6", "caption", "dt", "th"}
EXCLUDED_CLASSES = {"math", "citation", "statement-title", "knowledge-background", "case-source", "case-sources", "sources", "source-reference", "footnote-backref"}
PROTECTED_SELECTOR = "pre, .math, img, .citation"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalized(text):
    return " ".join(str(text).split())


def text_of(tag):
    return normalized(tag.get_text("", strip=False))


def parse(html):
    return BeautifulSoup(html, "html.parser")


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def protected(soup):
    """Canonical markup keeps every code/formula/figure/citation unchanged."""
    return [str(node) for node in soup.select(PROTECTED_SELECTOR)]


def original_protected(soup):
    """Ignore added teaching blocks when comparing original protected nodes."""
    original = parse(str(soup))
    clean_generated(original)
    return protected(original)


def clean_generated(soup):
    for node in list(soup.select("a.knowledge-link")):
        node.unwrap()
    for node in list(soup.select("[data-knowledge-block], .knowledge-background")):
        node.decompose()
    for node in list(soup.select('[data-knowledge-anchor="true"]')):
        node.decompose()
    for node in list(soup.select("[data-knowledge-reference]")):
        if str(node.get("id", "")).startswith("knowledge-ref-"):
            del node["id"]
        del node["data-knowledge-reference"]


def locate_text(soup, text):
    wanted = normalized(text)
    candidates = soup.find_all(["p", "td"])
    exact = [node for node in candidates if text_of(node) == wanted]
    found = exact or [node for node in candidates if text_of(node).startswith(wanted)]
    # A paragraph nested in a table cell can satisfy the same prefix twice.
    found = [node for node in found if not any(other is not node and other in node.descendants for other in found)]
    if len(found) != 1:
        raise ValueError(f"Expected one paragraph/cell beginning {text!r}; found {len(found)}")
    return found[0]


def locate_statement(soup, title):
    found = [node for node in soup.select(".statement-title") if text_of(node) == normalized(title)]
    if len(found) != 1:
        raise ValueError(f"Expected one statement {title!r}; found {len(found)}")
    return found[0].find_parent(class_="statement") or found[0].parent


def locate(soup, location):
    if "statement" in location:
        return locate_statement(soup, location["statement"])
    if "text" in location:
        return locate_text(soup, location["text"])
    if "heading" in location:
        node = soup.find(id=location["heading"])
        if node is None or node.name not in {"h2", "h3", "h4"}:
            raise ValueError(f"Missing definition heading: {location['heading']}")
        return node
    raise ValueError(f"Unknown definition location: {location}")


def add_blocks(soup, blocks):
    for block in blocks:
        placement = block["placement"]
        if "beforeAnchor" in placement or "afterAnchor" in placement:
            before = "beforeAnchor" in placement
            target = soup.find(id=placement.get("beforeAnchor", placement.get("afterAnchor")))
            if target is None:
                raise ValueError(f"Missing stable placement anchor: {placement}")
        elif "beforeHeading" in placement:
            target = soup.find(id=placement["beforeHeading"])
            if target is None or target.name not in {"h2", "h3", "h4"}:
                raise ValueError(f"Missing block heading: {placement['beforeHeading']}")
            before = True
        elif "afterStatement" in placement:
            target = locate_statement(soup, placement["afterStatement"])
            before = False
        elif "beforeText" in placement or "afterText" in placement:
            before = "beforeText" in placement
            target = locate_text(soup, placement.get("beforeText", placement.get("afterText")))
        else:
            raise ValueError(f"Unknown block placement: {placement}")
        wrapper = soup.new_tag("div", attrs={"class": "knowledge-supplement", "data-knowledge-block": block["id"]})
        fragment = parse(block["html"])
        if block.get("presentation") == "reference":
            section = fragment.select_one(".knowledge-foundations")
            if section is None:
                raise ValueError(f"Reference block has no definition section: {block['id']}")
            heading = section.find("h4")
            label = heading.get_text(strip=True) if heading else "相关概念"
            if heading:
                heading.decompose()
            for anchor in block.get("visibleConcepts", []):
                term = section.find(id=anchor)
                if term is None:
                    raise ValueError(f"Missing visible definition: {anchor}")
                group, definition = term.parent, term.find_next_sibling("dd")
                aside = soup.new_tag("aside", attrs={"class": "statement definition readable-definition", "id": anchor})
                title = soup.new_tag("div", attrs={"class": "statement-title"})
                title.string = "定义 · " + term.get_text()
                paragraph = soup.new_tag("p")
                for child in list(definition.contents):
                    paragraph.append(child)
                aside.extend([title, paragraph])
                wrapper.append(aside)
                group.decompose()
            note = soup.new_tag("details", attrs={"class": "knowledge-note"})
            summary = soup.new_tag("summary")
            summary.string = "术语释义 · " + label
            note.append(summary)
            for child in list(section.contents):
                note.append(child)
            fragment.clear()
            fragment.append(note)
        for child in list(fragment.contents):
            wrapper.append(child)
        if before:
            target.insert_before(wrapper)
        else:
            target.insert_after(wrapper)


def definition_scope(target):
    """Suppress the concept's own name only within its definition unit."""
    statement = target.find_parent(class_="statement")
    if statement is not None:
        return statement
    if target.name in {"aside", "p", "td", "li", "dd"}:
        return target
    if target.name in {"h2", "h3", "h4"}:
        return target.find_next_sibling(["p", "aside", "div", "table"])
    if target.parent and target.parent.name in {"p", "td", "aside", "li", "dd"}:
        return target.parent
    sibling = target.find_next_sibling()
    while sibling and sibling.name == "span" and not sibling.get_text(strip=True):
        sibling = sibling.find_next_sibling()
    if sibling and sibling.name in {"p", "aside"}:
        return sibling
    return target.parent


def install_definitions(soups, concepts):
    scopes = {}
    for concept in concepts:
        chapter, anchor = concept["chapter"], concept["anchor"]
        soup = soups[chapter]
        existing = soup.find_all(id=anchor)
        if len(existing) > 1:
            raise ValueError(f"Duplicate target {chapter}#{anchor}")
        if existing:
            target = existing[0]
        elif "location" in concept:
            target = locate(soup, concept["location"])
            node = soup.new_tag("span", attrs={"id": anchor, "data-knowledge-anchor": "true"})
            target.insert_before(node)
        else:
            raise ValueError(f"Missing target and location for concept {concept['id']}")
        scopes[concept["id"]] = definition_scope(target)
    return scopes


def add_background(soup, chapter, entries):
    entries = [entry for entry in entries if chapter in entry["chapters"]]
    if not entries:
        return
    section = soup.new_tag("section", attrs={"class": "knowledge-background", "aria-labelledby": "background-terms"})
    title = soup.new_tag("h2", attrs={"id": "background-terms"})
    title.string = "背景术语与名称释义"
    section.append(title)
    listing = soup.new_tag("dl")
    for entry in entries:
        dt = soup.new_tag("dt", attrs={"id": "term-" + entry["id"]})
        dt.string = entry["term"]
        dd = soup.new_tag("dd")
        paragraph = soup.new_tag("p")
        paragraph.string = entry["definition"]
        dd.append(paragraph)
        if entry.get("sourceUrl"):
            a = soup.new_tag("a", attrs={"href": entry["sourceUrl"], "target": "_blank", "rel": "noopener noreferrer", "class": "knowledge-source"})
            a.string = "资料来源"
            dd.append(a)
        listing.extend([dt, dd])
    reference = soup.new_tag("details", attrs={"class": "knowledge-glossary"})
    summary = soup.new_tag("summary")
    summary.string = "查看机构、产品与缩写释义"
    reference.extend([summary, listing])
    section.append(reference)
    soup.append(section)


def is_excluded(node):
    return any(parent.name in EXCLUDED_TAGS or EXCLUDED_CLASSES.intersection(parent.get("class", [])) for parent in node.parents if isinstance(parent, Tag))


def make_matcher(concepts, background):
    aliases = {}
    for kind, entries in (("course", concepts), ("background", background)):
        for entry in entries:
            for term in entry.get("linkAliases", [entry["term"], *entry.get("aliases", [])]):
                if not term:
                    raise ValueError(f"Empty alias in {entry['id']}")
                if term in aliases and aliases[term][1]["id"] != entry["id"]:
                    raise ValueError(f"Conflicting alias {term!r}")
                aliases[term] = (kind, entry)
    # Longest-first alternatives prevent short Chinese names inside compounds.
    ordered = sorted(aliases, key=lambda value: (-len(value), value))
    patterns = []
    for alias in ordered:
        left = r"(?<![A-Za-z0-9_])" if re.match(r"[A-Za-z0-9_]", alias) else ""
        right = r"(?![A-Za-z0-9_])" if re.search(r"[A-Za-z0-9_]$", alias) else ""
        # A one-character Chinese label (e.g. 键) is not the same term inside
        # an unrelated word such as 关键.  Longer registered aliases still
        # match normal compounds such as 主键 and 候选键.
        if len(alias) == 1 and "\u3400" <= alias <= "\u9fff":
            left, right = r"(?<![\u3400-\u9fff])", r"(?![\u3400-\u9fff])"
        # 单元组织/单元组成 contains two ordinary words, not the term 元组.
        if alias == "元组":
            left += r"(?<!单)"
        patterns.append(left + re.escape(alias) + right)
    return re.compile("|".join(patterns)) if patterns else re.compile(r"(?!x)x"), aliases


def link_chapter(soup, chapter, chapters, matcher, aliases, scopes):
    seen = {}
    counts = Counter()
    occurrences = Counter()
    forwards = []
    reference_number = 0
    for node in list(soup.find_all(string=True)):
        if not node.parent or is_excluded(node):
            continue
        matches = list(matcher.finditer(str(node)))
        if not matches:
            continue
        container = node.find_parent(["p", "td", "li", "dd"])
        if container is None:
            continue
        bucket = seen.setdefault(id(container), set())
        replacements = []
        last = 0
        for match in matches:
            kind, entry = aliases[match.group()]
            if kind == "background" and chapter not in entry["chapters"]:
                continue
            entry_id = entry["id"]
            occurrences[entry_id] += 1
            if kind == "course":
                own_scope = scopes.get(entry_id)
                if entry["chapter"] == chapter and own_scope is not None and (container is own_scope or own_scope in container.parents):
                    continue
                if chapters.index(entry["chapter"]) > chapters.index(chapter):
                    forwards.append({"concept": entry_id, "term": match.group(), "text": text_of(container)[:200]})
                    continue
                target_chapter, target_anchor = entry["chapter"], entry["anchor"]
                number = chapters.index(target_chapter) + 1
                title = f"第{number}讲定义：{entry['definition']}"
            else:
                target_chapter, target_anchor = chapter, "term-" + entry_id
                title = f"文末释义：{entry['definition']}"
            if entry_id in bucket:
                continue
            bucket.add(entry_id)
            if not container.get("id"):
                reference_number += 1
                reference_id = f"knowledge-ref-{reference_number:04d}"
                while soup.find(id=reference_id):
                    reference_number += 1
                    reference_id = f"knowledge-ref-{reference_number:04d}"
                container["id"] = reference_id
                container["data-knowledge-reference"] = "true"
            reference = container["id"]
            href = "#/chapter/" + target_chapter + "?" + urlencode({"anchor": target_anchor, "from": chapter, "at": reference})
            link = soup.new_tag("a", attrs={"href": href, "class": "knowledge-link", "data-knowledge-id": entry_id, "data-knowledge-kind": kind, "title": title})
            link.string = match.group()
            replacements.extend([NavigableString(str(node)[last:match.start()]), link])
            last = match.end()
            counts[entry_id] += 1
        if replacements:
            replacements.append(NavigableString(str(node)[last:]))
            node.replace_with(*replacements)
    return {"links": dict(sorted(counts.items())), "occurrences": dict(sorted(occurrences.items())), "forwardReferences": forwards, "referenceAnchors": reference_number}


def update_toc(chapter, soup):
    existing = {item["id"]: item for item in chapter["toc"] if not item.get("knowledgeLink")}
    result = []
    for node in soup.find_all(["h2", "h3"]):
        anchor = node.get("id")
        if anchor in existing:
            result.append(existing[anchor])
        elif anchor and (node.find_parent(attrs={"data-knowledge-block": True}) or node.find_parent(class_="knowledge-background")):
            result.append({"id": anchor, "title": text_of(node), "level": int(node.name[1]), "knowledgeLink": True})
    missing = set(existing).difference(item["id"] for item in result)
    if missing:
        raise ValueError(f"Existing TOC targets disappeared: {sorted(missing)}")
    chapter["toc"] = result


def build(source, content_dir, review_dir):
    knowledge = read_json(source)
    chapters = knowledge["chapters"]
    concepts, background = knowledge["concepts"], knowledge["background"]
    ids = [entry["id"] for entry in concepts + background]
    if len(ids) != len(set(ids)):
        raise ValueError("Concept and background ids must be unique")
    payloads, soups, safeguards = {}, {}, {}
    for chapter_id in chapters:
        payload = read_json(content_dir / (chapter_id + ".json"))
        soup = parse(payload["html"])
        clean_generated(soup)
        payloads[chapter_id], soups[chapter_id] = payload, soup
        safeguards[chapter_id] = {"protected": protected(soup), "ids": [node["id"] for node in soup.find_all(id=True)]}
    for edit in knowledge.get("edits", []):
        chapter_id = edit["chapter"]
        html = str(soups[chapter_id])
        old, new = edit["old"], edit["new"]
        if not old:
            raise ValueError("An edit must contain nonempty original text")
        if old in html:
            html = html.replace(old, new)
        elif new not in html:
            raise ValueError(f"Neither old nor replacement text found in {chapter_id}: {old[:80]}")
        soups[chapter_id] = parse(html)
    for chapter_id in chapters:
        add_blocks(soups[chapter_id], [block for block in knowledge.get("blocks", []) if block["chapter"] == chapter_id])
    scopes = install_definitions(soups, concepts)
    for chapter_id in chapters:
        add_background(soups[chapter_id], chapter_id, background)
    matcher, aliases = make_matcher(concepts, background)
    reports = {}
    pending_chapters = {}
    for chapter_id in chapters:
        soup = soups[chapter_id]
        reports[chapter_id] = link_chapter(soup, chapter_id, chapters, matcher, aliases, scopes)
        final_protected = original_protected(soup)
        if safeguards[chapter_id]["protected"] != final_protected:
            raise ValueError(f"Protected code/math/image/citation changed in {chapter_id}")
        final_ids = [node["id"] for node in soup.find_all(id=True)]
        if len(final_ids) != len(set(final_ids)):
            duplicates = [key for key, count in Counter(final_ids).items() if count > 1]
            raise ValueError(f"Duplicate anchors in {chapter_id}: {duplicates}")
        missing = set(safeguards[chapter_id]["ids"]) - set(final_ids)
        if missing:
            raise ValueError(f"Original anchors disappeared in {chapter_id}: {sorted(missing)}")
        reports[chapter_id]["protection"] = {"protectedNodes": len(final_protected), "protectedHash": digest("\n".join(final_protected)), "originalAnchorsPreserved": len(safeguards[chapter_id]["ids"])}
        payload = payloads[chapter_id]
        payload["html"] = str(soup)
        update_toc(payload, soup)
        pending_chapters[chapter_id] = payload
    registry = {"chapters": chapters, "concepts": concepts, "background": background}
    catalog_path = content_dir / "catalog.json"
    catalog = read_json(catalog_path)
    catalog["index"] = [item for item in catalog["index"] if not item.get("conceptLink")]
    for entry in concepts:
        catalog["index"].append({"term": entry["term"], "sort": entry["term"], "chapter": entry["chapter"], "anchor": entry["anchor"], "conceptLink": True})
    for entry in background:
        for chapter_id in entry["chapters"]:
            catalog["index"].append({"term": entry["term"], "sort": entry["term"], "chapter": chapter_id, "anchor": "term-" + entry["id"], "conceptLink": True})
    manifest_path = content_dir / "source-manifest.json"
    manifest = read_json(manifest_path)
    try:
        source_name = str(source.resolve().relative_to(ROOT))
    except ValueError:
        source_name = str(source)
    manifest["conceptLinks"] = {"source": source_name, "sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "build": "scripts/build-concept-links.py", "chapters": chapters, "concepts": len(concepts), "background": len(background)}
    all_counts = Counter()
    for report in reports.values():
        all_counts.update(report["links"])
    report = {"chapters": reports, "counts": {"concepts": len(concepts), "background": len(background), "links": sum(all_counts.values()), "supplementBlocks": len(knowledge.get("blocks", [])), "forwardReferences": sum(len(value["forwardReferences"]) for value in reports.values())}, "unusedDefinitions": [entry["id"] for entry in concepts + background if not all_counts[entry["id"]]]}
    # Resolve and validate every target before changing any published chapter.
    for chapter_id, payload in pending_chapters.items():
        write_json(content_dir / (chapter_id + ".json"), payload)
    write_json(content_dir / "concept-map.json", registry)
    write_json(catalog_path, catalog)
    write_json(manifest_path, manifest)
    write_json(review_dir / "build.json", report)
    print(json.dumps(report["counts"], ensure_ascii=False))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--content-dir", type=Path, default=ROOT / "dist/content")
    parser.add_argument("--review-dir", type=Path, default=ROOT / "review/concept-links-20261024")
    args = parser.parse_args()
    build(args.source, args.content_dir, args.review_dir)


if __name__ == "__main__":
    main()

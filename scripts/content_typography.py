"""Normalize Chinese prose spacing and accessible endnotes after conversion.

Only visible prose text is normalized. Math, source code, SVG labels, citations,
URLs and HTML attributes retain their exact contents.
"""
from __future__ import annotations

import re
from urllib.parse import parse_qs, unquote

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

HAN = r"\u3400-\u9fff\uf900-\ufaff"
CJK_PUNCTUATION = "，。；：！？、（）《》【】「」『』"
GAPS = r"[\s\u2000-\u200b\u202f\u205f\u2060\u3000\ufeff]+"
INNER_GAP = re.compile(rf"(?<=[{HAN}]){GAPS}(?=[{HAN}])")
PUNCT_GAP = re.compile(
    rf"(?<=[{HAN}{CJK_PUNCTUATION}]){GAPS}(?=[{CJK_PUNCTUATION}])|"
    rf"(?<=[{CJK_PUNCTUATION}]){GAPS}(?=[{HAN}])"
)
PROTECTED_TAGS = {"pre", "code", "kbd", "samp", "script", "style", "svg", "math", "textarea"}
PROTECTED_CLASSES = {"math", "katex", "citation", "csl-entry"}
INLINE_TAGS = {"a", "em", "strong", "span", "b", "i", "u", "s", "sup", "sub", "abbr", "small", "mark"}


def normalize_text(value: str) -> str:
    """Remove spurious CJK gaps; English words and mixed-script spacing survive."""
    return PUNCT_GAP.sub("", INNER_GAP.sub("", value))


def protected(node: NavigableString | Tag) -> bool:
    chain = ([node] if isinstance(node, Tag) else []) + list(node.parents)
    return any(isinstance(tag, Tag) and (
        tag.name in PROTECTED_TAGS or PROTECTED_CLASSES.intersection(tag.get("class", []))
    ) for tag in chain)


def prose_parent(node: NavigableString) -> Tag | None:
    parent = node.parent
    while isinstance(parent, Tag) and parent.name in INLINE_TAGS:
        parent = parent.parent
    return parent


def adjacent_character(node: NavigableString, before: bool) -> str:
    """Look across inline markup, never across a block or a protected node."""
    boundary = prose_parent(node)
    sequence = node.previous_elements if before else node.next_elements
    for item in sequence:
        if item is boundary:
            return ""
        if isinstance(item, Tag):
            if protected(item) or item.name == "br":
                return ""
            if item.name not in INLINE_TAGS and item is not node.parent:
                return ""
            continue
        if not isinstance(item, NavigableString) or isinstance(item, Comment):
            continue
        if prose_parent(item) is not boundary or protected(item):
            return ""
        value = str(item).strip()
        if value:
            return value[-1] if before else value[0]
    return ""


def cjk_join(left: str, right: str) -> bool:
    return bool(left and right and re.fullmatch(
        rf"[{HAN}{CJK_PUNCTUATION}]{{2}}", left + right))


def normalize_soup(soup: BeautifulSoup) -> int:
    changed = 0
    for node in list(soup.find_all(string=True)):
        if isinstance(node, Comment) or protected(node):
            continue
        value = str(node)
        normalized = normalize_text(value)
        if re.match(r"^\s", normalized):
            first = normalized.lstrip()
            if first and cjk_join(adjacent_character(node, True), first[0]):
                normalized = normalized.lstrip()
        if re.search(r"\s$", normalized):
            last = normalized.rstrip()
            if last and cjk_join(last[-1], adjacent_character(node, False)):
                normalized = normalized.rstrip()
        if normalized.strip() == "" and cjk_join(
                adjacent_character(node, True), adjacent_character(node, False)):
            normalized = ""
        if normalized != value:
            node.replace_with(NavigableString(normalized))
            changed += 1
    return changed


def anchor_id(href: str) -> str:
    if href.startswith("#/chapter/"):
        return parse_qs(href.partition("?")[2]).get("anchor", [""])[0]
    return unquote(href.lstrip("#"))


def normalize_notes(soup: BeautifulSoup, slug: str) -> int:
    sections = soup.select("section.footnotes, div.footnote")
    for section in sections:
        section["role"] = "doc-endnotes"
        section["class"] = sorted(set(section.get("class", [])) | {"course-notes"})
        section["aria-labelledby"] = slug + "-notes"
        for separator in section.find_all("hr", recursive=False):
            separator.decompose()
        if not section.find(id=slug + "-notes"):
            heading = soup.new_tag("h2", id=slug + "-notes")
            heading.string = "注释"
            section.insert(0, heading)
        for item in section.select("ol > li[id]"):
            item["role"] = "doc-endnote"
    references = soup.select("a.footnote-ref, a[role='doc-noteref']")
    for ref in references:
        number = ref.get_text(strip=True)
        ref["role"] = "doc-noteref"
        ref["aria-label"] = "阅读注释 " + number
        target = soup.find(id=anchor_id(ref.get("href", "")))
        if target:
            preview = target.get_text(" ", strip=True).replace("↩︎", "").replace("↩", "").strip()
            ref["title"] = normalize_text(preview)
    for ref in soup.select("a.footnote-back, a.footnote-backref, a[role='doc-backlink']"):
        ref["role"] = "doc-backlink"
        ref["aria-label"] = "返回正文中的注释位置"
        ref["title"] = "返回正文"
    for link in soup.select("a.footnote-ref, a.footnote-back, a.footnote-backref, a[role='doc-noteref'], a[role='doc-backlink']"):
        href = link.get("href", "")
        if href.startswith("#") and not href.startswith("#/"):
            link["href"] = "#/chapter/" + slug + "?anchor=" + href[1:]
    return len(references)


def normalize_document(document: dict) -> tuple[dict, dict]:
    soup = BeautifulSoup(document["html"], "html.parser")
    changes = normalize_soup(soup)
    notes = normalize_notes(soup, document["id"])
    # Removing a generated <hr> can leave adjacent whitespace-only nodes.
    # Canonicalize those nodes so repeated content builds are idempotent.
    soup.smooth()
    for node in list(soup.find_all(string=True)):
        if not isinstance(node, Comment) and not protected(node) and not str(node).strip() and "\n" in str(node):
            node.replace_with(NavigableString("\n"))
    document["html"] = str(soup)
    document["title"] = normalize_text(document["title"])
    for item in document.get("toc", []):
        item["title"] = normalize_text(item["title"])
    if notes and not any(item["id"] == document["id"] + "-notes" for item in document.get("toc", [])):
        document.setdefault("toc", []).append({"id": document["id"] + "-notes", "title": "注释", "level": 2})
    return document, {"document": document["id"], "changedTextNodes": changes, "footnoteReferences": notes}

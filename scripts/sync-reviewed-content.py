"""Rebuild source prose without discarding reviewed programs or chapter anchors.

The ordinary exporter is intentionally broad. This transaction stages its output,
checks the protected teaching material, and retains the browser workbench's
reviewed code annotations. Run build:agent and normalize-content.py afterwards.
"""
from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from bs4 import BeautifulSoup

from content_typography import normalize_document

SITE = Path(__file__).resolve().parents[1]
DIST = SITE / "dist"


def read(path):
    return json.loads(path.read_text())


def sequence_preserved(before, after):
    remaining = iter(after)
    return all(any(candidate == item for candidate in remaining) for item in before)


def protected(soup):
    return {
        "math": [item.get_text() for item in soup.select(".math")],
        "citations": [item["href"] for item in soup.select('a[href*="/bibliography?anchor=ref-"]')],
        "images": [item["src"] for item in soup.find_all("img")],
    }


def merge_document(old, new):
    old_soup = BeautifulSoup(old["html"], "html.parser")
    new_soup = BeautifulSoup(new["html"], "html.parser")
    old_protected, new_protected = protected(old_soup), protected(new_soup)
    for kind in ["math", "citations"]:
        if not sequence_preserved(old_protected[kind], new_protected[kind]):
            raise ValueError(f"{old['id']}: original {kind} changed or lost")
    if old_protected["images"] != new_protected["images"]:
        raise ValueError(f"{old['id']}: source images changed")
    old_code, new_code = old_soup.find_all("pre"), new_soup.find_all("pre")
    if len(old_code) != len(new_code):
        raise ValueError(f"{old['id']}: number of source code blocks changed")
    for before, after in zip(old_code, new_code):
        after.replace_with(before)
    # Preserve public/slide links even when an unlabelled heading is rephrased.
    old_headings = [item for item in old_soup.find_all(["h2", "h3"]) if not item.find_parent(class_=["course-notes", "footnote", "footnotes", "agent-connection"])]
    new_headings = [item for item in new_soup.find_all(["h2", "h3"]) if not item.find_parent(class_=["course-notes", "footnote", "footnotes", "agent-connection"])]
    if len(old_headings) != len(new_headings):
        raise ValueError(f"{old['id']}: chapter structure changed ({len(old_headings)} -> {len(new_headings)})")
    id_changes = {}
    for before, after in zip(old_headings, new_headings):
        if before.get("id") and after.get("id") != before["id"]:
            id_changes[after.get("id")] = before["id"]
            after["id"] = before["id"]
    for item in new.get("toc", []):
        item["id"] = id_changes.get(item["id"], item["id"])
    new["html"] = str(new_soup)
    # All former source-labelled destinations, including equation labels, stay valid.
    old_ids = {item["id"] for item in old_soup.find_all(id=True) if not item.find_parent(class_="agent-connection")}
    missing = old_ids - {item["id"] for item in new_soup.find_all(id=True)}
    if missing:
        raise ValueError(f"{old['id']}: former anchors missing: {sorted(missing)}")
    new, normalization = normalize_document(new)
    return new, {"id": old["id"], "protected": {key: len(value) for key, value in old_protected.items()},
                 "codeBlocksPreserved": len(old_code), "anchorsPreserved": len(old_ids), **normalization}


old_catalog = read(DIST / "content/catalog.json")
reports = []
updates = {}
with tempfile.TemporaryDirectory(prefix="bdm-reviewed-") as folder:
    stage = Path(folder)
    shutil.copytree(DIST / "figures", stage / "figures")
    env = {**os.environ, "BDM_SITE_OUTPUT": str(stage)}
    for script in ["build_content.py", "enrich_content.py"]:
        subprocess.run([sys.executable, str(SITE / "scripts" / script)], check=True, env=env)
    new_catalog = read(stage / "content/catalog.json")
    for path in sorted((stage / "content").glob("*.json")):
        new = read(path)
        if not isinstance(new, dict) or "html" not in new:
            continue
        # Its own source/diagram exporter preserves the Agent chapter's section IDs.
        if path.stem in {"14_ai_agent", "final_project"}:
            continue
        old_path = DIST / "content" / path.name
        if not old_path.exists():
            raise ValueError(f"Unexpected new document {path.name}")
        old = read(old_path)
        if path.stem == "bibliography":
            old_soup = BeautifulSoup(old["html"], "html.parser")
            new_soup = BeautifulSoup(new["html"], "html.parser")
            if [item["id"] for item in old_soup.select(".csl-entry")] != [item["id"] for item in new_soup.select(".csl-entry")]:
                raise ValueError("Bibliography source set or ordering changed")
            updates[old_path] = new
            continue
        merged, report = merge_document(old, new)
        updates[old_path] = merged
        reports.append(report)
    for key in ["chapters", "extras"]:
        generated = {item["id"]: item for item in new_catalog[key]}
        old_catalog[key] = [{**item, **generated.get(item["id"], {})} for item in old_catalog[key]]
    for key in ["sourceHash", "index", "bibliographyCount"]:
        old_catalog[key] = new_catalog[key]
    # Only commit the staged prose after every protected-content check has passed.
    for path, document in updates.items():
        path.write_text(json.dumps(document, ensure_ascii=False) + "\n")
    (DIST / "content/catalog.json").write_text(json.dumps(old_catalog, ensure_ascii=False, indent=2) + "\n")
    shutil.copy2(stage / "content/source-manifest.json", DIST / "content/source-manifest.json")
    for source in (stage / "downloads/source").rglob("*") if (stage / "downloads/source").exists() else []:
        if source.is_file():
            target = DIST / "downloads/source" / source.relative_to(stage / "downloads/source")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
target = SITE / "review/language-20261017/web-sync.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(reports, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"documents": len(updates), "protectedCodeBlocks": sum(item["codeBlocksPreserved"] for item in reports),
                  "protectedMath": sum(item["protected"]["math"] for item in reports)}, ensure_ascii=False))

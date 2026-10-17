"""Render the course's Markdown notes, or normalize a generated document JSON."""
import json
import sys

import markdown

from content_typography import normalize_document

source = sys.stdin.read()
if "--normalize-document" in sys.argv:
    document, _ = normalize_document(json.loads(source))
    sys.stdout.write(json.dumps(document, ensure_ascii=False))
else:
    sys.stdout.write(markdown.markdown(source, extensions=["tables", "fenced_code", "footnotes"],
        extension_configs={"footnotes": {"BACKLINK_TITLE": "返回正文注释 {}", "USE_DEFINITION_ORDER": False}}))

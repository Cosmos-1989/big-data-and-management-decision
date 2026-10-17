"""Apply the shared prose typography and endnote rules to generated content."""
import json
import os
from pathlib import Path

from content_typography import normalize_document

SITE = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("BDM_SITE_OUTPUT", SITE / "dist"))
reports = []
for path in sorted((OUT / "content").glob("*.json")):
    document = json.loads(path.read_text())
    if not isinstance(document, dict) or not document.get("html"):
        continue
    document, report = normalize_document(document)
    path.write_text(json.dumps(document, ensure_ascii=False) + "\n")
    reports.append(report)
target = SITE / "review/language-20261017/typography.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(reports, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"documents": len(reports),
                  "changedTextNodes": sum(item["changedTextNodes"] for item in reports),
                  "footnoteReferences": sum(item["footnoteReferences"] for item in reports)}))

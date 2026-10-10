"""Build portable Song-style web fonts for the current lecture slides.

Usage: PYTHONPATH=<fonttools-and-brotli> python3 scripts/subset-slide-fonts.py
       <directory-containing-official-SourceHanSerifCN-fonts-and-LICENSE.txt>
The original fonts stay outside the repository; only licensed WOFF2 subsets ship.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys

from fontTools import subset
from fontTools.ttLib import TTFont

root = Path(__file__).resolve().parents[1]
source = Path(sys.argv[1])
target = root / "dist/assets/fonts"
target.mkdir(parents=True, exist_ok=True)
text = (root / "dist/content/lecture-slides.json").read_text()
text += (root / "dist/slides.js").read_text()
text += (root / "dist/slide-diagrams.js").read_text()
unicodes = set(map(ord, text)) | set(range(32, 127))
required_cjk = {u for u in unicodes if 0x3400 <= u <= 0x9fff}
manifest = {"family": "BDM Course Song", "upstream": "https://github.com/adobe-fonts/source-han-serif", "license": "SIL OFL 1.1", "contentSha256": sha256((root / "dist/content/lecture-slides.json").read_bytes()).hexdigest(), "requiredCjkCharacters": len(required_cjk), "fonts": []}
rules = []
for style, weight in [("Regular", 400), ("Bold", 700)]:
    path = source / f"SourceHanSerifCN-{style}.otf"
    font = TTFont(path)
    missing = required_cjk - set(font.getBestCmap())
    assert not missing, f"Missing Chinese characters: {''.join(map(chr, sorted(missing)))}"
    options = subset.Options()
    options.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14, 16, 17]
    options.name_legacy = True
    options.name_languages = [0x409]
    options.recalc_timestamp = False
    sub = subset.Subsetter(options=options)
    sub.populate(unicodes=unicodes)
    sub.subset(font)
    # The OFL reserves "Source". Rename the modified subset, including CFF names.
    names = {1: "BDM Course Song", 2: style, 3: f"BDM-CourseSong-{style}", 4: f"BDM Course Song {style}", 6: f"BDMCourseSong-{style}", 16: "BDM Course Song", 17: style}
    for record in font["name"].names:
        if record.nameID in names:
            record.string = names[record.nameID].encode(record.getEncoding())
    if "CFF " in font:
        cff = font["CFF "].cff
        cff.fontNames = [f"BDMCourseSong-{style}"]
        for top in cff.topDictIndex:
            top.FamilyName = "BDM Course Song"
            top.FullName = f"BDM Course Song {style}"
    font.flavor = "woff2"
    output = target / f"course-song-{style.lower()}.woff2"
    font.save(output)
    digest = sha256(output.read_bytes()).hexdigest()
    loaded = TTFont(output)
    assert required_cjk <= set(loaded.getBestCmap())
    manifest["fonts"].append({"weight": weight, "file": output.name, "bytes": output.stat().st_size, "sha256": digest, "sourceSha256": sha256(path.read_bytes()).hexdigest(), "version": loaded["name"].getDebugName(5), "missingCjk": []})
    rules.append(f'@font-face{{font-family:"BDM Course Song";font-style:normal;font-weight:{weight};font-display:swap;src:url("./{output.name}?v={digest[:12]}") format("woff2")}}')
(target / "course-song.css").write_text("\n".join(rules) + "\n")
(target / "OFL.txt").write_bytes((source / "LICENSE.txt").read_bytes())
(target / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
(target / "README.md").write_text("# Course Song web fonts\n\nSong-style glyphs are derived from Adobe Source Han Serif CN, under SIL OFL 1.1.\nThe modified subsets are renamed BDM Course Song to respect the reserved name.\nCopyright and license notices remain in the fonts and OFL.txt.\n\nOfficial source: https://github.com/adobe-fonts/source-han-serif/tree/release/SubsetOTF/CN\n\nRegenerate after changing lecture text using scripts/subset-slide-fonts.py.\nThe manifest records source hashes, output hashes, and Chinese character coverage.\n")
print(json.dumps({"fonts": len(manifest["fonts"]), "cjkCharacters": len(required_cjk), "bytes": sum(x["bytes"] for x in manifest["fonts"]), "missingCjk": []}))

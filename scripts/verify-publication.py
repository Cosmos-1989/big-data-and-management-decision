"""Compare published course assets to the reviewed local bytes over HTTPS."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
revision = sys.argv[1]
base = 'https://cosmos-1989.github.io/big-data-and-management-decision/'
paths = ['index.html', 'app.js', 'slides.js', 'slides-refined.css', 'slide-diagrams.js',
         'business-cases.js', 'business-cases.css', 'content/catalog.json',
         'content/lecture-slides.json', 'content/business-cases.json',
         'content/business-casebook.json', 'content/lecture-terms.json',
         'content/source-manifest.json', 'assets/fonts/course-song.css',
         'assets/fonts/manifest.json', 'assets/fonts/course-song-regular.woff2',
         'assets/fonts/course-song-bold.woff2', 'downloads/business-casebook.md']

def check(path):
    local = (root / 'dist' / path).read_bytes()
    result = subprocess.run(['curl', '--fail', '--silent', '--show-error', '--location',
                             '--max-time', '45', '--retry', '2', base + path + '?v=' + revision],
                            capture_output=True, check=True)
    return {'path': path, 'bytes': len(result.stdout), 'localSha256': sha256(local).hexdigest(),
            'publicSha256': sha256(result.stdout).hexdigest(), 'match': local == result.stdout}

with ThreadPoolExecutor(max_workers=4) as pool:
    records = list(pool.map(check, paths))
report = {'base': base, 'pagesRevision': revision, 'tlsVerification': True, 'files': records,
          'allMatched': all(r['match'] for r in records)}
out = root / 'review/teaching-20261017/public-files.json'
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'checkedFiles': len(records), 'allMatched': report['allMatched'],
                  'mismatched': [r['path'] for r in records if not r['match']]}))
if not report['allMatched']:
    raise SystemExit(1)

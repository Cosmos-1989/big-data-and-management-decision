"""Check canonical-domain redirects using normal certificate validation."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent
cases = [
    ('https://datasci.biz/', 'https://datasci.biz/', False),
    ('http://datasci.biz/', 'https://datasci.biz/', True),
    ('https://www.datasci.biz/', 'https://datasci.biz/', True),
    ('http://www.datasci.biz/', 'https://datasci.biz/', True),
    ('https://www.datasci.biz/content/catalog.json?wwwcheck=1',
     'https://datasci.biz/content/catalog.json?wwwcheck=1', True),
]


def check(case):
    url, canonical, redirect_required = case
    command = ['curl', '--silent', '--show-error', '--fail', '--head',
               '--location', '--max-time', '30', '--output', '/dev/null',
               '--write-out', '%{json}']
    # Public DoH confirms this origin; pin HTTP to avoid local fake-IP DNS caching.
    if url.startswith('http:'):
        host = url.split('/')[2]
        command += ['--resolve', f'{host}:80:185.199.108.153']
    result = subprocess.run(command + [url], capture_output=True, text=True)
    stats = json.loads(result.stdout) if result.stdout else {}
    record = {'url': url, 'expectedCanonical': canonical,
              'exitCode': result.returncode, 'error': result.stderr.strip()}
    for key in ['http_code', 'url_effective', 'num_redirects', 'ssl_verify_result']:
        record[key] = stats.get(key)
    record['passed'] = (result.returncode == 0
                        and record['http_code'] == 200
                        and record['url_effective'] == canonical
                        and record['ssl_verify_result'] == 0
                        and (not redirect_required or record['num_redirects'] >= 1))
    return record


with ThreadPoolExecutor(max_workers=4) as pool:
    records = list(pool.map(check, cases))
report = {'checkedAtUtc': datetime.now(timezone.utc).isoformat(),
          'tlsVerification': True, 'checks': records,
          'allPassed': all(r['passed'] for r in records)}
(root / 'www-final-check.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
if not report['allPassed']:
    raise SystemExit(1)

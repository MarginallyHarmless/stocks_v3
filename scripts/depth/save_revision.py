"""Register a validated revision and point the registry, visuals manifest and key-stats at it.
usage: python3 scripts/depth/save_revision.py OUT_DIR/NEW_ID.json   (from the repository root)
Then run scripts/render_reports.py and scripts/build_index.py."""
import json, subprocess, sys
from pathlib import Path
rev = json.load(open(sys.argv[1])); new_id = rev['report_id']; base_id = rev['editorial_revision_of']
reg_path = Path('stock-analysis-registry.json'); reg = json.loads(reg_path.read_text())
company = next(c for c in reg['companies'].values() if any(r['report_id'] == base_id for r in c['reports']))
archive = Path(company['archive_path'])
base_html = next(r['html_path'] for r in company['reports'] if r['report_id'] == base_id)
import re
suffix = re.search(r'-r\d+$', new_id).group(0)
new_html = re.sub(r'-r\d+\.html$', '.html', base_html).replace('.html', suffix + '.html')
print('report path', new_html)
card = Path(sys.argv[1]).with_suffix('.card.json'); card.write_text(json.dumps(dict(company['card'], report_id=new_id), ensure_ascii=False))
stock = 'skills/stock-analysis/scripts/stock.py'
def run(*cmd):
    r = subprocess.run([sys.executable, stock, *cmd], capture_output=True, text=True)
    print(r.stdout.strip()[-400:], r.stderr.strip()[-400:]);  r.returncode and sys.exit('failed: ' + ' '.join(cmd[:1]))
if new_id not in json.loads(archive.read_text())['snapshots']:
    run('register', sys.argv[1], '--archive', str(archive), '--expected-hash', company['archive_sha256'])
Path(new_html).touch()
run('catalog', str(archive), '--registry', str(reg_path), '--repo-root', '.', '--repository', 'MarginallyHarmless/stocks_v3', '--report-path', new_html, '--card', str(card))
for p in (Path('research/visuals/manifest.json'), Path('research/key-stats.json')):
    m = json.loads(p.read_text())
    if base_id in m and new_id not in m:
        m[new_id] = m[base_id]; p.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n'); print('mapped', new_id, 'in', p)

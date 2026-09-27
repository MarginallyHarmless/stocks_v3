#!/usr/bin/env python3
"""Validate saved research and regenerate the repository index."""
import re
import html as html_module
from datetime import datetime
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/stock-analysis/scripts"))
from archive import verify_archive
from company_index import render_index, repository_file
from model import digest, load, need

registry = load(ROOT / "stock-analysis-registry.json")
for identity, company in registry["companies"].items():
    archive = verify_archive(load(repository_file(ROOT, company["archive_path"])))
    need(archive["identity"] == identity, "Registry/archive identity mismatch")
    need(digest(archive) == company["archive_sha256"], "Registry/archive hash mismatch")
    for report in company["reports"]:
        need(report["report_id"] in archive["snapshots"], "Report missing from archive")
        repository_file(ROOT, report["html_path"])
index = ROOT / "index.html"
html = render_index(registry, repo_root=ROOT)
market_path = ROOT / 'market-sweep-registry.json'
if market_path.exists():
    market = load(market_path)
    reports = sorted(market['reports'], key=lambda r: datetime.fromisoformat(r['cutoff']), reverse=True)
    need(len({r['run_id'] for r in reports}) == len(reports), 'Duplicate market report')
    need(market['latest_run_id'] in {r['run_id'] for r in reports}, 'Latest market report missing')
    esc = html_module.escape
    def bilingual(en, ro):
        return f'<span class="reports-en">{esc(en)}</span><span class="reports-ro">{esc(ro)}</span>'
    cards = []
    for report in reports:
        repository_file(ROOT, report['html_path'])
        data = load(repository_file(ROOT, report['data_path']))
        need(data['run_id'] == report['run_id'], 'Market report identity mismatch')
        link = esc(report['html_path'], quote=True)
        day = esc(report['cutoff'][:10])
        start = esc(report['window_start'][:10])
        latest = report['run_id'] == market['latest_run_id']
        badge = '<span class="report-latest">' + bilingual('Latest', 'Cel mai recent') + '</span>' if latest else ''
        counts = bilingual(f"{report['company_count']} companies · {report['question_count']} saved questions",
                           f"{report['company_count']} companii · {report['question_count']} întrebări salvate")
        cards.append(f'''<article class="landscape-card">
<div class="landscape-card-meta"><span>{bilingual('Market landscape', 'Contextul pieței')}</span>{badge}<time datetime="{esc(report['cutoff'], quote=True)}">{day}</time></div>
<h3><a href="{link}">{bilingual(data['title']['en'], data['title']['ro'])}<span aria-hidden="true"> ↗</span></a></h3>
<p class="landscape-summary">{bilingual(data['summary']['en'], data['summary']['ro'])}</p>
<div class="landscape-card-foot"><span>{counts}</span><span>{bilingual('Review window', 'Interval analizat')}: {start} → {day}</span></div>
</article>''')
    section = f'''<section id="reports" class="landscape-reports" aria-labelledby="reports-title">
<div class="reports-heading"><div><h2 id="reports-title">{bilingual('Reports', 'Rapoarte')}</h2><p>{bilingual('Market news, macroeconomics and geopolitics across the companies we follow.', 'Știri de piață, macroeconomie și geopolitică pentru companiile urmărite.')}</p></div><span class="reports-cadence">{bilingual('Updated on request', 'Actualizate la cerere')}</span></div>
<div class="landscape-report-list">{''.join(cards)}</div>
</section>'''
    css = '<style>' + (ROOT / 'assets/market-index.css').read_text() + '</style>'
    marker = '<div class="index-layout">'
    need(marker in html, 'Company index layout marker missing')
    html = html.replace('</head>', css + '</head>').replace(marker, section + marker, 1)
stamp = re.compile(r'"generated_at": "[^"]*"')
# Rebuilding unchanged research keeps the file, so the saved-at date only moves with content.
if not (index.exists() and stamp.sub("", index.read_text(encoding="utf-8")) == stamp.sub("", html)):
    index.write_text(html, encoding="utf-8")
print(f"Built index for {len(registry['companies'])} companies.")

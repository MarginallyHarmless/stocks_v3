#!/usr/bin/env python3
"""Regenerate report presentation from unchanged, verified archive snapshots."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/stock-analysis/scripts'))
from archive import verify_archive
from company_index import repository_file
from model import load
from render import render

registry = load(ROOT / 'stock-analysis-registry.json')
manifest_path = ROOT / 'research/visuals/manifest.json'
manifest = load(manifest_path) if manifest_path.exists() else {}
for company in registry['companies'].values():
    archive = verify_archive(load(repository_file(ROOT, company['archive_path'])))
    links = {r['report_id']: Path(r['html_path']).name for r in company['reports']}
    for report in company['reports']:
        data = archive['snapshots'][report['report_id']]['research']
        parent = data.get('parent_report_id')
        baseline = archive['snapshots'][parent]['research'] if parent else None
        entry = manifest.get(data['report_id'])
        visual_data = load(ROOT / entry['path'])[entry['key']] if entry else None
        path = repository_file(ROOT, report['html_path'])
        path.write_text(render(data, baseline=baseline, archive=archive, visual_data=visual_data, report_links=links), encoding='utf-8')
        print('Rendered', report['html_path'])

"""Readable dump of a saved snapshot (sections + full evidence ledger) for authoring a depth revision.
usage: python3 scripts/depth/dump_report.py REPORT_ID > dump.txt   (from the repository root)"""
import json, sys
sys.path.insert(0, 'skills/stock-analysis/scripts')
from model import format_number
reg = json.load(open('stock-analysis-registry.json'))
rid = sys.argv[1]
for c in reg['companies'].values():
    for r in c['reports']:
        if r['report_id'] == rid:
            d = json.load(open(c['archive_path']))['snapshots'][rid]['research']
src = {s['id']: s for s in d['sources']}
print('REPORT', rid, 'cutoff', d['cutoff'], '| company', d['company']['name'])
print('SUMMARY:', ' || '.join(c['text']['en'] for c in d['summary']))
print('BUSINESS:', d['business_assessment']['text']['en']); print('PRICE:', d['price_assessment']['text']['en'])
print('GAPS:', d['evidence_gaps']['en'])
for s in d['sections']:
    g = s.get('guide') or {}
    print('\n=== SECTION', s['id'], '|', s['question']['en'])
    for c in g.get('claims', []): print('  GUIDE', c['type'], c['evidence_refs'], '::', c['text']['en'])
    for m in g.get('metrics', []): print('  GMETRIC', m['evidence_ref'], '::', m['meaning']['text']['en'])
    if g: print('  WHY', g['why_it_matters']['evidence_refs'], '::', g['why_it_matters']['text']['en'])
    for c in s['claims']: print('  CLAIM', c['type'], c['evidence_refs'], '::', c['text']['en'])
    print('  METRICS', s.get('metrics'))
    print('  CAVEAT ::', s['caveat']['en'])
    if s.get('lesson'): print('  LESSON ::', {k: v['en'] for k, v in s['lesson'].items()})
print('\n=== EVIDENCE')
for e in d['evidence']:
    val = format_number(e, 'en') if 'value' in e else 'UNAVAILABLE: ' + str(e.get('state', {}).get('en', e.get('state')))
    p = e.get('period', {})
    s = src.get(e.get('source_id'), {})
    print(f"- {e['id']} [{e['kind']}] {e['label']['en'] if isinstance(e['label'],dict) else e['label']} = {val} | {p.get('label','')} {'FORECAST' if p.get('forecast') else ''} | {e.get('basis','')} | def: {e['definition'][:160]}"
          + (f" | src: {s.get('title',{}).get('en', s.get('title')) if isinstance(s.get('title'),dict) else s.get('title')}" if s else '')
          + (f" | op: {e.get('operation')} {e.get('inputs')}" if e.get('inputs') else '')
          + (f" | loc: {e['extraction']['locator']['en'] if isinstance(e['extraction']['locator'],dict) else e['extraction']['locator']}" if e.get('extraction') else ''))

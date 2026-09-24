"""Review sheet: each new claim/lesson (EN, then RO) with the cited evidence values underneath.
usage: python3 scripts/depth/review_sheet.py SPEC OUT_DIR/NEW_ID.json   (from the repository root)"""
import json, sys
sys.path.insert(0, 'skills/stock-analysis/scripts')
from model import format_number
spec = json.load(open(sys.argv[1])); d = json.load(open(sys.argv[2]))
ev = {e['id']: e for e in d['evidence']}
def show(k):
    e = ev[k]; lab = e['label']['en'] if isinstance(e['label'], dict) else e['label']
    val = format_number(e, 'en') if 'value' in e else '(text) ' + str(e.get('state', {}).get('en', ''))[:150]
    p = e.get('period', {})
    return f"      {k}: {lab} = {val} | {p.get('label','')}{' FORECAST' if p.get('forecast') else ''} | {e.get('basis','')}" + (f" | {e['operation']}{e['inputs']}" if e.get('inputs') else '')
new_ev = {e['id'] for e in spec.get('evidence', [])}
print('NEW CALCULATIONS:'); [print(show(k)) for k in new_ev]
for sid, add in spec['sections'].items():
    sec = next(s for s in d['sections'] if s['id'] == sid)
    print(f"\n##### {sid}: {sec['question']['en']}")
    print('   SHORT ANSWER:', sec['guide']['claims'][0]['text']['en'] if sec.get('guide') else '-')
    for c in add.get('claims', []):
        print(f"\n  [{c['type']}] EN: {c['text']['en']}\n              RO: {c['text']['ro']}")
        for k in c['evidence_refs']: print(show(k))
    if 'lesson' in add:
        for part in ('concept', 'example', 'trap'):
            print(f"\n  LESSON {part} EN: {add['lesson'][part]['en']}\n              RO: {add['lesson'][part]['ro']}")

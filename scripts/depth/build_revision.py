"""Build an editorial depth revision from a saved snapshot and a deepening spec.

Rules enforced mechanically (anything else fails):
- the base snapshot's existing text, evidence, sources, cutoff, conclusions and watchlist are untouched;
- new evidence may only be `calculation` entries whose inputs already exist (values come from recompute);
- new claims are interpretation/model/limitation, cite existing (or newly derived) evidence, and are bilingual;
- a lesson is only added to a section that has none;
- the result must pass the project's recompute and validate.

usage: python3 scripts/depth/build_revision.py research/depth/NEW_ID.spec.json OUT_DIR   (from the repository root)
"""
import copy, datetime, json, subprocess, sys
from pathlib import Path

ROOT = Path.cwd()
STOCK = ROOT / 'skills/stock-analysis/scripts/stock.py'
spec = json.loads(Path(sys.argv[1]).read_text())
out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)

def fail(msg):
    sys.exit('deepen: ' + msg)

def bilingual(value, where):
    if not (isinstance(value, dict) and set(value) == {'en', 'ro'} and all(isinstance(v, str) and v.strip() for v in value.values())):
        fail(f'{where} needs non-empty en and ro text')

reg = json.loads((ROOT / 'stock-analysis-registry.json').read_text())
company = next((c for c in reg['companies'].values() if any(r['report_id'] == spec['base'] for r in c['reports'])), None) or fail('base report not in registry')
archive = json.loads((ROOT / company['archive_path']).read_text())
base = archive['snapshots'][spec['base']]['research']
d = copy.deepcopy(base)
if spec['new_id'] in archive['snapshots']:
    fail('new report id already archived')

ids = {e['id'] for e in d['evidence']}
for e in spec.get('evidence', []):
    if e.get('kind') != 'calculation':
        fail(f"{e.get('id')}: only calculation evidence may be added")
    if e['id'] in ids:
        fail(f"{e['id']}: evidence id already exists")
    missing = [i for i in e.get('inputs', []) if i not in ids]
    if missing:
        fail(f"{e['id']}: unknown inputs {missing}")
    bilingual(e['label'], e['id'] + ' label')
    if 'value' in e:
        fail(f"{e['id']}: do not supply a value; recompute derives it")
    d['evidence'].append(e)
    ids.add(e['id'])

sections = {s['id']: s for s in d['sections']}
added_claims = added_lessons = 0
for sid, add in spec['sections'].items():
    s = sections.get(sid) or fail(f'unknown section {sid}')
    existing = {c['text']['en'] for c in s['claims']} | {c['text']['en'] for c in (s.get('guide') or {}).get('claims', [])}
    for c in add.get('claims', []):
        if c['type'] not in {'interpretation', 'model', 'limitation'}:
            fail(f'{sid}: new claims must be interpretation, model or limitation')
        bilingual(c['text'], f'{sid} claim')
        if c['text']['en'] in existing:
            fail(f'{sid}: claim repeats existing text')
        if c['type'] != 'limitation' and not c.get('evidence_refs'):
            fail(f'{sid}: claim needs evidence_refs')
        unknown = [r for r in c.get('evidence_refs', []) if r not in ids]
        if unknown:
            fail(f'{sid}: unknown evidence {unknown}')
        s['claims'].append({'type': c['type'], 'text': c['text'], 'evidence_refs': c.get('evidence_refs', [])})
        added_claims += 1
    if 'lesson' in add:
        if s.get('lesson'):
            fail(f'{sid}: already has a lesson; lessons are not replaced')
        for part in ('concept', 'example', 'trap'):
            bilingual(add['lesson'][part], f'{sid} lesson {part}')
        for lang, prefix in (('en', 'Hypothetical'), ('ro', 'Exemplu ipotetic')):
            if not add['lesson']['example'][lang].startswith(prefix):
                fail(f'{sid}: lesson example ({lang}) must start with "{prefix}"')
        s['lesson'] = {k: add['lesson'][k] for k in ('concept', 'example', 'trap')}
        added_lessons += 1

bilingual(spec['revision_note'], 'revision_note')
d['report_id'] = spec['new_id']
d['editorial_revision_of'] = spec['base']
d['revision_note'] = spec['revision_note']
d['prepared_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()

draft = out / f"{spec['new_id']}-draft.json"
final = out / f"{spec['new_id']}.json"
draft.write_text(json.dumps(d, ensure_ascii=False, indent=1))
for cmd in ([sys.executable, STOCK, 'recompute', draft, '--out', final], [sys.executable, STOCK, 'validate', final]):
    r = subprocess.run([str(x) for x in cmd], capture_output=True, text=True)
    if r.returncode:
        fail('project check failed:\n' + r.stdout + r.stderr)

# The recomputed record must differ from the base only where this revision is allowed to.
f = json.loads(final.read_text())
for key in base:
    if key in {'report_id', 'prepared_at', 'evidence', 'sections', 'editorial_revision_of', 'revision_note'}:
        continue
    if f.get(key) != base[key]:
        fail(f'top-level field {key} changed')
old_ev = {e['id']: e for e in base['evidence']}
for e in f['evidence']:
    if e['id'] in old_ev and e != old_ev[e['id']]:
        fail(f"existing evidence {e['id']} changed")
for old, new in zip(base['sections'], f['sections']):
    if new['claims'][:len(old['claims'])] != old['claims']:
        fail(f"existing claims changed in {old['id']}")
    for k in old:
        if k not in {'claims', 'lesson'} and new.get(k) != old[k]:
            fail(f"section field {old['id']}.{k} changed")
    if old.get('lesson') and new.get('lesson') != old['lesson']:
        fail(f"lesson changed in {old['id']}")
new_ev = {e['id']: e for e in f['evidence'] if e['id'] not in old_ev}
print(f"ok: {final}  (+{added_claims} claims, +{added_lessons} lessons, +{len(new_ev)} derived calculations)")
for e in new_ev.values():
    sys.path.insert(0, str(ROOT / 'skills/stock-analysis/scripts'))
    from model import format_number
    print(f"  {e['id']}: {format_number(e, 'en')}  ({e['operation']} of {e['inputs']})")

"""List numbers in a revision's new claims that do not match a value from the cited evidence (EN and RO).

usage: python3 scripts/depth/check_numbers.py SPEC OUT_DIR/NEW_ID.json   (from the repository root)
Unmatched numbers are not necessarily wrong (years, rounding, dates, lesson arithmetic) but each needs a human look.
"""
import json, re, sys
sys.path.insert(0, 'skills/stock-analysis/scripts')
from model import format_number

spec = json.load(open(sys.argv[1]))
d = json.load(open(sys.argv[2]))
ev = {e['id']: e for e in d['evidence']}

def numbers(text, lang='en'):
    """Parse numbers by language: EN uses 1,234.5 and RO uses 1.234,5. Years are skipped."""
    out = []
    for m in re.finditer(r'(?<![\w.,])(\d{1,3}(?:[., ]\d{3})+(?:[.,]\d+)?|\d+(?:[.,]\d+)?)', text):
        raw = m.group(1)
        norm = raw.replace(' ', '')
        norm = norm.replace(',', '') if lang == 'en' else norm.replace('.', '').replace(',', '.')
        v = float(norm)
        if v.is_integer() and 1990 <= v <= 2100:
            continue
        out.append((raw, v))
    return out

def closure(refs):
    seen, todo = set(), list(refs)
    while todo:
        k = todo.pop()
        if k in seen or k not in ev:
            continue
        seen.add(k)
        todo += ev[k].get('inputs', []) + ev[k].get('evidence_refs', [])
    return seen

def targets(keys):
    vals = set()
    for k in keys:
        e = ev[k]
        if 'value' not in e:
            continue
        for lang in ('en', 'ro'):
            for _, v in numbers(format_number(e, lang), lang):
                vals.add(round(v, 6))
        v = e['value']
        vals |= {round(v, 6), round(v, 2), round(v, 1), round(v), round(v * e.get('scale', 1) / 1e9, 2), round(v * e.get('scale', 1) / 1e6)}
    return vals

problems = 0
for sid, add in spec['sections'].items():
    for c in add.get('claims', []):
        allowed = targets(closure(c['evidence_refs']))
        for lang in ('en', 'ro'):
            for raw, v in numbers(c['text'][lang], lang):
                if not any(abs(v - a) <= max(0.051, abs(a) * 0.006) for a in allowed):
                    problems += 1
                    print(f'[{sid}/{lang}] {raw!r} not in cited evidence :: {c["text"][lang][:90]}')
print(f'{problems} number(s) to review by hand')

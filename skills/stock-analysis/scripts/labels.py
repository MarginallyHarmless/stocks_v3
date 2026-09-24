"""Display-only Romanian wording for stored period, date and basis labels.

Stored research keeps its original labels; only the rendered Romanian view changes.
"""
from __future__ import annotations
import re

MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
RO_MONTHS = ['ianuarie', 'februarie', 'martie', 'aprilie', 'mai', 'iunie', 'iulie', 'august', 'septembrie', 'octombrie', 'noiembrie', 'decembrie']
RO_SHORT = ['ian.', 'feb.', 'mar.', 'apr.', 'mai', 'iun.', 'iul.', 'aug.', 'sept.', 'oct.', 'nov.', 'dec.']
_FULL = '|'.join(m.capitalize() for m in MONTHS)
_SHORT = 'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec'

BASIS = {'adjusted': 'ajustat', 'market': 'piață', 'model': 'model', 'operating': 'operațional'}

EXACT = {
    'Comparable prior-year quarter': 'Trimestrul comparabil din anul anterior',
    '2026 proxy': 'Proxy 2026',
}

# Longest phrases first so "regular close" wins over "close".
WORDS = [
    ('Illustrative FY2028 recurring diluted EPS', 'EPS diluat recurent ilustrativ FY2028'),
    ('management guidance', 'estimarea conducerii'), ('management forecast', 'prognoza conducerii'),
    ('analyst estimate', 'estimarea analiștilor'), ('illustrative scenario', 'scenariu ilustrativ'),
    ('disclosure bridge', 'reconciliere raportată'), ('acquisition terms', 'termenii achiziției'),
    ('regular close', 'închiderea ședinței'), ('run rate', 'ritm anualizat'),
    ('total returns', 'randamente totale'), ('total return', 'randament total'),
    ('Next 12 months from', 'Următoarele 12 luni din'), ('Disclosed by', 'Raportat până la'),
    ('Year to', 'Anul până la'), ('price using', 'preț folosind'),
    ('guidance', 'estimarea conducerii'), ('estimate', 'estimare'), ('scenario', 'scenariu'),
    ('illustrative', 'ilustrativ'), ('sensitivity', 'sensibilitate'), ('preliminary', 'preliminar'),
    ('valuation', 'evaluare'), ('model', 'model'), ('close', 'închidere'),
]


def _month(name):
    key = name.lower().rstrip('.')
    for i, m in enumerate(MONTHS):
        if m.startswith(key[:3]):
            return i
    raise ValueError(name)


def ro_date(text):
    """Month-name dates in English word order become Romanian (30 iunie 2026)."""
    text = re.sub(rf'\b({_FULL}) (\d{{1,2}}), (\d{{4}})', lambda m: f'{int(m[2])} {RO_MONTHS[_month(m[1])]} {m[3]}', text)
    text = re.sub(rf'\b({_SHORT}) (\d{{1,2}}), (\d{{4}})', lambda m: f'{int(m[2])} {RO_SHORT[_month(m[1])]} {m[3]}', text)
    text = re.sub(rf'\b(\d{{1,2}}) ({_SHORT}) (\d{{4}})', lambda m: f'{m[1]} {RO_SHORT[_month(m[2])]} {m[3]}', text)
    text = re.sub(rf"\b({_SHORT}) '(\d\d)\b", lambda m: f'{RO_SHORT[_month(m[1])]} ’{m[2]}', text)
    text = re.sub(rf'\b({_SHORT}) (\d{{4}})\b', lambda m: f'{RO_SHORT[_month(m[1])]} {m[2]}', text)
    text = re.sub(rf'\b({_FULL}) (\d{{1,2}})\b', lambda m: f'{int(m[2])} {RO_MONTHS[_month(m[1])]}', text)
    text = re.sub(rf'\b({_FULL})\b', lambda m: RO_MONTHS[_month(m[1])], text)
    # 12-hour clock to 24-hour: "4:00 PM EDT" -> "16:00 EDT"
    return re.sub(r'\b(\d{1,2}):(\d\d) ?([AP])M\b', lambda m: f'{int(m[1]) % 12 + (12 if m[3] == "P" else 0)}:{m[2]}', text)


def period(label, lang):
    """Localized period label for display (Q2 2026 -> T2 2026, H1 -> S1, TTM June 2026 -> TTM iunie 2026)."""
    label = str(label)
    if lang != 'ro':
        return label
    if label in EXACT:
        return EXACT[label]
    text = re.sub(r'\bQ([1-4])(\d\d)\b', r'T\1 20\2', label)
    text = re.sub(r'\bQ([1-4])\b', r'T\1', text)
    text = re.sub(r'\bH([12])\b', r'S\1', text)
    text = re.sub(r'\b9M\b', '9 luni', text)
    text = re.sub(r'\bTTM to\b', 'TTM până la', text)
    text = ro_date(text)
    for en, ro in WORDS:
        text = re.sub(rf'\b{re.escape(en)}\b', ro, text)
    return text


def basis(value, lang):
    return BASIS.get(value, value) if lang == 'ro' else value


PERIOD_ONLY = re.compile(r'(?:Q[1-4] ?(?:FY ?)?\d{2,4}|H[12] (?:FY ?)?\d{4}|9M FY ?\d{4}|TTM[\w ,-]*)')


def cell(text, lang):
    """Localize a table cell only when its whole text is a period label."""
    return period(text, lang) if PERIOD_ONLY.fullmatch(str(text).strip()) else text

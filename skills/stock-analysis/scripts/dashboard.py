"""Dated financial charts. Explicit source data; no ticker or metric guessing."""
from __future__ import annotations
import html
import json
import math
import statistics
from datetime import date
from urllib.parse import urlparse

NAMES = {
    'revenue': ('Revenue', 'Venituri'),
    'net_income': ('Net profit', 'Profit net'),
    'cfo': ('Operating cash flow', 'Numerar operațional'),
    'fcf': ('Free cash flow', 'Flux liber de numerar'),
    'diluted_shares': ('Diluted average shares', 'Media acțiunilor diluate'),
    'cash': ('Cash', 'Numerar'),
    'investments': ('Short-term investments', 'Investiții pe termen scurt'),
    'debt': ('Total debt', 'Datorii totale'),
    'sga': ('Selling & administration', 'Vânzări și administrare'),
    'rnd': ('Research & development', 'Cercetare și dezvoltare'),
    'opex': ('Operating expenses', 'Cheltuieli operaționale'),
    'payroll': ('Employee costs', 'Costuri cu personalul'),
    'service_costs': ('Service costs', 'Costuri ale serviciilor'),
    'fuel': ('Fuel & purchased power', 'Combustibil și energie cumpărată'),
    'maintenance': ('Operations & maintenance', 'Operare și mentenanță'),
    'pe': ('Historical P/E', 'P/E istoric'),
    'ps': ('Historical P/S', 'P/S istoric'),
}
COLORS = ['var(--plot-violet)', 'var(--plot-mint)', 'var(--plot-gold)']
RATINGS = ['Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell']
RATINGS_RO = ['Cumpărare fermă', 'Cumpărare', 'Păstrare', 'Vânzare', 'Vânzare fermă']


def h(v):
    return html.escape(str(v), quote=True)


def tr(lang, en, ro):
    return ro if lang == 'ro' else en


def name(key, lang):
    return NAMES[key][lang == 'ro']


def ensure(condition, message):
    if not condition:
        raise ValueError('Visual data: ' + message)


def finite(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def validate_dashboard(d, identity=None):
    ensure(d.get('kind') == 'visual_research_supplement', 'wrong record kind')
    ensure(d.get('identity') and (identity is None or d['identity'] == identity), 'security identity mismatch')
    date.fromisoformat(d['retrieved_at'])
    for key, source in d['sources'].items():
        ensure(urlparse(source['url']).scheme in ('http', 'https'), 'unsafe source URL')
        ensure(source.get('status') == 'read', 'unread source: ' + key)
        date.fromisoformat(source['retrieved_at'])
    def sourced(record):
        ensure(record.get('source_id') in d['sources'], 'missing source')
    for key, series in d['series'].items():
        ensure(key in NAMES, 'unknown series: ' + key)
        sourced(series)
        ensure(series['unit'] in ('currency', 'shares', 'ratio'), 'unknown unit')
        ensure(finite(series['scale']) and series['scale'] > 0, 'invalid scale')
        ensure(series['period_kind'] in ('annual', 'quarter'), 'mixed or unspecified cadence')
        ensure(series.get('basis'), 'missing accounting basis')
        if series['unit'] == 'currency':
            ensure(series.get('currency') == 'USD', 'this formatter requires USD')
        points = series['points']
        labels = [p['period'] for p in points]
        ensure(len(set(labels)) == len(labels), 'duplicate periods')
        ensure(all(x not in ('TTM', 'Current') for x in labels), 'TTM/current mixed into history')
        for p in points:
            ensure(p['value'] is None or finite(p['value']), 'invalid observation')
            if key in ('pe', 'ps'):
                ensure(p['value'] is None or p['value'] > 0, 'nonpositive multiple')
    m = d.get('market', {})
    for key in ('overview_quote', 'stats_quote', 'forecast_quote'):
        if key in m:
            sourced(m[key]); ensure(finite(m[key]['price']) and m[key]['price'] > 0, 'invalid quote')
            ensure(m[key].get('observed_at') and m[key].get('session'), 'undated quote')
    if m.get('range'):
        r = m['range']; sourced(r)
        ensure(finite(r['low']) and finite(r['high']) and 0 < r['low'] < r['high'], 'invalid range')
    if m.get('ma200'):
        sourced(m['ma200']); ensure(finite(m['ma200']['value']) and m['ma200']['value'] > 0, 'invalid average')
    if d.get('cash_bridge'):
        b=d['cash_bridge']; sourced(b)
        ensure(all(finite(b[k]) for k in ('cfo','cash_capex','lease_principal','issuer_fcf','scale')), 'invalid cash bridge')
        ensure(abs(b['cfo']-b['cash_capex']-b['lease_principal']-b['issuer_fcf'])<1e-6, 'cash bridge does not reconcile')
    c = d.get('consensus', {})
    if c.get('targets'):
        t = c['targets']; sourced(t)
        ensure(all(finite(t[k]) for k in ('low', 'mean', 'median', 'high')), 'invalid target')
        ensure(0 < t['low'] <= t['mean'] <= t['high'] and t['low'] <= t['median'] <= t['high'], 'target order')
    if c.get('ratings'):
        r = c['ratings']; sourced(r)
        ensure(set(r['counts']) == set(RATINGS), 'incomplete recommendation categories')
        ensure(all(finite(v) and int(v) == v and v >= 0 for v in r['counts'].values()), 'invalid rating count')
        ensure(r['total'] == sum(r['counts'].values()) and r['total'] > 0, 'rating total mismatch')
        score = sum((i + 1) * r['counts'][k] for i, k in enumerate(RATINGS)) / r['total']
        ensure(abs(score - r['score']) < 1e-8, 'rating score mismatch')
    return d


def fmt(v, unit='currency', scale=1, lang='en', compact=True):
    if v is None:
        return tr(lang, 'Not available', 'Indisponibil')
    n = v * scale
    if unit == 'percent':
        result = f'{n:+.1f}%'
    elif unit == 'ratio':
        result = f'{n:,.2f}×'
    else:
        suffix = ''
        if compact:
            for threshold, tag in [(1e12, 'T'), (1e9, 'B'), (1e6, 'M'), (1e3, 'K')]:
                if abs(n) >= threshold:
                    n /= threshold; suffix = tag; break
        result = ('$' if unit == 'currency' else '') + f'{n:,.2f}'.rstrip('0').rstrip('.') + suffix
    return result.replace(',', ' ').replace('.', ',') if lang == 'ro' else result


def link(d, key, lang):
    return f'<a href="{h(d["sources"][key]["url"])}" target="_blank" rel="noopener noreferrer">{tr(lang,"Source","Sursă")} ↗</a>'


def explanation(en, ro, lang):
    return f'<p class="viz-explain">{h(tr(lang, en, ro))}</p>'


def rows_html(rows):
    return '<dl class="viz-facts">' + ''.join(f'<div><dt>{h(a)}</dt><dd>{h(b)}</dd></div>' for a, b in rows) + '</dl>'


def card_open(title, subtitle=''):
    return f'<article class="viz-card"><header><h3>{h(title)}</h3><p class="viz-subtitle">{h(subtitle)}</p></header>'


def blank(lang, en='This source does not supply this series.', ro='Această sursă nu furnizează seria.'):
    return '<p class="viz-unavailable">' + h(tr(lang, en, ro)) + '</p>'


def periods_for(series):
    """Align by period key, never by array index; missing observations stay null."""
    cadence = {s['period_kind'] for _, s in series}
    ensure(len(cadence) == 1, 'cannot mix annual and quarterly data in one chart')
    def order(label):
        words = label.split()
        ensure(len(words) == 2 and words[1].isdigit(), 'invalid period: ' + label)
        return (int(words[1]), int(words[0][1]) if words[0].startswith('Q') else 0)
    found = sorted({p['period'] for _, s in series for p in s['points']}, key=order)
    if not found:
        return []
    first, last = order(found[0]), order(found[-1])
    if next(iter(cadence)) == 'annual':
        return [f'FY {year}' for year in range(first[0], last[0]+1)]
    start, end = first[0]*4+first[1]-1, last[0]*4+last[1]-1
    return [f'Q{index%4+1} {index//4}' for index in range(start,end+1)]


def chart_data(d, keys):
    series = [(k, d['series'][k]) for k in keys if k in d['series']]
    if not series:
        return [], [], []
    base = series[0][1]
    ensure(all(s['unit'] == base['unit'] and s.get('currency') == base.get('currency') and s['basis'] == base['basis'] for _, s in series), 'incompatible chart series')
    labels = periods_for(series)
    values = []
    for _, s in series:
        mapped = {p['period']: p['value'] for p in s['points']}
        # Normalize scales before shared-axis plotting.
        values.append([None if mapped.get(p) is None else mapped[p] * s['scale'] for p in labels])
    return series, labels, values


def chart(d, keys, lang, style='bar', median=False):
    series, labels, values = chart_data(d, keys)
    if not series:
        return blank(lang)
    valid = [v for row in values for v in row if v is not None]
    if not valid:
        return blank(lang, 'No usable observations. Missing values are not zero.', 'Nu există observații utilizabile. Datele lipsă nu înseamnă zero.')
    unit = series[0][1]['unit']
    low, high = min(0, min(valid)), max(0, max(valid))
    # Honest bar baseline and shared axis. Lines also keep zero, except dilution.
    restricted = style == 'shares' and min(valid) > 0
    if restricted:
        pad = max((max(valid) - min(valid)) * .15, max(valid) * .01)
        low, high = min(valid) - pad, max(valid) + pad
    span = high - low or 1
    if not restricted:
        if high > 0: high += span * .12
        if low < 0: low -= span * .08
    span = high - low or 1
    x0, x1, y0, y1 = 64, 460, 20, 190
    step = (x1 - x0) / len(labels)
    y = lambda v: y1 - (v - low) / span * (y1 - y0)
    svg = f'<svg class="viz-chart" viewBox="0 0 480 230" role="img" aria-label="{h(" / ".join(name(k,lang) for k,_ in series))}"><title>{h(" / ".join(name(k,lang) for k,_ in series))}</title>'
    svg += '<desc>' + tr(lang, 'Values and dates are available below in the data table.', 'Valorile și datele sunt disponibile în tabelul de mai jos.') + '</desc>'
    for v in sorted(set([low, low + span / 2, high] + ([] if restricted else [0]))):
        yy = y(v)
        svg += f'<line class="viz-gridline" x1="{x0}" x2="{x1}" y1="{yy:.2f}" y2="{yy:.2f}"/><text x="{x0-9}" y="{yy+4:.2f}" text-anchor="end">{h(fmt(v,unit,lang=lang))}</text>'
    median_value = statistics.median(valid) if median and len(valid) >= 8 and len(series) == 1 else None
    if median_value is not None:
        yy = y(median_value)
        svg += f'<line class="viz-median" x1="{x0}" x2="{x1}" y1="{yy:.2f}" y2="{yy:.2f}"/>'
    for j, ((key, _), row) in enumerate(zip(series, values)):
        color = COLORS[j % len(COLORS)]
        segment = []
        def flush():
            return f'<polyline points="{" ".join(segment)}" fill="none" stroke="{color}" stroke-width="2.4"/>' if len(segment) > 1 else ''
        for i, v in enumerate(row):
            x = x0 + step * (i + .5)
            if v is None:
                svg += flush(); segment = []; continue
            label = f'{labels[i]} · {name(key,lang)}: {fmt(v,unit,lang=lang)}'
            if style == 'bar':
                bw = step * .76 / len(series)
                xx = x - step * .38 + j * bw
                yy = min(y(v), y(0)); height = abs(y(v) - y(0))
                # A true zero is a hairline, never a fabricated positive bar.
                fill = 'var(--plot-loss)' if v < 0 and len(series) == 1 else color
                svg += f'<rect x="{xx:.2f}" y="{yy:.2f}" width="{bw*.83:.2f}" height="{max(height,.5):.2f}" fill="{fill}" rx="1.5"><title>{h(label)}</title></rect>'
            else:
                segment.append(f'{x:.2f},{y(v):.2f}')
                svg += f'<circle cx="{x:.2f}" cy="{y(v):.2f}" r="3" fill="{color}"><title>{h(label)}</title></circle>'
        svg += flush()
    label_indices = sorted(set([0, len(labels)//3, 2*len(labels)//3, len(labels)-1]))
    for i in label_indices:
        x = x0 + step * (i + .5)
        anchor = 'start' if i == 0 else ('end' if i == len(labels)-1 else 'middle')
        svg += f'<text x="{x:.2f}" y="216" text-anchor="{anchor}">{h(labels[i].replace(" 20", " ’"))}</text>'
    svg += '</svg>'
    out = '<div class="viz-readout" aria-live="polite">'
    for j, ((key, _), row) in enumerate(zip(series, values)):
        out += f'<div><span><i style="background:{COLORS[j%3]}"></i>{h(name(key,lang))}</span><strong data-viz-value="{j}">{h(fmt(row[-1],unit,lang=lang))}</strong></div>'
    out += '</div>'
    absent = [name(k,lang) for k in keys if k not in d['series']]
    if absent:
        out += '<p class="viz-footnote">' + h(', '.join(absent)) + ': ' + tr(lang,'not supplied separately.','nefurnizat separat.') + '</p>'
    selected = labels[-1]
    out += f'<div class="viz-chart-box">{svg}</div><div class="viz-period-row"><span>{tr(lang,"Period","Perioadă")}</span><select class="viz-period" aria-label="{h(tr(lang,"Inspect period — ","Vezi perioada — ")+name(keys[0],lang))}">'
    for i, label in enumerate(labels):
        out += f'<option value="{i}"{" selected" if i==len(labels)-1 else ""}>{h(label)}</option>'
    out += '</select></div>'
    payload = [[fmt(row[i], unit, lang=lang) for row in values] for i in range(len(labels))]
    out += '<script class="viz-values" type="application/json">' + json.dumps(payload).replace('<', '\\u003c') + '</script>'
    if median_value is not None:
        out += '<p class="viz-footnote">' + tr(lang, 'Dashed line: historical median ', 'Linie punctată: mediana istorică ') + h(fmt(median_value,unit,lang=lang)) + f' · {len(valid)} ' + tr(lang, 'valid observations.', 'observații valide.') + '</p>'
    elif median:
        out += explanation('A median needs at least 8 usable observations.', 'Mediana necesită minimum 8 observații utilizabile.', lang)
    if restricted:
        out += '<p class="viz-footnote">' + tr(lang, 'Vertical axis is cropped to show changes in share count.', 'Axa verticală este restrânsă pentru a evidenția variația numărului de acțiuni.') + '</p>'
    missing = sum(v is None for row in values for v in row)
    if missing:
        out += '<p class="viz-footnote">' + tr(lang, f'{missing} missing observations; gaps are not interpolated.', f'{missing} observații lipsă; golurile nu sunt interpolate.') + '</p>'
    out += '<details class="viz-data"><summary>' + tr(lang, 'View values & sources', 'Vezi valorile și sursele') + '</summary><div class="table-wrap"><table><caption>' + h(' / '.join(name(k,lang) for k,_ in series)) + '</caption><thead><tr><th>' + tr(lang,'Period','Perioadă') + '</th>'
    out += ''.join(f'<th>{h(name(k,lang))}</th>' for k,_ in series) + '</tr></thead><tbody>'
    for i, label in enumerate(labels):
        out += '<tr><th scope="row">' + h(label) + '</th>' + ''.join('<td>' + h(fmt(row[i],unit,lang=lang,compact=False)) + '</td>' for row in values) + '</tr>'
    out += '</tbody></table></div><ul class="viz-sources">'
    for key, s in series:
        source = d['sources'][s['source_id']]
        out += '<li>' + h(name(key,lang)) + ': ' + link(d,s['source_id'],lang) + ' · ' + h(s['source_row']) + ' · ' + h(source['retrieved_at']) + '</li>'
    out += '</ul><p class="viz-footnote">' + h(d.get('basis_note',{}).get(lang,'')) + '</p></details>'
    return out


def financial_card(d, title, keys, lang, explanation_pair, style='bar', median=False):
    series = [d['series'][k] for k in keys if k in d['series']]
    if series:
        count = len(periods_for([(k,d['series'][k]) for k in keys if k in d['series']]))
        cadence = tr(lang,'quarters','trimestre') if series[0]['period_kind']=='quarter' else tr(lang,'years · annual data','ani · date anuale')
        subtitle = f'{count} {cadence} · ' + ('USD' if series[0]['unit']=='currency' else tr(lang,'shares','acțiuni') if series[0]['unit']=='shares' else tr(lang,'times earnings / sales','multiplu al profitului / veniturilor'))
    else:
        subtitle = tr(lang,'Historical data unavailable','Istoric indisponibil')
    result = card_open(title, subtitle) + chart(d,keys,lang,style,median)
    if keys==['cfo','fcf'] and d.get('cash_bridge'):
        b=d['cash_bridge'];value=lambda k:fmt(b[k],'currency',b['scale'],lang)
        result += '<div class="viz-bridge"><strong>' + tr(lang,'Why Meta reports a different figure','De ce Meta raportează altă valoare') + '</strong><p>' + h(b['period']) + ': ' + h(fmt(b['cfo']-b['cash_capex'],'currency',b['scale'],lang)) + tr(lang,' before lease principal − ',' înainte de principalul leasingului − ') + h(value('lease_principal')) + ' = <strong>' + h(value('issuer_fcf')) + '</strong> ' + tr(lang,'company-defined free cash flow.','flux liber definit de companie.') + '</p>' + link(d,b['source_id'],lang) + '</div>'
    return result + explanation(*explanation_pair,lang) + '</article>'


def price_card(d, lang):
    out = card_open(tr(lang,'Price in the past 12 months','Prețul în ultimele 12 luni'),tr(lang,'Published 52-week range · USD','Interval publicat pentru 52 de săptămâni · USD'))
    m=d.get('market',{}); q=m.get('overview_quote'); r=m.get('range')
    if not q or not r:
        return out + blank(lang) + '</article>'
    price=q['price']; low=r['low']; high=r['high']; pct=(price-low)/(high-low)*100
    out += f'<div class="viz-price">{h(fmt(price,lang=lang))}</div><p class="viz-footnote">{h(q["observed_at"])} · {tr(lang,"Regular close","Închiderea ședinței")}</p>'
    out += f'<div class="viz-range" role="img" aria-label="{h(tr(lang,"Position in range: ","Poziția în interval: ")+str(round(pct,1))+"%")}"><div class="viz-range-fill" style="width:{max(0,min(100,pct)):.2f}%"></div><i style="left:{max(0,min(100,pct)):.2f}%"></i></div>'
    out += '<div class="viz-range-labels"><span>'+tr(lang,'Low','Minim')+' <strong>'+h(fmt(low,lang=lang))+'</strong></span><span>'+tr(lang,'High','Maxim')+' <strong>'+h(fmt(high,lang=lang))+'</strong></span></div>'
    rows=[(tr(lang,'Position in range','Poziție în interval'),f'{pct:.1f}%'),(tr(lang,'From the high','Față de maxim'),fmt((price/high-1)*100,'percent',lang=lang)),(tr(lang,'From the low','Față de minim'),fmt((price/low-1)*100,'percent',lang=lang))]
    ma=m.get('ma200'); sq=m.get('stats_quote')
    if ma:
        rows.append((tr(lang,'200-day average','Media de 200 de zile'),fmt(ma['value'],lang=lang)))
        if sq and sq['observed_at']==q['observed_at']:
            rows.append((tr(lang,'From 200-day average','Față de media de 200 de zile'),fmt((price/ma['value']-1)*100,'percent',lang=lang)))
    rows += [(tr(lang,'Low / high dates','Datele minimului / maximului'),tr(lang,'Not supplied','Nefurnizate'))]
    out += rows_html(rows) + '<p class="viz-footnote">'+link(d,r['source_id'],lang)+' · '+(link(d,ma['source_id'],lang) if ma else '')+'</p>'
    out += explanation('Range uses the provider’s published high and low, not daily closing prices. Position and moving averages describe history; they do not identify a buying point.', 'Intervalul folosește minimul și maximul publicate de furnizor, nu închiderile zilnice. Poziția și media descriu trecutul; nu indică un moment de cumpărare.',lang)
    return out+'</article>'


def consensus_card(d,lang):
    c=d.get('consensus',{}); t=c.get('targets'); r=c.get('ratings'); q=d.get('market',{}).get('forecast_quote')
    out=card_open(tr(lang,'Analyst consensus','Consensul analiștilor'),tr(lang,'12-month price targets · estimates','Ținte de preț pe 12 luni · estimări'))
    if c.get('label'):
        label = dict(zip(RATINGS, RATINGS_RO)).get(c['label'], c['label']) if lang == 'ro' else c['label']
        out += '<p class="viz-consensus-label">' + h(label) + '</p>'
    if t:
        out+='<div class="viz-price">'+h(fmt(t['mean'],lang=lang))+'</div><p class="viz-footnote">'+tr(lang,'Average target','Țintă medie')
        if q:out+=' · '+h(fmt((t['mean']/q['price']-1)*100,'percent',lang=lang))+' '+tr(lang,'vs. quoted price','față de cotație')
        out+='</p>'+rows_html([(tr(lang,'Low / median / high','Minim / mediană / maxim'),' / '.join(fmt(t[k],lang=lang) for k in ('low','median','high'))),(tr(lang,'Target contributors','Analiști cu ținte'),str(c.get('target_analyst_count',tr(lang,'Not supplied','Nefurnizat'))))])
    else:out+=blank(lang)
    if r:
        names=RATINGS_RO if lang=='ro' else RATINGS
        out+='<h4>'+tr(lang,'Recommendation distribution','Distribuția recomandărilor')+'</h4><p class="viz-footnote">'+h(str(r['total'])+' · '+r['period'])+'</p><div class="viz-rating-bar" role="img" aria-label="'+h(', '.join(f'{names[i]} {int(r["counts"][k])}' for i,k in enumerate(RATINGS)))+'">'
        for i,k in enumerate(RATINGS):
            count=r['counts'][k]
            if count:out+=f'<span class="viz-rating-{i}" style="width:{100*count/r["total"]:.4f}%"></span>'
        out+='</div><ul class="viz-rating-legend">'
        for i,k in enumerate(RATINGS):out+=f'<li><i class="viz-rating-{i}"></i><span>{h(names[i])}</span><strong>{int(r["counts"][k])}</strong></li>'
        out+='</ul><p class="viz-footnote">'+tr(lang,'Average score','Scor mediu')+f': {r["score"]:.2f}/5 · '+tr(lang,'1 = strong buy; 5 = strong sell.','1 = cumpărare fermă; 5 = vânzare fermă.')+'</p>'
    else:out+=blank(lang,'Recommendation counts were not supplied.','Numărul recomandărilor nu a fost furnizat.')
    if t:out+='<p class="viz-footnote">'+link(d,t['source_id'],lang)+'</p>'
    out+=explanation('Targets are opinions, not guaranteed returns. Target contributors and recommendation counts can differ because coverage differs.', 'Țintele sunt opinii, nu randamente garantate. Numărul analiștilor cu ținte poate diferi de numărul recomandărilor.',lang)
    return out+'</article>'


def dashboard_html(d, data, lang):
    identity=data['company']['issuer_id']+'|'+data['company']['security_id']
    validate_dashboard(d,identity)
    out=f'<section class="visual-dashboard" id="{lang}-visuals"><div class="viz-intro"><div class="kicker">{tr(lang,"The numbers, visually","Cifrele, vizual")}</div><h2>{tr(lang,"Financial performance","Evoluția financiară")}</h2><p>{tr(lang,"See how sales, profit and cash have changed. Select a period in any chart to inspect its values.","Vezi evoluția vânzărilor, profitului și numerarului. Selectează o perioadă în orice grafic pentru a vedea valorile.")}</p><p class="viz-date">{tr(lang,"Chart data collected","Datele graficelor colectate la")} {h(d["retrieved_at"])} · {tr(lang,"Original analysis","Analiza originală")}: {h(data["cutoff"][:10])}. {tr(lang,"Charts are a dated supplement; the original conclusions and watchlist have not been reassessed.","Graficele sunt un supliment datat; concluziile originale și lista de verificări nu au fost reevaluate.")}</p></div>'
    if d['ticker'] in ('SOFI','HOOD'):
        out += explanation('Financial-company cash flows include lending and customer-funding movements. Do not interpret this free-cash-flow series like that of a software or industrial company.', 'Fluxurile companiilor financiare includ creditarea și mișcările fondurilor clienților. Nu interpreta seria fluxului liber ca la o companie software sau industrială.', lang)
    if d['ticker']=='NBIS':
        out += explanation('The history spans a major business restructuring. Earlier periods are not a like-for-like record of today’s Nebius business.', 'Istoricul include o restructurare majoră a afacerii. Perioadele anterioare nu sunt direct comparabile cu activitatea actuală Nebius.', lang)
    out+='<div class="viz-grid">'
    out+=financial_card(d,tr(lang,'Revenue','Venituri'),['revenue'],lang,('Money earned from selling products and services. Compare the same quarter a year apart to allow for seasonality.','Banii obținuți din vânzarea produselor și serviciilor. Compară același trimestru între ani pentru a ține cont de sezonalitate.'))
    out+=financial_card(d,tr(lang,'Net profit','Profit net'),['net_income'],lang,('Profit attributable to common shareholders after costs and taxes. Red bars show losses. One-off gains can lift profit without improving the core business.','Profitul acționarilor ordinari după costuri și taxe. Barele roșii indică pierderi. Câștigurile excepționale pot mări profitul fără îmbunătățirea activității.'))
    out+=financial_card(d,tr(lang,'Cash flow','Flux de numerar'),['cfo','fcf'],lang,('Operating cash is money generated by operations. Provider free cash flow subtracts cash capital spending; it may differ from the company’s definition.','Numerarul operațional este generat de activitate. Fluxul liber al furnizorului scade investițiile de capital plătite; poate diferi de definiția companiei.'))
    out+=financial_card(d,tr(lang,'Share count','Numărul de acțiuni'),['diluted_shares'],lang,('More diluted shares divide the business among more shares. This weighted average is not the number of shares outstanding on a single date.','Mai multe acțiuni diluate împart afacerea între mai multe acțiuni. Această medie ponderată nu este numărul de acțiuni în circulație la o anumită dată.'),'shares')
    out+=financial_card(d,tr(lang,'Cash, investments & debt','Numerar, investiții și datorii'),['cash','investments','debt'],lang,('Balances at each period end. Provider total debt includes lease obligations. A missing component is not zero.','Solduri la finalul fiecărei perioade. Datoria furnizorului include obligațiile de leasing. O componentă lipsă nu înseamnă zero.'))
    expense_keys=['sga','rnd'] if 'rnd' in d['series'] else [k for k in ('payroll','service_costs','fuel','maintenance','opex') if k in d['series']][:2]
    if not expense_keys:expense_keys=['opex']
    out+=financial_card(d,tr(lang,'Operating expenses','Cheltuieli operaționale'),expense_keys,lang,('Follow the named cost categories alongside revenue. These categories may not add up to all operating costs.','Urmărește categoriile de costuri afișate alături de venituri. Aceste categorii pot să nu reprezinte toate cheltuielile operaționale.'),'line')
    out+='</div><div class="viz-group-heading"><h2>'+tr(lang,'Price & market expectations','Preț și așteptările pieței')+'</h2><p>'+tr(lang,'Separate business performance from the price investors are paying.','Separă evoluția afacerii de prețul plătit de investitori.')+'</p></div><div class="viz-grid">'+price_card(d,lang)+consensus_card(d,lang)+'</div>'
    out+='<div class="viz-group-heading"><h2>'+tr(lang,'Valuation through time','Evaluarea în timp')+'</h2><p>'+tr(lang,'How much investors paid for one dollar of earnings or sales.','Cât au plătit investitorii pentru un dolar de profit sau venituri.')+'</p></div><div class="viz-grid">'
    for k in ('pe','ps'):
        note=('P/E compares equity value with trailing earnings. Unavailable or nonpositive earnings multiples are gaps, never zero.','P/E compară valoarea acțiunilor cu profitul ultimelor 12 luni. Multiplii indisponibili sau nepozitivi rămân goluri, niciodată zero.') if k=='pe' else ('P/S compares equity value with trailing sales. A low multiple alone does not make a company cheap.','P/S compară valoarea acțiunilor cu veniturile ultimelor 12 luni. Un multiplu mic nu înseamnă automat o companie ieftină.')
        out+=financial_card(d,name(k,lang),[k],lang,note,'line',True)
    out+='</div><p class="viz-date">'+tr(lang,'Provider historical multiples at period end, not a reconstruction using prices on filing dates. Restatements and provider conventions may differ from the original analysis. The historical median is a reference, not a price target.','Multipli istorici ai furnizorului la finalul perioadei, nu o reconstrucție cu prețurile din zilele raportărilor. Retratările și convențiile furnizorului pot diferi de analiza originală. Mediana este un reper, nu o țintă de preț.')+'</p><button class="viz-export" data-export-visuals>'+tr(lang,'Download chart data','Descarcă datele graficelor')+'</button></section>'
    return out

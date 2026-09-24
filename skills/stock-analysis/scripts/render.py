"""Deterministic, offline HTML reports with optional lessons and evidence dialogs."""
from __future__ import annotations
import html
import json
from pathlib import Path
from financial_terms import annotate, TERMS
from dashboard import dashboard_html
from archive import verify_archive
from model import digest, format_number, number, validate, need, dimensions, period_key

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def h(value):
    return html.escape(str(value), quote=True)


def t(value, lang):
    if isinstance(value, dict):
        return value.get(lang, value.get("en", next(iter(value.values()), "")))
    return str(value)


def tr(lang, en, ro):
    return ro if lang == "ro" else en


def ref_buttons(ids, lang):
    ids = list(dict.fromkeys(ids))
    if not ids:
        return ''
    return f'<button class="ref" data-evidence="{h(ids[0])}" data-evidence-ids="{h(json.dumps(ids))}">{tr(lang,"Sources","Surse")}</button>'


def claims(items, lang, compact=False):
    parts = []
    for c in items:
        label = {"fact": tr(lang, "Reported evidence", "Date raportate"), "interpretation": tr(lang, "Interpretation", "Interpretare"),
                 "model": tr(lang, "Conditional model", "Model condiționat"), "limitation": tr(lang, "Evidence limit", "Limită a datelor")}[c["type"]]
        badge = '' if compact and c['type'] in {'fact', 'interpretation'} else f'<span class="claim-type">{label}</span>'
        parts.append(f'<p class="claim">{badge}{h(t(c["text"],lang))}{ref_buttons(c.get("evidence_refs",[]),lang)}</p>')
    return "".join(parts)


def event_html(ev, sources, lang, compact=False):
    confidence = {"Confirmed": tr(lang,"Confirmed","Confirmată"), "Estimated": tr(lang,"Estimated","Estimată"), "Not announced":tr(lang,"Not announced","Neanunțată")}[ev["confidence"]]
    date = ev.get("date") or tr(lang, "Date not announced", "Data nu a fost anunțată")
    time = (" · " + ev["time"] + " " + ev["timezone"]) if ev.get("time") else ""
    link = ""
    if ev.get("source_id") in sources:
        s = sources[ev["source_id"]]
        link = f' · <a href="{h(s["url"])}" target="_blank" rel="noopener noreferrer">{h(t(s["title"],lang))}</a>'
    heading = {'results':tr(lang,'Next results','Următoarele rezultate'),'call':tr(lang,'Earnings call','Conferința de rezultate'),'filing':tr(lang,'Regulatory filing','Raportarea de reglementare')}[ev['kind']]
    result = f'<div class="event"><span class="kicker">{heading} · {h(t(ev["period"],lang))}</span><br><strong>{h(date)}{h(time)}</strong> <span class="meta">— {confidence}</span><div class="meta">{tr(lang,"Schedule checked","Calendar verificat")}: {h(ev["checked_at"])}{link}</div>'
    if ev.get("basis"):
        result += f'<div class="meta">{h(t(ev["basis"],lang))}</div>'
    return result + '</div>'


def metrics_html(ids, ev, lang, explanations=None):
    result = '<div class="metrics">'
    assumptions = []
    for key in ids:
        e = ev[key]
        explanation = (explanations or {}).get(key)
        label = explanation.get('label', e['label']) if explanation else e['label']
        tag = tr(lang,"Forecast","Prognoză") if e["period"]["forecast"] else (tr(lang,"Assumption","Ipoteză") if e["kind"] == "assumption" else "")
        result += f'<div class="metric"><span class="label">{h(t(label,lang))}</span><strong>{h(format_number(e,lang))}</strong><span class="period">{h(e["period"]["label"])} · {h(e["basis"])}{f"<span class=tag>{tag}</span>" if tag else ""}</span>'
        result += (f'<div class="metric-meaning">{claims([explanation["meaning"]],lang,True)}</div>' if explanation else ref_buttons([key],lang)) + '</div>'
        if e.get('model_assumptions'):
            note = t(e['model_assumptions'], lang)
            if note not in assumptions:
                assumptions.append(note)
    result += '</div>'
    return result + ''.join(f'<p class="caveat">{tr(lang,"Model assumptions","Ipotezele modelului")}: {h(note)}</p>' for note in assumptions)


def series_html(series, ev, lang):
    ids = series["evidence_refs"]
    records = [ev[x] for x in ids]
    need(len(records) >= 2 and all("value" in x for x in records), "Trend needs at least two numeric observations")
    need(all(dimensions(x) == dimensions(records[0]) and x["definition"] == records[0]["definition"] for x in records), "Trend definitions/units/basis differ")
    values = [number(e) for e in records]
    low, high = min(0, min(values)), max(values)
    span = high-low or 1
    xy = [(60 + i*580/(len(values)-1), 150-(v-low)/span*110) for i,v in enumerate(values)]
    points = ' '.join(f'{x:.1f},{y:.1f}' for x,y in xy)
    svg = f'<svg class="chart" viewBox="0 0 720 220" role="img" aria-label="{h(t(series["title"],lang))}"><title>{h(t(series["title"],lang))}</title><line x1="60" x2="650" y1="150" y2="150"/><polyline points="{points}"/>'
    for i, ((x,y), e) in enumerate(zip(xy,records)):
        svg += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3"/><text x="{x:.1f}" y="{max(18,y-12):.1f}" text-anchor="middle">{h(format_number(e,lang))}</text><text x="{x:.1f}" y="180" text-anchor="middle">{h(e["period"]["label"])}</text>'
    svg += '</svg>'
    rows = ''.join(f'<tr><td>{h(e["period"]["label"])}</td><td class="numeric">{h(format_number(e,lang))}</td><td>{ref_buttons([e["id"]],lang)}</td></tr>' for e in records)
    return f'<figure style="margin:20px 0"><div class="chart-wrap">{svg}</div><figcaption class="chart-caption">{h(t(series["title"],lang))} · {h(records[0]["basis"])}</figcaption></figure><details class="evidence-disclosure"><summary>{tr(lang,"Trend data & sources","Datele tendinței și sursele")}</summary><div class="table-wrap"><table><thead><tr><th>{tr(lang,"Period","Perioadă")}</th><th>{tr(lang,"Value","Valoare")}</th><th>{tr(lang,"Evidence","Dovezi")}</th></tr></thead><tbody>{rows}</tbody></table></div></details>'


def evidence_table_html(table, ev, lang):
    out = '<div class="table-wrap"><table><caption>' + h(t(table['title'], lang)) + '</caption><thead><tr>'
    out += ''.join('<th scope="col">' + h(t(x, lang)) + '</th>' for x in table['columns']) + '</tr></thead><tbody>'
    for row in table['rows']:
        out += '<tr><th scope="row">' + h(t(row['label'], lang)) + '</th>'
        for cell in row['cells']:
            if 'evidence_ref' in cell:
                e = ev[cell['evidence_ref']]
                val = format_number(e, lang) if 'value' in e else t(e['state'], lang)
                content = h(val) + ref_buttons([e['id']], lang)
            else:
                content = claims([cell], lang, True)
            out += '<td>' + content + '</td>'
        out += '</tr>'
    return out + '</tbody></table></div>'


def tables_html(tables, ev, lang):
    """Authored section tables: each row is one cell per column, backed by evidence or a typed claim."""
    out = ''
    for table in tables:
        columns = table['columns']
        out += '<div class="table-wrap"><table class="research-table"><caption>' + h(t(table['title'], lang)) + '</caption><thead><tr>'
        out += ''.join('<th scope="col">' + h(t(c, lang)) + '</th>' for c in columns) + '</tr></thead><tbody>'
        for row in table.get('rows', []):
            out += '<tr>'
            for column, cell in zip(columns, row):
                if 'evidence_ref' in cell:
                    e = ev[cell['evidence_ref']]
                    content = h(format_number(e, lang) if 'value' in e else t(e['state'], lang)) + ref_buttons([e['id']], lang)
                else:
                    content = h(t(cell['text'], lang)) + ref_buttons(cell.get('evidence_refs', []), lang)
                out += '<td data-label="' + h(t(column, lang)) + '">' + content + '</td>'
            out += '</tr>'
        out += '</tbody></table></div>'
    return out


def scenario_assumptions_html(s, ev, lang):
    """Keep the authored model claims visible beside a guided model result."""
    model_inputs, pending = set(), [m['evidence_ref'] for m in s.get('guide', {}).get('metrics', [])
                                    if ev[m['evidence_ref']].get('basis') == 'model']
    while pending:
        key = pending.pop()
        if key not in model_inputs:
            model_inputs.add(key)
            pending.extend(ev[key].get('inputs', []))
    assumptions = [c for c in s['claims'] if c['type'] == 'model' and model_inputs.intersection(c.get('evidence_refs', []))]
    if not assumptions:
        return ''
    return (f'<aside class="scenario-assumptions"><h3>{tr(lang,"Assumptions behind the displayed scenario","Ipotezele scenariului afișat")}</h3>'
            + claims(assumptions, lang) + '</aside>')


def section_html(s, ev, lang, index, sources):
    output = f'<section class="section" id="{h(lang)}-{h(s["id"])}"><div class="section-no">{index:02d}</div><h2>{h(t(s["question"],lang))}</h2>'
    guide = s.get('guide')
    if guide:
        output += '<div class="guide">' + claims(guide['claims'],lang,True)
        explanations = {m['evidence_ref']:m for m in guide.get('metrics',[])}
        if explanations:
            output += metrics_html(list(explanations),ev,lang,explanations)
        output += f'<div class="takeaway"><strong>{tr(lang,"Why it matters","De ce contează")}</strong>{claims([guide["why_it_matters"]],lang,True)}</div></div>'
    else:
        output += claims(s["claims"], lang)
        if s.get("metrics"):
            output += metrics_html(s["metrics"],ev,lang)
    output += f'<p class="caveat">{h(t(s["caveat"],lang))}</p>'
    lesson = s.get("lesson")
    if lesson:
        output += f'<details class="lesson"><summary>{tr(lang,"Explain this","Explică-mi conceptul")}</summary><div class="lesson-content"><p>{h(t(lesson["concept"],lang))}</p><p class="example"><strong>{tr(lang,"Hypothetical example","Exemplu ipotetic")}: </strong>{h(t(lesson["example"],lang))}</p><p><strong>{tr(lang,"Common trap","Confuzie frecventă")}: </strong>{h(t(lesson["trap"],lang))}</p></div></details>'
    if guide:
        output += scenario_assumptions_html(s, ev, lang)
        output += f'<details class="deep-data"><summary>{tr(lang,"Detailed analysis","Analiza detaliată")}</summary><div class="detail-content">' + claims(s['claims'],lang)
        if s.get('metrics'):
            output += metrics_html(s['metrics'],ev,lang)
    if s.get("series"):
        output += series_html(s["series"], ev, lang)
    if s.get('evidence_table'):
        output += evidence_table_html(s['evidence_table'], ev, lang)
    ids = list(s.get("metrics", [])) + [x for c in s["claims"] for x in c.get("evidence_refs",[])]
    if guide:
        guide_claims = guide['claims'] + [guide['why_it_matters']] + [m['meaning'] for m in guide.get('metrics',[])]
        ids += [x for c in guide_claims for x in c.get('evidence_refs',[])]
    if s.get('series'):
        ids += s['series']['evidence_refs']
    if s.get('evidence_table'):
        for row in s['evidence_table']['rows']:
            for cell in row['cells']:
                ids += [cell['evidence_ref']] if 'evidence_ref' in cell else cell.get('evidence_refs', [])
    roots, todo, seen = {}, list(ids), set()
    while todo:
        key=todo.pop()
        if key in seen:continue
        seen.add(key);e=ev[key]
        if e.get('source_id'):roots[e['source_id']]=sources[e['source_id']]
        todo.extend(e.get('inputs',[]));todo.extend(e.get('evidence_refs',[]))
    links=''.join(f'<p><a href="{h(source["url"])}" target="_blank" rel="noopener noreferrer">{h(t(source["title"],lang))}</a></p>' for source in roots.values())
    output += f'<details class="evidence-disclosure"><summary>{tr(lang,"Sources & calculation","Surse și calcul")}</summary><p class="meta">{tr(lang,"Open a reference to inspect its source, definition and inputs.","Deschide o referință pentru sursă, definiție și datele de intrare.")}</p>{ref_buttons(ids,lang)}{links}</details>'
    output += tables_html(s.get('tables', []), ev, lang)
    if guide:
        output += '</div></details>'
    return output + '</section>'


def evidence_html(data, lang):
    sources = {s["id"]:s for s in data["sources"]}
    output = ''
    for e in data["evidence"]:
        dependencies = list(dict.fromkeys(e.get('inputs',[]) + e.get('evidence_refs',[])))
        output += f'<article class="evidence-card" id="ev-{lang}-{h(e["id"])}" data-evidence-key="{h(e["id"])}" data-inputs="{h(json.dumps(dependencies))}"><div class="kicker">{h(e["id"])} · {h(e["kind"])}</div><h3>{h(t(e["label"],lang))}</h3><span class="value">{h(format_number(e,lang) if "value" in e else t(e["state"],lang))}</span><p>{h(e["definition"])}</p>'
        if e.get("period"):
            p = e["period"]
            output += f'<p class="meta">{h(p["label"])} · {h(p.get("start", ""))} → {h(p["end"])} · {h(e.get("basis", ""))}{" · Forecast" if p["forecast"] else ""}</p>'
        if e.get("source_id"):
            s = sources[e["source_id"]]
            output += f'<p><a href="{h(s["url"])}" target="_blank" rel="noopener noreferrer">{h(t(s["title"],lang))}</a></p><p class="meta">{h(t(e["extraction"]["locator"],lang))} · {h(t(e["extraction"]["note"],lang))}</p><p class="meta">{tr(lang,"Retrieved","Accesat")}: {h(s["retrieved_at"])}</p>'
        if e.get("inputs"):
            output += f'<p><code>{h(e["operation"])}</code> {ref_buttons(e["inputs"],lang)}</p>'
        for key in ("rationale", "model_assumptions"):
            if e.get(key):
                output += f'<p>{h(t(e[key],lang))}</p>'
        output += '</article>'
    return output


def coverage_html(data, lang):
    if not data.get('checklist'):
        return ''
    mapping=json.loads((ASSETS.parent/'references/checklist.json').read_text())
    names={c['id']:c[lang] for s in mapping['sections'] for c in s['checks']}
    names.update({c['id']:c[lang] for c in mapping['optional']})
    labels={'meets':tr(lang,'Meets','Îndeplinit'),'mixed':tr(lang,'Mixed','Mixt'),
            'does_not_meet':tr(lang,'Does not meet','Neîndeplinit'),
            'insufficient_evidence':tr(lang,'Insufficient evidence','Dovezi insuficiente'),
            'not_applicable':tr(lang,'Not applicable','Nu se aplică'),'not_researched':tr(lang,'Not researched','Necercetat')}
    rows=''.join(f'<tr><th>{h(key)} · {h(names.get(key,key))}</th><td>{h(labels[c["status"]])}</td><td>{h(t(c["reason"],lang))}{ref_buttons(c.get("evidence_refs",[]),lang)}</td></tr>' for key,c in data['checklist'].items())
    return f'<details class="evidence-disclosure"><summary>{tr(lang,"Complete checklist and research coverage","Lista completă și acoperirea cercetării")}</summary><p class="meta">{tr(lang,"Research completeness is separate from investment quality.","Completitudinea cercetării este diferită de calitatea investiției.")}</p><div class="table-wrap"><table><tbody>{rows}</tbody></table></div></details>'


def review_html(data, baseline, ev, lang):
    r = data["review"]
    old_ev = {e["id"]:e for e in baseline["evidence"]}
    old_watch = {w["id"]:w for w in baseline["watchlist"]}
    labels = [tr(lang,"Original check","Criteriul original"), tr(lang,"Previous value","Valoarea anterioară"), tr(lang,"New evidence","Date noi"), tr(lang,"Outcome","Rezultat"), tr(lang,"What changes","Ce se schimbă")]
    out = f'<section class="section" id="{lang}-review"><div class="kicker">{tr(lang,"Results follow-up","Verificarea rezultatelor")} · {h(r["release"]["period"])}</div><h2>{tr(lang,"Did the results meet our original checks?","Rezultatele îndeplinesc criteriile salvate?")}</h2><p>{h(t(r["thesis_change"],lang))}</p><p class="notice">{h(t(r["coverage_note"],lang))}</p>'
    if r["release"]["status"] == "pending":
        out += f'<p class="notice">{tr(lang,"Results not yet confirmed published. Original checks remain pending.","Publicarea rezultatelor nu este confirmată. Criteriile originale rămân în așteptare.")}</p>'
    out += '<div class="table-wrap"><table class="review-table"><thead><tr>' + ''.join(f'<th>{h(x)}</th>' for x in labels) + '</tr></thead><tbody>'
    for o in r["outcomes"]:
        w = old_watch[o["watch_id"]]
        previous = '; '.join(format_number(old_ev[x],lang) if 'value' in old_ev[x] else t(old_ev[x]["state"],lang) for x in w["baseline_refs"])
        new = '; '.join(format_number(ev[x],lang) if 'value' in ev[x] else t(ev[x]["state"],lang) for x in o.get("new_evidence_refs",[])) or '—'
        localized_outcome = {'Met':'Îndeplinit','Missed':'Neîndeplinit','Mixed':'Mixt','Not disclosed':'Neraportat','Not yet due':'Încă nu este scadent','Not comparable':'Necomparabil'}.get(o['outcome'],o['outcome']) if lang=='ro' else o['outcome']
        cells = [f'{h(t(w["question"],lang))}<p class="meta">{h(t(w["criterion"]["description"],lang))} · v{w["criterion_version"]}</p>',
                 h(previous), h(new) + ref_buttons(o.get("new_evidence_refs",[]),lang),
                 f'<span class="outcome" data-outcome="{h(o["outcome"])}">{h(localized_outcome)}</span><p>{h(t(o["reason"],lang))}</p>', h(t(o["thesis_impact"],lang))]
        if o.get("restated_baseline_ref"):
            cells[1] += f'<p class="meta">{tr(lang,"Restated comparison","Comparație retratată")}: {h(t(o["restatement_note"],lang))}{ref_buttons([o["restated_baseline_ref"]],lang)}</p>'
        out += '<tr>' + ''.join(f'<td data-label="{h(label)}">{cell}</td>' for label,cell in zip(labels,cells)) + '</tr>'
    out += '</tbody></table></div>'
    if r["new_risks"]:
        out += f'<h3>{tr(lang,"Newly identified risks","Riscuri identificate acum")}</h3>' + claims(r["new_risks"],lang)
    return out + '</section>'


def watch_html(data, ev, sources, lang):
    if not data["watchlist"]:
        return ''
    out = f'<section class="section" id="{lang}-watch"><div class="kicker">{tr(lang,"Next checkpoint","Următoarea verificare")}</div><h2>{tr(lang,"What to watch at the next results","Ce verificăm la următoarele rezultate")}</h2>' + event_html(data["next_event"],sources,lang)
    if data.get('related_events'):
        out += f'<details class="evidence-disclosure"><summary>{tr(lang,"Call and filing dates","Datele conferinței și raportării")}</summary>'
        out += ''.join(event_html(related,sources,lang) for related in data['related_events']) + '</details>'
    for i,w in enumerate(data["watchlist"],1):
        baseline = '; '.join((format_number(ev[x],lang) if 'value' in ev[x] else t(ev[x]["state"],lang)) + ' · ' + ev[x].get('period',{}).get('label','') for x in w["baseline_refs"])
        basis = {"management_guidance":tr(lang,"Management guidance","Estimarea conducerii"), "external_estimate":tr(lang,"External estimate","Estimare externă"), "analytical_test":tr(lang,"Our analytical test","Criteriul nostru de analiză")}[w["criterion"]["basis"]]
        out += f'<article class="watch-item"><span class="index">{i:02d}</span><h3>{h(t(w["question"],lang))}</h3><p class="why"><strong>{tr(lang,"Why it matters","De ce contează")}: </strong>{h(t(w["why"],lang))}</p><p><strong>{tr(lang,"What to check","Ce verificăm")}: </strong>{h(t(w["criterion"]["description"],lang))}</p><p class="meta">{basis} · {h(w["due_period"])}{(" · "+h(w["due_date"])) if w.get("due_date") else ""}</p>'
        out += f'<p class="meta"><strong>{tr(lang,"If favorable","Dacă este favorabil")}: </strong>{h(t(w["impact"]["favorable"],lang))}<br><strong>{tr(lang,"If adverse","Dacă este nefavorabil")}: </strong>{h(t(w["impact"]["adverse"],lang))}</p>'
        out += f'<details class="deep-data"><summary>{tr(lang,"Saved rule and context","Criteriul salvat și contextul")}</summary><p class="meta">{h(w["id"])} · v{w["criterion_version"]}</p><dl class="watch-grid"><dt>{tr(lang,"Starting point","Punct de plecare")}</dt><dd>{h(baseline)}{ref_buttons(w["baseline_refs"],lang)}</dd><dt>{tr(lang,"Why this criterion","De ce acest criteriu")}</dt><dd>{h(t(w["criterion"]["rationale"],lang))}{ref_buttons(w["criterion"].get("evidence_refs",[]),lang)}</dd></dl><p><strong>{tr(lang,"If mixed","Dacă este mixt")}: </strong>{h(t(w["impact"]["mixed"],lang))}</p><p><strong>{tr(lang,"If unresolved","Dacă rămâne neclar")}: </strong>{h(t(w["impact"]["unresolved"],lang))}</p></details></article>'
    prompt = f'Use $stock-analysis to review the new results for {data["company"]["name"]} ({data["company"]["ticker"]}, {data["company"]["exchange"]}, {data["company"]["share_class"]}). Retrieve baseline {data["report_id"]}, security {data["company"]["security_id"]}, and assess every saved watch item against its original criterion before creating the next watchlist.'
    out += f'<div class="prompt-box"><h3>{tr(lang,"Continue after results are published","Continuă după publicarea rezultatelor")}</h3><p class="meta">{tr(lang,"Copy this prompt into a new session. If the saved analysis cannot be found, attach the exported research package.","Copiază acest text într-o sesiune nouă. Dacă analiza salvată nu poate fi găsită, atașează pachetul de date exportat.")}</p><textarea id="prompt-{lang}" aria-label="{tr(lang,"New-session prompt","Text pentru sesiunea nouă")}" readonly>{h(prompt)}</textarea><div class="actions"><button data-copy="prompt-{lang}">{tr(lang,"Copy update prompt","Copiază textul")}</button><button data-export="{h(data["report_id"])}-package.json">{tr(lang,"Export research package","Exportă pachetul de date")}</button></div><p class="status" aria-live="polite"></p></div></section>'
    return out


def key_stats_html(data, ev, lang):
    # Presentation-only mappings keep historic research snapshots immutable.
    presets = json.loads((ASSETS / 'key-stats.json').read_text())
    rows = data.get('key_stats', presets.get(data['report_id'], []))
    if not rows:
        return ''
    meanings = {term['id']: term[lang] for term in TERMS}
    meanings['price'] = tr(lang, 'The cost of one share at the recorded date. Share price alone does not show whether a business is cheap.', 'Costul unei acțiuni la data indicată. Prețul singur nu arată dacă afacerea este ieftină.')
    meanings['revenue'] = tr(lang, 'Sales recorded during this period, before costs. Revenue is not profit or cash collected.', 'Vânzări înregistrate în perioada indicată, înainte de costuri. Veniturile nu sunt profit sau numerar încasat.')
    out = '<section class="key-stats" aria-label="' + tr(lang, 'Key stats', 'Indicatori esențiali') + '"><h2>' + tr(lang, 'Key stats', 'Indicatori esențiali') + '</h2><p class="meta">' + tr(lang, 'Saved report figures, not live quotes. Hover, focus or tap a dotted term for its meaning.', 'Valorile analizei salvate, nu cotații live. Treci cursorul, focalizează sau atinge un termen subliniat punctat pentru explicație.') + '</p><dl class="key-stats-list">'
    for row in rows:
        need(row.get('concept') in meanings, 'Unknown key-stat concept')
        key = row.get('evidence_ref')
        need(key is None or key in ev, 'Unknown key-stat evidence')
        e = ev.get(key) if key else None
        label = t(row.get('label', e['label'] if e else 'EPS'), lang)
        out += '<div class="key-stat"><dt>' + h(label) + '<span class="stat-meaning">' + h(meanings[row['concept']]) + '</span></dt><dd>'
        if e and 'value' in e:
            out += '<strong class="stat-value">' + h(format_number(e,lang)) + '</strong><span class="stat-period">' + h(e['period']['label']) + ' · ' + h(e['basis'])
            if e['period']['forecast']:
                out += ' · ' + tr(lang, 'Forecast', 'Prognoză')
            out += '</span>' + ref_buttons([key],lang)
        else:
            out += '<strong class="stat-value">' + tr(lang, 'Not established', 'Nestabilit') + '</strong>'
            note = e['state'] if e else row['note']
            out += '<p class="stat-note">' + h(t(note,lang)) + '</p>' + (ref_buttons([key],lang) if key else '')
        out += '</dd></div>'
    return out + '</dl></section>'


def render(data, baseline=None, archive=None, visual_data=None):
    validate(data, baseline)
    ev = {e["id"]:e for e in data["evidence"]}
    sources = {s["id"]:s for s in data["sources"]}
    default = data["default_language"]
    nav, main, evidence = '', '', ''
    for lang in data["languages"]:
        hidden = ' hidden' if lang != default else ''
        nav += f'<nav aria-label="{tr(lang,"Sections","Secțiuni")}" data-lang="{lang}"{hidden}><a href="#{lang}-summary">{tr(lang,"At a glance","Pe scurt")}</a>'
        if visual_data:
            nav += f'<a href="#{lang}-visuals">{tr(lang,"Financial charts","Grafice financiare")}</a>'
        if data.get("review"):
            nav += f'<a href="#{lang}-review">{tr(lang,"Original checks","Criteriile originale")}</a>'
        nav += ''.join(f'<a href="#{lang}-{h(s["id"])}">{h(t(s.get("nav_label",s["question"]),lang))}</a>' for s in data["sections"])
        nav += f'<a class="watch-link" href="#{lang}-watch">{tr(lang,"What to watch next","Ce verificăm în continuare")} ↗</a></nav>'
        main += f'<div data-lang="{lang}"{hidden}>'
        if data["synthetic"]:
            main += f'<div class="synthetic">{tr(lang,"ILLUSTRATIVE DEMO · Fictional company and invented numbers. This is a workflow example, not company research.","DEMONSTRAȚIE · Companie fictivă și valori inventate. Exemplu de funcționare, nu analiză a unei companii reale.")}</div>'
        main += f'<header class="summary" id="{lang}-summary"><div class="kicker">{h(data["company"]["ticker"])} · {h(data["company"]["exchange"])} · {h(data["company"]["share_class"])}</div><h1>{h(data["company"]["name"])}</h1><p class="meta">{tr(lang,"Information cutoff","Date disponibile până la")}: {h(data["cutoff"])} · {h(data["report_id"])}</p><div class="lead">{claims(data["summary"][:1],lang)}</div>{claims(data["summary"][1:],lang)}<dl class="assessment"><dt>{tr(lang,"Business quality","Calitatea afacerii")}</dt><dd>{claims([data["business_assessment"]],lang)}</dd><dt>{tr(lang,"Price attractiveness","Atractivitatea prețului")}</dt><dd>{claims([data["price_assessment"]],lang)}</dd></dl><p class="notice">{h(t(data["evidence_gaps"],lang))}</p>'
        if data.get("next_event"):
            main += event_html(data["next_event"], sources,lang,True)
        main += key_stats_html(data, ev, lang) + '</header>'
        if visual_data:
            main += dashboard_html(visual_data, data, lang)
        if data.get("review"):
            main += review_html(data,baseline,ev,lang)
        main += ''.join(section_html(s,ev,lang,i,sources) for i,s in enumerate(data["sections"],1))
        main += watch_html(data,ev,sources,lang) + '</div>'
        # Evidence IDs occur only once in the shared dialog; both language views share the same ledger.
    evidence = "".join(f'<div data-lang="{lang}"{(" hidden" if lang != default else "")}>{coverage_html(data,lang)}{evidence_html(data,lang)}</div>' for lang in data["languages"])
    if archive:
        verify_archive(archive)
        snapshot_list = [v['research'] for v in archive['snapshots'].values()] + [data]
    else:
        need(not baseline or baseline['mode'] != 'update', 'Exporting a later update requires --archive to preserve the baseline chain')
        snapshot_list = ([baseline] if baseline else []) + [data]
    package = {"schema_version":"3.0","kind":"company_archive","identity":data["company"]["issuer_id"]+'|'+data["company"]["security_id"],"snapshots":{d["report_id"]:{"sha256":digest(d),"research":d} for d in snapshot_list}}
    verify_archive(package)
    embedded = json.dumps(package, ensure_ascii=False, allow_nan=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    visual_embedded = json.dumps(visual_data, ensure_ascii=False).replace("<", "\\u003c") if visual_data else "null"
    opts = ''.join(f'<option value="{lang}"{" selected" if lang == default else ""}>{"English" if lang == "en" else "Română"}</option>' for lang in data["languages"])
    css = (ASSETS / 'report.css').read_text() + '\n' + (ASSETS / 'dashboard.css').read_text()
    js = (ASSETS / 'dashboard.js').read_text() + '\n' + (ASSETS / 'report.js').read_text() + '\n' + (ASSETS / 'financial-terms.js').read_text()
    main = annotate(main, 'report')
    evidence = annotate(evidence, 'evidence')
    home_link = '<a class="brand home-link" href="../index.html"><span class="brand-name"><span class="brand-icon" aria-hidden="true">◒</span> Stock Analysis / 03</span><span class="back-label" data-lang="en">← All companies</span><span class="back-label" data-lang="ro" hidden>← Toate companiile</span></a>'
    if default == 'ro':
        home_link = home_link.replace('data-lang="en">', 'data-lang="en" hidden>').replace('data-lang="ro" hidden>', 'data-lang="ro">')
    return f'''<!doctype html><html lang="{default}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(data["company"]["name"])} — Stock Analysis</title><style>{css}</style></head><body data-reading="beginner"><a class="skip" href="#main">Skip to report</a><div class="layout"><aside class="sidebar">{home_link}{nav}</aside><main id="main"><div class="toolbar"><label>Language / Limbă<select id="language">{opts}</select></label><label>Reading / Lectură<select id="reading"><option value="beginner">Guided / Ghidat</option><option value="experienced">Detailed / Detaliat</option></select></label><label>Theme / Temă<select id="theme"><option value="dark">Dark / Întunecată</option><option value="light">Light / Luminoasă</option></select></label><button id="expand-lessons" aria-expanded="false">Explain all / Explică tot</button><button id="open-sources">Evidence / Dovezi</button></div><noscript><p class="nojs">Interactive evidence and language controls require JavaScript. The main report remains readable.</p></noscript>{main}</main></div><dialog id="evidence-dialog" aria-label="Sources and calculations"><div class="dialog-head"><h2>Sources & calculation / Surse și calcul</h2><button id="close-sources" autofocus>Close / Închide</button></div><label for="evidence-search">Search evidence / Caută dovezi</label><input id="evidence-search" type="search">{evidence}</dialog><script type="application/json" id="visual-package">{visual_embedded}</script><script type="application/json" id="research-package">{embedded}</script><script>{js}</script></body></html>'''


def compare(reports, spec):
    """Integrated evidence table; incompatible rows remain explicitly incomparable."""
    need(len(reports) >= 2, "Comparison requires at least two companies")
    for d in reports:
        need(d["mode"] != "update", "For comparison use full/focused snapshots, or extract a separately validated current snapshot")
        validate(d)
    lang = spec.get("language", "en")
    need(lang in {"en","ro"}, "Invalid comparison language")
    report_map = {d["report_id"]:d for d in reports}
    need(len(report_map) == len(reports), "Duplicate comparison report ID")
    output = ''
    for row in spec["rows"]:
        need(text_ok_compare(row.get("interpretation")), "Author a company-specific comparison interpretation")
        need(set(row["values"]) == set(report_map), "Every comparison row must address every company")
        records, cells = [], []
        for rid,d in report_map.items():
            ev = {e["id"]:e for e in d["evidence"]}
            key = row["values"][rid]
            need(key in ev, "Unknown comparison evidence")
            e = ev[key]
            need('value' in e, "Comparison row needs numeric evidence; use prose for unavailable comparisons")
            records.append(e)
            sources = {s["id"]:s for s in d["sources"]}
            roots, todo = [], [key]
            while todo:
                item = ev[todo.pop()]
                if item.get('source_id'):
                    roots.append(sources[item['source_id']])
                todo.extend(item.get('inputs',[]))
            links = ' '.join(f'<a href="{h(s["url"])}">{h(t(s["title"],lang))}</a>' for s in {s['id']:s for s in roots}.values())
            cells.append(f'<td><strong>{h(format_number(e,lang))}</strong><p class="meta">{h(e["period"]["label"])} · {h(e["basis"])} · {h(e["definition"])}</p>{links}</td>')
        compatible = all(dimensions(e)==dimensions(records[0]) and period_key(e)==period_key(records[0]) and e['definition']==records[0]['definition'] for e in records)
        need(compatible or row.get('status') == 'Not comparable', "Incompatible comparison requires Not comparable status")
        need(row.get('status') in {'Comparable','Not comparable'}, "Comparison status required")
        output += f'<tr><th>{h(t(row["question"],lang))}</th>{"".join(cells)}<td><strong>{h(row["status"])}</strong><p>{h(t(row["interpretation"],lang))}</p></td></tr>'
    css = (ASSETS/'report.css').read_text()
    names = ''.join(f'<th>{h(d["company"]["name"])}<p class="meta">{h(d["cutoff"])}</p></th>' for d in reports)
    need(text_ok_compare(spec.get('summary')), "Comparison conclusion required")
    return f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Company comparison</title><style>{css}</style></head><body><main style="max-width:1200px;padding:40px 24px;margin:auto"><div class="kicker">Stock Analysis / Comparison</div><h1>{h(t(spec["title"],lang))}</h1><p class="lead">{h(t(spec["summary"],lang))}</p><p class="notice">{h(t(spec["limitations"],lang))}</p><div class="table-wrap"><table><thead><tr><th>Question</th>{names}<th>Interpretation</th></tr></thead><tbody>{output}</tbody></table></div></main></body></html>'


def text_ok_compare(value):
    return isinstance(value, (str,dict)) and bool(value)

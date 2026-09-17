#!/usr/bin/env python3
"""Render a validated research snapshot, including optional evidence-backed tables."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/stock-analysis/scripts'))
import render as core
from model import claim, format_number, load, need, text_ok, validate


def tables_html(tables, evidence, lang):
    output = ''
    for table in tables:
        need(text_ok(table.get('title')), 'Table title requires both languages')
        columns = table.get('columns', [])
        need(bool(columns) and all(text_ok(c) for c in columns), 'Invalid table columns')
        output += '<div class="table-wrap"><table class="research-table"><caption>'
        output += core.h(core.t(table['title'], lang)) + '</caption><thead><tr>'
        output += ''.join('<th scope="col">' + core.h(core.t(c, lang)) + '</th>' for c in columns)
        output += '</tr></thead><tbody>'
        for row in table.get('rows', []):
            need(len(row) == len(columns), 'Table row width does not match columns')
            output += '<tr>'
            for column, cell in zip(columns, row):
                if 'evidence_ref' in cell:
                    key = cell['evidence_ref']
                    need(key in evidence, 'Unknown table evidence reference')
                    e = evidence[key]
                    value = format_number(e, lang) if 'value' in e else core.t(e['state'], lang)
                    content = core.h(value) + core.ref_buttons([key], lang)
                else:
                    claim(cell, evidence)
                    content = core.h(core.t(cell['text'], lang)) + core.ref_buttons(cell.get('evidence_refs', []), lang)
                output += '<td data-label="' + core.h(core.t(column, lang)) + '">' + content + '</td>'
            output += '</tr>'
        output += '</tbody></table></div>'
    return output


def render(data, baseline=None, archive=None):
    validate(data, baseline)
    original = core.section_html

    def section_with_tables(section, evidence, lang, index, sources):
        html = original(section, evidence, lang, index, sources)
        # Keep the existing authored assumptions visible beside a guided model
        # result, without changing any archived research or calculation inputs.
        model_inputs = set()
        pending = [m['evidence_ref'] for m in section.get('guide', {}).get('metrics', [])
                   if evidence[m['evidence_ref']].get('basis') == 'model']
        while pending:
            key = pending.pop()
            if key in model_inputs:
                continue
            model_inputs.add(key)
            pending.extend(evidence[key].get('inputs', []))
        assumptions = [c for c in section.get('claims', [])
                       if c['type'] == 'model' and model_inputs.intersection(c.get('evidence_refs', []))]
        if assumptions:
            heading = core.tr(lang, 'Assumptions behind the displayed scenario',
                              'Ipotezele scenariului afișat')
            note = '<aside class="scenario-assumptions"><h3>' + heading + '</h3>'
            note += core.claims(assumptions, lang) + '</aside>'
            html = html.replace('<details class="deep-data">', note + '<details class="deep-data">', 1)
        tables = tables_html(section.get('tables', []), evidence, lang)
        ending = '</div></details></section>' if section.get('guide') else '</section>'
        need(html.endswith(ending), 'Unexpected section layout')
        return html[:-len(ending)] + tables + ending

    core.section_html = section_with_tables
    try:
        html = core.render(data, baseline, archive)
    finally:
        core.section_html = original
    css = '<style>.research-table{min-width:600px;width:100%;border-collapse:collapse}.research-table caption{text-align:left;font-weight:700;padding:20px 0 12px}.research-table th,.research-table td{vertical-align:top;padding:12px;border-bottom:1px solid var(--line,#ddd);font-size:.88rem}.research-table th{text-align:left}.research-table .ref{white-space:normal}.table-wrap{max-width:100%;overflow-x:auto;margin:16px 0}.scenario-assumptions{font-size:15px;border-left:2px solid var(--warn);padding:4px 0 1px 18px;margin:24px 0}.scenario-assumptions h3{font-size:15px}</style>'
    return html.replace('</head>', css + '</head>')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('research')
    parser.add_argument('--archive')
    parser.add_argument('--baseline')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(load(args.research), load(args.baseline) if args.baseline else None,
                             load(args.archive) if args.archive else None), encoding='utf-8')
    print(output)

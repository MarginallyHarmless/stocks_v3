#!/usr/bin/env python3
"""Validate and render manually authored market landscapes from frozen run inputs."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/stock-analysis/scripts'))
from model import digest
from render import fonts_css
from company_index import repository_file


def validate(data, manifest):
    assert data['kind']=='market_landscape' and data['schema_version']=='market-landscape-1'
    assert data['run_id']==manifest['run_id'] and data['cutoff']==manifest['cutoff']
    assert data['window_start']==manifest['window_start']
    assert data['delivery']=='on_demand_only'
    assert manifest['status']=='ready', 'Resolve blocked scope before rendering a complete universe'
    assert len(data['companies'])==len(manifest['companies'])
    assert {c['identity'] for c in data['companies']}==set(manifest['companies'])
    assert sum(len(c['questions']) for c in data['companies'])==manifest['question_count']
    source_ids={s['id'] for s in data['sources']}
    assert len(source_ids)==len(data['sources'])
    for s in data['sources']:
        assert s['url'].startswith('https://') and s['access']=='free'
        assert not s['published_date'] or s['published_date']<=data['cutoff'][:10]
    event_ids={e['id'] for e in data['events']}
    assert len(event_ids)==len(data['events'])
    for e in data['events']:
        assert set(e['source_ids'])<=source_ids and e['source_ids']
        assert e['date']<=data['cutoff'][:10]
        assert e['fact']['en'] and e['fact']['ro']
    for c in data['companies']:
        baseline=manifest['companies'][c['identity']]
        assert c['report_id']==baseline['report_id']
        assert c['report_cutoff']==baseline['report_cutoff']
        original=[q['question'] for q in c['questions']]
        assert digest(original)==baseline['questions_sha256'], 'Saved question or criterion changed'
        assert all(q['criterion_outcome'] is None for q in c['questions']), 'Landscape cannot resolve earnings tests'
        assert set(c['event_ids'])<=event_ids
        for q in c['questions']:
            assert set(q['event_ids'])<=set(c['event_ids'])
            assert q['state'] in {'context_added','unverified_lead','no_decisive_new_evidence'}
    assert set(data['summary_sources'])<=source_ids
    for item in data['calendar']:
        assert set(item['source_ids'])<=source_ids and item['source_ids']
    for item in data['new_questions']:
        assert set(item['event_ids'])<=event_ids
    for theme in data['themes']:
        assert set(theme['sources'])<=source_ids
        for metric in theme['metrics']:
            assert metric['source'] in source_ids
            assert metric['date']<=data['cutoff'][:10]
    for series in data['series'].values():
        assert 'parse_error' not in series and series['source']['status']=='retrieved'
        days=[]
        for obs in series['observations']:
            assert obs['date']<=data['cutoff'][:10] and math.isfinite(obs['value'])
            days.append(obs['date'])
        assert days==sorted(set(days))
    assert data['question_outcomes_resolved']==0
    if data.get('news_reading_standard')=='beginner-news-1':
        for item in data['events']+data['themes']:
            for key in ('context','meaning','watch'):
                assert set(item[key])=={'en','ro'} and all(item[key].values()), 'Missing beginner explanation'
        pulse=data['market_pulse_guide']
        assert pulse['paragraphs'] and set(pulse['source_ids'])<=source_ids
        assert all(set(p)=={'en','ro'} and all(p.values()) for p in pulse['paragraphs'])
    return data


def validate_guide(guide, data):
    assert guide['schema_version']=='market-reading-guide-1'
    assert guide['editorial_only'] is True
    assert guide['run_id']==data['run_id'] and guide['cutoff']==data['cutoff']
    def bilingual(value):
        assert set(value)=={'en','ro'} and all(isinstance(v,str) and v.strip() for v in value.values())
    bilingual(guide['revision_note'])
    for category, source_key in [('events','source_ids'),('themes','sources')]:
        originals={item['id']:item for item in data[category]}
        assert set(guide[category])==set(originals), 'Every selected story needs a beginner explanation'
        for identity, item in guide[category].items():
            assert set(item)=={'context','meaning','watch','source_ids'}
            assert set(item['source_ids'])==set(originals[identity][source_key]), 'Editorial revision cannot add source evidence'
            for key in ('context','meaning','watch'):bilingual(item[key])
    pulse=guide['market_pulse']
    assert set(pulse['source_ids'])<=set(s['id'] for s in data['sources'])
    assert pulse['paragraphs']
    for p in pulse['paragraphs']:bilingual(p)
    return guide


def render(data, manifest, guide=None, successor=None):
    validate(data,manifest)
    presentation=copy.deepcopy(data)
    if guide:presentation['reading_guide']=validate_guide(guide,data)
    if successor:presentation['newer_version']=successor
    payload=json.dumps(presentation,ensure_ascii=False,allow_nan=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    html=(ROOT/'assets/market-sweep.html').read_text()
    return html.replace('/*FONTS*/',fonts_css()).replace('/*CSS*/',(ROOT/'assets/market-sweep.css').read_text()).replace('/*JS*/',(ROOT/'assets/market-sweep.js').read_text()).replace('"__DATA__"',payload)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path)
    p.add_argument('--out',type=Path)
    p.add_argument('--all',action='store_true')
    args=p.parse_args()
    if args.all:
        registry=json.loads((ROOT/'market-sweep-registry.json').read_text())
        jobs=[(repository_file(ROOT,x['data_path']), ROOT/x['html_path'], x) for x in registry['reports']]
    else:
        if not args.data or not args.out:p.error('Use --all or provide --data and --out')
        jobs=[(args.data,args.out,None)]
    for path,out,entry in jobs:
        data=json.loads(path.read_text())
        manifest_path=repository_file(ROOT,data['manifest_path'])
        manifest=json.loads(manifest_path.read_text())
        if entry:
            assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['data_sha256'], 'Report ledger differs from saved registry hash'
            assert data['manifest_path']==entry['manifest_path']
            assert hashlib.sha256(manifest_path.read_bytes()).hexdigest()==entry['manifest_sha256'], 'Manifest differs from saved registry hash'
            assert data['run_id']==entry['run_id'] and data['cutoff']==entry['cutoff']
        revisions=entry.get('presentation_revisions',[]) if entry else []
        if revisions:
            assert revisions[-1]['html_path']==entry['html_path']
            out=ROOT/entry['original_html_path']
        out.parent.mkdir(parents=True,exist_ok=True)
        successor=Path(entry['html_path']).name if revisions else None
        out.write_text(render(data,manifest,successor=successor))
        for revision in revisions:
            guide_path=repository_file(ROOT,revision['guide_path'])
            assert hashlib.sha256(guide_path.read_bytes()).hexdigest()==revision['guide_sha256']
            guide=json.loads(guide_path.read_text())
            assert guide['revision_id']==revision['revision_id']
            assert guide['base_data_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
            revision_out=ROOT/revision['html_path']
            revision_out.parent.mkdir(parents=True,exist_ok=True)
            revision_out.write_text(render(data,manifest,guide=guide))
        print(f'Validated and rendered {data["run_id"]}: {len(data["companies"])} companies')


if __name__=='__main__':main()

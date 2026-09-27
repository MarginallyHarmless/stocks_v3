#!/usr/bin/env python3
"""Freeze the current research universe for a market/news sweep. No network or scheduling."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/stock-analysis/scripts'))
from archive import verify_archive
from model import digest, identity


def instant(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Timestamps must include a timezone')
    return result


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def diff_universe(current, previous):
    if previous is None:
        return {'baseline': 'first_run', 'companies_added': sorted(current),
                'companies_removed': [], 'companies_changed': {}}
    old = previous['companies']
    changes = {}
    for key in sorted(current.keys() & old.keys()):
        now, before = current[key], old[key]
        if now.get('status') != 'ready' or before.get('status') != 'ready':
            changes[key] = {'comparison_status': 'unavailable',
                            'reason': 'One manifest could not load this company; do not infer question removals.'}
            continue
        nw = {w['id']: w for w in now.get('questions', [])}
        ow = {w['id']: w for w in before.get('questions', [])}
        changed = [q for q in sorted(nw.keys() & ow.keys()) if digest(nw[q]) != digest(ow[q])]
        record = {'questions_added': sorted(nw.keys() - ow.keys()),
                  'questions_removed': sorted(ow.keys() - nw.keys()),
                  'questions_changed': changed,
                  'report_changed': now.get('report_id') != before.get('report_id'),
                  'identity_metadata_changed': now['company'] != before['company'],
                  'same_version_content_changes': [q for q in changed if
                      nw[q].get('criterion_version') == ow[q].get('criterion_version')]}
        if any(record.values()):
            changes[key] = record
    return {'baseline': previous.get('run_id'),
            'companies_added': sorted(current.keys() - old.keys()),
            'companies_removed': sorted(old.keys() - current.keys()),
            'companies_changed': changes}


def prepare(repo, start, cutoff, run_id, previous=None):
    repo = Path(repo).resolve()
    if instant(start) >= instant(cutoff):
        raise ValueError('Window start must precede cutoff')
    registry_path = repo / 'stock-analysis-registry.json'
    raw = registry_path.read_bytes()
    registry = json.loads(raw)
    if registry.get('kind') != 'company_registry' or not isinstance(registry.get('companies'), dict):
        raise ValueError('Invalid company registry')
    companies = {}
    for key, entry in sorted(registry['companies'].items()):
        record = {'company': copy.deepcopy(entry['company']), 'report_id': entry.get('latest_report_id'),
                  'questions': [], 'status': 'pending', 'errors': []}
        companies[key] = record  # Preserve the row even if its archive cannot be loaded.
        try:
            archive_path = (repo / entry['archive_path']).resolve()
            archive_path.relative_to(repo)
            archive = verify_archive(read_json(archive_path))
            if archive['identity'] != key or identity(entry['company']) != key:
                raise ValueError('Registry/archive security identity mismatch')
            snapshot = archive['snapshots'][entry['latest_report_id']]
            research = snapshot['research']
            if instant(research['cutoff']) > instant(cutoff):
                raise ValueError('Latest research is later than this sweep cutoff; choose an earlier registry revision')
            questions = copy.deepcopy(research.get('watchlist', []))
            if not questions:
                raise ValueError('Latest saved report has no follow-up questions')
            if len({w['id'] for w in questions}) != len(questions):
                raise ValueError('Duplicate question IDs within company')
            refs = {ref for w in questions for ref in w.get('baseline_refs', [])}
            record.update({
                'status': 'ready', 'archive_path': entry['archive_path'],
                'archive_sha256': digest(archive), 'report_sha256': snapshot['sha256'],
                'report_cutoff': research['cutoff'],
                'retrospective_questions_postdate_window_start': instant(research['cutoff']) > instant(start),
                'questions': questions, 'questions_sha256': digest(questions),
                'baseline_evidence': [copy.deepcopy(e) for e in research.get('evidence', []) if e['id'] in refs],
                'sources': copy.deepcopy(research.get('sources', [])),
                'next_event': copy.deepcopy(research.get('next_event')),
                'search_brief': {
                    'names': list(dict.fromkeys([entry['company']['name'], entry['company']['ticker'],
                                               *entry.get('ticker_aliases', [])])),
                    'direct_company_scan': True,
                    'questions': [{'id': w['id'], 'question': w['question'], 'why': w.get('why'),
                                   'due_period': w.get('due_period'), 'criterion': w.get('criterion')}
                                  for w in questions],
                    'independent_new_risk_scan': True,
                },
            })
        except (ValueError, KeyError, TypeError, OSError) as exc:
            record['status'] = 'blocked'
            record['errors'].append(str(exc))
    try:
        commit = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'],
                                         text=True, stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain', '--',
                     'stock-analysis-registry.json', 'archives/'],
                     text=True, stderr=subprocess.DEVNULL).strip())
    except subprocess.CalledProcessError:
        commit, dirty = None, None
    return {
        'schema_version': 'market-sweep-manifest-1', 'kind': 'market_sweep_manifest',
        'run_id': run_id, 'window_start': start, 'cutoff': cutoff,
        'selection_policy': 'all_current_registry_entries_latest_report_id',
        'purpose': 'on_demand_market_landscape_using_frozen_questions_not_a_point_in_time_backtest',
        'repository': 'MarginallyHarmless/stocks_v3', 'repository_commit': commit,
        'research_inputs_dirty': dirty, 'registry_sha256': hashlib.sha256(raw).hexdigest(),
        'status': 'ready' if all(v['status'] == 'ready' for v in companies.values()) and companies else 'partial',
        'company_count': len(companies), 'question_count': sum(len(c['questions']) for c in companies.values()),
        'companies': companies, 'changes': diff_universe(companies, previous),
        'policy': {
            'paid_sources_allowed': False, 'earnings_review_flags_may_be_cleared': False,
            'question_outcomes_require_compatible_evidence': True,
            'questions_may_be_rewritten_by_news_collector': False,
            'coverage_failure_means_no_news': False,
        },
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=ROOT)
    p.add_argument('--start', required=True)
    p.add_argument('--cutoff', required=True)
    p.add_argument('--run-id', required=True)
    p.add_argument('--previous', type=Path)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    result = prepare(args.repo, args.start, args.cutoff, args.run_id,
                     read_json(args.previous) if args.previous else None)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation: preserve earlier run inputs, even if rerunning the same command.
    with args.out.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({k: result[k] for k in ['run_id', 'status', 'company_count', 'question_count']}))
    return 0 if result['status'] == 'ready' else 2


if __name__ == '__main__':
    raise SystemExit(main())

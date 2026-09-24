"""Portable company index derived from the persistent registry and saved reports."""
from __future__ import annotations
import base64
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import re
from model import need, timestamp

ASSETS = Path(__file__).resolve().parents[1] / 'assets'


def repository_file(root, name):
    """Resolve a portable repo-relative path and reject traversal or missing files."""
    need(isinstance(name, str) and bool(re.fullmatch(r'[A-Za-z0-9_./-]+', name)), 'Invalid repository path')
    need(not name.startswith('/') and all(p not in {'', '.', '..'} for p in name.split('/')), 'Expected repository-relative file path')
    root = Path(root).resolve()
    path = (root / name).resolve()
    need(path.is_relative_to(root) and path.is_file(), f'Missing repository file: {name}')
    return path


EVENT_FIELDS = {'confidence', 'date', 'time', 'timezone', 'checked_at', 'source_id', 'basis'}


def enrich_entry(previous, reports):
    """Retain schedules by financial period, including unreviewed older periods."""
    entry = copy.deepcopy(previous)
    events = {e['period']: copy.deepcopy(e) for e in entry.get('earnings_events', [])}
    for report in reports:
        event = report.get('next_event')
        if event and event.get('kind') == 'results':
            old = events.get(event['period'], {})
            # A fresh standalone calendar check must survive an older ledger.
            if event.get('checked_at', '') >= old.get('checked_at', ''):
                if 'scheduled_at' not in event and (event.get('date') != old.get('date') or event.get('confidence') != 'Confirmed'):
                    old.pop('scheduled_at', None)
                # Schedule fields the newer event omits are stale; registry-owned keys stay.
                for key in EVENT_FIELDS - set(event):
                    old.pop(key, None)
                old.update(copy.deepcopy(event))
                source = next((s for s in report['sources'] if s['id'] == event.get('source_id')), {})
                old['source_url'] = source.get('url')
                old['source_title'] = source.get('title')
            if not old.get('reviewed_report_id') and not (report.get('review', {}).get('release', {}).get('status') == 'pending'):
                old['baseline_report_id'] = report['report_id']
            old.setdefault('reviewed_report_id', None)
            events[event['period']] = old
        review = report.get('review', {})
        release = review.get('release', {})
        if release.get('status') == 'published':
            parent = next((r for r in reports if r['report_id'] == report.get('parent_report_id')), {})
            period = release['period']
            # Only the actual saved baseline/release pair clears its period.
            if parent.get('next_event', {}).get('period') == period and period in events:
                source = next((s for s in report['sources'] if s['id'] == release['source_id']), {})
                events[period].update(publication_status='published', published_at=release['published_at'],
                    publication_source_url=source.get('url'), reviewed_report_id=report['report_id'],
                    review_provisional=review['provisional'], reviewed_at=report['cutoff'])
    entry['earnings_events'] = list(events.values())
    latest = reports[-1]
    entry['latest_report_id'] = latest['report_id']
    entry['latest_cutoff'] = latest['cutoff']
    entry['watch_count'] = len(latest['watchlist'])
    if entry.get('card', {}).get('report_id') != latest['report_id']:
        logo = {k:v for k,v in entry.get('card', {}).items() if k.startswith('logo_')}
        entry['card'] = {**logo, 'report_id': latest['report_id'],
                         'summary': latest['summary'][0]['text']}
    return entry


def validate_registry(registry):
    need(registry.get('kind') == 'company_registry', 'Expected company registry')
    for key, entry in registry['companies'].items():
        c = entry['company']
        need(key == c['issuer_id'] + '|' + c['security_id'], 'Registry identity mismatch')
        ids = {r['report_id'] for r in entry['reports']}
        periods = set()
        for e in entry.get('earnings_events', []):
            need(e['period'] not in periods, 'Duplicate earnings period')
            periods.add(e['period'])
            need(e['kind'] == 'results', 'Calendar only includes results releases')
            need(e['confidence'] in {'Confirmed','Estimated','Not announced'}, 'Invalid date confidence')
            need(e.get('reviewed_report_id') is None or e['reviewed_report_id'] in ids, 'Unknown reviewed report')
            if e.get('date'):
                datetime.strptime(e['date'], '%Y-%m-%d')
            need((e.get('date') is None) == (e['confidence'] == 'Not announced'), 'Date and confidence must agree')
            try:
                ZoneInfo(e.get('timezone', 'UTC'))
            except (ZoneInfoNotFoundError, ValueError) as exc:
                raise ValueError('Invalid issuer timezone') from exc
            if e.get('scheduled_at'):
                need(e['confidence'] == 'Confirmed', 'Exact release time must be confirmed')
                timestamp(e['scheduled_at'])
            if e.get('publication_status') == 'published':
                timestamp(e['published_at'])
                need(bool(e.get('publication_source_url')), 'Publication requires a source')
    return registry


def render_index(registry, reports_dir=None, repo_root=None):
    validate_registry(registry)
    payload = copy.deepcopy(registry)
    payload['generated_at'] = datetime.now(timezone.utc).isoformat()
    embedded = {}
    if repo_root:
        need(not reports_dir, 'Choose repository links or embedded reports')
        for entry in payload['companies'].values():
            report = next((r for r in entry['reports'] if r['report_id'] == entry.get('latest_report_id')), {})
            repository_file(repo_root, report.get('html_path'))
            repository_file(repo_root, entry.get('archive_path'))
    if reports_dir:
        root = Path(reports_dir).resolve()
        for key, entry in payload['companies'].items():
            report = next((r for r in entry['reports'] if r['report_id'] == entry.get('latest_report_id')), {})
            name = report.get('html_filename')
            if name:
                need(Path(name).name == name, 'Report filename must not contain a path')
                path = root / name
                need(path.is_file(), f'Materialize latest report before rendering: {name}')
                embedded[key] = base64.b64encode(path.read_bytes()).decode('ascii')
    payload['embedded_reports'] = embedded
    safe = json.dumps(payload, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    from render import fonts_css  # same embedded fonts as the reports; imported late to avoid a cycle
    return (ASSETS / 'company-index.html').read_text().replace('/*INDEX_FONTS*/', fonts_css()).replace('/*INDEX_CSS*/', (ASSETS / 'company-index.css').read_text()).replace('/*INDEX_LOGIC*/', (ASSETS / 'company-index-state.js').read_text()).replace('/*INDEX_UI*/', (ASSETS / 'company-index.js').read_text()).replace('"__INDEX_DATA__"', safe)

#!/usr/bin/env python3
"""Run once on request: collect free SEC metadata, official feeds and FRED data.

This discovers evidence; it does not decide materiality or write investment conclusions.
"""
import argparse
import csv
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import hashlib
import io
import json
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from prepare_market_sweep import instant

SERIES = {
    'DGS10': ('US 10-year Treasury yield', 'percent'),
    'DCOILBRENTEU': ('Brent spot oil price', 'USD per barrel'),
    'DEXUSEU': ('US dollars per euro', 'USD per EUR'),
}
FEEDS = {'fed': 'https://www.federalreserve.gov/feeds/press_all.xml',
         'ecb': 'https://www.ecb.europa.eu/rss/press.html'}


def get(url, user_agent):
    """At most one short retry. A failed source always remains explicit."""
    result = {'url': url, 'status': 'unavailable', 'attempts': []}
    for attempt in range(2):
        stamp = datetime.now(timezone.utc).isoformat()
        try:
            req = urllib.request.Request(url, headers={'User-Agent': user_agent})
            with urllib.request.urlopen(req, timeout=20) as r:
                raw = r.read()
                result.update(status='retrieved', retrieved_at=stamp, http_status=r.status,
                              content_type=r.headers.get('Content-Type'),
                              response_sha256=hashlib.sha256(raw).hexdigest())
                result['attempts'].append({'at': stamp, 'http_status': r.status})
                return raw, result
        except (OSError, urllib.error.URLError) as exc:
            code = getattr(exc, 'code', None)
            result['attempts'].append({'at': stamp, 'http_status': code, 'error': str(exc)})
            result['error'] = str(exc)
            if attempt or code not in (429, 500, 502, 503, 504):
                break
            retry = getattr(exc, 'headers', {}).get('Retry-After', '3')
            if not retry.isdigit() or int(retry) > 10:
                result['retry_deferred'] = True
                break
            time.sleep(max(1, int(retry)))
    return None, result


def select_filings(table, cik, start, cutoff):
    selected = []
    for i, day in enumerate(table.get('filingDate', [])):
        acceptance = table.get('acceptanceDateTime', [])
        accepted = acceptance[i] if i < len(acceptance) else ''
        if accepted:
            stamp = instant(accepted)
            inside = start <= stamp <= cutoff
        else:
            # Date-only records are candidates; exact boundary inclusion needs review.
            inside = start.date().isoformat() <= day <= cutoff.date().isoformat()
        if inside:
            accession = table['accessionNumber'][i]
            selected.append({'accession': accession, 'form': table['form'][i], 'filed': day,
                             'accepted_at': accepted or None,
                             'boundary_review_required': not bool(accepted),
                             'url': f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/'
                                    f'{accession.replace("-", "")}/{table["primaryDocument"][i]}',
                             'review_status': 'discovered_not_read'})
    return selected


def collect(manifest, user_agent):
    start, cutoff = instant(manifest['window_start']), instant(manifest['cutoff'])
    result = {'run_id': manifest['run_id'], 'window_start': manifest['window_start'],
              'cutoff': manifest['cutoff'], 'mode': 'on_demand', 'companies': [],
              'feeds': {}, 'series': {}, 'limitations': [
                  'SEC metadata is discovery, not document review; subsidiary issuers need separate checks.',
                  'RSS feeds can be truncated; no historical completeness is inferred.',
                  'FRED values are retrieved vintages and can be revised; this is not a point-in-time backtest.',
                  'Issuer, counterparty, regulator and public news reading is a separate manual research step.']}
    mapping = None
    for key, company in manifest['companies'].items():
        co = company['company']
        row = {'identity': key, 'ticker': co['ticker'], 'status': 'unavailable', 'sources': [], 'filings': []}
        result['companies'].append(row)
        try:
            if co['issuer_id'].startswith('CIK:'):
                cik = co['issuer_id'].split(':', 1)[1].zfill(10)
            else:
                if mapping is None:
                    raw, meta = get('https://www.sec.gov/files/company_tickers.json', user_agent)
                    result['sec_identity_mapping'] = meta
                    mapping = json.loads(raw) if raw else {}
                matches = [x for x in mapping.values() if x['ticker'] == co['ticker']]
                if len(matches) != 1:
                    raise ValueError('SEC CIK mapping is ambiguous or unavailable')
                cik = str(matches[0]['cik_str']).zfill(10)
            raw, meta = get(f'https://data.sec.gov/submissions/CIK{cik}.json', user_agent)
            row['sources'].append(meta)
            if raw is None:
                continue
            data = json.loads(raw)
            if str(data['cik']).zfill(10) != cik or co['ticker'] not in data.get('tickers', []):
                raise ValueError('SEC identity/ticker mismatch: manual resolution required')
            if co['issuer_id'].startswith('SEC-FILE:'):
                if co['issuer_id'].split(':', 1)[1] not in data['filings']['recent'].get('fileNumber', []):
                    raise ValueError('SEC file-number mapping could not be verified')
            row.update(status='checked', cik=cik, issuer_name=data['name'])
            row['filings'] = select_filings(data['filings']['recent'], cik, start, cutoff)
            for archive in data['filings'].get('files', []):
                if archive['filingTo'] < start.date().isoformat() or archive['filingFrom'] > cutoff.date().isoformat():
                    continue
                raw, meta = get('https://data.sec.gov/submissions/' + archive['name'], user_agent)
                row['sources'].append(meta)
                if raw is None:
                    row['status'] = 'partial'
                else:
                    row['filings'].extend(select_filings(json.loads(raw), cik, start, cutoff))
            row['filings'] = list({f['accession']: f for f in row['filings']}.values())
        except (ValueError, TypeError, KeyError) as exc:
            row.update(status='partial' if row['filings'] else 'unavailable', error=str(exc))
        print(f"{co['ticker']}: {row['status']}, {len(row['filings'])} filing candidates", flush=True)
        time.sleep(.2)
    for name, url in FEEDS.items():
        raw, meta = get(url, user_agent)
        feed = {'source': meta, 'items': [], 'coverage': 'feed_only_not_exhaustive'}
        result['feeds'][name] = feed
        if raw:
            try:
                root = ET.fromstring(raw)
                for item in root.findall('.//item'):
                    date = item.findtext('pubDate')
                    stamp = parsedate_to_datetime(date) if date else None
                    if stamp and start <= stamp <= cutoff:
                        feed['items'].append({'title': item.findtext('title'), 'url': item.findtext('link'),
                                              'published_at': stamp.isoformat(), 'review_status': 'discovered_not_read'})
            except (ET.ParseError, ValueError, TypeError) as exc:
                feed['parse_error'] = str(exc)
    for sid, (label, unit) in SERIES.items():
        query = urllib.parse.urlencode({'id': sid, 'cosd': (start - timedelta(days=14)).date().isoformat(),
                                       'coed': cutoff.date().isoformat()})
        raw, meta = get('https://fred.stlouisfed.org/graph/fredgraph.csv?' + query, user_agent)
        series = {'label': label, 'unit': unit, 'source': meta, 'observations': []}
        result['series'][sid] = series
        if raw:
            try:
                reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
                if not reader.fieldnames or sid not in reader.fieldnames:
                    raise ValueError('Expected FRED CSV schema, not an HTML page')
                for item in reader:
                    day = item.get('observation_date', item.get('DATE'))
                    if day and day <= cutoff.date().isoformat() and item[sid] not in ('', '.'):
                        series['observations'].append({'date': day, 'value': float(item[sid])})
            except (ValueError, UnicodeDecodeError) as exc:
                series['parse_error'] = str(exc)
    result['prepared_at'] = datetime.now(timezone.utc).isoformat()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--user-agent', default='StocksV3Research/1.0 https://github.com/MarginallyHarmless/stocks_v3')
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Output exists: choose a new attempt filename to preserve collection history')
    data = collect(json.loads(args.manifest.read_text()), args.user_agent)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
    print(f'Saved {args.out}')


if __name__ == '__main__':
    main()

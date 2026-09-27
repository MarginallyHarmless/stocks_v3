#!/usr/bin/env python3
"""Prepare one user-triggered sweep; no scheduling or background work."""
import argparse
from datetime import datetime, timedelta
import json
from pathlib import Path
from zoneinfo import ZoneInfo
from prepare_market_sweep import ROOT, instant, prepare, read_json


def select_window(reports, cutoff, explicit_start=None):
    applicable=[r for r in reports if instant(r['cutoff'])<instant(cutoff)]
    prior=max(applicable,key=lambda r:instant(r['cutoff'])) if applicable else None
    start=explicit_start or ((instant(prior['cutoff'])-timedelta(hours=48)).isoformat() if prior else
                             (instant(cutoff)-timedelta(days=7)).isoformat())
    return prior,start


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True,type=Path,help='New run directory')
    parser.add_argument('--cutoff',help='Timezone-aware ISO timestamp; defaults to now in Bucharest')
    parser.add_argument('--start',help='Explicit research window; otherwise previous landscape minus 48h, or last 7 days')
    args=parser.parse_args()
    if args.out.exists():parser.error('Choose a new output directory; earlier runs are preserved')
    cutoff=args.cutoff or datetime.now(ZoneInfo('Europe/Bucharest')).isoformat(timespec='seconds')
    registry_path=ROOT/'market-sweep-registry.json'
    reports=[]
    if registry_path.exists():
        registry=read_json(registry_path)
        reports=registry['reports']
    prior,start=select_window(reports,cutoff,args.start)
    previous=read_json(ROOT/prior['manifest_path']) if prior else None
    result=prepare(ROOT,start,cutoff,args.out.name,previous)
    result['invocation']='user_triggered_only'
    result['previous_landscape_cutoff']=prior['cutoff'] if prior else None
    result['overlap_hours']=48 if prior and not args.start else 0
    result['previous_landscape_report']=prior['data_path'] if prior else None
    args.out.mkdir(parents=True)
    with (args.out/'manifest.json').open('x') as stream:
        json.dump(result,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({k:result[k] for k in ('run_id','status','company_count','question_count','window_start','cutoff')}))
    return 0 if result['status']=='ready' else 2


if __name__=='__main__':raise SystemExit(main())

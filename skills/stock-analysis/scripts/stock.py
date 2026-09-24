#!/usr/bin/env python3
"""Stock Analysis command line. Run `python3 stock.py --help`."""
import argparse
import json
import sys
from pathlib import Path
from archive import baseline, catalog, register, verify_archive, write_json
from model import Invalid, digest, load, recompute, validate
from render import render, compare


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("validate", "render", "recompute"):
        cmd = sub.add_parser(name)
        cmd.add_argument("research")
        cmd.add_argument("--baseline")
        if name == "render":
            cmd.add_argument("--archive")
            cmd.add_argument("--visuals", help="Dated visual supplement for this exact security")
        if name != "validate":
            cmd.add_argument("--out", required=True)
    cmd = sub.add_parser("register")
    cmd.add_argument("research")
    cmd.add_argument("--archive", required=True)
    cmd.add_argument("--expected-hash")
    cmd = sub.add_parser("baseline")
    cmd.add_argument("archive")
    cmd.add_argument("--identity", required=True)
    cmd.add_argument("--report-id")
    cmd.add_argument("--before")
    cmd.add_argument("--out", required=True)
    cmd = sub.add_parser("verify-archive")
    cmd.add_argument("archive")
    cmd = sub.add_parser("catalog")
    cmd.add_argument("archive")
    cmd.add_argument("--registry", required=True)
    cmd.add_argument("--library-file-id")
    cmd.add_argument("--filename")
    cmd.add_argument("--report-file-id")
    cmd.add_argument("--report-filename")
    cmd.add_argument("--card")
    cmd.add_argument("--repo-root")
    cmd.add_argument("--repository")
    cmd.add_argument("--report-path")
    cmd = sub.add_parser("index")
    cmd.add_argument("registry")
    cmd.add_argument("--reports-dir")
    cmd.add_argument("--repo-root")
    cmd.add_argument("--out", required=True)
    cmd = sub.add_parser("compare")
    cmd.add_argument("research", nargs="+")
    cmd.add_argument("--spec", required=True)
    cmd.add_argument("--out", required=True)
    args = p.parse_args()
    try:
        if args.command in {"validate","render","recompute"}:
            d = load(args.research)
            b = load(args.baseline) if args.baseline else None
            if args.command == "recompute":
                d = recompute(d)
            result = validate(d,b)
            if args.command == "render":
                Path(args.out).parent.mkdir(parents=True,exist_ok=True)
                Path(args.out).write_text(render(d,b,load(args.archive) if args.archive else None,visual_data=load(args.visuals) if args.visuals else None),encoding="utf-8")
            elif args.command == "recompute":
                write_json(args.out,d)
        elif args.command == "register":
            result = register(args.archive,load(args.research),args.expected_hash)
        elif args.command == "baseline":
            d = baseline(load(args.archive),args.identity,args.report_id,args.before)
            write_json(args.out,d)
            result = {"report_id":d["report_id"],"sha256":digest(d)}
        elif args.command == "verify-archive":
            a = verify_archive(load(args.archive))
            result = {"snapshots":len(a["snapshots"]),"sha256":digest(a)}
        elif args.command == "catalog":
            result = catalog(args.registry,args.archive,args.library_file_id,args.filename,args.report_file_id,args.report_filename,load(args.card) if args.card else None,repo_root=args.repo_root,repository=args.repository,report_path=args.report_path)
        elif args.command == "index":
            from company_index import render_index
            Path(args.out).parent.mkdir(parents=True,exist_ok=True)
            Path(args.out).write_text(render_index(load(args.registry),args.reports_dir,args.repo_root),encoding='utf-8')
            result = {'status':'rendered','companies':len(load(args.registry)['companies'])}
        else:
            Path(args.out).write_text(compare([load(x) for x in args.research],load(args.spec)),encoding="utf-8")
            result = {"status":"rendered","companies":len(args.research)}
        print(json.dumps(result,ensure_ascii=False))
        return 0
    except (Invalid, KeyError, TypeError, OSError, ValueError) as e:
        print(f"Validation failed: {e}",file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

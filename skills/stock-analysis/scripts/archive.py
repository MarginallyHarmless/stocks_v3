"""Portable company archives and registry. No implicit saving during rendering."""
from __future__ import annotations
import copy
import json
import os
import tempfile
from pathlib import Path
from model import VERSION, Invalid, digest, identity, load, need, timestamp, validate


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".stock-analysis-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def verify_archive(archive):
    need(archive.get("schema_version") == VERSION and archive.get("kind") == "company_archive", "Invalid archive")
    snapshots = archive.get("snapshots", {})
    need(isinstance(snapshots, dict), "Invalid snapshots")
    for key, entry in snapshots.items():
        d = entry["research"]
        need(key == d["report_id"] and entry["sha256"] == digest(d), "Saved snapshot was modified")
        need(identity(d["company"]) == archive["identity"], "Mixed securities in company archive")
        parent_id = d.get("parent_report_id")
        parent = snapshots.get(parent_id, {}).get("research")
        if d["mode"] == "update":
            need(parent is not None, "Archive missing original baseline")
        validate(d, parent)
    return archive


def register(archive_path, research, expected_hash=None):
    path = Path(archive_path)
    if path.exists():
        archive = verify_archive(load(path))
        if expected_hash:
            need(digest(archive) == expected_hash, "Archive changed since it was read")
    else:
        need(expected_hash is None, "Expected an existing archive")
        archive = {"schema_version": VERSION, "kind": "company_archive", "identity": identity(research["company"]), "snapshots": {}}
    need(archive["identity"] == identity(research["company"]), "Archive belongs to another security")
    snapshots = archive["snapshots"]
    rid = research["report_id"]
    if rid in snapshots:
        need(snapshots[rid]["sha256"] == digest(research), "Cannot overwrite an immutable report ID")
        return {"status": "unchanged", "report_id": rid, "archive_sha256": digest(archive)}
    parent = snapshots.get(research.get("parent_report_id"), {}).get("research")
    validate(research, parent)
    if research["mode"] == "update" and research["review"]["release"]["status"] == "published":
        key = review_key(research)
        previous = [entry['research'] for entry in snapshots.values() if entry['research']['mode']=='update'
                    and entry['research']['review']['release']['status']=='published' and review_key(entry['research'])==key]
        if previous:
            old=max(previous,key=lambda d: timestamp(d['cutoff']))
            if research.get("supersedes_report_id") != old["report_id"]:
                raise Invalid(f"Release already reviewed as {old['report_id']}; reuse it or explicitly supersede it with new evidence")
            need(timestamp(research["cutoff"]) > timestamp(old["cutoff"]), "Revision needs a later cutoff")
    snapshots[rid] = {"sha256": digest(research), "research": copy.deepcopy(research)}
    write_json(path, archive)
    return {"status": "saved", "report_id": rid, "archive_sha256": digest(archive)}


def review_key(d):
    # Stable filing accession/release identifier, never just a mutable scheduled date.
    return d["parent_report_id"], d["review"]["release"]["id"], d["review"]["release"]["period"]


def baseline(archive, security_identity, report_id=None, before=None):
    verify_archive(archive)
    need(archive["identity"] == security_identity, "Wrong company/share class; ticker alone is insufficient")
    entries = [v["research"] for v in archive["snapshots"].values()]
    if report_id:
        matches = [d for d in entries if d["report_id"] == report_id]
    else:
        need(before is not None, "Selecting latest baseline requires the actual new-release publication timestamp")
        limit = timestamp(before)
        matches = [d for d in entries if timestamp(d["cutoff"]) < limit and d.get("watchlist")
                   and not (d["mode"] == "update" and d["review"]["release"]["status"] == "pending")]
    need(bool(matches), "No saved applicable baseline; retrieve the original package")
    return max(matches, key=lambda d: timestamp(d["cutoff"]))


def catalog(registry_path, archive_path, library_file_id=None, filename=None, report_file_id=None, report_filename=None, card=None, *, repo_root=None, repository=None, report_path=None):
    """Catalog saved repo files, or legacy artifacts with verified durable IDs."""
    if repo_root:
        import re
        need(isinstance(repository, str) and bool(re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository)), 'Repository owner/name required')
        from company_index import repository_file
        relative_archive = Path(archive_path).resolve().relative_to(Path(repo_root).resolve()).as_posix()
        repository_file(repo_root, relative_archive)
        repository_file(repo_root, report_path)
    else:
        need(isinstance(library_file_id, str) and library_file_id.strip(), "Actual durable file ID required")
    archive = verify_archive(load(archive_path))
    path = Path(registry_path)
    registry = load(path) if path.exists() else {"schema_version": VERSION, "kind": "company_registry", "companies": {}}
    need(registry.get("kind") == "company_registry", "Invalid company registry")
    reports = sorted((v["research"] for v in archive["snapshots"].values()), key=lambda d: timestamp(d["cutoff"]))
    need(bool(reports), "Cannot catalog an empty archive")
    latest = reports[-1]
    from company_index import enrich_entry
    previous = registry["companies"].get(archive["identity"], {})
    old_reports = {r['report_id']: r for r in previous.get('reports', [])}
    entry = enrich_entry(previous, reports)
    entry.update({
        "company": latest["company"], "ticker_aliases": sorted({d["company"]["ticker"] for d in reports}),
        "archive_sha256": digest(archive), "reports": [{**old_reports.get(d['report_id'], {}), "report_id": d["report_id"], "cutoff": d["cutoff"],
            "parent_report_id": d.get("parent_report_id"), "watch_count": len(d["watchlist"])} for d in reports]})
    if repo_root:
        registry['storage'] = {'provider': 'github', 'repository': repository, 'branch': 'main'}
        entry.update(archive_path=relative_archive, archive_filename=Path(relative_archive).name)
        entry.pop('archive_file_id', None)
        for item in entry['reports']:
            item.pop('html_file_id', None)
        entry['reports'][-1].update(html_path=report_path, html_filename=Path(report_path).name)
    else:
        entry.update(archive_file_id=library_file_id, archive_filename=filename)
    if not repo_root and (report_file_id or report_filename):
        need(bool(report_file_id and report_filename), 'Both actual report file ID and filename are required')
        entry['reports'][-1].update(html_file_id=report_file_id, html_filename=report_filename)
    if card is not None:
        need(card.get('report_id') == latest['report_id'], 'Card must describe the latest report')
        entry['card'].update(copy.deepcopy(card))
    registry["companies"][archive["identity"]] = entry
    write_json(path, registry)
    return {"status": "cataloged", "identity": archive["identity"], "reports": len(reports)}

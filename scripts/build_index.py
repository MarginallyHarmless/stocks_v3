#!/usr/bin/env python3
"""Validate saved research and regenerate the repository index."""
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/stock-analysis/scripts"))
from archive import verify_archive
from company_index import render_index, repository_file
from model import digest, load, need

registry = load(ROOT / "stock-analysis-registry.json")
for identity, company in registry["companies"].items():
    archive = verify_archive(load(repository_file(ROOT, company["archive_path"])))
    need(archive["identity"] == identity, "Registry/archive identity mismatch")
    need(digest(archive) == company["archive_sha256"], "Registry/archive hash mismatch")
    for report in company["reports"]:
        need(report["report_id"] in archive["snapshots"], "Report missing from archive")
        repository_file(ROOT, report["html_path"])
index = ROOT / "index.html"
html = render_index(registry, repo_root=ROOT)
stamp = re.compile(r'"generated_at": "[^"]*"')
# Rebuilding unchanged research keeps the file, so the saved-at date only moves with content.
if not (index.exists() and stamp.sub("", index.read_text(encoding="utf-8")) == stamp.sub("", html)):
    index.write_text(html, encoding="utf-8")
print(f"Built index for {len(registry['companies'])} companies.")

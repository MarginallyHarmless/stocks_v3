# Working in stocks_v3

This repository is the canonical home for all studied-company reports, the shared index and future earnings follow-ups. The user explicitly chose GitHub. Do not publish on ChatGPT Sites or create parallel Library copies.

Before researching or updating a company:

1. Read `skills/stock-analysis/SKILL.md` and its relevant references.
2. Fetch the latest main branch and load the complete `stock-analysis-registry.json`.
3. Resolve the company by issuer and security identity, then verify its archive under `archives/`. Never reconstruct the original watchlist from memory.

Save report HTML under `reports/` and immutable research snapshots in the same company archive. Use a new report ID/file for new research; preserve earlier reports. Editorial-only changes keep the research cutoff and archived facts unchanged. Catalog repository-relative paths, update the company card and earnings schedule with sources, then run `python3 scripts/build_index.py`. Preserve other companies and unreviewed past periods. Only a saved earnings review of the matching period can clear its flag.

Before committing, run the generator and verify the archive. For generator changes also run:

```sh
python3 -m unittest discover -s skills/stock-analysis/scripts/tests
node skills/stock-analysis/scripts/tests/test_company_index.js
node skills/stock-analysis/scripts/tests/test_report_controls.js
```

Commit and push the report, archive, registry and index together. Never force-push. Inspect the remote commit after saving. GitHub Pages should publish from main at the repository root. Do not describe its URL as live until the deployment and page response have been checked.

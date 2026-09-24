# Working in stocks_v3

This repository is the canonical home for all studied-company reports, the shared index and future earnings follow-ups. The user explicitly chose GitHub. Do not publish on ChatGPT Sites or create parallel Library copies.

Before researching or updating a company:

1. Read `skills/stock-analysis/SKILL.md` and its relevant references.
2. Fetch the latest main branch and load the complete `stock-analysis-registry.json`.
3. Resolve the company by issuer and security identity, then verify its archive under `archives/`. Never reconstruct the original watchlist from memory.

To make an existing report explain more ("deepen it like HOOD"), follow `skills/stock-analysis/references/depth-revisions.md` and the tools in `scripts/depth/`; the worked example is `research/depth/HOOD-2026-09-18-v3-r2.spec.json`.

Save report HTML under `reports/` and immutable research snapshots in the same company archive. Use a new report ID/file for new research; preserve earlier reports. Editorial-only changes keep the research cutoff and archived facts unchanged. Catalog repository-relative paths, update the company card and earnings schedule with sources, then run `python3 scripts/build_index.py`. Preserve other companies and unreviewed past periods. Only a saved earnings review of the matching period can clear its flag.

Before committing, run the generator and verify the archive. For generator changes also run:

```sh
python3 -m unittest discover -s skills/stock-analysis/scripts/tests
node skills/stock-analysis/scripts/tests/test_company_index.js
node skills/stock-analysis/scripts/tests/test_report_controls.js
node skills/stock-analysis/scripts/tests/test_financial_terms.js
node skills/stock-analysis/scripts/tests/test_dashboard_controls.js
python3 scripts/render_reports.py   # CI fails if reports/ differs afterwards
```

Commit and push the report, archive, registry and index together. Never force-push. Inspect the remote commit after saving. If the shell has no push credentials, use the platform's GitHub integration when one is connected; otherwise report that the push is blocked. A local browser login is not needed for routine updates.

Every push to `main` runs `.github/workflows/pages.yml`: validate the research, regenerate the index, package the website and deploy to GitHub Pages. Pull requests validate without publishing. Website files belong in `index.html`, `stock-analysis-registry.json`, `reports/`, `archives/` and optional `assets/`; update the packaging step if adding another public directory.

Monitor the Actions run for the exact pushed commit. Inspect failed job logs and fix actionable failures; re-run failed jobs after a transient error or an account-side setup change. If an expired artifact prevents a retry, run the workflow again from the Actions UI or make the next intended content push. Do not force-push or fabricate a content change just to trigger deployment.

One-time account setup is Settings → Pages → Build and deployment → Source: **GitHub Actions**. Assistant integrations normally cannot change repository administration settings. Once enabled, the workflow uses GitHub's built-in credentials; no personal token, hosting secret or browser login is needed for future deployments.

After a successful deployment, check the index and changed report URLs under `https://marginallyharmless.github.io/stocks_v3/` before describing them as live. Report an unresolved deployment failure explicitly, even when the push succeeded.

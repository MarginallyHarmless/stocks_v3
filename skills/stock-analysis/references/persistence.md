# Durable research packages

The user chose **https://github.com/MarginallyHarmless/stocks_v3** for the index and every report. Use this repository as the source of truth. Do not use ChatGPT Sites or save duplicate Library copies. If GitHub is unavailable, retain local work and report the blocked save; do not substitute another publishing service.

## Repository layout

- `index.html`: shared visual company index and logo calendar.
- `stock-analysis-registry.json`: registry keyed by issuer_id + security_id, with repository-relative archive/report paths, cards and earnings states.
- `archives/stock-analysis-<security-key>-archive.json`: all immutable snapshots for one security. Derive the key from identity, not ticker alone.
- `reports/<report-filename>.html`: complete readable report. Save new research as a new file; preserve earlier reports. Editorial changes may update the same HTML without changing its research cutoff or archived evidence.
- `skills/stock-analysis/`: versioned generator, templates and research instructions. Research data belongs outside this folder.

## Save an analysis

1. Fetch the repository's current main branch, read `AGENTS.md`, load the existing registry and verify the target archive. Preserve every unrelated company.
2. Validate and render the new ledger; register it explicitly in the same company archive. Preserve the original archive and use an expected hash when updating one previously read.

```text
python3 scripts/stock.py register research.json --archive REPO/archives/company-archive.json
python3 scripts/stock.py catalog REPO/archives/company-archive.json --registry REPO/stock-analysis-registry.json --repo-root REPO --repository MarginallyHarmless/stocks_v3 --report-path reports/REPORT.html --card card.json
python3 scripts/stock.py index REPO/stock-analysis-registry.json --repo-root REPO --out REPO/index.html
```

3. Follow [company-index.md](company-index.md) for cards, schedule provenance and review states. Verify report links resolve within the repository and all archived snapshots still validate.
4. Commit and push report, archive, registry and generated index together. Include generator/template changes when needed. Use the GitHub connector when available; preserve concurrent changes and never force-push. Inspect the actual remote tree/commit after writing. A local commit or a rendered HTML file alone is not success.
5. Every push to `main` runs the repository's `.github/workflows/pages.yml` to validate, build and deploy through GitHub Pages using GitHub's built-in credentials. Monitor the Actions run for the exact pushed commit, inspect failed job logs and fix or retry actionable failures. Check the index and changed report URLs under `https://marginallyharmless.github.io/stocks_v3/` before claiming they are live. The connected GitHub app can push without a browser login; keep using it when shell Git lacks credentials. The one-time repository setting is Settings → Pages → Source: GitHub Actions. The connector cannot change that administration setting: complete and push the workflow first, then request only that exact account action if still missing. Do not ask for personal tokens or repeat browser sign-in for routine updates. Keep this preference in the repository's `AGENTS.md` for future sessions.

## Fresh session

Read `stock-analysis-registry.json` from `MarginallyHarmless/stocks_v3` first; resolve by durable security identity and verified ticker/exchange/share class. Read its archive at the recorded `archive_path` from the same repository. If the registry is absent/stale, inspect `archives/` for the company's archive and verify embedded identity rather than choosing solely by filename. Ticker changes must not lose the security's history, and a reused ticker must not select another issuer.

```text
python3 scripts/stock.py verify-archive company-archive.json
python3 scripts/stock.py baseline company-archive.json --identity 'ISSUER|SECURITY' --report-id EXACT_BASELINE_ID --out baseline.json
```

Without an explicit baseline, supply the actual newly published release timestamp:

```text
python3 scripts/stock.py baseline company-archive.json --identity 'ISSUER|SECURITY' --before 2026-08-05T20:05:00Z --out baseline.json
```

The command selects the newest eligible pre-release snapshot with a watchlist and excludes pending-only updates. Confirm it is applicable to the relevant period. If results are unpublished, use the latest actual baseline for a pending review; do not fabricate a publication time to satisfy the command.

If retrieval cannot find the original package, request the exported JSON/report containing it. Explain what is missing and stop the historical comparison; new standalone research may still proceed with explicit scope. Never fabricate past expectations.

## Immutable updates and revisions

Supply the whole saved archive when rendering an update so exported packages retain all ancestors:

```text
python3 scripts/stock.py render update.json --baseline baseline.json --archive company-archive.json --out update.html
python3 scripts/stock.py register update.json --archive company-archive.json
```

Registration validates the original baseline, security identity and all original watch outcomes. An existing report ID with different contents is rejected. Re-registering identical contents is idempotent. A second assessment of the same baseline/release is rejected unless it explicitly supersedes the current review with a later cutoff. Preserve the original, including a provisional release-only review.

After registration update archive → report → registry → index.html and commit them together to the repository. Preserve unrelated companies and all earlier snapshots. Fetch before pushing; if the branch advanced, merge the new snapshot into the current registry/archive and regenerate the index. Never force-push. Verify the remote commit and, when publishing is configured, the GitHub Pages deployment. An HTML export/import is portable, but only a successful repository save establishes retrieval in a future session. Imported archives must pass `verify-archive` before use. Hashes detect accidental changes; do not describe them as signed or tamper-proof.

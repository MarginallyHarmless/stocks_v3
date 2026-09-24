# Shared company index

Maintain `index.html` and `stock-analysis-registry.json` in `MarginallyHarmless/stocks_v3`, alongside every report and company archive. This is a static site with a live in-browser countdown, not a background monitor. Full analyses and earnings updates refresh it; editorial changes preserve the original cutoff and review state.

## Maintenance flow

1. Fetch the repository and read its `AGENTS.md`, complete registry and target archive. Preserve all other companies.
2. Save the report under `reports/` and archive under `archives/`. Catalog actual repository files:

```text
python3 scripts/stock.py catalog REPO/archives/company-archive.json --registry REPO/stock-analysis-registry.json --repo-root REPO --repository MarginallyHarmless/stocks_v3 --report-path reports/REPORT.html --card card.json
```

3. Supply a succinct English/Romanian card with business, summary and risk, keyed to the latest report ID. Keep a verified logo and its provenance. `card.json` has this shape; every text field is `{"en": …, "ro": …}`:

```json
{"report_id": "EXACT-LATEST-REPORT-ID", "summary": {"en": "…", "ro": "…"}, "business": {"en": "…", "ro": "…"},
 "risk": {"en": "…", "ro": "…"}, "logo_url": "https://…", "logo_source_url": "https://…", "logo_data_uri": "data:image/png;base64,…"}
```

   Without `--card`, cataloging a newer report keeps only the logo fields and falls back to the report's first summary claim, dropping business and risk, so always pass a card for a new report. Cataloging retains schedule checks newer than the ledger and unreviewed periods. Repeated cataloging is idempotent; it does not push changes.
4. Render links to actual reports. Missing files must fail the build:

```text
python3 scripts/stock.py index REPO/stock-analysis-registry.json --repo-root REPO --out REPO/index.html
```

5. Validate and commit the report, archive, registry and index in one change. Verify the remote save. If concurrent changes arrived, merge only the target company and regenerate. The legacy `--reports-dir` mode embeds reports for an explicitly requested portable export; it is not the canonical repository output.

## State rules

| Evidence / timing | Visible state |
|---|---|
| Future date | Awaiting results + days left + Confirmed/Estimated |
| Date-only release today in issuer timezone | Expected today; publication unverified |
| Confirmed exact time passed, or date-only day ended | Review needed; check publication |
| Estimated date passed | Check results; publication unverified |
| Explicitly verified release, no saved review | Review needed immediately |
| Saved published update assessed original baseline for this period | Reviewed; next period stays separate |
| Published provisional review | Partial review; attention remains |
| No date | Date not announced; no invented countdown |

Publication requires `publication_status: "published"`, `published_at`, and `publication_source_url`. Catalog clears a period only from a validated published update whose baseline's `next_event.period` equals `review.release.period`. No toggle, file modification, newer cutoff, schedule refresh, pending update or next-quarter date can clear it. Keep unresolved older periods. `Not disclosed` is a completed assessment, not a failed investment criterion. A complete revision may supersede a provisional one through the archive workflow.

Countdowns recalculate on opening, visibility return and while open. Date-only releases use issuer calendar days, not viewer/UTC midnight. The file does not fetch new research or issue background notifications.

## Presentation and verification

The index shares the reports' colour tokens, embedded fonts and card surfaces, and the same saved language and theme choice. Keep cards succinct: logo, ticker and exchange, company name, countdown chip, one-line business, the summary verdict, one "Watch" line, then a footer with the next results date, period and confidence, a follow-up prompt button, a download button and "Read". Do not repeat schedule sources, check dates or saved-check counts on cards; they live in the report and registry. Use a compact calendar-style side agenda with real company logos; on phones it becomes a sideways strip of date tiles. Keep the agenda sticky on desktop and bounded on phones. Use a consistent 18px identity, 14px reading text and 12px metadata hierarchy; avoid oversized countdowns and redundant future-state badges. Clicking a logo reveals its date, period and status. Group same-day releases without losing companies. Preserve search, attention filtering, mobile reflow, keyboard access, English/Romanian, light/dark themes, report downloads and copyable follow-up prompts. Do not add synthetic companies to the user's saved index to demonstrate density.

Verify future, today, overdue estimate, overdue confirmed, published-unreviewed, unknown, rescheduled, reviewed, provisional and wrong-period states, and preservation of other companies. Run `node scripts/tests/test_company_index.js` plus standard skill tests. Inspect desktop/phone layouts when preview is available.

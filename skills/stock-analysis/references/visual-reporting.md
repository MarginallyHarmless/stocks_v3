# Visual financial reporting

Full reports include an always-visible financial dashboard, in English and Romanian. Use `scripts/dashboard.py` and `assets/dashboard.{css,js}`. The ordinary report narrative and next-results watchlist remain intact. Do not hide the dashboard behind Detailed analysis.

## Required coverage

| Panel | Data and visual |
|---|---|
| Revenue | Prefer 16 comparable fiscal quarters; zero-based bars |
| Net profit | Profit attributable to common shareholders; show negative bars below zero |
| Cash flow | Operating cash and explicitly defined free cash flow; grouped bars on one axis |
| Diluted average shares | Weighted average diluted shares, not period-end shares; line chart with disclosed cropped axis |
| Cash, investments and debt | Cash/equivalents, short-term investments, total debt; dated balances; disclose lease treatment |
| Operating expenses | SG&A and R&D, or industry-relevant cost categories; do not imply components equal total costs |
| Price in the last 12 months | Quote/session/time, low/high, extrema dates when available, position, distance from both extremes, 200-day average and distance from it |
| Analyst consensus | Mean, median, low/high target, target horizon, contributor count, upside/downside against a dated quote; all five recommendation counts and weighted 1–5 score |
| Historical P/E | Prefer 20 period-end observations; trailing earnings basis; null for nonpositive/unknown denominators |
| Historical P/S | Prefer 20 period-end observations; equity value divided by trailing sales, not EV/sales |

Keep all ten panel headings visible even when data cannot be obtained; say exactly what is missing. A placeholder is not completed research. Attempt source retrieval; use explicitly labeled annual history only when quarterly data is unavailable. Do not interpolate missing points or mix TTM, annual, YTD and quarter values. Analyst price-target contributors can differ from recommendation contributors; label both.

Use issuer statements for financial research and an identified market provider for quotes, analyst data and historical multiples. Provider-standardized history must be labeled separately from issuer figures. Check at least the latest period against the issuer ledger. Show any material definition mismatch beside the chart, especially free cash flow, lease-inclusive debt and bank/broker cash flow. Financial-company cash flow and a company undergoing major restructuring need visible comparability caveats.

## Visual supplement contract

Pass one explicit `visual_research_supplement` via:

```sh
python3 scripts/stock.py render research.json --visuals visual-data.json --out report.html
```

The record has `kind`, `schema_version`, `ticker`, `identity` (`issuer_id|security_id`), `retrieved_at`, `sources`, `series`, `market`, `consensus`, and bilingual `basis_note`. Security identity must match the research. Persist company data under repository `research/visuals/`; never put it inside the reusable skill. The repository renderer uses `research/visuals/manifest.json` to select data by exact report ID. Add new reports to that manifest. Never silently attach a supplement using the ticker alone.

A source has HTTP(S) `url`, `status: read`, `retrieved_at`, provider name, source update date when supplied, extraction note and the exact numeric row transcribed. Source artifacts can be consulted to audit extraction; do not save entire copyrighted webpages in the report.

Each series has a supported metric key (see `NAMES`), `unit`, `currency`, `scale`, `basis`, `period_kind: quarter|annual`, `source_id`, `source_row`, and chronological `points`: `{period: "Q2 2026"|"FY 2025", period_ending, value, state}`. Null means absent, never zero. P/E/P/S must be positive or null. Preserve the source distinction between not meaningful and unavailable.

`market` stores separate dated `overview_quote`, `stats_quote`, `forecast_quote` records with `price`, `observed_at`, `session`, `source_id`. `range` has low/high, dates or null, method and source_id. `ma200` has value, method and source_id. Never describe a provider intraday 52-week range as a daily-closing-price range. Do not fabricate dates of extrema. Derive distance to an average only when the price/average snapshot dates agree.

`consensus.targets` has low/mean/median/high, horizon_months, source_id; consensus also has target_analyst_count and label. `ratings` has the five exact category counts, total, period, source_id, score, score_scale. Validate total and weighted score. Targets are estimates, not intrinsic values or promised returns.

Historical P/E/P/S are provider period-end multiples unless independently reconstructed with a documented method. Do not label them filing-date values. Show a historical median only with at least eight usable observations; it is not a price target. Restatements and differences from current-quote multiples stay visible.

## Editorial and display rules

A later-dated supplement has its own prominent date. Keep the original analysis cutoff, sources, conclusions, watchlist criteria and archive hashes unchanged. Explicitly state that conclusions have not been reassessed. Embed the supplement separately from the immutable research archive and provide a separate download. Do not clear earnings-review flags.

Use two roomy columns on desktop, one on phones. Keep a consistent title, cadence/unit, visible values, chart, period selector, source table and short interpretation. Date labels stay horizontal and sparse; every observation remains available through the selector and table. Normalize scales before sharing axes. Fill missing period slots so line segments cannot bridge a missing quarter. Losses in a single series use a loss color; grouped series preserve their distinct colors above and below zero.

Run the maintenance suite, then inspect actual chart layouts and controls. Verify negative values, missing periods, absent components, annual fallbacks, long translated labels, and both themes. Test source disclosures, period selectors, export, mobile overflow, and unchanged archive hashes. If the preview environment cannot access local files, do not claim local visual QA; inspect the authorized deployed report instead.

Period selectors inspect one observation within the full history. Highlight the selected period in the plot and source table, and label the headline values with its date. Keep axes and historical values unchanged; a missing observation remains unavailable, with no invented point.

# v3 data contract

Contents: root records, evidence and calculations, presentation, watchlists, reviews, comparisons, validation limits.

Use `scripts/demo.py --out <temporary-directory>` to create a complete bilingual fictional example. It exercises a full baseline, a later review and a portable archive. It is an authoring aid, never a research source. `model.py` is the executable contract; validation stops at the first error.

## Root research record

| Field | Contract |
|---|---|
| `schema_version`, `profile` | `3.0`, `strict`. Never relabel an old schema as v3. |
| `report_id` | Immutable ASCII identifier, letters/digits/period/underscore/hyphen, at most 101 characters. |
| `parent_report_id` | Original baseline ID for an update; otherwise null. |
| `mode` | `full`, `focused`, `update`. Comparison consumes multiple company records. |
| `synthetic` | Explicit boolean. `false` for researched companies, `true` for invented fixtures. |
| `company` | `issuer_id`, `security_id`, `name`, `ticker`, `exchange`, `share_class`; also record `reporting_currency`, `trading_currency`, `fiscal_year_end`, ADR ratio when relevant. IDs require verified provenance in research. |
| `cutoff`, `prepared_at`, `freshness_checked_at` | ISO timestamps with timezone. Historical information cutoff differs from preparation date. |
| `languages`, `default_language` | Available `en`/`ro` and selected default. Default reading level is Guided on first use. |
| `presentation` | Set `"guided"` for new full reports; every section then requires a `guide`. Omission remains valid for existing archives. Do not rewrite old snapshots to add it. |
| `sources`, `evidence` | Lists with unique IDs. |
| `summary` | Nonempty list of typed claims. |
| `business_assessment`, `price_assessment` | Separate typed claims, not unreferenced verdict strings. |
| `evidence_gaps` | Visible material research limitations. Use “No material gap identified in the researched scope” only when warranted. |
| `sections` | Question-led authored sections, independent of checklist IDs. |
| `coverage`, `checklist` | Module coverage and original checklist audit. |
| `watchlist`, `next_event`, `related_events` | Closing checks and dated reporting events; watchlist required for full/update. |
| `review` | Update-only original-criteria assessment. |

Narrative text accepts a string for a single-language report or `{ "en": "…", "ro": "…" }`. Author both translations when both languages are listed. Preserve exact source titles, stable IDs and technical definitions rather than translating identifiers. Do not use arbitrary HTML in prose; the renderer escapes it. String definitions are normalization keys for calculations, not prose templates.

## Sources

Each source has `id`, `title`, HTTP(S) `url`, `authority` (`issuer`, `regulator`, `market`, `secondary`; `synthetic` only in demos), `status` (`read`, `pending`, `inaccessible`), `retrieved_at`, and `published_at` or an explanatory `publication_note`. Evidence can only use a read source. Publication cannot be after the research cutoff. Track what was actually available; an earnings release is not a reviewed 10-Q.

## Evidence

All records have `id`, `kind`, `label`, and a precise string `definition`. Kinds: `fact`, `estimate`, `assumption`, `calculation`, `judgment`, `unavailable`.

Numeric records carry:

```json
{
  "id": "revenue-q1", "kind": "fact", "label": {"en":"Revenue","ro":"Venituri"},
  "definition": "Consolidated revenue", "value": 100, "unit": "currency",
  "currency": "USD", "scale": 1000000, "basis": "GAAP",
  "period": {"kind":"duration", "start":"2026-01-01", "end":"2026-03-31",
             "label":"Q1 2026", "forecast":false},
  "source_id":"issuer-q1", "extraction":{"locator":"Income statement, p. 4", "note":"Revenue row, USD millions"}
}
```

Units: `currency`, `currency_per_share`, `shares`, `percent`, `ratio`, `count`. Currency is an ISO three-letter code only on currency units. `scale` is 1, 1,000, 1,000,000, 1,000,000,000 or 1,000,000,000,000. Percent 12 means 12%; ratio 0.1 means 10%. `precision` optionally controls display decimals (0–6). `display` and legacy `raw_value` are forbidden.

Basis: `GAAP`, `IFRS`, `adjusted`, `market`, `operating`, `model`. A derived standard FCF may use GAAP inputs, but explain that FCF itself is a non-GAAP measure. Preserve adjustments/reconciliations explicitly.

Periods are `duration` with start/end, or `instant` with end only. Both require a label and forecast boolean. Facts cannot be forecasts. Numerical market evidence also needs `observed_at` and `session` (e.g. regular close); access time is not quote time. Non-numeric evidence uses `state` and a period, except unavailable records can omit the period.

Facts/estimates require `source_id` and `extraction` with locator and compact extraction note. Assumptions require `rationale`. Judgments require `evidence_refs`. Unavailable records explain the reason in `state`; never turn absence into zero.

### Calculations

Every calculation adds `operation`, `inputs` (evidence IDs), numerical output fields and optional `parameters`. Store full precision; recompute from inputs. Inputs may be calculations, but cycles are rejected. All arithmetic normalizes scale before operating.

| Operation | Ordered inputs / constraints |
|---|---|
| `sum`, `difference` | Same-period, same-unit/currency/basis values. Difference has exactly two inputs. |
| `ratio`, `percent_ratio` | Numerator/positive denominator, matching period and dimensions. Output ratio or percent. |
| `per_share` | Same-period currency / shares. Output currency_per_share. |
| `growth` | `[new, old]`, same definition/basis/currency and comparable period lengths, positive old value. Output percent. |
| `cagr` | `[new, old]` plus `parameters.years` agreeing with dated endpoints. Positive base, nonnegative end. For conventional EPS CAGR use positive endpoints and discuss losses separately. |
| `ttm` | `[full_year, current_YTD, prior_YTD]`, same financial definition; dated adjacent fiscal years and matching YTD durations. |
| `quarter_sum` | Four ordered contiguous fiscal quarters, same definition/basis/currency. |
| `average_balance` | Ordered comparable instant balances, including opening and closing dates. Output duration. |
| `pe` | `[observed_price, EPS]`; per-share currency compatible, positive duration EPS. Output basis/period identify the earnings denominator. |
| `net_debt_to_fcf` | `[instant_net_debt, TTM_FCF]` with matched end date and positive FCF. Explain net cash separately. |
| `product`, `taxed_profit` | `[amount, ratio]`; taxed profit uses amount × (1−ratio). Match periods or declare assumption rationale and model basis. |
| `required_revenue` | `[equity_market_value, assumed_P/S]`; model basis and `model_assumptions` required. Do not silently substitute EV. |
| `equity_value` | `[observed_price, observed_instant_shares]`; model basis and explicit bridge assumptions. Share observation cannot postdate quote; output uses quote date. Distinguish basic shares from future dilution. |
| `valuation_multiple` | `[instant_equity_or_enterprise_value, positive_duration_amount]`; matching currency, model basis and explicit period/basis assumptions. Output uses valuation date. Label P/S versus EV/sales correctly. |
| `eps_multiple` | `[positive_future_EPS, positive_multiple]`; model basis, forecast period and `model_assumptions`. Output is future price. |
| `discounted_value` | `[future_value, discount_rate_ratio]`; `parameters.years`, matching actual dated horizon, model basis and assumptions. |

Do not force a calculation into the wrong operation to pass validation. Add a narrow tested typed extension for a genuinely unsupported model, or preserve the result as unavailable. A DCF needs complete cash-flow and enterprise/equity bridges; do not claim this engine supplies an automatic general DCF.

## Claims and presentation

A claim is `{type, text, evidence_refs}`. Types: `fact`, `interpretation`, `model`, `limitation`. All except limitation require nonempty supporting evidence. Factual claims may not depend transitively on assumptions/estimates. An empty source list is permitted for explicit research limitations, not as a route to disguise factual assertions.

A section has `id`, `question`, optional `nav_label`, nonempty `claims`, `metrics` evidence IDs, visible `caveat`, and optional `lesson` containing `concept`, hypothetical `example`, and `trap`. Optional `series` has `title` and ordered `evidence_refs` with matching units, basis and definition. Put company interpretation in visible claims, not only in lessons.

For Guided presentation add `section.guide`:

```json
{
  "claims": [{"type":"interpretation", "text":{"en":"Short answer with concepts explained first.","ro":"Răspuns scurt, cu noțiunile explicate mai întâi."}, "evidence_refs":["supporting-evidence"]}],
  "metrics": [{"evidence_ref":"numeric-evidence", "label":{"en":"Plain label","ro":"Etichetă simplă"}, "meaning":{"type":"interpretation", "text":{"en":"What this actual figure means for the company.","ro":"Ce înseamnă această valoare pentru companie."}, "evidence_refs":["numeric-evidence"]}}],
  "why_it_matters": {"type":"interpretation", "text":{"en":"The practical implication for a shareholder.","ro":"Consecința practică pentru un acționar."}, "evidence_refs":["supporting-evidence"]}
}
```

Replace placeholder IDs and prose with researched content. `claims` has one to three typed claims. `metrics` is optional, at most three unique numeric references; each needs a typed `meaning` referencing that metric, and may override its label with plain text. `why_it_matters` is a required typed claim. Normal provenance, fact/estimate and bilingual checks apply throughout. A limitation can explain an unanswered question without pretending it is answered.

`guide` is the visible reading layer; original `claims`, `metrics` and `series` are retained under “Detailed analysis”. The section `caveat` remains visible and `lesson` stays separately expandable. Keep decisive adverse evidence, assumptions and gaps in the guide/caveat even when further explanation is in the details. The renderer uses the same typed metric values, keeps forecast labels, and exports the original research record unchanged. It does not automatically rewrite dense prose. For editorial revisions preserve cutoff, sources, evidence and exact watch criteria; do not mutate an archived baseline used by later reviews.

Full reports require all module coverage keys: business, moat, growth, profitability, cash_flow, balance_sheet, capital_allocation, dilution, management, valuation, scenarios, peers, market_context, risks. Each has status covered/partial/unavailable/inapplicable, reason and section_ids. “Covered” requires a section. This is research coverage, never investment quality.

`checklist` maps every original ID from checklist.json to status, reason, evidence_refs and section_ids. Statuses: meets/mixed/does_not_meet/insufficient_evidence/not_applicable; optional IDs may be not_researched. Do not count unavailable tests as met. Retain thresholds from checklist.md in the relevant visible discussion when material.

## Watchlists and events

Optional `section.evidence_table` has an authored `title`, `columns`, and `rows`. Each row has a `label` and one `cells` entry per non-label column. Each cell is either `{evidence_ref: ID}` or a typed claim. Values render from the ledger; claims follow normal evidence and translation validation. The table appears in Detailed analysis and its references join the source navigation. Use it for peer matrices with explicit period and comparability limits.

See earnings-follow-up.md for meaning. Each item has id, positive criterion_version, question, why, baseline_refs, due_period, optional due_date, criterion and impact. `impact` has favorable/adverse/mixed/unresolved text.

`criterion`: kind numeric/qualitative, basis management_guidance/external_estimate/analytical_test, description, rationale. External or management criteria require evidence_refs. Numeric criteria also have operator gt/gte/lt/lte/between, value, optional upper, unit, scale, accounting_basis, definition, and currency when applicable. Numeric actual comparisons use base units; percent thresholds are percentages, not decimal ratios.

An event has id, kind results/call/filing, period, confidence Confirmed/Estimated/Not announced, date or null, checked_at, source_id where dated, and basis for estimated/unannounced events. Confirmed requires an issuer source. Time and timezone are optional and must be published. Keep each event type separate.

## Update review

`review` contains baseline_sha256 (digest of the original complete baseline), release, provisional boolean, coverage_note, thesis_status (strengthened/weakened/broadly_unchanged/unresolved), thesis_change, outcomes, and new_risks (typed claims).

Release: stable id such as filing accession or canonical issuer release identity, period, status published/pending. Published requires source_id and published_at no later than cutoff. Do not use the changing scheduled date as release identity.

Each outcome: watch_id, original criterion_version, criterion_sha256 (digest of the entire original watch item), outcome, reason, thesis_impact, new_evidence_refs. Resolved items also need observed_period matching the saved due_period. Numeric Met/Missed need actual_ref; the validator checks the saved numeric rule. Not disclosed needs checked_source_ids of read sources. Not comparable needs comparability_reason. Restatements add restated_baseline_ref and restatement_note without replacing original values. Pending releases permit only Not yet due outcomes. Every original ID must appear exactly once.

Changed future items retaining an ID must increment criterion_version. A revision of an already reviewed release needs supersedes_report_id; archives never overwrite a report ID.

## Comparison specification

`comparison.json` contains title, summary, limitations, language and rows. Each row has question, interpretation, status Comparable/Not comparable, and values mapping each company report_id to one evidence ID. The renderer displays values, periods, definitions and direct source links together. Missing metrics belong in explicit prose; do not insert zeros. Extend with a researched qualitative comparison for management/moat/allocation as needed; do not mislabel a numerical subset as a full peer analysis.

## What validation does not prove

Structural/numerical checks do not establish source truth, economic appropriateness, honest classification of a limitation, completeness of prose or translation quality. Perform the source-to-claim audit and scenario/evaluation review in the skill. No source or outcome is an automatic investment recommendation.

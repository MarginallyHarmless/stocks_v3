# Legacy reports

The v3 strict schema replaces the old report contract. Do not silently pass a v2 ledger as current, infer typed units from ambiguous display strings or invent old watch thresholds. Preserve the original file unchanged.

For an old report requested as background, identify its version/cutoff, read its evidence and limitations, and label it legacy. Existing static HTML remains a readable artifact. The v3 scripts deliberately refuse its schema rather than claiming it meets new validation requirements.

For a new analysis based on v2:

1. Resolve security identity and retain original evidence/source IDs where meaningful. Copy source provenance, not just displayed numbers.
2. Map reported/calculated/estimate/assumption/judgment/unavailable kinds explicitly. Parse units, currency, scaling, periods and accounting bases from original sources; do not guess missing metadata.
3. Recompute using the typed operations. Check v2 CAGR input order: the new engine uses `[new, old]`. Restore claim-level references and review EN/RO explanations.
4. Preserve original checklist IDs and map them to the new question-led layout. Annotate legacy gaps instead of padding the report.
5. Establish the new watchlist prospectively. An old narrative monitoring point can be preserved as a qualitative criterion if its actual wording is retrievable; never retrofit a numeric threshold.
6. Save a new v3 snapshot with `legacy_origin` metadata (original identifier, cutoff and source filename/URL). Retain the old package separately. A new information cutoff requires real source rechecks; an editorial migration keeps the old cutoff.

This release does not include an automatic legacy converter: the missing currency/period/basis metadata identified in the review requires source-informed decisions. It also does not modify the two source projects or their saved company reports.

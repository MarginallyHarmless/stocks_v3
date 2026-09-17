# Inherited material and scope

Implementation based on the user's `stock-analysis-repository-review.md`, dated 16 September 2026, and these inspected snapshots:

- `MarginallyHarmless/stock_analysis_v2` at `e80376352af18dfdb6f7e4a2f6ec3feeb3c65c26`: original checklist JSON/Markdown/PDF retained; research method retained with the calculation-contract paragraph updated. Evidence kinds, provenance, sector applicability, separate business/price judgments and snapshot principles form the foundation.
- `MarginallyHarmless/stock-research` at `080c9b463c9e309f29e20478afbf36738ff960f8`: concept → company evidence → implication teaching pattern, quarterly momentum, per-share growth, market-context questions, conditional expectations and integrated comparisons adapted. The glossary is corrected and rewritten rather than copied with its overly definite claims.

The source v2 test suite reproduced 30 passes and 3 failures: two disconnected flow-diagram expectations and one stale collection-card statistic expectation. v3 has a new renderer and explicit registration, does not claim to render those old flow diagrams or collection statistic cards, and validates its own contract. It does not silently patch the original projects.

The typed v3 schema and portable watchlist archive are intentionally new. The old untyped numerical records remain legacy until source-informed migration. The source projects' saved company reports are not silently imported or treated as fresh research. Testing uses prominently labeled synthetic company data.

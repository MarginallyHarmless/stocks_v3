# Portfolio arithmetic contract

Use this contract only for an unlevered long-only snapshot already converted to one base currency. The script performs arithmetic on explicit inputs. It does not fetch prices, score a profile, select weights, supply correlations, certify suitability or generate orders. Keep investor interview/policy decision records separately, linked to the snapshot in the private decision record.

Run from the skill directory or use absolute paths:

```text
python3 scripts/portfolio.py validate /private/path/snapshot.json
python3 scripts/portfolio.py calculate /private/path/snapshot.json
```

Both commands write JSON to stdout; input errors exit 2 without emitting partial results. The output is not saved automatically. Save personal output only to a private destination. Monetary values, weights, returns and derived fractions are exported as decimal strings to retain precision; do not concatenate them as text when performing further arithmetic. Present percentages as fraction × 100. Output validity is numerical, not investment suitability.

## Fields

| Field | Contract |
|---|---|
| `schema_version`, `kind` | `"1.0"`, `"portfolio_snapshot"` |
| `synthetic` | Required boolean; `true` only for invented examples |
| `as_of` | ISO date or timestamp with timezone; observation date, not an invented quote timestamp |
| `base_currency` | Three uppercase letters for the real common currency; values must already be converted |
| `scope` | `whole_portfolio` or `stock_sleeve`; all caps, targets and scenario returns use this scope |
| `total_investable_value_base` | Optional; equal to summed values for whole portfolio; at least the sleeve value for stock sleeve. Omit when unknown |
| `positions` | Nonempty list, one row per unique security after combining accounts; includes cash. Total value must be positive |
| `target_weights` | Optional object mapping **every** security ID to a fraction 0–1; sum 1 within 1e-9; explicit zero for exits |
| `target_basis` | Required explanation of assumptions when targets are supplied; distinguish a comparison from a recommendation |
| `policy` | Optional, supports `max_issuer_weight`, `theme_caps` and required explanation `basis`; no universal defaults |
| `scenarios` | Optional list of explicit hypothetical return sets |
| `contribution` | Optional nonnegative `amount_base` and complete `allocation_weights` summing to 1; externally supplied fresh money added to the analyzed scope |

Each position requires `security_id`, `label`, `asset_type` (`company`, `fund`, `cash`, `bond`), finite nonnegative `value_base`, and `value_source` describing origin/date/conversion. Company and bond positions require `issuer_id`; different share classes and direct bonds of the same issuer aggregate for issuer concentration. Cash and fund positions are excluded from direct issuer caps; fund constituents are **not** inferred.

Optional `themes` is a list of unique labels backed by `theme_source`. Omitted/null means unclassified. An empty list means reviewed with no assigned theme; explain the basis. Do not use an empty list to hide missing research. Multiple tags are allowed and their capital weights can sum above 100%. The calculator does not estimate economic sensitivity or correlation from a tag.

An unowned candidate may have value zero so an authored comparison can include it. Its presence is not eligibility or evidence that it has been researched. Apply workflow gates before presenting its target as a recommendation. Enter cash as an explicit instrument such as `CASH:EUR`; no residual cash is inferred from incomplete target weights.

Each scenario requires unique `id`, `label`, `horizon`, `assumptions`, and `returns` mapping every position to a finite base-currency total return ≥ -1. Include cash and explicit zero assumptions. The horizon is common to all returns in that scenario. The script multiplies fixed initial weights by returns with no interim rebalancing, cash flows, taxes or transaction costs. Currency effects and distributions must already be included in each return assumption. Results describe the analyzed scope only; a stock-sleeve scenario is not a whole-portfolio loss estimate.

`max_issuer_weight` aggregates direct company and bond positions by issuer. `theme_caps` maps observed tags to fractions. Limits are within the declared scope. Unknown themes cannot be treated as unexposed; the output shows unclassified weight and incomplete theme coverage. With funds present, even a `no_direct_breach_found` result does not establish compliance after look-through. Other constraints such as liquidity floors, locked positions, turnover and sector caps require explicit additional analysis; the current script does not evaluate them.

For percentage-only holdings, diagnose the supplied weights directly, checking their denominator and cash coverage. This monetary calculator requires real current values; do not invent a portfolio balance or use a fake currency to obtain monetary outputs. Obtain amounts before using it for a monetary comparison.

## Synthetic example

All amounts, identities, targets, limits and shocks below are invented arithmetic examples, not recommended settings. `DEMO:*` identifiers must never be matched to real companies.

```json
{
  "schema_version": "1.0",
  "kind": "portfolio_snapshot",
  "synthetic": true,
  "as_of": "2026-09-24",
  "scope": "stock_sleeve",
  "base_currency": "EUR",
  "total_investable_value_base": "20000",
  "positions": [
    {"security_id": "DEMO:A", "issuer_id": "DEMO:ISSUER-A", "label": "Example A", "asset_type": "company", "value_base": "4000", "value_source": "Invented EUR value", "themes": ["Example theme"], "theme_source": "Invented classification"},
    {"security_id": "DEMO:B", "issuer_id": "DEMO:ISSUER-B", "label": "Example B", "asset_type": "company", "value_base": "4000", "value_source": "Invented EUR value", "themes": null},
    {"security_id": "CASH:EUR", "label": "Cash", "asset_type": "cash", "value_base": "2000", "value_source": "Invented EUR balance", "themes": [], "theme_source": "Cash has no example business-theme tag"}
  ],
  "target_weights": {"DEMO:A": "0.3", "DEMO:B": "0.3", "CASH:EUR": "0.4"},
  "target_basis": "Invented comparison only; no investor profile supplied",
  "policy": {"max_issuer_weight": "0.35", "theme_caps": {"Example theme": "0.35"}, "basis": "Invented limits for arithmetic demonstration"},
  "scenarios": [{"id": "demo-stress", "label": "Hypothetical joint decline", "horizon": "One year", "assumptions": "A loses 50%, B loses 25%, EUR cash unchanged; no costs or rebalancing", "returns": {"DEMO:A": "-0.5", "DEMO:B": "-0.25", "CASH:EUR": "0"}}],
  "contribution": {"amount_base": "1000", "allocation_weights": {"DEMO:A": "0", "DEMO:B": "0", "CASH:EUR": "1"}}
}
```

Expected arithmetic: analyzed value €10,000; A and B each 40% of the sleeve and 20% of total investable assets. The hypothetical current loss is €3,000 (30% of the sleeve); target loss is €2,250 (22.5% of the sleeve). Total-portfolio scenario loss remains uncomputed because assets outside the sleeve were not stressed. The cash contribution reduces A's sleeve weight to approximately 36.36%. Unknown B theme exposure prevents a complete theme-cap conclusion.

## Output interpretation

Show `current_exposure` beside `target_exposure` when present. `delta_weight` is target minus current in fractional units; multiply by 100 for percentage points. `delta_value_base` compares allocations at unchanged total value before costs and is not a trade instruction. Targets use the existing sleeve size; changing the sleeve itself requires a separate whole-portfolio proposal.

The effective number counts all positions including cash and depends on the instrument grouping. It is a weight-concentration statistic, not a count of independent risks. Report direct issuer and fund-overlap limitations alongside it. Preserve `suitability: not_assessed_by_calculator` in machine-readable output. Do not translate a numerically valid snapshot into a recommendation without applying the workflow.

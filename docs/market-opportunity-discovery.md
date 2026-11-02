# Market opportunity discovery

Status: on-demand research workflow, defined 2 November 2026. This is a method for finding **new publicly traded investment candidates**, not a completed automated screener or a recommendation engine. Each run is initiated by the user. No recurring job, automatic monitoring, trading, or position sizing is authorized.

## Route the request correctly

| Request | Workflow |
| --- | --- |
| "Run the market sweep", or check the news, macro, geopolitics and saved questions | Existing [market-sweep design](market-sweep-design.md), with its own registry, evidence ledger and rendering scripts. |
| "Find interesting stocks", "scan the market for opportunities", or "what companies deserve research?" | This open-market opportunity discovery workflow. |
| "Find investments that improve my portfolio" | This workflow **plus** the stock-analysis skill's private portfolio discovery/profile rules. |
| Deep-dive or allocate to a candidate | Run the existing full company analysis first; apply portfolio decision gates before proposing funded targets. |

Do not replace the established market-sweep pipeline, rename its reports, or use `market-sweep-registry.json` for opportunity candidates. If a request uses only "market sweep", retain the established meaning unless the user explicitly asks to screen for new companies.

## 1. Define a reproducible search universe

Freeze an information cutoff and record the user's objective, investment horizon, eligible exchanges/countries, asset types, size/liquidity boundaries, currency considerations, sector exclusions and any constraints. Ask at most two high-impact questions when their answers would materially change the search. Reuse recent explicit answers. Do not infer risk capacity from a desire to find high-growth stocks.

When no scope is supplied, start with **liquid, exchange-listed common equities and verified ADRs in major developed markets**, while deliberately sampling different sectors and adding an explicitly labeled exploratory sleeve for smaller or earlier-stage companies. State geographic, size and data-provider biases; this default is a starting sample, **not** the entire global stock market. Separate ETFs/funds from operating companies and check vehicle eligibility before comparison. Verify exact issuer, exchange, share class, listing/reporting currency and ADR terms; ticker matches alone are insufficient.

For a claimed systematic screen, record the provider, security-universe size, as-of date, filters, exclusion counts, missing-data handling and all retrieval limits. If only searches or curated lists are available, describe an evidence-led **sample**, not a census or top-N ranking of all listed companies. Do not treat a search engine's result order as a quantitative screen. Do not fabricate a universe denominator or hide regions or small caps that could not be checked.

## 2. Generate leads through independent lenses

Use multiple lanes so that one fashionable narrative does not dominate:

1. **Quality at a plausible price:** durable economics, cash generation, balance-sheet resilience and valuation relative to prospects.
2. **Improving fundamentals:** accelerating organic growth, margins, recurring revenue, per-share cash generation or return on capital; verify base effects and one-offs.
3. **Valuation dislocations:** a price decline or temporary problem that appears larger than the supported long-term business damage; include the strongest bear case.
4. **Structural change:** verifiable demand shifts, regulation, infrastructure investment, product adoption and supply-chain beneficiaries; distinguish addressable-market stories from captured economics.
5. **Catalysts and neglected situations:** identifiable changes in capital allocation, financing, leadership, profitability or industry structure, with a date and observable success/failure measures.
6. **Diversifiers and counterexamples:** credible candidates outside the dominant themes and explicit alternatives to the most popular idea.

The existing market landscape can supply leads, but is not a substitute for screening. Include followed companies as benchmarks where useful, while making a separate list of genuinely new candidates. Deduplicate by legal issuer and security identity. Keep a longlist and a short rejection log so later runs can distinguish unexamined from rejected.

## 3. Apply a two-stage evidence funnel

**Triage:** For each longlist candidate, establish identity, business model, sector, recent operating trend, approximate valuation, funding position, relevant event and data freshness. Exclude clear identity failures, ineligible instruments, inaccessible or stale decisive figures, and companies that contradict explicit constraints. Mark "needs verification" rather than inventing a failure or pass. Do not apply one industry's accounting thresholds mechanically to banks, insurers, REITs, cyclicals or pre-revenue ventures.

**Verification:** For survivors, read the latest original annual/interim filings, earnings releases and relevant issuer/counterparty/regulator originals. Use timestamped price and comparable valuation inputs. Check:

- Growth quality: organic versus acquisitions, per-share versus aggregate, historical versus guidance or consensus, and whether margins/cash follow sales.
- Financial resilience: debt maturities, interest burden, cash runway, dilution, working capital and capital intensity, as relevant to the business.
- Competitive case: evidence for customer willingness to pay, switching costs, distribution, cost position, market share or other durable advantages.
- Price paid: appropriate TTM/forward earnings, EV, cash-flow or sector-specific measures with consistent dates, currency and accounting basis; a good business can be a poor investment at an excessive price.
- Main risk and falsification: one or more realistic ways the thesis could fail, not just generic market volatility; note what evidence would change the view.
- Catalysts: actual next financial report, commercial milestone, regulatory decision or observable operational change; distinguish announced plans from completed events.

Trace decisive claims to the underlying source and record URL, publication and retrieval dates, financial period and calculation basis. Screeners, analyst commentary and media are **discovery leads**, not sufficient primary proof. Keep estimates and inference separate from reported facts. When evidence conflicts, explain it or mark the candidate unresolved. No access to paid data is assumed, and no paywall bypass is allowed.

## 4. Rank research priority, not imagined certainty

Compare survivors across these dimensions, explaining each judgment: business durability, improvement/growth evidence, financial resilience, valuation margin for error, catalyst credibility, downside exposure, and evidence completeness. For a portfolio-aware run, assess diversification and overlapping drivers **separately** from business merit.

Use an ordinal research-priority tier:

| Tier | Meaning |
| --- | --- |
| **Deep-dive next** | A reasonably supported, potentially attractive case with an identifiable decision-relevant question. Still not a buy recommendation. |
| **Watch for price or evidence** | Interesting business or catalyst, but valuation, milestone or missing data prevents a strong case today. |
| **Exploratory** | Early or speculative idea worth monitoring, with substantial thesis uncertainty. |
| **Reject / defer** | Fails a stated constraint, has a disqualifying risk, or lacks enough evidence even for a reliable preliminary view. |

Rank within tiers only with explicit reasons. Do not produce a weighted "opportunity score", probabilistic return forecast or universal numerical cutoffs without a specified, validated model. Separate quality, valuation and confidence; missing evidence must not turn into an optimistic default. Compare at the same price/filing cutoff where feasible, and make unavoidable date differences visible.

## 5. Deliver a readable discovery report

Lead with the strongest cross-market findings and the most important uncertainty, then provide:

- **Scope and coverage audit:** window/cutoff, countries/exchanges, data sources, filters, observed universe or sample count, longlist and verified counts, source failures and unsearched areas. Never imply comprehensive coverage from a finite news/search sample.
- **Opportunity map:** the few economic trends supported by evidence, with counterarguments and overlooked sectors. Clearly label hypothesis versus confirmed company economics.
- **Shortlist:** normally 5–15 candidates, fewer if evidence is insufficient. Give company and verified security, business in plain language, discovery lens, current operating/valuation evidence with dates, thesis, strongest bear case, next catalyst or research question, tier, confidence and primary source links.
- **Alternatives and rejects:** at least the consequential exclusions or comparable names not selected, and why. Distinguish a low priority from a verdict that the business is bad.
- **Next research queue:** which 1–3 deserve full stock-analysis reports, what must be verified next, and when to revisit the other leads.

Treat this as a **research shortlist**, not a funded allocation or automatic watchlist addition. Do not create company archive records, modify saved earnings questions or clear review states merely because a company appeared. Only a completed company analysis enters the ordinary research registry.

For portfolio-aware discovery, retrieve user-confirmed current holdings and profile privately, identify actual exposure gaps and funding trade-offs, and compare candidates with already owned/researched alternatives. Keep company findings distinct from portfolio suitability. A candidate cannot receive a funded target until current full-company evidence, constraints and the portfolio workflow's decision gates support it. Never publish personal share counts, portfolio amounts or private position data; use public percentages only where explicitly authorized.

## 6. Save and compare runs when requested

The user must initiate each run. For durable published work, save a dated, immutable evidence package under `research/opportunity-discovery/YYYY-MM-DD-rN/` in `MarginallyHarmless/stocks_v3`, including a scope/coverage manifest, a source-and-candidate ledger, rejected/unknown leads, and a readable report under `reports/`. Use a new revision for changed facts, criteria or cutoff; preserve older results. Keep the output distinct from the existing market-sweep registry. If creating a public HTML report, validate its links, rendering and index integration before saying it is published; no dedicated automated opportunity-discovery renderer is installed yet.

A future follow-up compares identical security identities, dates, universe rules and original research triggers; newly eligible/ineligible or never-covered names are not retroactive winners/losers. Preserve the original source cutoff and label changed data. No automatic polling, notification, trade execution or background run is implied.

Use the stock-analysis skill's `research-method.md` for fundamental definitions and `portfolio-workflow.md` for personalized applications. The [existing market sweep](market-sweep-design.md) remains authoritative for tracked-company news, macro, geopolitics and saved-question coverage.

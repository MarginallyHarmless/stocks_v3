# Investor profile and portfolio allocation

Contents: [Interview](#interview), [Decision gates](#decision-gates), [Allocation](#allocation), [Discovery](#discovery), [Deliver](#deliver), [Persistence](#persistence), [Evidence](#evidence).

## Interview

Use this workflow for the user's personal investing decisions, independently of the company-report checklist. Assess loss capacity, behavioral tolerance, goals and practical constraints separately. Never manufacture a validated score, profile-to-weight lookup or predicted loss ceiling. Treat the following as a structured interview, not a psychometrically validated test. Do not infer answers from occupation, age, beginner status, researched tickers or unrelated personal history.

Start with up to three unanswered questions. Ask naturally in the user's language, allow approximate amounts or ranges, and explain only distinctions needed to answer. Reuse explicit recent answers and ask for an update only when their freshness matters. A request to build the component does not itself supply personal profile answers.

First round:

1. Scope: the whole investable portfolio, or only the individual-stock portion? If only stocks, establish how large that portion is relative to other investments before making whole-portfolio claims.
2. Purpose and timing: what is this money for, and when might the first withdrawal occur? Distinguish an essential near-term goal from flexible long-term growth.
3. Holdings: which companies/funds are actually owned, their current amounts or percentages, cash included, and the spending currency? Accept a user-provided list or statement; do not require brokerage access.

Later rounds, at most three main questions per message:

- Financial capacity: reserves outside this portfolio; reliable contributions and income stability; debt and unavoidable payments; planned withdrawals. Establish whether employment income could fall with the same investments. Collect only detail that changes the decision; sensitive background is unnecessary.
- Tolerance: actual behavior during prior losses; hypothetical losses in both money and percentages; duration of uncertainty and prolonged benchmark underperformance. Separate “could afford” from “would feel comfortable.” Never promise recovery or treat “buy more” as the correct answer. If portfolio value is unknown, label amounts hypothetical or use percentages.
- Implementation: tax residence/account type only when relevant, allowed assets, restrictions or locked holdings, willingness to add unowned companies, contribution schedule, monitoring capacity and broker availability.

Record answers verbatim or faithfully summarized with dates, separate derived judgments and unresolved contradictions, and distinguish no experience from missing information. Do not average away a conflict between high willingness and limited financial capacity. Knowledge informs explanation and product complexity; it does not establish risk tolerance.

Conclude with a short profile narrative, evidence for each dimension, goal-specific constraints, unresolved issues and the next review trigger. Label it provisional where material answers are absent. Do not ask for an arbitrary desired return and treat it as a feasible expectation. If goal math requires implausible returns, explain alternatives in timing, contribution amount or goal size.

## Decision gates

| Available information | Permitted outcome |
|---|---|
| Goal/scope only | Continue intake; explain principles with labeled hypotheticals |
| Holdings only | Describe weights, concentration and evidence gaps; do not certify suitability |
| Holdings as percentages | Normalize only after confirming the denominator and whether cash is included; diagnose in percentages; do not invent amounts |
| Profile plus dated holdings, stale company evidence | Diagnose exposure and identify refresh needs; keep unsupported targets unresolved |
| Profile, holdings, current decisive company evidence and explicit constraints | Propose reasoned target weights/ranges and compare alternatives |
| Missing historical return data | Still provide supported qualitative exposure and hypothetical scenarios; leave correlations/volatility unavailable |
| Incompatible goals or infeasible caps | Explain conflicts and alternatives; do not weaken constraints silently |

Keep goal-specific horizons and cash requirements visible. Distinguish total investable portfolio, stock portion and company weights within that portion. A concentrated stock portion can coexist with a diversified overall portfolio; conversely a stock-only allocation may not meet a short-term need. Do not treat personal net worth, home equity or pension entitlements as deployable cash.

## Allocation

1. Resolve the latest registry from the canonical project, then map **user-confirmed** holdings to issuer/security identities. Support unresearched holdings and funds without making up reports. Preserve report IDs, cutoffs and outstanding earnings checks. Refresh prices, new results, financing and thesis-changing events before relying on current valuation or risks. Browse for current investment recommendations.
2. Establish allowed investments, investable budget, reserves, explicit company/issuer limits, overlapping theme limits, restrictions and monitoring capacity. Each numerical limit needs an investor-specific rationale and version; do not prescribe universal caps. Default to unlevered long-only cash investments for the calculator. Route leverage, shorts and derivatives to a separately specified model, not this arithmetic.
3. Extract separate judgments for business resilience, valuation, funding/dilution, catalysts, evidence quality and portfolio role. Do not turn a company rating into an expected return or target weight mechanically. Critical unknowns constrain decisions. Zero allocation remains valid.
4. Diagnose common drivers from evidence: business lines, customers, geography, rates, financing, growth expectations and currency. Distinguish observed historical correlations from qualitative hypotheses. Revenue-linked suppliers and buyers can respond differently to the same shock. Exposures through funds require dated look-through; missing constituents are not zero exposure.
5. Construct an explained proposal, considering equal weighting of eligible holdings as a comparison where feasible. Author one internally consistent target vector, optional ranges around it, reasons for each tilt, and relevant alternatives. Round displayed percentages sensibly; retain precision for calculation. Do not label subjective judgments as model-derived optimums.
6. Compare existing holdings with any expanded alternative using the same budget, constraints, timestamps and stress assumptions. Cash/reserves remain explicit. If caps cannot accommodate 100%, report infeasibility or an allowed residual reserve; never renormalize capped weights beyond limits. A company removed from the proposal needs an explicit zero target.
7. Use `scripts/portfolio.py` with the contract in `portfolio-data.md` for reproducible arithmetic. The script validates numbers and comparisons, not suitability, evidence freshness or the profile. Explain this distinction when relevant to interpreting results; keep routine implementation detail out of the report.
8. Stress consistent portfolio-wide scenarios. Name horizon, shocks, rationale, currency and costs. Keep all holdings' scenario returns explicit, including cash and any assumed zero. Allow a complete loss for an unlevered stock. Do not label scenario output a percentile or worst possible loss. Never assign bear/base/bull probabilities from confident prose. Compare simultaneous and issuer-specific shocks; personal loss preference is not a guaranteed drawdown ceiling.
9. Explain how new contributions change weights before considering sales. Compare the time required to repair concentration with the risk of waiting. Include spread, commissions, FX and tax assumptions in a separate implementation estimate; do not silently import US tax rules. Recheck local rules when needed. Clearly distinguish gross allocation arithmetic from net executable trades.
10. Set review triggers: material investor change, scheduled review, breached allocation band, new earnings/financing evidence, or thesis invalidation. A price fall is not itself a reason to restore a target. A strong quarter does not automatically increase portfolio capacity. Preserve old decisions when revising future targets.

Advanced statistics require dated total-return data, aligned observations, corporate-action handling, suitable currency conventions and declared missing-data policy. Never correlate raw price levels, backfill pre-listing history with zero, or reuse a changed business's old history without explaining limitations. Test estimation-window sensitivity. Do not claim optimizers, covariance models or simulations ran unless actual inputs, method and output exist.

## Discovery

Separate owned companies, researched-unowned companies and outside research candidates. Suggest additions only after diagnosing a portfolio gap or supported opportunity. For each candidate state:

- The gap or opportunity and why existing holdings do not address it well.
- Current business/valuation case and material uncertainties.
- What holding or cash allocation would fund it.
- Change in exposures and scenario outcomes under comparable assumptions.
- Risks newly introduced, research freshness and the simpler alternative considered.

Complete the relevant company research before assigning a funded target. An unresearched name is a research candidate. Consider a broad fund, appropriate reserves, or no change if these meet the objective better and are permitted. Do not fill sector slots mechanically, pad candidate lists, or assume another stock fixes asset-class or near-term liquidity risk.

## Deliver

Use the existing beginner-first principles and the user's chosen language. Lead with portfolio fit, the largest vulnerability, the most useful change and material uncertainty. A concise conversational result is valid; use a private standalone artifact when richer comparison helps.

Show an aligned table with company, current weight, proposed target/range, role, reason, and trigger for review. Identify the denominator prominently and show total-portfolio weights for a stock portion when known. Put the proposed portfolio beside the current one using the same scenarios. Keep arithmetic, assumptions and judgments distinguishable. Correlation and risk-contribution graphics are optional only when computed; theme bars represent tagged capital, not statistical risk shares, and may overlap.

Always include data cutoff, profile status, goals/scope, source report links, missing coverage, explicit policy constraints and the next review items. Show report existence separately from ownership. State unknown total holdings or fund constituents when this limits a conclusion. Avoid securities-specific target numbers when the decision gates are not met; complete the supported diagnosis first.

## Persistence

Maintain separate versioned records: profile, holdings snapshot, policy, proposed allocation, and decision/review history. Keep user statements separate from interpretations and sources; store recommendation reasons, report IDs, quote/FX timestamps, scenarios and changed assumptions. Link a new version to its predecessor rather than silently rewriting the earlier assessment.

Personal records are private. Save user-facing personal files through Library, retaining its identity on updates, or use an explicitly chosen private destination. Do not put them in the public research repository, Pages package, company registry/archive, skill files or test fixtures. Synthetic examples and reusable methodology can be public. If private saving is unavailable, preserve conversational progress and state that durable personal saving is incomplete. Never substitute public publishing.

When resuming, retrieve the actual saved private records and confirm holdings that may have changed. Do not reconstruct balances, past tolerance answers or old target criteria from memory. Do not schedule monitoring or execute trades as part of this workflow.

## Evidence

Methodology checked 2026-09-24. Consult the full project research brief at `research/portfolio/portfolio-allocation-research-2026-09-24.md` for the 22-source review; the skill remains usable without that file. Recheck current data and any jurisdiction-specific requirements when applying them.

- [CFA, Investment Risk Profiling (2020)](https://rpc.cfainstitute.org/research/reports/investment-risk-profiling): distinct required return, ability and behavioral tolerance; use validated instruments before claiming psychometric validity.
- [ESMA, suitability guidance (2023)](https://www.esma.europa.eu/sites/default/files/2023-04/ESMA35-43-3172_Guidelines_on_certain_aspects_of_the_MiFID_II_suitability_requirements.pdf): concrete questions and consistency checks; a design reference, not a claim of regulatory compliance.
- [CFA, portfolio planning (2026)](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/basics-of-portfolio-planning-and-construction): objectives, constraints and investment policy.
- [FINRA, concentration risk](https://www.finra.org/investors/insights/concentration-risk): correlated holdings and fund overlap.
- [DeMiguel, Garlappi and Uppal (2009)](https://academic.oup.com/rfs/article-abstract/22/5/1915/1592901): estimation uncertainty and the usefulness of an equal-weight comparison; not universal equal-weight superiority.
- [CFA, market risk (2026)](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/measuring-managing-market-risk): historical versus hypothetical scenarios and model limitations.
- [Vanguard, rebalancing](https://investor.vanguard.com/investor-resources-education/portfolio-management/rebalancing-your-portfolio): risk maintenance, costs and contribution-based adjustments.

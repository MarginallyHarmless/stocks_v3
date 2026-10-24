# Investor profiling and portfolio allocation

Research brief for Stock Analysis v3 · 24 September 2026

This brief covers methodology and proposes a component design. It does not establish the investor's profile or recommend personal company weights. Holdings, goals, investable assets, spending needs and loss capacity have not been collected.

The project was inspected at commit `8e9ec3f`. Its registry contains 14 researched companies: AVGO, PLTR, NBIS, ONDS, HOOD, APP, GOOG, CEG, ISRG, VST, SOFI, ASTS, META and LEU. A research entry is not evidence of ownership. Company reports were not financially refreshed for this methodology review.

**The recommended approach is a goal-based allocation process with explicit risk limits, using existing company research as evidence for security selection and sizing.** Start with the investor's financial circumstances, decide how much belongs in the individual-stock portion, then distribute that portion across suitable companies. Compare the resulting portfolio with simple alternatives and show its vulnerabilities. Additional companies should qualify by the improvement they make to the whole portfolio.

The 22 references below are primary institutional guidance, original research, or authors' research summaries. The source register specifies the material inspected. Established findings, historical observations, illustrative arithmetic and proposed product rules are distinguished throughout. Proposed rules are design judgments; they are not scientifically calibrated defaults.

**1. What the evidence supports**

Portfolio construction involves two related decisions: allocating across broad assets, and selecting the investments that implement that allocation. CFA's framework explicitly separates these steps. Starting with favorite stocks can bypass the first decision and produce a portfolio inconsistent with the purpose of the money. [S04]

Investor profiling needs financial and behavioral information. CFA's risk-profiling research distinguishes required return, ability to bear risk, and behavioral loss tolerance. These can conflict. A goal that needs more return than the investor can responsibly pursue calls for revisiting the goal, saving rate or timing. A higher desired return is not evidence of greater loss capacity. [S01]

Diversification depends on exposures and relationships, including overlapping fund holdings. Merely counting companies is insufficient. FINRA identifies correlated assets and concentration that develops through price appreciation as important sources of risk. [S06]

Optimization is useful, but estimated inputs can be unreliable. DeMiguel, Garlappi and Uppal tested 14 portfolio methods across seven datasets; none consistently beat equal weighting across their stated out-of-sample measures. This is a result for their tests, not proof that equal weighting always wins. It supports requiring simple comparison portfolios before trusting complexity. [S08]

There is no universally correct number of holdings, company cap, stock/bond split, or rebalancing threshold. Those are decisions that require an investor objective, a defined investment universe and explicit assumptions.

**2. Assess the investor on separate dimensions**

| Dimension | What it establishes | Information to collect | Consequence for this component |
|---|---|---|---|
| Financial loss capacity | What can be lost without disrupting essential plans | Available reserves, liabilities, income stability, dependants, planned withdrawals, other assets | Constrains exposure even when enthusiasm for risk is high |
| Behavioral tolerance | What uncertainty and losses the investor can live with | Responses to loss scenarios, actual behavior in previous declines, reactions to prolonged underperformance | Informs the range of strategies likely to remain usable |
| Goals and required return | What the money needs to achieve | Amount, date, contributions, inflation basis, priority and flexibility for each goal | Tests whether the plan is plausible |
| Knowledge and experience | Which products and explanations are understood | Instruments used, duration of experience, understanding of diversification and losses | Determines explanation and product-complexity needs |
| Practical constraints | What can actually be implemented | Accounts, broker access, transaction costs, spending currencies, tax circumstances, restrictions | Changes the feasible set and transition plan |

This table is a proposed product decomposition informed by investor-profiling and portfolio-planning guidance. Knowledge should remain separate from willingness to take risk. Beginner status alone does not justify a conservative allocation; technical fluency does not establish financial capacity. [S01, S03]

The output should be a short narrative with supporting dimensions, for example: “Comfortable with large fluctuations, but upcoming spending limits how much of these funds can be exposed to them.” A single label such as “aggressive” is insufficient to explain that conflict.

**Questionnaire design.** ESMA's guidance favors understandable questions, factual financial information, concrete loss scenarios and consistency checks over broad self-assessment. Its suitability framework separates knowledge and experience, financial situation, and investment objectives. This is a useful design reference; using these ideas is not a claim that the project meets a regulatory standard. [S02]

For this project, I propose a short staged interview with follow-ups only where answers affect the decision:

1. What is each pool of money for, how much is required, and when?
2. Which goals are essential, and which can change in amount or timing?
3. How much is currently invested, held in reserve, or committed to other uses?
4. What contributions and withdrawals are expected, and how reliable are they?
5. Could income fall at the same time as the investments? Are employer shares involved?
6. What debt payments and other financial commitments constrain the plan?
7. Which currencies matter for future spending?
8. Which companies and funds are actually owned, in what amounts?
9. What happened during the investor's largest experienced loss? No experience is a valid answer.
10. How would a substantial portfolio loss affect spending and behavior, separately?
11. How would the investor react to several years of lagging a broad market benchmark?
12. Are broad funds, cash and bonds allowed, or is this strictly an individual-stock allocation?
13. How many companies can realistically be monitored, and are any holdings locked?

Loss scenarios should show both percentages and money, describe an uncertain recovery, and avoid implying that a decline always rebounds. Neutral wording matters: “buy more” is not automatically the correct answer.

**A custom interview is not a validated psychological test.** CFA recommends instruments with demonstrated reliability and validity. For an eventual numerical tolerance scale, investigate the original instrument's validation, licensing and language adaptation. Until then, retain answers and reasons, label the assessment provisional, and avoid invented score cutoffs or confidence percentages. [S01]

**3. Define exactly which money is being allocated**

The product should distinguish these denominators:

| Scope | Purpose | Display requirement |
|---|---|---|
| Financial context | Understand reserves, liabilities and other assets | Clearly identify what is available for investment |
| Total investable portfolio | Allocate among permitted asset classes | Weights include relevant cash, funds and bonds |
| Individual-stock portion | Allocate among companies | Show company weight within this portion and within total investable assets |

Illustrative calculation: if individual stocks are 40% of investable assets and a company is 10% of that stock portion, the company is 4% of total investable assets. “10% in Company A” is ambiguous without the denominator.

The system should support a stock-only request, but label its scope. Changing the distribution among equities cannot by itself supply money reserved for near-term spending. SEC guidance emphasizes both asset-class allocation and diversification within classes. [S05]

A proposed whole-portfolio alternative can use a broad diversified foundation plus a separately sized stock-selection portion. This is an option to compare, not a preset allocation. If the user wants only individual companies, the output should explain any unmet risk requirement instead of forcing an apparently suitable 100% allocation.

**4. Evaluate several meanings of risk**

| Risk | Plain-language question | Proposed evidence/display |
|---|---|---|
| Company failure or permanent impairment | Could this business destroy a meaningful amount of capital? | Balance sheet, financing needs, competitive threats and thesis failures |
| Market fluctuations | How widely might portfolio value move? | Historical volatility with period, frequency and currency |
| Drawdown | How far did value fall from a previous peak? | Historical peak-to-trough loss; scenario losses shown separately |
| Concentration | What common event could damage several holdings? | Company, industry, theme and factor exposures |
| Liquidity and timing | Could money be needed when selling is difficult or prices are depressed? | Cash-flow schedule, reserves and instrument liquidity |
| Currency and inflation | Will the proceeds buy what the investor needs? | Returns and scenarios in spending currency and real purchasing power |
| Behavior and maintenance | Could the investor abandon or fail to maintain the plan? | Scenario responses, monitoring workload and review rules |

Volatility, drawdown and expected shortfall answer different questions. Expected shortfall describes average loss in a modeled adverse tail; it is neither a maximum loss nor a promise. Historical statistics and forward-looking stress scenarios should complement each other. [S12, S13]

Correlations can change. BIS documented a switch toward positive US stock–government-bond correlations during the inflation period beginning in 2021. That episode supports testing joint losses; it is not a statement about today's exact correlation or a reason to assume bonds never diversify stocks. [S14]

Withdrawals make return order matter. Poor returns early in a withdrawal period can reduce the assets available for recovery because spending continues. The component should therefore model cash flows, rather than judging every plan only by average annual returns. [S17]

**5. What allocation methods offer**

The descriptions below summarize the methods; the final column is my proposed use in this project.

| Method | Main idea | Main limitation | Proposed use |
|---|---|---|---|
| Equal weighting | Allocate the same amount to each eligible holding | Equal money is not equal risk; the chosen universe may already be concentrated | Transparent baseline, subject to feasibility and caps |
| Fundamental judgment with limits | Give different weights based on business evidence, valuation, uncertainty and portfolio role | Subjective judgments can become inconsistent | First-version approach with documented reasons and sensitivity checks |
| Inverse volatility | Give smaller weights to assets with larger historical fluctuations | Ignores correlation in its simplest form and misses business risks | Diagnostic comparison, not automatic recommendation |
| Equal risk contribution | Balance each holding's modeled contribution to portfolio risk | Model-dependent; can concentrate capital in low-volatility exposures | Later comparison if data are adequate |
| Minimum variance | Find weights with the lowest modeled volatility under constraints | Low estimated volatility does not establish capital safety or attractive valuation | Secondary comparison |
| Mean–variance / maximum Sharpe | Balance estimated returns against covariance-based risk | Return estimates can drive unstable, concentrated results | Research benchmark; unsuitable as the unquestioned default |
| Black–Litterman | Combine a market-based starting point with explicit return views and uncertainty | Requires defensible starting assumptions and calibrated views | Possible later extension |
| Hierarchical risk parity | Group assets using relationships before allocating risk | Results still depend on data, clustering and the eligible universe | Possible later robustness comparison |

CFA describes the sensitivity and concentration problems of mean–variance methods. Ledoit and Wolf propose shrinking noisy covariance estimates toward a more structured estimate. This improves estimation in their research; it does not remove forecasting uncertainty. [S04, S09]

Black–Litterman's original explanation explicitly connects allocation changes to views and confidence. An AI-written company report's confident tone is not a calibrated probability and should never be used as that model's confidence input. [S10; latter sentence is a product rule]

The HRP author's materials describe hierarchical construction and a simulation comparison. That is a reason to investigate it, not evidence that it will outperform for this particular collection of stocks. [S11]

**Recommendation:** begin with explicit targets and allowable ranges, justified by fundamentals and checked against portfolio limits. Use quantitative methods to expose disagreements and fragility. Do not promise a uniquely optimal set of percentages.

**6. Turn company research into position-sizing evidence**

The existing reports should supply evidence for distinct questions:

| Company input | Effect on allocation reasoning |
|---|---|
| Cash generation and balance-sheet resilience | Ability to withstand operating or financing stress |
| Growth drivers and economic sensitivities | What the portfolio is depending on |
| Current valuation and scenario assumptions | What expectations are already in the price |
| Dilution, project dependencies and cash runway | Potential severity and timing of unfavorable outcomes |
| Confidence in evidence and unresolved gaps | Whether a decision is sufficiently supported |
| Thesis invalidation conditions | What developments require a review |
| Historical market behavior | Additional evidence about co-movement and fluctuations |

These dimensions should not collapse into an unexplained “company score” that mechanically becomes a weight. A strong business can be expensive; a promising opportunity can deserve only a small allocation; a useful diversifier can still be a poor investment at its current price.

**Illustrative loss-budget arithmetic:** suppose one holding is allowed to contribute no more than 3 percentage points to portfolio loss under an assumed 60% stock decline. Its scenario-based weight ceiling is `3% / 60% = 5%`. At a 5% weight, a complete loss would cost 5 percentage points. The 60% shock, the 3% budget and the resulting 5% ceiling are invented examples, not recommended settings.

This ceiling only describes that scenario's direct contribution, with other holdings held unchanged. Multiple companies can fall together. If 35% of a portfolio experienced a shared 45% decline, its direct contribution would be a 15.75% portfolio loss before effects elsewhere. Individual caps must therefore be supplemented with aggregate exposure and scenario limits.

Stops cannot turn such assumptions into guaranteed loss ceilings. FINRA explains that a stop order can execute far from its trigger price, while a stop-limit order may not execute. Position sizing must remain meaningful without assuming perfect exits. [S19]

**7. Diagnose the current research universe carefully**

The following are *hypotheses to investigate from saved report descriptions*, not a measured correlation study or a claim about the investor's actual holdings:

| Potential connection | Examples in the registry | What to investigate |
|---|---|---|
| AI infrastructure and spending | AVGO, NBIS, GOOG, META; possible indirect links to CEG and VST | Supplier versus buyer exposure, spending commitments, energy-demand expectations |
| Digital advertising | APP, GOOG, META | Advertiser budgets, platform dependencies, competitive substitution |
| Consumer finance and market activity | HOOD, SOFI | Different sensitivities to trading volumes, funding, rates and consumer credit |
| Capital-intensive expansion or milestone delivery | NBIS, ASTS, LEU; ONDS has integration and funding questions | Financing conditions, dilution, delivery delays and independently timed milestones |
| Electricity and nuclear-related expectations | CEG, VST, LEU | Separate power prices, fuel supply, regulation and project economics |
| Healthcare technology | ISRG | Procedure demand, hospital investment and valuation sensitivity |

Economic links can produce different effects. A lower chip price could hurt a supplier while helping a buyer. A utility, a nuclear-fuel business and an AI infrastructure provider should not receive identical shocks merely because they appear in one investment narrative.

The tagging system should allow multiple exposures per issuer and explain the evidence behind each tag. Overlapping theme percentages must not be added as if they were mutually exclusive slices. Unknown exposures remain unknown, not zero.

Sector charts alone are insufficient. Useful diagnostics include largest issuer weight, top-five concentration, combined exposure through funds, common revenue drivers, financing dependence, and sensitivity to valuation changes. A stock's listing currency also does not fully describe its business's currency exposure.

**8. A proposed allocation workflow**

1. **Establish scope and completeness.** Confirm owned holdings, current values, cash, goal, time horizon and denominator. Permit a diagnostic result when data are incomplete; label recommendations provisional or unavailable as appropriate.
2. **Set the investor policy.** Record permissible assets, liquidity needs, monitoring capacity, company/theme limits and acceptable scenario outcomes. Every numerical policy setting needs a reason and version.
3. **Refresh decisive inputs.** Check current prices, relevant new results, financing events, corporate actions and thesis developments. Preserve the original reports and their cutoffs.
4. **Determine eligibility and role.** A report makes a company researched, not automatically suitable. Distinguish owned, researched-unowned, and new research candidates. A target of zero must remain possible.
5. **Construct a simple feasible baseline.** Equal weights can reveal how proposed tilts change the result, but they must pass the same constraints. Do not normalize away a meaningful cash balance.
6. **Propose targets and ranges.** Document why each differs from the baseline: valuation, resilience, uncertainty, overlap, or the investor's restrictions. Avoid meaningless decimal precision.
7. **Stress and compare.** Evaluate the current allocation, the proposed allocation using existing holdings, and any expanded alternative under the same assumptions.
8. **Build a transition plan.** Show the impact of new money, sales, costs and known tax constraints. A target allocation and a sensible path toward it are different deliverables.
9. **Save the decision record.** Preserve holdings date, profile version, report IDs, price/FX timestamps, assumptions, policy limits, alternatives and reasons.

Feasibility must be explicit. If the allowed company weights cannot sum to the required invested amount without breaking limits, return the conflicting constraints and possible remedies. Do not quietly weaken limits or stretch weak candidates to fill the pie.

**9. Evaluate new companies by their marginal contribution**

A candidate suggestion should answer: “What specific problem does this solve, at what cost, and compared with what alternative?”

For each candidate, require a current research case, plausible portfolio role, evidence of how its drivers differ, valuation assessment, material risks, suitable data, and a comparison with the existing allocation. Show which holding or cash allocation funds the addition. Adding a stock without specifying the replacement does not define a comparison.

Use three discovery pools: existing holdings, already researched but unowned companies, and outside candidates requiring research. Unresearched candidates can enter a research queue; they should not silently receive funded targets.

If the issue is dependence on advertising revenue, investigate different demand drivers. If it is excessive company-specific risk, compare a broad fund where permitted. If it is an upcoming withdrawal, investigate appropriate liquid reserves. A new company is not necessarily the best solution to every gap.

Bessembinder's university research summary reports that the top 2.4% of firms accounted for net global stock-market wealth creation in its 1991–2020 sample. This historical result illustrates the cost of missing exceptional winners and the limits of a narrow stock universe. It neither identifies future winners nor means every other stock lost money. [S07]

A useful candidate card should contain: portfolio gap, investment case, proposed funding source, effect under shared scenarios, newly introduced risks, data freshness, and why it is preferable to a simpler alternative. The system should be able to conclude that no addition is justified.

**10. Make risk understandable with consistent scenarios**

The proposed stress suite should consider a broad equity downturn, tighter financing, higher inflation and rates, weaker AI spending, advertising weakness, company-specific execution failure and an adverse currency move. These are scenario categories, not predictions. Each populated scenario needs a common horizon, documented shocks and an explanation of how exposures interact.

Keep three displays separate:

- **Observed history:** measured outcomes using identified data and an explicit methodology.
- **Hypothetical stress:** what the proposed allocation would lose under specified assumptions.
- **Forecast distribution:** model-generated outcomes, only if defensible return assumptions and a disclosed probability model exist.

Do not invent bear/base/bull probabilities from report prose. Do not sum independently modeled company bear cases and call the result a statistical percentile. A simultaneous downside scenario can be useful if labeled exactly that.

Show losses in money and percentages, alongside the affected goal. A preferred maximum drawdown is a planning constraint to test; it is not an enforceable ceiling on future losses. VaR, simulations and stress tests each have limitations, including dependence on distribution and co-movement assumptions. [S13]

Illustrative recovery arithmetic: a 20% decline needs a 25% gain to recover; a 30% decline needs about 42.9%; a 50% decline needs 100%, before withdrawals and costs. This explains why minimizing avoidable damage can matter even when the investor accepts volatility.

**11. Data requirements and numerical discipline**

Company reports alone cannot calculate reliable portfolio correlations or current allocation weights. The new component requires a separate market-data and holdings layer.

| Dataset | Minimum useful fields | Failure behavior |
|---|---|---|
| Holdings | Security identity, units or market value, currency, observation time, cash | Do not infer ownership from report existence |
| Investor context | Goals, liquidity, capacity, tolerance evidence, constraints, version date | Avoid definitive personalized weights when critical inputs are missing |
| Company evidence | Exact report/snapshot IDs, thesis, valuation basis, material gaps | Require a refresh when decisive evidence is stale |
| Returns | Total-return convention, corporate actions, dates, currency, missing-data flags | Report insufficient history; never fill pre-listing periods with zero returns |
| Currency | Explicit conversion direction, matching dates and source | Do not combine currency-incompatible values |
| Fund exposures, if applicable | Dated constituent weights and coverage | Show incomplete look-through rather than assuming no overlap |
| Implementation | Broker availability, fractional shares, spreads, commissions, tax-lot facts when needed | Label transition estimates incomplete |

Use returns, not price levels, for correlation. Align observation dates, investigate trading suspensions and economic discontinuities, and test multiple windows. A recently transformed business may have a long ticker history that poorly describes the current investment. Different estimation windows should be shown as a sensitivity, not selectively chosen for the most appealing outcome.

Currency should be tied to goals. Vanguard's currency research shows that identical investments can produce different home-currency outcomes; hedging effects depend on the asset mix and currency relationships. Its evidence does not supply a ready-made optimal hedge for RON spending. [S16]

Proposed calculation definitions:

- Current weight: base-currency market value divided by the explicitly defined portfolio value.
- Portfolio variance: `wᵀΣw`, where `Σ` is a dated covariance estimate on consistent returns.
- Contribution to variance: `wᵢ(Σw)ᵢ`; these contributions sum to variance. Divide by variance for shares where defined. Some contributions can be negative when an exposure offsets others.
- Scenario return: `Σ wᵢrᵢ` for a specified horizon and portfolio convention, with cash included and costs handled explicitly.
- Effective number of equally sized holdings: `1 / Σwᵢ²`, calculated within a clearly defined, normalized set. This measures weight concentration; it does not measure independence of business risks.

Report the observation window, return frequency, annualization convention and data limitations beside statistical outputs. The math should be deterministic and inspectable; language generation should explain results, not invent missing inputs.

**12. Rebalancing and maintenance**

Vanguard distinguishes calendar-based, threshold-based and combined rebalancing, and describes cash-flow methods that can reduce the need to sell. The stated purpose is to maintain intended risk; better returns are not guaranteed. [S15]

My proposed first-version policy is a scheduled review plus predefined drift triggers, with additional reviews after material company or investor changes. Review does not mean trade. Bands should reflect position size, cost and uncertainty; a threshold suited to a broad asset class may be unsuitable for a small company position.

New contributions should first be evaluated against underweight eligible positions and reserves. This may reduce turnover, but cannot always repair large concentration quickly enough. For example, an unchanged €8,000 holding in a €100,000 portfolio becomes 7.27% after €10,000 is added elsewhere. The effect depends on the size of contributions relative to the portfolio.

Distinguish price drift from a broken thesis. A price decline alone does not justify adding to a company. Review the existing watchlist and new evidence before restoring its old target. Likewise, a strong earnings update does not automatically justify a larger weight if valuation or aggregate exposure has worsened.

Costs include commissions, spreads, FX conversions, fund expenses and potential taxes. Small recurring fees compound over time. [S18] This brief does not assume a jurisdiction, account tax treatment or current Romanian tax rate. Those must be established for an implementation plan; percentages-only comparison can precede tax-lot analysis.

Regular contributions from income are different from deliberately delaying investment of an available lump sum. Vanguard describes the trade-off between immediate market exposure and staging purchases to manage entry anxiety. Neither approach corrects an unsuitable final allocation. [S22]

**13. Validation before trusting recommendations**

The component should be judged on suitability, clarity, robustness and implementation cost, as well as investment outcomes. Historical outperformance by itself is insufficient.

Research on backtest overfitting explains how choosing among many tested strategies can make impressive historical results misleading. Repeatedly adjusting an allocation rule to fit these 14 companies would create exactly the type of selection problem that needs scrutiny. [S21]

Proposed evaluation requirements:

- Compare with equal weighting where feasible and a relevant diversified benchmark, using the same dates, currency, dividends, cash flows and costs.
- Separate an illustration of today's holdings in past markets from a backtest of decisions actually available at each historical date.
- Avoid using today's reports to decide past weights; include delisted and failed securities where a historical investment universe is being tested.
- Test sensitivity to windows, shocks, expected returns and constraints. Large weight changes from small input changes should reduce confidence.
- Reserve unseen evaluation periods, document all configurations tried, and account for repeated testing. A single holdout is not a complete defense against selection bias.
- Verify that missing data, infeasible caps, restricted holdings, new listings, overlapping funds and short-horizon needs produce understandable outcomes.
- Track investor comprehension: can the user explain why a holding has its weight and what would change it?

Track goal progress separately from benchmark performance. Use time-weighted returns to assess investment performance apart from external contributions, and money-weighted returns to describe the investor's cash-flow experience when suitable data are available. Do not show either as a complete measure of suitability.

A common statistical misstatement should also be avoided: the famous “90%” asset-allocation finding does not mean asset allocation determines 90% of every investor's profit. Ibbotson and Kaplan distinguish variation over time, variation across funds and return levels. [S20]

**14. Recommended product output**

The first screen should answer: “Does this portfolio fit the purpose of my money, what is its largest vulnerability, and what change is worth considering?”

| Component | Useful output |
|---|---|
| Investor profile | Separate capacity and tolerance, goal dates, constraints and unresolved questions |
| Portfolio diagnosis | Current exposure, concentrated drivers, gaps and data quality |
| Allocation proposal | Current weight, target, range, portfolio role and reason for change |
| Alternatives | Existing holdings, expanded universe, and a diversified foundation where permitted |
| Stress comparison | Consistent side-by-side losses in percentage and money |
| New candidates | Specific gap addressed, displaced allocation, evidence and new risks |
| Next contribution | How additional money would change weights and remaining imbalances |
| Review checklist | Company watchlist triggers, portfolio drift and investor changes |

For visual clarity, use aligned current-versus-target bars with direct labels, followed by a compact explanatory table. Show portfolio composition and risk contribution as distinct views. Keep the denominator visible. Correlation heatmaps and advanced statistics can sit in optional detail; the main explanation must stand alone.

Personal profile and holdings data need private persistence separate from the public research and website deployment paths. The repository can contain methodology, schemas and synthetic examples. A future personal portfolio file must not be included automatically in Pages packaging or public company archives.

**15. Suggested delivery sequence**

1. **Profile and diagnosis:** collect factual inputs, record constraints, map actual holdings to reports, explain concentration and missing data.
2. **Allocation proposals:** add targets and ranges, reproducible scenario arithmetic, comparison portfolios and contribution planning.
3. **Candidate discovery:** research outside companies only when they address a diagnosed gap; compare marginal improvements.
4. **Advanced analytics:** add robust covariance estimates and model comparisons after reliable historical data and evaluation are available.

The first implementation should deliver an understandable decision record, not an impressive-looking optimizer. The next design decision is whether the component's primary scope is the whole investable portfolio or only the individual-stock portion. Actual holdings and investor inputs are required before personal allocations can follow.

**Source register**

All sources accessed 24 September 2026. Dates below come from the document or publication record where available, rather than treating a search engine's crawl date as publication. Relevant portions were inspected; an abstract or summary is identified as such. Asset-manager research is treated as evidence about its stated methodology, not independent proof of superiority for this investor.

| ID | Primary source and date | Material inspected and role |
|---|---|---|
| S01 | [CFA Institute — Investment Risk Profiling: A Guide for Financial Advisors](https://rpc.cfainstitute.org/sites/default/files/-/media/documents/survey/investment-risk-profiling.pdf), Hubble, Grable and Dannhauser, 2020 | Executive framework, risk capacity, psychometric assessment and conflicting-profile sections of the PDF |
| S02 | [ESMA — Guidelines on certain aspects of the MiFID II suitability requirements](https://www.esma.europa.eu/sites/default/files/2023-04/ESMA35-43-3172_Guidelines_on_certain_aspects_of_the_MiFID_II_suitability_requirements.pdf), 3 April 2023 | Questionnaire design, objective information, consistency and assessment sections; used as a design reference |
| S03 | [CFA Institute — Basics of Portfolio Planning and Construction](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/basics-of-portfolio-planning-and-construction), 2026 curriculum | Public introduction and summary: policy statement, objectives and constraints |
| S04 | [CFA Institute — Principles of Asset Allocation](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/principles-asset-allocation), 2026 curriculum | Public introduction and summary: two-stage construction, goals and optimization limitations |
| S05 | [SEC Investor.gov — Asset Allocation and Diversification](https://www.investor.gov/introduction-investing/getting-started/asset-allocation), undated page | Asset allocation, horizon, diversification and fund overlap guidance |
| S06 | [FINRA — Concentrate on Concentration Risk](https://www.finra.org/investors/insights/concentration-risk), 15 June 2022 | Correlated holdings, employer exposure, drift, liquidity and fund look-through |
| S07 | [Arizona State University — Do Stocks Outperform Treasury Bills?](https://wpcarey.asu.edu/department-finance/faculty-research/do-stocks-outperform-treasury-bills), research collection | University's summary of Bessembinder's global 1991–2020 evidence; numerical claim refers specifically to that sample |
| S08 | [DeMiguel, Garlappi and Uppal — Optimal Versus Naive Diversification](https://academic.oup.com/rfs/article-abstract/22/5/1915/1592901), Review of Financial Studies, May 2009 | Publisher abstract; out-of-sample comparison of 14 models across seven datasets |
| S09 | [Ledoit and Wolf — Honey, I Shrunk the Sample Covariance Matrix](https://www.econ.uzh.ch/dam/jcr:ffffffff-961c-1dd9-ffff-ffffb4762fbf/honey.pdf), November 2003 working paper | Abstract, shrinkage construction and empirical comparison sections; university-hosted author paper |
| S10 | [He and Litterman — The Intuition Behind Black–Litterman Model Portfolios](https://people.duke.edu/~charvey/Teaching/BA453_2006/GS_The_intuition_behind.pdf), December 1999 | Original Goldman Sachs paper, university-hosted copy; framework and interpretation of views/confidence |
| S11 | [Marcos López de Prado — Software and research materials](https://www.quantresearch.org/Software.htm), HRP entry dated 2015, associated paper 2016 | Author's implementation description and simulation summary; full journal paper was not accessible in this review |
| S12 | [CFA Institute — Active Equity Investing: Portfolio Construction](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/active-equity-investing-portfolio-construction), 2026 curriculum | Public summary: selection versus sizing, risk budgets, drawdown and costs |
| S13 | [CFA Institute — Measuring and Managing Market Risk](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/measuring-managing-market-risk), 2026 curriculum | Public summary: risk-model limitations, historical/hypothetical scenarios and risk constraints |
| S14 | [BIS — The correlation of equity and bond returns](https://www.bis.org/publications/correlation-equity-and-bond-returns), 4 December 2023 | Research box on inflation and changing stock–bond correlations |
| S15 | [Vanguard — Rebalancing your portfolio](https://investor.vanguard.com/investor-resources-education/portfolio-management/rebalancing-your-portfolio), undated page | Calendar, threshold and cash-flow approaches; purpose and costs |
| S16 | [Vanguard — The FX dimension: Evaluating currency hedging for global multi-asset portfolios](https://www.vanguard.co.uk/content/dam/intl/europe/documents/en/fas-fx-hedging-whitepaper-en-eu.pdf), May 2026 | Executive findings and sections on variable hedging effects and currency relationships |
| S17 | [Vanguard — Principles for Retirement Income](https://corporate.vanguard.com/content/dam/corp/research/pdf/vanguard_principles_retirement_income.pdf), edition retrieved September 2026 | Market/inflation risk and sequence-of-returns discussion; US retirement-specific rules not applied |
| S18 | [SEC Investor.gov — How Fees and Expenses Affect Your Investment Portfolio](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/updated), 23 July 2025 | Fee compounding and investment-cost disclosure guidance |
| S19 | [FINRA — Stop Orders: Factors to Consider During Volatile Markets](https://www.finra.org/investors/insights/stop-orders-factors-consider-during-volatile-markets), page retrieved September 2026 | Execution-price uncertainty and non-execution risk for stop-limit orders |
| S20 | [Ibbotson and Kaplan — Does Asset Allocation Policy Explain 40, 90, or 100 Percent of Performance?](https://rpc.cfainstitute.org/research/financial-analysts-journal/2000/does-asset-allocation-policy-explain-40-90-or-100-percent-of-performance), 2000 | Publisher summary distinguishing the three statistical questions; full article not accessed |
| S21 | [Bailey, Borwein, López de Prado and Zhu — The Probability of Backtest Overfitting](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf), revised February 2015 | Author-hosted paper: abstract, strategy-selection definition and evaluation discussion |
| S22 | [Vanguard — How to invest a lump sum of money](https://investor.vanguard.com/investor-resources-education/online-trading/dollar-cost-averaging-vs-lump-sum), page retrieved September 2026 | Investor education on immediate investment versus staged entry; no win-rate statistic used |

The scope deliberately leaves several choices open: a validated profiling instrument, personal constraints, target asset mix, market-data provider, numerical position limits and suitable outside candidates. Those require subsequent design or investor-specific evidence. No profile answers, holdings or allocations have been inferred from the user's research interests.

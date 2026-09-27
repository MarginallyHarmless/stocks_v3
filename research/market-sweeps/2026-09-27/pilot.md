# Free-source collection pilot — 21–27 September 2026

**Result:** the current project can supply a dynamic research scope for every followed company. Free original sources yielded useful evidence, but this pilot is a collection feasibility study, not a complete weekly market report. Recurring collection has not been activated.

## Frozen scope

- Window: 21 September 2026 00:00 through 27 September 2026 22:44:06, Europe/Bucharest (UTC+03:00).
- Registry revision: `ecdaa7bf1e0531508401cfe59c2fd69f142367c4`.
- Included: **16 companies and 108 exact follow-up questions** from their latest saved reports.
- All 16 archives verified; no company reports, question criteria, registry entries or earnings flags changed.
- AMZN, LEU and NOW research cutoffs fall inside this window. This is a retrospective collection exercise using current questions, not a point-in-time backtest.

## What was checked

Broad company-news discovery was attempted for every company, followed by issuer-index access checks and selected original documents. SEC recent-submissions JSON was retrieved for all 16 companies, yielding **26 filing metadata records** within the acceptance-time window. Only three of those filing documents were read for this sample; metadata discovery must not be presented as full filing review. Insider forms and registration documents are not automatically material business news.

Vistra required resolving its registry SEC file number to CIK 1692819 using the SEC ticker mapping and verifying the file number in SEC data. Its saved identity was preserved. This illustrates why the system needs explicit identifier resolution in addition to ticker searches.

| Company | Questions | SEC items | Issuer index access | Pilot observation |
| --- | ---: | ---: | --- | --- |
| AVGO | 7 | 5 | readable index | No in-window financial release visible on the reviewed index; broader product coverage remains partial. |
| PLTR | 7 | 0 | index not extractable | News index yielded little usable content; discovery leads need original-source confirmation. |
| NBIS | 7 | 1 | readable index | Latest visible release was September 8; no in-window item selected from this index. |
| ONDS | 7 | 4 | readable index | Acquisition release and associated 8-K read; update cash/dilution evidence at the next review. |
| HOOD | 7 | 4 | readable index | Latest visible IR release was September 10; Fed proposal is sector context only. |
| APP | 7 | 0 | index not extractable | Legal advertisement read as an unverified lead; complaint not reviewed. |
| GOOG | 7 | 0 | index not extractable | Separate Google blog original read: planned orbital AI test; no financial criterion resolved. |
| CEG | 7 | 0 | index unavailable | No primary in-window event selected; source gap prevents a no-news conclusion. |
| ISRG | 6 | 0 | index unavailable | No primary in-window event selected; index fallback still needed. |
| VST | 7 | 1 | readable index | Counterparty power agreement and September 24 debt completion filing read. |
| SOFI | 7 | 4 | index not extractable | Individual stablecoin settlement release read despite weak index extraction. |
| ASTS | 7 | 0 | index not extractable | No deployment/funding outcome adjudicated; issuer feed extraction still needs validation. |
| META | 7 | 5 | index not extractable | Discovery leads remain unverified in this sample; no saved question outcome changed. |
| LEU | 7 | 0 | readable index | Visible September 17 and September 9 partnership news predates this window. |
| NOW | 5 | 0 | index not extractable | Partner case study read; underlying implementation predates its publication. |
| AMZN | 6 | 2 | index not extractable | Debt registration and logistics-counterparty original read; distinguish publication from event date. |

Every row has partial overall news coverage: a readable index or successful API request cannot prove that all relevant events were found. “No item selected” means no item was selected from this sample, not that the company had no news.

## Shared-source tests

| Source | Observed result | Implication |
| --- | --- | --- |
| SEC submissions | 16/16 metadata requests successful; 26 records | Reliable candidate for filing discovery; document triage and historical pagination still needed |
| Federal Reserve RSS | HTTP 200; four in-window feed items; stablecoin proposal read | Feeds can separate discovery from document review |
| FRED public CSV, DGS10 | HTTP 200; sample ended on 24 September | Store observation date and retrieval time separately; do not silently substitute old data for a missing day |
| GDELT article API | HTTP 429; no usable article list; not retried | Keep discovery partial and implement bounded backoff/fallback before relying on this source |
| Issuer indexes | Some readable, others unavailable or yielded little usable content | Maintain company-specific fallbacks, including SEC exhibits and original counterparty releases |

FRED and Fed access are feasibility samples. A full inflation, labor, growth, credit, energy, international-policy and geopolitical sweep was **not** performed. No conclusion about the overall current market landscape follows from these samples. Search discovery also produced stale events, duplicated legal notices and non-original commentary; date filters alone were insufficient.

## Selected evidence and matching pitfalls

These ten selected records demonstrate collection and question-linking rules. Nine are reviewed original announcements or filings; one is a law-firm notice whose underlying allegations remain unverified. They are not an exhaustive inventory or investment recommendations. 🧠 marks analytical interpretation. Links to saved questions in `events.json` mean context, not a resolved criterion.

### E01 — Ondas acquisitions and share registration

Published 2026-09-23. Ondas announced three defense-technology acquisitions. Its 8-K distinguishes acquisition-issued shares from registration for their resale.

🧠 Include the new consideration, contingent obligations and shares in the next cash/dilution bridge; separate acquired from organic activity. The complete quarterly liquidity and share bridges remain untested. A resale registration must not be counted as a second issuance.

[Source 1: Ondas](https://ir.ondas.com/press-releases/detail/329/ondas-acquires-three-defense-technology-businesses-to); [Source 2: SEC / Ondas](https://www.sec.gov/Archives/edgar/data/1646188/000121390026102458/ea0306273-8k_ondas.htm)

### E02 — SoFi stablecoin settlement launch

Published 2026-09-22. SoFi and Mastercard announced live stablecoin settlement and plans to migrate SoFi card settlement.

🧠 Track evidence of commercial adoption and revenue contribution in subsequent disclosures. Transaction volume is not revenue. This issuer claim does not establish the quarterly growth or Technology Platform result.

[Source 1: SoFi / Mastercard](https://investors.sofi.com/news/news-details/2026/SoFi-Becomes-First-National-Bank-to-Go-Live-with-Stablecoin-Settlement-across-Mastercards-Global-Payments-Network/default.aspx)

### E03 — Fed proposed stablecoin framework

Published 2026-09-24. The Federal Reserve requested comment on two proposals for Board-supervised payment stablecoin issuers.

🧠 Track sector policy and separately verify the relevant supervisor and legal entity before assigning a direct company effect. Proposals are not final rules. The release does not establish direct applicability to SoFi or Robinhood; SoFi Bank has a different primary supervisor.

[Source 1: Federal Reserve](https://www.federalreserve.gov/newsevents/pressreleases/bcreg20260924a.htm)

### E04 — New Era announces Vistra power agreement

Published 2026-09-21. New Era Energy & Digital announced a 20-year power agreement with Luminant, a Vistra subsidiary, with supply expected in Q3 2027.

🧠 Follow execution and contract economics as additional context for Vistra power demand. Counterparty announcement. Future supply is not current revenue; it does not answer the saved Meta/AWS delivery milestones.

[Source 1: New Era Energy & Digital via GlobeNewswire](https://www.globenewswire.com/news-release/2026/09/21/3365358/0/en/new-era-energy-digital-secures-20-year-207-mw-ppa-with-vistra.html)

### E05 — Vistra completes subordinated debt offering

Published 2026-09-24. Vistra disclosed completion of $1.5 billion of junior subordinated notes in two series on September 24.

🧠 Add the financing to the next debt/cash reconciliation and check its use and cost. The filing alone does not establish the complete financing criterion, acquisition funding or maturity coverage.

[Source 1: SEC / Vistra](https://www.sec.gov/Archives/edgar/data/1692819/000114036126037577/ef20082680_8k.htm)

### E06 — INRY ServiceNow deployment case study

Published 2026-09-23. INRY published a ServiceNow EmployeeWorks deployment case study, describing a March purchase and subsequent six-week implementation.

🧠 Useful qualitative adoption context; seek broader disclosure for subscription growth and contracted demand. Partner-reported benefits, not independently measured. Publication this week does not make the implementation a new September sale.

[Source 1: INRY via Business Wire](https://www.businesswire.com/news/home/20260923916632/en/INRY-deploys-ServiceNow-EmployeeWorks-in-six-weeks-replacing-its-legacy-portal-with-an-AI-front-door-to-work)

### E07 — Amazon registration refers to earlier financing

Published 2026-09-24. Amazon filed an 8-A debt registration referring to a September 9 prospectus and September 14 financing closing.

🧠 Link this document to the earlier financing event to avoid counting new funding twice. The September 24 filing date is not proof of new cash raised that day.

[Source 1: SEC / Amazon](https://www.sec.gov/Archives/edgar/data/1018724/000110465926110227/tm2625860d1_8a12b.htm)

### E08 — Kuehne+Nagel announces Amazon collaboration

Published 2026-09-21. Kuehne+Nagel announced an expanded long-term Amazon collaboration including logistics through the AWS infrastructure lifecycle.

🧠 Monitor infrastructure delivery and supply-chain capacity as context for AWS growth. Counterparty announcement does not quantify Amazon revenue, cash returns or the outcome of the saved quarterly criterion.

[Source 1: Kuehne+Nagel](https://newsroom.kuehne-nagel.com/kuehnenagel-announces-long-term-strategic-collaboration-with-amazon/)

### E09 — Google discusses planned orbital AI test

Published 2026-09-24. Google described a planned prototype satellite test for Project Suncatcher, a long-term research project.

🧠 Track as an emerging research topic; seek cost and commercial evidence before changing investment assumptions. The publication describes a planned test, not a completed launch or an established revenue stream. No implication for ASTS is established.

[Source 1: Google](https://blog.google/innovation-and-ai/models-and-research/google-research/google-project-suncatcher-facts/)

### E10 — AppLovin legal notice needs primary verification

Published 2026-09-24. A plaintiff law firm published a notice stating that a securities lawsuit had been filed.

🧠 Retrieve the complaint and court status before linking any substantiated issue to platform access or business assumptions. The court complaint was not reviewed. A law-firm advertisement is not a finding of misconduct; repeated notices should be deduplicated.

[Source 1: Bernstein Liebhard via GlobeNewswire](https://www.globenewswire.com/news-release/2026/09/24/3368436/0/en/shareholder-alert-bernstein-liebhard-llp-announces-a-securities-fraud-class-action-lawsuit-has-been-filed-against-applovin-corporation-app.html)

## Implications for the recurring design

1. Read the registry and archived questions fresh on every run. The preparer has no fixed company count and compares membership, report IDs and question versions with a previous manifest.
2. Keep evidence linked to the exact report and question version that prompted collection. A changed threshold cannot revise an old outcome silently.
3. Scan beyond existing questions. Google's research announcement and the Fed proposal illustrate topics that may deserve a new follow-up; adding that question requires an explicit report revision.
4. Track publication dates, underlying event dates, proposed versus completed actions, and issuer versus counterparty claims. Avoid turning publicity into reported financial results.
5. Preserve gaps. The 108-row question ledger deliberately says `not_adjudicated_collection_pilot`; it does not imply that every question was researched to a conclusion.

**Next gate:** validate issuer fallbacks and the complete macro/geopolitical source basket; implement recurring collection with coverage, retry and deduplication records; then trial a complete report before setting its schedule.

## Files

- [Design and change rules](../../../docs/market-sweep-design.md)
- [Immutable company/question manifest](manifest.json)
- [Company and question coverage ledger](coverage.json)
- [Selected evidence records](events.json)
- [SEC metadata discovery](sec-discovery.json)
- [Fed feed discovery](fed-discovery.json)
- [FRED sample response](fred-sample.json)
- [Source access results](source-access.json)

Historical source lists copied into the manifest belong to the original company reports. They are not a log of sources reread during this pilot. Selected web documents have a review date, not a byte-level archival copy; API response hashes exist where captured. Accordingly, this pilot is auditable by source links and recorded inputs but not a complete historical snapshot of the public web.

# classifier.dev trial on META

Date: September 19, 2026. Companion research: `META-2026-09-19-v3-r2` (same financial values and criteria as the original baseline; corrected source links and explicit component sums).

**Decision: keep experimental; do not integrate into the stock-analysis skill yet.** The service can suggest topic tags, but this trial did not demonstrate sufficient recall or time savings for routine evidence routing.

## Method

The report author selected 26 real excerpts from Meta's [Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1326801/000162828026050705/meta-20260630.htm). Six topic labels and all reference annotations were fixed before the first service call. The set includes short disclosures, multi-topic passages, audience-measurement context, an accounting-standard notice and a document heading. The reference annotations were made by the assistant, without independent human adjudication.

The test used the public [classifier.dev](https://classifier.dev/) WebMCP `classify_multi_label` method, with all six labels available and `max_labels=6`. The returned model was `jev-1.13.0`, fast tier; no escalation was reported. No private company data, user information or skill files were submitted. The companion JSON preserves the labels, source locators, input hashes, raw scores, predicted tags and discrepancies. Source excerpts are not republished.

## Observed results

| Measure | Result |
|---|---:|
| Passages | 26 |
| Reference topic assignments | 36 |
| Correct returned assignments | 24 |
| Extra assignments | 0 |
| Missed assignments | 12 |
| Exact label-set agreement | 15 / 26 (57.7%) |
| Micro precision | 100% |
| Micro recall | 66.7% |
| Measured complete tool-call time | 17.344 seconds |
| Service-reported processing time | 396 milliseconds |

These are descriptive results for one deliberately selected sample, not estimates of general financial-research accuracy. The service time and complete tool-call time measure different things. There was no timed manual or keyword baseline, so neither number proves a net saving in research time.

## Where it helped and where it failed

It recognized clear disclosures about ad demand, dividends, debt, cash and capital expenditure. None of its returned tags conflicted with the frozen reference labels.

It missed secondary relevance. Infrastructure leases, purchase commitments and restricted infrastructure cash were tagged as financing/liquidity but not capital spending. Share-compensation references in cost and operating-cash passages were not routed to ownership/dilution. A cost paragraph mentioning legal charges did not reach the legal topic. It also left headcount reductions and two audience-measurement passages without any tag.

Some secondary-topic judgments are debatable: a legal charge is not a complete litigation-risk disclosure, and share compensation does not establish realized dilution. Broad labels may contribute to the misses. Those qualifications strengthen the case for a held-out test with clearer inclusion rules; they do not justify changing the frozen reference labels after seeing results.

## Consequence for the META report and the skill

The report retained all relevant passages through direct source review. Classifier output did not decide numerical values, accounting definitions, source credibility, conclusions or watchlist outcomes. This is a new baseline report, so the test does not establish performance on an actual earnings follow-up.

Do not make the service a default dependency or a filter that can exclude evidence. A possible later integration is an optional suggestion layer that preserves every input, allows multiple topics, keeps untagged passages visible, records model/version and has a deterministic fallback. Before adopting it, test another company with independently reviewed labels and measure end-to-end effort against the existing workflow. Any label refinements or threshold changes learned from META should be evaluated on that held-out set, not presented as improved accuracy on this same sample.

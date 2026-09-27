# Free-source market and company sweep

Status: design and collection pilot, 27 September 2026. Dynamic scope preparation is implemented; recurring collection and report delivery are not scheduled yet.

## Scope comes from the project

At the start of every run, load the current committed `stock-analysis-registry.json`. Include every company entry, resolve it by issuer and security identity, verify its archive, and read the exact `latest_report_id`. Use that snapshot's `watchlist`, including its question IDs, criterion versions, thresholds, periods and baseline references. Never maintain a second manually edited ticker list.

`scripts/prepare_market_sweep.py` implements this step and produces an immutable run manifest. The first manifest includes 16 companies and 108 questions; these are observed counts, not limits. Each company also receives a general news search brief so an emerging issue can be discovered even when it is absent from the existing questions.

| Project change | Next sweep | Historical treatment |
| --- | --- | --- |
| Company added | Include it automatically; label it newly tracked and collect its initial source baseline | No invented comparison with runs where it was absent |
| Company removed from registry | Stop including it in subsequent active scope | Retain previous manifests, evidence and reports |
| Ticker/name changes, same security identity | Update search aliases and display metadata | Preserve continuity through the stable identity |
| Security identity changes | Treat as an addition/removal unless an explicit, reviewed migration links them | Never merge companies by similar names alone |
| Question added | Begin tracking its exact wording, period and criterion version | Label the first assessment as a baseline |
| Question wording, threshold, period or baseline changes | Record a change; compare versions before judging evidence | Preserve the old question and assessments; do not retroactively apply a new threshold |
| Question removed | Record that it left active scope; distinguish retirement from resolution | Retain outstanding historical assessments |
| Archive cannot be loaded | Keep a blocked company row and report the error | Do not interpret missing questions as retirement |

The loader detects changed question content even when its criterion version was not incremented. Such changes need review before comparing outcomes. Detection does not itself assign a new version or rewrite the source report. It can compare a run against its predecessor using `--previous`.

## Free data collection

No paid data subscriptions are required. Execution, storage and model usage are separate from data licensing and may have costs. Public access does not grant unlimited redistribution of article text; store URLs, necessary excerpts or paraphrases, and permitted source data.

| Layer | Candidate sources and collection method | Role and current validation |
| --- | --- | --- |
| Company disclosures | [SEC submissions JSON](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), issuer investor relations releases, earnings presentations | Primary facts. SEC recent-submissions metadata worked for all 16 pilot companies. Issuer indexes varied; individual releases sometimes worked when the index did not. |
| Company ecosystem | Customer, supplier and partner releases; regulator and court records | Identify developments omitted from the issuer's own news feed. Verify the relationship and distinguish counterparty claims from independent confirmation. |
| Broad news discovery | [GDELT](https://www.gdeltproject.org/), public publisher feeds and web search | Discover leads, then read the underlying article. The pilot GDELT request received HTTP 429; this is an unresolved reliability issue, not a working collection dependency. |
| US macro | [FRED](https://fred.stlouisfed.org/), [BLS releases](https://www.bls.gov/bls/news-release/), [BEA releases](https://www.bea.gov/news), [Federal Reserve RSS](https://www.federalreserve.gov/feeds/feeds.htm) | Observation data, release calendars and policy statements. Fed RSS and one FRED public CSV series were tested; the full macro basket remains to be validated. |
| International macro | [ECB data portal](https://data.ecb.europa.eu/), [Eurostat](https://ec.europa.eu/eurostat), [World Bank data](https://data.worldbank.org/) | Add according to documented revenue, funding and supply-chain exposures. Candidate sources, not completed pilot integrations. |
| Geopolitics and policy | [US Treasury](https://home.treasury.gov/news/press-releases), [OFAC](https://ofac.treasury.gov/), [BIS](https://www.bis.gov/), [European Commission](https://ec.europa.eu/commission/presscorner/home/en), relevant national agencies and public original reporting | Sanctions, trade restrictions, tariffs, energy policy, conflict and shipping disruptions. Official notices establish policy; independent reporting provides context. A full geopolitical sweep was not completed in this collection pilot. |

Prefer documented APIs and feeds. Respect provider access policies, cache shared requests, identify the client where required, and use rate-limited queues. A free key, if a future source requires one, belongs in private configuration. Do not depend on paywall workarounds or a proprietary news API's temporary free trial.

## Collection and evidence rules

1. Freeze a timezone-aware window, cutoff, repository revision and question snapshot. Fetch shared macro/policy feeds once, then route relevant evidence to companies.
2. Discover direct company news, each question's subject and new risks. Use names, aliases and source-backed counterparties, not bare ticker matches alone. Maintain an exposure map with evidence for geography, customers, suppliers, energy, financing and regulation; do not manufacture those relationships from generic sector labels.
3. Read original sources. Keep publication time, event time, retrieval time and the period described separately. A newly published article about an old deal is not a new deal. A proposed rule is not an enacted rule; a financing registration is not necessarily a new financing.
4. Deduplicate articles into events using canonical URL, accession number, parties and event date. Keep multiple independent confirmations, but count syndicated copies and repeated legal advertisements as one lead.
5. Attach evidence to the company identity, source report ID, question ID and criterion version. Keep unrelated but potentially important developments in a new-issue queue for human review.
6. Evaluate only compatible evidence against a question. Product launches and contracts can inform the next review without answering a quarterly revenue, cash or margin test. Conflicting evidence remains visible. No collector may silently rewrite questions or clear earnings flags.

Separate three layers in the report: **source fact → possible economic mechanism → company implication**. Label analytical implications as inferences, with confidence and alternatives. For example, a rise in yields may affect financing costs; a company's actual exposure requires its debt structure and maturity evidence. Do not infer a share-price forecast from the headline alone.

Each evidence record should retain source URL, publisher, document locator, publication/event dates, retrieval timestamp or date precision, available response hash, evidence type, concise claim, review status, linked questions and limitations. Historical report sources in the manifest are baseline references, not proof they were reread in the current sweep.

## Coverage and scaling

Report three separate denominators: companies included, sources successfully checked, and questions with sufficient new evidence. Including 108 questions does not mean 108 answers were found. Never replace a failed request with “nothing happened.” Use explicit states: checked with relevant evidence, checked with none found, partial, unavailable, and not assessed.

As the universe grows, retain one coverage row per company and one assessment row per active question. Batch shared feeds, cache documents by URL/hash, queue issuer-specific work, and divide date ranges or page through results when a provider truncates responses. No silent top-N company or headline cap. If a time budget is exhausted, publish an incomplete coverage section and resume pending work.

For a future recurring collector, keep per-source watermarks only after successful retrieval. Use an overlap window (initially 48 hours), deduplicate, and backfill after outages. Rate limits require bounded backoff and later retry; missing pages remain a visible gap. Content hashes detect revisions, but preserve the earlier evidence used by an already published report.

Each completed run should produce:

- A market landscape section: macro releases, policy/geopolitical developments, mechanisms and uncertainty.
- A company section for every active company, including quiet companies and coverage gaps.
- A question ledger: evidence changes, unresolved questions and proposed new follow-ups.
- An audit appendix: exact scope, dates, source failures, unresolved leads and changes since the prior run.

## Implemented preparation step

From the repository root:

```sh
python3 scripts/prepare_market_sweep.py \
  --start 2026-09-21T00:00:00+03:00 \
  --cutoff 2026-09-27T22:44:06+03:00 \
  --run-id MARKET-PILOT-2026-09-27 \
  --out research/market-sweeps/2026-09-27/manifest.json
```

Use new timestamps, run ID and output path for subsequent runs. Add `--previous path/to/prior/manifest.json` to obtain the scope diff. Output creation is exclusive: an existing manifest is not overwritten. Exit status 2 means partial scope; retain the file and resolve the blocked entries before claiming full preparation.

The loader records the repository commit, registry hash, report hashes and whether registry/archive inputs have local modifications. Production runs should begin from a clean, pinned revision. Running against today's questions for a past week is retrospective research, not a point-in-time backtest. The pilot marks reports whose research cutoff falls inside the collection window. A true backtest must use the registry and reports available at its historical cutoff; the loader rejects research newer than the sweep cutoff.

The loader currently prepares scope and search briefs only. Network collection, question adjudication, report rendering and scheduling remain separate work. The next implementation gate is to validate the macro/geopolitical source basket and issuer fallbacks, then build a collector that preserves these coverage guarantees. Frequency and delivery can be chosen after that trial.

See the [first pilot](../research/market-sweeps/2026-09-27/pilot.md).

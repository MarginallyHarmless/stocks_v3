# Free-source market and company sweep

Status: on-demand workflow implemented, 27 September 2026. The user triggers each run. There is no recurring schedule, background monitoring or automatic delivery. The first completed landscape covers all 16 current companies and 108 saved questions, with explicit source gaps.

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
| US macro | [FRED](https://fred.stlouisfed.org/), [BLS releases](https://www.bls.gov/bls/news-release/), [BEA releases](https://www.bea.gov/news), [Federal Reserve RSS](https://www.federalreserve.gov/feeds/feeds.htm) | Observation data, release calendars and policy statements. Fed RSS, BLS/BEA releases and calendars, and three government-origin FRED CSV series were verified in the first landscape. |
| International macro | [ECB data portal](https://data.ecb.europa.eu/), [Eurostat](https://ec.europa.eu/eurostat), [World Bank data](https://data.worldbank.org/) | Add according to documented revenue, funding and supply-chain exposures. ECB RSS and the latest policy release were verified. Eurostat and World Bank remain optional sources, not implemented integrations. |
| Geopolitics and policy | [US Treasury](https://home.treasury.gov/news/press-releases), [OFAC](https://ofac.treasury.gov/), [BIS](https://www.bis.gov/), [European Commission](https://ec.europa.eu/commission/presscorner/home/en), relevant national agencies and public original reporting | Sanctions, trade restrictions, tariffs, energy policy, conflict and shipping disruptions. Official notices establish policy; independent reporting provides context. The first landscape verifies EIA energy/shipping context, EU sanctions and a Treasury release. BIS discovery remains partial; this is not comprehensive worldwide conflict coverage. |

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

For each manually initiated run, retain successful source checkpoints. Use a 48-hour overlap with the previous completed landscape, deduplicate, and backfill after outages. Rate limits require bounded backoff and later retry; missing pages remain a visible gap. Content hashes detect revisions, but preserve the earlier evidence used by an already published report.

Each completed run should produce:

- A market landscape section: macro releases, policy/geopolitical developments, mechanisms and uncertainty.
- A company section for every active company, including quiet companies and coverage gaps.
- A question ledger: evidence changes, unresolved questions and proposed new follow-ups.
- An audit appendix: exact scope, dates, source failures, unresolved leads and changes since the prior run.

## Run on request

A request such as **“Run the market sweep”** initiates the workflow. Fetch the latest main branch and start from a clean, pinned revision. Read this document and both registries; do not reuse a fixed company list from an earlier prompt.

From the repository root, choose a new run directory:

```sh
python3 scripts/start_market_sweep.py \
  --out research/market-sweeps/YYYY-MM-DD-r1

python3 scripts/collect_market_sources.py \
  --manifest research/market-sweeps/YYYY-MM-DD-r1/manifest.json \
  --out research/market-sweeps/YYYY-MM-DD-r1/collection.json
```

Replace the example date with the actual run date and increment the suffix if needed. The starter defaults to now in Europe/Bucharest and the previous completed landscape cutoff minus 48 hours. With no previous landscape it uses seven days. Optional `--start` and `--cutoff` accept timezone-aware ISO timestamps. An irregular gap of several weeks remains several weeks of research; it is never silently shortened to the last seven days. Split long date ranges, paginate historical submissions and search past releases where current RSS feeds are too short. Deduplicate overlapping evidence by accession, canonical URL and event identity. New material about an earlier event is labelled as a correction or late discovery.

The starter compares against the previous completed manifest and captures all additions, removals, revised questions and source-report changes. Exit status 2 means blocked scope: retain the manifest, explain the errors and resolve them before claiming full coverage. Newly tracked companies receive a baseline from their current archive and an explicit source backfill where needed; do not invent a previous assessment. The earlier pilot is retained as research history, not used as the completed-landscape watermark.

The collector performs bounded, rate-limited discovery once: SEC submissions metadata (including overlapping historical pages), Fed/ECB feeds and three FRED series. Metadata is not a read filing. Collectors preserve failures and refuse to overwrite earlier attempts. Read originals for every selected claim, and separately search each company's general news and question subjects. Useful issuer fallbacks verified in this run include Intuitive's regional newsroom, Constellation's corporate releases, regulator originals for Meta and free original reporting for Palantir. ASTS issuer-feed and BIS discovery gaps remain visible.

Public access and redistribution are separate. The public payload currently includes government-origin Treasury yield (`DGS10`), Brent spot (`DCOILBRENTEU`) and dollars per euro (`DEXUSEU`) data. FRED's S&P 500 and Nasdaq series state that reproduction requires prior approval; their histories are excluded from the public report. Check each added series' source notes before embedding data. Do not publish full news articles.

## Author, validate and publish

Write for a first-time investor. For each selected news item, aim for roughly 100–170 words across the factual summary, a plain-language explanation, the company implication and the next observable check. Use judgment rather than padding to a word count. Explain unfamiliar terms where they appear: for example, what settlement does, how issuing shares differs from resale, or why a court finding is separate from a penalty. Say who announced the development, which step has actually happened and what remains conditional. Retain material uncertainty in the visible text. Avoid procedural shorthand such as “funding bridge” without explaining the cash available, money needed and repayment commitments it refers to.

For new research ledgers, set `news_reading_standard` to `beginner-news-1`. Author bilingual `context`, `meaning` and `watch` on every event and theme, alongside the factual summary. Add `market_pulse_guide` with bilingual `paragraphs` and existing `source_ids`; these explanations are included in the standalone HTML.

Give macro themes and market indicators comparable teaching depth. Explain the route from the event to borrowing costs, customer spending, company cash or valuation. A conditional mechanism is not a stock-price prediction. Keep essential explanations visible; saved-question criteria and source detail may remain expandable. Author natural English and Romanian. Do not add unsupported company details to make an explanation sound fuller.

After collecting, read sources and author `report.json` beside the manifest, using the first completed report's schema as the reference. This is a research step, not an unattended summary generator. It must include:

- A bilingual market overview and themes, separating pre-window starting conditions from new developments, with dated observations and cited mechanisms.
- Selected event records with source facts, analytical interpretation, limitations and question links. Keep company-announced aspirations, proposals, litigation allegations and completed actions distinct.
- Every current company and its exact frozen questions/criteria, including companies with no selected event. Use `context_added`, `unverified_lead` or `no_decisive_new_evidence`; keep `criterion_outcome` null. A landscape is not an earnings adjudication.
- A coverage section explaining what was checked, failures, unresolved leads, changed scope and proposed new questions. Proposals never automatically edit the company watchlists. Compare events with both the previous landscape and the company's latest research cutoff; an old event is not new merely because it was selected again.
- The source ledger, available response hashes/retrieval dates, permitted market series with actual observation dates and future release checks. Sources inside frozen company archives are baseline references, not automatically reread evidence.

Append a record to `market-sweep-registry.json` with the new run ID, dates, repository-relative report/data/manifest paths, counts and SHA-256 hashes of the exact data and manifest bytes. Set `latest_run_id` to the new completed report. Never remove prior entries or overwrite earlier research snapshots. Then run:

```sh
python3 scripts/render_market_sweep.py --all
python3 scripts/build_index.py
python3 -m unittest discover -s scripts/tests
```

The renderer rejects missing companies, changed questions or criteria, changed manifest/data hashes, unresolved source references, future observations and attempts to grade earnings outcomes. Inspect the report in English/Romanian and at desktop/mobile sizes. Run the repository's remaining AGENTS.md validation gates, commit all related changes together, push without force, inspect the exact commit's Actions deployment and check the live index and report URLs.

For an explanation-only revision, preserve the original `report.json`, manifest, cutoff, findings and question criteria. Save a new `reading-guide-rN.json` with the existing run ID, cutoff and base-data hash; author a context/meaning/watch explanation for every selected event and macro theme, plus an indicator guide. All source references must come from the corresponding original items. Register its hash and a new HTML filename under the run’s `presentation_revisions`, retaining `original_html_path` and pointing the run’s `html_path` to the latest edition. The renderer checks the guide against the original scope, embeds both in a standalone HTML export and links the earlier edition to the expanded one. This does not create a new research run or advance the collection watermark. A true factual update needs a new dated run.

The index’s Reports section lists every completed landscape, newest first, with its coverage window and company/question counts. Adding a completed run to the registry automatically adds its card when the index is rebuilt. Each report provides a reusable next-run prompt. The user may also say “Run the market sweep”; project instructions carry the dynamic scope and free-source requirements.

## Time and interpretation limits

The loader records the repository revision, registry hash, report hashes and local input changes. Current saved questions applied to a historical window are retrospective research, not a point-in-time backtest. Reports whose company research cutoff falls inside the window are labelled accordingly. A true backtest must use the registry and reports available at its historical cutoff; the loader rejects company research newer than the sweep cutoff. Market observations are retrieved vintages and can later be revised.

Full company/question inclusion is a scope guarantee, not a claim that every published article or every geopolitical issue has been reviewed. Preserve the three denominators: scope included, sources checked, and questions with decisive evidence. No result may clear an earnings-review flag unless a separate, matching earnings review is saved through the existing process.

See the [first completed landscape](../reports/market-landscape-2026-09-27-r2.html), its [evidence ledger](../research/market-sweeps/2026-09-27-r1/report.json), and the earlier [collection pilot](../research/market-sweeps/2026-09-27/pilot.md).

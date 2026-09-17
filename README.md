# Stock research

Company research, saved earnings watchlists and a shared earnings calendar.

- **Index:** [`index.html`](index.html), with company cards, logos, countdowns and review states.
- **AVGO report:** [`reports/AVGO-stock-analysis-v3-2026-09-16.html`](reports/AVGO-stock-analysis-v3-2026-09-16.html).
- **Registry:** [`stock-analysis-registry.json`](stock-analysis-registry.json).
- **Research archives:** [`archives/`](archives/), preserving immutable evidence and watchlist snapshots.
- **Research workflow and generator:** [`skills/stock-analysis/`](skills/stock-analysis/SKILL.md).

## Read locally

Download the repository and open `index.html` in a browser. Reports also work as standalone HTML files. English/Romanian and light/dark controls are included.

## Publish with GitHub Pages

In this repository's Settings → Pages, choose **Deploy from a branch**, **main**, **/(root)**, then Save. The expected address is https://marginallyharmless.github.io/stocks_v3/ once deployment completes. GitHub Pages publishes the committed static files; no package install or build service is needed.

## Add or update research

Read [`AGENTS.md`](AGENTS.md) and the Stock Analysis skill first. Fetch the current registry and archive before making changes. Save new reports under `reports/`, preserve earlier reports and immutable snapshots, then update the registry and regenerate the index:

```sh
python3 scripts/build_index.py
```

Commit the report, archive, registry and index together. All future reports belong in this repository. Do not publish research on ChatGPT Sites.

## Earnings states

Countdowns update while the index is open. Research and scheduled dates change only when a research update is committed. An overdue estimated date asks for a publication check; it does not claim that results are published. A confirmed release or verified publication stays flagged until a saved review covers that reporting period. Editorial changes do not clear the flag.

AVGO's next results date is currently an **estimate**, with its source and last check recorded in the index. The report retains its original 16 September 2026 research cutoff.

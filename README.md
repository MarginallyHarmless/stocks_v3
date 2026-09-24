# Stock research

Company research, saved earnings watchlists and a shared earnings calendar.

- **Index:** [`index.html`](index.html), with company cards, logos, countdowns and review states.
- **Reports:** [`reports/`](reports/), one standalone HTML file per saved analysis. Earlier reports are kept; a replaced report links to its successor.
- **Chart data:** [`research/visuals/`](research/visuals/), dated supplements selected per report by `manifest.json`.
- **Registry:** [`stock-analysis-registry.json`](stock-analysis-registry.json).
- **Research archives:** [`archives/`](archives/), preserving immutable evidence and watchlist snapshots.
- **Research workflow and generator:** [`skills/stock-analysis/`](skills/stock-analysis/SKILL.md).

## Read locally

Download the repository and open `index.html` in a browser. Reports also work as standalone HTML files. English/Romanian and light/dark controls are included.

## Publish with GitHub Pages

The [deployment workflow](.github/workflows/pages.yml) tests the research tools, verifies saved archives, rebuilds the index and publishes the website after every push to `main`. Pull requests run validation without publishing. Deployments use GitHub's built-in credentials; no personal access token or hosting secrets are needed.

**One-time setup:** Open [Settings → Pages](https://github.com/MarginallyHarmless/stocks_v3/settings/pages). Under **Build and deployment → Source**, select **GitHub Actions**. Keep whichever GitHub integration your assistant uses (or plain Git credentials) able to push to this repository.

Then open [Actions](https://github.com/MarginallyHarmless/stocks_v3/actions/workflows/pages.yml). If the first run failed because Pages was not enabled, choose **Re-run failed jobs**, or use **Run workflow** on `main` to start a fresh deployment. Subsequent pushes publish automatically.

The site address after a successful deployment is [marginallyharmless.github.io/stocks_v3](https://marginallyharmless.github.io/stocks_v3/). Check the workflow result and live page before treating an update as published. Files deployed are the index, registry, reports, archives and optional `assets/` directory.

## Add or update research

Read [`AGENTS.md`](AGENTS.md) and the Stock Analysis skill first. Fetch the current registry and archive before making changes. Save new reports under `reports/`, preserve earlier reports and immutable snapshots, then update the registry and regenerate the index:

```sh
python3 scripts/build_index.py
```

Commit the report, archive, registry and index together. All future reports belong in this repository. Do not publish research on ChatGPT Sites.

## Earnings states

Countdowns update while the index is open. Research and scheduled dates change only when a research update is committed. An overdue estimated date asks for a publication check; it does not claim that results are published. A confirmed release or verified publication stays flagged until a saved review covers that reporting period. Editorial changes do not clear the flag.

Each company's next results date shows whether it is confirmed or estimated, with its source and last check recorded in the index. Reports keep their original research cutoff.

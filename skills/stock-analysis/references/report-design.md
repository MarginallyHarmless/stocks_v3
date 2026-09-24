# Report design

Use the bundled renderer/CSS/JS. Keep a single main reading column with compact section navigation. Defaults: warm-neutral near-black background, restrained borders, legible 17–18px body text, aligned tabular numbers, subdued green and amber with text labels. Light theme is available independently of language/reading level. Do not fill the screen with equal-weight score cards.

## Information hierarchy

1. First screen: company/security identity, information cutoff, clear answer, strongest supporting/opposing evidence, separate business and price assessments, important missing evidence, next reporting date/confidence.
2. Main sections: question → concept in everyday language → company answer → zero to three decisive typed figures, each with its meaning → “Why it matters” → material caveat. Use five main questions plus the closing watchlist by default; keep the complete checklist in the underlying research.
3. “Explain this”: short concept, hypothetical worked example, common trap. “Sources & calculation”: underlying evidence, direct document link, definition, period, source locator and calculation input chain. Keep these distinct.
4. Closing section: prioritized next questions, why each matters, exact target and due period, date confidence/source, favorable/adverse implications. Original baselines, criterion versions, rationale and mixed/unresolved implications remain in expandable context. Copyable update prompt and portable export follow. The source appendix is reached through the evidence dialog, not a long mandatory scroll after the watchlist.

## Default six-part reading path

| Part | Beginner's question | Detailed research belongs here |
|---|---|---|
| 1 | What would I own? | Products, customers, revenue mix, competitors, competitive advantage |
| 2 | Why might this business grow? | Demand, quarterly momentum, historical growth, guidance and its uncertainty |
| 3 | Do sales leave useful cash? | Profit versus cash, cash investment, cash conversion, cash per share, dividends/buybacks |
| 4 | What could go wrong? | Debt, financing, customer concentration, dilution, management, industry/market risks |
| 5 | Is the share price reasonable? | Dated price, historical/adjusted/forecast earnings, peers, scenarios, benchmark context |
| 6 | What do I check when results arrive? | Saved questions and original criteria, generated from the watchlist |

Adapt the question to the evidence, including weak companies and missing data. Do not turn “why might it grow” into an unsupported growth claim. The five analytical sections plus generated watchlist are the default for a full report; focused/update reports need only the relevant questions. The closing watchlist is generated automatically: do not duplicate it in `sections`.

For every main section author a `guide` (data-contract.md). Use short sentences and ordinary words; explain a concept before asking the reader to interpret its figure. One paragraph should make one point. A metric caption must explain the actual figure, not repeat its label. Prefer “cash left after the defined business investments” before introducing FCF. Avoid unexplained GAAP, TTM, EPS, SBC and P/E in the main prose. Preserve exact periods and basis alongside figures, but explain their significance in words. Label all invented teaching examples as hypothetical.

The essential conclusion, adverse evidence, material assumptions, forecast labels and gaps stay visible in both modes. Detailed mode opens the full analysis; Guided closes it. Optional lessons stay available in either mode. “Explain all” opens lessons and returns to Guided. Language, theme and reading preferences are independent. Never require opening a lesson to understand the main conclusion. Source buttons say “Sources”, with internal identifiers confined to the evidence view and exports.

## Charts

Use [visual-reporting.md](visual-reporting.md) for the ten-panel financial dashboard. Its charts remain visible in Guided mode. Use two columns with consistent titles, visible values and short explanations; reflow to one column on phones.

Only plot comparable values already present in the ledger. Label value, period, unit and basis, with a data table and source references. Use a chart when it adds a trend/relationship; omit it for a single number or unsupported history. Revenue alone is not proof of demand quality. Use a reconciled cash-flow diagram only when components genuinely reconcile and improve comprehension; this release does not advertise the old disconnected flow-diagram feature.

## UI checks

Check desktop, 768px and narrow 320/390px widths. Watch for clipping, page-wide horizontal overflow, overly tiny chart text, translated labels, oversized numbers, and long IDs/URLs. Dense update tables reflow into labeled rows on phones. Verify keyboard focus, touch controls, dialog Escape/close, nested calculation links, independent language/reading preferences, copy fallback and JSON download. Use only offline bundled assets; no analytics or external JS dependencies.

Interpretive claims remain authored text. Check their numbers against typed metrics; the number formatter prevents metric-display drift but cannot fact-check free prose.

## Key stats and inline definitions

Add a compact `key_stats` list near the top: dated share price, market capitalization, reported annual/TTM EPS and matching P/E, then a few relevant sales, margin or cash figures. Each row references the typed ledger and uses a concept from `assets/financial-terms.json` (plus `price` and `revenue`). Include adjusted or forward multiples only with explicit basis and period. Explain distorted, unavailable or nonmeaningful P/E instead of displaying a negative multiple as a bargain. Do not substitute quarterly EPS into annual P/E. Context and limitations remain visible.

The renderer annotates financial terms with a dotted underline and a short EN/RO definition on hover, focus or tap. Definitions supplement the main explanation; they do not replace the concept → company evidence → implication sequence. Add new reusable terms and aliases to `assets/financial-terms.json`; avoid ambiguous short aliases. Links, controls, code, source IDs and exported research are not rewritten.

For editorial regeneration use `python3 scripts/render_reports.py` from the repository root, then `python3 scripts/build_index.py`. The repository's `research/key-stats.json` selects existing evidence for older immutable report IDs; new research should author `key_stats` directly. Never use this presentation mapping to alter an archived value or analysis date.

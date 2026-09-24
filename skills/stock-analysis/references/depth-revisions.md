# Depth revisions

A depth revision makes a saved report teach more without changing what it found. It adds plain-language explanations and concept lessons that interpret evidence already in the report. It is an editorial revision: a new report ID (`…-r2`, `…-r3`), the same cutoff, sources, reported figures, conclusions and watch criteria, and a bilingual revision note. The earlier report stays archived and links to its successor. The worked example is `research/depth/HOOD-2026-09-18-v3-r2.spec.json` in the research repository; match its depth, tone and Romanian.

Use it when a report's sections add little beyond the short answer or lack lessons. It is not a refresh: new facts, prices or filings need new research with a new cutoff.

## What to add

In Guided reading each section shows the short answer, figure cards and "Why it matters", then "What else to understand" (the section `claims`, minus text that repeats the guide), the caveat, and the "Learn the concept" card (the section `lesson`).

- Aim for at least three non-duplicate claims per section in total. Add something the short answer does not say: a distinction beginners confuse, what a figure does not mean, how two figures relate, a condition that must hold, why a number looks the way it does. Skip a point rather than stretch the evidence.
- Add a lesson to every section without one: a one- or two-sentence concept; an `example` starting "Hypothetical:" / "Exemplu ipotetic:" with invented round numbers whose arithmetic is checked; one common `trap`. No two lessons in a report teach the same concept. Existing lessons are never replaced.

## Accuracy rules

1. No new facts. Company statements must follow from ledger evidence, cited in `evidence_refs`. Do not add knowledge about the company from memory. General, hedged finance knowledge is fine.
2. Every number in claim text comes from the cited evidence, correctly rounded, with its period and basis. A needed ratio, growth rate or difference becomes a new `calculation` entry built from existing inputs; the tool recomputes it and you quote the printed value. If validation refuses a calculation, the comparison is not like-for-like: describe it qualitatively or drop it.
3. Claim types: `interpretation`, `model` (scenarios, assumptions, model values) or `limitation`; never `fact`. Label estimates and forecasts. Scenario values are not targets.
4. Do not contradict or soften existing conclusions, assessments, caveats or watch criteria, and do not repeat existing text.
5. Short sentences, ordinary words, one point per claim, jargon defined in the sentence. Romanian is natural, with ș/ț/ă/â/î, "776 mil. USD", "2,38 mld. USD", "16,9%", "T2 2026", and says exactly what the English says.

## Procedure (from the repository root)

```sh
python3 scripts/depth/dump_report.py BASE_ID > /tmp/BASE.txt          # sections + full evidence ledger
# write research/depth/NEW_ID.spec.json  (format: see the HOOD spec)
python3 scripts/depth/build_revision.py research/depth/NEW_ID.spec.json /tmp/rev
python3 scripts/depth/check_numbers.py research/depth/NEW_ID.spec.json /tmp/rev/NEW_ID.json
python3 scripts/depth/review_sheet.py research/depth/NEW_ID.spec.json /tmp/rev/NEW_ID.json
python3 scripts/depth/save_revision.py /tmp/rev/NEW_ID.json
python3 scripts/render_reports.py && python3 scripts/build_index.py
```

`build_revision.py` refuses anything outside these rules: non-calculation evidence, changed existing text or evidence, replaced lessons, uncited or unknown evidence, missing translations, unlabeled examples. It then runs the project's recompute and validation. `check_numbers.py` lists every number in the new text that does not match the cited evidence; resolve each (dates, years and phrases such as "12 months" are expected). Read the review sheet line by line against the evidence before saving. `save_revision.py` registers the snapshot, catalogs the registry and card, and maps the chart data and key stats to the new ID.

Then verify the archive, run the full test suite, inspect the new page in both languages, and commit the spec, archive, reports, registry, manifest and index together, following `AGENTS.md`.

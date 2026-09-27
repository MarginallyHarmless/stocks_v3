# Validation of MARKET-2026-09-27-r1

- Frozen scope: 16 companies, 108 exact saved questions; data and manifest hashes match the run registry.
- Research guards: 11 tests passed, including changed criteria, omitted companies, future observations, invalid source references, irregular run gaps and SEC timestamp boundaries.
- Existing research suite: 105 Python tests and the four JavaScript control suites passed. Regenerating the existing company reports produced no changes.
- Standalone report JavaScript parsed successfully. A local DOM check verified English/Romanian rendering, all 16 company sections and 108 questions, 31 sources, five themes, three market series, company search, date filter, source expansion, theme switching and prompt copying.
- Visual browser QA remains outstanding: the local browser executable was incomplete, and both browser/headless-shell downloads returned truncated archives. DOM checks do not establish pixel layout or mobile viewport behavior.
- Source coverage is selective and explicitly bounded in the report. ASTS issuer-feed access and BIS export-control discovery remain gaps. Discovery metadata does not imply every filing was read.
- Existing company watchlists, archives, registry and earnings-review flags were not modified.

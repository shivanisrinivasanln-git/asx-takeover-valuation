# TODO

My task list. Every task is about two hours of work or less, has acceptance criteria and a check that proves it, and names what it depends on. I tick a task only with one line of evidence (the command and its result, or a screenshot path). The plan behind it is in [docs/ROADMAP.md](docs/ROADMAP.md).

Tags:
- [ME] judgement, learning or writing that I do myself, because I must be able to explain it.
- [AUTO] scaffolding, code and automation that I run through scripts and tools and then read and test.
- [MIXED] work where I decide and automation does the repetitive part.

The full check command is defined in P0-04. Until it exists, a check means the command named in the row.

## Research and planning (done)

| Done | ID | Tag | Task | Evidence |
|---|---|---|---|---|
| [x] | R-01 | [ME] | Research how Australian expert reports work | docs/RESEARCH.md sections 1 to 5, commit 370b7c7 |
| [x] | R-02 | [ME] | Shortlist ten deals and choose Domain | docs/DEAL_SHORTLIST.md, commit f268f88 |
| [x] | R-03 | [ME] | Source the data for Domain | docs/RESEARCH.md section 6, commit 195999f |
| [x] | R-04 | [ME] | Choose the architecture | docs/ARCHITECTURE.md, commit 9e78cef |
| [x] | R-05 | [ME] | Research design and choose a visual direction | docs/DESIGN_RESEARCH.md, commits 2f5cdbf and f06c414 |
| [x] | R-06 | [ME] | Approve this roadmap and task list | Approved 4 October 2026, recorded in docs/DECISIONS.md |

## Phase 0: setup

| Done | ID | Tag | Task | Acceptance | Check | Needs |
|---|---|---|---|---|---|---|
| [x] | P0-01 | [AUTO] | Python project skeleton | `pyproject.toml`, source and test folders, pinned dependencies with a lockfile, `.gitignore` covers `research/raw/`, build output and caches | A clean virtual environment installs from the lockfile and imports the package. Evidence: a fresh virtual environment built only from `requirements.lock` (hash-pinned) passes `python scripts/check.py`, 4 October 2026 | R-06 |
| [x] | P0-02 | [AUTO] | Formatting, lint and type checks | Formatter, linter and type checker configured with strict settings and no ignored errors | Each command exits 0 on the skeleton and non-zero on a planted error. Evidence: planted unused import, type error and bad formatting each made `python scripts/check.py` exit 1 at lint, types and format | P0-01 |
| [x] | P0-03 | [AUTO] | Test runner and the Harbour Industrial fixture | The worked example in docs/RESEARCH.md is a unit test with the hand-worked answer | The test passes, and fails when I change the expected value. Evidence: `tests/engine/test_harbour_industrial.py` passes, and changing an expected value to 3.26 made it fail | P0-01 |
| [x] | P0-04 | [AUTO] | One full-check command | One command runs format check, lint, types, tests and, once a build exists (added with P5-03), the build step, and prints one summary line | It exits 0 on a clean tree and non-zero if any step fails. Evidence: `python scripts/check.py` prints `check: PASS (4 steps: format, lint, types, tests)` and `check: FAIL at <step>` with exit 1 otherwise | P0-02, P0-03 |
| [x] | P0-05 | [AUTO] | CI workflow for the product checks | Runs the full check on every push and pull request, with read-only permissions and actions pinned to commit hashes | A push shows a green run, and a planted failure turns it red. Evidence: the GitHub Actions run on commit 0429b44 was green, which I read on 5 October 2026. The failing path is the same `python scripts/check.py` that I made fail locally at each step, so I did not push a red commit | P0-04 |
| [x] | P0-06 | [AUTO] | Dependency audit in CI | The audit step fails on a known vulnerable pin | I pin a vulnerable version on a branch and the step fails. Evidence: the audit step passed in that green run, and run locally on a file pinning `jinja2==2.10` it exited 1 with three advisories, so I did not push a vulnerable pin to a branch | P0-05 |
| [x] | P0-07 | [ME] | Choose a licence and write the README skeleton | A licence file, the disclaimer text and the README headings from docs/ROADMAP.md | I can say in one sentence why I chose the licence. Evidence: `LICENSE` (MIT) and `README.md` with the disclaimer and the headings added on 5 October 2026, and the reason for the licence is in docs/DECISIONS.md | P0-01 |
| [ ] | P0-08 | [ME] | Excel practice: a one-sheet DCF by hand | A small DCF with a sensitivity table built with a data table, with a note of what each formula does | I can rebuild the sensitivity table from a blank sheet | none |

## Phase 1: deal review

| Done | ID | Tag | Task | Acceptance | Check | Needs |
|---|---|---|---|---|---|---|
| [ ] | P1-01 | [ME] | Read the report introduction, methods and valuation summary | Notes in my words on which methods Grant Samuel used and how it reached A$4.06 to A$4.46 (booklet pp. 116 to 135) | I explain the conclusion aloud in 2 minutes | R-06 |
| [ ] | P1-02 | [ME] | Read the DCF section | A table of each DCF assumption, its value and its page (booklet pp. 136 to 148) | Every row has a page number, and I can explain scenario A | P1-01 |
| [ ] | P1-03 | [ME] | Summarise the expert's DCF assumptions in my own words | A one-page summary in docs/EXPERT_NOTES.md covering growth, margins, capex, tax, terminal value | I read it aloud without looking at the booklet | P1-02 |
| [ ] | P1-04 | [ME] | Read the discount rate section | The WACC build and the beta evidence explained in my words (booklet pp. 139 to 140) | I explain why a beta of 1.0 to 1.1 was chosen despite the evidence range | P1-02 |
| [ ] | P1-05 | [ME] | Read the comparables and precedents sections | A list of each peer and transaction, why it was kept or excluded, with pages (booklet pp. 145 to 153) | I explain the exclusion of Zillow and CoStar | P1-01 |
| [ ] | P1-06 | [ME] | Read the control premium and fairness analysis | Notes on the premium evidence and why A$4.43 sits near the top of the range (booklet pp. 157 to 160) | I explain the control premium with a worked example | P1-01 |
| [ ] | P1-07 | [MIXED] | Build the deal timeline | Each event from the first approach to implementation has a date and a link to an ASX document | Every link opens, and each date matches its document | P1-01 |
| [ ] | P1-08 | [ME] | Interview prep: DCF against capitalised earnings | A 2-minute explanation of why Grant Samuel used both | I record myself and it fits in 2 minutes | P1-02 |

## Phase 2: data collection and extraction

| Done | ID | Tag | Task | Acceptance | Check | Needs |
|---|---|---|---|---|---|---|
| [x] | P2-01 | [AUTO] | Assumptions file schema and check | `assumptions.yaml` schema with value, unit, source, location, date and note, and a test that rejects a missing field | The test passes on a valid file and fails on each missing field. Evidence: `tests/engine/test_assumptions.py` passes (39 tests in the full check) and has one failing case for each of the six required fields, bad values, an unknown field, a duplicate key and several errors at once | P0-04 |
| [x] | P2-02 | [AUTO] | Extracted data schema and source trace test | CSV layout for `data/extracted/` with a source and page on every row, and a test for it | A row with no source makes the test fail. Evidence: `tests/engine/test_extracted.py` and `test_source_trace.py` pass, and a planted CSV with an empty source made `test_every_extracted_row_has_a_source` fail | P0-04 |
| [ ] | P2-03 | [ME] | Transcribe the valuation summary and share build | Values from booklet pp. 92 and 131 with the diluted share build | Totals match the printed totals, and a second reading finds no differences | P2-02 |
| [ ] | P2-04 | [ME] | Transcribe the historical profit and loss | FY21 to 1H25 from booklet pp. 118 and 120, with the one-off items | Subtotals match the printed subtotals | P2-02 |
| [ ] | P2-05 | [ME] | Transcribe the balance sheet, cash flow and net debt build | Booklet pp. 123 to 125 and 155 to 156, including the leases and the A$173.2m starting figure | The net debt bridge reaches A$187.0m | P2-02 |
| [ ] | P2-06 | [ME] | Transcribe the broker forecasts | By broker and median for FY25 and FY26 (booklet pp. 122 and 165) | The medians match the printed medians | P2-02 |
| [ ] | P2-07 | [ME] | Transcribe the DCF parameters and scenarios A to H | Booklet pp. 137 and 141 to 143, with the NPV chart values read from the chart and marked as read | Every value has a page, and chart readings are marked | P2-02 |
| [ ] | P2-08 | [ME] | Transcribe the discount rate evidence | Risk-free rate, premium, beta evidence and gearing (booklet pp. 139 to 140) | The WACC reproduces the 9.3% to 10.5% range | P2-02 |
| [ ] | P2-09 | [ME] | Transcribe the comparable companies | The peer table and multiples from booklet pp. 149 to 152, chart values marked as read | Each peer has a multiple and a page | P2-02 |
| [ ] | P2-10 | [ME] | Transcribe the precedent transactions and check primary sources | Booklet pp. 145 to 149 and 153, with the four multiples stated by a party checked against their releases | Each multiple has its release link, and unverified ones are labelled | P2-02 |
| [ ] | P2-11 | [ME] | Copy peer prices at 30 May 2025 by hand | Each price with its source and the date I read it | Every row passes the source trace test | P2-02 |
| [ ] | P2-12 | [MIXED] | Peer financials on one EBITDA basis | EBITDA, net debt and share counts from annual reports, with each adjustment recorded | A reconciliation row per peer from reported to adjusted EBITDA | P2-11 |
| [ ] | P2-13 | [MIXED] | Risk-free rate and exchange rates | RBA 10-year yield and the exchange rates I need, with the CC BY 4.0 credit | The 30 May 2025 yield is 4.249% as in RESEARCH.md | P2-02 |
| [ ] | P2-14 | [ME] | Fill the forecast and DCF inputs in `assumptions.yaml` | Revenue, margin, capex, working capital, tax, terminal growth and valuation date inputs, each with value, source, page and note, and my own judgements marked as mine | The schema test and the source trace test pass | P2-03 to P2-08 |
| [ ] | P2-15 | [ME] | Fill the discount rate and multiple inputs | Risk-free rate, premium, beta, gearing, cost of debt, peer multiples and precedent multiples, each with source, page and note | The WACC reproduces the 9.3% to 10.5% range from these inputs | P2-08 to P2-13 |
| [ ] | P2-16 | [ME] | Fill the balance sheet, share and control premium inputs | Net debt build, diluted shares, other assets and liabilities, and the control premium evidence, each with source and page | The net debt build reaches A$187.0m, and both checks pass | P2-03, P2-05, P2-10 |
| [ ] | P2-17 | [ME] | List what I could not verify | A short list in docs/RESEARCH.md with the reason and next step for each item | Each item has a reason and a next step | P2-14 to P2-16 |

## Phase 3: valuation model

| Done | ID | Tag | Task | Acceptance | Check | Needs |
|---|---|---|---|---|---|---|
| [ ] | P3-01 | [AUTO] | Engine structure and input loader | A package that loads the assumptions and data and raises an error on anything missing | Unit tests for loading, including a missing key | P2-14 to P2-16 |
| [ ] | P3-02 | [AUTO] | Free cash flow forecast | Revenue to unlevered free cash flow for each year, with a hand-worked fixture | The fixture test passes at full precision | P3-01 |
| [ ] | P3-03 | [AUTO] | WACC and terminal value | WACC from its inputs, Gordon growth terminal value, discounting with a mid-year option | A hand-worked example matches to six decimals | P3-02 |
| [ ] | P3-04 | [AUTO] | Equity bridge | Enterprise value to equity value to value per share using the adjusted net debt and diluted shares | Reproduces the expert's bridge from the expert's own enterprise value | P3-03 |
| [ ] | P3-05 | [AUTO] | Trading comparables | Multiples, selected range and implied value, with the peer basis adjustments | Unit tests with a two-peer hand example | P2-12 |
| [ ] | P3-06 | [AUTO] | Precedent transactions | Control multiples, selected range and implied value | Unit tests with a two-deal hand example | P2-10 |
| [ ] | P3-07 | [AUTO] | Control premium handling | Premium applied to trading values, with the basis stated in the output | A test shows the same value with and without the premium on the same inputs | P3-05 |
| [ ] | P3-08 | [AUTO] | Sensitivity grid | Value per share for a grid of discount rate and terminal growth, with the base cell marked | The base cell equals the DCF value | P3-04 |
| [ ] | P3-09 | [AUTO] | `valuation.json` writer | Every displayed number at full precision under a stable key, with its unit | A schema test lists every key | P3-04, P3-08 |
| [ ] | P3-10 | [AUTO] | Excel Assumptions sheet | Written from `assumptions.yaml`, with the source column | The workbook opens, and the sheet matches the file | P3-09 |
| [ ] | P3-11 | [AUTO] | Excel DCF sheet | Formulas that reference the Assumptions sheet, no hard-coded numbers | A scan finds no numeric constants in formula cells | P3-10 |
| [ ] | P3-12 | [AUTO] | Excel comparables and precedents sheets | Formulas for multiples and implied values | The same scan passes | P3-10 |
| [ ] | P3-13 | [AUTO] | Excel summary sheet and defined names | A defined name for each output equal to its `valuation.json` key | Each key resolves to a cell | P3-11, P3-12 |
| [ ] | P3-14 | [AUTO] | LibreOffice recalculation script | A script that recalculates the workbook headless with its own profile set to always recalculate | The calculated values come back for every named cell | P3-13 |
| [ ] | P3-15 | [AUTO] | Reconciliation tests and tolerance | Compares each named cell with the engine at A$0.005 per share and A$0.05m, and fails on empty or error cells | The test fails when I change a formula | P3-14 |
| [ ] | P3-16 | [ME] | Explain each Excel sheet | A written note per sheet saying what it does and why each formula is right | I walk through the DCF sheet aloud | P3-15 |
| [ ] | P3-17 | [ME] | Cross-check against the expert's disclosed scenario | My engine run on scenario A inputs, compared with the expert's value, with the difference explained | The difference is written up and sourced | P3-04 |

## Phase 4: reconciliation and gap analysis

| Done | ID | Tag | Task | Acceptance | Check | Needs |
|---|---|---|---|---|---|---|
| [ ] | P4-01 | [ME] | Set the base case forecasts | Growth, margins, capex and working capital, each with evidence and a range, written in my words | Each input has a source or a stated reason | P3-17 |
| [ ] | P4-02 | [ME] | Argue the discount rate | Inputs chosen with evidence and compared with the expert's, written in my words | I can defend each input in 60 seconds | P4-01 |
| [ ] | P4-03 | [ME] | Argue the terminal growth rate | A value and range with the reasoning against the expert's 4.0% | The note cites inflation and growth evidence | P4-01 |
| [ ] | P4-04 | [ME] | Choose the multiple ranges | Comparable and precedent ranges, with the peers and deals that drive them | Each range lists its evidence | P3-05, P3-06 |
| [ ] | P4-05 | [ME] | Argue the control premium | A value and range with the evidence from RESEARCH.md section 4 | The note cites the studies and the expert's treatment | P3-07 |
| [ ] | P4-06 | [MIXED] | Set my preferred value and range | Each method has a low, high and preferred value, and the combined range is explained | The weights are stated and the football field data is in `valuation.json` | P4-02 to P4-05 |
| [ ] | P4-07 | [AUTO] | Gap bridge from the expert's midpoint to my value | The bridge starts at A$4.26, labelled as the midpoint of the range and not a published figure, and each step is one assumption difference with its value per share | The steps sum to the total gap within the tolerance | P4-06 |
| [ ] | P4-08 | [ME] | Write a short explanation for each gap step | Two or three sentences with a source for each step | Each explanation names the input, both values and the effect | P4-07 |
| [ ] | P4-09 | [ME] | Interview prep: the largest gap in 60 seconds | A recorded explanation | It fits in 60 seconds and uses no notes | P4-08 |
| [ ] | P4-10 | [MIXED] | Trace every number | A list of every displayed figure with its source or test | No figure has an empty source | P4-08 |

## Phase 5: website

| Done | ID | Tag | Task | Acceptance | Check | Needs |
|---|---|---|---|---|---|---|
| [ ] | P5-01 | [MIXED] | Confirm the proposed chart and type defaults | Each proposed default in docs/DESIGN_RESEARCH.md (tick pitch, base-case border, bridge layout, fluid type) is confirmed or changed after the first chart is built, and the result is recorded there | The section lists each default as confirmed or changed | R-05, P5-04b |
| [ ] | P5-02 | [AUTO] | Design tokens and fonts | One tokens file with the colours, type scale and spacing, and the font subset self-hosted | No raw colour outside the tokens file, and the font file is under 25 KB | R-05 |
| [ ] | P5-03 | [AUTO] | Templates, build script and security tags | Base template, build script, the policy and referrer meta tags, scripts from the site only | The build output has no inline script and no third-party request | P5-02, P3-09 |
| [ ] | P5-04 | [AUTO] | Football field SVG generator | Rows with bars drawn from the price scale using percentage coordinates and no `viewBox`, ends labelled, an axis note, the offer line and the undisturbed line; if percentage coordinates do not resolve correctly in the browsers I test, I fall back to a `viewBox` with non-scaling strokes and record that | The SVG test checks each label against `valuation.json`, and a screenshot shows no collisions at 390 px | P5-03 |
| [ ] | P5-04b | [AUTO] | Football field styling and alternatives | My bars as a 45 degree hatch with an accent outline, the expert's bar as an ink outline, the preferred value tick, a text alternative and a data table | The edge of each bar and each line is at least 3:1 against the page, and the table lists every row's low and high | P5-04 |
| [ ] | P5-05 | [AUTO] | Landing page | Verdict sentence using the chart's notation (hatched band, outlined box, offer rule), the football field, and the three routes onward | Screenshots at 390, 768, 1280 and 1440 px | P5-04 |
| [ ] | P5-06 | [AUTO] | Provenance marker | A dotted accent underline on each sourced figure that opens the document, page and date as a popover, with a link fallback on older iOS, by keyboard and by tap | Keyboard and touch tests pass, and the note is dismissible | P5-03 |
| [ ] | P5-07 | [AUTO] | "Show sources" switch | Off by default; on, it prints a reference code beside each sourced figure | The page still works when the script fails | P5-06 |
| [ ] | P5-08 | [AUTO] | Valuation page: DCF tables | Forecast table and assumptions with units and sources | Every figure matches `valuation.json` | P5-03 |
| [ ] | P5-09 | [AUTO] | Sensitivity table | Discount rate by terminal growth grid with the base case shaded and a caveat line | A test confirms the shaded cell equals the base value | P5-08 |
| [ ] | P5-10 | [AUTO] | Comparables and precedents tables | Right-aligned figures, units in headers, scroll with a sticky first column at 390 px | Screenshots at four widths and a keyboard scroll test | P5-08 |
| [ ] | P5-11 | [AUTO] | Gap bridge chart and page | A bridge chart with signed steps and a link to each explanation | The steps add up in the test | P4-07, P5-03 |
| [ ] | P5-12 | [AUTO] | Deal timeline page | Each event with a date and a link | The link check passes | P1-07, P5-03 |
| [ ] | P5-13 | [AUTO] | Method and sources page | The assumption register, limitations and the disclaimer | Every register row matches `assumptions.yaml` | P2-14 to P2-16, P5-03 |
| [ ] | P5-14 | [ME] | Write the About page | Who I am, what the project is, and links to the repository and my resume | I am happy for every claim to be public | P5-03 |
| [ ] | P5-15 | [AUTO] | Site consistency test | Every figure in the built HTML is compared with `valuation.json` | The test fails when I change a figure in a template | P5-08 |
| [ ] | P5-16 | [AUTO] | Accessibility on every page | axe on each built page, with fixes for every violation | Zero axe violations | P5-05 to P5-13 |
| [ ] | P5-17 | [AUTO] | Performance and screenshots | Lighthouse on mobile for each page and screenshots at four widths, with fixes | Performance 90 or more, accessibility and best practices 95 or more, and the screenshots reviewed | P5-16 |
| [ ] | P5-18 | [ME] | Write the landing page copy | The verdict sentence and the text around the football field, in my words | Every sentence states a fact or a judgement with its reason | P4-06 |
| [ ] | P5-19 | [ME] | Write the valuation, gap and method page copy | Headings, captions and introductions in my words, with the gap explanations from P4-08 | The same check on every sentence | P4-08 |
| [ ] | P5-20 | [ME] | Review the site as a first-time visitor | A list of what I could not follow, and fixes | A friend reads it and can state the verdict in 30 seconds | P5-18, P5-19 |
| [ ] | P5-21 | [AUTO] | Deal docket header and colophon footer | A labelled line of target, acquirer, consideration and implementation date under the title; a footer with valuation date, data date, build date with a commit link, the disclaimer and the unit note | Both appear on every page, and the dates match `valuation.json` | P5-03 |
| [ ] | P5-22 | [AUTO] | Link-preview image | A 1200 by 630 image of the football field rendered at build time, with absolute `og:image` tags | The image exists in the build output and shows the base case | P5-04 |

## Phase 6: write-up and packaging

| Done | ID | Tag | Task | Acceptance | Check | Needs |
|---|---|---|---|---|---|---|
| [ ] | P6-01 | [AUTO] | Typst report template | A pinned Typst version, the template reads `valuation.json` and builds a PDF | The PDF builds from a clean clone | P3-09 |
| [ ] | P6-02 | [ME] | Write the report method and result sections | The three methods and my range, with a source for each input | Every figure on the page is in `valuation.json` | P4-06 |
| [ ] | P6-02b | [ME] | Write the report gap and limitations sections | The gap bridge in words, and what I could not verify | Each gap step names its input and effect | P4-08, P2-17 |
| [ ] | P6-02c | [ME] | Edit the report as a whole | One read-through for length, order and plain wording | It reads cleanly in under 15 minutes | P6-02, P6-02b |
| [ ] | P6-03 | [AUTO] | PDF reconciliation test | Figures extracted from the PDF text match `valuation.json` as displayed | The test fails when I mistype a figure in the template | P6-01 |
| [ ] | P6-04 | [ME] | Write the README | Executive summary first, then the structure in docs/ROADMAP.md | A reader gets the result in the first paragraph | P4-06 |
| [ ] | P6-05 | [ME] | Write the resume bullets and the LinkedIn post | Final text with my real results | I can defend each number in the bullets | P4-06 |
| [ ] | P6-06 | [ME] | Interview prep: questions on single numbers | An answer for each input in the assumption register | I answer any five random inputs without notes | P4-10 |
| [ ] | P6-07 | [ME] | Rehearse the 60-second walkthrough | A recording with the live site open | It fits in 60 seconds | P6-05 |

## Phase 7: deploy, QA and launch

| Done | ID | Tag | Task | Acceptance | Check | Needs |
|---|---|---|---|---|---|---|
| [ ] | P7-01 | [AUTO] | Pages deploy job | Deploys the site, the model and the PDF from a green `main` only | A deploy from a failing branch does not run | P5-17, P6-03 |
| [ ] | P7-02 | [ME] | Decide the first deploy to the public address | I confirm the address, the content and the About page | I have read the site once more | P7-01 |
| [ ] | P7-03 | [ME] | Check the live site on a phone and a laptop | A list of what I checked and the result | Downloads open and every page loads | P7-02 |
| [ ] | P7-04 | [AUTO] | Final checks on the live address | axe and Lighthouse on the deployed pages | Budgets met | P7-02 |
| [ ] | P7-05 | [ME] | Check the disclaimer and the sources on every page | Each page carries the disclaimer and a source line for each figure | I scroll every page | P7-03 |
| [ ] | P7-06 | [ME] | Link the site from my portfolio and resume | Both links work from a private window | I click each | P7-05 |
| [ ] | P7-07 | [ME] | Publish the LinkedIn post | The post is live with the chart image and its alternative text | I check the link preview | P7-06 |

## Version 2 (after the MVP is deployed)

| Done | ID | Tag | Task | Acceptance | Check | Needs |
|---|---|---|---|---|---|---|
| [ ] | V2-01 | [AUTO] | DCF controls | Sliders and fields look up the precalculated grid, with the scenario in the URL | The result matches the engine for every grid point | P7-07 |
| [ ] | V2-02 | [AUTO] | "Use the expert's assumptions" and "Reset to my base case" | Both buttons set the controls, with the change in value shown | A test for each button against the grid | V2-01 |
| [ ] | V2-03 | [AUTO] | Print stylesheet | The landing view and valuation page print as a clean two-page memo | A print preview screenshot at A4 | P7-07 |
| [ ] | V2-04 | [AUTO] | Copy link to this scenario | A button copies the URL holding the current control settings, and every parameter is checked against the precalculated grid before use | A test opens the copied link and gets the same result | V2-01 |
| [ ] | V2-05 | [AUTO] | Signed change marker | A changed figure fades briefly and shows its signed change from my base case, with no counting animation and one polite live region | A screen reader test reads the new sentence once | V2-01 |

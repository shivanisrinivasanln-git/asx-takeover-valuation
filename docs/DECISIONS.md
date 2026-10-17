# Decisions

A dated log of my decisions, the options I considered and the reason for each. Newest entries go at the bottom.

## 26 September 2026: the project folder is the repository

The GitHub repository is `shivanisrinivasanln-git/asx-takeover-valuation`. I kept the name independent of the deal, because the GitHub Pages address includes the repository name, so renaming the repository later would change the site's address.

## 26 September 2026: LF line endings and the main branch

This machine's system git config sets `core.autocrlf=true`, which would check shell scripts out with CRLF line endings on a fresh Windows clone, and `sh` fails on those. `.gitattributes` sets `eol=lf` for text files.

The default branch is `main`, since I will deploy only from a green main branch.

## 26 September 2026: time, tools, hosting and budget

Time: I want to finish as soon as possible without lowering quality. There is no fixed deadline and no weekly-hours cap. I will automate scaffolding, checks and data extraction where that saves time, and keep time for learning and interview preparation, because I need to be able to defend every number.

Excel: my level is intermediate (formulas, lookups, basic charts). The model stays readable at that level, and I will add learning tasks on model layout and data tables to my plan.

Stack: I lean towards a Python valuation engine feeding a static Next.js and React site, the tools I already know. I will make the final choice after comparing architecture options.

Hosting: a GitHub Pages project site at my github.io address, linked from my existing portfolio. I also considered a separate host such as Vercel, Netlify or Cloudflare Pages (previews, but another account and free-tier terms that can change) and a folder inside my portfolio repo (mixes histories). Pages needs no new account and costs nothing. It requires a fully static site, which the architecture must respect.

Budget and domain: A$0 and no custom domain, so there is no renewal that could lapse and break the link.

Analytics: none. No third-party script, no cookie banner, nothing to disclose.

## 27 September 2026: Domain Holdings Australia is the deal

I will value Domain Holdings Australia, acquired by CoStar Group by scheme at A$4.43 per share and implemented on 27 August 2025. Grant Samuel's range was A$4.06 to A$4.46.

Options considered: ten shortlisted deals, scored in [DEAL_SHORTLIST.md](DEAL_SHORTLIST.md). Domain scored highest: the expert used both DCF and multiples, it has close ASX-listed peers, and every document is free. The alternatives I weighed were each strongest on one thing: Boral for the expert changing its opinion (but the scrip consideration and missing ASX peers make it harder to value), Insignia Financial for a 2026 private equity contest (but the expert used one method), and Pacific Smiles for deal tactics (but no close listed peers). CSR and MMA Offshore scored above some of these but are orderly or sector-specific deals.

## 27 September 2026: architecture

The full design, with the sources for each tool fact, is in [ARCHITECTURE.md](ARCHITECTURE.md).

Valuation logic: one assumptions file, where every input carries its source, page and date, feeds a Python engine. The engine writes `valuation.json` for the site and the PDF, and writes the Excel model with live formulas. A reconciliation test recalculates the workbook in LibreOffice and compares every named output cell with the engine. The alternative was a workbook I build by hand, with Python reading it; that gives more Excel practice but leaves no unit tests on individual calculations and makes the workbook the thing that must be kept correct.

Site: the same Python code renders static HTML from Jinja2 templates, with charts drawn as SVG at build time and a little plain JavaScript that looks up precalculated values. I also considered a Next.js static export, which I already know but which loads the React runtime on every page, and Astro with React islands, which sends less JavaScript but is new to me. The Python route has the fewest dependencies and nothing to upgrade on the site side; the cost is that interactive parts are harder to build and test without a component framework.

Market data: no automated price downloads. Domain's prices and VWAPs and the beta evidence come from the scheme booklet, and peer prices for 30 May 2025 are copied by hand with their source. Yahoo Finance has no Domain history and its terms ban automated collection. UNSW's databases would have given a daily Domain series, but my access was not confirmed. The consequence is that I test Grant Samuel's beta against its own published evidence rather than estimating a regression beta of my own.

GitHub Pages cannot send HTTP security headers, so the security policy goes in a meta tag in each page. All scripts are separate files served from the site, so the policy can allow scripts from the site only.

## 4 October 2026: visual direction

I chose direction B, range first, with the "Show sources" switch from direction A. The football field is the landing page and each row opens its method. The type is Atkinson Hyperlegible Next only, subset and self-hosted, so the site makes no third-party request. The theme is light only at launch, and negative numbers use a true minus sign.

Options considered: A (workpaper, with reference codes on every figure), B, and C (a scheme booklet rebuilt for the screen). The measurements and the three self-reviews are in [DESIGN_RESEARCH.md](DESIGN_RESEARCH.md). B gives the fastest read on a phone and the lightest font load. I took the source switch from A because an interviewer needs to see where each number came from, and it starts off so it does not crowd the first screen. I rejected a dark theme for now because it doubles the contrast and colour-vision checks, and parentheses for negatives because I would still need minus signs for variances.

## 4 October 2026: roadmap approved

I approved the roadmap and task list as drafted in [ROADMAP.md](ROADMAP.md) and [TODO.md](../TODO.md): a minimum version with one deal, three methods, the football field, the gap analysis, the assumption register, the deal timeline, an Excel model, a PDF and a live site; a version 2 with the DCF controls and the print memo; and no stretch item until the minimum version is live. The task tags are [ME], [AUTO] and [MIXED].

## 4 October 2026: front-end refinements and the bridge start

After reading how public sites handle dense numbers (see [DESIGN_RESEARCH.md](DESIGN_RESEARCH.md)), I kept the palette and typeface of direction B and adopted: a stronger hatch with an accent outline and a dotted underline as the provenance marker; the chart's notation in the verdict sentence; a deal docket header; a colophon footer; and a link-preview image. For version 2: a copy-link button and a signed change marker. I did not adopt a white plate behind the chart (my rule keeps the raised white surface for overlays), the offer line as a stepped border in the sensitivity table, a sticky range summary, an SVG download button, or page transitions from each row to its method page.

The gap bridge starts from the midpoint of Grant Samuel's range, A$4.26, labelled as a midpoint and not as a figure the expert published, because the expert gave a range only. The alternatives I was offered were two bridges (low to low and high to high), which is more faithful but doubles the chart and is hard to read on a phone, and a bridge from the offer price, which answers a different question.

## 4 October 2026: Python tooling

I use a `pyproject.toml` for dependencies and tool settings, `uv` to compile `requirements.lock` with a hash for every package (installs from it fail if a file does not match its hash), Ruff for formatting and linting, mypy in strict mode for types, and pytest for tests. The alternatives were Poetry or PDM, which add a larger tool and their own lock formats, and plain `pip freeze`, which records no hashes. The full check is one script, `scripts/check.py`, that runs the four steps with the interpreter that started it and prints one summary line, so it behaves the same on my machine and in CI.

Rates in the engine are percentages named with `_pct`, money is A$ millions named with `_aud_m`, and per-share values are in A$ named with `_aud`, so a unit is visible in every name.

The Harbour Industrial example in [RESEARCH.md](RESEARCH.md) became the first test. It found a rounding in the example: the WACC works out to 10.42%, not 10.4%. The example's later steps use 10.4%, so I changed the text to say 10.42% rounded to 10.4%, and the test checks both.

Three Ruff ignores are the only ones: asserts in tests, and the fixed subprocess call and printed summary line in the check script. I declared Jinja2, openpyxl, PyYAML and the audit tool now, although nothing uses them yet, because the architecture fixes them and the lockfile should hold the full set from the start. The build step joins the full check when the first build exists, in task P5-03.

## 5 October 2026: how the inputs and data files are checked

`assumptions.yaml` entries have six required fields (value, unit, source, location, as_at, note) and one optional flag, `judgement`, which marks an input that is my own judgement and not a figure from a document. A value is a number or a list of numbers, and `as_at` must be a real date written like "30 May 2025". The loader rejects an unknown field, because a misspelt field would otherwise be silently ignored, and a repeated key, because plain YAML keeps the last one without a warning. It reports every problem in one error, so I can fix a file in one pass.

Each CSV file under `data/extracted/` must have `source`, `location` and `as_at` columns, with a value in each on every row, and at least one row. The source trace test runs both checks over the files in the repository, so a figure I add without a source fails the full check.

## 5 October 2026: licence

I chose the MIT licence for the code, with the copyright line "Copyright (c) 2026 Shivani Srinivasan". The options were Apache-2.0, which adds an explicit patent grant and a longer notice that a project this size does not need, and no licence, which would stop anyone legally reusing the code and looks closed to someone reading the repository. MIT is short, permissive and the usual choice for a portfolio project. It covers the code only. The documents I link to, such as the scheme booklet and company reports, belong to their owners and keep their own terms, and I do not copy them into the repository.

## 5 October 2026: design tokens and the font file

The site's static files live in `site/static/`: `tokens.css` and the font in `site/static/fonts/`. The notes and script for rebuilding the font are in `site/font-source/`, outside the folder that will be published. `tokens.css` holds every raw colour, the type scale and the spacing scale as CSS custom properties, so a component never writes a hex value. A test fails if any other stylesheet, SVG or template in `site/` contains one.

The font is one variable file of Atkinson Hyperlegible Next, narrowed to weights 400 to 600 and subset to Basic Latin plus the punctuation I use and the true minus. It is 11.6 KB. The design research estimated 21 KB from an earlier subset whose settings I did not keep, so I do not know what accounts for the difference. Both are below the 25 KB limit. I downloaded it from the Google Fonts repository and checked the file's git hash against the one GitHub lists. The font's own licence file sits beside it.

The colours are the ones in the design research. The tests recalculate their contrast ratios, so a change to a hex value that breaks the contrast rules fails the full check. The three largest type steps use the `rem` plus `vw` values from the front-end research, growing one step between 390 and 1440 px. At 390 px a section heading is therefore 20 px, the same size as a subheading, and only the weight separates them. I will look at that on the first built page and confirm or change it in P5-01.

I left out the radius and shadow tokens, the chart stroke widths and the fallback font face with `size-adjust`. Each is needed by a later task (templates, chart styling, performance), and I will measure each against a real page then.

## 5 October 2026: risk-free rate and exchange rates

I read the 30 May 2025 rows of the RBA tables and stored them in `data/extracted/market_rates_30_may_2025.csv`: the 10-year yield of 4.249%, A$1 = EUR 0.5670 and A$1 = GBP 0.4775, with the RBA credit that CC BY 4.0 requires in each row's source.

Two things differ from what I had written in RESEARCH.md. The RBA's monthly table has a SEK column, but it stopped in November 2013, so no RBA table has the krona rate for my date. And Grant Samuel's 4.3% (booklet p. 139) is not the RBA's 4.249% rounded; it is 0.05 percentage points higher, for a reason I could not find. Which figure goes into `assumptions.yaml` as my risk-free input is a decision for P2-15, where I will record both.

I did not collect SEK or NOK rates. An EV/EBITDA multiple needs no conversion when the value and the earnings are in the same currency, so the rates would only show Hemnet's and Vend's size in A$. The options were the Riksbank and Norges Bank tables (free, but a second set of terms to check) or leaving the sizes in local currency. I will revisit this if the peer table needs A$ sizes.

## 5 October 2026: which tasks I do by hand

I retagged the reading, transcription and note-writing tasks (P1-01 to P1-07, P0-08 and P2-03 to P2-11) from [ME] to [AUTO], so tools do them and I read and test the result. The reason is time: reading the expert's report and transcribing its tables is the slowest part of the plan, and it needs no judgement that I have not already scoped.

I keep [ME] for judgement calls: which risk-free rate, which peers, which multiples, the forecast assumptions (P2-14 to P2-16 and Phase 4), anything public about me, and the interview preparation that only I can rehearse. The Excel practice sheet (P0-08) is in the list too. It was a learning task, so its check now tests the workbook and no longer tests whether I can rebuild it; I will rebuild its sensitivity table myself before an interview. The no-download rule for market prices still applies to P2-11: prices are read from a named source and recorded with the date read. Each check that read "I explain it aloud" became a check against the source, such as a page number on every statement, a total that matches the printed total, or a test.

Transcription rules: a table is checked against the totals printed in the booklet, and when a total does not match I re-read the page and never change a number to make it fit. A figure read from a chart is marked as read. A timeline row is marked verified only when I have opened its source document, and otherwise stays unverified with the reason. The cost is that I must read the notes closely before an interview, because I did not write the first draft of my understanding; the notes carry page numbers so I can check each claim against the booklet.

## 5 October 2026: no peer share prices

The booklet prints no peer share prices, and the investor sites I tried (REA Group and Scout24) show no historical close. I have not cleared the terms of the price portals for reading by a tool, and my architecture rule is that I download no price series.

Options I considered: reading each close from a price portal and marking it as a secondary source (fast, but it breaks the rule); looking each close up through UNSW's Bloomberg or FactSet access (the most defensible, but my access was never confirmed); or using the peer multiples that Grant Samuel printed for the same date, 30 May 2025 (booklet p. 150). I chose the printed multiples. I recorded all 32 of them in task P2-09 and P3-05 will use them.

I dropped P2-11 (peer prices) and P2-12 (peer financials on one EBITDA basis), because P2-12 only serves multiples recomputed from peer prices. The cost is that my trading comparables rest on the expert's multiples and I cannot put the peers on my own EBITDA basis. The A$ size of Hemnet and Vend, which I would have needed krona and krone rates for, also drops out.

## 5 October 2026: the practice workbook and Excel

I built the one-sheet DCF (task P0-08) from the Harbour Industrial example, so its base value per share is the hand-worked A$3.05, and its sensitivity table is a real Excel data table. LibreOffice is not installed on this machine and desktop Excel 16 is, so I recalculate the workbook with Excel through a short PowerShell script and test the values Excel stores against a Python calculation. The recalculation script also removes the author names that Excel adds. The reconciliation in task P3-14 will use LibreOffice in the build, as the architecture says.

openpyxl has no type information, which fails the strict type check on the script and the test that read the workbook, so I added `types-openpyxl` to the development dependencies and regenerated the hashed lock file. The only change in the lock file is that one package. The alternative was to switch off type checking for openpyxl, which would loosen the check.

## 5 October 2026: how I fill assumptions.yaml

The expert did not publish its cash flows, only averages and end points (booklet pp. 137 to 145). I chose to seed every input with the value the expert disclosed, with its page, and to change an input only where I disagree, in Phase 4. The other options were to propose my own values for every input now, which blocks the engine until dozens of inputs are settled, and to enter values I decide one by one.

Where the booklet describes a value in words, I chose a number and marked it `judgement: true`: revenue growth of 9.0% a year ("just over 9%"), an FY35 EBITDA margin of 47.9% ("just below 48%"), capital expenditure of 9.6% of revenue for FY26 to FY30 (the 1HY25 level; the expert says "higher in the early years"), depreciation rising to 9.0% of revenue (it says "approximately equal" to capital expenditure after the early years), and Residential plus Media, Developers and Commercial at 82.1% of revenue (the base for the agents' dividends). Between the disclosed end points the engine will use straight lines, for the EBITDA margin from the FY25 level to 41% in FY30 and then to the FY35 level, and for depreciation. The expert's average capital expenditure of almost 9.5% of revenue is not reproduced by my path, which averages 9.3%, and I cannot tell which years carry the higher rates (UNVERIFIED).

## 5 October 2026: risk-free rate and the seeded multiples

I answered three questions while filling the discount rate and multiple inputs (task P2-15).

Risk-free rate: I chose the RBA 10-year yield of 4.249% at 30 May 2025. The options were the expert's 4.3% (no gap on this input, but I could not reproduce it from the RBA series) and 4.366%, the RBA yield at 31 December 2024 (matches the valuation date but differs from the expert's date). I chose 4.249% so that the 0.05 point difference from the expert shows as its own step in the gap bridge. I keep the expert's 4.3% as a separate input, so the cross-check against its scenario A (P3-17) uses its own inputs. With either rate the inputs reproduce the expert's calculated WACC range of 9.3% to 10.5%, because the cost of debt is the risk-free rate plus the 1.2 point margin.

Trading comparables: I seeded the range with the expert's implied multiple of FY26 adjusted EBITDA, 18.2x to 19.9x (booklet p. 153), and set no control premium until I decide one in P4-05. That multiple is already on a control basis, so applying a premium to it would count the premium twice. The alternatives were the forecast EBITDA multiples of the four peers the expert compares Domain with (SEEK 16.3x, Rightmove 19.1x, Scout24 22.2x and CAR Group 22.8x) plus a premium of 20% to 35%, which puts my seed well above the expert's value, and the full spread of the eight peers, which includes REA, Hemnet, Baltic and Vend. When I put the question I gave the four-peer range as 16.3x to 22.2x, which left out CAR Group's 22.8x; the answer does not depend on it.

Precedent transactions: I seeded the same implied range. The expert says it sits at the high end of diversified marketplace deals (15x to 20x forecast EBITDA) and towards the lower end of the property deals (22x to 25x for ZPG and the Rightmove proposal). The alternatives were the diversified deals alone or the property deals alone. I choose my own ranges in P4-04.

## 6 October 2026: how my forecast turns revenue into free cash flow

The expert did not publish its cash flows, so I built a plain forecast from the inputs I seeded (task P3-02). Free cash flow each year is (EBITDA plus the corporate cost saving minus depreciation) taxed at 30%, plus depreciation, minus capital expenditure, minus the increase in working capital, minus the dividends paid to the agents who hold equity in Domain's subsidiaries. The agents' dividends reduce the cash flow that belongs to Domain's shareholders, which is how the expert treats them (booklet pp. 136 to 137 and 142).

My modelling choices, each of which changes the value and which I will measure when I cross-check against the expert's scenario A (P3-17): the EBITDA margin and depreciation move in straight lines between the disclosed end points, with depreciation reaching its long-term share of revenue in FY30; tax is charged on EBITDA plus the saving, less depreciation, with no deduction for the amortisation of acquired intangibles (the booklet does not say whether it is deductible); working capital is 2.5% of the change in revenue; the corporate saving of A$4.0m a year is part of taxable profit and the agents' dividends are deducted after tax; and the second half of FY25 is the FY25 broker median less the first half actually reported, with capital expenditure at the early-year rate of 9.6% of the stub revenue and with working capital, the agents' dividends and the saving scaled by the half year left.

Run on the seeded inputs, the forecast gives FY26 revenue of A$457.8m and EBITDA of A$165.1m, against broker medians of A$453.8m and A$160.0m, and FY35 revenue of A$994.3m.

## 6 October 2026: mid-year discounting

The booklet does not say whether the expert discounted each year's cash flow at the middle of the year or at the end (UNVERIFIED). I chose mid-year for my base case (task P3-03). It treats cash as arriving evenly through the year, which fits how Domain earns it. When I put the question I also described mid-year as the more usual practice; I have not checked that against a source (UNVERIFIED), so it is not part of the reason. The alternative was year end, which values the business about 5% lower at a 10% discount rate. The engine computes both, the choice is the input `mid_year_discounting_flag`, and the cross-check in task P3-17 will report both.

Mid-year flows come half a year sooner, so the Gordon terminal value, which assumes year-end flows, is multiplied by one plus the discount rate to the power of 0.5 before it is discounted. The stub period is the second half of FY25, so its cash flow is on average a quarter of a year after the valuation date instead of half a year.

On the seeded inputs and mid-year discounting, the enterprise value of business operations is A$2,401m at a 10.5% discount rate and A$2,898m at 9.5%, against the A$2,402m and A$2,893m I read from the expert's scenario A bar (booklet p. 144). Year end gives A$2,285m and A$2,770m. I chose the convention before I ran the comparison, and I did not change a modelling choice to make the numbers agree.

## 8 October 2026: what valuation.json holds

`valuation.json` has four parts (task P3-09): `values`, a flat map from a stable key to a number and its unit; `football_field`, the rows of the chart as pairs of keys; `forecast`, the stub period and FY26 to FY35 with each line of the free cash flow and its present value at the base discount rate; and `sensitivity`, the 5 by 5 grid. The key names carry the unit (`_aud_m`, `_aud`, `_pct`, `_x`, `_shares_m`), a test checks that each stored unit matches its key, and a second test lists every key, so adding or dropping one fails the full check until the list is updated. The Excel defined names will equal these keys (task P3-13).

A trailing `_low`, `_mid` or `_high` is the value case, not the rate. The low case discounts at the top of my adopted range (10.5%) and uses the larger of the two diluted share counts, which is how the expert pairs them (booklet p. 131). The mid case uses the middle rate (10.0%) and the average share count, so it equals the base cell of the sensitivity grid, and a test checks that.

The football field lists the DCF, the trading and precedent methods on the EBITDA multiple, and the expert's range. The EBITA values are in `values` but not in the chart rows, because choosing between the two measures is part of my multiple ranges in P4-04. On the seeded inputs the DCF gives A$3.47, A$3.83 and A$4.26 a share (low, mid, high). The expert's midpoint of A$4.26 is the average of its printed A$4.06 and A$4.46, and is labelled as mine wherever it appears. The file is written to `build/valuation.json` by `PYTHONPATH=src python -m valuation`, and `build/` is not tracked.

## 8 October 2026: the Assumptions sheet and defined names

The workbook's Assumptions sheet (task P3-10) lists the 59 inputs from `assumptions.yaml`, then eight values that the engine reads from the transcribed tables (FY24 revenue, the 1HY25 revenue, EBITDA and depreciation, and the expert's printed business operations value and value per share), then one model structure row, `early_years_count` = 5. The second and third groups are there so that every number a formula uses sits on this sheet with its source, and no formula reads a CSV file. Each row has the value, unit, source, page, date, a judgement marker and the note. The 1HY25 depreciation is stored as printed, a negative cost, and the DCF sheet will reverse the sign.

Each input has an Excel defined name equal to its input name, so a formula reads `=tax_rate_pct`. A series such as `valuation_date_ymd` is one name over three cells. Where a `valuation.json` key is also an input (for example `offer_price_aud`), the name points at the input cell, so the output and the input cannot disagree.

## 8 October 2026: the DCF sheet

The DCF sheet (task P3-11) repeats the engine's calculation as formulas, row by row: the forecast from the stub period to FY35, the terminal year, the value at the low, mid and high discount rates, the equity bridge and the 5 by 5 sensitivity grid, where each cell is a full recalculation (the present value of the cash flows at the row's rate is in column H, and the terminal year is worked out again for each growth rate). Every input is read by its defined name, never by cell address, and a test fails if a formula uses an address on the Assumptions sheet.

A formula may contain only the numbers 0, 1, 2 and 100: percent to a fraction, a step of one year, and an average of two. The scan in `src/valuation/formula_audit.py` fails on any other number. The mid-year switch is written as `mid_year_discounting_flag / 2`, so that setting the flag to 0 gives year-end discounting without changing a formula. The grid is five cells wide; if I change `sensitivity_steps_each_side` the sheet would need a wider grid, and the reconciliation test (P3-15) would catch the mismatch.

Before writing the tests I recalculated the workbook in desktop Excel and compared the DCF outputs with `valuation.json` by hand: all 39 DCF and reference outputs agreed to 1e-9 or better, and the 25 grid cells differed by at most 9e-16. The committed comparison is task P3-15. This machine blocks unsigned PowerShell scripts, so I run `scripts/recalculate_with_excel.ps1` with `-ExecutionPolicy Bypass` for that one process, which leaves the machine setting unchanged.

## 12 October 2026: the Comparables and Precedents sheets

Both sheets (task P3-12) value Domain at my selected multiple range times FY26 adjusted earnings, for EBITDA and for EBITA, then run the same bridge as the DCF sheet, reading net debt and the share counts by the names of the DCF sheet's cells, so the three methods cannot drift apart. The control premium row on the Comparables sheet reads `control_premium_applied_pct`, which is zero until P4-05. On the Precedents sheet the premium is a typed 0, because deal multiples are control multiples.

Under each value block I copied the expert's printed multiples with their page and date (8 peers by four multiples on Comparables, 9 deals on Precedents), and added the lowest, median and highest of each column as formulas. These tables are evidence for me to read when I choose my ranges in P4-04. The value does not use them, and each sheet says so. I put the evidence on the sheets and not on the Assumptions sheet because they are not inputs to the calculation.

## 12 October 2026: the Summary sheet and the defined names

The Summary sheet (task P3-13) lists value per share by method as the football field rows of `valuation.json`, then the offer, the undisturbed price, the offer premium and the midpoint of the expert's range, then the adopted discount rate range beside the two WACC builds. The WACC build sits at the bottom of the DCF sheet, once at my risk-free rate and once at the expert's, so the 9.3% to 10.5% range can be traced input by input.

The workbook has one defined name for each input and one for each of the 101 keys in `valuation.json`, and no others. A test fails if a key has no name, if a name points at a range, or if a name exists that is neither an input nor a key. Where a key is also an input (the offer price and the undisturbed price, for example) the name points at the Assumptions cell.

## 12 October 2026: my base case (tasks P4-01 to P4-05)

I answered five sets of questions, and the inputs, evidence and ranges I tested are in [BASE_CASE.md](BASE_CASE.md). In each case the options were the expert's value, a value between the evidence on either side, and a lower value.

Forecasts: I kept the expert's growth of 9.0%, FY30 and FY35 EBITDA margins of 41% and 47.9%, capital expenditure of 9.6% then 9.0%, and working capital of 2.5%. The brokers cover only FY25 and FY26 (growth of 7.4% and 8.0%), so they do not set a ten-year rate, and keeping the expert's forecast makes my differences from it appear in the discount rate and the multiples. The cost is that my value inherits a margin above anything Domain has reported. I show 46% (the expert's Scenario C) as the downside at A$3.67 a share.

Discount rate and terminal growth: I kept 9.5% to 10.5%, beta 1.0 to 1.1 and terminal growth 4.0%. Brokers use 8.4% to 9.0%, and a beta of 0.9 would give 8.77% and a DCF high value of A$5.04, but I do not want one beta estimate to put my bar above the offer. The terminal value at 4.0% is 9.9x FY35 EBITDA, so I do not regard 4.0% as aggressive.

Multiples: the seeded 18.2x to 19.9x was the expert's own implied multiple, so I replaced it. Trading is 16.3x to 19.1x (SEEK and Rightmove, the two lowest of the eight peers) and precedents are 15.2x to 22.3x (the six deals less the highest and the lowest). For EBITA I used the same two peers for trading (not the two lowest on EBITA, since CAR Group's 23.1x is second lowest) and the same trimming rule for precedents, and I left the football field on EBITDA. The alternatives were SEEK, Rightmove, Scout24 and CAR Group in full (16.3x to 22.8x) and Rightmove to Scout24 (19.1x to 22.2x). I first described those four as the closest peers, which was wrong: the expert keeps SEEK and CAR Group with caution as less comparable, and calls REA the closest Australian peer. I asked again on 12 October 2026 and kept 16.3x to 19.1x.

Control premium: 25% on the trading method only, at enterprise value level, which is about 27.4% on the share price (the RSM median is 27.5%). The alternatives were 20%, 30% and no premium, which would leave the trading bar on a minority basis against a control offer. The engine applies the premium to enterprise value, so a share-price premium would overstate it for Domain, whose net debt is 8.7% of enterprise value.

## 12 October 2026: method weights, mid cases and my preferred value (task P4-06)

I answered one question on the weights. The options were equal thirds, 50/25/25, 40/30/30 and the DCF alone. I chose DCF 50%, trading comparables 25% and precedent transactions 25%. The combined low, preferred and high values per share are the weights times each method's low, middle and high value, so my preferred value is A$4.21 and my range is A$3.71 to A$4.75. The numbers and the alternatives are in [BASE_CASE.md](BASE_CASE.md).

Trading and precedents needed a middle case. I used the midpoint of the multiple range and the average of the two diluted share counts, the same share count as the DCF middle case, because neither range has a preferred point. The weights are three inputs that must add to 100, and the engine stops with an error if they do not. The football field uses the EBITDA multiple for both multiples methods, so the weights use those values and the EBITA values stay as information.

The preferred value of each method is its middle case. I added a named key for each (`preferred_dcf_value_per_share_aud` and the same for trading and precedent) as well as the combined `combined_value_per_share_aud_low`, `preferred_value_per_share_aud` and `combined_value_per_share_aud_high`, so the site, the model and the report read one name for each. The football field has a fifth row for my combined range and every row except the expert's carries a key for its preferred value. The Summary sheet shows the weights and the combination as formulas, and the Comparables and Precedents sheets have a Mid column.

## 12 October 2026: how the gap bridge is built (task P4-07)

The bridge starts at A$4.26, the midpoint of the expert's printed A$4.06 to A$4.46 (a midpoint of a printed range and not a figure it published) and ends at my preferred value of A$4.21. The gap is A$0.05 below the start. Each step changes one group of inputs from the expert's value to mine and records the change in my preferred value per share, running the engine from the inputs to the preferred value each time.

The expert's value for each input I can change is stored in `assumptions.yaml` as `expert_` plus my input's name, with its page: the adopted discount rate of 9.5% and 10.5% (pp. 138 and 140), its forecast (pp. 141 and 142), terminal growth of 4.0% (p. 142), and the multiples of 18.2x and 19.9x implied by its own range (p. 153). It prints no premium and no weights, so I store a premium of zero and weights of 0, 50 and 50 (DCF, trading, precedents) as my reading, each flagged as my judgement. Where the expert gave a description and I chose the number (growth, the FY35 margin, early capital expenditure and depreciation) the expert's entry carries the same number and the same judgement flag.

Order used, because it changes the size of each step: method weights, discount rate, forecast, terminal growth, trading multiples, precedent multiples, control premium, then net debt and shares. The expert gave no weights, and its range equals the range its multiples imply (p. 153), so on its own inputs its position matches the multiples methods and not its DCF. The first step applies my 50/25/25 weights to the expert's inputs, which gives A$4.05 and moves the value by A$0.21 down. Every later step is then measured at my weights, so a DCF input counts at half its effect on the DCF and a multiples input at a quarter. Putting the weights last would have left the DCF steps at zero weight, so they would show no effect even if I changed a DCF input later.

On my inputs the steps are weights A$0.21 down, trading multiples A$0.08 down, precedent multiples A$0.02 down and the control premium A$0.27 up. The discount rate, forecast, terminal growth and the net debt and share counts are A$0.00, because I kept the expert's values (the net debt and share counts are its own figures in my model, so that step is zero by construction). The order matters most for the trading multiples and the premium: swapping them gives A$0.10 down and A$0.29 up, with the same sum of A$0.18 up. My engine on the expert's multiple range gives A$4.2597 against the printed midpoint of A$4.26, a difference of A$0.0003 from the rounding of its printed multiples, which I show apart from the steps.

The steps are computed by the engine and are in `valuation.json` under `gap_bridge`, not in the workbook. A step is a full recalculation with one group swapped, which would need eight copies of the model sheets. A test checks that the start plus the reconstruction difference plus the steps equals the end, and that the steps add up to the gap within A$0.005. The explanation of each step is task P4-08.

## 12 October 2026: the model is recalculated in Excel and committed (task P3-14)

I planned to recalculate the workbook in LibreOffice (5 October 2026 entry and [ARCHITECTURE.md](ARCHITECTURE.md)). LibreOffice is not installed on this machine and I have not approved installing it, so I use desktop Excel through `scripts/recalculate_with_excel.ps1`, which I run with the execution policy bypassed for that one process. This machine blocks unsigned scripts and the setting itself is unchanged. The options were installing LibreOffice (closer to the plan, and what a CI job would use, but an install I have not approved) and Excel (already here, and I recalculated by hand with it in P0-08 and P3-11 to P3-13).

`scripts/build_model.py` builds the workbook, has Excel calculate and save it, and writes `model/domain_valuation_model.xlsx`, then checks that every one of the 134 named cells holds a number within tolerance. I commit that file so the reconciliation test (task P3-15) reads stored values. CI has no spreadsheet program, so what it tests is the committed file. The cost is a binary file in the repository and a build step I have to remember after any input or formula change. The tolerance is A$0.005 a share and A$0.05m, and the same order of size for percentages, multiples and share counts, set in `src/valuation/reconcile.py`.

## 12 October 2026: how the reconciliation test works (task P3-15)

`reconcile` in `src/valuation/reconcile.py` reports two kinds of problem, and the test in `tests/engine/test_reconciliation.py` fails on any. A value problem is a named output cell that is missing, empty, an error or further from the engine than the tolerance for its unit (A$0.005 a share, A$0.05m, and the same order of size for percentages, multiples, years and share counts). A stale problem is a difference between the committed workbook and one built now from the inputs: any formula, typed value or defined name. Without the second check, a change to an input or a formula would pass as long as I had not rebuilt the file, because the stored values would still agree with the engine's old figures.

Excel did not rewrite any formula in this workbook, so the formula comparison is exact text, and numbers are compared to a relative 1e-12. What the test cannot see is a function that another program calculates differently, because it reads Excel's stored values and CI has no spreadsheet program. I accept that, since the workbook uses plain arithmetic and seven standard functions (`IF`, `INDEX`, `SUM`, `SUMPRODUCT`, `MIN`, `MEDIAN` and `MAX`), and a test fails if a formula uses any other.

I checked that each part can fail. Each of these is a test: a changed formula, a changed typed input, a removed name, a stored value that differs from the engine, an empty cell, an error cell, values just inside and just outside both tolerances, an uncalculated workbook, and an input changed without rebuilding the model. I also changed `/100` to `/101` in the Summary sheet's formula writer without rebuilding, and the main test failed on the formula text.

## 12 October 2026: the explanation of each gap step (task P4-08)

I went through the eight steps one at a time and chose the wording of each, with the question tool, on 12 October 2026. The step 2 wording was put to me with the question about zero steps, and I took the answer to that question as agreeing to it. The texts are in `data/written/gap_step_explanations.csv`, one row per step with its pages, which the loader reads like the transcribed tables (each row needs a source, location and date). The engine adds each text and its pages to its step in `gap_bridge`, so the site and the report use the same words. The options were a Markdown document that someone would have to keep in step with the numbers, and a field in `assumptions.yaml`, which holds inputs and not prose.

Two checks keep the words honest. The bridge raises an error if the explanations do not match the steps, and a test fails unless each text contains its step's amount to the cent (for example A$0.21 for the weights), so a change in an input that moves a step forces a rewrite. The figures quoted inside the texts (A$4.77 at 9.0%, A$3.67 at 46% and so on) are not tested individually, and I checked each against the engine when I wrote it.

Four steps are A$0.00 because I kept the expert's value, and I chose to keep all four on the bridge, each explained, so the bridge shows where I did not differ.

Two of the four deals in my precedent range, Scout24 and Rightmove, were unsuccessful proposals, which I had not been told when I chose the range. I kept the range and show a second figure: with completed deals only (15.2x to 17.7x, same trimming rule) my preferred value is A$4.07 and my range A$3.71 to A$4.47. It is calculated by the engine and sits in `valuation.json` under `sensitivities`, not in the workbook, which would need a second precedents range. Where it appears on the site is decided with the method page copy.

I corrected one error in my earlier notes. The forecast section of BASE_CASE.md and the 12 October entry above called the FY35 margin "the expert's most favourable assumption", but its Scenario B has a higher margin (51%, p. 143), and a point of growth is worth more than a point of margin. Both now say that the margin is above anything Domain has reported.

## 12 October 2026: the list of every figure and where it comes from (task P4-10)

The list is `data/written/figure_trace.csv`, one row for each group of figures in `valuation.json` (81 rows, expanding to 175 figures). I put it beside the other tables I wrote myself, and not in a Markdown document, because a CSV can be tested and the Method page can read it. A row has the figure's path, whether it is an input, a transcribed value, a calculation or my own wording, one sentence on how it is calculated, the inputs and transcribed tables it depends on, and the tests that cover it. A row can also cite a heading in one of my documents, which I use for the two precedent control premiums: they are zero because deal multiples are control multiples, a rule that sits in the engine and in the Control premium section of BASE_CASE.md, not in a source document. The source and page of a figure are read from the entries of its inputs when the listing is written (`PYTHONPATH=src python -m valuation.figure_trace` writes `build/figure_trace.csv`), so a source is typed once, in `assumptions.yaml` or the data file.

The test fails when a figure has no row, a row has no figure, a named input or test does not exist, or a figure has no source and no test. The part I added after the first draft is the dependency check: the test moves each input by 5% (the weights against each other, the mid-year switch to zero, the grid width to three steps) and each numeric column of each transcribed table, and fails if a figure moves that its row does not list. Without it, the list would be true only on the day I wrote it. The reverse (a row names an input that moves nothing) is checked for inputs written out in a row, and not for inputs that arrive through a reference to another figure, because a reference brings in a whole stem and one case of it may not use every input.

Five inputs move no figure: the typical control premium range, the listed share discount range and the special dividend. They are evidence I keep in `assumptions.yaml` and show on the Assumptions sheet, not inputs to a calculation. The test lists them by name, so a sixth has to be looked at. The two dates are not moved, because a date changes labels and the number of forecast years and not a figure by a step; I name them by hand on the row they affect.

The listing does not check the figures quoted inside the explanation texts (A$4.77 at 9.0% and so on). That row is kind `written`: its source is my wording of 12 October 2026, and the test from P4-08 checks each text against its step's amount.

## 12 October 2026: how the site is built and what its pages may load (task P5-03)

`python -m valuation.site_build` renders the Jinja2 templates in `site/templates/` from the engine's numbers and writes `build/site/`, together with a copy of `site/static/` (the tokens file, the page stylesheet and the font). It then runs `src/valuation/site_check.py` over the files it wrote and exits with an error on any problem, so the full check fails if a page breaks the rules below. The check reads the built files and not the templates, so it sees what the browser sees. Jinja2 autoescaping is on and an undefined variable is an error, so a misspelt name fails the build and does not print an empty string.

The policy in every page's meta tag allows the page's own origin and nothing else: `default-src 'none'`, then `script-src`, `style-src`, `img-src`, `font-src` and `connect-src` set to `'self'`, and `base-uri` and `form-action` set to `'none'`. A check rejects any value other than `'self'` and `'none'`, so `'unsafe-inline'`, a host or a `data:` address fails. A directive that appears twice fails, because a browser uses only the first, and the policy tag must sit in `<head>` before anything is loaded. A consequence is that no page can carry an inline script, a `<style>` element or a `style` attribute, and the check fails on each. Charts therefore get their colours and sizes from classes in `site/static/site.css`, and positions from SVG attributes.

The check accepts a list of known forms and rejects the rest, because a list of bad forms kept missing variants. Anything a page loads must be a plain relative path: a scheme, a protocol-relative address, a root-absolute address, a backslash, a control character or a `srcset` candidate that points elsewhere fails, and so does a `url()` in an SVG attribute that is not a relative path or a fragment. Only the element names my templates use are accepted (`ALLOWED_TAGS` in `site_check.py`), so frames, objects, forms, `<base>`, `<style>` and SVG animation fail because they are not on the list, and a template that needs another element adds it there, which shows in the diff. A link a visitor follows (`<a href>`) may be an absolute http or https address, because following it loads nothing into the page, and no other scheme: `javascript:` and `data:` fail, and so does `mailto:`, which I can allow if the About page needs it. The variants the check closes, each with a test, are a repeated attribute (a browser uses the first and a parser can keep the last), an HTML comment or declaration (a parser and a browser can end it in different places, so a built page holds none), a script end tag with extra characters, an unclosed `<title>` (a browser reads the rest of the page as its text, which removes the policy tag), a `referrerpolicy` attribute that overrides the page's, and CSS that uses escapes, an import or a data address. A stylesheet is scanned as raw text, so a comment that mentions an outside address is reported, which is a harmless false positive.

The threat model is my own mistakes, not deliberate evasion. Only I edit the templates, so the failures to catch are an accidental font link, an inline handler, a wrong attribute or a third-party script. The check is not a defence against someone who writes a page to hide code from it: HTML read by a different parser than the browser's cannot promise that. The page policy is the second layer, since a browser enforces it whatever the checker saw. Script files are not scanned yet, because the site has none; the policy's `connect-src 'self'` is what limits a script's requests until one exists.

The referrer policy is `no-referrer`. The page links out to ASX and company documents, and I see no reason for those sites to learn which page sent a visitor. The alternative, the browser default of sending the origin only, would reveal the address of my site to each document host, which gains me nothing.

`site/static/site.css` holds no raw size: the page width, the line weights and the underline offset are tokens in `tokens.css`, which I added with this task.

The full check now sets `PYTHONPATH=src` for every step, because the build step runs the package as a module. Pages use relative addresses (`static/tokens.css`), so the same files work at the GitHub Pages project address and from a local folder.

A headless browser here will not lay a page out narrower than 500 px, so `scripts/screenshot.py` shows the page in an iframe of the target width, inside a wrapper page, and writes build/screenshots/ at 390, 768, 1280 and 1440 px. It uses the Chrome or Edge already installed and installs nothing. The page inside lays out at 390 px, which I confirmed by reading the 390 px screenshot.

## 12 October 2026: how the football field is drawn (tasks P5-04 and P5-04b)

Python decides every position and label in `src/valuation/football_field.py`, from the five rows of `valuation.json` `football_field`, and the template only writes them out, so no figure is typed into the page. The chart is an inline SVG with percentage x coordinates and no `viewBox`. In Chrome the percentages resolve as I expected: bars stretch with the page, while text, the hatch angle and line weights keep their size. I have not looked at it in Safari or Firefox, and the fallback in the task (a `viewBox` with non-scaling strokes) is not needed so far.

The axis runs from the lowest value less A$0.25 to the highest value plus A$0.25, each rounded outwards to a multiple of A$0.50, and includes the offer and the undisturbed price. On these inputs it is A$2.50 to A$6.00. Ticks fall every A$0.50, and the half-dollar ticks and gridlines are hidden below 40rem, which leaves one every A$1.00 on a phone. The axis is written above the first row and again below the last, so a row is never read without a scale. That departs from the proposed default of repeating it above every second row; the chart is five rows, so two copies are enough.

Rows use short labels (`Discounted cash flow`, `Trading comparables`) and the data table uses the long ones, which name the EBITDA multiple. The preferred value is a tick on the bar and a column in the table, and not a printed number on the chart, because a third label on a 358 px row collides with the row name. Text sits on a surface-coloured halo (`--chart-halo`, 8 px) and the two reference lines are drawn first, so a line breaks around a figure and does not run through its digits. A 4 px halo left the line visible between digits at 2x zoom, so I made it wider. At 390 px four end labels (4.26, 4.57, 3.33 and 3.47) still sit on a reference line, which the halo masks. My research note (docs/DESIGN_RESEARCH.md) asks for the offer line to stay clear of end labels, and moving those labels would put them inside a bar or in the row label, so I left them and listed the choice for P5-01.

The offer line reads "Offer A$4.43 (deed signed 9 May 2025)" and the undisturbed line "Undisturbed price A$3.12 (20 February 2025)", each with the `as_at` of its input. 9 May 2025 is when Domain signed the scheme implementation deed at A$4.43 (a verified row of data/extracted/deal_timeline.csv); A$4.43 was first offered on 27 March 2025, so the label says what the date is. Each label and each table cell carries a `data-key` naming its key in `valuation.json`, which the site consistency test (P5-15) will read.

## 12 October 2026: the valuation page (tasks P5-08, P5-09 and P5-10)

`valuation.html` holds the DCF assumptions, the free cash flow forecast, the DCF value by case, the sensitivity grid, and the trading and precedent tables. The forecast, the DCF value, the grid and the selected ranges are read from `valuation.json`. The peer and deal multiples are the expert's printed values from `data/extracted/`, with their summary rows (lowest, median, highest) worked out by the page builder from those tables. The assumptions come from `assumptions.yaml`, each with its document, page and date, so the page shows the source beside the figure.

Each table is in its own scroll container that takes the keyboard (`tabindex="0"`, a region role and a label) and holds its first column in place, so at 390 px a wide table scrolls sideways under its row labels. Figures do not wrap, so a number is never split across lines; a row label may wrap. The base case in the grid is boxed with a 2 px accent inset line and a heavier weight and is not shaded, so it does not read as a heat map and does not depend on colour alone. The grid's caption states that only the discount rate and terminal growth vary. The keyboard scroll test for P5-10 needs a browser driver, so that task stays open; the page test checks that each container can take focus.

I added `comparable_peer_set` to the tables the engine loads, because the page shows each peer's treatment (kept or not). The deals marked as unsuccessful proposals are shown as such in the status column, as the expert's chart marks them. Where the completed-deals-only figure of A$4.07 appears is not decided; it is not on this page.

## 17 October 2026: the deal docket and the colophon (task P5-21)

Every page has a labelled list under its title (target, acquirer, consideration, implementation date) and a colophon in the footer (valuation date, the date of my market data, the build date and the commit, then the unit note and the disclaimer). `src/valuation/site_frame.py` builds both. The target, the valuation date and the offer come from `valuation.json`. The implementation date is the one timeline row that says the scheme was implemented (27 August 2025, `data/extracted/deal_timeline.csv`), and the acquirer is a constant that cites the booklet and the 27 March 2025 timeline row.

I added `data_date` to the `meta` block of `valuation.json`. It is the as-at date of the risk-free rate (30 May 2025), and a test checks that it equals the as-at date of the peer multiples and of the RBA table, because the three are one date. The undisturbed price date (20 February 2025) stays on the chart's label, and I did not use it as the data date, because it dates one price and not the market data.

The build date is the day the build ran and the commit is the one HEAD points at. I read it from the git folder (a branch file, `packed-refs` or a detached head) and not by running git, so the build starts no other program and the code needs no exception to the lint rule on subprocess calls. A commit taken before the commit that carries the build is the one shown, which is accurate for a deploy from a green main.

The consideration reads "A$4.43 cash a share, less any special dividend", which is how the deed and the timeline row of 9 May 2025 state it. The special dividend of 8.8 cents is not subtracted anywhere on the page, because the offer price input is the headline price.

## 17 October 2026: the deal timeline page (task P5-12)

`timeline.html` lists the 30 rows of `data/extracted/deal_timeline.csv` in date order: the date, the event, the source as a link with its page, and either "Checked against the source" or "Not checked" with the reason from the row. The summary line counts the checked rows (29 of 30; the 28 April 2025 row is unverified because its announcement returned HTTP 503 when I opened it). I show the evidence column's result and not its wording, because the evidence lines describe how I opened each file and are for my own records.

I used an ordered list and not a table. Each event is a sentence or two and a table cell that does not wrap (my table rule keeps figures on one line) would push the text off a phone screen. The page text is limited to the summary line; any introduction is page copy for P5-19.

The link check on 17 October 2026 was a one-off request to each of the 17 distinct addresses, and it is not part of the build, because the build must pass without a network. Fifteen answered (200, and 206 for the ATO ruling, which refuses a HEAD request). The two SEC addresses returned 403: the SEC blocks anonymous automated requests, and I did not send a made-up identity to get past that. Both rows were opened by hand on 5 October 2026 (evidence column). What the build tests is that every link is an https address equal to the one in the table.

## 17 October 2026: the gap bridge page (task P5-11)

`gap.html` draws the eight steps of `valuation.json` `gap_bridge` as a horizontal bridge, then a table of the same figures, then one section for each step with my explanation from `data/written/gap_step_explanations.csv` printed unchanged, and a table of the inputs in that step (the expert's value and mine). `src/valuation/bridge_page.py` decides every position and label, as the football field module does.

The chart is a price axis from A$3.80 to A$4.40, which does not start at zero, and the page says so. The first mark is the expert's midpoint (ink) and the last is my preferred value (accent), both as lines and not as bars from zero, because a bar from a truncated axis would show a length that means nothing. A step is a bar from the value before it to the value after it, in the two variance colours of DESIGN.md (teal raises my value, orange lowers it) with the sign printed beside it, so colour is never the only cue. A step that is zero at the cent is a short mark labelled 0.00, so the four steps where I kept the expert's value stay on the chart. Thin connectors join each step to the next. The accent stays out of the step bars, as DESIGN.md asks.

The chart's row labels are short (`Forecast`, `Control premium`), and the table and the step headings use the full labels from the engine, because the full forecast label is cut off at 390 px. The chart rows are not links. I first made them links and found that the surface-coloured halo behind each label hides its underline, so a link looked like plain text. The table's first column carries an underlined link to each step.

The rounded steps do not add up to the rounded total: they sum to the figure in the note under the table (A$0.04 down) while the total change from the midpoint is A$0.05 down, because each step is rounded to the cent on its own. The note states both numbers, taken from the engine. The 0.0003 reconstruction difference is its own row in the table and is not a step.

The A$4.07 completed-deals figure is not on this page. Where it goes is still open (P5-13 and P5-19).

## 17 October 2026: the site consistency check (task P5-15)

`src/valuation/site_consistency.py` runs at the end of every site build, so the full check fails if a page disagrees with the engine. It has three rules. First, a template holds no typed figure: digits in a template's own text or in an expression that writes text are errors, with fiscal year labels such as FY26 as the one allowed form. Second, a figure that names its origin (`data-key`, `data-input`, `data-forecast` or `data-bridge`) must equal that value in `valuation.json` or `assumptions.yaml` at the precision the page shows. Third, every other number in the visible text must appear somewhere in the evidence: the numbers in `valuation.json` rounded to up to four places, the text of the inputs and tables, the timeline, and the lowest, median and highest multiples that the page works out from the peer and deal tables.

The third rule is a net and not a proof. A changed figure that happens to equal another number in the evidence passes it, and a test records that (16.3 swapped for 19.9 in the peer table). The figures that matter most carry an attribute and are held to the second rule. I left two things out of the third rule on purpose: the scale marks on a chart axis, whose positions the chart tests check, and the commit hash in the footer.

The first run of the third rule found a real case. The rounding note on the gap page quoted the sum of the rounded steps (A$0.04) as plain text, and no source holds that number. I made the note a sentence in the template with two tagged figures, the sum of the rounded steps and the total change, and the check recalculates the sum from the steps. I also changed the wording of the note from "before rounding to the cent" to "rounded once", because the total is rounded once and not "before" rounding.

The planted-change tests change one figure in a copy of the built pages, as a typo in a template would, and check that the right problem is reported: a valuation figure, a forecast figure, an input, a bridge figure, a chart label, a flag, a key that names nothing, an untagged number, a date on the timeline and a number in the chart's text alternative. A typed figure in a template is tested in five forms, and seven forms that must pass are tested too (year labels, layout numbers in attributes, a comment, a condition).

## 17 October 2026: the method and sources page, register only (task P5-13)

`method.html` shows the register: all 80 entries of `assumptions.yaml` in the order of the file, each with its value, unit, document, page or table, date, a marker where the input is my judgement (26 of them) and the entry's note, unchanged. A test reads the built page and compares each row with the entry, so a register row cannot drift from the file. The value is written with up to four decimal places and no trailing zeros, because the inputs run from 0.5 years to 4.249% and a fixed number of places would either round an input or pad the others. Input names are the file's own keys, and the first column may break a name anywhere (`overflow-wrap: anywhere`), so that it does not take the width of a phone. I first used `<wbr>` to break after each _, which reads better, but it needed a new element on the site checker's allow-list, and I do not loosen that list for a cosmetic gain.

I did not add a limitations section. The list I keep of things I could not verify (docs/RESEARCH.md) names internal tasks and a page-fetch tool in its next-step column, and which limits to state publicly, and in what words, is the page copy I write in P5-19. The disclaimer is in the footer of every page, as on the other pages. P5-13 therefore stays open until the limitations are written.

The consistency check (P5-15) found two unsourced counts while I built this page: the number of inputs and the number marked as my judgement. I added a fifth origin, `data-count`, for counts the pages quote, and a count is checked against the file (inputs, judgement inputs) or the timeline (events, events checked). The timeline's "29 of 30" had passed the untagged rule only because 29 and 30 appear in dates elsewhere, so I tagged it too, and a test changes it to 28 and expects a failure.

## 17 October 2026: Playwright for browser tests (task P5-10)

I approved a browser driver on 17 October 2026 for the keyboard scroll test (P5-10) and for the accessibility checks (P5-16). I chose Playwright for Python at version 1.63.0, released on 15 September 2026, and not the newest release (1.64.0 came out on 13 October 2026), because I pin to a release that has been public for more than two weeks. Its licence is Apache-2.0. It is a development dependency in `pyproject.toml`, and regenerating `requirements.lock` added three packages and changed no other: playwright, its dependency pyee (13.0.1) and greenlet (3.5.6). `pip-audit` reports no known vulnerabilities on the new lock file. The alternatives were Selenium, which needs a separate driver program for each browser version, and a short script against Chrome's debugging port, which I would have to write and maintain myself.

Playwright downloads its own browsers by default. I do not run that download. The tests start the Chrome that is already installed (`channel="chrome"`), so nothing outside the Python packages is installed. The cost is that the tests need Chrome on any machine that runs them. The GitHub Actions runner image for ubuntu-24.04 lists Google Chrome, but I have not seen CI run these tests yet (UNVERIFIED until the next push finishes).

`tests/engine/test_table_scroll.py` opens the valuation page at 390 px, presses Tab until a wide table's scroll region has the focus, presses the right arrow key and checks that the region scrolled, that its first column stayed at the region's left edge while the last column moved, and that every scroll region on the page can be reached by keyboard and shows a focus outline. Playwright's `wait_for_function` evaluates a string, which the page's own security policy blocks, so the test polls the scroll position from Python until two reads agree; the block is also a sign that the policy works. I confirmed the test can fail: with the sticky column switched off, and separately with the container's overflow switched off, it failed (3 and 6 of 7 tests).

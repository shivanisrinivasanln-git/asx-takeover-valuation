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

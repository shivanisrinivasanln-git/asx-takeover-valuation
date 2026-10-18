# Notes on the Excel model

What each sheet of `model/domain_valuation_model.xlsx` does and why its formulas are right. Page numbers are booklet pages of the Grant Samuel report in the Domain scheme booklet. The workbook is built by `scripts/build_model.py` from the same inputs as the engine, and a test reads Excel's own calculated values and compares all 134 named output cells with `valuation.json` ([DECISIONS.md](DECISIONS.md), 12 October 2026). Each formula row also carries a one-line note in its last column.

## How the five sheets fit together

Inputs are only on the Assumptions sheet, each under an Excel defined name equal to its input name in `assumptions.yaml`, so a formula reads `=tax_rate_pct` and never a cell address on another sheet. The DCF, Comparables and Precedents sheets calculate a value per share. The Summary sheet combines them with my weights. Every output cell has a defined name equal to its key in `valuation.json`, which is how the tests find it. A test fails if a formula has a typed-in number other than 0, 1, 2 or 100 (a unit conversion, a step of one year or an average of two), if a formula addresses another sheet by cell, or if a formula uses a function outside IF, INDEX, SUM, SUMPRODUCT, MIN, MEDIAN and MAX.

## Assumptions

The sheet lists 89 rows: 80 inputs from `assumptions.yaml`, 8 values copied from the transcribed tables in `data/extracted/` (FY24 revenue, three first-half FY25 figures (revenue of A$217.2m, EBITDA of A$77.8m, and depreciation and other amortisation), and the expert's printed business operations value and value per share at each end), and one model structure row, the five early years of the forecast. Each row has the value, unit, source, page, date, a marker for my own judgement (26 rows) and a note. I keep the transcribed values here so that no formula needs to read a CSV file.

Why it is right: a test compares every row with the file or table it came from (value, unit, source, page, date, note and judgement flag), and the source trace test fails if an input has no source.

## DCF

The sheet follows the engine's `forecast.py`, `dcf.py`, `bridge.py` and `sensitivity.py` line by line, in four blocks.

**Forecast, rows 5 to 23, columns C to M.** Column C is the second half of FY25 (the stub, 1 January to 30 June 2025, p. 137) and columns D to M are FY26 to FY35. Each row is one line of the free cash flow.

| Row | Formula idea | Why it is right |
|---|---|---|
| 8 Full-year revenue | FY25 broker median of A$420.0m, then grown at 9.0% a year | Median of 13 brokers (pp. 122 and 165); the expert's growth is "just over 9%" (p. 141), which I take as 9.0% |
| 10 Revenue in the period | Stub revenue is the FY25 forecast less the first half reported | The first half of A$217.2m is reported (p. 118), so the stub is the remainder |
| 11 EBITDA margin | A straight line from the FY25 margin to 41% in FY30, then to 47.9% in FY35 | The end points are the expert's (p. 142); the straight line is my choice between them (DECISIONS.md, 5 and 6 October 2026) |
| 13 Corporate cost saving | A$4.0m a year, times the fraction of the year in row 7 | The saving the expert says any acquirer makes (p. 143); it is part of taxable profit |
| 14 to 15 Depreciation | A straight line from the FY25 share of revenue to 9.0% | The expert says depreciation roughly equals capital expenditure after the early years (p. 142); the path is my choice |
| 16 to 17 Tax | 30% of EBITDA plus the corporate cost saving, less depreciation | The rate is the expert's (p. 142); the booklet does not say whether acquired intangibles are deductible, so I take no deduction (DECISIONS.md, 6 October 2026) |
| 18 to 19 Capital expenditure | 9.6% of revenue for the stub and FY26 to FY30, then 9.0% | The expert gives almost 9.5% over the projection and "higher in the early years" and 9.0% long term (p. 142); 9.6% is the 1HY25 level (p. 125), my choice |
| 20 Increase in working capital | 2.5% of the change in full-year revenue, times the fraction of the year in row 7 (a half in the stub) | The expert's 2.5% (p. 142) |
| 21 Dividends to agents | 1.6% of the prior year's revenue of the segments the agents hold equity in (82.1% of revenue), times the fraction of the year in row 7 | The expert deducts them from cash flow to shareholders (pp. 136, 137 and 142) |
| 22 Free cash flow | Taxable profit less tax, plus depreciation, less capital expenditure, working capital and agents' dividends | The standard unlevered free cash flow; the engine computes the same number and the test compares them |
| 23 Years from the valuation date | The stub counts a quarter of a year, and each later year counts from the middle of the year | Mid-year timing is my choice; the booklet is silent (DECISIONS.md, 6 October 2026) and setting `mid_year_discounting_flag` to 0 gives year end |

**Value at three discount rates, rows 28 to 41, columns C to E.** The low case discounts at the top of my range (10.5%) and uses the larger of the two diluted share counts, the mid case uses 10.0% and the average, and the high case uses 9.5% and the smaller count. The expert pairs them the same way (p. 131). The present value of the cash flows is each free cash flow divided by one plus the rate, to the power of its time (row 30). The terminal value (row 31) is the FY36 cash flow over the rate less the growth rate, multiplied by one plus the rate to the power 0.5 under mid-year timing, because the Gordon formula assumes year-end flows. Discounting from the end of FY35 (row 32) is 10.5 years: the stub plus ten full years (p. 137). Operations value plus other assets and liabilities is the enterprise value; less adjusted net debt (A$187.0m, pp. 131 and 156) it is the equity value; over diluted shares (p. 131) it is the value per share. With the expert's own business operations value of A$2,775m and A$3,025m the same bridge gives A$4.06 and A$4.46 a share (test in `test_bridge.py`).

**Terminal year, rows 45 to 54.** Revenue grows at the terminal growth rate (4.0%, p. 142), the last margin is held, depreciation and capital expenditure take their long-term shares of revenue, and working capital takes the smaller revenue increase. This is the cash flow the terminal value grows from.

**Sensitivity grid, rows 59 to 77.** Each of the 25 cells is a full recalculation at that discount rate and terminal growth, not an interpolation: the present value of the cash flows at the row's rate is in column H, and the terminal year is worked out again for each growth rate in rows 61 to 70. The middle cell equals the mid case value per share in D41, which a test checks.

**Discount rate builds, rows 81 to 98.** CAPM at my risk-free rate (4.249%, RBA, 30 May 2025) and at the expert's (4.3%, p. 139). Cost of equity is the risk-free rate plus beta times the 6.0% premium; the cost of debt is the risk-free rate plus 1.2 points, taxed at 30%; the weights are 85% to 95% equity. With the expert's inputs the build gives 9.33% to 10.55%, which rounds to its printed 9.3% to 10.5% (p. 140). My adopted range of 9.5% to 10.5% is an input and not this build.

## Comparables and Precedents

Both sheets multiply FY26 adjusted EBITDA of A$152.2m (pp. 136 and 153) by the low, mid and high ends of my selected multiple range, then run the same bridge as the DCF sheet and read net debt and the share counts from the DCF sheet by name, so the three methods cannot disagree on them. A second block does the same on EBITA, which is shown and not used in the weights. The mid case is the midpoint of the two multiples (row 6, `=(C6+E6)/2`) on the average share count.

The Comparables sheet applies my control premium of 25% to enterprise value (row 8, `=control_premium_applied_pct`) because peer multiples come from minority share prices. The Precedents sheet has a typed 0 there because deal multiples are control multiples. Why the premium applies at enterprise value level and the evidence for 25% are in [BASE_CASE.md](BASE_CASE.md).

Below each value block I copied the expert's printed multiples with their pages (8 peers on p. 150, 9 deals on pp. 146 and 147), with the lowest, median and highest of each column as formulas. These tables are evidence for choosing my ranges and are not used in the value, which each sheet says. A test compares them with the transcribed CSV rows.

## Summary

The top table shows low, high and preferred value per share for each method, my combined range and the expert's printed range, the same rows as the football field in `valuation.json`. The combination block below it multiplies each method's value by its weight (50%, 25% and 25%, my inputs) and divides by 100, separately for the low, high and preferred columns, and the weights column totals 100. The preferred value is the weighted mid case, so it is not a midpoint of the combined range. The sheet also holds the offer, the undisturbed price, the offer premium of 42.0% (A$4.43 over A$3.12, p. 157), my midpoint of the expert's range, and the discount rate range beside the two WACC builds.

Why it is right: every cell is a formula on a defined name, the weighting is checked against a hand example in the engine (`test_combine.py`), and the Excel-calculated preferred value is A$4.2124 against the engine's, with a worst difference across all 134 named cells of 2.6e-16.

## What the model does not do

- The gap bridge is calculated by the engine and is in `valuation.json`, not in the workbook, because each step is a full recalculation with one group of inputs swapped (DECISIONS.md, 12 October 2026).
- Excel calculated the stored values, so a function that another spreadsheet program reads differently would not be caught by the test (DECISIONS.md, 12 October 2026).

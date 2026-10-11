# Cross-check against the expert's scenario A

I ran my engine on the inputs of Grant Samuel's scenario A and compared it with the value it shows for that scenario. This tests my DCF mechanics (the forecast, the timing, the terminal value) against a figure I did not choose. On 12 October 2026 I kept the expert's forecast, discount rate range and terminal growth (docs/BASE_CASE.md), so my DCF inputs currently equal scenario A's and the engine values below are also my own DCF's business operations values at the ends of my range. Only my multiples, control premium and method weights differ from the expert's. Page numbers are booklet pages.

## What I compared

The expert printed the inputs of scenario A (pp. 141 to 143) and showed its value of business operations at 9.5% and 10.5% only as a bar on a chart (p. 144), with no number. I read the two bar ends from the chart's vector rectangles and checked the reading against the printed value range box (`data/extracted/dcf_npv_chart_reads.csv`). The reading is good to about plus or minus A$5m.

The engine side uses the `expert_` inputs in `assumptions.yaml`, which hold the expert's value of each input I can change, so the check stays a test of scenario A if I later change my own DCF inputs. Scenario A has growth of 9.0% (p. 141), FY30 and FY35 margins of 41% and just below 48% (p. 142), capital expenditure of almost 9.5% of revenue (p. 142), terminal growth of 4.0% (p. 142), and discount rates of 9.5% and 10.5% (pp. 138 and 140). The test is `tests/engine/test_cross_check.py` and the code is `src/valuation/cross_check.py`.

## Result

| Discount rate | Convention | My engine (A$m) | The expert's bar, read (A$m) | Difference (A$m) | Difference (%) |
|---|---|---|---|---|---|
| 10.5% | Mid-year | 2,401.1 | 2,402 | -0.9 | -0.04 |
| 9.5% | Mid-year | 2,897.6 | 2,893 | +4.6 | +0.16 |
| 10.5% | Year end | 2,284.9 | 2,402 | -117.1 | -4.88 |
| 9.5% | Year end | 2,769.7 | 2,893 | -123.3 | -4.26 |

## What the difference means

Mid-year discounting lands within the reading precision of both bar ends. Year end is about A$120m (4% to 5%) below both ends, far outside it. So either the expert discounted mid-year, or it used year end and something else in its model offsets A$120m. The booklet does not state its convention (p. 137), so which is UNVERIFIED. I chose mid-year on 6 October 2026, before I ran this comparison, because it fits how Domain earns cash (docs/DECISIONS.md), and I did not change any modelling choice to close the gap.

The A$4.6m gap at 9.5% and A$0.9m gap at 10.5% are within what I cannot pin down. The expert published no cash flows, so I cannot split the residual by line. The expert also describes several inputs in words ("just over 9%", "just below 48%", "higher in the early years"), and I chose the numbers. Changing one of those choices by a rounding-size amount on the expert's inputs moves the value by more than the residual, as the engine shows (A$m at 10.5% and 9.5%; the change column is worked from the unrounded engine values and can differ by 0.1 from subtracting the cells shown):

| Change to one input on the expert's inputs | Value at 10.5% | Value at 9.5% | Change at 10.5% and 9.5% |
|---|---|---|---|
| None | 2,401.1 | 2,897.6 | |
| Growth 9.1% instead of 9.0% | 2,419.4 | 2,920.3 | +18.3 and +22.7 |
| FY35 margin 47.5% instead of 47.9% | 2,381.5 | 2,872.9 | -19.5 and -24.6 |
| Capital expenditure FY26 to FY30 10.0% instead of 9.6% | 2,392.2 | 2,888.5 | -8.9 and -9.1 |

My capital expenditure path averages 9.3% over the projection against the expert's "almost 9.5%" (p. 142), which I noted on 5 October 2026 and cannot place by year (UNVERIFIED). The gap has the sign that a lower capital expenditure on my side would give at 9.5%, but not at 10.5%, so I do not claim it as the cause.

## What this does not show

- It validates the mechanics of the DCF on one scenario. Because my DCF inputs equal scenario A's, it also checks my DCF's business operations value, but not my value per share: the multiples, the premium and the weights are outside it, and scenario NPVs are not printed as numbers, so I have no per-share figure from the expert to compare.
- The expert's selected range of A$2,775m to A$3,025m sits above scenario A's bar. Its own words are that the range is "a subjective balancing of the scenarios" (p. 144), with the multiples as evidence (p. 135), so scenario A alone is not the expert's value.
- The chart reading itself carries about A$5m of uncertainty, so a difference of that size is not a finding.

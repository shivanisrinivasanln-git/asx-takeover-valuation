# My base case

The inputs I chose on 12 October 2026 for my valuation of Domain, each with the evidence I weighed and the range I tested. Page numbers are booklet pages of the Grant Samuel report (printed page N is PDF page N+3). Values per share come from my engine at a 10.0% discount rate and 4.0% terminal growth with mid-year discounting, unless a row says otherwise, and the engine is in `src/valuation/`. The reasons for the choices are in [DECISIONS.md](DECISIONS.md), and every input is in [assumptions.yaml](../assumptions.yaml) with its source.

The common thread is that I start from the expert's disclosed inputs and change one only where I have evidence of my own. For the forecasts, the discount rate and terminal growth I found no document that sets a better number, so I kept the expert's. For the multiple ranges the expert's published figure is its own conclusion, so I chose ranges from the peers and deals it printed.

## Forecasts (task P4-01)

| Input | My value | Source | Range I tested (value per share) |
|---|---|---|---|
| Revenue growth FY26 to FY35 | 9.0% a year | Total revenue "just over 9% a year", over A$990m in FY35 (p. 141) | 8.0% A$3.53, 8.5% A$3.68, 9.5% A$3.99 |
| EBITDA margin FY30 | 41% | p. 142 | 38% A$3.77, 39% A$3.79 |
| EBITDA margin FY35 | 47.9% | "Just below 48%" (p. 142); my reading of the words | 44% A$3.50, 46% A$3.67 (the expert's Scenario C, p. 143) |
| Capital expenditure FY26 to FY30 | 9.6% of revenue | "Almost 9.5%" over the period, higher early (p. 142); my reading | 9.0% A$3.85, 10.0% A$3.82 |
| Capital expenditure long term | 9.0% of revenue | p. 142 | 10.0% A$3.70 (the expert's Scenario G, p. 143) |
| Working capital | 2.5% of the change in revenue | p. 142 | 0% A$3.86, 5.0% A$3.81 |

Revenue growth moves the value most: about A$0.15 a share for each half point. The evidence for a lower rate is the broker medians, which imply growth of 7.4% in FY25 (A$391.1m to A$420.0m) and 8.0% in FY26 (to A$453.8m) (p. 118 and p. 165). Revenue grew at 10.5% a year from FY21 to FY24 (A$289.6m to A$391.1m, p. 118), so history points the other way. The brokers cover two years and the expert states a ten-year average, so I kept 9.0%.

Domain's EBITDA margin was 34.7%, 35.9%, 31.4% and 35.1% from FY21 to FY24 (p. 118, my division) and 35.8% in 1HY25 (p. 142). The expert says its path to 41% and almost 48% is above that history and points to REA Group's 63% to 65% as evidence that higher margins are possible in the sector (p. 142). Each margin point in FY35 is worth about A$0.08 a share. The path is above anything Domain has reported, so I inherit this assumption from the expert and cannot support it from Domain's own history. I kept it so that my differences from the expert appear in the discount rate and the multiples, and I show 46% as the downside.

## Discount rate (task P4-02)

I use the expert's adopted range of 9.5% to 10.5% (pp. 138 and 140), with the middle, 10.0%, as the base. My build from the inputs gives 9.28% to 10.50% at my risk-free rate of 4.249%, and 9.33% to 10.55% at the expert's 4.3% (p. 139).

| Input | My value | Source |
|---|---|---|
| Risk-free rate | 4.249% | RBA 10-year yield at 30 May 2025 (docs/DECISIONS.md, 5 October 2026) |
| Market risk premium | 6.0% | The expert's rate; analysts typically use 5% to 7% (p. 139) |
| Equity beta | 1.0 to 1.1 | The expert's judgement (pp. 139 and 140) |
| Equity weight | 85% to 95% | Gearing of comparable listed companies over four years (p. 140) |
| Debt margin over risk-free | 1.2% | p. 140 |

The evidence for a lower rate is that brokers use 8.4% to 9.0%, median 8.5% (p. 140), and that Barra's predicted beta for Domain is 0.8 to 0.9 (p. 139). Against it, SIRCA's four-year beta for Domain is about 1.4 to 2.1 and 1.4 at 31 December 2024 (p. 139), and the evidence the expert weighed runs from about 0.3 to 2.1. A beta of 0.9 with 85% equity gives a discount rate of 8.77%, which would put my DCF high value at A$5.04, above the A$4.43 offer, so I did not take it on the strength of one estimate. A premium of 5.0% or 7.0% moves the build to 8.43% to 9.45% or 10.13% to 11.54%.

Value per share by discount rate, with 4.0% growth: 8.5% A$5.39, 9.0% A$4.77, 9.5% A$4.26, 10.0% A$3.83, 10.5% A$3.47, 11.0% A$3.17. This is the largest driver of my DCF.

## Terminal growth (task P4-03)

I use 4.0%, the expert's rate, which it builds from long-term inflation of 2.5% a year plus real growth in EBITDA (p. 142). Two thirds of my DCF value, 66%, comes after FY35, so the rate matters: 2.5% gives A$3.26, 3.0% A$3.42, 3.5% A$3.61, 4.0% A$3.83 and 4.5% A$4.09 a share.

The terminal value at 4.0% is 9.9x FY35 EBITDA of A$476.3m, about half the 18.2x to 19.9x FY26 multiples the expert applies today (p. 153). Lower growth lowers that multiple further (8.4x at 3.0%, 7.8x at 2.5%), which argues against calling 4.0% aggressive. The only other report in docs/RESEARCH.md that gives a terminal growth rate, Grant Thornton on RPMGlobal (2025), used 3.0% for a different business (section 2), so it is a reference point and not a like-for-like.

## Multiple ranges (task P4-04)

The multiples apply to FY26 adjusted EBITDA of A$152.2m (p. 136 and p. 153). The expert's implied 18.2x to 19.9x is the output of its own range (p. 153), so I did not use it as evidence.

| Method | My range | How I chose it | Value per share, before any premium |
|---|---|---|---|
| Trading comparables | 16.3x to 19.1x | SEEK's and Rightmove's forecast EBITDA multiples at 30 May 2025 (p. 150), the two lowest of the eight peers | A$3.60 to A$4.28 |
| Precedent transactions | 15.2x to 22.3x | The six deals with a forecast EBITDA multiple (pp. 146 and 147), less the highest (ZPG, 25.1x) and the lowest (58.com, 12.9x) | A$3.33 to A$5.04 |

The eight peers' forecast EBITDA multiples are SEEK 16.3x, Rightmove 19.1x, Scout24 22.2x, CAR Group 22.8x, Vend 27.2x, Hemnet 30.5x, Baltic 32.0x and REA 32.6x. I take the low end because Domain is the number two portal in its market and its EBITDA margin of 35.8% sits far below REA's 63% to 65% (p. 142). The expert keeps SEEK (employment) and CAR Group (automotive) with caution as less comparable than the property marketplaces (pp. 140 and 151), so the bottom of my range is the multiple of a peer it treats as a weaker guide, and Rightmove is the lowest property marketplace. The expert itself quotes SEEK and CAR Group at 16x to 22x forecast EBITDA (p. 151). The deal multiples are 58.com 12.9x, Trade Me 15.2x, Adevinta 17.7x, Scout24 19.7x, the Rightmove proposal 22.3x and ZPG 25.1x, and their median is 18.7x. They are Grant Samuel's printed chart labels, and I have not checked them against primary sources.

For EBITA I used the same two peers for trading, which gives 19.4x to 23.8x (Rightmove 19.4x and SEEK 23.8x, so the order reverses). They are not the two lowest on EBITA, because CAR Group's 23.1x is second lowest. For precedents I used the same trimming rule, which gives 17.9x to 25.8x. The football field uses EBITDA.

Two of the four deals inside my precedent range, Scout24 (19.7x, 2019) and Rightmove (22.3x, 2024), were unsuccessful proposals, which the expert keeps and shows hatched as benchmarks (pp. 147 and 148). I had not noticed this when I chose the range on 12 October 2026. On completed deals only, with the same rule of dropping the highest and the lowest, the range is 15.2x to 17.7x (Trade Me and Adevinta), my preferred value A$4.07 and my range A$3.71 to A$4.47. I kept the base range and show this as a second figure (`sensitivities` in valuation.json).

## Control premium (task P4-05)

I apply 25% to the trading method only, at enterprise value level, because peer multiples come from minority share prices and deal multiples already include control. Without a premium the trading range (A$3.60 to A$4.28) is not comparable with a control offer of A$4.43.

The evidence is in two forms. On the share price, the RSM and Curtin study of 605 ASX takeovers from 2005 to 2020 found an average premium of 34.7% and a median of 27.5% (RSM p. 4), schemes averaging 32.1% (p. 10) and targets above A$500m averaging 20.8% (p. 11). Lonergan Edwards puts the average at 30% to 35% over the undisturbed price, which it says is about 20% to 25% at enterprise value level (Bigtincan scheme booklet, pp. 187 to 188). Grant Samuel says premiums of 20% to 35% are typical and that they are an outcome, not a determinant, of value (pp. 133 and 158). The offer was 42.0% above the undisturbed price (A$4.43 against A$3.12, p. 157).

My engine applies the premium to enterprise value. At the undisturbed price Domain's equity was about A$1,973m and its adjusted net debt A$187.0m, 8.7% of enterprise value, so a 25% enterprise value premium equals about a 27.4% premium on the share price, close to the RSM median. With 25% the trading range is A$4.57 to A$5.42. At 20% it would be A$4.38 to A$5.19, and at 30% A$4.77 to A$5.65.

## Method weights and my preferred value (task P4-06)

Each method has a low, a middle and a high value per share. The middle is the midpoint of the multiple range for trading and precedents, and the middle discount rate (10.0%) for the DCF. In all three the middle uses the average of the two diluted share counts.

| Method | Low | Middle | High | What sets the ends |
|---|---|---|---|---|
| DCF | A$3.47 | A$3.83 | A$4.26 | Discount rate 10.5%, 10.0% and 9.5% at 4.0% terminal growth |
| Trading comparables | A$4.57 | A$5.00 | A$5.42 | 16.3x, 17.7x and 19.1x FY26 adjusted EBITDA with the 25% premium |
| Precedent transactions | A$3.33 | A$4.19 | A$5.04 | 15.2x, 18.75x and 22.3x FY26 adjusted EBITDA |

The bars do not all overlap: the top of the DCF (A$4.26) is below the bottom of trading (A$4.57). The expert gave both methods weight, used neither as a cross-check, and says its range cannot be reduced to a weighting calculation (p. 135), so there is no weighting to copy and the weights are my judgement.

I weight the DCF 50%, trading comparables 25% and precedent transactions 25%. For comparison, equal thirds give A$3.79, A$4.34 and A$4.91 (low, middle, high), 40/30/30 gives A$3.76, A$4.29 and A$4.84, and the DCF alone gives A$3.47, A$3.83 and A$4.26. With 50/25/25 my preferred value is the weighted middle values, A$4.21, and my range is the weighted low values and the weighted high values, A$3.71 to A$4.75.

Two things to keep in mind when I explain this. The range is the weighted sum of each method's low end and each method's high end, so it is the range if every method comes in low together or high together, and it is wider than a range that treats the methods as independent. And the offer of A$4.43 is inside my range and A$0.22 above my preferred value, while the expert's midpoint of A$4.26 (a midpoint of its printed A$4.06 to A$4.46 and not a figure it published) is A$0.05 above it.

## What I could not verify

- The expert's reasons for starting its adopted range at 9.5% when its calculation gives 9.3% (p. 140).
- Whether the expert discounted mid-year or at year end (p. 137). I chose mid-year (docs/DECISIONS.md, 6 October 2026).
- The deal multiples against their primary sources, and the forecast year each peer multiple refers to. The peer multiples are Grant Samuel's printed labels.

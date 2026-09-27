# Research

The sourced findings behind my valuation. Every factual claim carries a link and an access date. Anything that could not be checked against a source is marked UNVERIFIED. Page references use the printed page number in a scheme booklet ("booklet p.") unless marked "PDF p.", which is the page of the downloaded file.

This file covers how Australian independent expert's reports work. Findings on data sources, architecture and design will be added as those items are researched.

## IERs and valuation methods in 10 minutes

A plain-language primer. The numbers in the worked example are invented for teaching and do not describe any real company.

### What an IER is for

When a company agrees to be taken over, its shareholders vote on a scheme of arrangement or decide whether to accept a takeover bid. They usually get an Independent Expert's Report (IER): a valuation of the company by a licensed firm with no stake in the outcome, and an opinion on whether the offer is good enough. Some reports are required by law, for example when the bidder already holds 30% or more. ASIC notes that targets often commission one even when it is not required (RG 111 Table 1; see section 1).

The expert answers two questions, set by ASIC in Regulatory Guide 111:

1. Is the offer fair? Compare the offer price with the value of the company, where the company is valued as if a buyer were acquiring all of it. A buyer of 100% gets control (it can set strategy, replace the board and take the cash flows), so that value includes a control premium.
2. Is the offer reasonable? An offer that is fair is reasonable. An offer that is not fair can still be reasonable, for example if the share price would probably fall without it and no other bidder is in sight.

For a scheme, "fair and reasonable" becomes "in the best interests of members".

### Why control matters

The share price on the ASX reflects trades in small parcels, which carry no control. It is a minority value. The expert's range is a control value. The gap between the two is the control premium. Australian studies put the average at about 30% to 35% above the price before the deal was announced (see section 4).

### The main methods

- Discounted cash flow (DCF): forecast the free cash flow the business will generate, and discount it to today at the rate investors require (the weighted average cost of capital, WACC). Used when forecasts have a reasonable basis, and for mines with a known life.
- Capitalisation of future maintainable earnings: take the earnings the business can sustain (often EBITDA) and multiply by a multiple drawn from comparable companies and past takeovers. Used for stable, profitable businesses.
- Comparable company multiples: the multiples at which similar listed companies trade. These are minority values, so an expert adjusts them for control.
- Precedent transaction multiples: the multiples paid in past takeovers of similar companies. These already include a control premium.
- Sum of the parts: value each business or asset with the method that suits it, then add them up.
- Quoted market price plus a premium: the undisturbed share price grossed up for control, usually as a cross-check.
- For miners: a DCF of the life-of-mine plan for producing assets, and dollars per tonne or per ounce of resource for undeveloped ones, under the VALMIN Code.

Experts normally use one primary method and at least one cross-check, and must explain why.

### Worked example

Harbour Industrial Ltd (invented) has 100 million shares and A$100m of net debt. It sustains EBITDA of A$50m a year. Its shares traded at A$2.20 before a bidder offered A$3.10 cash.

Step 1, primary method (capitalised earnings). Recent takeovers of similar firms were done at 7.5 to 8.5 times EBITDA.

| | Low | High |
|---|---|---|
| EBITDA (A$m) | 50 | 50 |
| Multiple (control basis) | 7.5x | 8.5x |
| Enterprise value (A$m) | 375 | 425 |
| Less net debt (A$m) | 100 | 100 |
| Equity value (A$m) | 275 | 325 |
| Per share (A$) | 2.75 | 3.25 |

Step 2, cross-check (DCF). Next year's free cash flow is forecast at A$30m, growing 3% a year.

- Cost of equity, from the capital asset pricing model: risk-free rate plus beta times the market risk premium, 4.0% + 1.3 × 6.0% = 11.8%.
- Cost of debt after 30% tax: 7.0% × (1 − 0.30) = 4.9%.
- WACC with 80% equity and 20% debt: 0.8 × 11.8% + 0.2 × 4.9% = 10.4%.
- A cash flow growing for ever at a constant rate is worth cash flow ÷ (WACC − growth): 30 ÷ (0.104 − 0.03) = A$405m of enterprise value, A$305m of equity, or A$3.05 per share. That sits inside the range from step 1.

The result is sensitive to the discount rate. At a WACC of 9.4% the value is 30 ÷ 0.064 = A$469m, or A$3.69 per share; at 11.4% it is 30 ÷ 0.084 = A$357m, or A$2.57 per share. One percentage point either way moves the value by 48 to 63 cents a share, which is why experts publish sensitivity tables.

Step 3, cross-check (market price plus premium). A$2.20 × 1.30 = A$2.86, inside the range.

Step 4, the opinion. The range is A$2.75 to A$3.25. The offer of A$3.10 is above the low end, so it is fair; being fair, it is also reasonable. (Kroll states in its Insignia report that the low end of the range is the threshold for fairness; see section 5.) The offer premium is 3.10 ÷ 2.20 − 1 = 40.9%.

My valuation repeats those steps for a real deal with my own inputs, then explains each gap between my range and the expert's.

## 1. How IERs are regulated

### The two ASIC guides and their current versions

Regulatory Guide 111 *Content of expert reports* (RG 111) is the October 2020 version, issued 22 October 2020. Earlier versions were issued in October 2007 and March 2011. No later version is listed on ASIC's page. Sources: [RG 111 page, ASIC](https://www.asic.gov.au/regulatory-resources/find-a-document/regulatory-guides/rg-111-content-of-expert-reports/) and [RG 111 PDF](https://download.asic.gov.au/media/5827832/rg111-published-22-october-2020.pdf) (both accessed 26 September 2026).

Regulatory Guide 112 *Independence of experts* (RG 112) is still dated 30 March 2011, but ASIC has amended the text in place: in August 2015 (a relief instrument reference), December 2025 (a cover note and simplified wording in RG 112.7 and RG 112.12) and April 2026 (changes to match the updated RG 181 on conflicts of interest). Sources: [RG 112 page, ASIC](https://www.asic.gov.au/regulatory-resources/find-a-document/regulatory-guides/rg-112-independence-of-experts/) and [RG 112 PDF, file dated 21 April 2026](https://download.asic.gov.au/media/dfros4dv/rg112-published-30-march-2011-20260421.pdf) (both accessed 26 September 2026).

Both guides apply to expert reports on transactions under Chapters 2E, 5, 6 and 6A of the Corporations Act, whether the report is required by law or commissioned voluntarily (RG 111.1, RG 112.1).

### When a report is required

- Takeover bids: section 640 requires the target's statement to include an expert's report on whether the offers are "fair and reasonable" where the bidder has voting power of 30% or more in the target, or where the bidder and target share directors ([Takeovers Panel, Summary of takeover provisions](https://takeovers.gov.au/resources/key-concepts/summary-takeover-provisions); RG 111 Table 1; both accessed 26 September 2026).
- Bidders: s636(1)(h)(iii) and s636(2) require a bidder's expert report in a narrow case involving unquoted securities used to buy a pre-bid stake (RG 111 Table 1).
- Schemes of arrangement: regulation 5.1.01 and Schedule 8, clauses 8303 and 8306 of the Corporations Regulations 2001 require an expert's report where the other party holds 30% or more of the voting shares or the parties share directors. The expert states whether the scheme is "in the best interests of the members" (RG 111 Table 1 and RG 111.6(b)).
- Voluntary reports: RG 111 Table 1 notes that targets "often commission expert reports to assist security holders, even if there is no requirement to do so", and that scheme companies often do so when a transaction is complex or effects a takeover. A voluntary report must meet the same content and independence standards (RG 111.1, RG 112.33).

The section numbers above come from ASIC and Takeovers Panel documents. The statute text was not read directly (AustLII and legislation.gov.au blocked automated access on 26 September 2026), so the wording of the sections themselves is UNVERIFIED.

### Fair, reasonable and in the best interests

RG 111 treats "fair" and "reasonable" as two separate tests (RG 111.10).

- Fair: an offer is fair if the value of the consideration is equal to or greater than the value of the target's securities. The target is valued as if 100% of it were being acquired, between a knowledgeable and willing, but not anxious, buyer and seller, whether the consideration is cash or scrip. The expert must not apply a minority discount to the target shares. Special value that only one particular bidder could obtain, such as cost savings from combining two businesses, is left out of the fairness test but may be considered under reasonableness (RG 111.11).
- Reasonable: an offer is reasonable if it is fair, or if there are enough reasons to accept it despite being not fair, in the absence of a higher bid. RG 111.13 lists factors such as the bidder's existing stake, other large holdings, liquidity, the likely share price if the offer fails, and the chance of a rival bid.
- Schemes: for a control scheme ASIC expects "substantially the same" analysis as for a takeover (RG 111.18). Fair and reasonable means in the best interests; not fair but reasonable may still be in the best interests if the report says so clearly; not fair and not reasonable means not in the best interests (RG 111.19 to RG 111.22).
- Scrip offers: the bidder's shares are valued on a minority basis, because target holders receive a minority stake in the combined group, and compared with the target valued on a 100% basis (RG 111.30 and RG 111.31).

Source for this subsection: [RG 111 PDF](https://download.asic.gov.au/media/5827832/rg111-published-22-october-2020.pdf), pages 7 to 13 (accessed 26 September 2026).

What this means for my valuation: the expert's range is a control value. The offer is compared with that range, and the undisturbed share price is a minority value. My range has to be on the same control basis before I can compare it with the expert's.

### What an IER must disclose

From RG 111 and RG 112 ([RG 111 PDF](https://download.asic.gov.au/media/5827832/rg111-published-22-october-2020.pdf), pages 21 to 32; [RG 112 PDF](https://download.asic.gov.au/media/dfros4dv/rg112-published-30-march-2011-20260421.pdf), pages 5 to 20; accessed 26 September 2026):

- a reasonable basis for the choice of method, the reason for each method used or rejected, and the weight given to each (RG 111.81 to RG 111.85);
- more than one method where possible, with comment on differences, and comment where the value differs materially from the pre-announcement price plus a typical control premium (RG 111.82);
- a value range as narrow as possible, with an explanation if it is wide (RG 111.95 and RG 111.96);
- all material assumptions, stated specifically (interest rates, exchange rates, commodity prices), with sensitivity analysis where a change would move the value materially (RG 111.92 to RG 111.94);
- for forecasts: the material inputs, the discount rate and its basis, risk adjustments and the forecast period (RG 111.117), with reasonable grounds for forward-looking statements (RG 111.112);
- the qualifications of the people responsible, the fee as an actual amount, relationships with the parties, and any valuation work for the commissioning party in the past two years (RG 111.134, RG 112.31 to RG 112.35);
- a specialist (for example a geologist) where the matter is outside the expert's expertise, with the expert critically reviewing the specialist's work (RG 111.136, RG 112.71);
- a supplementary report if material changes occur after the report is issued (RG 111.119 to RG 111.121).

RG 112 treats a fee that depends on the outcome as a loss of independence (RG 112.45), and lists warning signs such as discussing methodology with the commissioning party or changing an opinion at its suggestion without explanation (RG 112.47).

Some paragraph numbers in RG 111.10 to RG 111.23, RG 111.83 to RG 111.94 and RG 112.31 to RG 112.35 were printed together in the PDF text and were assigned from the guides' own cross-references. Check them against the PDF before quoting.

### ASIC's letter to expert licensees

ASIC's [Corporate Finance Update, Issue 27 (February 2026)](https://www.asic.gov.au/about-asic/corporate-publications/newsletters/asic-corporate-finance-update/corporate-finance-update-issue-27/) (accessed 26 September 2026) reports that, after a review of IERs, ASIC wrote to independent experts to address concerns about report clarity, rigour and transparency. The newsletter says reports should:

1. explain and justify the choice of valuation figures and ranges, especially where ranges are close or overlap;
2. give a reasoned basis for the choice of methods, consistent with RG 111;
3. disclose all material assumptions;
4. show critical assessment of any specialist engaged and a thorough review of specialist reports;
5. rest on internal policies and procedures that match current standards.

ASIC said it may take licensing action where it has concerns. The date of the letter and its full text are not published (UNVERIFIED); only the newsletter summary was found.

Related ASIC material, all accessed 26 September 2026:
- [Corporate Finance Update, Issue 24 (August 2025)](https://www.asic.gov.au/about-asic/corporate-publications/newsletters/asic-corporate-finance-update/corporate-finance-update-issue-24/) raised insufficient disclosure of material assumptions, the basis for choosing methods, and the selection of values and ranges.
- [Corporate Finance Update, Issue 29 (June 2026)](https://www.asic.gov.au/about-asic/corporate-publications/newsletters/asic-corporate-finance-update/corporate-finance-update-issue-29-june-2026/) said IERs should explain why a method was adopted and why alternatives were not used or were given less weight, and that ASIC may require more disclosure or act, delaying transactions.
- [24-131MR](https://www.asic.gov.au/about-asic/news-centre/find-a-media-release/2024-releases/24-131mr-pkf-admits-to-contraventions-concerning-independent-expert-report-engagements/): PKF Melbourne Corporate gave a court enforceable undertaking after admitting it lacked documented policies on method selection, specialist competence and conflicts, and agreed to stop IER work until an independent review was done. The date of 20 June 2024 comes from search summaries (UNVERIFIED).
- [24-189MR](https://www.asic.gov.au/about-asic/news-centre/find-a-media-release/2024-releases/24-189mr-afs-licensee-to-cease-providing-independent-expert-reports-on-corporate-transactions/): AP Lloyds' licence was varied from 28 August 2024 so it can no longer prepare IERs, after ASIC found problems with its selection and disclosure of methods and inputs and its use of specialists.

I use ASIC's five points as a checklist for reading the Domain IER: which figures sit inside the range and why, why each method was chosen, which assumptions are disclosed, and how any specialist was reviewed.

### Recent Takeovers Panel and court matters involving IERs

1. Montu Group Pty Ltd [2024] ATP 25 (decision 23 October 2024). A selective buy-back priced on a valuation summary given on a non-reliance basis, without medium-term forecasts and with unexplained minority discounts. The Panel declared unacceptable circumstances and accepted undertakings to update the valuation and improve disclosure, but did not require a full IER. [Reasons](https://takeovers.gov.au/reasons-decisions/2024-atp-25) (accessed 26 September 2026).
2. PointsBet Holdings Limited [2025] ATP 25 (decision 14 August 2025). During the contest between betr's scrip bid and MIXI's offer, the Panel declined to act after betr undertook to put its selective buy-back to shareholders with an IER that values the shares under RG 110. [Reasons](https://takeovers.gov.au/reasons-decisions/2025-atp-25) (accessed 26 September 2026).
3. Twinza Oil Limited [2025] ATP 30 (decision 8 September 2025). A shareholder challenged the IER in a creditors' debt-for-equity scheme. The Panel found the report gave a basis for the expert's conclusion, "while recognising that different experts may form different views", and left the matter to the court. [Reasons](https://takeovers.gov.au/reasons-decisions/2025-atp-30) (accessed 26 September 2026).
4. Twinza Oil Limited (No 2) [2025] FCA 1325. The Federal Court refused to approve the same scheme. According to a law firm summary, the court criticised the lack of a clear link between cash flow projections and the valuation and the reliance on an undisclosed model. [MinterEllison summary](https://www.minterellison.com/articles/court-rejects-twinza-creditors-scheme-of-arrangement) (accessed 26 September 2026). The judgment itself could not be retrieved, so the details are UNVERIFIED against the primary source.
5. Zenith Minerals Limited 01 and 02 (media release TP26/059, 28 August 2026). The bid implementation deed said the target would not commission an IER. The Panel found this clause, with other deed terms, gave the bidder undue influence over the target board and declared unacceptable circumstances. [TP26/059](https://takeovers.gov.au/media-releases/tp26-059) (accessed 26 September 2026).
6. Kingsland Minerals Ltd (media release TP26/035, 19 June 2026). The Panel declined to conduct proceedings, noting that an IER was proposed for the transaction. [TP26/035](https://takeovers.gov.au/media-releases/tp26-035) (accessed 26 September 2026).

The common thread in items 1, 4 and 5 is disclosure: the Panel and the court each objected when shareholders could not see how a value was reached.

## 2. Valuation methods Australian experts use

### ASIC's frame

RG 111 does not prescribe methods (RG 111.83). The expert needs a reasonable basis for its choice (RG 111.81), should use more than one method where possible (RG 111.82), and must say how much weight each method carries (RG 111.84 and RG 111.85). RG 111.86 lists the methods ASIC considers generally appropriate: DCF plus surplus assets; capitalised future maintainable earnings or cash flows plus surplus assets; orderly realisation of assets; the quoted price of listed securities where the market is liquid; and recent genuine offers. It adds: "Some valuation methodologies include a premium for control while others do not." A DCF before a project produces cash needs reasonable grounds for the forecasts, otherwise "other valuation methodologies should be used" (RG 111.116). Mineral assets are expected to be valued under the VALMIN Code (note to RG 111.131). Source: [RG 111 PDF](https://download.asic.gov.au/media/5827832/rg111-published-22-october-2020.pdf) (accessed 27 September 2026).

Deloitte's Gold Road report groups the methods into three approaches: market (earnings multiples, share trading, resource multiples), income (DCF, "appropriate where a projection of future cash flows can be made with a reasonable degree of confidence") and cost (net assets and orderly realisation, which Deloitte considers suitable for companies that are not profitable, companies whose assets are largely liquid, and asset holding companies) (booklet p. 157, [Gold Road Scheme Booklet](https://announcements.asx.com.au/asxpdf/20250815/pdf/06mxpjvcw9991s.pdf), accessed 27 September 2026).

### Methods in recent IERs

All documents in this table were accessed on 27 September 2026.

| Method | When it is used | Example |
|---|---|---|
| DCF as the primary method | Forecasts with a reasonable basis; growth businesses; finite-life assets | Grant Thornton, RPMGlobal (2025): DCF primary, cross-checked with multiples and the quoted price; ten-year forecast FY26 to FY35, terminal growth 3.0% (booklet pp. 112 to 114, [RPMGlobal Scheme Booklet](https://announcements.asx.com.au/asxpdf/20251117/pdf/06s31d5bvrfzdy.pdf)) |
| DCF rejected | Forecasts lack a reasonable basis | Kroll, Insignia Financial (2026): the management model "does not have a sufficiently reasonable basis to be used for our valuation" (booklet p. 155, [Insignia Scheme Booklet](https://announcements.asx.com.au/asxpdf/20260227/pdf/06wwkrzh14m716.pdf)). Kroll also rejected DCF for Johns Lyng because no forecasts beyond FY26 existed (booklet pp. 185 to 187, [Johns Lyng Scheme Booklet](https://announcements.asx.com.au/asxpdf/20250902/pdf/06nrd228fq17jl.pdf)) |
| Capitalised maintainable earnings | Profitable, stable going concern | Kroll, Insignia: maintainable EBITDA of A$430.0m to A$450.0m at 8.5x to 9.0x on a control basis, giving A$4.49 to A$5.08 per share (booklet pp. 152 and 157) |
| Listed company multiples | Evidence for the multiple, or a cross-check | Grant Thornton, RPMGlobal: implied 12.9x to 15.1x FY25 revenue, checked against listed software peers whose values were grossed up by a 30% control premium (booklet pp. 114 and 174 to 177). Kroll notes that listed multiples "do not include a premium for control" (Insignia, booklet p. 156) |
| Precedent transaction multiples | Direct evidence of control multiples | Kroll, Insignia: Australian and international wealth management transactions (booklet pp. 152 and 154) |
| Multiples with a DCF cross-check | Mature business with good peer data | Kroll, Silk Logistics (2024): EBITDA multiples A$1.64 to A$2.27 per share, DCF cross-check A$1.89 to A$2.38 (booklet p. 125, [Silk Scheme Booklet](https://announcements.asx.com.au/asxpdf/20241223/pdf/06czsy1179jjcp.pdf)) |
| Sum of the parts | Assets that need different methods | Kroll, CSR (2024): building products by DCF, CSR's effective 25.2% interest in the Tomago aluminium smelter (held through its 70% of Gove Aluminium Finance) by DCF, and property separately (booklet pp. 121 to 122, [CSR Scheme Booklet](https://announcements.asx.com.au/asxpdf/20240426/pdf/062x9p8g3s3cxn.pdf)). Deloitte, Gold Road: mines by DCF, exploration by a technical specialist, listed shares at market (booklet pp. 117 to 118) |
| Quoted price plus control premium | Usually a cross-check | BDO, Australian Strategic Materials (2026): A$0.68 to A$0.80 plus 25% to 35%, giving A$0.850 to A$1.080 (booklet p. 164, [ASM Supplementary Scheme Booklet](https://asm-au.com/wp-content/uploads/2026/07/20260727_ASM-SchemeBooklet-Supplement-FINAL.pdf)) |
| Net assets or orderly realisation | Asset-holding entities, loss-makers, or a component of a sum of the parts | BDO aggregates ASM's component values as net assets (booklet p. 140). None of the 2024 to 2026 reports read used orderly realisation as the primary method |
| Option pricing | Options and rights | BDO, ASM: Black-Scholes for the listed options (booklet p. 143) |

### Mining companies

- Producing assets with Ore Reserves are valued by a DCF of the life-of-mine plan. Deloitte valued Gold Road's 50% of Gruyere this way at a real post-tax 6.0% to 7.0%, because the assets "have finite lives and thus it is not appropriate to apply an earnings multiple approach" (booklet pp. 117 and 140, [Gold Road Scheme Booklet](https://announcements.asx.com.au/asxpdf/20250815/pdf/06mxpjvcw9991s.pdf), accessed 27 September 2026).
- Undeveloped resources are valued by comparable transactions, expressed as dollars per unit of resource. SRK valued ASM's Dubbo project at A$70 to A$185 per tonne of total rare earth oxide, with a yardstick method (0.1% to 1.25% of in-situ value) as a secondary check (booklet pp. 299 to 309, [ASM Supplementary Scheme Booklet](https://asm-au.com/wp-content/uploads/2026/07/20260727_ASM-SchemeBooklet-Supplement-FINAL.pdf), accessed 27 September 2026).
- The [VALMIN Code (2015)](https://www.valmin.org/docs/VALMIN_Code_2015_final.pdf) (accessed 27 September 2026) requires at least two valuation approaches (section 8.3) and a low, most-likely and high value (section 8.6). Its Table 1 (p. 29) says the income approach does not suit exploration projects and suits development and production projects. VALMIN states that its Market Value "has the same meaning as Fair Value in RG111" (section 8.1). Resource and reserve reporting follows the JORC Code (2012), which the ASX Listing Rules incorporate (VALMIN p. 7). The JORC Code itself was not read (UNVERIFIED beyond VALMIN's description).

## 3. Discount rate conventions

### Risk-free rate

The latest 10-year Australian Government bond yield in [RBA statistical table F2](https://www.rba.gov.au/statistics/tables/csv/f2-data.csv) (accessed 27 September 2026) is 5.245% for 23 September 2026. Averages calculated from the same file: 20 trading days, 5.231%; 250 trading days, 4.804%; ten years to 23 September 2026, 2.921%.

Experts differ on whether to use the spot yield or an average:
- Spot or five-day average: Deloitte used 4.36% (five-day average at 16 July 2025) for Gold Road (booklet p. 162). Grant Samuel used 4.3% at 30 May 2025 for Domain (booklet p. 139, [Domain Scheme Booklet](https://announcements.asx.com.au/asxpdf/20250630/pdf/06l8x6ntjgw6f7.pdf), accessed 27 September 2026).
- Longer average: Grant Thornton adopted 4.00% for RPMGlobal, against a five-day average of 4.35% and a 20-year average of 2.81% (booklet pp. 189 to 190).
- Normalised: Kroll built a normalised rate of about 3.5% for Silk from real-rate and inflation estimates, noted a spot yield of 4.18%, and adopted 4.0% (booklet pp. 150 to 151). It also adopted 4.0% for CSR against a spot yield of 4.38% (booklet pp. 202 to 203).
- Currency: US-dollar cash flows get a US rate. BDO used 4.00% to 4.50% for ASM's Korean plant, modelled in real US dollars (booklet pp. 203 to 204).

The choice matters now: in September 2026 the spot yield (5.245%) is well above the ten-year average (2.921%).

### Market risk premium

| Expert | Deal and year | MRP | Stated basis | Source (accessed 27 September 2026) |
|---|---|---|---|---|
| Kroll | Silk (2024), CSR (2024) | 6.0% | Long-run Australian averages (Bishop, 1900 to 2020) | Silk booklet p. 151; CSR booklet pp. 202 to 203 |
| Grant Thornton | RPMGlobal (2025) | 6.00% | Own studies suggest 5.50% to 6.00% | RPMGlobal booklet p. 190 |
| Deloitte | Gold Road (2025) | 5.50% | Implied return on the All Ordinaries from prices and consensus dividends | Gold Road booklet p. 162 |
| Deloitte | Quickstep (2025) | 5.0% | Firm's current view | IER p. 30, [Quickstep Scheme Booklet](https://announcements.asx.com.au/asxpdf/20250305/pdf/06g90bp2h0rrgf.pdf) |
| Grant Samuel | Domain (2025) | 6% | "a standard rate adopted by Grant Samuel" | Domain booklet p. 139 |
| BDO | ASM (2026) | 6% (US) | Surveys and practitioner rates | ASM booklet p. 204 |

Deloitte pairs a lower MRP with a spot risk-free rate; Kroll and Grant Thornton pair 6.0% with a rate near 4.0%. The resulting costs of equity are closer than the MRP gap suggests.

### Beta, and size or specific risk premiums

- Data: S&P Capital IQ in most reports; Grant Samuel also used SIRCA, MSCI Barra and Bloomberg (Domain booklet p. 139).
- Frequency and period: weekly over two to four years and monthly over five years are both common (Silk booklet pp. 152 to 153; RPMGlobal booklet pp. 190 to 193; Gold Road booklet pp. 162 to 164; ASM booklet pp. 204 to 206).
- Method: observed peer betas are unlevered to remove the effect of each peer's debt, a range is selected, then relevered at a target gearing (Kroll and Grant Thornton 10%, Deloitte 20% for Gold Road). Deloitte applied the Blume adjustment and excluded betas with R² below 5%.
- Extra premiums: Kroll added 0.5% to 1.5% for size for Silk (booklet p. 154); Grant Thornton added 1.00% to 1.50% for forecast risk for RPMGlobal (booklet p. 193); Deloitte added 2.5% to 3.5% for Quickstep (IER p. 30) and none for Gold Road (booklet p. 165); BDO added none for ASM (booklet pp. 205 to 206).

### Five worked examples from published IERs

| | Silk (Kroll) | RPMGlobal (Grant Thornton) | Gold Road (Deloitte) | Domain (Grant Samuel) | ASM plant (BDO) |
|---|---|---|---|---|---|
| Risk-free rate | 4.0% | 4.00% | 4.36% | 4.3% | 4.00% to 4.50% (US) |
| MRP | 6.0% | 6.00% | 5.50% | 6% | 6.00% |
| Beta | Levered 1.19 to 1.29 | Equity 1.19 to 1.29 | Levered 0.94 to 1.18 | 1.0 to 1.1 | 1.10 to 1.30 |
| Extra premium | Size 0.5% to 1.5% | Specific 1.00% to 1.50% | None | Not found | None |
| Cost of equity | 11.6% to 13.3% | 12.11% to 13.26% | 9.54% to 10.84% | 10.3% to 10.9% | 10.60% to 12.30% nominal |
| Result | WACC 10.8% to 12.4% nominal | WACC 11.40% to 12.50% | Real WACC selected 6.0% to 7.0% | Cost of equity only | Real cost of equity 9.0% adopted |
| Pages | Booklet pp. 149 to 154; parameter table on PDF p. 156 | Booklet pp. 189 to 195 | Booklet pp. 161 to 165 | Booklet p. 139 | Booklet pp. 203 to 207 |

Gold Road and ASM convert nominal rates to real ones because their cash flow models are in real terms. Silk and RPMGlobal show the same levered beta because both reports relever an asset beta of 1.10 to 1.20 at 10% gearing and a 30% tax rate. Kroll prints 13.3% as Silk's top cost of equity; the rounded inputs in its table give 13.24%.

## 4. Control premiums

### Published evidence

- [RSM Control Premium Study 2021](https://content.rsm.com.au/rs/897-ZGB-534/images/2023_01_08_NAT_Control_Premium_Study_2021.pdf) (accessed 27 September 2026), with Curtin University: 605 successful takeovers and schemes of ASX-listed targets, 1 July 2005 to 31 December 2020. Measured against the price 20 days before announcement, the average premium was 34.7% and the median 27.5% (p. 4). Schemes averaged 32.1% (median 25.2%) and off-market bids 37.3% (median 30.1%) (p. 10). Targets above A$500m averaged 20.8%, and those between A$100m and A$500m averaged 30.9% (p. 11). No later RSM study was found.
- Lonergan Edwards, in its Bigtincan report: over 500 successful cash change-of-control transactions in Australia from January 2000 to December 2024 show an average premium of 30% to 35% over the undisturbed price, which it says equals about 20% to 25% at the enterprise value level, depending on debt (PDF pp. 169 and 187 to 188, [Bigtincan Scheme Booklet](https://announcements.asx.com.au/asxpdf/20250228/pdf/06g49p222vx9td.pdf), accessed 27 September 2026).
- Bugeja, da Silva Rosa, Izan and Ngan (2016), "To scheme or bid? Choice of takeover method and impact on premium", *Australian Journal of Management* ([DOI](https://doi.org/10.1177/0312896214565120); [working paper](https://opus.lib.uts.edu.au/bitstream/10453/88977/4/ajmresubmissionblind.pdf), accessed 27 September 2026): 276 schemes and 555 takeovers from 2000 to 2011; after controlling for self-selection, scheme premiums are lower than takeover premiums.

### Premiums applied in recent IERs

| Expert and deal | Premium | Evidence cited | Source (accessed 27 September 2026) |
|---|---|---|---|
| BDO, ASM (2026) | 25% to 35% on the quoted price | Own sample, June 2016 to June 2026: all ASX median 27.56%, mining median 29.72% | ASM booklet pp. 164 and 201 to 202 |
| Grant Thornton, RPMGlobal (2025) | 30% on listed peer values | "frequently been in the range of 20% to 40% in Australia" | RPMGlobal booklet pp. 174, 177 and 205 |
| Kroll, Insignia (2026) | No fixed figure; control-basis multiples | FactSet: 25% to 40% median in deals with a US party; the premium is "an outcome of the valuation process, not a determinant of value" | Insignia booklet p. 156 |
| Lonergan Edwards, Bigtincan (2025) | 30% to 35% for the quoted price cross-check | Own study above | Bigtincan PDF pp. 187 to 188 |

RG 111.82 asks the expert to comment where its value differs materially from the undisturbed price plus a typical premium. Kroll states that its Insignia range of A$4.49 to A$5.08 sits 46.9% to 65.9% above the undisturbed close of A$3.06 on 11 December 2024 (A$5.08 ÷ A$3.06 − 1 gives 66.0%, so Kroll's top figure appears to use unrounded inputs; UNVERIFIED). Kroll attributed the gap to the market's earlier view of remediation risk and the acquirer's ability to direct strategy (Insignia booklet pp. 152 to 153).

## 5. How a published IER is laid out

Three reports from different firms were read in full: Deloitte for Gold Road (August 2025, [booklet](https://announcements.asx.com.au/asxpdf/20250815/pdf/06mxpjvcw9991s.pdf), pp. 114 to 160), Kroll for Insignia Financial (February 2026, [booklet](https://announcements.asx.com.au/asxpdf/20260227/pdf/06wwkrzh14m716.pdf), from p. 89) and BDO for Australian Strategic Materials (replacement report, July 2026, [supplementary booklet](https://asm-au.com/wp-content/uploads/2026/07/20260727_ASM-SchemeBooklet-Supplement-FINAL.pdf), from p. 86). All accessed 27 September 2026. They share one structure:

1. A Financial Services Guide, required because the report is financial product advice.
2. A summary letter or section 2 that states the opinion first: fair and reasonable, or in the best interests of members, "in the absence of a superior proposal" (Gold Road p. 116; Insignia p. 92; ASM p. 91).
3. The fairness comparison: a table and usually a bar chart of the low and high value per share on a control basis against the offer. Kroll states that "the low end of the valuation range represents the relevant threshold for fairness" (Insignia p. 95).
4. Reasonableness factors: the premium to the undisturbed price, certainty of cash, the absence of other offers, the likely share price if the deal fails, and tax. BDO uses a two-column table of advantages and disadvantages (ASM pp. 92 to 93); Deloitte and Kroll use headed paragraphs or bullets.
5. The body: transaction terms, scope, industry, company profile, then valuation (method choice, each method, cross-checks).
6. Appendices: method descriptions, discount rate, control premium evidence, comparable companies and transactions, and for miners the technical specialist's VALMIN report.

Preferred values are uncommon. Deloitte and Kroll give low and high only; BDO gives a preferred value for each method in its body tables (ASM p. 165) but not in its headline comparison. For a scrip offer, BDO values the consideration on a minority basis using the bidder's post-announcement trading (ASM pp. 142 and 166).

## Unverified or not found

- The text of Corporations Act sections 411, 636, 640 and 648A and Schedule 8 of the Corporations Regulations was not read directly; section numbers come from ASIC and Takeovers Panel documents.
- The date and full text of ASIC's letter to expert licensees are not published; only the February 2026 newsletter summary was found.
- The Twinza Federal Court judgment ([2025] FCA 1325) could not be retrieved; its summary relies on a law firm article.
- The PKF undertaking date (20 June 2024) comes from search summaries.
- Some RG 111 and RG 112 paragraph numbers were assigned from cross-references because the PDF text printed them together.
- RSM's 2017 study figures were not read, and no RSM study after 2021 was found.
- The JORC Code was not read directly.
- Grant Samuel's unlevering method and any specific risk premium for Domain were not found in the pages read.
- Page references for the Quickstep and Bigtincan reports are internal IER pages or PDF pages, not booklet pages.

# Design research

What I studied before choosing how the site looks, what I took from it, and the three directions I am choosing between. All pages and files were accessed on 4 October 2026. Where a page was read through a summary tool and not in full, I say so, and I re-check any quotation before it appears on the site. Anything I could not confirm is marked UNVERIFIED.

The brief: the site shows my valuation range next to the expert's range and the offer price, and every number leads to its source. A recruiter opens it on a phone for about 30 seconds, a hiring manager reads it on a laptop for about 5 minutes, and an interviewer asks about single figures.

## Constraints that apply to every direction

- Plain HTML, CSS and SVG drawn by Python at build time, with a little plain JavaScript that only looks up precalculated values (see [ARCHITECTURE.md](ARCHITECTURE.md)). No component kit.
- Scripts come from separate files on the same site, so the Content-Security-Policy meta tag allows scripts from the site only.
- No third-party request of any kind, fonts included. Fonts are self-hosted subsets.
- Charts are SVG in the page, so they show before any script runs, and each has a data table beside it.
- The light theme is the default. A dark theme is a later option and would have to pass the same contrast checks.

## What published reports do

I read how four expert reports and several adviser and research documents lay out ranges, assumptions and sources. Page numbers are the printed numbers in each booklet's footer.

### Documents read

Page numbers in this file are printed footer numbers. To find the PDF page, add 3 for the Domain booklet, 4 for Gold Road and 2 for Insignia (checked by rendering the pages); for ASM the printed and PDF numbers are the same. The adviser slides are image files inside the SEC exhibit pages.

| Document | Address | Terms |
|---|---|---|
| Domain scheme booklet, Grant Samuel report (pp. 116 to 170) | [ASX announcement, 30 June 2025](https://announcements.asx.com.au/asxpdf/20250630/pdf/06l8x6ntjgw6f7.pdf) | Third-party document, linked and not copied |
| Gold Road scheme booklet, Deloitte (pp. 114 to 160, tables on pp. 117, 118, 148 and 165) | [ASX announcement, 15 August 2025](https://announcements.asx.com.au/asxpdf/20250815/pdf/06mxpjvcw9991s.pdf) | None stated |
| Insignia Financial scheme booklet, Kroll (pp. 93, 152, 163 and 170) | [ASX announcement, 27 February 2026](https://announcements.asx.com.au/asxpdf/20260227/pdf/06wwkrzh14m716.pdf) | None stated |
| ASM supplementary scheme booklet, BDO (pp. 91, 92 and 153) | [ASM website, 27 July 2026](https://asm-au.com/wp-content/uploads/2026/07/20260727_ASM-SchemeBooklet-Supplement-FINAL.pdf) | None stated |
| Morgan Stanley for the Soho House special committee, 12 August 2025, slide 9 | [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1846510/000114036125035726/ny20055352x2_ex16-ciii.htm) | None stated |
| Goldman Sachs for the Select Medical special committee, data at 27 February 2026, slides 3, 4 and 13 | [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1320414/000110465926043531/tm2611660d2_ex99-cxiii.htm) | None stated |
| Citi for a special committee (target shown as "Alpha"), January 2025, slide 7 | [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1897982/000114036125003656/ny20042057x7_exc-10.htm) | None stated |
| Pitt Street Research, AFT Pharmaceuticals initiation, 24 July 2026 (pp. 1, 22, 24) | [report](https://pittstreetresearch.com/wp-content/uploads/2026/07/AFT-Pharmaceuticals-research-initiation-report-24-07-2026.pdf) | Free download, no reuse terms read |
| Edison Investment Research, Accsys Technologies, 25 February 2025 (pp. 1 and 11) | [report](https://d3s3shtvds09gm.cloudfront.net/cd44f22793b0a52a81a760c5e939c42c.pdf) | Free download, no reuse terms read |
| Football field guides | [CT Acquisitions](https://ctacquisitions.com/football-field-valuation-chart-guide/), [Macabacus](https://macabacus.com/blog/build-football-field-chart-excel), [Breaking Into Wall Street](https://breakingintowallstreet.com/kb/excel/football-field-valuation/), [Umbrex](https://umbrex.com/resources/frameworks/finance-frameworks/football-field-valuation/) | None read |
| Datawrapper on axes and range plots | [why bar charts start at zero](https://www.datawrapper.de/academy/why-our-column-and-bar-charts-start-at-zero), [customising a range plot](https://www.datawrapper.de/academy/customizing-your-range-plot) | None read |

The Morgan Stanley, Goldman Sachs and Citi slides and the Pitt Street and Edison pages were rendered and looked at. Two more adviser documents (FONAR, 10 December 2025, and Cepton, 13 February 2024, both SEC exhibits) were read as extracted text only, so I draw nothing from their layout. The booklets are saved in `research/raw/`, which is not in git.

### The Domain report (Grant Samuel)

- The valuation summary on p. 131 is a bridge table: business operations, other assets and liabilities, enterprise value, net debt, equity value, shares and value per share, with Low and High columns and a column of section references. It gives no preferred value and does not show the offer.
- The only chart of the expert's range is the eight-scenario NPV chart on p. 144, drawn on an enterprise value axis in A$m with no labels at the bar ends. The reader has to turn back to pp. 142 and 143 to learn what scenarios A to H mean.
- The best encoding of the offer is on p. 158: a labelled horizontal line for the A$4.43 consideration, a grey band for the three-year trading range (A$2.44 to A$4.25) and a labelled marker for the initial proposal, with no legend.
- The undisturbed price appears only in the premium table on p. 157 (A$3.12 close on 20 February 2025, with VWAPs of A$3.14, A$2.95, A$2.77 and A$2.88).
- The discount rate inputs (pp. 139 to 142) are in paragraphs and footnotes, not a table, and there is no per-share sensitivity grid.

### Other expert reports

- Deloitte (Gold Road) has the clearest tables: p. 117 shows the offer as a range with equal low and high so it fits the same table shape as the value, p. 148 is a two-way sensitivity grid with the base-case block shaded, and p. 165 is a WACC table with Low, High and Mid columns, a source line and a "Selected" row.
- Kroll (Insignia) puts the drivers inside the valuation table (maintainable EBITDA and the multiple sit above the operating business value). Its broker-target chart (p. 170) draws the expert's range as a grey band with no axis, which cannot be read against the columns.
- BDO (ASM) places a table above a two-bar chart whose bars have no labels, uses one-variable sensitivity strips with the base case marked (p. 153), and is the only one of the four to state a preferred value (in text).

### Adviser presentations and research notes

I viewed football field slides filed with the SEC by Morgan Stanley (Soho House), Goldman Sachs (Select Medical) and Citi (a target shown as "Alpha"), and two free research notes, Pitt Street Research on AFT Pharmaceuticals and Edison on Accsys. I found no UK scheme document with a football field in two searches.

- The slides agree on one row per method, a floating bar on a common per-share axis, low and high printed at the two bar ends, and one vertical line for the offer. Morgan Stanley adds a dashed line for the unaffected price and prints premium and multiples under the axis, so one x-position can be read as several quantities.
- Goldman and Citi put an assumptions column beside the bars (for example the WACC and growth ranges), which is what makes a range traceable. Both put reference rows (52-week range, broker targets) in grey.
- Weak points I saw: Goldman's chart has no axis, so bar length can be read only from the labels; Citi's offer line crosses two end labels; Morgan Stanley's plot holds three dashed lines and several dashed boxes.
- Pitt Street states its valuation range in the first paragraph and shows base and bull cases side by side. Both notes carry a sponsor disclosure. Edison's two WACC grids leave the base case unshaded, so the reader has to match it to the text.

### Football field conventions in guides

Guides from CT Acquisitions, Macabacus, Breaking Into Wall Street and Umbrex agree on horizontal bars, labelled ends and one offer or current price line. Row order has no standard: CT Acquisitions puts comparables first, Goldman and Citi put the DCF first and reference rows last. Umbrex lists the common faults: mixing enterprise value, equity value and per-share figures without a bridge, using different periods across rows, and false precision from narrow ranges. Datawrapper says dot and range plots need not start at zero because there is no filled bar. Applying that to filled floating bars is my own extension, not Datawrapper's statement. IBCS rule detail for scenarios and notes could not be confirmed from the standard itself (see the next section).

### What this means for the site

1. Print both ends of every bar, and draw an axis with tick values.
2. Draw one labelled offer line across all rows, with its price and date, and give the undisturbed price a different mark (dashed).
3. Draw the expert's range as a bar in the same form as mine, on the same per-share axis, and state any row that is on a different basis.
4. Put the assumptions on the row (the WACC and growth ranges, the multiple range), not on another page.
5. Show my preferred value as a marker, and say that the expert's published range has none, so my bar is not read as more precise.
6. Mute reference-only rows in grey under a "For reference" label.
7. Use a bridge-shaped summary table with a section reference column, bold subtotals, the per-share row last and the drivers inside it.
8. Build the assumption register on Deloitte's pattern: input, low, high, selected value, source line.
9. Shade the base case in every sensitivity grid and add one line saying what the grid does not cover.
10. Put a source line and numbered notes directly under each figure, with the data date.
11. Keep the offer line clear of end labels.
12. Put the answer and the disclaimer on the first screen.

No source I found offers a marker on every figure that opens its document, page and date. That is the one place where the site goes beyond what the reports do.

What breaks at 390 px, and the fix I plan:

| Layout in the sources | Why it breaks on a phone | Fix |
|---|---|---|
| Bars with labels at both ends and several lines | Labels collide on narrow bars | Stack one row per method, print low and high as text on the row, and pin the offer value above the plot |
| Assumptions or multiples in columns beside the bars | Three to five columns do not fit | One block per method: title, one-line assumptions, bar, then low and high, with full assumptions on tap |
| Several reference lines and dashed boxes | Unreadable at 390 px | Show only the offer line by default and put the undisturbed price on a toggle |
| Wide summary and sensitivity tables | A five by seven grid shrinks the type | Scroll inside the table with a sticky first column, type at 14 px or more, and the base-case shading kept |
| Price and volume on two axes | Fine detail disappears | Price only, with the offer line and one or two labelled events |
| Footnotes under 12 px | Unreadable | 12 to 13 px, tap to expand, source line always visible |

## Sources for design principles

Licence notes are what the source states. "None stated" means I found no licence on the page or in the repository, so I link to the source and restate the idea in my own words.

| Source | Licence | Principle I take | Fit |
|---|---|---|---|
| [IBCS standards](https://www.ibcs.com/standards/) (IBCS 2.0, 11 June 2026; ISO 24896 is a paid document) | CC BY-SA 4.0; adaptations need attribution and the same licence | Encode scenario by fill (solid actual, outline comparison, hatch estimate); variances on their own aligned strip; one meaning per style. Exact notation text UNVERIFIED: I could only read secondary summaries | Principles only, with a credit if I copy any wording |
| [FT Visual Vocabulary](https://github.com/Financial-Times/chart-doctor) | MIT for software; the FT's content is all rights reserved | Choose the chart from the relationship shown (deviation, ranking, change over time). It has no guidance on uncertainty or ranges | Principles only |
| [Vercel Web Interface Guidelines](https://vercel.com/design/guidelines) ([repository](https://github.com/vercel-labs/web-interface-guidelines)) | MIT (repository) | Labelled controls, visible `:focus-visible`, tabular numerals, reduced-motion support, 44 px touch targets, 16 px minimum input text | Fits: every rule is plain CSS or HTML |
| [WCAG 2.2 Understanding pages](https://www.w3.org/WAI/WCAG22/Understanding/) | W3C document licence | 1.1.1 text alternative with a data table; 1.4.1 colour is not the only cue; 1.4.11 3:1 for chart lines and marks; 1.4.10 tables may scroll but the text around must reflow; 1.4.13 hover content must be dismissible and hoverable; 2.5.8 24 px targets. Focus appearance (2.4.13) is AAA, so I treat it as a target | Fits: these are the tests |
| [UK Analysis Function: charts, tables and colour](https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-charts/) | None stated on the pages (UK government content is usually Open Government Licence; UNVERIFIED here) | Headline plus statistical subtitle; direct labels; right-aligned numbers with consistent decimals; units in column headers; a source line with a link; never a table as an image; at most four categories; data download beside a chart | Fits: closest to my brief |
| [Datawrapper: colour-blindness](https://www.datawrapper.de/blog/colorblindness-part2) and [accessibility](https://www.datawrapper.de/academy/how-we-make-sure-our-charts-maps-and-tables-are-accessible) | None stated | Blue with orange is the safest pair; vary lightness; use patterns, symbols and direct labels; chart footer with source, notes and "Get the data" | Principles only; the footer pattern is reusable |
| [Chartability](https://github.com/Chartability/POUR-CAF) | None stated | A heuristic audit workbook of 50 checks under the four WCAG principles, plus extra checks for assistive use | Principles only; I use it as a manual checklist |
| [Urban Institute style guide](https://urbaninstitute.github.io/graphics-styleguide/) | Apache-2.0 on the repository, with a GPL-3.0 mention in the README (UNVERIFIED which covers the text) | No non-zero bar baselines, dual axes or 3D; a mandatory source line and notes; alt text that describes the function; a border only under column headings and the last row | Fits as a checklist |
| [Visa Chart Components](https://github.com/visa/visa-chart-components) | MIT | A data table beside each chart and written keyboard instructions. README only; source not read | Principles only: it needs a component framework |
| [Fossheim, review of 2024 election dashboards](https://fossheim.io/writing/posts/2024-dataviz-a11y-elections/) | None stated | Failures to test against: hover-only tooltips, random tab order, alt text that names the chart but not the result, sticky headers that hide content at 400% zoom | Fits |
| Colour palettes: [Okabe and Ito](https://jfly.uni-koeln.de/color/), [ColorBrewer](https://github.com/axismaps/colorbrewer), [Paul Tol](https://sronpersonalpages.nl/~pault/), [viridis](https://github.com/BIDS/colormap) | Okabe-Ito and Tol: none stated, cite the authors; ColorBrewer Apache-2.0; viridis CC0 | Blue and vermilion work as a favourable and unfavourable pair for all common colour-vision types; red and green do not | Fits, with credit |
| [web.dev performance budgets](https://web.dev/articles/performance-budgets-101), [LCP](https://web.dev/articles/lcp), [font loading](https://web.dev/articles/optimize-webfont-loading) | Not stated on the fetched pages | Under about 170 KB on the critical path; LCP of 2.5 s or less; WOFF2, subsetting and `font-display` | Fits |
| [MDN Popover API](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API/Using), [details](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/details), [W3C tooltip pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/) | MDN content licence not on the page (usually CC-BY-SA; UNVERIFIED) | A tooltip cannot hold a link and never takes focus, so a source note that links to a document must be a popover or a `details` element that works by tap and keyboard. Browser support for `popover="hint"` is UNVERIFIED | Fits, and shapes the provenance marker |
| [Our World in Data chart pages](https://ourworldindata.org/grapher/life-expectancy) | CC BY 4.0 (stated on the page) | A source line per dataset, a data tab, CSV download and a citation text | Principles only |
| [Damodaran online data](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datacurrent.html) | Not stated | Every dataset carries a "last updated" date and an Excel download | Principles only |
| [RBA Statement on Monetary Policy](https://www.rba.gov.au/publications/smp/2026/aug/contents.html) and [Bank of England Monetary Policy Report](https://www.bankofengland.co.uk/monetary-policy-report/2026/july-2026) | Not stated | Chapters as web pages and a PDF, an Excel file of the data behind the charts, named sources, alt text that states the finding. I saw only the contents page for the RBA, so its chart layout is UNVERIFIED | Principles only |
| [Takeover valuation report on Qantas](https://aharlingfinance.wordpress.com/portfolio/takeover-valuation-report-%EF%BB%BFqantas-airways-limited/) | Not stated | The nearest subject match: a readable HTML takeover valuation with an executive summary and a disclaimer. It is hosted on WordPress.com, so it makes third-party requests | Principles only |

I did not reach Simply Wall St, Bloomberg Graphics, Reuters Graphics or Morningstar (access blocked or not attempted), so I draw nothing from them. An Alpha Spread DCF page returned a summary that named a different company from its address, so I discard it.

Principles that appeared in three or more of these sources:

1. Colour is never the only cue; add labels, symbols or patterns.
2. Label directly instead of using a legend.
3. Every chart has a text alternative and a data table or download beside it.
4. Every figure and table has a visible source line with a link.
5. Use three or four colours at most.
6. Pair blue with orange or vermilion, not red with green.
7. Zero baselines for bars, no 3D, no dual axes, sparse gridlines.
8. Right-aligned tabular figures with consistent decimals and units in the header.
9. Everything works by keyboard, with a visible and unobscured focus ring.
10. Graphics reach 3:1 contrast and text 4.5:1.
11. Anything shown on hover is also reachable by tap and keyboard and can be dismissed.
12. Date every dataset.
13. Tables are never images, and the text around a table reflows.
14. Keep the page small and static.

## Defaults I avoid

These are the stock choices that make a finance or dashboard site look like every other one. Each direction below is checked against this list.

- Colour: purple, indigo or blue-to-purple gradients; gradient text; neon glow; glassmorphism; a gradient wash as decoration; the same soft grey shadow under everything; coloured stripes on the edge of cards; grey text on a coloured background; a warm cream page with a high-contrast serif and a terracotta, clay or sage accent; a near-black page with one acid-green or vermilion accent; navy with gold, or orange on black.
- Layout: a centred hero followed by three feature cards; identical rounded cards; cards inside cards; bento grids; newspaper imitation (hairlines, zero radius, dense columns) used as a style; numbered markers on content that is not a sequence.
- Type and chrome: Inter, Roboto, Arial or the framework's default face; small all-caps headings above headings; one word in a headline set in a different colour or style; meta strings joined with middle dots; labels built as "WORD, fragment"; a monospace face for small data labels; an arrow appended to every link.
- Components and content: emoji as icons; icons in coloured squares above headings; chat buttons, fake live badges, ticker tapes, candlestick decoration and stock photos; unchanged component-kit styling; placeholder or invented figures in anything shipped.

I did not run the brief through a generic prompt to see where it lands. I compared each direction with this list instead.

## What I measured

### Typefaces

Every face must have an open licence, uniform lining figures (default or through `tnum` and `lnum`), a true minus (U+2212), and a small subset file. I downloaded the candidates from the [Google Fonts repository](https://github.com/google/fonts/tree/main/ofl), read each file's tables with fontTools (MIT), and subset each to Basic Latin plus the punctuation I need and the minus, keeping the number features, as WOFF2. The licence column is the name recorded in each font file (name ID 13), which I did not cross-check against the licence file.

| Family | Licence in file | Default figures | `tnum` | U+2212 | WOFF2 subset |
|---|---|---|---|---|---|
| IBM Plex Sans | SIL OFL 1.1 | Uniform widths, lining | Not needed | Yes | 17 KB (width fixed at 100, weights 400 to 700); 37 KB with both axes |
| IBM Plex Serif | SIL OFL 1.1 | Uniform widths, lining | Not needed | Yes | 11 KB per weight |
| Source Sans 3 | SIL OFL 1.1 | Uniform widths | Not needed | Yes | 17 KB |
| Source Serif 4 | SIL OFL 1.1 | Uniform widths, lining | Yes | Yes | 22 KB with the optical size fixed; 82 KB with it free |
| Atkinson Hyperlegible Next | SIL OFL 1.1 | Proportional | Yes | Yes | 21 KB |
| Public Sans | SIL OFL 1.1 (USWDS modified version) | Proportional | Yes | Yes | 15 KB |
| Newsreader | SIL OFL 1.1 | Uniform widths, lining | Yes | Yes | 85 KB (optical size axis) |
| Literata | SIL OFL 1.1 | Proportional | Yes | Yes | 80 KB (optical size axis) |
| Libre Franklin | SIL OFL 1.1 | Proportional | No | Yes | Rejected: no tabular figures |

Faces with proportional defaults pass only if the CSS sets `font-variant-numeric: tabular-nums lining-nums` on every number, which the site does anyway. My check of the `tnum` feature reads single-substitution rules only, so a face reported as lacking `tnum` should be re-tested in a browser before I rely on that result.

### Colours

Contrast ratios use the WCAG relative luminance formula, which I calculated against each direction's page colour. Colour-vision checks use the Viénot simulation matrices for deuteranopia, protanopia and tritanopia and a simple CIE76 colour difference (ΔE) between the favourable and unfavourable colours. Values above about 40 are clearly distinguishable. This is an approximation; before launch I repeat the check with Color Oracle or Coblis on screenshots of the charts as built.

The favourable and unfavourable colours stay clearly apart in every direction. Blue and orange (directions A and C) give ΔE 82 to 125 across the three colour-vision types. Teal and orange (direction B) give 92 and 97 for deuteranopia and tritanopia and 43 for protanopia. The two colours differ little in lightness (the contrast ratio between them is 1.0 to 1.2), so colour never carries the meaning alone: every variance has a plus or minus sign, and bars point left or right.

## The three directions

Each direction is a complete proposal for the landing view and the system behind it. All three draw the football field as SVG at build time and use the same notation (solid for actuals, outline for the expert, hatch for my estimates, a solid offer line and a dashed undisturbed price line). None makes a third-party request. The wireframes use A$x.xx for my own results, which I have not valued yet. The other numbers are published: the offer is A$4.43, Grant Samuel's range is A$4.06 to A$4.46, and the undisturbed close was A$3.12 on 20 February 2025.

Each colour table has six core values, marked "core" (paper, ink, accent, the two variance colours and the dividing rule), and three supporting values (the raised surface for overlays, the muted ink and the stronger border for controls). Hex values are my choices, checked as described above.

### Direction A: workpaper

Concept. A valuation file as an auditor or analyst keeps it, where every figure carries a reference to the document it came from. The provenance marker is a short reference code (for example "GS-131" for Grant Samuel, booklet p. 131), and a "Show sources" switch prints every code beside its figure at once, the way a reviewer flips through a file to see its tick marks.

| Role | Hex | Use |
|---|---|---|
| paper (core) | #F5F6F4 | page background |
| surface-raised | #FFFFFF | overlays and the source popover |
| ink (core) | #1D2A30 | text and the expert's outlines (13.6:1 on paper) |
| ink-muted | #4F6068 | secondary text (6.0:1) |
| rule (core) | #C8D0D2 | gridlines and dividers (decorative) |
| rule-strong | #7C8A90 | control borders (3.3:1) |
| accent (core) | #F2D54B | highlighter fill behind my preferred value and the current selection, never as text (ink on it 10.1:1) |
| positive-variance (core) | #0B5CAD | text and bars (6.2:1) |
| negative-variance (core) | #A8510A | text and bars (5.0:1) |

Type. IBM Plex Sans for everything in the working area and IBM Plex Serif regular for page titles and section headings only. Scale ratio 1.2 from a 16 px base: 13 (source notes), 14 (table text), 16 (prose), 19 (subheadings), 23 (section headings), 28 (page title), 34 (the verdict sentence). About 28 KB of fonts in total.

Landing view, desktop:

```
+--------------------------------------------------------------------------------+
| Domain Holdings (ASX: DHG), CoStar scheme   Valuation  Gap  Timeline  Sources  |
|                                                          [ ] Show sources     |
+--------------------------------------------------------------------------------+
|                                                                                |
|  My valuation of A$x.xx to A$x.xx per share [x] includes / excludes the        |
|  A$4.43 offer. Grant Samuel's range was A$4.06 to A$4.46 [GS-131].             |
|                                                                                |
|  A$ per share        2.50   3.00   3.50   4.00   4.50   5.00                   |
|  DCF                  .......[////////*////////].........                      |
|  Trading comps        ..........[///*///]..............                        |
|  Precedents           ...............[///*////].........                       |
|  Grant Samuel        ..................[========]......                       |
|                              :                  |                              |
|                        undisturbed A$3.12     offer A$4.43                     |
|  [ ] = ink outline: expert   [///] = hatched: my estimate   * = my preferred   |
|                                                                                |
|  How I valued it        Where I differ from the expert    Download the model   |
+--------------------------------------------------------------------------------+
```

Landing view, mobile (390 px):

```
+--------------------------------+
| DHG, CoStar scheme        Menu |
| [ ] Show sources               |
+--------------------------------+
| My range of A$x.xx to A$x.xx   |
| [includes] the A$4.43 offer.   |
| Grant Samuel: A$4.06 to 4.46.  |
|                                |
| DCF                            |
|  x.xx [///////*///////] x.xx   |
| Trading comparables            |
|  x.xx [////*///] x.xx          |
| Precedent transactions         |
|  x.xx [///*////] x.xx          |
| Grant Samuel                   |
|  4.06 [========] 4.46          |
|   dashed 3.12   solid 4.43     |
|                                |
| How I valued it                |
| Where I differ                 |
| Download model and report      |
+--------------------------------+
```

Where it takes its one visible risk. The reference codes and the "Show sources" switch put the evidence trail on the face of the page, where most finance sites hide it in footnotes. Each figure carries a small bracketed code in muted ink, so a busy page looks like a marked-up file and not a clean dashboard.

Self-review against the defaults above.
- The cool off-white page with a serif for headings is one step from the warm cream page with a display serif. The paper is a cool grey-green, the serif is limited to titles, and there is no terracotta, clay or sage accent.
- A highlighter yellow accent does not match the stock finance palettes: navy with gold needs a navy, and here the ink is slate and the yellow fills small areas only.
- The bracketed codes could read as "WORD, fragment" labels. They are codes that resolve to a document and are never decoration.
- Plex Sans is not a default of any stack but is common on developer sites. I accept that because the figures and the minus sign are right and no monospace face is used.
- Changes made in review: the yellow is never used for text, because it fails contrast, and the focus ring is ink with a paper offset.

Third-party requests: none.

### Direction B: range first

Concept. The football field is the landing page and the navigation. Every row is a link that opens the method behind it (DCF, comparables, precedents, the expert's report). The page reads as the exhibit page of an expert's report enlarged to the width of the screen, with the verdict above it.

| Role | Hex | Use |
|---|---|---|
| paper (core) | #F7F9FB | page background |
| surface-raised | #FFFFFF | overlays and popovers |
| ink (core) | #1A2332 | text and the expert's outlines (15.0:1) |
| ink-muted | #4B5768 | secondary text (7.0:1) |
| rule (core) | #D0D7E0 | gridlines (decorative) |
| rule-strong | #7D899B | control borders (3.4:1) |
| accent (core) | #1B4FBF | my hatch, my preferred value, focus and selection (6.8:1) |
| positive-variance (core) | #00796B | text and bars (5.0:1) |
| negative-variance (core) | #B34700 | text and bars (5.2:1) |

Type. Atkinson Hyperlegible Next as the only family, weights 400 and 600. It was designed to keep letters and digits distinct, which suits a page of figures. Scale ratio 1.25 from 16 px: 13, 16, 20, 25, 31, 39, with the verdict sentence at 31. About 21 KB of fonts.

Landing view, desktop:

```
+--------------------------------------------------------------------------------+
| DHG / CoStar                                Method  Gap  Timeline  Sources     |
+--------------------------------------------------------------------------------+
| My valuation of A$x.xx to A$x.xx includes the A$4.43 offer.                    |
| The expert's range was A$4.06 to A$4.46.                                       |
|                                                                                |
|        2.50       3.00       3.50       4.00       4.50       5.00              |
|   DCF               [////////////*///////////]                                 |
|        low x.xx                         high x.xx                              |
|   Trading comparables   [////////*////////]                                    |
|   Precedent transactions        [///////*///////]                              |
|   Grant Samuel (expert)                          [==========]                  |
|                         :                           |                          |
|                  undisturbed A$3.12             offer A$4.43                   |
|                                                                                |
|  Each row opens its method. Prices are A$ per share, valuation date 31 Dec 2024|
|  [Download the model (Excel)]  [Download the report (PDF)]                     |
+--------------------------------------------------------------------------------+
```

Landing view, mobile (390 px). Rows stack with the bar at full width under each label, and the axis repeats above every second row so no row is read without a scale.

```
+--------------------------------+
| DHG / CoStar              Menu |
| My range A$x.xx to A$x.xx      |
| includes the A$4.43 offer.     |
| Expert: A$4.06 to A$4.46.      |
|  3.00      4.00      5.00      |
| DCF                            |
|  [///////*//////]              |
|  x.xx               x.xx       |
| Trading comparables            |
|  [////*///]                    |
| Precedent transactions         |
|  [///*////]                    |
| Grant Samuel                   |
|        [======]                |
|   : 3.12      | 4.43           |
| Download model  Download PDF   |
+--------------------------------+
```

Where it takes its one visible risk. The chart is the hero at full width with no illustration, no headline number and no supporting statistics. The 30-second read is the chart and one sentence. If the ranges are not interesting the page is thin, so the gap analysis has to carry the story.

Self-review against the defaults above.
- A blue accent on a cool white page is the commonest finance palette. I kept it because the blue is deep and appears only on my hatch, my preferred marker and the focus ring, so no large area reads as a brand colour.
- Rows are links shown by an underlined label, not by an appended arrow.
- A full-width chart is not the default hero: there is no large number, no row of statistics and no gradient.
- Atkinson is recognisable but is not the default of any stack.
- Changes made in review: the axis repeats on mobile, and the row links use underlines.

Third-party requests: none.

### Direction C: disclosure document

Concept. A scheme booklet rebuilt for the screen. Shareholders read a booklet in a fixed order (the chair's letter, why vote, key dates, the expert's conclusion), so the site follows that order and keeps the booklet's habit of stating the conclusion first and the evidence after. A contents list sits at the side on desktop and at the top on mobile. Sections are numbered because they are read in sequence.

| Role | Hex | Use |
|---|---|---|
| paper (core) | #FBFBF9 | page background |
| surface-raised | #FFFFFF | overlays and popovers |
| ink (core) | #23272E | text and the expert's outlines (14.5:1) |
| ink-muted | #575F6B | secondary text (6.2:1) |
| rule (core) | #D5D8DC | dividers (decorative) |
| rule-strong | #80868F | control borders (3.5:1) |
| accent (core) | #0F766E | my hatch, preferred value, focus and links (5.3:1) |
| positive-variance (core) | #0B5CAD | text and bars (6.4:1) |
| negative-variance (core) | #B04A0A | text and bars (5.3:1) |

Type. Source Serif 4 for prose (optical size fixed, weights 400 to 700) and Source Sans 3 for tables, labels, the chart and controls. Both have uniform lining figures by default and a true minus. Scale ratio 1.2 with prose at 17 px and tables at 14 px: 13, 14, 17, 20, 24, 29, with the conclusion at 29. Line length 66 characters. About 39 KB of fonts.

Landing view, desktop:

```
+--------------------------------------------------------------------------------+
| Domain Holdings, CoStar scheme: an independent valuation        Download  About|
+--------------------+-----------------------------------------------------------+
| Contents           | 1  My conclusion                                          |
|  1 Conclusion      |    My valuation of A$x.xx to A$x.xx per share includes    |
|  2 Valuation       |    the A$4.43 offer. Grant Samuel's range was A$4.06 to   |
|  3 Against the     |    A$4.46.                                                |
|    expert          |                                                           |
|  4 Deal timeline   |    A$ per share  3.00     4.00     5.00                   |
|  5 Sources         |    DCF           ....[////*///]....                       |
|                    |    Trading comps ....[//*//]........                      |
| Key dates          |    Precedents    ......[//*///]......                     |
|  27 Mar 2025 best  |    Grant Samuel  ........[=====]......                    |
|  and final offer   |            dashed 3.12            solid 4.43              |
|  27 Aug 2025       |                                                           |
|  implemented       |    Read next: how I valued it. Where I differ.            |
+--------------------+-----------------------------------------------------------+
```

Landing view, mobile (390 px):

```
+--------------------------------+
| DHG, CoStar scheme             |
| Contents (5 sections)       v  |
+--------------------------------+
| 1  My conclusion               |
| My range A$x.xx to A$x.xx      |
| includes the A$4.43 offer.     |
| Grant Samuel: A$4.06 to 4.46.  |
|                                |
| DCF       x.xx [///*///] x.xx  |
| Comps     x.xx [//*//] x.xx    |
| Precedent x.xx [//*///] x.xx   |
| G. Samuel 4.06 [=====] 4.46    |
|                                |
| Key dates (27 Mar to 27 Aug)   |
| Read next: how I valued it     |
+--------------------------------+
```

Where it takes its one visible risk. It is the quietest of the three and puts prose first: a visitor reads a short argument with exhibits inside it, not a dashboard. A recruiter who wants a chart in 30 seconds may scroll past text, so the conclusion and the chart must both fit above the fold on a phone.

Self-review against the defaults above.
- A serif for body text on a near-white page is one step from the cream page with a display serif and an earthy accent. The paper is a very pale neutral, the serif is for reading text only (headings and all data are sans), and the accent is a cool teal.
- Numbered sections could breach the rule on numbered markers. Here they are a reading sequence, as in the booklet, and the numbers appear only in the contents list and section headings.
- A contents column beside one column of text can drift towards newspaper imitation. I keep ordinary radius and rule weights and use one text column.
- Changes made in review: headings are sans, not serif, and the key dates are a plain list, not a card.
- The teal accent and the blue favourable colour are close under tritanopia (ΔE 12), so the accent never marks a variance.

Third-party requests: none.

### Comparison

| | A: workpaper | B: range first | C: disclosure document |
|---|---|---|---|
| First 30 seconds on a phone | Verdict and chart, with a sources switch | Verdict and chart only | Verdict and chart after a contents line |
| Provenance marker | Visible reference codes, switched on or off | Small marker that opens a source popover | Footnote-style marker that opens a source popover |
| Strongest for | An interviewer checking a number | A recruiter in 30 seconds | A hiring manager reading the argument |
| Main risk | Busy page with codes | Thin if the ranges are dull | Chart sits below text |
| Fonts | 28 KB, two files | 21 KB, one file | 39 KB, two files |

### Recommendation

Direction B, with direction A's "Show sources" switch added to it. B makes the football field the landing page, which is the 30-second read, and it has the lightest font load and one file to subset. The source switch costs one small script and little CSS, and it keeps the provenance marker visible to an interviewer without crowding the first screen, because it starts switched off. I would change the palette and type of A only if I chose A outright.

## Choice

On 4 October 2026 I chose direction B, range first, with direction A's "Show sources" switch added.

- The football field is the landing page, and each row opens the method behind it. Palette, type and wireframes are as in direction B above: Atkinson Hyperlegible Next as the only family, a cool white page, a deep blue accent, teal for favourable variances and orange for unfavourable ones.
- The "Show sources" switch comes from direction A. It starts switched off and prints a short reference code beside each sourced figure when switched on, so an interviewer can see every source at once. It needs one small script served from the site and a few lines of CSS.
- Light theme only at launch. A dark theme would double the contrast and colour-vision checks on every chart and hatch pattern, and I can add one later if it passes the same checks.
- Negative numbers use a true minus sign (for example −0.12) everywhere, matching the plus or minus sign every variance carries. I considered parentheses, which Grant Samuel's tables use, and rejected them because I would still need minus signs for variances and would end up with two conventions.

Why B: it gives the 30-second reader the verdict and the chart with nothing in between, and it has the lightest font load (one file of about 21 KB). Direction A would have put reference codes in front of every first-time visitor, and direction C would have put prose above the chart on a phone. I accept B's risk that the page is thin if my ranges are dull, so the gap analysis has to carry the story.

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

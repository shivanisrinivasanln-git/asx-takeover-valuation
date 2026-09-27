# Decisions

A dated log of decisions, the options considered and the reason for each. Newest entries go at the bottom.

## 26 September 2026: the project folder is the repository

Decided by the owner. The GitHub repository is `shivanisrinivasanln-git/asx-takeover-valuation`. The name does not depend on the deal chosen at checkpoint B, which matters because the Pages address includes the repository name, so renaming the repository later would change the site's address.

## 26 September 2026: LF line endings and the main branch

This machine's system git config sets `core.autocrlf=true`, which would check shell scripts out with CRLF line endings on a fresh Windows clone, and `sh` fails on those. `.gitattributes` sets `eol=lf` for text files.

The default branch is `main`, since deploys will run only from a green main branch.

## 26 September 2026: checkpoint A answers

Decided by the owner.

Time: finish as soon as possible without lowering quality, with more automation where it helps. There is no fixed deadline and no weekly-hours cap. The roadmap will compress the calendar by automating scaffolding, checks and data extraction, and will keep the learning and interview-preparation tasks, because the owner must be able to defend every number.

Excel: intermediate (formulas, lookups, basic charts). The model stays readable at that level, and the roadmap adds learning tasks on model layout and data tables.

Stack: lean towards a Python valuation engine feeding a static Next.js and React site, the tools the owner already knows. The final choice is at checkpoint C.

Hosting: a GitHub Pages project site at the owner's github.io address, linked from the existing portfolio. Options considered were a separate host such as Vercel, Netlify or Cloudflare Pages (previews, but another account and free-tier terms that can change) and a folder inside the portfolio repo (mixes histories). Pages needs no new account and costs nothing. It requires a fully static site, which checkpoint C must respect.

Budget and domain: A$0 and no custom domain, so there is no renewal that could lapse and break the link.

Analytics: none. No third-party script, no cookie banner, nothing to disclose.

## 27 September 2026: Domain Holdings Australia is the deal

I will value Domain Holdings Australia, acquired by CoStar Group by scheme at A$4.43 per share and implemented on 27 August 2025. Grant Samuel's range was A$4.06 to A$4.46.

Options considered: ten shortlisted deals, scored in [DEAL_SHORTLIST.md](DEAL_SHORTLIST.md). Domain scored highest: the expert used both DCF and multiples, it has close ASX-listed peers, and every document is free. The alternatives I weighed were each strongest on one thing: Boral for the expert changing its opinion (but the scrip consideration and missing ASX peers make it harder to value), Insignia Financial for a 2026 private equity contest (but the expert used one method), and Pacific Smiles for deal tactics (but no close listed peers). CSR and MMA Offshore scored above some of these but are orderly or sector-specific deals.

# Font source

The site uses one typeface, Atkinson Hyperlegible Next (SIL Open Font License 1.1), self-hosted so the pages make no third-party request. The subset in `site/static/fonts/` is 11.6 KB, against a 25 KB budget.

## Source

- File: `ofl/atkinsonhyperlegiblenext/AtkinsonHyperlegibleNext[wght].ttf` in the [Google Fonts repository](https://github.com/google/fonts/tree/main/ofl/atkinsonhyperlegiblenext), the variable font with a weight axis of 200 to 800.
- Git blob `92a357554bdcca62a7e80d5e3724bf4eb8932e5e`, 114,552 bytes, downloaded on 5 October 2026. The hash matches the one the GitHub API lists for the file.
- The licence text is `site/static/fonts/OFL.txt`, copied from the same folder. The OFL asks for it to travel with the font.

## What the subset keeps

- Basic Latin, the no-break and thin spaces, the en dash, curly quotes and the true minus sign (U+2212).
- The weight axis, narrowed to 400 to 600. The site uses 400 for text and 600 for headings, totals and preferred values.
- Kerning, ligatures, and the `tnum`, `pnum` and `lnum` features. The font has no `lnum` rules, so lining figures are its default. The default figures are proportional, so every number on the site sets `font-variant-numeric: tabular-nums lining-nums`.

## Measured on 5 October 2026

- With `tnum`, all ten digits advance 632 units. By default they range from 407 (the digit 1) to 648 (the digit 0).
- The true minus advances 606 units, slightly narrower than a tabular digit. It matters only if signed values are centred, because right-aligned columns line up from the right edge.

## Rebuild

```
python -m venv scratch-env
scratch-env/Scripts/python -m pip install fonttools==4.66.1 brotli==1.2.0
scratch-env/Scripts/python site/font-source/subset_font.py "AtkinsonHyperlegibleNext[wght].ttf" AtkinsonHyperlegibleNext-subset.woff2
```

The output differs between runs only in the timestamp the font header records.

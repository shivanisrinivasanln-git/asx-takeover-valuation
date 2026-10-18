# Font source

The site and the report use two typefaces: Source Serif 4 for page titles, section headings and the verdict sentence, and Source Sans 3 for everything else. Both are under the SIL Open Font License 1.1 and self-hosted, so the pages make no third-party request.

## Source

Both files come from the [Google Fonts repository](https://github.com/google/fonts), downloaded on 18 October 2026. Each git blob hash matches the one the GitHub API lists for the file.

| File | Git blob | Bytes |
|---|---|---|
| `ofl/sourcesans3/SourceSans3[wght].ttf` | `d259aa494fe7117141a2752a998a52c172bbd42b` | 646,340 |
| `ofl/sourceserif4/SourceSerif4[opsz,wght].ttf` | `40bbb58cb58e893ad0470f0bb291e096c73d3554` | 1,209,508 |

The licence texts, `OFL-SourceSans3.txt` and `OFL-SourceSerif4.txt`, are copied from the same folders (the OFL asks for them to travel with the fonts) and ship in `site/static/fonts` and `report/fonts`.

## Why the files are renamed

The Source Sans 3 licence reserves the font name "Source", and under the OFL a subset is a modified version, which may not use a reserved name. `subset_font.py` renames every file it writes to Site Sans or Site Serif and stops if a name record other than the copyright and licence lines still says "Source". Source Serif 4 has no reserved name; it is renamed the same way so the two read alike.

## What the files keep

- Site: `SiteSans-subset.woff2` (12.4 KB) and `SiteSerif-subset.woff2` (18.3 KB), each under the 25 KB budget. Basic Latin, the no-break and thin spaces, the en dash, curly quotes and the true minus sign (U+2212). The weight axis is narrowed to 400 to 600.
- Report: static Regular (400) and SemiBold (600) TrueType files of each family, with Latin-1, the figure space, the bullet and the ellipsis added.
- Source Serif 4's optical size axis is held at 20, its default text setting. The display end of the axis raises the stroke contrast.
- Kerning, ligatures, and the `tnum`, `pnum` and `lnum` features.

## Measured on 18 October 2026

- Both families draw tabular lining figures and a plain zero by default. In the site subsets all ten digits advance 497 units (sans) and 500 units (serif).
- The true minus advances 497 units in the sans, the same as a digit, and 530 in the serif, the same as the plus sign. Tables and chart labels are set in the sans.

## Rebuild

```
python -m venv scratch-env
scratch-env/Scripts/python -m pip install fonttools==4.66.1 brotli==1.2.0
scratch-env/Scripts/python site/font-source/subset_font.py "SourceSans3[wght].ttf" site/static/fonts/SiteSans-subset.woff2 "Site Sans"
scratch-env/Scripts/python site/font-source/subset_font.py "SourceSerif4[opsz,wght].ttf" site/static/fonts/SiteSerif-subset.woff2 "Site Serif"
scratch-env/Scripts/python site/font-source/subset_font.py "SourceSans3[wght].ttf" report/fonts/SiteSans-Regular.ttf "Site Sans" 400
scratch-env/Scripts/python site/font-source/subset_font.py "SourceSans3[wght].ttf" report/fonts/SiteSans-SemiBold.ttf "Site Sans" 600
scratch-env/Scripts/python site/font-source/subset_font.py "SourceSerif4[opsz,wght].ttf" report/fonts/SiteSerif-Regular.ttf "Site Serif" 400
scratch-env/Scripts/python site/font-source/subset_font.py "SourceSerif4[opsz,wght].ttf" report/fonts/SiteSerif-SemiBold.ttf "Site Serif" 600
```

The output differs between runs only in the timestamp the font header records.

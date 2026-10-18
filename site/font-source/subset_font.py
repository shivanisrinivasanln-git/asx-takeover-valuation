"""Subset Source Sans 3 or Source Serif 4 for the site or the report, under a new family name.

Usage:
    python subset_font.py SOURCE.ttf OUTPUT.woff2 FAMILY          web file, weights 400 to 600
    python subset_font.py SOURCE.ttf OUTPUT.ttf FAMILY WEIGHT     report file, one static weight

Source Sans 3 is licensed with the Reserved Font Name "Source", and a subset is a modified
version under the OFL, so every file this writes is renamed to FAMILY ("Site Sans" or
"Site Serif"). Source Serif 4 is renamed the same way so the two families read alike.

Needs fontTools and brotli (versions in README.md); neither is a dependency of the
valuation engine, so run it in a scratch environment.
"""

import sys

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

# Basic Latin, no-break space, thin space, en dash, curly quotes and the true minus sign.
WEB_UNICODES = [*range(0x20, 0x7F), 0xA0, 0x2009, 0x2013, 0x2018, 0x2019, 0x201C, 0x201D, 0x2212]
# The report adds Latin-1 (the multiplication sign and accented names), the figure space,
# the bullet and the ellipsis.
REPORT_UNICODES = sorted({*WEB_UNICODES, *range(0xA0, 0x100), 0x2007, 0x2022, 0x2026})
LAYOUT_FEATURES = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk", "tnum", "pnum", "lnum"]
# Licence, copyright, family and style names. The licence text itself ships beside the file.
NAME_IDS = [0, 1, 2, 3, 4, 5, 6, 13, 14, 16, 17]
# Optical size is held at the text setting (the font's default of 20 pt): the display end of
# the axis raises the stroke contrast.
TEXT_OPTICAL_SIZE = 20
WEB_WEIGHTS = (400, 600)
OLD_NAMES = ("Source Sans 3", "SourceSans3", "Source Serif 4", "SourceSerif4")
# Name records that may still say "Source": the copyright line, the licence and its URL.
NAMES_KEPT_AS_PUBLISHED = (0, 13, 14)


def rename(font: TTFont, family: str) -> None:
    for record in font["name"].names:
        text = record.toUnicode()
        for old in OLD_NAMES:
            text = text.replace(old, family if " " in old else family.replace(" ", ""))
        record.string = text
    left = [
        record.nameID
        for record in font["name"].names
        if record.nameID not in NAMES_KEPT_AS_PUBLISHED and "Source" in record.toUnicode()
    ]
    if left:
        raise SystemExit(f"name records still carry the reserved name: {left}")


def main(source_path: str, output_path: str, family: str, weight: int | None) -> None:
    font = TTFont(source_path)
    axes = {axis.axisTag for axis in font["fvar"].axes}

    options = subset.Options()
    options.layout_features = LAYOUT_FEATURES
    options.name_IDs = NAME_IDS
    options.hinting = False
    unicodes = WEB_UNICODES if weight is None else REPORT_UNICODES
    subsetter = subset.Subsetter(options)
    subsetter.populate(unicodes=unicodes)
    subsetter.subset(font)

    # Narrowing the axes before subsetting drops the .notdef variations the subsetter expects,
    # so it runs second.
    limits: dict[str, object] = {"wght": WEB_WEIGHTS if weight is None else weight}
    if "opsz" in axes:
        limits["opsz"] = TEXT_OPTICAL_SIZE
    font = instancer.instantiateVariableFont(font, limits, updateFontNames=weight is not None)
    rename(font, family)
    if weight is None:
        # The variable file keeps the source's default instance name; it is named for its
        # lightest weight here, which is now 400.
        for record in font["name"].names:
            if record.nameID == 1:
                record.string = family
            if record.nameID == 17:
                record.string = "Regular"
    font.flavor = "woff2" if weight is None else None
    font.save(output_path)

    cmap = TTFont(output_path).getBestCmap()
    missing = [hex(code) for code in unicodes if code not in cmap]
    if missing:
        raise SystemExit(f"code points missing from the subset: {missing}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else None)

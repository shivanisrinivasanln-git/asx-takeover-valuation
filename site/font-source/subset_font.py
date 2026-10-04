"""Subset Atkinson Hyperlegible Next to the characters the site uses, weights 400 to 600.

Usage: python subset_font.py SOURCE.ttf OUTPUT.woff2

Needs fontTools and brotli (versions in README.md); neither is a dependency of the
valuation engine, so run it in a scratch environment.
"""

import sys

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

# Basic Latin, no-break space, thin space, en dash, curly quotes and the true minus sign.
UNICODES = [*range(0x20, 0x7F), 0xA0, 0x2009, 0x2013, 0x2018, 0x2019, 0x201C, 0x201D, 0x2212]
LAYOUT_FEATURES = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk", "tnum", "pnum", "lnum"]
# Licence, copyright and family names. The licence text itself ships beside the file.
NAME_IDS = [0, 1, 2, 3, 4, 5, 6, 13, 14]


def main(source_path: str, output_path: str) -> None:
    font = TTFont(source_path)

    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = LAYOUT_FEATURES
    options.name_IDs = NAME_IDS
    options.hinting = False
    subsetter = subset.Subsetter(options)
    subsetter.populate(unicodes=UNICODES)
    subsetter.subset(font)

    # Narrowing the weight axis before subsetting drops the .notdef variations the subsetter
    # expects, so it runs second.
    font = instancer.instantiateVariableFont(font, {"wght": (400, 600)})
    font.flavor = "woff2"
    font.save(output_path)

    cmap = TTFont(output_path).getBestCmap()
    missing = [hex(code) for code in UNICODES if code not in cmap]
    if missing:
        raise SystemExit(f"code points missing from the subset: {missing}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

"""Compare the figures in the PDF report with valuation.json as the site displays them (task P6-03).

The template, report/report.typ, formats every figure itself in Typst. This module formats the
same values in Python with src/valuation/site_format.py and compares them with the numbers that
come out of the PDF's text, in reading order, so a mistyped, swapped or missing figure shows up.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from valuation.site_format import MINUS, number, signed

# A figure with a decimal part, with an optional sign, as the tables write it. Dates, page
# numbers and years have none, so they are not read as figures.
FIGURE = re.compile(rf"[+{MINUS}-]?\d[\d,]*\.\d+")


def pdf_text(pdf: Path) -> str:
    """The text of every page. Runs of white space, including non-breaking and narrow
    non-breaking spaces, become one space; the minus sign is left as the PDF holds it."""
    pages = PdfReader(pdf).pages
    return re.sub(r"\s+", " ", "\n".join(page.extract_text() for page in pages)).strip()


def figures_in(text: str) -> list[str]:
    return FIGURE.findall(text)


def expected_figures(valuation: dict[str, Any]) -> list[str]:
    """Every figure the template prints, in the order it prints them."""
    values = {key: entry["value"] for key, entry in valuation["values"].items()}
    figures: list[str] = []
    for row in valuation["football_field"]:
        figures.append(number(values[row["low_key"]]))
        if row["preferred_key"] is not None:
            figures.append(number(values[row["preferred_key"]]))
        figures.append(number(values[row["high_key"]]))
    figures.append(number(values["offer_price_aud"]))
    figures.append(number(values["undisturbed_share_price_aud"]))
    for key in (
        "dcf_business_operations_value_aud_m_low",
        "dcf_business_operations_value_aud_m_mid",
        "dcf_business_operations_value_aud_m_high",
        "expert_business_operations_value_aud_m_low",
        "expert_business_operations_value_aud_m_high",
    ):
        figures.append(number(values[key], 1))
    bridge = valuation["gap_bridge"]
    figures.append(number(bridge["start_value_per_share_aud"]))
    figures.append(signed(bridge["reconstruction_change_aud"], 4))
    for step in bridge["steps"]:
        figures.append(signed(step["change_aud"]))
        figures.append(number(step["cumulative_value_per_share_aud"]))
    figures.append(number(bridge["end_value_per_share_aud"]))
    return figures


def figure_problems(valuation: dict[str, Any], text: str) -> list[str]:
    """One line for each position where the PDF's figure differs from the expected one."""
    expected = expected_figures(valuation)
    found = figures_in(text)
    problems = [
        f"figure {position + 1}: the PDF has {actual}, valuation.json gives {wanted}"
        for position, (wanted, actual) in enumerate(zip(expected, found, strict=False))
        if wanted != actual
    ]
    if len(found) != len(expected):
        problems.append(f"the PDF holds {len(found)} figures, valuation.json gives {len(expected)}")
    return problems

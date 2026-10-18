"""The method and sources page: the register of every input with its source (task P5-13).

Each row is one entry of `assumptions.yaml`, in the file's order, with the document, page and date
that the entry carries. Nothing here is rewritten; the register shows the file as it is.
"""

from __future__ import annotations

from typing import Any

from valuation.inputs import Inputs
from valuation.precedent_sensitivity import base_range_deals
from valuation.site_format import aud, number, plain

# The flag reads Yes or No, as it does in the DCF assumptions table.
FLAG_KEY = "mid_year_discounting_flag"
UNIT_LABELS = {
    "pct": "%",
    "times": "x",
    "aud_m": "A$m",
    "aud": "A$",
    "million shares": "m shares",
}


def _value_text(key: str, value: float | tuple[float, ...]) -> str:
    if isinstance(value, tuple):
        # A date is written as year, month and day with no thousands separator in the year.
        return ", ".join(str(int(part)) for part in value)
    if key == FLAG_KEY:
        return "Yes" if value == 1 else "No"
    return plain(value)


SENSITIVITY = "precedent_completed_deals_only"
# The wording I approved on 17 October 2026 says "two of the four deals behind my precedent
# range". A change in the data that makes it untrue stops the build instead of printing it.
DEALS_IN_RANGE = 4
UNSUCCESSFUL_IN_RANGE = 2


def _figure(valuation: dict[str, Any], field: str, places: int, *, money: bool = False) -> str:
    value = float(valuation["sensitivities"][SENSITIVITY][field])
    return aud(value, places) if money else number(value, places)


def _completed_deals_note(valuation: dict[str, Any], inputs: Inputs) -> dict[str, Any]:
    """The sensitivity on completed deals only: the unsuccessful deals, then base and changed."""
    deals = base_range_deals(inputs)
    unsuccessful = [(deal, year) for deal, year, failed in deals if failed]
    if len(deals) != DEALS_IN_RANGE or len(unsuccessful) != UNSUCCESSFUL_IN_RANGE:
        raise ValueError(
            f"the completed-deals note says two of the four deals in my range were unsuccessful, "
            f"but the data has {len(unsuccessful)} of {len(deals)}"
        )
    unsuccessful.sort(key=lambda deal: deal[1])
    columns = (
        ("multiple_low_x", 1, False),
        ("multiple_high_x", 1, False),
        ("preferred_value_per_share_aud", 2, True),
        ("combined_value_per_share_aud_low", 2, True),
        ("combined_value_per_share_aud_high", 2, True),
    )
    return {
        "earlier_unsuccessful": {"deal": unsuccessful[0][0], "year": unsuccessful[0][1]},
        "later_unsuccessful": {"deal": unsuccessful[1][0], "year": unsuccessful[1][1]},
        "figures": {
            field: _figure(valuation, field, places, money=money)
            for field, places, money in columns
        },
        "base_figures": {
            field: _figure(valuation, f"base_{field}", places, money=money)
            for field, places, money in columns
        },
        "rows": [
            {
                "label": label,
                "cells": [
                    {
                        "key": f"{SENSITIVITY}:{prefix}{field}",
                        "text": _figure(valuation, f"{prefix}{field}", places),
                    }
                    for field, places, _ in columns
                ],
            }
            for label, prefix in (("My base case", "base_"), ("Completed deals only", ""))
        ],
    }


# Terms the pages use without defining them, for a reader new to valuation (task P5-20). Each
# definition says only what the site and the booklet use the term for.
TERMS = (
    (
        "Discounted cash flow (DCF)",
        "The value today of the cash a business is forecast to generate, each year's cash "
        "discounted at a rate that reflects the risk of receiving it.",
    ),
    (
        "EBITDA and EBITA",
        "Earnings before interest, tax, depreciation and amortisation, and earnings before "
        "interest, tax and amortisation. My range uses EBITDA multiples; the EBITA tables on the "
        "valuation page are a cross-check.",
    ),
    (
        "WACC",
        "Weighted average cost of capital: a discount rate built from the cost of equity and the "
        "cost of debt, weighted by how much of each a company like Domain uses.",
    ),
    (
        "Business operations, enterprise and equity value",
        "The value of the operating business; enterprise value adds other assets and "
        "liabilities; equity value subtracts adjusted net debt. Equity value divided by the "
        "diluted share count gives the value per share.",
    ),
    (
        "Control premium",
        "The amount a buyer pays above the market price of a small holding in order to control "
        "the company. Peer multiples come from such market prices, so I add one to them.",
    ),
    (
        "Scenario A",
        "The independent expert's base case for its DCF forecast, one of eight scenarios it "
        "disclosed; each of the others changes part of it.",
    ),
    (
        "Grant Samuel",
        "The independent expert that valued Domain for the scheme booklet, using a DCF and "
        "multiples of EBITDA and EBITA.",
    ),
    ("Nine", "Nine Entertainment, which owned about 60% of Domain before the scheme."),
    (
        "1HY25 and FY25",
        "The six months to 31 December 2024, and the year to 30 June 2025. Domain's financial "
        "year ends on 30 June.",
    ),
    (
        "Agents' dividends",
        "Dividends that Domain's subsidiaries pay to the real estate agents who own part of them. "
        "They are not Domain's cash, so the DCF deducts them.",
    ),
    (
        "Football field",
        "The chart on the overview page, with one bar for each method's range of value per share.",
    ),
)


def build_method_page(valuation: dict[str, Any], inputs: Inputs) -> dict[str, Any]:
    """Everything the method and sources template needs."""
    rows = [
        {
            "key": key,
            "value": _value_text(key, entry.value),
            "scalar": not isinstance(entry.value, tuple),
            "unit": "" if key == FLAG_KEY else UNIT_LABELS.get(entry.unit, entry.unit),
            "source": entry.source,
            "location": entry.location,
            "as_at": entry.as_at,
            "judgement": "My judgement" if entry.judgement else "",
            "note": entry.note,
        }
        for key, entry in inputs.assumptions.items()
    ]
    return {
        "rows": rows,
        "count": len(rows),
        "judgement_count": sum(1 for row in rows if row["judgement"]),
        "completed_deals": _completed_deals_note(valuation, inputs),
        "limitations": [row["text"] for row in inputs.tables["limitations"]],
        "terms": TERMS,
    }

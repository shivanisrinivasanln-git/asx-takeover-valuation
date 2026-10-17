"""The method and sources page: the register of every input with its source (task P5-13).

Each row is one entry of `assumptions.yaml`, in the file's order, with the document, page and date
that the entry carries. Nothing here is rewritten: the register is the file, shown.
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
    }

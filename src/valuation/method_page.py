"""The method and sources page: the register of every input with its source (task P5-13).

Each row is one entry of `assumptions.yaml`, in the file's order, with the document, page and date
that the entry carries. Nothing here is rewritten: the register is the file, shown.
"""

from __future__ import annotations

from typing import Any

from valuation.inputs import Inputs
from valuation.site_format import plain

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


def build_method_page(inputs: Inputs) -> dict[str, Any]:
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
    }

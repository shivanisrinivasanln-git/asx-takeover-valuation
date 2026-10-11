"""Compare the recalculated Excel model with the engine.

A problem is a named output cell that is missing, empty, an error, or differs from the engine's
figure by more than the tolerance for its unit. The stored values come from Excel's own
calculation (scripts/build_model.py), so a formula that Excel and the engine read differently
shows up here.
"""

from __future__ import annotations

import math
from collections.abc import Mapping

from openpyxl.workbook.workbook import Workbook

# Absolute tolerance by the unit a key's name promises. Money follows the project rule of
# A$0.005 per share and A$0.05m; the others are set at the same order of size.
TOLERANCE_BY_UNIT: dict[str, float] = {
    "aud": 0.005,
    "aud_m": 0.05,
    "shares_m": 0.05,
    "pct": 0.005,
    "x": 0.005,
    "years": 0.005,
}


def _destination(book: Workbook, name: str) -> tuple[str, str] | None:
    if name not in book.defined_names:
        return None
    destinations = list(book.defined_names[name].destinations)
    if len(destinations) != 1:
        return None
    sheet_name, reference = destinations[0]
    return sheet_name, reference.replace("$", "")


def value_problems(calculated: Workbook, expected: Mapping[str, Mapping[str, object]]) -> list[str]:
    """Compare every named output cell in a workbook holding calculated values with the engine."""
    problems: list[str] = []
    for key, entry in expected.items():
        destination = _destination(calculated, key)
        if destination is None or destination[0] not in calculated.sheetnames:
            problems.append(f"{key}: no defined name for a single cell")
            continue
        sheet_name, reference = destination
        cell = calculated[sheet_name][reference].value
        if cell is None:
            problems.append(f"{key}: {sheet_name}!{reference} is empty")
            continue
        if isinstance(cell, bool) or not isinstance(cell, int | float):
            problems.append(f"{key}: {sheet_name}!{reference} holds {cell!r}, not a number")
            continue
        engine = entry["value"]
        unit = entry["unit"]
        if not isinstance(engine, int | float) or not isinstance(unit, str):
            raise TypeError(f"{key}: the engine entry is malformed")
        tolerance = TOLERANCE_BY_UNIT[unit]
        if not math.isfinite(cell) or abs(cell - engine) > tolerance:
            problems.append(
                f"{key}: {sheet_name}!{reference} is {cell!r}, engine {engine!r}, "
                f"tolerance {tolerance}"
            )
    return problems

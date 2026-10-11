"""Reconcile the recalculated Excel model with the engine.

Two kinds of problem are reported, each as one line:

- value problems: a named output cell is missing, empty, an error, or differs from the engine's
  figure by more than the tolerance for its unit;
- stale model problems: the committed workbook's formulas, typed values or defined names differ
  from a workbook built now from the inputs, so the file was not rebuilt after a change.

The stored values come from Excel's own calculation (scripts/build_model.py), so a formula that
Excel and the engine read differently shows up as a value problem.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from pathlib import Path
from tempfile import TemporaryDirectory

from openpyxl import load_workbook
from openpyxl.workbook.workbook import Workbook

from valuation.inputs import Inputs
from valuation.output import build_valuation
from valuation.workbook import build_workbook

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
FORMULA_NUMBER_TOLERANCE = 1e-12


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


def _same(a: object, b: object) -> bool:
    if isinstance(a, int | float) and isinstance(b, int | float):
        return not isinstance(a, bool) and abs(a - b) <= FORMULA_NUMBER_TOLERANCE * max(1.0, abs(b))
    return a == b


def stale_problems(committed: Workbook, rebuilt: Workbook) -> list[str]:
    """Compare formulas, typed values and defined names of the committed file with a rebuild."""
    problems: list[str] = []
    if committed.sheetnames != rebuilt.sheetnames:
        return [f"sheets differ: {committed.sheetnames} against {rebuilt.sheetnames}"]
    for sheet_name in rebuilt.sheetnames:
        old, new = committed[sheet_name], rebuilt[sheet_name]
        seen: set[tuple[int, int]] = set()
        for row in new.iter_rows():
            for cell in row:
                if cell.value is None:
                    continue
                seen.add((cell.row, cell.column))
                stored = old.cell(cell.row, cell.column).value
                if not _same(stored, cell.value):
                    problems.append(
                        f"{sheet_name}!{cell.coordinate}: file has {stored!r}, "
                        f"a rebuild gives {cell.value!r}"
                    )
        for row in old.iter_rows():
            for cell in row:
                if cell.value is not None and (cell.row, cell.column) not in seen:
                    problems.append(
                        f"{sheet_name}!{cell.coordinate}: file has {cell.value!r}, a rebuild "
                        "leaves it empty"
                    )
    names_old = {name: _destination(committed, name) for name in committed.defined_names}
    names_new = {name: _destination(rebuilt, name) for name in rebuilt.defined_names}
    for name in sorted(set(names_old) | set(names_new)):
        if names_old.get(name) != names_new.get(name):
            problems.append(
                f"name {name}: file has {names_old.get(name)}, "
                f"a rebuild gives {names_new.get(name)}"
            )
    return problems


def reconcile(committed_path: Path, inputs: Inputs) -> list[str]:
    """Every problem found between the committed model file, a fresh rebuild and the engine."""
    expected = build_valuation(inputs)["values"]
    with TemporaryDirectory() as directory:
        rebuilt_path = Path(directory) / "rebuilt.xlsx"
        build_workbook(inputs).save(rebuilt_path)
        rebuilt = load_workbook(rebuilt_path)
    problems = stale_problems(load_workbook(committed_path), rebuilt)
    problems += value_problems(load_workbook(committed_path, data_only=True), expected)
    return problems

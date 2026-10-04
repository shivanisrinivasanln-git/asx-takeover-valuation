"""Load the hand-transcribed data under `data/extracted/` and check that each row has a source.

Each CSV file holds one table. Besides its own columns, every row must carry the
document it came from (`source`), the page or table (`location`) and the date of
the information (`as_at`), so any figure on the site can be traced.
"""

from __future__ import annotations

import csv
from pathlib import Path

TRACE_COLUMNS = ("source", "location", "as_at")


class ExtractedDataError(ValueError):
    """A data file has one or more problems; the message lists each."""


def trace_problems(csv_path: Path) -> list[str]:
    """Return one line per problem found in a data file."""
    with csv_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        missing = [column for column in TRACE_COLUMNS if column not in header]
        if missing:
            return [f"{csv_path.name}: missing column(s) {', '.join(missing)}"]
        problems: list[str] = []
        row_count = 0
        for number, row in enumerate(reader, start=2):
            row_count += 1
            problems += [
                f"{csv_path.name} line {number}: '{column}' is empty"
                for column in TRACE_COLUMNS
                if not (row[column] or "").strip()
            ]
        if row_count == 0:
            problems.append(f"{csv_path.name}: no data rows")
        return problems


def check_extracted_dir(directory: Path) -> None:
    """Raise if any CSV file in the folder has a row without a source."""
    problems: list[str] = []
    for csv_path in sorted(directory.glob("*.csv")):
        problems += trace_problems(csv_path)
    if problems:
        raise ExtractedDataError("\n".join(problems))


def load_rows(csv_path: Path) -> list[dict[str, str]]:
    """Return the rows of one data file after checking that each has a source."""
    problems = trace_problems(csv_path)
    if problems:
        raise ExtractedDataError("\n".join(problems))
    with csv_path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))

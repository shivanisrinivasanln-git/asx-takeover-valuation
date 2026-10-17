"""The deal timeline rows, read from the transcribed table.

The rows are the hand-transcribed `data/extracted/deal_timeline.csv`. A row is verified only when
I opened the source document (the evidence column says when).
"""

from __future__ import annotations

from pathlib import Path

from valuation.extracted import load_rows

TIMELINE_FILE = ("data", "extracted", "deal_timeline.csv")
IMPLEMENTATION_EVENT = "The scheme is implemented"


def load_timeline(root: Path) -> list[dict[str, str]]:
    """The timeline rows in date order, or an error if a row has no source."""
    return load_rows(root.joinpath(*TIMELINE_FILE))


def implementation_date(rows: list[dict[str, str]]) -> str:
    """The date of the row that records implementation of the scheme."""
    dates = [row["date"] for row in rows if row["event"].startswith(IMPLEMENTATION_EVENT)]
    if len(dates) != 1:
        raise ValueError(f"expected one implementation row in the timeline, found {len(dates)}")
    return dates[0]

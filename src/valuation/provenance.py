"""Reference codes for the sourced figures on the site (task P5-06).

A sourced figure is one that is an input in `assumptions.yaml` or a value transcribed from a
document into `data/extracted/`. Both carry a document, a page or table and a date. A figure the
engine calculates has no page to cite, so it carries no reference code here.

Codes are the same on every page. An input is `A` plus its position in the register (the order of
`assumptions.yaml`). A group of transcribed values that share one document, page and date is `T`
plus a number, in the order the tables are listed below.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from valuation.inputs import Inputs

# (table, label of the table on the site). The order fixes the numbers of the T codes.
TRANSCRIBED_TABLES = (
    ("comparable_multiples", "Peer multiples"),
    ("precedent_transactions", "Deal multiples"),
    ("valuation_summary", "Expert's valuation summary"),
)
# Tables whose rows carry a `measure` column, which names the chart a value was read from.
MEASURE_TABLES = ("comparable_multiples", "precedent_transactions")
REGISTER_PAGE = "method.html"
REGISTER_LINK_LABEL = "Input in the register"


@dataclass(frozen=True)
class Reference:
    code: str
    name: str
    source: str
    location: str
    as_at: str
    link: str | None
    link_label: str | None


def _table_key(table: str, row: Mapping[str, str]) -> tuple[str, str, str, str]:
    return (table, row["source"], row["location"], row["as_at"])


class ReferenceBook:
    """Every reference code the site can print, built from the inputs."""

    def __init__(self, inputs: Inputs) -> None:
        self._inputs: dict[str, Reference] = {
            key: Reference(
                code=f"A{position}",
                name=key,
                source=entry.source,
                location=entry.location,
                as_at=entry.as_at,
                link=f"{REGISTER_PAGE}#input-{key}",
                link_label=REGISTER_LINK_LABEL,
            )
            for position, (key, entry) in enumerate(inputs.assumptions.items(), start=1)
        }
        self._tables: dict[tuple[str, str, str, str], Reference] = {}
        for table, label in TRANSCRIBED_TABLES:
            for row in inputs.tables[table]:
                key = _table_key(table, row)
                if key in self._tables:
                    continue
                name = f"{label} on {row['measure'].upper()}" if table in MEASURE_TABLES else label
                self._tables[key] = Reference(
                    code=f"T{len(self._tables) + 1}",
                    name=name,
                    source=row["source"],
                    location=row["location"],
                    as_at=row["as_at"],
                    link=None,
                    link_label=None,
                )

    def for_input(self, key: str) -> Reference:
        return self._inputs[key]

    def for_table_row(self, table: str, row: Mapping[str, str]) -> Reference:
        return self._tables[_table_key(table, row)]

    def all_references(self) -> list[Reference]:
        return [*self._inputs.values(), *self._tables.values()]


class PageSources:
    """The references one page prints, collected as its builder marks figures."""

    def __init__(self, book: ReferenceBook) -> None:
        self.book = book
        self._used: dict[str, Reference] = {}

    def use(self, reference: Reference) -> str:
        """Record that the page prints this reference and return its code."""
        self._used[reference.code] = reference
        return reference.code

    def entries(self) -> list[Reference]:
        """The references used, inputs first and then transcribed groups, each in code order."""
        return sorted(self._used.values(), key=lambda ref: (ref.code[0], int(ref.code[1:])))

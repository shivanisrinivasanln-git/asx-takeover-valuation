"""The valuation page: every figure comes from valuation.json or a transcribed table, units are in
the headers, negatives use a true minus and the base case in the grid is the base value."""

import re
import statistics
from html.parser import HTMLParser
from pathlib import Path

import pytest

from valuation.inputs import Inputs, load_inputs
from valuation.output import build_valuation
from valuation.site_build import build_site
from valuation.site_format import MINUS, number
from valuation.site_frame import BuildInfo
from valuation.valuation_page import DCF_VALUE_ROWS, FORECAST_COLUMNS

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="17 October 2026", commit="0123456789abcdef0123456789abcdef01234567")
CSS = ROOT / "site" / "static" / "site.css"

Cell = tuple[str, dict[str, str], str]


class _Page(HTMLParser):
    """Tables as lists of cells, plus the scroll containers and spans with a data-key."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[dict[str, object]] = []
        self.scrollers: list[dict[str, str]] = []
        self.spans: list[tuple[dict[str, str], str]] = []
        self._cell: tuple[str, dict[str, str], list[str]] | None = None
        self._span: tuple[dict[str, str], list[str]] | None = None
        self._caption: list[str] | None = None
        self._row: list[Cell] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        if tag == "div" and "table-scroll" in values.get("class", ""):
            self.scrollers.append(values)
        if tag == "table":
            self.tables.append({"caption": "", "rows": [], "attrs": values})
        if tag == "caption":
            self._caption = []
        if tag == "tr":
            self._row = []
        if tag in ("th", "td"):
            self._cell = (tag, values, [])
        if tag == "span" and "data-key" in values:
            self._span = (values, [])

    def handle_endtag(self, tag: str) -> None:
        if tag == "caption" and self._caption is not None:
            self.tables[-1]["caption"] = "".join(self._caption).strip()
            self._caption = None
        if tag in ("th", "td") and self._cell is not None and self._row is not None:
            name, values, parts = self._cell
            self._row.append((name, values, "".join(parts).strip()))
            self._cell = None
        if tag == "tr" and self._row is not None:
            rows = self.tables[-1]["rows"]
            assert isinstance(rows, list)
            rows.append(self._row)
            self._row = None
        if tag == "span" and self._span is not None:
            self.spans.append((self._span[0], "".join(self._span[1]).strip()))
            self._span = None

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell[2].append(data)
        if self._caption is not None:
            self._caption.append(data)
        if self._span is not None:
            self._span[1].append(data)


@pytest.fixture(scope="module")
def inputs() -> Inputs:
    return load_inputs(ROOT)


@pytest.fixture(scope="module")
def valuation(inputs: Inputs) -> dict[str, object]:
    return build_valuation(inputs)


@pytest.fixture(scope="module")
def page() -> _Page:
    out_dir = ROOT / "build" / "site_test"
    build_site(ROOT, out_dir, BUILD)
    reader = _Page()
    reader.feed((out_dir / "valuation.html").read_text(encoding="utf-8"))
    return reader


def rows_of(table: dict[str, object]) -> list[list[Cell]]:
    rows = table["rows"]
    assert isinstance(rows, list)
    return rows


def table_with(page: _Page, caption_start: str) -> dict[str, object]:
    for table in page.tables:
        caption = table["caption"]
        assert isinstance(caption, str)
        if caption.startswith(caption_start):
            return table
    raise AssertionError(f"no table with caption starting {caption_start!r}")


def places_for_key(key: str) -> int:
    """Decimals for a value key: per-share values and multiples to two, A$m and shares to one."""
    for _, stem, places in DCF_VALUE_ROWS:
        if key.startswith(f"{stem}_"):
            return places
    if "_multiple_x_" in key or "_value_per_share_aud_" in key:
        return 2
    if key.endswith("_aud_m") or "_aud_m_" in key:
        return 1
    raise AssertionError(f"no precision rule for {key}")


FORECAST_PLACES = {field: places for field, _, places in FORECAST_COLUMNS}


def value_of(valuation: dict[str, object], key: str) -> float:
    values = valuation["values"]
    assert isinstance(values, dict)
    return float(values[key]["value"])


def test_every_data_key_cell_equals_the_value_in_valuation_json(
    page: _Page, valuation: dict[str, object]
) -> None:
    checked = 0
    cells = [cell for table in page.tables for row in rows_of(table) for cell in row]
    for _, attrs, text in cells:
        if "data-key" in attrs:
            expected = number(
                value_of(valuation, attrs["data-key"]), places_for_key(attrs["data-key"])
            )
            assert text == expected, (attrs["data-key"], text)
            checked += 1
    for attrs, text in page.spans:
        expected = number(value_of(valuation, attrs["data-key"]), 1)
        assert text == expected, (attrs["data-key"], text)
        checked += 1
    # Three DCF cases of ten lines, two ranges of three lines in two blocks for two methods,
    # the grid's base cell and two figures in a note.
    assert checked == 30 + 2 * 2 * 9 + 1 + 2


def test_the_forecast_table_is_the_forecast_in_valuation_json(
    page: _Page, valuation: dict[str, object]
) -> None:
    table = table_with(page, "Forecast from the second half of FY25")
    forecast = valuation["forecast"]
    assert isinstance(forecast, dict)
    body = [
        row
        for row in rows_of(table)
        if row and row[0][0] == "th" and row[0][1].get("scope") == "row"
    ]
    assert len(body) == len(forecast["rows"]) == 11
    for shown, source in zip(body, forecast["rows"], strict=True):
        assert shown[0][2] == source["period"]
        for _, attrs, text in shown[1:]:
            field = attrs["data-forecast"]
            assert text == number(source[field], FORECAST_PLACES[field]), (
                source["period"],
                field,
            )


def test_the_grid_is_five_by_five_and_the_boxed_cell_is_the_base_value(
    page: _Page, valuation: dict[str, object]
) -> None:
    table = table_with(page, "DCF value per share, A$. Rows are discount rates")
    grid = valuation["sensitivity"]
    assert isinstance(grid, dict)
    body = [row for row in rows_of(table) if row[0][0] == "th" and row[0][1].get("scope") == "row"]
    assert len(body) == 5
    boxed: list[str] = []
    for row_index, row in enumerate(body):
        assert row[0][2] == number(grid["discount_rates_pct"][row_index], 1)
        assert len(row) == 6
        for column, (_, attrs, text) in enumerate(row[1:]):
            assert text == number(grid["value_per_share_aud"][row_index][column], 2)
            if "base" in attrs.get("class", "").split():
                boxed.append(text)
                assert (row_index, column) == (grid["base_row"], grid["base_column"])
    assert boxed == [number(value_of(valuation, "dcf_value_per_share_aud_mid"), 2)]
    css = CSS.read_text(encoding="utf-8")
    assert re.search(r"\.sensitivity td\.base\s*\{[^}]*box-shadow[^}]*var\(--accent\)", css)


def test_the_grid_axes_are_the_rates_around_the_base(
    page: _Page, valuation: dict[str, object]
) -> None:
    table = table_with(page, "DCF value per share, A$. Rows are discount rates")
    header = rows_of(table)[0]
    grid = valuation["sensitivity"]
    assert isinstance(grid, dict)
    assert [text for _, _, text in header[1:]] == [
        number(growth, 1) for growth in grid["terminal_growth_rates_pct"]
    ]
    assert header[0][2] == "Discount rate (%)"


def test_numeric_headers_carry_their_unit(page: _Page) -> None:
    forecast = table_with(page, "Forecast from the second half of FY25")
    headers = [text for _, _, text in rows_of(forecast)[0]][1:]
    unitless = {"Discount factor"}
    assert [h for h in headers if not h.endswith(")") and h not in unitless] == []
    comparables = table_with(page, "Peer multiples printed")
    assert all(h.endswith("(x)") for _, _, h in rows_of(comparables)[0][2:])
    dcf = table_with(page, "Value by case")
    labels = [row[0][2] for row in rows_of(dcf)[1:]]
    assert all(label.endswith(")") for label in labels)


def test_negative_numbers_use_the_true_minus_and_numbers_are_right_aligned(page: _Page) -> None:
    texts = [
        (tag, attrs, text)
        for table in page.tables
        for row in rows_of(table)
        for tag, attrs, text in row
    ]
    numeric = [
        (tag, attrs, text)
        for tag, attrs, text in texts
        if re.fullmatch(r"[\u2212-]?[\d,]+(\.\d+)?", text)
    ]
    assert numeric
    assert [text for _, _, text in numeric if text.startswith("-")] == []
    for tag, attrs, text in numeric:
        # A four-digit year in the Announced column is a label, set in the text column.
        if tag == "td" and not re.fullmatch(r"\d{4}", text):
            assert "num" in attrs.get("class", "").split(), text
    css = CSS.read_text(encoding="utf-8")
    assert re.search(r"\.figures td\.num,\s*\.figures th\.num\s*\{[^}]*text-align:\s*end", css)
    assert any(text.startswith(MINUS) for page_span in page.spans for text in [page_span[1]])


def test_every_table_scrolls_in_a_labelled_focusable_container_with_a_sticky_first_column(
    page: _Page,
) -> None:
    assert len(page.scrollers) == len(page.tables) == 10
    for attrs in page.scrollers:
        assert attrs["tabindex"] == "0"
        assert attrs["role"] == "region"
        assert attrs["aria-label"].strip()
    css = CSS.read_text(encoding="utf-8")
    assert re.search(r"\.table-scroll\s*\{[^}]*overflow-x:\s*auto", css)
    assert re.search(r"tbody th\[scope=\"row\"\][^{]*\{[^}]*position:\s*sticky", css)


def test_assumption_rows_show_the_input_value_source_and_page(page: _Page, inputs: Inputs) -> None:
    table = table_with(page, "Inputs to the discounted cash flow")
    shown = {
        attrs["data-input"]: (text, row)
        for row in rows_of(table)[1:]
        for _, attrs, text in row
        if "data-input" in attrs
    }
    assert len(shown) == 13
    for key, (text, row) in shown.items():
        entry = inputs.assumptions[key]
        if key != "mid_year_discounting_flag":
            assert text == number(inputs.number(key), 1)
        assert row[3][2] == entry.source
        assert row[4][2] == entry.location
        assert row[5][2] == entry.as_at


def test_peer_multiples_and_their_summary_equal_the_transcribed_table(
    page: _Page, inputs: Inputs
) -> None:
    table = table_with(page, "Peer multiples printed")
    rows = rows_of(table)
    lookup = {
        (r["company"], r["measure"], r["basis"]): float(r["multiple_x"])
        for r in inputs.tables["comparable_multiples"]
    }
    columns = [
        ("ebitda", "forecast"),
        ("ebitda", "historical"),
        ("ebita", "forecast"),
        ("ebita", "historical"),
    ]
    peers = [
        row
        for row in rows[1:]
        if row[0][1].get("scope") == "row" and row[0][2] not in ("Lowest", "Median", "Highest")
    ]
    assert len(peers) == 8
    for row in peers:
        for (_, _, text), (measure, basis) in zip(row[2:], columns, strict=True):
            assert text == number(lookup[(row[0][2], measure, basis)], 1)
    summary = {row[0][2]: row for row in rows if row[0][2] in ("Lowest", "Median", "Highest")}
    for index, column in enumerate(columns):
        values = [v for (_, m, b), v in lookup.items() if (m, b) == column]
        assert summary["Lowest"][2 + index][2] == number(min(values), 1)
        assert summary["Median"][2 + index][2] == number(statistics.median(values), 1)
        assert summary["Highest"][2 + index][2] == number(max(values), 1)


def test_precedent_table_marks_the_unsuccessful_proposals(page: _Page, inputs: Inputs) -> None:
    table = table_with(page, "Deal multiples printed")
    status = {row[0][2]: row[3][2] for row in rows_of(table)[1:] if len(row) > 4}
    assert status["Scout24"] == "Unsuccessful proposal"
    assert status["Rightmove"] == "Unsuccessful proposal"
    assert status["Trade Me"] == "Completed"
    deals = {(r["deal"], r["announced"]) for r in inputs.tables["precedent_transactions"]}
    body = [row for row in rows_of(table)[1:] if row[0][2] not in ("Lowest", "Median", "Highest")]
    assert len(body) == len(deals)

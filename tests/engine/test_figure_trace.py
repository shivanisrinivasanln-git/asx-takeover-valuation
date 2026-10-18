"""Figure trace: every figure in valuation.json has a source or a test, and the list is exact."""

from dataclasses import replace
from pathlib import Path

import pytest

from valuation.figure_trace import (
    TraceError,
    TraceRow,
    changed_figures,
    dependency_problems,
    figure_groups,
    load_trace,
    match_rows,
    missing_tests,
    resolved_inputs,
    trace_lines,
    unknown_names,
    write_trace_listing,
)
from valuation.inputs import Inputs, load_inputs
from valuation.output import build_valuation

ROOT = Path(__file__).resolve().parents[2]
TRACE_FILE = ROOT / "data" / "written" / "figure_trace.csv"


@pytest.fixture(scope="module")
def inputs() -> Inputs:
    return load_inputs(ROOT)


@pytest.fixture(scope="module")
def valuation(inputs: Inputs) -> dict[str, object]:
    return build_valuation(inputs)


@pytest.fixture(scope="module")
def rows() -> list[TraceRow]:
    return load_trace(TRACE_FILE)


@pytest.fixture(scope="module")
def by_group(valuation: dict[str, object], rows: list[TraceRow]) -> dict[str, TraceRow]:
    return match_rows(figure_groups(valuation), rows)


@pytest.fixture(scope="module")
def moved(inputs: Inputs) -> dict[str, set[str]]:
    return changed_figures(inputs, build_valuation)


def row_for(rows: list[TraceRow], figure: str) -> TraceRow:
    return next(row for row in rows if row.figure == figure)


def test_every_figure_has_exactly_one_row_and_every_row_has_a_figure(
    valuation: dict[str, object], by_group: dict[str, TraceRow]
) -> None:
    # match_rows raises on a figure with no row or two rows, and on a row with no figure.
    assert list(by_group) == figure_groups(valuation)
    keys = valuation["values"]
    assert isinstance(keys, dict)
    assert sum(group.startswith("values.") for group in by_group) == len(keys)


def test_every_input_table_and_document_a_row_names_exists(
    rows: list[TraceRow], inputs: Inputs
) -> None:
    assert unknown_names(rows, inputs, ROOT) == []


def test_every_test_a_row_names_exists(rows: list[TraceRow]) -> None:
    assert missing_tests(rows, ROOT) == []


def test_no_figure_has_an_empty_source(
    valuation: dict[str, object], rows: list[TraceRow], inputs: Inputs
) -> None:
    lines = trace_lines(valuation, rows, inputs)
    # Every figure names a document and page (or a section of my notes), and a calculated one
    # names a test as well.
    assert [line["figure"] for line in lines if not line["sources"].strip()] == []
    assert [line["figure"] for line in lines if line["kind"] != "input" and not line["tests"]] == []
    assert [line["figure"] for line in lines if not line["how"].strip()] == []


def test_every_values_key_appears_in_the_listing(
    valuation: dict[str, object], rows: list[TraceRow], inputs: Inputs
) -> None:
    listed = {line["figure"] for line in trace_lines(valuation, rows, inputs)}
    keys = valuation["values"]
    assert isinstance(keys, dict)
    assert set(keys) <= listed


def test_a_figure_does_not_depend_on_an_input_its_row_leaves_out(
    by_group: dict[str, TraceRow], moved: dict[str, set[str]]
) -> None:
    assert dependency_problems(by_group, moved) == []


def test_every_input_that_moves_no_figure_is_one_i_hold_for_information(
    moved: dict[str, set[str]],
) -> None:
    # An input that moves nothing is either unused in assumptions.yaml or a figure missing from
    # valuation.json. Each one is listed here so a new one has to be looked at.
    never_moved = sorted(
        name for name, groups in moved.items() if not groups and not name.startswith("table:")
    )
    assert never_moved == [
        "control_premium_typical_high_pct",
        "control_premium_typical_low_pct",
        "listed_share_discount_to_underlying_high_pct",
        "listed_share_discount_to_underlying_low_pct",
        "special_dividend_aud",
    ]


def test_a_row_that_leaves_out_an_input_is_reported(
    rows: list[TraceRow], by_group: dict[str, TraceRow], moved: dict[str, set[str]]
) -> None:
    target = row_for(rows, "values.dcf_terminal_growth_pct")
    trimmed = replace(target, inputs=("discount_rate_high_pct",))
    swapped = {group: trimmed if row is target else row for group, row in by_group.items()}
    problems = dependency_problems(swapped, moved)
    assert any("also depends on terminal_growth_pct" in problem for problem in problems)


def test_a_row_that_names_an_input_that_moves_nothing_is_reported(
    rows: list[TraceRow], by_group: dict[str, TraceRow], moved: dict[str, set[str]]
) -> None:
    target = row_for(rows, "values.dcf_terminal_growth_pct")
    padded = replace(target, inputs=(*target.inputs, "special_dividend_aud"))
    swapped = {group: padded if row is target else row for group, row in by_group.items()}
    problems = dependency_problems(swapped, moved)
    assert any("names special_dividend_aud but none moves" in problem for problem in problems)


def test_a_figure_with_no_row_is_reported(
    rows: list[TraceRow], by_group: dict[str, TraceRow]
) -> None:
    without = [row for row in rows if row.figure != "values.offer_price_aud"]
    with pytest.raises(TraceError, match=r"no row for figure values\.offer_price_aud"):
        match_rows(list(by_group), without)


def test_a_row_with_no_figure_is_reported(
    rows: list[TraceRow], by_group: dict[str, TraceRow]
) -> None:
    stray = replace(rows[0], figure="values.no_such_key", line=999)
    with pytest.raises(TraceError, match="line 999"):
        match_rows(list(by_group), [*rows, stray])


def test_two_rows_for_one_figure_are_reported(
    rows: list[TraceRow], by_group: dict[str, TraceRow]
) -> None:
    doubled = replace(rows[0], figure="values.offer_*", line=998)
    with pytest.raises(TraceError, match="matches rows on lines"):
        match_rows(list(by_group), [*rows, doubled])


def test_a_test_that_does_not_exist_is_reported(rows: list[TraceRow]) -> None:
    broken = replace(rows[0], tests=("tests/engine/test_output.py::test_nothing_of_the_kind",))
    assert any("has no test" in problem for problem in missing_tests([broken], ROOT))
    elsewhere = replace(rows[0], tests=("tests/engine/test_missing_file.py::test_x",))
    assert any("not file::name" in problem for problem in missing_tests([elsewhere], ROOT))


def test_an_input_that_does_not_exist_is_reported(rows: list[TraceRow], inputs: Inputs) -> None:
    broken = replace(
        rows[0],
        inputs=(
            "no_such_input",
            "table:no_such_table",
            "doc:docs/BASE_CASE.md#No such heading",
            "doc:docs/NO_SUCH_FILE.md#Control premium",
        ),
    )
    assert len(unknown_names([broken], inputs, ROOT)) == 4


def test_a_reference_to_an_unknown_figure_is_reported(
    rows: list[TraceRow], by_group: dict[str, TraceRow]
) -> None:
    broken = replace(rows[0], inputs=("@values.no_such_key",))
    with pytest.raises(TraceError, match="does not match a figure"):
        resolved_inputs(broken, by_group)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("figure,kind,how,inputs,tests\nx,calculated,,a,t\n", "'how' is empty"),
        ("figure,kind,how,inputs,tests\nx,guess,why,a,t\n", "is not one of"),
        ("figure,kind,how,inputs,tests\nx,calculated,why,,\n", "names no input and no test"),
        ("figure,kind,how,inputs,tests\nx,calculated,why,a,\n", "names no test"),
        ("figure,kind,how,inputs,tests\nx,input,why,,t\n", "names no input or table"),
        ("figure,kind,how\nx,input,why\n", "columns are"),
    ],
)
def test_a_malformed_trace_file_is_rejected(tmp_path: Path, text: str, message: str) -> None:
    path = tmp_path / "figure_trace.csv"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(TraceError, match=message):
        load_trace(path)


def test_the_listing_is_written_with_one_line_per_figure(
    tmp_path: Path, valuation: dict[str, object]
) -> None:
    path = tmp_path / "figure_trace.csv"
    count = write_trace_listing(ROOT, path)
    assert count == len(figure_groups(valuation))
    assert len(path.read_text(encoding="utf-8").splitlines()) == count + 1

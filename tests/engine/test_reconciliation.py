"""The committed Excel model reconciles with the engine, and each check can fail.

The model file holds the values Excel calculated (scripts/build_model.py). The first test is the
reconciliation itself. The rest change a copy of the model in one way each and check that the
problem is reported: a changed formula, a changed typed input, a changed stored value, an empty
cell, an error cell and a value just outside the tolerance.
"""

import re
from dataclasses import replace
from pathlib import Path

import pytest
from openpyxl import load_workbook
from openpyxl.workbook.workbook import Workbook

from valuation.inputs import Inputs, load_inputs
from valuation.output import build_valuation
from valuation.reconcile import reconcile, stale_problems, value_problems
from valuation.workbook import build_workbook

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "model" / "domain_valuation_model.xlsx"
PER_SHARE_TOLERANCE_AUD = 0.005
MONEY_TOLERANCE_AUD_M = 0.05


@pytest.fixture(scope="module")
def inputs() -> Inputs:
    return load_inputs(ROOT)


@pytest.fixture(scope="module")
def expected(inputs: Inputs) -> dict[str, dict[str, object]]:
    values: dict[str, dict[str, object]] = build_valuation(inputs)["values"]
    return values


@pytest.fixture
def calculated() -> Workbook:
    return load_workbook(MODEL, data_only=True)


@pytest.fixture(scope="module")
def rebuilt(inputs: Inputs, tmp_path_factory: pytest.TempPathFactory) -> Workbook:
    path = tmp_path_factory.mktemp("rebuilt") / "model.xlsx"
    build_workbook(inputs).save(path)
    return load_workbook(path)


def cell_of(book: Workbook, key: str) -> tuple[str, str]:
    ((sheet_name, reference),) = book.defined_names[key].destinations
    return sheet_name, reference.replace("$", "")


def test_the_committed_model_reconciles_with_the_engine_and_is_not_stale(
    inputs: Inputs,
) -> None:
    assert reconcile(MODEL, inputs) == []


def test_every_key_has_a_calculated_number_within_tolerance(
    calculated: Workbook, expected: dict[str, dict[str, object]]
) -> None:
    assert len(expected) == 134
    assert value_problems(calculated, expected) == []


def test_a_changed_formula_is_reported_as_stale(rebuilt: Workbook) -> None:
    committed = load_workbook(MODEL)
    sheet, reference = cell_of(committed, "dcf_value_per_share_aud_mid")
    original = committed[sheet][reference].value
    assert isinstance(original, str)
    assert original.startswith("=")
    committed[sheet][reference].value = original + "*1.01"
    problems = stale_problems(committed, rebuilt)
    assert len(problems) == 1
    assert reference in problems[0]


def test_a_changed_typed_input_is_reported_as_stale(rebuilt: Workbook) -> None:
    committed = load_workbook(MODEL)
    sheet, reference = cell_of(committed, "terminal_growth_pct")
    committed[sheet][reference].value = 3.5
    problems = stale_problems(committed, rebuilt)
    assert len(problems) == 1
    assert "3.5" in problems[0]


def test_a_removed_defined_name_is_reported_as_stale(rebuilt: Workbook) -> None:
    committed = load_workbook(MODEL)
    del committed.defined_names["preferred_value_per_share_aud"]
    problems = stale_problems(committed, rebuilt)
    assert any("preferred_value_per_share_aud" in problem for problem in problems)


def test_a_stored_value_that_differs_from_the_engine_is_reported(
    calculated: Workbook, expected: dict[str, dict[str, object]]
) -> None:
    sheet, reference = cell_of(calculated, "preferred_value_per_share_aud")
    calculated[sheet][reference].value = 4.30
    problems = value_problems(calculated, expected)
    assert len(problems) == 1
    assert "preferred_value_per_share_aud" in problems[0]


def test_an_empty_named_cell_is_reported(
    calculated: Workbook, expected: dict[str, dict[str, object]]
) -> None:
    sheet, reference = cell_of(calculated, "dcf_terminal_value_aud_m_mid")
    calculated[sheet][reference].value = None
    problems = value_problems(calculated, expected)
    assert len(problems) == 1
    assert "is empty" in problems[0]


def test_an_error_cell_is_reported(
    calculated: Workbook, expected: dict[str, dict[str, object]]
) -> None:
    sheet, reference = cell_of(calculated, "wacc_pct_low")
    calculated[sheet][reference].value = "#NAME?"
    problems = value_problems(calculated, expected)
    assert len(problems) == 1
    assert "#NAME?" in problems[0]


@pytest.mark.parametrize(
    ("key", "offset", "reported"),
    [
        ("preferred_value_per_share_aud", PER_SHARE_TOLERANCE_AUD * 0.8, False),
        ("preferred_value_per_share_aud", PER_SHARE_TOLERANCE_AUD * 1.2, True),
        ("dcf_enterprise_value_aud_m_mid", MONEY_TOLERANCE_AUD_M * 0.8, False),
        ("dcf_enterprise_value_aud_m_mid", MONEY_TOLERANCE_AUD_M * 1.2, True),
    ],
)
def test_a_value_just_inside_the_tolerance_passes_and_just_outside_is_reported(
    calculated: Workbook,
    expected: dict[str, dict[str, object]],
    key: str,
    offset: float,
    reported: bool,
) -> None:
    sheet, reference = cell_of(calculated, key)
    stored = calculated[sheet][reference].value
    assert isinstance(stored, float)
    calculated[sheet][reference].value = stored + offset
    assert bool(value_problems(calculated, expected)) is reported


def test_a_workbook_that_excel_has_not_calculated_is_reported(
    expected: dict[str, dict[str, object]], tmp_path: Path, inputs: Inputs
) -> None:
    path = tmp_path / "raw.xlsx"
    build_workbook(inputs).save(path)
    problems = value_problems(load_workbook(path, data_only=True), expected)
    assert len(problems) > 100


def test_an_input_changed_without_rebuilding_the_model_is_reported_twice(
    inputs: Inputs,
) -> None:
    assumptions = dict(inputs.assumptions)
    assumptions["terminal_growth_pct"] = replace(assumptions["terminal_growth_pct"], value=3.5)
    changed = Inputs(assumptions=assumptions, tables=inputs.tables)
    problems = reconcile(MODEL, changed)
    assert any(problem.startswith("Assumptions!") for problem in problems)
    assert any(problem.startswith("dcf_value_per_share_aud_mid") for problem in problems)


def test_the_workbook_uses_only_the_standard_functions_the_decision_note_lists() -> None:
    allowed = {"IF", "INDEX", "MAX", "MEDIAN", "MIN", "SUM", "SUMPRODUCT"}
    used: set[str] = set()
    for sheet in load_workbook(MODEL):
        for row in sheet.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    used |= set(re.findall(r"([A-Z][A-Z0-9.]*)\(", cell.value))
    assert used == allowed

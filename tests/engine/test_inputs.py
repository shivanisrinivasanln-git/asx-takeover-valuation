"""Loading the engine inputs: the real files load, and anything missing stops the run."""

import shutil
from pathlib import Path

import pytest

from valuation.inputs import REQUIRED_ASSUMPTIONS, REQUIRED_TABLES, MissingInputError, load_inputs

ROOT = Path(__file__).resolve().parents[2]


def copy_inputs(destination: Path) -> Path:
    shutil.copy(ROOT / "assumptions.yaml", destination / "assumptions.yaml")
    shutil.copytree(ROOT / "data" / "extracted", destination / "data" / "extracted")
    return destination


def test_the_repository_inputs_load() -> None:
    inputs = load_inputs(ROOT)
    assert set(REQUIRED_ASSUMPTIONS) <= set(inputs.assumptions)
    assert set(REQUIRED_TABLES) <= set(inputs.tables)


def test_every_input_in_the_file_is_required_by_the_engine() -> None:
    # An input nobody reads would be a number I could not defend, so the lists must agree.
    inputs = load_inputs(ROOT)
    assert set(inputs.assumptions) == set(REQUIRED_ASSUMPTIONS)


def test_number_and_series_return_the_right_kind() -> None:
    inputs = load_inputs(ROOT)
    assert inputs.number("tax_rate_pct") == 30.0
    assert inputs.series("valuation_date_ymd") == (2024.0, 12.0, 31.0)
    with pytest.raises(ValueError, match="series"):
        inputs.number("valuation_date_ymd")
    with pytest.raises(ValueError, match="single number"):
        inputs.series("tax_rate_pct")


def test_table_number_finds_one_row_and_rejects_none_or_many() -> None:
    inputs = load_inputs(ROOT)
    assert inputs.table_number(
        "historical_pnl", "value", period="1HY25", line_item="revenue"
    ) == pytest.approx(217.2)
    with pytest.raises(ValueError, match="expected 1"):
        inputs.table_number("historical_pnl", "value", period="FY99", line_item="revenue")
    with pytest.raises(ValueError, match="expected 1"):
        inputs.table_number("historical_pnl", "value", line_item="revenue")


def test_a_missing_assumption_raises_and_names_it(tmp_path: Path) -> None:
    root = copy_inputs(tmp_path)
    text = (root / "assumptions.yaml").read_text(encoding="utf-8")
    start = text.index("tax_rate_pct:")
    end = text.index("\n\n", start)
    (root / "assumptions.yaml").write_text(text[:start] + text[end + 2 :], encoding="utf-8")
    with pytest.raises(MissingInputError, match="missing input 'tax_rate_pct'"):
        load_inputs(root)


def test_a_missing_data_file_raises_and_names_it(tmp_path: Path) -> None:
    root = copy_inputs(tmp_path)
    (root / "data" / "extracted" / "cash_flow.csv").unlink()
    with pytest.raises(MissingInputError, match=r"cash_flow\.csv: file not found"):
        load_inputs(root)


def test_every_problem_is_reported_in_one_error(tmp_path: Path) -> None:
    root = copy_inputs(tmp_path)
    (root / "data" / "extracted" / "cash_flow.csv").unlink()
    (root / "data" / "extracted" / "share_build.csv").unlink()
    with pytest.raises(MissingInputError) as error:
        load_inputs(root)
    assert "cash_flow.csv" in str(error.value)
    assert "share_build.csv" in str(error.value)


def test_a_missing_assumptions_file_raises(tmp_path: Path) -> None:
    with pytest.raises(MissingInputError, match=r"assumptions.yaml: file not found"):
        load_inputs(tmp_path)

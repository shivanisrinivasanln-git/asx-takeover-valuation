"""The sensitivity grid: its base cell is the DCF value and each cell is a full recalculation."""

from pathlib import Path

import pytest

from valuation.bridge import equity_bridge
from valuation.dcf import dcf_value
from valuation.forecast import forecast_from_inputs
from valuation.inputs import load_inputs
from valuation.sensitivity import (
    base_discount_rate_pct,
    base_value_per_share_aud,
    sensitivity_grid,
)

ROOT = Path(__file__).resolve().parents[2]


def test_the_grid_is_five_by_five_around_the_base_case() -> None:
    inputs = load_inputs(ROOT)
    grid = sensitivity_grid(inputs)
    assert grid.discount_rates_pct == pytest.approx((9.0, 9.5, 10.0, 10.5, 11.0))
    assert grid.terminal_growth_rates_pct == pytest.approx((3.0, 3.5, 4.0, 4.5, 5.0))
    assert len(grid.value_per_share_aud) == 5
    assert all(len(row) == 5 for row in grid.value_per_share_aud)


def test_the_base_cell_equals_the_dcf_value() -> None:
    inputs = load_inputs(ROOT)
    grid = sensitivity_grid(inputs)
    base = grid.value_per_share_aud[grid.base_row][grid.base_column]
    assert base == pytest.approx(base_value_per_share_aud(inputs), rel=1e-12)
    assert grid.discount_rates_pct[grid.base_row] == pytest.approx(base_discount_rate_pct(inputs))
    assert grid.terminal_growth_rates_pct[grid.base_column] == pytest.approx(4.0)


def test_the_base_cell_is_the_dcf_built_step_by_step() -> None:
    inputs = load_inputs(ROOT)
    operations = dcf_value(
        inputs, forecast_from_inputs(inputs), 10.0, 4.0, mid_year=True
    ).enterprise_value_aud_m
    expected = equity_bridge(inputs, operations, "mid").value_per_share_aud
    grid = sensitivity_grid(inputs)
    assert grid.value_per_share_aud[2][2] == pytest.approx(expected, rel=1e-12)


def test_value_falls_as_the_discount_rate_rises_and_rises_with_terminal_growth() -> None:
    grid = sensitivity_grid(load_inputs(ROOT))
    values = grid.value_per_share_aud
    for column in range(5):
        column_values = [values[row][column] for row in range(5)]
        assert column_values == sorted(column_values, reverse=True)
    for row in values:
        assert list(row) == sorted(row)


def test_a_corner_cell_is_a_full_recalculation() -> None:
    inputs = load_inputs(ROOT)
    operations = dcf_value(
        inputs, forecast_from_inputs(inputs), 9.0, 5.0, mid_year=True
    ).enterprise_value_aud_m
    expected = equity_bridge(inputs, operations, "mid").value_per_share_aud
    assert sensitivity_grid(inputs).value_per_share_aud[0][4] == pytest.approx(expected, rel=1e-12)

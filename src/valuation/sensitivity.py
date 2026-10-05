"""The DCF value per share for a grid of discount rates and terminal growth rates.

Rates are percentages and per-share values are A$. Every cell is a full recalculation of the DCF
at that pair of rates, so the table needs no approximation in the browser or the workbook.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from valuation.bridge import equity_bridge
from valuation.dcf import dcf_value
from valuation.forecast import YearCashFlow, forecast_from_inputs
from valuation.inputs import Inputs


@dataclass(frozen=True)
class SensitivityGrid:
    discount_rates_pct: tuple[float, ...]
    terminal_growth_rates_pct: tuple[float, ...]
    value_per_share_aud: tuple[tuple[float, ...], ...]
    base_row: int
    base_column: int


def base_discount_rate_pct(inputs: Inputs) -> float:
    """The middle of the adopted discount rate range."""
    return (inputs.number("discount_rate_low_pct") + inputs.number("discount_rate_high_pct")) / 2


def use_mid_year(inputs: Inputs) -> bool:
    return inputs.number("mid_year_discounting_flag") == 1.0


def value_per_share_aud(
    inputs: Inputs,
    cash_flows: Sequence[YearCashFlow],
    discount_rate_pct: float,
    terminal_growth_pct: float,
) -> float:
    """DCF value per share at one pair of rates, on the average of the two diluted share counts."""
    operations = dcf_value(
        inputs, cash_flows, discount_rate_pct, terminal_growth_pct, use_mid_year(inputs)
    ).enterprise_value_aud_m
    return equity_bridge(inputs, operations, "mid").value_per_share_aud


def base_value_per_share_aud(inputs: Inputs) -> float:
    return value_per_share_aud(
        inputs,
        forecast_from_inputs(inputs),
        base_discount_rate_pct(inputs),
        inputs.number("terminal_growth_pct"),
    )


def sensitivity_grid(inputs: Inputs) -> SensitivityGrid:
    cash_flows = forecast_from_inputs(inputs)
    steps = int(inputs.number("sensitivity_steps_each_side"))
    base_rate = base_discount_rate_pct(inputs)
    base_growth = inputs.number("terminal_growth_pct")
    rates = tuple(
        base_rate + offset * inputs.number("sensitivity_rate_step_pct")
        for offset in range(-steps, steps + 1)
    )
    growths = tuple(
        base_growth + offset * inputs.number("sensitivity_growth_step_pct")
        for offset in range(-steps, steps + 1)
    )
    values = tuple(
        tuple(value_per_share_aud(inputs, cash_flows, rate, growth) for growth in growths)
        for rate in rates
    )
    return SensitivityGrid(
        discount_rates_pct=rates,
        terminal_growth_rates_pct=growths,
        value_per_share_aud=values,
        base_row=steps,
        base_column=steps,
    )

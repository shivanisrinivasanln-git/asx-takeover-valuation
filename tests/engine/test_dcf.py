"""Discount rate, discounting and terminal value against hand-worked examples.

The example: free cash flows of 10 at the end of year 1 and 20 at the end of year 2, a discount
rate of 10% and a terminal growth rate of 3%, with a year 3 cash flow of 22 and no stub period.

End of year: 10 / 1.1 + 20 / 1.21 = 9.090909 + 16.528926 = 25.619835.
Mid-year (cash flows at 0.5 and 1.5 years): (10 + 20 / 1.1) / sqrt(1.1) = 26.870309.
Terminal value at the end of year 2: 22 / (0.10 - 0.03) = 314.285714, which is 329.625638 for
mid-year flows (times sqrt(1.1)), and its present value over 1.21 is 259.740260 (end of year)
or 272.417883 (mid-year).
"""

from pathlib import Path

import pytest

from valuation.dcf import (
    dcf_value,
    discount_factor,
    present_value_aud_m,
    terminal_value_aud_m,
    terminal_year_cash_flow_aud_m,
    time_of_cash_flow_years,
    wacc_for_pct,
    wacc_range_pct,
)
from valuation.forecast import YearCashFlow, forecast_from_inputs
from valuation.inputs import load_inputs

ROOT = Path(__file__).resolve().parents[2]
SIX_DECIMALS = 5e-7


def flow(year: int, cash_flow: float) -> YearCashFlow:
    return YearCashFlow(
        year=year,
        revenue_aud_m=0.0,
        ebitda_aud_m=0.0,
        corporate_cost_saving_aud_m=0.0,
        depreciation_aud_m=0.0,
        tax_aud_m=0.0,
        capex_aud_m=0.0,
        working_capital_increase_aud_m=0.0,
        agent_dividends_aud_m=0.0,
        free_cash_flow_aud_m=cash_flow,
    )


def test_discount_factor_matches_the_hand_value() -> None:
    assert discount_factor(10.0, 2.0) == pytest.approx(1 / 1.21, abs=SIX_DECIMALS)


def test_present_value_at_year_end_matches_the_hand_example() -> None:
    value = present_value_aud_m([flow(1, 10.0), flow(2, 20.0)], 10.0, 0.0, mid_year=False)
    assert value == pytest.approx(25.619835, abs=SIX_DECIMALS)


def test_present_value_mid_year_matches_the_hand_example() -> None:
    value = present_value_aud_m([flow(1, 10.0), flow(2, 20.0)], 10.0, 0.0, mid_year=True)
    assert value == pytest.approx(26.870309, abs=SIX_DECIMALS)


def test_timing_of_the_stub_and_each_year() -> None:
    assert time_of_cash_flow_years(0, 0.5, mid_year=False) == 0.5
    assert time_of_cash_flow_years(0, 0.5, mid_year=True) == 0.25
    assert time_of_cash_flow_years(1, 0.5, mid_year=False) == 1.5
    assert time_of_cash_flow_years(1, 0.5, mid_year=True) == 1.0
    assert time_of_cash_flow_years(10, 0.5, mid_year=False) == 10.5


def test_terminal_value_matches_the_hand_example() -> None:
    assert terminal_value_aud_m(22.0, 10.0, 3.0, mid_year=False) == pytest.approx(
        314.285714, abs=SIX_DECIMALS
    )
    assert terminal_value_aud_m(22.0, 10.0, 3.0, mid_year=True) == pytest.approx(
        329.625638, abs=SIX_DECIMALS
    )


def test_present_value_of_the_terminal_value_matches_the_hand_example() -> None:
    assert terminal_value_aud_m(22.0, 10.0, 3.0, mid_year=False) * discount_factor(
        10.0, 2.0
    ) == pytest.approx(259.740260, abs=SIX_DECIMALS)
    assert terminal_value_aud_m(22.0, 10.0, 3.0, mid_year=True) * discount_factor(
        10.0, 2.0
    ) == pytest.approx(272.417883, abs=SIX_DECIMALS)


def test_terminal_year_cash_flow_matches_the_hand_example() -> None:
    # Last year: revenue 100, EBITDA 40, saving 1. At 3% growth: revenue 103, EBITDA 41.2,
    # depreciation 10.3, capex 10.3, working capital 2% x 3 = 0.06, agents 100 x 50% x 2% = 1.0.
    # Taxable profit 41.2 + 1 - 10.3 = 31.9, tax 9.57, so
    # free cash flow = 31.9 - 9.57 + 10.3 - 10.3 - 0.06 - 1.0 = 21.27.
    last_year = YearCashFlow(
        year=10,
        revenue_aud_m=100.0,
        ebitda_aud_m=40.0,
        corporate_cost_saving_aud_m=1.0,
        depreciation_aud_m=0.0,
        tax_aud_m=0.0,
        capex_aud_m=0.0,
        working_capital_increase_aud_m=0.0,
        agent_dividends_aud_m=0.0,
        free_cash_flow_aud_m=0.0,
    )
    value = terminal_year_cash_flow_aud_m(
        last_year,
        growth_pct=3.0,
        long_term_depreciation_pct=10.0,
        long_term_capex_pct=10.0,
        working_capital_pct=2.0,
        tax_rate_pct=30.0,
        agent_dividend_pct=2.0,
        agent_revenue_share_pct=50.0,
    )
    assert value == pytest.approx(21.27, abs=SIX_DECIMALS)


def test_wacc_matches_the_hand_value_at_the_expert_risk_free_rate() -> None:
    inputs = load_inputs(ROOT)
    # Cost of equity 4.3 + 1.0 x 6 = 10.3, cost of debt (4.3 + 1.2) x 0.7 = 3.85,
    # WACC = 0.85 x 10.3 + 0.15 x 3.85 = 9.3325.
    assert wacc_for_pct(inputs, 4.3, 1.0, 85.0) == pytest.approx(9.3325, abs=SIX_DECIMALS)
    assert wacc_for_pct(inputs, 4.3, 1.1, 95.0) == pytest.approx(10.5475, abs=SIX_DECIMALS)


def test_wacc_range_at_both_risk_free_rates_rounds_to_the_expert_range() -> None:
    inputs = load_inputs(ROOT)
    mine = wacc_range_pct(inputs)
    expert = wacc_range_pct(inputs, "expert_risk_free_rate_pct")
    assert round(mine[0], 1) == round(expert[0], 1) == 9.3
    assert round(mine[1], 1) == round(expert[1], 1) == 10.5
    assert mine[0] < expert[0]
    assert mine[1] < expert[1]


def test_the_dcf_on_the_seeded_inputs_is_close_to_the_expert_scenario_a_bar() -> None:
    # The expert's scenario A NPV bar on p. 144, read from the chart, runs from about 2,402 at
    # 10.5% to 2,893 at 9.5%. This is a consistency check on my modelling choices, not a fit.
    inputs = load_inputs(ROOT)
    cash_flows = forecast_from_inputs(inputs)
    mid_year = inputs.number("mid_year_discounting_flag") == 1.0
    at_high_rate = dcf_value(inputs, cash_flows, 10.5, 4.0, mid_year).enterprise_value_aud_m
    at_low_rate = dcf_value(inputs, cash_flows, 9.5, 4.0, mid_year).enterprise_value_aud_m
    assert at_high_rate < at_low_rate
    assert at_high_rate == pytest.approx(2402.0, abs=25.0)
    assert at_low_rate == pytest.approx(2893.0, abs=25.0)


def test_enterprise_value_is_the_sum_of_its_parts_and_mid_year_is_higher() -> None:
    inputs = load_inputs(ROOT)
    cash_flows = forecast_from_inputs(inputs)
    mid = dcf_value(inputs, cash_flows, 10.0, 4.0, mid_year=True)
    end = dcf_value(inputs, cash_flows, 10.0, 4.0, mid_year=False)
    assert mid.enterprise_value_aud_m == pytest.approx(
        mid.present_value_of_cash_flows_aud_m + mid.present_value_of_terminal_value_aud_m,
        rel=1e-12,
    )
    assert mid.enterprise_value_aud_m > end.enterprise_value_aud_m
    # Every flow moves half a year sooner, except the stub, which moves a quarter of a year.
    ratio = mid.enterprise_value_aud_m / end.enterprise_value_aud_m
    assert 1.1**0.25 < ratio < 1.1**0.5
    assert (
        mid.present_value_of_terminal_value_aud_m / end.present_value_of_terminal_value_aud_m
        == (pytest.approx(1.1**0.5, rel=1e-12))
    )

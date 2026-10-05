"""Discount rate, discounting and terminal value for the DCF.

Rates are percentages (4.0 means 4.0%) and money is A$ millions. Nothing is rounded here.
Time is measured in years from the valuation date. Cash flows arrive at the end of each period,
or in the middle of it when `mid_year` is true.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from valuation import finance
from valuation.forecast import YearCashFlow, free_cash_flow_aud_m
from valuation.inputs import Inputs


@dataclass(frozen=True)
class DcfValue:
    present_value_of_cash_flows_aud_m: float
    terminal_value_aud_m: float
    present_value_of_terminal_value_aud_m: float
    enterprise_value_aud_m: float


def wacc_for_pct(
    inputs: Inputs, risk_free_rate_pct: float, beta: float, equity_weight_pct: float
) -> float:
    """WACC from the CAPM cost of equity, the cost of debt (risk-free plus margin) and gearing."""
    cost_of_equity = finance.cost_of_equity_pct(
        risk_free_rate_pct, beta, inputs.number("market_risk_premium_pct")
    )
    pre_tax_cost_of_debt = risk_free_rate_pct + inputs.number(
        "cost_of_debt_margin_over_risk_free_pct"
    )
    after_tax_cost_of_debt = finance.after_tax_cost_of_debt_pct(
        pre_tax_cost_of_debt, inputs.number("tax_rate_pct")
    )
    return finance.wacc_pct(cost_of_equity, after_tax_cost_of_debt, equity_weight_pct)


def wacc_range_pct(
    inputs: Inputs, risk_free_key: str = "risk_free_rate_pct"
) -> tuple[float, float]:
    """Lowest and highest WACC: low beta with low equity weight, high beta with high weight."""
    risk_free = inputs.number(risk_free_key)
    low = wacc_for_pct(
        inputs, risk_free, inputs.number("equity_beta_low"), inputs.number("equity_weight_low_pct")
    )
    high = wacc_for_pct(
        inputs,
        risk_free,
        inputs.number("equity_beta_high"),
        inputs.number("equity_weight_high_pct"),
    )
    return low, high


def time_of_cash_flow_years(year: int, stub_years: float, mid_year: bool) -> float:
    """Years from the valuation date to a cash flow; year 0 is the stub period."""
    if year == 0:
        return stub_years / 2 if mid_year else stub_years
    return stub_years + year - (0.5 if mid_year else 0.0)


def discount_factor(rate_pct: float, years: float) -> float:
    return float(1 / (1 + rate_pct / 100) ** years)


def present_value_aud_m(
    cash_flows: Sequence[YearCashFlow], rate_pct: float, stub_years: float, mid_year: bool
) -> float:
    return sum(
        row.free_cash_flow_aud_m
        * discount_factor(rate_pct, time_of_cash_flow_years(row.year, stub_years, mid_year))
        for row in cash_flows
    )


def terminal_value_aud_m(
    next_year_cash_flow_aud_m: float, rate_pct: float, growth_pct: float, mid_year: bool
) -> float:
    """Gordon growth value at the end of the last forecast year.

    The formula assumes the flows arrive at the end of each year. If they arrive mid-year, every
    flow comes half a year sooner, so the value is larger by half a year of the discount rate.
    """
    value = finance.growing_perpetuity_value_aud_m(next_year_cash_flow_aud_m, rate_pct, growth_pct)
    return value * (1 + rate_pct / 100) ** 0.5 if mid_year else value


def terminal_year_cash_flow_aud_m(
    last_year: YearCashFlow,
    growth_pct: float,
    long_term_depreciation_pct: float,
    long_term_capex_pct: float,
    working_capital_pct: float,
    tax_rate_pct: float,
    agent_dividend_pct: float,
    agent_revenue_share_pct: float,
) -> float:
    """Free cash flow of the year after the last forecast year, at the terminal growth rate.

    Revenue grows at the terminal rate, the EBITDA margin stays at its last value, depreciation and
    capital expenditure are at their long-term shares of revenue, working capital grows with the
    smaller change in revenue, and the agents' dividends follow the last forecast year's revenue.
    """
    revenue = last_year.revenue_aud_m * (1 + growth_pct / 100)
    ebitda = revenue * last_year.ebitda_aud_m / last_year.revenue_aud_m
    _, cash_flow = free_cash_flow_aud_m(
        ebitda_aud_m=ebitda,
        corporate_cost_saving_aud_m=last_year.corporate_cost_saving_aud_m,
        depreciation_aud_m=revenue * long_term_depreciation_pct / 100,
        capex_aud_m=revenue * long_term_capex_pct / 100,
        working_capital_increase_aud_m=(revenue - last_year.revenue_aud_m)
        * working_capital_pct
        / 100,
        agent_dividends_aud_m=last_year.revenue_aud_m
        * agent_revenue_share_pct
        / 100
        * agent_dividend_pct
        / 100,
        tax_rate_pct=tax_rate_pct,
    )
    return cash_flow


def dcf_value(
    inputs: Inputs,
    cash_flows: Sequence[YearCashFlow],
    rate_pct: float,
    terminal_growth_pct: float,
    mid_year: bool,
) -> DcfValue:
    """Enterprise value of business operations: discounted flows plus discounted terminal value."""
    stub_years = inputs.number("stub_period_years")
    last_year = cash_flows[-1]
    next_year = terminal_year_cash_flow_aud_m(
        last_year,
        terminal_growth_pct,
        inputs.number("depreciation_pct_of_revenue_long_term_pct"),
        inputs.number("capex_pct_of_revenue_long_term_pct"),
        inputs.number("working_capital_pct_of_revenue_pct"),
        inputs.number("tax_rate_pct"),
        inputs.number("agent_dividend_pct_of_prior_year_revenue_pct"),
        inputs.number("residential_and_mdc_share_of_revenue_pct"),
    )
    terminal = terminal_value_aud_m(next_year, rate_pct, terminal_growth_pct, mid_year)
    end_of_forecast_years = stub_years + last_year.year
    present_value_of_terminal = terminal * discount_factor(rate_pct, end_of_forecast_years)
    present_value_of_flows = present_value_aud_m(cash_flows, rate_pct, stub_years, mid_year)
    return DcfValue(
        present_value_of_cash_flows_aud_m=present_value_of_flows,
        terminal_value_aud_m=terminal,
        present_value_of_terminal_value_aud_m=present_value_of_terminal,
        enterprise_value_aud_m=present_value_of_flows + present_value_of_terminal,
    )

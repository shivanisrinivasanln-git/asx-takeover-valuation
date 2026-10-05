"""Unlevered free cash flow forecast: revenue to free cash flow for each year.

Rates are percentages (4.0 means 4.0%) and money is A$ millions. Nothing is rounded here.
Paths between two disclosed values are straight lines, which is my choice where the expert
published only end points (docs/DECISIONS.md).

Free cash flow each year is
    (EBITDA + corporate cost saving - depreciation) x (1 - tax rate)
    + depreciation - capital expenditure - increase in working capital - dividends to agents,
that is, tax on earnings before interest, with depreciation added back, less the cash the
business reinvests and the dividends paid to the agents who hold equity in its subsidiaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise

from valuation.inputs import Inputs

# The inputs are named for FY26 to FY30 (the early years) and FY31 to FY35, so five early years.
EARLY_YEARS = 5


@dataclass(frozen=True)
class ForecastParameters:
    base_revenue_aud_m: float
    base_ebitda_aud_m: float
    base_depreciation_aud_m: float
    prior_year_revenue_aud_m: float
    revenue_growth_pct: float
    ebitda_margin_waypoints_pct: tuple[tuple[int, float], ...]
    capex_early_pct: float
    capex_early_years: int
    capex_long_term_pct: float
    depreciation_long_term_pct: float
    depreciation_long_term_from_year: int
    working_capital_pct: float
    tax_rate_pct: float
    agent_dividend_pct: float
    agent_revenue_share_pct: float
    corporate_cost_saving_aud_m: float
    years: int


@dataclass(frozen=True)
class YearCashFlow:
    year: int
    revenue_aud_m: float
    ebitda_aud_m: float
    corporate_cost_saving_aud_m: float
    depreciation_aud_m: float
    tax_aud_m: float
    capex_aud_m: float
    working_capital_increase_aud_m: float
    agent_dividends_aud_m: float
    free_cash_flow_aud_m: float


def straight_line_pct(waypoints: tuple[tuple[int, float], ...], year: int) -> float:
    """Value at `year` on straight lines through the waypoints, flat beyond the last one."""
    ordered = sorted(waypoints)
    if year <= ordered[0][0]:
        return ordered[0][1]
    for (year_a, value_a), (year_b, value_b) in pairwise(ordered):
        if year <= year_b:
            return value_a + (value_b - value_a) * (year - year_a) / (year_b - year_a)
    return ordered[-1][1]


def free_cash_flow_aud_m(
    ebitda_aud_m: float,
    corporate_cost_saving_aud_m: float,
    depreciation_aud_m: float,
    capex_aud_m: float,
    working_capital_increase_aud_m: float,
    agent_dividends_aud_m: float,
    tax_rate_pct: float,
) -> tuple[float, float]:
    """Return (tax, free cash flow) for one period."""
    taxable_profit = ebitda_aud_m + corporate_cost_saving_aud_m - depreciation_aud_m
    tax = taxable_profit * tax_rate_pct / 100
    cash_flow = (
        taxable_profit
        - tax
        + depreciation_aud_m
        - capex_aud_m
        - working_capital_increase_aud_m
        - agent_dividends_aud_m
    )
    return tax, cash_flow


def forecast(parameters: ForecastParameters) -> list[YearCashFlow]:
    """Free cash flow for years 1 to `years` after the base year."""
    growth = parameters.revenue_growth_pct / 100
    base_depreciation_pct = parameters.base_depreciation_aud_m / parameters.base_revenue_aud_m * 100
    depreciation_waypoints = (
        (0, base_depreciation_pct),
        (parameters.depreciation_long_term_from_year, parameters.depreciation_long_term_pct),
    )
    rows: list[YearCashFlow] = []
    prior_revenue = parameters.base_revenue_aud_m
    for year in range(1, parameters.years + 1):
        revenue = prior_revenue * (1 + growth)
        ebitda = revenue * straight_line_pct(parameters.ebitda_margin_waypoints_pct, year) / 100
        depreciation = revenue * straight_line_pct(depreciation_waypoints, year) / 100
        capex_pct = (
            parameters.capex_early_pct
            if year <= parameters.capex_early_years
            else parameters.capex_long_term_pct
        )
        capex = revenue * capex_pct / 100
        working_capital_increase = (revenue - prior_revenue) * parameters.working_capital_pct / 100
        agent_dividends = (
            prior_revenue
            * parameters.agent_revenue_share_pct
            / 100
            * parameters.agent_dividend_pct
            / 100
        )
        tax, cash_flow = free_cash_flow_aud_m(
            ebitda,
            parameters.corporate_cost_saving_aud_m,
            depreciation,
            capex,
            working_capital_increase,
            agent_dividends,
            parameters.tax_rate_pct,
        )
        rows.append(
            YearCashFlow(
                year=year,
                revenue_aud_m=revenue,
                ebitda_aud_m=ebitda,
                corporate_cost_saving_aud_m=parameters.corporate_cost_saving_aud_m,
                depreciation_aud_m=depreciation,
                tax_aud_m=tax,
                capex_aud_m=capex,
                working_capital_increase_aud_m=working_capital_increase,
                agent_dividends_aud_m=agent_dividends,
                free_cash_flow_aud_m=cash_flow,
            )
        )
        prior_revenue = revenue
    return rows


def stub_cash_flow(
    parameters: ForecastParameters,
    first_half_revenue_aud_m: float,
    first_half_ebitda_aud_m: float,
    first_half_depreciation_aud_m: float,
    stub_years: float,
) -> YearCashFlow:
    """Free cash flow for the rest of the base year: its forecast less the half already reported.

    Working capital, the agents' dividends and the corporate saving are the annual amounts times
    the fraction of the year left. The row has year 0.
    """
    revenue = parameters.base_revenue_aud_m - first_half_revenue_aud_m
    ebitda = parameters.base_ebitda_aud_m - first_half_ebitda_aud_m
    depreciation = parameters.base_depreciation_aud_m - first_half_depreciation_aud_m
    capex = revenue * parameters.capex_early_pct / 100
    working_capital_increase = (
        (parameters.base_revenue_aud_m - parameters.prior_year_revenue_aud_m)
        * parameters.working_capital_pct
        / 100
        * stub_years
    )
    agent_dividends = (
        parameters.prior_year_revenue_aud_m
        * parameters.agent_revenue_share_pct
        / 100
        * parameters.agent_dividend_pct
        / 100
        * stub_years
    )
    saving = parameters.corporate_cost_saving_aud_m * stub_years
    tax, cash_flow = free_cash_flow_aud_m(
        ebitda,
        saving,
        depreciation,
        capex,
        working_capital_increase,
        agent_dividends,
        parameters.tax_rate_pct,
    )
    return YearCashFlow(
        year=0,
        revenue_aud_m=revenue,
        ebitda_aud_m=ebitda,
        corporate_cost_saving_aud_m=saving,
        depreciation_aud_m=depreciation,
        tax_aud_m=tax,
        capex_aud_m=capex,
        working_capital_increase_aud_m=working_capital_increase,
        agent_dividends_aud_m=agent_dividends,
        free_cash_flow_aud_m=cash_flow,
    )


def parameters_from_inputs(inputs: Inputs) -> ForecastParameters:
    """Forecast parameters from `assumptions.yaml` and the transcribed prior-year revenue."""
    base_revenue = inputs.number("fy25_revenue_aud_m")
    # Full years after the stub period: FY26 to the year of the projection end date.
    forecast_years = int(
        inputs.series("projection_end_date_ymd")[0] - (inputs.series("valuation_date_ymd")[0] + 1)
    )
    base_margin_pct = inputs.number("fy25_ebitda_aud_m") / base_revenue * 100
    return ForecastParameters(
        base_revenue_aud_m=base_revenue,
        base_ebitda_aud_m=inputs.number("fy25_ebitda_aud_m"),
        base_depreciation_aud_m=inputs.number("fy25_depreciation_and_other_amortisation_aud_m"),
        prior_year_revenue_aud_m=inputs.table_number(
            "historical_pnl", "value", period="FY24", line_item="revenue"
        ),
        revenue_growth_pct=inputs.number("revenue_growth_fy26_to_fy35_pct"),
        ebitda_margin_waypoints_pct=(
            (0, base_margin_pct),
            (EARLY_YEARS, inputs.number("ebitda_margin_fy30_pct")),
            (forecast_years, inputs.number("ebitda_margin_fy35_pct")),
        ),
        capex_early_pct=inputs.number("capex_pct_of_revenue_fy26_to_fy30_pct"),
        capex_early_years=EARLY_YEARS,
        capex_long_term_pct=inputs.number("capex_pct_of_revenue_long_term_pct"),
        depreciation_long_term_pct=inputs.number("depreciation_pct_of_revenue_long_term_pct"),
        depreciation_long_term_from_year=EARLY_YEARS,
        working_capital_pct=inputs.number("working_capital_pct_of_revenue_pct"),
        tax_rate_pct=inputs.number("tax_rate_pct"),
        agent_dividend_pct=inputs.number("agent_dividend_pct_of_prior_year_revenue_pct"),
        agent_revenue_share_pct=inputs.number("residential_and_mdc_share_of_revenue_pct"),
        corporate_cost_saving_aud_m=inputs.number("corporate_cost_saving_aud_m"),
        years=forecast_years,
    )


def forecast_from_inputs(inputs: Inputs) -> list[YearCashFlow]:
    """The stub period (year 0) followed by FY26 to FY35 (years 1 to 10)."""
    parameters = parameters_from_inputs(inputs)
    first_half = {
        item: inputs.table_number("historical_pnl", "value", period="1HY25", line_item=item)
        for item in ("revenue", "ebitda", "depreciation_and_other_amortisation")
    }
    stub = stub_cash_flow(
        parameters,
        first_half_revenue_aud_m=first_half["revenue"],
        first_half_ebitda_aud_m=first_half["ebitda"],
        first_half_depreciation_aud_m=-first_half["depreciation_and_other_amortisation"],
        stub_years=inputs.number("stub_period_years"),
    )
    return [stub, *forecast(parameters)]

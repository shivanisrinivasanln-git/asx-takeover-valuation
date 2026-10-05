"""The free cash flow forecast against a two-year example worked out by hand.

Base year: revenue 100, EBITDA 30, depreciation 8, prior-year revenue 90.
Revenue grows 10% a year. The EBITDA margin goes from 30% to 40% over two years in a straight
line (35%, 40%). Depreciation goes from 8% of revenue to 10% over two years (9%, 10%). Capital
expenditure is 12% of revenue in both years. Working capital is 2% of revenue, tax is 30%, the
agents' dividends are 2% of the prior year's revenue on a 50% share, and the corporate saving is 1.

Year 1: revenue 110, EBITDA 38.5, depreciation 9.9, capex 13.2, working capital 0.02 x 10 = 0.2,
agents 0.02 x 0.5 x 100 = 1.0. Taxable profit 38.5 + 1 - 9.9 = 29.6, tax 8.88, so
free cash flow = 29.6 - 8.88 + 9.9 - 13.2 - 0.2 - 1.0 = 16.22.

Year 2: revenue 121, EBITDA 48.4, depreciation 12.1, capex 14.52, working capital 0.22, agents 1.1.
Taxable profit 48.4 + 1 - 12.1 = 37.3, tax 11.19, so
free cash flow = 37.3 - 11.19 + 12.1 - 14.52 - 0.22 - 1.1 = 22.37.
"""

from pathlib import Path

import pytest

from valuation.forecast import (
    ForecastParameters,
    forecast,
    forecast_from_inputs,
    free_cash_flow_aud_m,
    straight_line_pct,
    stub_cash_flow,
)
from valuation.inputs import load_inputs

ROOT = Path(__file__).resolve().parents[2]

EXAMPLE = ForecastParameters(
    base_revenue_aud_m=100.0,
    base_ebitda_aud_m=30.0,
    base_depreciation_aud_m=8.0,
    prior_year_revenue_aud_m=90.0,
    revenue_growth_pct=10.0,
    ebitda_margin_waypoints_pct=((0, 30.0), (2, 40.0)),
    capex_early_pct=12.0,
    capex_early_years=2,
    capex_long_term_pct=9.0,
    depreciation_long_term_pct=10.0,
    depreciation_long_term_from_year=2,
    working_capital_pct=2.0,
    tax_rate_pct=30.0,
    agent_dividend_pct=2.0,
    agent_revenue_share_pct=50.0,
    corporate_cost_saving_aud_m=1.0,
    years=2,
)


def test_year_one_matches_the_hand_worked_figures() -> None:
    year_one = forecast(EXAMPLE)[0]
    assert year_one.revenue_aud_m == pytest.approx(110.0, rel=1e-12)
    assert year_one.ebitda_aud_m == pytest.approx(38.5, rel=1e-12)
    assert year_one.depreciation_aud_m == pytest.approx(9.9, rel=1e-12)
    assert year_one.capex_aud_m == pytest.approx(13.2, rel=1e-12)
    assert year_one.working_capital_increase_aud_m == pytest.approx(0.2, rel=1e-12)
    assert year_one.agent_dividends_aud_m == pytest.approx(1.0, rel=1e-12)
    assert year_one.tax_aud_m == pytest.approx(8.88, rel=1e-12)
    assert year_one.free_cash_flow_aud_m == pytest.approx(16.22, rel=1e-12)


def test_year_two_matches_the_hand_worked_figures() -> None:
    year_two = forecast(EXAMPLE)[1]
    assert year_two.revenue_aud_m == pytest.approx(121.0, rel=1e-12)
    assert year_two.ebitda_aud_m == pytest.approx(48.4, rel=1e-12)
    assert year_two.depreciation_aud_m == pytest.approx(12.1, rel=1e-12)
    assert year_two.capex_aud_m == pytest.approx(14.52, rel=1e-12)
    assert year_two.tax_aud_m == pytest.approx(11.19, rel=1e-12)
    assert year_two.free_cash_flow_aud_m == pytest.approx(22.37, rel=1e-12)


def test_the_forecast_has_one_row_per_year() -> None:
    rows = forecast(EXAMPLE)
    assert [row.year for row in rows] == [1, 2]


def test_capex_switches_to_the_long_term_rate_after_the_early_years() -> None:
    longer = ForecastParameters(**{**EXAMPLE.__dict__, "years": 3, "capex_early_years": 2})
    third = forecast(longer)[2]
    assert third.capex_aud_m == pytest.approx(third.revenue_aud_m * 0.09, rel=1e-12)


def test_free_cash_flow_helper_returns_tax_and_cash_flow() -> None:
    tax, cash_flow = free_cash_flow_aud_m(
        ebitda_aud_m=38.5,
        corporate_cost_saving_aud_m=1.0,
        depreciation_aud_m=9.9,
        capex_aud_m=13.2,
        working_capital_increase_aud_m=0.2,
        agent_dividends_aud_m=1.0,
        tax_rate_pct=30.0,
    )
    assert tax == pytest.approx(8.88, rel=1e-12)
    assert cash_flow == pytest.approx(16.22, rel=1e-12)


@pytest.mark.parametrize(
    ("year", "expected"),
    [(0, 30.0), (1, 35.0), (2, 40.0), (3, 40.0), (-1, 30.0)],
)
def test_straight_line_path_is_flat_outside_the_waypoints(year: int, expected: float) -> None:
    assert straight_line_pct(((0, 30.0), (2, 40.0)), year) == pytest.approx(expected)


def test_straight_line_path_through_three_waypoints() -> None:
    waypoints = ((0, 34.8), (5, 41.0), (10, 47.9))
    assert straight_line_pct(waypoints, 5) == pytest.approx(41.0)
    assert straight_line_pct(waypoints, 7) == pytest.approx(41.0 + (47.9 - 41.0) * 2 / 5)


def test_stub_period_matches_the_hand_worked_figures() -> None:
    # Stub: revenue 100 - 48 = 52, EBITDA 30 - 14 = 16, depreciation 8 - 3.5 = 4.5, capex 52 x 12%
    # = 6.24, working capital (100 - 90) x 2% x 0.5 = 0.1, agents 90 x 50% x 2% x 0.5 = 0.45,
    # saving 1 x 0.5 = 0.5. Taxable profit 16 + 0.5 - 4.5 = 12, tax 3.6,
    # free cash flow 12 - 3.6 + 4.5 - 6.24 - 0.1 - 0.45 = 6.11.
    stub = stub_cash_flow(
        EXAMPLE,
        first_half_revenue_aud_m=48.0,
        first_half_ebitda_aud_m=14.0,
        first_half_depreciation_aud_m=3.5,
        stub_years=0.5,
    )
    assert stub.year == 0
    assert stub.revenue_aud_m == pytest.approx(52.0, rel=1e-12)
    assert stub.capex_aud_m == pytest.approx(6.24, rel=1e-12)
    assert stub.tax_aud_m == pytest.approx(3.6, rel=1e-12)
    assert stub.free_cash_flow_aud_m == pytest.approx(6.11, rel=1e-12)


def test_the_forecast_built_from_the_repository_inputs() -> None:
    rows = forecast_from_inputs(load_inputs(ROOT))
    assert [row.year for row in rows] == list(range(11))
    stub, fy26, fy30, fy35 = rows[0], rows[1], rows[5], rows[10]
    # 1HY25 actuals from the booklet p. 118: revenue 217.2, EBITDA 77.8, depreciation 13.7
    assert stub.revenue_aud_m == pytest.approx(420.0 - 217.2)
    assert stub.ebitda_aud_m == pytest.approx(146.3 - 77.8)
    assert stub.depreciation_aud_m == pytest.approx(30.5 - 13.7)
    assert fy35.revenue_aud_m == pytest.approx(420.0 * 1.09**10)
    assert fy26.ebitda_aud_m / fy26.revenue_aud_m * 100 == pytest.approx(
        146.3 / 420.0 * 100 + (41.0 - 146.3 / 420.0 * 100) / 5
    )
    assert fy30.ebitda_aud_m / fy30.revenue_aud_m * 100 == pytest.approx(41.0)
    assert fy35.ebitda_aud_m / fy35.revenue_aud_m * 100 == pytest.approx(47.9)
    assert fy30.depreciation_aud_m / fy30.revenue_aud_m * 100 == pytest.approx(9.0)
    assert fy35.capex_aud_m == pytest.approx(fy35.revenue_aud_m * 0.09)
    assert all(row.free_cash_flow_aud_m > 0 for row in rows)

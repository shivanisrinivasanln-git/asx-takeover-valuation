"""The expert's DCF parameters, scenarios and NPV chart readings, transcribed from the booklet."""

from pathlib import Path

import pytest

from valuation.extracted import load_rows

DATA = Path(__file__).resolve().parents[2] / "data" / "extracted"
SCENARIOS = list("ABCDEFGH")
SELECTED_RANGE_AUD_M = (2775.0, 3025.0)
CHART_READING_TOLERANCE_AUD_M = 5.0
AXIS_AUD_M = (1500.0, 4000.0)


def parameter(name: str) -> float:
    rows = load_rows(DATA / "dcf_parameters.csv")
    return float(next(r["value"] for r in rows if r["parameter"] == name))


def chart_read(scenario: str, bound: str) -> float:
    rows = load_rows(DATA / "dcf_npv_chart_reads.csv")
    return float(
        next(r["value_aud_m"] for r in rows if r["scenario"] == scenario and r["bound"] == bound)
    )


def test_every_scenario_a_to_h_has_a_chart_reading_and_a_description() -> None:
    reads = {r["scenario"] for r in load_rows(DATA / "dcf_npv_chart_reads.csv")}
    described = {r["scenario"] for r in load_rows(DATA / "dcf_scenarios.csv")}
    assert reads - {"range_box"} == set(SCENARIOS)
    assert described == set(SCENARIOS)


def test_chart_calibration_reproduces_the_printed_value_range() -> None:
    low, high = SELECTED_RANGE_AUD_M
    assert chart_read("range_box", "low") == pytest.approx(low, abs=CHART_READING_TOLERANCE_AUD_M)
    assert chart_read("range_box", "high") == pytest.approx(high, abs=CHART_READING_TOLERANCE_AUD_M)
    assert parameter("business_operations_value_low") == low
    assert parameter("business_operations_value_high") == high


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_each_bar_is_a_range_inside_the_chart_axis(scenario: str) -> None:
    low, high = chart_read(scenario, "low"), chart_read(scenario, "high")
    assert AXIS_AUD_M[0] < low < high < AXIS_AUD_M[1]


def test_the_text_claims_about_the_chart_hold_for_the_readings() -> None:
    lows = [chart_read(s, "low") for s in SCENARIOS]
    highs = [chart_read(s, "high") for s in SCENARIOS]
    # p. 144: the range of NPVs across the scenarios is wider than the selected range.
    assert max(highs) - min(lows) > SELECTED_RANGE_AUD_M[1] - SELECTED_RANGE_AUD_M[0]
    # p. 145: the selected range sits towards the higher end of most of the NPV outcomes.
    selected_midpoint = sum(SELECTED_RANGE_AUD_M) / 2
    below = [
        s
        for s in SCENARIOS
        if (chart_read(s, "low") + chart_read(s, "high")) / 2 < selected_midpoint
    ]
    assert len(below) > len(SCENARIOS) / 2
    # Scenario B (12% yield growth) is the highest bar and Scenario C (9%) the lowest.
    assert max(SCENARIOS, key=lambda s: chart_read(s, "high")) == "B"
    assert min(SCENARIOS, key=lambda s: chart_read(s, "low")) == "C"


def test_yield_growth_scenarios_are_ordered_as_described() -> None:
    rows = load_rows(DATA / "dcf_scenarios.csv")
    yields = {
        r["scenario"]: float(r["value"])
        for r in rows
        if r["assumption"] == "residential_yield_growth"
    }
    assert yields == {"A": 10.0, "B": 12.0, "C": 9.0}


def test_model_parameters_are_consistent_with_each_other() -> None:
    assert parameter("discount_rate_adopted_low") >= parameter("wacc_calculated_low")
    assert parameter("discount_rate_adopted_high") == parameter("wacc_calculated_high")
    assert parameter("terminal_growth") > parameter("long_term_inflation")
    assert parameter("listed_company_costs_low") <= parameter("corporate_cost_saving")
    assert parameter("corporate_cost_saving") <= parameter("listed_company_costs_high")
    assert parameter("ebitda_margin_fy30") < parameter("ebitda_margin_fy35")
    assert parameter("capital_expenditure_pct_of_revenue_long_term") < parameter(
        "capital_expenditure_pct_of_revenue"
    )

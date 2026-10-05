"""The inputs in assumptions.yaml agree with the transcribed data and with what the booklet says."""

from pathlib import Path

import pytest

from valuation.assumptions import load_assumptions
from valuation.extracted import load_rows

ROOT = Path(__file__).resolve().parents[2]
ASSUMPTIONS = load_assumptions(ROOT / "assumptions.yaml")
DATA = ROOT / "data" / "extracted"
ONE_DECIMAL_ROUNDING = 0.05

# Inputs where I chose a number for something the booklet describes in words.
JUDGEMENT_INPUTS_P2_14 = {
    "revenue_growth_fy26_to_fy35_pct",
    "ebitda_margin_fy35_pct",
    "capex_pct_of_revenue_fy26_to_fy30_pct",
    "depreciation_pct_of_revenue_long_term_pct",
    "residential_and_mdc_share_of_revenue_pct",
}


def value(key: str) -> float:
    entry = ASSUMPTIONS[key].value
    assert isinstance(entry, float)
    return entry


def broker_median(metric: str, year: str) -> float:
    rows = load_rows(DATA / "broker_forecast_summary.csv")
    return float(
        next(
            r["value_aud_m"]
            for r in rows
            if r["statistic"] == "median" and r["metric"] == metric and r["fiscal_year"] == year
        )
    )


def test_inputs_where_i_chose_a_number_for_a_description_are_marked_as_judgement() -> None:
    for key in JUDGEMENT_INPUTS_P2_14:
        assert ASSUMPTIONS[key].judgement, key


def test_fy25_starting_points_are_the_broker_medians() -> None:
    assert value("fy25_revenue_aud_m") == broker_median("revenue", "FY25")
    assert value("fy25_ebitda_aud_m") == broker_median("ebitda", "FY25")
    expected = broker_median("ebitda", "FY25") - broker_median("ebita", "FY25")
    assert value("fy25_depreciation_and_other_amortisation_aud_m") == pytest.approx(
        expected, abs=ONE_DECIMAL_ROUNDING
    )


def test_nine_per_cent_growth_reproduces_the_expert_fy35_revenue() -> None:
    revenue_fy35 = (
        value("fy25_revenue_aud_m") * (1 + value("revenue_growth_fy26_to_fy35_pct") / 100) ** 10
    )
    # p. 141: "over $990 million in FY35"
    assert 990 < revenue_fy35 < 1000


def test_fy35_margin_is_just_below_48_and_above_the_fy30_margin() -> None:
    assert 47.0 < value("ebitda_margin_fy35_pct") < 48.0
    assert value("ebitda_margin_fy30_pct") < value("ebitda_margin_fy35_pct")


def test_fy25_margin_is_below_the_fy30_margin() -> None:
    fy25_margin = value("fy25_ebitda_aud_m") / value("fy25_revenue_aud_m") * 100
    assert fy25_margin == pytest.approx(34.8, abs=ONE_DECIMAL_ROUNDING)
    assert fy25_margin < value("ebitda_margin_fy30_pct")


def test_early_capex_matches_1hy25_and_the_known_shortfall_against_the_expert_average() -> None:
    rows = load_rows(DATA / "cash_flow.csv")
    capex_1hy25 = float(
        next(
            r["value"]
            for r in rows
            if r["period"] == "1HY25" and r["line_item"] == "capital_expenditure_pct_of_revenue"
        )
    )
    assert value("capex_pct_of_revenue_fy26_to_fy30_pct") == capex_1hy25
    average = (
        5 * value("capex_pct_of_revenue_fy26_to_fy30_pct")
        + 5 * value("capex_pct_of_revenue_long_term_pct")
    ) / 10
    # The expert average is "almost 9.5%"; this path is below it, as the note on the input says.
    assert average == pytest.approx(9.3, abs=0.01)
    assert average < 9.5


def test_segment_share_matches_the_ltm24_chart_labels() -> None:
    # LTM24 labels on p. 120: Residential 282.4, Media Developers and Commercial 50.9, total 406.0.
    share = (282.4 + 50.9) / 406.0 * 100
    assert value("residential_and_mdc_share_of_revenue_pct") == pytest.approx(
        share, abs=ONE_DECIMAL_ROUNDING
    )


def test_timing_inputs_describe_ten_and_a_half_years() -> None:
    assert ASSUMPTIONS["valuation_date_ymd"].value == (2024.0, 12.0, 31.0)
    assert ASSUMPTIONS["projection_end_date_ymd"].value == (2035.0, 6.0, 30.0)
    assert value("stub_period_years") + 10 == 10.5


def test_inputs_that_the_expert_discloses_match_the_dcf_parameter_transcription() -> None:
    rows = load_rows(DATA / "dcf_parameters.csv")
    transcribed = {r["parameter"]: float(r["value"]) for r in rows if r["unit"] in {"pct", "aud_m"}}
    assert value("tax_rate_pct") == transcribed["corporate_tax_rate"]
    assert value("terminal_growth_pct") == transcribed["terminal_growth"]
    assert value("ebitda_margin_fy30_pct") == transcribed["ebitda_margin_fy30"]
    assert (
        value("capex_pct_of_revenue_long_term_pct")
        == transcribed["capital_expenditure_pct_of_revenue_long_term"]
    )
    assert (
        value("working_capital_pct_of_revenue_pct") == transcribed["working_capital_pct_of_revenue"]
    )
    assert (
        value("agent_dividend_pct_of_prior_year_revenue_pct")
        == transcribed["agent_dividends_pct_of_prior_year_revenue"]
    )
    assert value("corporate_cost_saving_aud_m") == transcribed["corporate_cost_saving"]

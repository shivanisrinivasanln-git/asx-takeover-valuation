"""The broker forecasts in Appendix 1 reproduce the printed minimum, maximum and median."""

import statistics
from pathlib import Path

import pytest

from valuation.extracted import load_rows

DATA = Path(__file__).resolve().parents[2] / "data" / "extracted"
METRICS = ["revenue", "ebitda", "ebit"]
YEARS = ["FY25", "FY26"]
ROUNDING_AUD_M = 0.05


def broker_values(metric: str, year: str) -> list[float]:
    rows = load_rows(DATA / "broker_forecasts.csv")
    return [
        float(r["value_aud_m"]) for r in rows if r["metric"] == metric and r["fiscal_year"] == year
    ]


def printed(statistic: str, metric: str, year: str) -> float:
    rows = load_rows(DATA / "broker_forecast_summary.csv")
    return float(
        next(
            r["value_aud_m"]
            for r in rows
            if r["statistic"] == statistic and r["metric"] == metric and r["fiscal_year"] == year
        )
    )


def test_thirteen_brokers_with_the_printed_gaps() -> None:
    rows = load_rows(DATA / "broker_forecasts.csv")
    assert len({r["broker"] for r in rows}) == 13
    assert len(broker_values("revenue", "FY25")) == 13
    assert len(broker_values("ebitda", "FY26")) == 13
    assert len(broker_values("ebit", "FY25")) == 11


@pytest.mark.parametrize("metric", METRICS)
@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("statistic", ["minimum", "maximum", "median"])
def test_printed_statistic_matches_the_brokers(statistic: str, metric: str, year: str) -> None:
    values = broker_values(metric, year)
    computed = {
        "minimum": min(values),
        "maximum": max(values),
        "median": statistics.median(values),
    }[statistic]
    assert printed(statistic, metric, year) == pytest.approx(computed, abs=ROUNDING_AUD_M)


@pytest.mark.parametrize("year", YEARS)
def test_median_ebita_is_median_ebit_plus_the_acquired_amortisation(year: str) -> None:
    expected = printed("median", "ebit", year) + printed(
        "adjustment", "amortisation_of_acquired_intangibles", year
    )
    assert printed("median", "ebita", year) == pytest.approx(expected, abs=ROUNDING_AUD_M)


@pytest.mark.parametrize("metric", ["revenue", "ebitda", "ebita", "ebit"])
@pytest.mark.parametrize("year", YEARS)
def test_median_table_on_p122_matches_appendix_except_fy26_revenue(metric: str, year: str) -> None:
    on_p122 = printed("median_on_p122", metric, year)
    appendix = printed("median", metric, year)
    if (metric, year) == ("revenue", "FY26"):
        # p. 122 prints 454.0 and Appendix 1 prints 453.8, which is also the recomputed median.
        assert on_p122 - appendix == pytest.approx(0.2, abs=0.01)
    else:
        assert on_p122 == pytest.approx(appendix, abs=ROUNDING_AUD_M)


def test_median_costs_and_margin_quoted_in_the_text_follow_from_the_medians() -> None:
    costs = printed("median", "revenue", "FY25") - printed("median", "ebitda", "FY25")
    assert costs == pytest.approx(273.7, abs=ROUNDING_AUD_M)
    margin = printed("median", "ebitda", "FY25") / printed("median", "revenue", "FY25") * 100
    assert round(margin, 1) == 34.8

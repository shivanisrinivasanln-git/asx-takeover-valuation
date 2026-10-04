"""The historical profit and loss transcribed from the booklet adds up as printed."""

from pathlib import Path

import pytest

from valuation.extracted import load_rows

PNL_FILE = Path(__file__).resolve().parents[2] / "data" / "extracted" / "historical_pnl.csv"
PERIODS = ["FY21", "FY22", "FY23", "FY24", "1HY25"]
ROUNDING_AUD_M = 0.05
ROUNDING_PCT = 0.1
GROWTH_ROUNDING_PCT = 0.25
CONSUMER_SOLUTIONS_FY21_AUD_M = 5.5


def value(period: str, item: str) -> float:
    rows = load_rows(PNL_FILE)
    return float(next(r["value"] for r in rows if r["period"] == period and r["line_item"] == item))


def has(period: str, item: str) -> bool:
    return any(r["period"] == period and r["line_item"] == item for r in load_rows(PNL_FILE))


@pytest.mark.parametrize("period", PERIODS)
def test_revenue_is_the_sum_of_its_parts(period: str) -> None:
    parts = (
        value(period, "core_digital_revenue")
        + value(period, "print_revenue")
        + value(period, "corporate_revenue")
    )
    assert value(period, "revenue") == pytest.approx(parts, abs=ROUNDING_AUD_M)


@pytest.mark.parametrize("period", PERIODS)
def test_ebita_ebit_and_npat_follow_from_the_lines_above(period: str) -> None:
    ebita = value(period, "ebitda") + value(period, "depreciation_and_other_amortisation")
    assert value(period, "ebita") == pytest.approx(ebita, abs=ROUNDING_AUD_M)
    ebit = value(period, "ebita") + value(period, "amortisation_of_acquired_intangibles")
    assert value(period, "ebit") == pytest.approx(ebit, abs=ROUNDING_AUD_M)
    npat = sum(
        value(period, item)
        for item in (
            "ebit",
            "net_finance_costs",
            "income_tax_expense",
            "net_profit_attributable_to_non_controlling_interest",
            "significant_items_net_of_tax",
            "net_profit_from_discontinued_operations",
        )
    )
    assert value(period, "npat_attributable_to_domain_shareholders") == pytest.approx(
        npat, abs=ROUNDING_AUD_M
    )


SIGNIFICANT_LINES = (
    "significant_restructuring_costs",
    "significant_impairment",
    "significant_contingent_consideration",
    "significant_mergers_and_acquisitions",
    "significant_other",
)


@pytest.mark.parametrize("period", ["FY21", "FY22", "FY24", "1HY25"])
def test_significant_items_add_up(period: str) -> None:
    lines = sum(value(period, item) for item in SIGNIFICANT_LINES)
    assert value(period, "significant_items_before_tax") == pytest.approx(lines, abs=ROUNDING_AUD_M)


def test_fy23_significant_items_differ_from_the_printed_total_by_a_known_amount() -> None:
    # The booklet prints a total of (9.4) for lines that add to (9.6); the page was re-read twice.
    lines = sum(value("FY23", item) for item in SIGNIFICANT_LINES)
    assert lines - value("FY23", "significant_items_before_tax") == pytest.approx(-0.2, abs=0.01)


@pytest.mark.parametrize("period", PERIODS)
def test_significant_items_after_tax_add_up(period: str) -> None:
    after_tax = value(period, "significant_items_before_tax") + value(
        period, "significant_items_income_tax"
    )
    assert value(period, "significant_items_after_tax") == pytest.approx(
        after_tax, abs=ROUNDING_AUD_M
    )


@pytest.mark.parametrize("period", PERIODS)
def test_segment_revenue_adds_up_and_reconciles_to_revenue(period: str) -> None:
    segments = sum(
        value(period, item)
        for item in (
            "segment_revenue_residential",
            "segment_revenue_media_developers_commercial",
            "segment_revenue_agent_solutions",
            "segment_revenue_domain_insight",
            "segment_revenue_print",
        )
    )
    assert value(period, "segment_revenue_total") == pytest.approx(segments, abs=ROUNDING_AUD_M)
    discontinued = CONSUMER_SOLUTIONS_FY21_AUD_M if period == "FY21" else 0.0
    reconciled = value(period, "segment_revenue_total") + value(period, "corporate_revenue")
    assert value(period, "revenue") == pytest.approx(reconciled + discontinued, abs=ROUNDING_AUD_M)


@pytest.mark.parametrize("period", PERIODS)
def test_margins_match_the_printed_profit_and_revenue(period: str) -> None:
    ebitda_margin = value(period, "ebitda") / value(period, "revenue") * 100
    ebita_margin = value(period, "ebita") / value(period, "revenue") * 100
    assert value(period, "ebitda_margin") == pytest.approx(ebitda_margin, abs=ROUNDING_PCT)
    assert value(period, "ebita_margin") == pytest.approx(ebita_margin, abs=ROUNDING_PCT)


@pytest.mark.parametrize(
    ("period", "prior"), [("FY22", "FY21"), ("FY23", "FY22"), ("FY24", "FY23")]
)
def test_growth_rates_match_the_printed_profit_and_revenue(period: str, prior: str) -> None:
    for item, growth in (
        ("revenue", "revenue_growth"),
        ("ebitda", "ebitda_growth"),
        ("ebita", "ebita_growth"),
    ):
        computed = (value(period, item) / value(prior, item) - 1) * 100
        assert value(period, growth) == pytest.approx(computed, abs=GROWTH_ROUNDING_PCT)


def test_significant_items_after_tax_differ_between_pages_only_in_fy24() -> None:
    # Page 118 prints (6.0) for FY24 and page 120 prints (6.1); both pages were re-read.
    for period in PERIODS:
        difference = value(period, "significant_items_net_of_tax") - value(
            period, "significant_items_after_tax"
        )
        expected = 0.1 if period == "FY24" else 0.0
        assert difference == pytest.approx(expected, abs=0.01)

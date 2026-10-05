"""The precedent deals and Domain's implied multiples, from the booklet, agree with each other."""

from pathlib import Path

import pytest

from valuation.extracted import load_rows

DATA = Path(__file__).resolve().parents[2] / "data" / "extracted"
YEARS = ["fy24", "fy25", "fy26"]
ONE_DECIMAL_ROUNDING = 0.05
# The dividend to agents is itself rounded to 0.1, so grossing it up can differ by 0.07:
# 5.5 / 0.7 is 7.857 and the booklet prints 7.8 (footnote 44).
GROSS_UP_ROUNDING = 0.1

# Multiples the expert states in the text (pp. 147 to 149), as (deal, measure, basis, text value).
# The text rounds to whole numbers or ranges, so the labels may differ by up to the tolerance.
TEXT_FIGURES = [
    ("Trade Me", "ebitda", "historical", 17.0),
    ("Trade Me", "ebitda", "forecast", 15.0),
    ("Trade Me", "ebita", "historical", 20.0),
    ("Trade Me", "ebita", "forecast", 18.0),
    ("58.com", "ebitda", "historical", 14.0),
    ("58.com", "ebitda", "forecast", 13.0),
    ("58.com", "ebita", "historical", 15.0),
    ("58.com", "ebita", "forecast", 14.0),
    ("Scout24", "ebitda", "historical", 21.0),
    ("Scout24", "ebitda", "forecast", 20.0),
    ("Scout24", "ebita", "historical", 23.0),
    ("Scout24", "ebita", "forecast", 21.0),
    ("Rightmove", "ebitda", "historical", 24.0),
    ("Rightmove", "ebitda", "forecast", 22.0),
    ("Rightmove", "ebita", "historical", 24.0),
    ("Rightmove", "ebita", "forecast", 23.0),
    ("Adevinta", "ebitda", "historical", 21.0),
    ("Adevinta", "ebitda", "forecast", 18.0),
    ("Adevinta", "ebita", "historical", 39.0),
    ("Adevinta", "ebita", "forecast", 26.0),
    ("eBay Classifieds", "ebitda", "historical", 25.0),
    ("eBay Classifieds", "ebita", "historical", 27.0),
    ("ZPG", "ebitda", "historical", 30.0),
    ("ZPG", "ebitda", "forecast", 25.0),
    ("ZPG", "ebita", "forecast", 26.0),
    ("Idealista", "ebitda", "historical", 30.0),
    ("Idealista, 70% interest", "ebitda", "historical", 31.0),
]
TEXT_ROUNDING = 1.0


def label(deal: str, measure: str, basis: str) -> float:
    rows = load_rows(DATA / "precedent_transactions.csv")
    return float(
        next(
            r["multiple_x"]
            for r in rows
            if r["deal"] == deal and r["measure"] == measure and r["basis"] == basis
        )
    )


def implied(item: str) -> float:
    rows = load_rows(DATA / "domain_implied_multiples.csv")
    return float(next(r["value"] for r in rows if r["item"] == item))


def test_the_charts_give_28_labelled_multiples_for_nine_deals() -> None:
    rows = load_rows(DATA / "precedent_transactions.csv")
    assert len(rows) == 28
    assert len({r["deal"] for r in rows}) == 9
    assert all(r["location"].startswith(("p. 146", "p. 147")) for r in rows)


def test_the_two_unsuccessful_proposals_are_flagged() -> None:
    rows = load_rows(DATA / "precedent_transactions.csv")
    assert {r["deal"] for r in rows if r["unsuccessful"] == "yes"} == {"Rightmove", "Scout24"}


@pytest.mark.parametrize(("deal", "measure", "basis", "text_value"), TEXT_FIGURES)
def test_chart_label_agrees_with_the_text(
    deal: str, measure: str, basis: str, text_value: float
) -> None:
    assert label(deal, measure, basis) == pytest.approx(text_value, abs=TEXT_ROUNDING)


def test_excluded_deals_are_listed_with_a_reason() -> None:
    rows = load_rows(DATA / "precedent_exclusions.csv")
    assert len(rows) == 4
    assert all(r["reason"].strip() for r in rows)


def test_four_party_stated_multiples_each_have_a_release_and_a_status() -> None:
    rows = load_rows(DATA / "party_stated_multiples.csv")
    assert len(rows) == 4
    for row in rows:
        assert row["url"].startswith("https://")
        assert row["status"] in {"verified", "unverified"}
        assert row["evidence"].strip()
    assert {r["status"] for r in rows} == {"verified"}


def test_rightmove_multiple_follows_from_the_stated_enterprise_value_and_ebitda() -> None:
    # REA's announcement: about 6.1 billion pounds over EBITDA of 272 million pounds.
    rows = load_rows(DATA / "party_stated_multiples.csv")
    stated = float(next(r["ev_ebitda_x"] for r in rows if r["deal"].startswith("Rightmove")))
    assert stated == pytest.approx(6100 / 272, abs=0.1)


@pytest.mark.parametrize("year", YEARS)
def test_adjusted_earnings_follow_from_the_dividends_to_agents(year: str) -> None:
    dividends = implied(f"dividends_paid_to_non_controlling_interests_{year}")
    gross_up = dividends / (1 - implied("tax_rate_used_to_gross_up_dividends") / 100)
    for measure in ("ebitda", "ebita"):
        adjustment = implied(f"earnings_attributable_to_non_controlling_interests_{measure}_{year}")
        assert adjustment == pytest.approx(-gross_up, abs=GROSS_UP_ROUNDING)
        adjusted = implied(f"{measure}_{year}") + adjustment
        assert implied(f"adjusted_{measure}_{year}") == pytest.approx(
            adjusted, abs=ONE_DECIMAL_ROUNDING
        )


@pytest.mark.parametrize("measure", ["ebitda", "ebita"])
@pytest.mark.parametrize("year", YEARS)
def test_implied_multiples_follow_from_the_value_range_and_adjusted_earnings(
    measure: str, year: str
) -> None:
    earnings = implied(f"adjusted_{measure}_{year}")
    low = implied("business_operations_value_low") / earnings
    high = implied("business_operations_value_high") / earnings
    assert implied(f"implied_{measure}_multiple_{year}_low") == pytest.approx(
        low, abs=ONE_DECIMAL_ROUNDING
    )
    assert implied(f"implied_{measure}_multiple_{year}_high") == pytest.approx(
        high, abs=ONE_DECIMAL_ROUNDING
    )


def test_the_earnings_for_valuation_agree_with_the_other_transcriptions() -> None:
    pnl = {
        (r["period"], r["line_item"]): float(r["value"])
        for r in load_rows(DATA / "historical_pnl.csv")
    }
    assert implied("ebitda_fy24") == pnl[("FY24", "ebitda")]
    assert implied("ebita_fy24") == pnl[("FY24", "ebita")]
    cash = {
        (r["period"], r["line_item"]): float(r["value"]) for r in load_rows(DATA / "cash_flow.csv")
    }
    assert (
        implied("dividends_paid_to_non_controlling_interests_fy24")
        == -cash[("FY24", "dividends_paid_to_non_controlling_interest")]
    )
    assert (
        implied("dividends_paid_to_non_controlling_interests_fy25")
        == -cash[("1HY25", "dividends_paid_to_non_controlling_interest")]
    )
    medians = {
        (r["fiscal_year"], r["metric"]): float(r["value_aud_m"])
        for r in load_rows(DATA / "broker_forecast_summary.csv")
        if r["statistic"] == "median"
    }
    assert implied("ebitda_fy25") == medians[("FY25", "ebitda")]
    assert implied("ebitda_fy26") == medians[("FY26", "ebitda")]
    assert implied("ebita_fy25") == medians[("FY25", "ebita")]
    assert implied("ebita_fy26") == medians[("FY26", "ebita")]

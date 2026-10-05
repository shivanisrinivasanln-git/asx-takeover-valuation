"""The peer multiples printed on p. 150 agree with the ranges the expert states in the text."""

from pathlib import Path

import pytest

from valuation.extracted import load_rows

DATA = Path(__file__).resolve().parents[2] / "data" / "extracted"
KEPT_PEERS = {
    "REA Group",
    "CAR Group",
    "SEEK",
    "Hemnet",
    "Scout24",
    "Rightmove",
    "Baltic Classifieds Group",
    "Vend Marketplaces",
}
GROUPS = {
    "CAR Group and SEEK": ["CAR Group", "SEEK"],
    "International property marketplaces excluding Hemnet": ["Scout24", "Rightmove"],
    "Baltic Classifieds Group and Vend Marketplaces": [
        "Baltic Classifieds Group",
        "Vend Marketplaces",
    ],
    "REA Group": ["REA Group"],
    "Hemnet": ["Hemnet"],
}
# The text gives whole numbers and rounds a little differently from the labels:
# 22.8 is 22 on p. 151 and 23 on p. 154.
TEXT_ROUNDING_X = 1.0


def multiple(company: str, measure: str, basis: str) -> float:
    rows = load_rows(DATA / "comparable_multiples.csv")
    return float(
        next(
            r["multiple_x"]
            for r in rows
            if r["company"] == company and r["measure"] == measure and r["basis"] == basis
        )
    )


def test_each_kept_peer_has_all_four_multiples_and_a_page() -> None:
    rows = load_rows(DATA / "comparable_multiples.csv")
    for company in KEPT_PEERS:
        mine = [r for r in rows if r["company"] == company]
        assert {(r["measure"], r["basis"]) for r in mine} == {
            ("ebitda", "historical"),
            ("ebitda", "forecast"),
            ("ebita", "historical"),
            ("ebita", "forecast"),
        }, company
        assert all(r["location"].startswith("p. 150") for r in mine)


def test_peer_set_lists_the_eight_kept_and_the_five_set_aside() -> None:
    rows = load_rows(DATA / "comparable_peer_set.csv")
    kept = {r["company"] for r in rows if r["treatment"] == "kept"}
    assert kept == KEPT_PEERS
    assert {r["company"] for r in rows if r["treatment"] != "kept"} == {
        "Zillow",
        "CoStar",
        "Cars.com",
        "Autohome",
        "Auto Trader Group",
    }


@pytest.mark.parametrize("row", load_rows(DATA / "comparable_multiple_ranges.csv"))
def test_label_range_agrees_with_the_range_stated_in_the_text(row: dict[str, str]) -> None:
    values = [multiple(c, row["measure"], row["basis"]) for c in GROUPS[row["group"]]]
    assert min(values) == pytest.approx(float(row["low_x"]), abs=TEXT_ROUNDING_X)
    assert max(values) == pytest.approx(float(row["high_x"]), abs=TEXT_ROUNDING_X)


def test_ebita_multiple_is_above_the_ebitda_multiple_for_every_peer_and_basis() -> None:
    # EBITA is lower than EBITDA, so the same value gives a higher multiple (p. 132).
    for company in KEPT_PEERS:
        for basis in ("historical", "forecast"):
            assert multiple(company, "ebita", basis) > multiple(company, "ebitda", basis)

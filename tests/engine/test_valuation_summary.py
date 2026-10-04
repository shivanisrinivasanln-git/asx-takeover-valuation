"""The expert valuation summary and share build, transcribed from the booklet, add up as printed."""

from pathlib import Path

import pytest

from valuation.extracted import load_rows

DATA = Path(__file__).resolve().parents[2] / "data" / "extracted"
CASES = ("low", "high")
PRINTED_ROUNDING_AUD_M = 0.05
PRINTED_ROUNDING_AUD = 0.005


def summary_value(item: str, case: str) -> float:
    rows = load_rows(DATA / "valuation_summary.csv")
    return float(next(r["value"] for r in rows if r["item"] == item and r["case"] == case))


def build_value(item: str, case: str = "") -> int:
    rows = load_rows(DATA / "share_build.csv")
    return int(next(r["value"] for r in rows if r["item"] == item and r["case"] == case))


@pytest.mark.parametrize("case", CASES)
def test_enterprise_value_is_business_operations_plus_other_assets(case: str) -> None:
    expected = summary_value("business_operations", case) + summary_value(
        "other_assets_and_liabilities", case
    )
    assert summary_value("enterprise_value", case) == pytest.approx(
        expected, abs=PRINTED_ROUNDING_AUD_M
    )


@pytest.mark.parametrize("case", CASES)
def test_equity_value_is_enterprise_value_less_net_debt(case: str) -> None:
    expected = summary_value("enterprise_value", case) + summary_value("adjusted_net_debt", case)
    assert summary_value("equity_value", case) == pytest.approx(
        expected, abs=PRINTED_ROUNDING_AUD_M
    )


@pytest.mark.parametrize("case", CASES)
def test_value_per_share_is_equity_value_over_diluted_shares(case: str) -> None:
    expected = summary_value("equity_value", case) / summary_value("fully_diluted_shares", case)
    assert summary_value("value_per_share", case) == pytest.approx(
        expected, abs=PRINTED_ROUNDING_AUD
    )


@pytest.mark.parametrize("case", CASES)
def test_share_build_reproduces_the_printed_diluted_shares(case: str) -> None:
    diluted = (
        build_value("ordinary_shares_on_issue")
        + build_value("share_rights_expected_to_vest", case)
        + build_value("share_rights_cash_settled")
        - build_value("treasury_shares")
    )
    assert round(diluted / 1_000_000, 1) == summary_value("fully_diluted_shares", case)


def test_share_rights_agree_with_the_securities_on_issue() -> None:
    assert build_value("share_rights_expected_to_vest", "low") + build_value(
        "share_rights_cash_settled"
    ) == build_value("share_rights_on_issue_total")
    assert (
        build_value("share_rights_expected_to_vest", "low")
        - build_value("share_rights_expected_to_vest", "high")
        == 1_057_858
    )

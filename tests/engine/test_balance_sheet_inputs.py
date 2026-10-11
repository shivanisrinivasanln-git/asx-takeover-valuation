"""The net debt, share count and control premium inputs reproduce the printed totals."""

from pathlib import Path

import pytest

from valuation import finance
from valuation.assumptions import load_assumptions
from valuation.extracted import load_rows

ROOT = Path(__file__).resolve().parents[2]
ASSUMPTIONS = load_assumptions(ROOT / "assumptions.yaml")
DATA = ROOT / "data" / "extracted"
ONE_DECIMAL_ROUNDING = 0.05
SHARE_ROUNDING_M = 0.05


def value(key: str) -> float:
    entry = ASSUMPTIONS[key].value
    assert isinstance(entry, float)
    return entry


def summary(item: str, case: str) -> float:
    rows = load_rows(DATA / "valuation_summary.csv")
    return float(next(r["value"] for r in rows if r["item"] == item and r["case"] == case))


def adjusted_net_debt_aud_m() -> float:
    return (
        value("reported_net_debt_including_leases_aud_m")
        + value("net_debt_adjustment_capitalised_borrowing_costs_aud_m")
        + value("net_debt_adjustment_interim_dividend_aud_m")
    )


def test_the_net_debt_build_reaches_the_expert_adjusted_net_debt() -> None:
    assert adjusted_net_debt_aud_m() == pytest.approx(
        -summary("adjusted_net_debt", "low"), abs=0.001
    )
    assert adjusted_net_debt_aud_m() == pytest.approx(187.0, abs=0.001)


def test_the_starting_net_debt_is_the_transcribed_balance_sheet_figure() -> None:
    rows = load_rows(DATA / "balance_sheet.csv")
    printed = float(
        next(
            r["value"]
            for r in rows
            if r["balance_date"] == "31 December 2024"
            and r["line_item"] == "net_debt_including_leases"
        )
    )
    assert value("reported_net_debt_including_leases_aud_m") == -printed


def test_other_assets_and_liabilities_match_the_valuation_summary() -> None:
    assert value("other_assets_and_liabilities_aud_m") == summary(
        "other_assets_and_liabilities", "low"
    )


@pytest.mark.parametrize(
    ("case", "vesting_key"),
    [("low", "share_rights_vesting_low_m"), ("high", "share_rights_vesting_high_m")],
)
def test_the_share_build_reproduces_the_printed_diluted_shares(case: str, vesting_key: str) -> None:
    diluted = (
        value("ordinary_shares_on_issue_m")
        + value(vesting_key)
        + value("share_rights_cash_settled_m")
        - value("treasury_shares_m")
    )
    assert diluted == pytest.approx(summary("fully_diluted_shares", case), abs=SHARE_ROUNDING_M)


def test_the_inputs_give_the_expert_value_per_share_from_its_enterprise_value() -> None:
    # The expert's bridge from enterprise value to value per share, using only these inputs.
    for case, vesting_key in (
        ("low", "share_rights_vesting_low_m"),
        ("high", "share_rights_vesting_high_m"),
    ):
        enterprise_value = summary("business_operations", case) + value(
            "other_assets_and_liabilities_aud_m"
        )
        shares = (
            value("ordinary_shares_on_issue_m")
            + value(vesting_key)
            + value("share_rights_cash_settled_m")
            - value("treasury_shares_m")
        )
        per_share = finance.equity_value_per_share_aud(
            enterprise_value, adjusted_net_debt_aud_m(), shares
        )
        assert per_share == pytest.approx(summary("value_per_share", case), abs=0.005)


def test_the_offer_premium_is_42_per_cent_on_the_undisturbed_price() -> None:
    premium = finance.offer_premium_pct(
        value("offer_price_aud"), value("undisturbed_share_price_aud")
    )
    assert premium == pytest.approx(42.0, abs=ONE_DECIMAL_ROUNDING)


def test_the_listed_share_discount_implies_a_premium_near_the_typical_range() -> None:
    # Paying underlying value for shares trading at a discount d is a premium of 1 / (1 - d) - 1.
    low = 1 / (1 - value("listed_share_discount_to_underlying_low_pct") / 100) - 1
    high = 1 / (1 - value("listed_share_discount_to_underlying_high_pct") / 100) - 1
    assert low * 100 == pytest.approx(17.6, abs=ONE_DECIMAL_ROUNDING)
    assert high * 100 == pytest.approx(33.3, abs=ONE_DECIMAL_ROUNDING)
    assert value("control_premium_typical_low_pct") < high * 100
    assert low * 100 < value("control_premium_typical_high_pct")


def test_the_control_premium_applied_is_my_choice_inside_the_experts_typical_range() -> None:
    assert value("control_premium_applied_pct") == 25.0
    assert ASSUMPTIONS["control_premium_applied_pct"].judgement
    assert value("control_premium_typical_low_pct") <= value("control_premium_applied_pct")
    assert value("control_premium_applied_pct") <= value("control_premium_typical_high_pct")

"""The expert's discount rate inputs reproduce the printed cost of equity and WACC ranges."""

from pathlib import Path

import pytest

from valuation.extracted import load_rows

EVIDENCE_FILE = (
    Path(__file__).resolve().parents[2] / "data" / "extracted" / "discount_rate_evidence.csv"
)
ONE_DECIMAL_ROUNDING_PCT = 0.05


def bound(item: str, which: str) -> float:
    rows = load_rows(EVIDENCE_FILE)
    return float(next(r[which] for r in rows if r["item"] == item))


def cost_of_equity_pct(beta: float) -> float:
    return bound("risk_free_rate", "low") + beta * bound("market_risk_premium", "low")


def wacc_pct(equity_weight_pct: float, cost_of_equity: float) -> float:
    after_tax_cost_of_debt = bound("pre_tax_cost_of_debt", "low") * (
        1 - bound("corporate_tax_rate", "low") / 100
    )
    equity_weight = equity_weight_pct / 100
    return equity_weight * cost_of_equity + (1 - equity_weight) * after_tax_cost_of_debt


def test_cost_of_equity_range_follows_from_capm() -> None:
    assert cost_of_equity_pct(bound("beta_adopted", "low")) == pytest.approx(
        bound("cost_of_equity", "low"), abs=ONE_DECIMAL_ROUNDING_PCT
    )
    assert cost_of_equity_pct(bound("beta_adopted", "high")) == pytest.approx(
        bound("cost_of_equity", "high"), abs=ONE_DECIMAL_ROUNDING_PCT
    )


def test_pre_tax_cost_of_debt_is_the_risk_free_rate_plus_the_margin() -> None:
    expected = bound("risk_free_rate", "low") + bound(
        "pre_tax_cost_of_debt_margin_over_risk_free", "low"
    )
    assert bound("pre_tax_cost_of_debt", "low") == pytest.approx(expected, abs=0.001)


def test_gearing_weights_add_to_one_hundred_at_each_end() -> None:
    assert bound("equity_weight", "low") + bound("debt_weight", "high") == 100.0
    assert bound("equity_weight", "high") + bound("debt_weight", "low") == 100.0


def test_wacc_range_is_reproduced_at_the_extreme_weights() -> None:
    # The booklet does not say which weight goes with which cost of equity.
    # These are the combinations that give the lowest and highest results.
    lowest = wacc_pct(bound("equity_weight", "low"), bound("cost_of_equity", "low"))
    highest = wacc_pct(bound("equity_weight", "high"), bound("cost_of_equity", "high"))
    assert lowest == pytest.approx(bound("wacc_calculated", "low"), abs=ONE_DECIMAL_ROUNDING_PCT)
    assert highest == pytest.approx(bound("wacc_calculated", "high"), abs=ONE_DECIMAL_ROUNDING_PCT)


def test_every_other_combination_falls_inside_the_calculated_wacc_range() -> None:
    for equity_weight in (bound("equity_weight", "low"), bound("equity_weight", "high")):
        for cost_of_equity in (bound("cost_of_equity", "low"), bound("cost_of_equity", "high")):
            result = wacc_pct(equity_weight, cost_of_equity)
            assert bound("wacc_calculated", "low") - ONE_DECIMAL_ROUNDING_PCT <= result
            assert result <= bound("wacc_calculated", "high") + ONE_DECIMAL_ROUNDING_PCT


def test_adopted_discount_rate_sits_inside_the_calculated_range_and_above_the_brokers() -> None:
    assert bound("discount_rate_adopted", "low") >= bound("wacc_calculated", "low")
    assert bound("discount_rate_adopted", "high") == bound("wacc_calculated", "high")
    assert bound("broker_discount_rates", "high") < bound("discount_rate_adopted", "low")
    assert (
        bound("broker_discount_rates", "low")
        <= bound("broker_discount_rates", "median")
        <= bound("broker_discount_rates", "high")
    )


def test_the_adopted_beta_lies_within_the_global_peer_beta_range() -> None:
    low = bound("global_property_peers_beta_bloomberg_two_years", "low")
    high = bound("global_property_peers_beta_bloomberg_four_years", "high")
    assert low <= bound("beta_adopted", "low") <= bound("beta_adopted", "high") <= high

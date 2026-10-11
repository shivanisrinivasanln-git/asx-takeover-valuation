"""The discount rate and multiple inputs reproduce the expert's printed results."""

from pathlib import Path

import pytest

from valuation import finance
from valuation.assumptions import load_assumptions
from valuation.extracted import load_rows

ROOT = Path(__file__).resolve().parents[2]
ASSUMPTIONS = load_assumptions(ROOT / "assumptions.yaml")
DATA = ROOT / "data" / "extracted"
ONE_DECIMAL_ROUNDING = 0.05
EXPERT_VALUE_RANGE_AUD_M = (2775.0, 3025.0)
MULTIPLE_ROUNDING_AUD_M = 6.0


def value(key: str) -> float:
    entry = ASSUMPTIONS[key].value
    assert isinstance(entry, float)
    return entry


def wacc_pct(risk_free_pct: float, beta: float, equity_weight_pct: float) -> float:
    cost_of_equity = finance.cost_of_equity_pct(
        risk_free_pct, beta, value("market_risk_premium_pct")
    )
    pre_tax_cost_of_debt = risk_free_pct + value("cost_of_debt_margin_over_risk_free_pct")
    after_tax_cost_of_debt = finance.after_tax_cost_of_debt_pct(
        pre_tax_cost_of_debt, value("tax_rate_pct")
    )
    return finance.wacc_pct(cost_of_equity, after_tax_cost_of_debt, equity_weight_pct)


@pytest.mark.parametrize("risk_free_key", ["risk_free_rate_pct", "expert_risk_free_rate_pct"])
def test_wacc_reproduces_the_expert_range_at_either_risk_free_rate(risk_free_key: str) -> None:
    rows = {r["item"]: r for r in load_rows(DATA / "discount_rate_evidence.csv")}
    low = wacc_pct(value(risk_free_key), value("equity_beta_low"), value("equity_weight_low_pct"))
    high = wacc_pct(
        value(risk_free_key), value("equity_beta_high"), value("equity_weight_high_pct")
    )
    assert round(low, 1) == float(rows["wacc_calculated"]["low"])
    assert round(high, 1) == float(rows["wacc_calculated"]["high"])


def test_the_expert_risk_free_rate_gives_the_expert_cost_of_debt_of_5_5_per_cent() -> None:
    expected = value("expert_risk_free_rate_pct") + value("cost_of_debt_margin_over_risk_free_pct")
    assert expected == pytest.approx(5.5)


def test_my_risk_free_rate_is_the_rba_yield_for_30_may_2025() -> None:
    rows = load_rows(DATA / "market_rates_30_may_2025.csv")
    rba = float(next(r["value"] for r in rows if r["item"] == "risk_free_rate_10y_pct"))
    assert value("risk_free_rate_pct") == rba
    assert ASSUMPTIONS["risk_free_rate_pct"].as_at == "30 May 2025"


def test_the_inputs_that_follow_the_expert_match_the_transcribed_evidence() -> None:
    rows = {r["item"]: r for r in load_rows(DATA / "discount_rate_evidence.csv")}
    assert value("expert_risk_free_rate_pct") == float(rows["risk_free_rate"]["low"])
    assert value("market_risk_premium_pct") == float(rows["market_risk_premium"]["low"])
    assert value("equity_beta_low") == float(rows["beta_adopted"]["low"])
    assert value("equity_beta_high") == float(rows["beta_adopted"]["high"])
    assert value("equity_weight_low_pct") == float(rows["equity_weight"]["low"])
    assert value("equity_weight_high_pct") == float(rows["equity_weight"]["high"])
    assert value("discount_rate_low_pct") == float(rows["discount_rate_adopted"]["low"])
    assert value("discount_rate_high_pct") == float(rows["discount_rate_adopted"]["high"])
    assert value("cost_of_debt_margin_over_risk_free_pct") == float(
        rows["pre_tax_cost_of_debt_margin_over_risk_free"]["low"]
    )


def test_the_expert_implied_multiples_reproduce_its_value_range_within_print_rounding() -> None:
    printed = {
        r["item"]: float(r["value"]) for r in load_rows(DATA / "domain_implied_multiples.csv")
    }
    low_aud_m, high_aud_m = EXPERT_VALUE_RANGE_AUD_M
    for measure in ("ebitda", "ebita"):
        earnings = value(f"fy26_adjusted_{measure}_aud_m")
        assert earnings * printed[f"implied_{measure}_multiple_fy26_low"] == pytest.approx(
            low_aud_m, abs=MULTIPLE_ROUNDING_AUD_M
        )
        assert earnings * printed[f"implied_{measure}_multiple_fy26_high"] == pytest.approx(
            high_aud_m, abs=MULTIPLE_ROUNDING_AUD_M
        )


def test_my_selected_ranges_are_ordered_and_marked_as_my_judgement() -> None:
    for method in ("trading", "precedent"):
        for measure in ("ebitda", "ebita"):
            low = f"{method}_{measure}_multiple_fy26_low_x"
            high = f"{method}_{measure}_multiple_fy26_high_x"
            assert value(low) < value(high), (method, measure)
            assert ASSUMPTIONS[low].judgement
            assert ASSUMPTIONS[high].judgement


def forecast_multiples(table: str, name_column: str, measure: str) -> dict[str, float]:
    return {
        row[name_column]: float(row["multiple_x"])
        for row in load_rows(DATA / f"{table}.csv")
        if row["measure"] == measure and row["basis"] == "forecast"
    }


def test_the_trading_range_is_the_forecast_multiples_of_seek_and_rightmove() -> None:
    for measure in ("ebitda", "ebita"):
        peers = forecast_multiples("comparable_multiples", "company", measure)
        pair = (peers["SEEK"], peers["Rightmove"])
        assert value(f"trading_{measure}_multiple_fy26_low_x") == min(pair)
        assert value(f"trading_{measure}_multiple_fy26_high_x") == max(pair)


def test_the_precedent_range_is_the_six_deal_multiples_less_the_highest_and_lowest() -> None:
    for measure in ("ebitda", "ebita"):
        deals = sorted(forecast_multiples("precedent_transactions", "deal", measure).values())
        assert len(deals) == 6
        assert value(f"precedent_{measure}_multiple_fy26_low_x") == deals[1]
        assert value(f"precedent_{measure}_multiple_fy26_high_x") == deals[-2]


def test_adjusted_earnings_match_the_transcribed_earnings_for_valuation() -> None:
    printed = {
        r["item"]: float(r["value"]) for r in load_rows(DATA / "domain_implied_multiples.csv")
    }
    assert value("fy26_adjusted_ebitda_aud_m") == printed["adjusted_ebitda_fy26"]
    assert value("fy26_adjusted_ebita_aud_m") == printed["adjusted_ebita_fy26"]

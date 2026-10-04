"""The Harbour Industrial worked example from docs/RESEARCH.md, as hand-worked.

Every expected value below is the figure printed in that example, worked out by
hand, so a change to a formula shows as a failing test.
"""

import pytest

from valuation import finance

SHARES_M = 100.0
NET_DEBT_AUD_M = 100.0
EBITDA_AUD_M = 50.0


def test_capitalised_earnings_range() -> None:
    low = finance.capitalised_earnings_value_aud_m(EBITDA_AUD_M, 7.5)
    high = finance.capitalised_earnings_value_aud_m(EBITDA_AUD_M, 8.5)
    assert low == pytest.approx(375.0)
    assert high == pytest.approx(425.0)
    assert finance.equity_value_per_share_aud(low, NET_DEBT_AUD_M, SHARES_M) == pytest.approx(2.75)
    assert finance.equity_value_per_share_aud(high, NET_DEBT_AUD_M, SHARES_M) == pytest.approx(3.25)


def test_wacc_build() -> None:
    cost_of_equity = finance.cost_of_equity_pct(4.0, 1.3, 6.0)
    cost_of_debt = finance.after_tax_cost_of_debt_pct(7.0, 30.0)
    assert cost_of_equity == pytest.approx(11.8)
    assert cost_of_debt == pytest.approx(4.9)
    # The worked example prints 10.4%, the rounded value of 10.42%, and uses 10.4% below.
    wacc = finance.wacc_pct(cost_of_equity, cost_of_debt, 80.0)
    assert wacc == pytest.approx(10.42)
    assert round(wacc, 1) == pytest.approx(10.4)


def test_dcf_cross_check_and_sensitivity() -> None:
    base = finance.growing_perpetuity_value_aud_m(30.0, 10.4, 3.0)
    assert base == pytest.approx(405.4054, rel=1e-6)
    per_share = finance.equity_value_per_share_aud(base, NET_DEBT_AUD_M, SHARES_M)
    assert per_share == pytest.approx(3.054054, rel=1e-6)
    low_rate = finance.growing_perpetuity_value_aud_m(30.0, 9.4, 3.0)
    high_rate = finance.growing_perpetuity_value_aud_m(30.0, 11.4, 3.0)
    assert finance.equity_value_per_share_aud(low_rate, NET_DEBT_AUD_M, SHARES_M) == pytest.approx(
        3.6875, rel=1e-6
    )
    assert finance.equity_value_per_share_aud(high_rate, NET_DEBT_AUD_M, SHARES_M) == pytest.approx(
        2.5714, rel=1e-4
    )


def test_premium_and_market_price_cross_check() -> None:
    assert finance.offer_premium_pct(3.10, 2.20) == pytest.approx(40.909, rel=1e-4)
    assert finance.price_with_premium_aud(2.20, 30.0) == pytest.approx(2.86)


def test_invalid_inputs_raise() -> None:
    with pytest.raises(ValueError, match="diluted_shares_m"):
        finance.equity_value_per_share_aud(1.0, 0.0, 0.0)
    with pytest.raises(ValueError, match="must exceed"):
        finance.growing_perpetuity_value_aud_m(1.0, 3.0, 3.0)
    with pytest.raises(ValueError, match="between 0 and 100"):
        finance.wacc_pct(10.0, 5.0, 120.0)
    with pytest.raises(ValueError, match="undisturbed_price_aud"):
        finance.offer_premium_pct(3.0, 0.0)

"""Peer and deal multiples, implied value and the control premium, against hand examples.

Two-peer example: peers at 10.0x and 14.0x earnings, so low 10.0, median 12.0, high 14.0. On
earnings of 50 the value range is 500 to 700. A 30% control premium turns it into 650 to 910.
The same inputs without the premium give 500 to 700, which differ from the premium values by
exactly 30%.
"""

from dataclasses import replace
from pathlib import Path

import pytest

from valuation.inputs import Inputs, load_inputs
from valuation.multiples import (
    implied_value_aud_m,
    multiples_value,
    summarise_multiples,
    with_control_premium_aud_m,
)

ROOT = Path(__file__).resolve().parents[2]


def test_two_peer_summary_matches_the_hand_example() -> None:
    summary = summarise_multiples([10.0, 14.0])
    assert (summary.low_x, summary.median_x, summary.high_x) == (10.0, 12.0, 14.0)


def test_two_deal_summary_matches_the_hand_example() -> None:
    # Two deals at 22.0x and 18.0x give a range of 18.0x to 22.0x with a median of 20.0x; on
    # earnings of 40 the implied value range is 720 to 880.
    summary = summarise_multiples([22.0, 18.0])
    assert (summary.low_x, summary.median_x, summary.high_x) == (18.0, 20.0, 22.0)
    assert implied_value_aud_m(40.0, summary.low_x) == 720.0
    assert implied_value_aud_m(40.0, summary.high_x) == 880.0


def test_three_deal_summary_takes_the_middle_value_as_the_median() -> None:
    summary = summarise_multiples([22.0, 18.0, 30.0])
    assert (summary.low_x, summary.median_x, summary.high_x) == (18.0, 22.0, 30.0)


def test_an_empty_set_of_multiples_is_rejected() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        summarise_multiples([])


def test_implied_value_and_premium_match_the_hand_example() -> None:
    low = implied_value_aud_m(50.0, 10.0)
    high = implied_value_aud_m(50.0, 14.0)
    assert (low, high) == (500.0, 700.0)
    assert with_control_premium_aud_m(low, 30.0) == pytest.approx(650.0, rel=1e-12)
    assert with_control_premium_aud_m(high, 30.0) == pytest.approx(910.0, rel=1e-12)


def test_the_same_inputs_with_and_without_the_premium_differ_by_exactly_the_premium() -> None:
    value = 700.0
    with_premium = with_control_premium_aud_m(value, 30.0)
    assert with_premium / with_control_premium_aud_m(value, 0.0) == pytest.approx(1.3, rel=1e-12)
    assert with_control_premium_aud_m(value, 0.0) == value


def test_seeded_trading_and_precedent_values_reproduce_the_expert_range() -> None:
    inputs = load_inputs(ROOT)
    for method in ("trading", "precedent"):
        result = multiples_value(inputs, method, "ebitda")
        assert result.control_premium_pct == 0.0
        assert result.value_low_aud_m == pytest.approx(152.2 * 18.2, rel=1e-12)
        assert result.value_high_aud_m == pytest.approx(152.2 * 19.9, rel=1e-12)
        assert result.value_low_aud_m == pytest.approx(2775.0, abs=6.0)
        assert result.value_high_aud_m == pytest.approx(3025.0, abs=6.0)
        expected = (
            "no further control premium applied"
            if method == "trading"
            else "no control premium applied"
        )
        assert expected in result.basis


def test_a_premium_input_changes_the_value_and_the_stated_basis() -> None:
    inputs = load_inputs(ROOT)
    base = multiples_value(inputs, "trading", "ebitda")
    assumptions = dict(inputs.assumptions)
    assumptions["control_premium_applied_pct"] = replace(
        assumptions["control_premium_applied_pct"], value=25.0
    )
    premium = multiples_value(
        Inputs(assumptions=assumptions, tables=inputs.tables), "trading", "ebitda"
    )
    assert premium.value_before_premium_low_aud_m == base.value_before_premium_low_aud_m
    assert premium.value_low_aud_m == pytest.approx(base.value_low_aud_m * 1.25, rel=1e-12)
    assert premium.value_high_aud_m == pytest.approx(base.value_high_aud_m * 1.25, rel=1e-12)
    assert "control premium of 25% applied" in premium.basis


def test_the_premium_input_is_not_applied_to_the_precedent_method() -> None:
    inputs = load_inputs(ROOT)
    assumptions = dict(inputs.assumptions)
    assumptions["control_premium_applied_pct"] = replace(
        assumptions["control_premium_applied_pct"], value=25.0
    )
    precedent = multiples_value(
        Inputs(assumptions=assumptions, tables=inputs.tables), "precedent", "ebitda"
    )
    assert precedent.control_premium_pct == 0.0
    assert precedent.value_low_aud_m == precedent.value_before_premium_low_aud_m
    assert "control multiples" in precedent.basis

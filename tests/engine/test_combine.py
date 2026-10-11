"""Method weights and the combined value, against a hand example.

Three methods with values per share of A$3.00, A$5.00 and A$4.00 and weights of 50%, 30% and
20% combine to 0.5 x 3.00 + 0.3 x 5.00 + 0.2 x 4.00 = 1.50 + 1.50 + 0.80 = A$3.80.
"""

from dataclasses import replace
from pathlib import Path

import pytest

from valuation.combine import MethodWeights, combined_value_per_share_aud, method_weights
from valuation.inputs import Inputs, load_inputs

ROOT = Path(__file__).resolve().parents[2]


def with_weights(inputs: Inputs, dcf: float, trading: float, precedent: float) -> Inputs:
    assumptions = dict(inputs.assumptions)
    for name, value in (
        ("method_weight_dcf_pct", dcf),
        ("method_weight_trading_pct", trading),
        ("method_weight_precedent_pct", precedent),
    ):
        assumptions[name] = replace(assumptions[name], value=value)
    return Inputs(assumptions=assumptions, tables=inputs.tables)


def test_the_hand_example_combines_to_3_80() -> None:
    weights = MethodWeights(dcf_pct=50.0, trading_pct=30.0, precedent_pct=20.0)
    combined = combined_value_per_share_aud(
        weights, {"dcf": 3.00, "trading": 5.00, "precedent": 4.00}
    )
    assert combined == pytest.approx(3.80, rel=1e-12)


def test_my_weights_are_50_25_25() -> None:
    weights = method_weights(load_inputs(ROOT))
    assert (weights.dcf_pct, weights.trading_pct, weights.precedent_pct) == (50.0, 25.0, 25.0)


def test_equal_weights_give_the_plain_average() -> None:
    weights = MethodWeights(dcf_pct=100 / 3, trading_pct=100 / 3, precedent_pct=100 / 3)
    combined = combined_value_per_share_aud(weights, {"dcf": 3.0, "trading": 5.0, "precedent": 4.0})
    assert combined == pytest.approx(4.0, rel=1e-12)


def test_weights_that_do_not_add_to_100_are_rejected() -> None:
    inputs = with_weights(load_inputs(ROOT), 50.0, 25.0, 20.0)
    with pytest.raises(ValueError, match="add to 95"):
        method_weights(inputs)


def test_a_negative_weight_is_rejected() -> None:
    inputs = with_weights(load_inputs(ROOT), 110.0, 25.0, -35.0)
    with pytest.raises(ValueError, match="negative"):
        method_weights(inputs)

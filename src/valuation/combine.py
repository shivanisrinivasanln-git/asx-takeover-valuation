"""Combine the three methods into my range and preferred value, by the weights I chose.

A weight is a percentage of the combined value and the three must add to 100. The combined low,
preferred and high values are the weighted sums of each method's low, preferred (mid) and high
value per share. Nothing is rounded here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from valuation.inputs import Inputs

MethodName = Literal["dcf", "trading", "precedent"]
METHOD_NAMES: tuple[MethodName, ...] = ("dcf", "trading", "precedent")
WEIGHT_TOTAL_PCT = 100.0
WEIGHT_TOLERANCE_PCT = 1e-9


@dataclass(frozen=True)
class MethodWeights:
    dcf_pct: float
    trading_pct: float
    precedent_pct: float

    def of(self, method: MethodName) -> float:
        return {
            "dcf": self.dcf_pct,
            "trading": self.trading_pct,
            "precedent": self.precedent_pct,
        }[method]


def method_weights(inputs: Inputs) -> MethodWeights:
    weights = MethodWeights(
        dcf_pct=inputs.number("method_weight_dcf_pct"),
        trading_pct=inputs.number("method_weight_trading_pct"),
        precedent_pct=inputs.number("method_weight_precedent_pct"),
    )
    total = sum(weights.of(method) for method in METHOD_NAMES)
    if abs(total - WEIGHT_TOTAL_PCT) > WEIGHT_TOLERANCE_PCT:
        raise ValueError(f"the method weights add to {total}, not {WEIGHT_TOTAL_PCT:g}")
    if any(weights.of(method) < 0 for method in METHOD_NAMES):
        raise ValueError("a method weight is negative")
    return weights


def combined_value_per_share_aud(
    weights: MethodWeights, value_per_share_aud: dict[MethodName, float]
) -> float:
    """Weighted sum of the methods' values for one case (low, preferred or high)."""
    return (
        sum(weights.of(method) * value_per_share_aud[method] for method in METHOD_NAMES)
        / WEIGHT_TOTAL_PCT
    )

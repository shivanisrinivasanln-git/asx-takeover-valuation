"""Earnings multiples: peer and deal summaries, implied value and the control premium.

Money is A$ millions and multiples are times earnings. Nothing is rounded here. Deal multiples
are control multiples and need no premium. Peer (trading) multiples come from minority share
prices, so the control premium input applies to the trading method only (docs/BASE_CASE.md).
"""

from __future__ import annotations

import statistics
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from valuation.inputs import Inputs

Measure = Literal["ebitda", "ebita"]
Method = Literal["trading", "precedent"]


@dataclass(frozen=True)
class MultipleSummary:
    low_x: float
    median_x: float
    high_x: float


@dataclass(frozen=True)
class MultiplesValue:
    method: Method
    measure: Measure
    earnings_aud_m: float
    low_multiple_x: float
    mid_multiple_x: float
    high_multiple_x: float
    value_before_premium_low_aud_m: float
    value_before_premium_mid_aud_m: float
    value_before_premium_high_aud_m: float
    control_premium_pct: float
    value_low_aud_m: float
    value_mid_aud_m: float
    value_high_aud_m: float
    basis: str


def summarise_multiples(multiples_x: Sequence[float]) -> MultipleSummary:
    """Lowest, median and highest of a set of peer or deal multiples."""
    if not multiples_x:
        raise ValueError("multiples_x must not be empty")
    return MultipleSummary(
        low_x=min(multiples_x),
        median_x=statistics.median(multiples_x),
        high_x=max(multiples_x),
    )


def implied_value_aud_m(earnings_aud_m: float, multiple_x: float) -> float:
    return earnings_aud_m * multiple_x


def with_control_premium_aud_m(value_aud_m: float, premium_pct: float) -> float:
    """A value grossed up by a control premium; a zero premium leaves it unchanged."""
    return value_aud_m * (1 + premium_pct / 100)


def multiples_value(inputs: Inputs, method: Method, measure: Measure) -> MultiplesValue:
    """Enterprise value of business operations from the selected multiple range for a method."""
    earnings = inputs.number(f"fy26_adjusted_{measure}_aud_m")
    low_x = inputs.number(f"{method}_{measure}_multiple_fy26_low_x")
    high_x = inputs.number(f"{method}_{measure}_multiple_fy26_high_x")
    # Deal multiples are control multiples already, so only trading values take the premium.
    premium = inputs.number("control_premium_applied_pct") if method == "trading" else 0.0
    # The ranges have no preferred point, so the mid case is the midpoint of the two ends.
    mid_x = (low_x + high_x) / 2
    low = implied_value_aud_m(earnings, low_x)
    mid = implied_value_aud_m(earnings, mid_x)
    high = implied_value_aud_m(earnings, high_x)
    return MultiplesValue(
        method=method,
        measure=measure,
        earnings_aud_m=earnings,
        low_multiple_x=low_x,
        mid_multiple_x=mid_x,
        high_multiple_x=high_x,
        value_before_premium_low_aud_m=low,
        value_before_premium_mid_aud_m=mid,
        value_before_premium_high_aud_m=high,
        control_premium_pct=premium,
        value_low_aud_m=with_control_premium_aud_m(low, premium),
        value_mid_aud_m=with_control_premium_aud_m(mid, premium),
        value_high_aud_m=with_control_premium_aud_m(high, premium),
        basis=_basis(method, premium),
    )


def _basis(method: Method, premium_pct: float) -> str:
    if method == "precedent":
        return (
            "FY26 adjusted earnings times the selected deal multiple range; deal multiples are "
            "control multiples, so no control premium applied"
        )
    if premium_pct == 0:
        return (
            "FY26 adjusted earnings times the selected peer multiple range; peer multiples "
            "carry no control premium and none is applied"
        )
    return (
        "FY26 adjusted earnings times the selected peer multiple range with a control premium "
        f"of {premium_pct:g}% applied"
    )

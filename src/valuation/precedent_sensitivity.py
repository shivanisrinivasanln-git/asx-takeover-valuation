"""The precedent range on completed deals only, shown beside my base case (task P4-08).

Two of the four deals inside my precedent range were unsuccessful proposals (Scout24 in 2019 and
Rightmove in 2024). This keeps only the deals that completed and applies the same rule I used
for the base range: drop the highest and the lowest forecast EBITDA multiple, keep the rest.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from valuation.inputs import Inputs

MINIMUM_DEALS = 3

CombinedRange = Callable[[Inputs], tuple[float, float, float]]


def completed_deals_range_x(inputs: Inputs) -> tuple[float, float, list[str]]:
    """Low and high multiple of the completed deals after trimming, and the deals kept."""
    completed = sorted(
        (float(row["multiple_x"]), f"{row['deal']} ({row['announced']})")
        for row in inputs.tables["precedent_transactions"]
        if row["measure"] == "ebitda" and row["basis"] == "forecast" and row["unsuccessful"] == "no"
    )
    if len(completed) < MINIMUM_DEALS:
        raise ValueError(f"only {len(completed)} completed deals with a forecast EBITDA multiple")
    kept = completed[1:-1]
    return kept[0][0], kept[-1][0], [name for _, name in kept]


def precedent_completed_deals_only(inputs: Inputs, combined_range: CombinedRange) -> dict[str, Any]:
    """My preferred value and range with the precedent multiples from completed deals only.

    `combined_range` is the engine's function returning (low, preferred, high) per share.
    """
    low_x, high_x, kept = completed_deals_range_x(inputs)
    changed = inputs.with_assumption_values(
        {
            "precedent_ebitda_multiple_fy26_low_x": low_x,
            "precedent_ebitda_multiple_fy26_high_x": high_x,
        }
    )
    base_low, base_preferred, base_high = combined_range(inputs)
    low, preferred, high = combined_range(changed)
    return {
        "label": "Precedent multiples from completed deals only",
        "deals_kept": kept,
        "multiple_low_x": low_x,
        "multiple_high_x": high_x,
        "base_multiple_low_x": inputs.number("precedent_ebitda_multiple_fy26_low_x"),
        "base_multiple_high_x": inputs.number("precedent_ebitda_multiple_fy26_high_x"),
        "preferred_value_per_share_aud": preferred,
        "combined_value_per_share_aud_low": low,
        "combined_value_per_share_aud_high": high,
        "base_preferred_value_per_share_aud": base_preferred,
        "base_combined_value_per_share_aud_low": base_low,
        "base_combined_value_per_share_aud_high": base_high,
        "change_in_preferred_value_aud": preferred - base_preferred,
    }

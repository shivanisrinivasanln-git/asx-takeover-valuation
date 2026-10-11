"""The gap bridge: from the midpoint of the expert's range to my preferred value (task P4-07).

The expert published a range only, so the start is the midpoint of its printed range, which is
my figure and not one it published. Each step swaps one group of inputs from the expert's value
to mine and records the change in my preferred value per share. The groups are swapped in a fixed
order, and the order changes the size of each step because the inputs interact (a higher
multiple is worth more at a higher premium), so the order is part of the result and is listed
in `valuation.json`.

The first step is my method weights. The expert's range is its judgement and equals the range
its implied multiples give (p. 153), so on the expert's inputs its position corresponds to the
multiples methods alone, not to its DCF. Putting my weights first means every later step is
measured in my own combination of the methods.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from typing import Any

from valuation.inputs import Inputs

WEIGHTS_STEP_ID = "weights"
WEIGHT_NAMES = (
    "method_weight_dcf_pct",
    "method_weight_trading_pct",
    "method_weight_precedent_pct",
)

# (id, label, my inputs that the step swaps). Each has an `expert_` counterpart in
# assumptions.yaml. Net debt and shares are the expert's own figures in my model, so that group
# has no input that differs and its step is zero by construction.
STEP_GROUPS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("discount_rate", "Discount rate range", ("discount_rate_low_pct", "discount_rate_high_pct")),
    (
        "forecast",
        "Revenue, margin, capital expenditure and working capital forecast",
        (
            "revenue_growth_fy26_to_fy35_pct",
            "ebitda_margin_fy30_pct",
            "ebitda_margin_fy35_pct",
            "capex_pct_of_revenue_fy26_to_fy30_pct",
            "capex_pct_of_revenue_long_term_pct",
            "depreciation_pct_of_revenue_long_term_pct",
            "working_capital_pct_of_revenue_pct",
        ),
    ),
    ("terminal_growth", "Terminal growth rate", ("terminal_growth_pct",)),
    (
        "trading_multiples",
        "Trading comparables multiple range",
        ("trading_ebitda_multiple_fy26_low_x", "trading_ebitda_multiple_fy26_high_x"),
    ),
    (
        "precedent_multiples",
        "Precedent transactions multiple range",
        ("precedent_ebitda_multiple_fy26_low_x", "precedent_ebitda_multiple_fy26_high_x"),
    ),
    ("control_premium", "Control premium on trading comparables", ("control_premium_applied_pct",)),
    ("net_debt_and_shares", "Net debt and diluted share counts", ()),
)

PreferredValue = Callable[[Inputs], float]


@dataclass(frozen=True)
class _Step:
    id: str
    label: str
    expert_values: Mapping[str, float]
    my_values: Mapping[str, float]


def expert_input_name(name: str) -> str:
    return f"expert_{name}"


def bridge_input_names() -> tuple[str, ...]:
    return tuple(name for _, _, names in STEP_GROUPS for name in names)


def _with_values(inputs: Inputs, values: Mapping[str, float]) -> Inputs:
    assumptions = dict(inputs.assumptions)
    for name, value in values.items():
        assumptions[name] = replace(assumptions[name], value=value)
    return Inputs(assumptions=assumptions, tables=inputs.tables)


def expert_case_inputs(inputs: Inputs) -> Inputs:
    """My inputs with each bridge input set to the expert's value (its scenario A position)."""
    return _with_values(
        inputs, {name: inputs.number(expert_input_name(name)) for name in bridge_input_names()}
    )


def _steps(inputs: Inputs) -> list[_Step]:
    steps = [
        _Step(
            id=WEIGHTS_STEP_ID,
            label="Method weights",
            expert_values={name: inputs.number(expert_input_name(name)) for name in WEIGHT_NAMES},
            my_values={name: inputs.number(name) for name in WEIGHT_NAMES},
        )
    ]
    for step_id, label, names in STEP_GROUPS:
        steps.append(
            _Step(
                id=step_id,
                label=label,
                expert_values={name: inputs.number(expert_input_name(name)) for name in names},
                my_values={name: inputs.number(name) for name in names},
            )
        )
    return steps


def gap_bridge(
    inputs: Inputs, preferred_value_aud: PreferredValue, start_value_aud: float
) -> dict[str, Any]:
    """The bridge on the current inputs. `preferred_value_aud` is the engine's preferred value."""
    steps = _steps(inputs)
    expert_inputs = _with_values(
        inputs, {name: value for step in steps[1:] for name, value in step.expert_values.items()}
    )
    multiples_reading_aud = preferred_value_aud(_with_values(expert_inputs, steps[0].expert_values))

    rows: list[dict[str, Any]] = []
    swapped: dict[str, float] = {}
    previous_aud = multiples_reading_aud
    cumulative_aud = multiples_reading_aud
    for step in steps:
        # Expert inputs already carry my weights, so the weights step swaps nothing.
        if step.id != WEIGHTS_STEP_ID:
            swapped.update(step.my_values)
        value_aud = preferred_value_aud(_with_values(expert_inputs, swapped))
        change_aud = value_aud - previous_aud
        cumulative_aud += change_aud
        rows.append(
            {
                "id": step.id,
                "label": step.label,
                "inputs": list(step.my_values),
                "expert_values": dict(step.expert_values),
                "my_values": dict(step.my_values),
                "change_aud": change_aud,
                "cumulative_value_per_share_aud": cumulative_aud,
            }
        )
        previous_aud = value_aud

    end_aud = preferred_value_aud(inputs)
    return {
        "start_key": "expert_value_per_share_aud_mid",
        "start_label": (
            "Midpoint of the expert's range (my midpoint of a printed range, "
            "not a figure the expert published)"
        ),
        "start_value_per_share_aud": start_value_aud,
        "reconstruction_change_aud": multiples_reading_aud - start_value_aud,
        "reconstruction_note": (
            "My engine on the expert's multiple range gives this value, which differs from the "
            "printed midpoint by the rounding in the printed multiples."
        ),
        "steps": rows,
        "end_key": "preferred_value_per_share_aud",
        "end_value_per_share_aud": end_aud,
        "total_gap_aud": end_aud - start_value_aud,
        "order_note": (
            "Steps are swapped from the expert's value to mine in this order, with my method "
            "weights first. A different order gives different step sizes and the same total."
        ),
    }

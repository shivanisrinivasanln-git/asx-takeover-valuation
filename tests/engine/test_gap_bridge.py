"""The gap bridge: the steps add up to the gap, and each step is one group of input differences.

Hand example: if the preferred value were 1.0 + 0.1 x terminal growth (in points) + 0.02 x the low
trading multiple + 0.03 x the control premium (in points) + 0.001 x the DCF weight (in points),
then swapping one input from the expert's value to mine changes the value by that input's
coefficient times the difference, whatever the order. With my terminal growth at 3.0 against the
expert's 4.0 the terminal growth step is 0.1 x (3.0 - 4.0) = -0.1.
"""

from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from valuation.extracted import load_rows
from valuation.gap_bridge import (
    STEP_GROUPS,
    WEIGHT_NAMES,
    WEIGHTS_STEP_ID,
    bridge_input_names,
    expert_input_name,
    gap_bridge,
)
from valuation.inputs import Inputs, load_inputs
from valuation.output import build_valuation, preferred_value_per_share_aud
from valuation.sensitivity import base_value_per_share_aud

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "extracted"
TOLERANCE_AUD = 0.005
STEP_ORDER = [WEIGHTS_STEP_ID, *(step_id for step_id, _, _ in STEP_GROUPS)]


def with_values(inputs: Inputs, **values: float) -> Inputs:
    assumptions = dict(inputs.assumptions)
    for name, value in values.items():
        assumptions[name] = replace(assumptions[name], value=value)
    return Inputs(assumptions=assumptions, tables=inputs.tables)


@pytest.fixture(scope="module")
def inputs() -> Inputs:
    return load_inputs(ROOT)


@pytest.fixture(scope="module")
def bridge(inputs: Inputs) -> dict[str, Any]:
    bridge: dict[str, Any] = build_valuation(inputs)["gap_bridge"]
    return bridge


def step_changes(bridge: dict[str, Any]) -> dict[str, float]:
    steps = bridge["steps"]
    assert isinstance(steps, list)
    return {step["id"]: step["change_aud"] for step in steps}


def test_the_steps_are_in_the_stated_order(bridge: dict[str, Any]) -> None:
    assert list(step_changes(bridge)) == STEP_ORDER


def test_the_bridge_starts_at_the_expert_midpoint_and_ends_at_my_preferred_value(
    bridge: dict[str, Any], inputs: Inputs
) -> None:
    assert bridge["start_value_per_share_aud"] == pytest.approx(4.26)
    assert bridge["end_value_per_share_aud"] == pytest.approx(
        preferred_value_per_share_aud(inputs), rel=1e-12
    )
    assert "midpoint" in str(bridge["start_label"])
    assert "not a figure the expert published" in str(bridge["start_label"])


def test_the_steps_sum_to_the_total_gap_within_the_tolerance(bridge: dict[str, Any]) -> None:
    total = sum(step_changes(bridge).values())
    assert total == pytest.approx(float(bridge["total_gap_aud"]), abs=TOLERANCE_AUD)
    reconstruction = float(bridge["reconstruction_change_aud"])
    assert float(bridge["start_value_per_share_aud"]) + reconstruction + total == pytest.approx(
        float(bridge["end_value_per_share_aud"]), rel=1e-12
    )
    assert abs(reconstruction) < TOLERANCE_AUD


def test_each_cumulative_value_is_the_previous_one_plus_the_step(
    bridge: dict[str, Any],
) -> None:
    previous = float(bridge["start_value_per_share_aud"]) + float(
        bridge["reconstruction_change_aud"]
    )
    steps = bridge["steps"]
    assert isinstance(steps, list)
    for step in steps:
        previous += step["change_aud"]
        assert step["cumulative_value_per_share_aud"] == pytest.approx(previous, rel=1e-12)


def test_every_bridge_input_has_the_expert_value_and_it_is_the_one_in_the_report(
    inputs: Inputs,
) -> None:
    parameters = {
        (row["parameter"], row["qualifier"]): float(row["value"])
        for row in load_rows(DATA / "dcf_parameters.csv")
        if row["value"].replace(".", "", 1).isdigit()
    }
    implied = {
        row["item"]: float(row["value"]) for row in load_rows(DATA / "domain_implied_multiples.csv")
    }
    assert (
        inputs.number("expert_discount_rate_low_pct")
        == parameters[("discount_rate_adopted_low", "")]
    )
    assert (
        inputs.number("expert_discount_rate_high_pct")
        == parameters[("discount_rate_adopted_high", "")]
    )
    assert inputs.number("expert_terminal_growth_pct") == parameters[("terminal_growth", "")]
    assert inputs.number("expert_ebitda_margin_fy30_pct") == parameters[("ebitda_margin_fy30", "")]
    assert (
        inputs.number("expert_capex_pct_of_revenue_long_term_pct")
        == parameters[("capital_expenditure_pct_of_revenue_long_term", "")]
    )
    assert (
        inputs.number("expert_working_capital_pct_of_revenue_pct")
        == parameters[("working_capital_pct_of_revenue", "")]
    )
    for method in ("trading", "precedent"):
        assert (
            inputs.number(f"expert_{method}_ebitda_multiple_fy26_low_x")
            == implied["implied_ebitda_multiple_fy26_low"]
        )
        assert (
            inputs.number(f"expert_{method}_ebitda_multiple_fy26_high_x")
            == implied["implied_ebitda_multiple_fy26_high"]
        )
    for name in (*bridge_input_names(), *WEIGHT_NAMES):
        assert expert_input_name(name) in inputs.assumptions, name


def test_the_experts_weights_add_to_100_and_put_nothing_on_the_dcf(inputs: Inputs) -> None:
    weights = [inputs.number(expert_input_name(name)) for name in WEIGHT_NAMES]
    assert sum(weights) == pytest.approx(100.0, rel=1e-12)
    assert inputs.number("expert_method_weight_dcf_pct") == 0.0


def test_on_my_inputs_only_weights_multiples_and_premium_move_the_value(
    bridge: dict[str, Any],
) -> None:
    changes = step_changes(bridge)
    for step_id in ("discount_rate", "forecast", "terminal_growth", "net_debt_and_shares"):
        assert changes[step_id] == pytest.approx(0.0, abs=1e-12), step_id
    for step_id in ("weights", "trading_multiples", "precedent_multiples", "control_premium"):
        assert abs(changes[step_id]) > 0.001, step_id
    assert changes["control_premium"] > 0
    assert changes["weights"] < 0


def fake_preferred_value(inputs: Inputs) -> float:
    return (
        1.0
        + 0.1 * inputs.number("terminal_growth_pct")
        + 0.02 * inputs.number("trading_ebitda_multiple_fy26_low_x")
        + 0.03 * inputs.number("control_premium_applied_pct")
        + 0.001 * inputs.number("method_weight_dcf_pct")
    )


def test_each_step_is_the_input_difference_times_its_effect_in_a_hand_example(
    inputs: Inputs,
) -> None:
    mine = with_values(inputs, terminal_growth_pct=3.0)
    bridge = gap_bridge(mine, fake_preferred_value, start_value_aud=2.0)
    changes = step_changes(bridge)
    assert changes["terminal_growth"] == pytest.approx(0.1 * (3.0 - 4.0), rel=1e-12)
    assert changes["trading_multiples"] == pytest.approx(0.02 * (16.3 - 18.2), rel=1e-12)
    assert changes["control_premium"] == pytest.approx(0.03 * (25.0 - 0.0), rel=1e-12)
    assert changes[WEIGHTS_STEP_ID] == pytest.approx(
        0.001 * (50.0 - inputs.number("expert_method_weight_dcf_pct")), rel=1e-12
    )
    for step_id in ("discount_rate", "forecast", "precedent_multiples", "net_debt_and_shares"):
        assert changes[step_id] == pytest.approx(0.0, abs=1e-12), step_id
    total = (
        float(bridge["reconstruction_change_aud"])
        + sum(changes.values())
        + float(bridge["start_value_per_share_aud"])
    )
    assert total == pytest.approx(float(bridge["end_value_per_share_aud"]), rel=1e-12)


def test_a_lower_terminal_growth_of_mine_shows_up_as_a_negative_dcf_step(
    inputs: Inputs,
) -> None:
    mine = with_values(inputs, terminal_growth_pct=3.0)
    bridge = gap_bridge(
        mine,
        preferred_value_per_share_aud,
        start_value_aud=build_valuation(mine)["values"]["expert_value_per_share_aud_mid"]["value"],
    )
    changes = step_changes(bridge)
    dcf_effect = base_value_per_share_aud(mine) - base_value_per_share_aud(inputs)
    assert dcf_effect < 0
    # The DCF carries a 50% weight, so the step is half its own effect.
    assert changes["terminal_growth"] == pytest.approx(0.5 * dcf_effect, rel=1e-9)
    total = sum(changes.values())
    assert total == pytest.approx(float(bridge["total_gap_aud"]), abs=TOLERANCE_AUD)

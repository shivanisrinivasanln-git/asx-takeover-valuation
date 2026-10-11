"""My engine on the expert's scenario A inputs, against the bar it printed on p. 144.

The bar ends are read from the chart (about plus or minus A$5m). Mid-year discounting, my choice
(docs/DECISIONS.md, 6 October 2026), lands within A$6m of both ends; year end lands about A$120m
below both, far outside the reading precision. The same checks with a planted year-end result
and a planted input change show that the comparison can fail.
"""

from dataclasses import replace
from pathlib import Path

import pytest

from valuation.cross_check import READING_PRECISION_AUD_M, ScenarioAPoint, scenario_a_check
from valuation.inputs import Inputs, load_inputs

ROOT = Path(__file__).resolve().parents[2]
MID_YEAR_LIMIT_AUD_M = 6.0
YEAR_END_FLOOR_AUD_M = 100.0


@pytest.fixture(scope="module")
def points() -> list[ScenarioAPoint]:
    return scenario_a_check(load_inputs(ROOT))


def pick(points: list[ScenarioAPoint], convention: str, bound: str) -> ScenarioAPoint:
    (found,) = [p for p in points if p.convention == convention and p.bound == bound]
    return found


def test_the_check_covers_both_ends_under_both_conventions(points: list[ScenarioAPoint]) -> None:
    assert [(p.convention, p.bound) for p in points] == [
        ("mid-year", "low"),
        ("mid-year", "high"),
        ("year end", "low"),
        ("year end", "high"),
    ]
    assert pick(points, "mid-year", "low").discount_rate_pct == 10.5
    assert pick(points, "mid-year", "high").discount_rate_pct == 9.5


def test_the_expert_bar_ends_are_the_values_read_from_the_chart(
    points: list[ScenarioAPoint],
) -> None:
    assert pick(points, "mid-year", "low").expert_read_aud_m == 2402.0
    assert pick(points, "mid-year", "high").expert_read_aud_m == 2893.0


def test_mid_year_lands_within_a_few_million_of_both_ends(points: list[ScenarioAPoint]) -> None:
    for bound in ("low", "high"):
        point = pick(points, "mid-year", bound)
        assert abs(point.difference_aud_m) <= MID_YEAR_LIMIT_AUD_M, bound
        assert abs(point.difference_pct) < 0.25
    assert READING_PRECISION_AUD_M < MID_YEAR_LIMIT_AUD_M


def test_year_end_is_far_below_both_ends(points: list[ScenarioAPoint]) -> None:
    for bound in ("low", "high"):
        point = pick(points, "year end", bound)
        assert point.difference_aud_m < -YEAR_END_FLOOR_AUD_M, bound


def test_the_comparison_uses_the_experts_inputs_and_not_mine() -> None:
    inputs = load_inputs(ROOT)
    assumptions = dict(inputs.assumptions)
    assumptions["revenue_growth_fy26_to_fy35_pct"] = replace(
        assumptions["revenue_growth_fy26_to_fy35_pct"], value=7.0
    )
    changed = Inputs(assumptions=assumptions, tables=inputs.tables)
    before = scenario_a_check(inputs)
    after = scenario_a_check(changed)
    assert [p.engine_aud_m for p in after] == [p.engine_aud_m for p in before]


def test_a_changed_expert_input_moves_the_result_outside_the_limit() -> None:
    inputs = load_inputs(ROOT)
    assumptions = dict(inputs.assumptions)
    assumptions["expert_ebitda_margin_fy35_pct"] = replace(
        assumptions["expert_ebitda_margin_fy35_pct"], value=44.0
    )
    changed = Inputs(assumptions=assumptions, tables=inputs.tables)
    point = pick(scenario_a_check(changed), "mid-year", "high")
    assert abs(point.difference_aud_m) > MID_YEAR_LIMIT_AUD_M

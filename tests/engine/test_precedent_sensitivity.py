"""The precedent range on completed deals only.

Hand example: the forecast EBITDA multiples of the six deals are 58.com 12.9x, Trade Me 15.2x,
Adevinta 17.7x, Scout24 19.7x (unsuccessful), Rightmove 22.3x (unsuccessful) and ZPG 25.1x. The
completed deals are 12.9x, 15.2x, 17.7x and 25.1x; dropping the lowest and the highest leaves
15.2x to 17.7x. On A$152.2m of FY26 adjusted EBITDA the precedent middle is
152.2 x 16.45 = A$2,503.7m, which is a lower preferred value than the base range gives.
"""

from pathlib import Path

import pytest

from valuation.inputs import Inputs, load_inputs
from valuation.output import build_valuation, combined_range_aud
from valuation.precedent_sensitivity import completed_deals_range_x

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def inputs() -> Inputs:
    return load_inputs(ROOT)


def test_the_completed_deals_trim_to_15_2x_and_17_7x(inputs: Inputs) -> None:
    low, high, kept = completed_deals_range_x(inputs)
    assert (low, high) == (15.2, 17.7)
    assert kept == ["Trade Me (2018)", "Adevinta (2023)"]


def test_the_two_unsuccessful_deals_are_scout24_and_rightmove(inputs: Inputs) -> None:
    unsuccessful = {
        (row["deal"], row["announced"])
        for row in inputs.tables["precedent_transactions"]
        if row["unsuccessful"] == "yes"
    }
    assert unsuccessful == {("Scout24", "2019"), ("Rightmove", "2024")}


def test_the_sensitivity_equals_the_engine_run_on_the_completed_deal_range(
    inputs: Inputs,
) -> None:
    section = build_valuation(inputs)["sensitivities"]["precedent_completed_deals_only"]
    changed = inputs.with_assumption_values(
        {
            "precedent_ebitda_multiple_fy26_low_x": 15.2,
            "precedent_ebitda_multiple_fy26_high_x": 17.7,
        }
    )
    low, preferred, high = combined_range_aud(changed)
    assert section["preferred_value_per_share_aud"] == pytest.approx(preferred, rel=1e-12)
    assert section["combined_value_per_share_aud_low"] == pytest.approx(low, rel=1e-12)
    assert section["combined_value_per_share_aud_high"] == pytest.approx(high, rel=1e-12)
    assert round(section["preferred_value_per_share_aud"], 2) == 4.07
    assert round(section["combined_value_per_share_aud_high"], 2) == 4.47


def test_the_base_case_is_left_unchanged_beside_the_sensitivity(inputs: Inputs) -> None:
    valuation = build_valuation(inputs)
    section = valuation["sensitivities"]["precedent_completed_deals_only"]
    base = valuation["values"]["preferred_value_per_share_aud"]["value"]
    assert section["base_preferred_value_per_share_aud"] == pytest.approx(base, rel=1e-12)
    assert section["change_in_preferred_value_aud"] == pytest.approx(
        section["preferred_value_per_share_aud"] - base, rel=1e-12
    )
    assert section["change_in_preferred_value_aud"] < 0


def test_the_base_multiples_and_base_combined_range_repeat_the_base_case(
    inputs: Inputs,
) -> None:
    valuation = build_valuation(inputs)
    section = valuation["sensitivities"]["precedent_completed_deals_only"]
    values = valuation["values"]
    assert section["base_multiple_low_x"] == inputs.number("precedent_ebitda_multiple_fy26_low_x")
    assert section["base_multiple_high_x"] == inputs.number("precedent_ebitda_multiple_fy26_high_x")
    for case in ("low", "high"):
        assert section[f"base_combined_value_per_share_aud_{case}"] == pytest.approx(
            values[f"combined_value_per_share_aud_{case}"]["value"], rel=1e-12
        )


def test_fewer_than_three_completed_deals_are_rejected(inputs: Inputs) -> None:
    rows = tuple({**row, "unsuccessful": "yes"} for row in inputs.tables["precedent_transactions"])
    changed = Inputs(
        assumptions=inputs.assumptions, tables={**inputs.tables, "precedent_transactions": rows}
    )
    with pytest.raises(ValueError, match="only 0 completed deals"):
        completed_deals_range_x(changed)

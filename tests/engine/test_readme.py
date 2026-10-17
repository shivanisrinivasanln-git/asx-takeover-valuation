"""The README gives the result in its first paragraph, with the same figures as valuation.json,
and links to the live site, the model and the report (task P6-04)."""

import re
from pathlib import Path
from typing import Any

import pytest

from valuation.inputs import load_inputs
from valuation.link_preview import SITE_URL
from valuation.output import build_valuation
from valuation.site_build import MODEL_HREF, REPORT_HREF
from valuation.site_format import number

ROOT = Path(__file__).resolve().parents[2]
README = (ROOT / "README.md").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def valuation() -> dict[str, Any]:
    return build_valuation(load_inputs(ROOT))


def first_paragraph() -> str:
    body = README.split("\n\n", 1)[1]
    return body.split("\n\n", 1)[0]


def test_the_first_paragraph_gives_the_result_from_valuation_json(
    valuation: dict[str, Any],
) -> None:
    values = valuation["values"]
    paragraph = first_paragraph()
    for key in (
        "combined_value_per_share_aud_low",
        "combined_value_per_share_aud_high",
        "preferred_value_per_share_aud",
        "offer_price_aud",
        "expert_value_per_share_aud_low",
        "expert_value_per_share_aud_high",
    ):
        assert f"A${number(values[key]['value'])}" in paragraph, key


def test_the_readme_links_to_the_site_the_model_and_the_report() -> None:
    for address in (SITE_URL, SITE_URL + MODEL_HREF, SITE_URL + REPORT_HREF):
        assert re.search(rf"^- [A-Za-z ]+: {re.escape(address)}$", README, re.MULTILINE), address


def test_every_figure_in_the_bridge_table_is_a_step_of_the_gap_bridge(
    valuation: dict[str, Any],
) -> None:
    bridge = valuation["gap_bridge"]
    expected = {
        number(bridge["start_value_per_share_aud"]),
        number(bridge["end_value_per_share_aud"]),
        number(abs(bridge["reconstruction_change_aud"]), 4),
    }
    for step in bridge["steps"]:
        expected.add(number(abs(step["change_aud"])))
        expected.add(number(step["cumulative_value_per_share_aud"]))
    table = re.search(r"\| Step \|.*?\n\n", README, re.DOTALL)
    assert table
    found = set(re.findall(r"\d+\.\d+", table.group(0)))
    assert found <= expected
    assert len(found) >= 8

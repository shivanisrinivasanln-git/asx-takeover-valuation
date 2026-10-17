"""The built pages agree with the engine: a figure changed in a template or in a page is caught
(task P5-15)."""

import re
import shutil
from pathlib import Path
from typing import Any

import pytest

from valuation.inputs import Inputs, load_inputs
from valuation.output import build_valuation
from valuation.site_build import build_site
from valuation.site_consistency import (
    _parse_figure,
    consistency_problems,
    evidence_tokens,
    template_problems,
)
from valuation.site_format import MINUS
from valuation.site_frame import BuildInfo
from valuation.timeline_page import load_timeline

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="17 October 2026", commit="0123456789abcdef0123456789abcdef01234567")


@pytest.fixture(scope="module")
def inputs() -> Inputs:
    return load_inputs(ROOT)


@pytest.fixture(scope="module")
def valuation(inputs: Inputs) -> dict[str, Any]:
    return build_valuation(inputs)


@pytest.fixture(scope="module")
def timeline() -> list[dict[str, str]]:
    return load_timeline(ROOT)


@pytest.fixture(scope="module")
def site_dir() -> Path:
    out_dir = ROOT / "build" / "site_consistency_test"
    build_site(ROOT, out_dir, BUILD)
    return out_dir


@pytest.fixture
def copy_of_site(site_dir: Path, tmp_path: Path) -> Path:
    copy = tmp_path / "site"
    shutil.copytree(site_dir, copy)
    return copy


def problems_for(
    site: Path,
    valuation: dict[str, Any],
    inputs: Inputs,
    timeline: list[dict[str, str]],
) -> list[str]:
    return consistency_problems(ROOT, site, valuation, inputs, BUILD, timeline)


def change_first(site: Path, page: str, pattern: str, replacement: str) -> None:
    """Rewrite the first match of a pattern in a built page, as a typo in a template would."""
    path = site / page
    html = path.read_text(encoding="utf-8")
    changed, count = re.subn(pattern, replacement, html, count=1)
    assert count == 1, pattern
    path.write_text(changed, encoding="utf-8")


def test_the_built_site_and_the_templates_have_no_problems(
    site_dir: Path, valuation: dict[str, Any], inputs: Inputs, timeline: list[dict[str, str]]
) -> None:
    assert problems_for(site_dir, valuation, inputs, timeline) == []


# Rule 1: templates


@pytest.mark.parametrize(
    "template",
    [
        "<p>The offer is A$4.43 a share.</p>",
        "<td>{{ 4.27 }}</td>",
        "<td>{{ cell.text or '4.27' }}</td>",
        "<p>Revenue grows {{ growth }} from 9 to 10.</p>",
        "{% if x %}<p>12</p>{% endif %}",
    ],
)
def test_a_typed_figure_in_a_template_is_reported(template: str, tmp_path: Path) -> None:
    (tmp_path / "page.html.j2").write_text(template, encoding="utf-8")
    problems = template_problems(tmp_path)
    assert len(problems) == 1
    assert problems[0].startswith("page.html.j2: typed figure")


@pytest.mark.parametrize(
    "template",
    [
        "<p>Forecast from FY25 to FY35, with FY26 earnings.</p>",
        '<rect x="{{ row.x }}" width="5" height="16" dx="-6"/>',
        '<td data-key="{{ cell.key }}" colspan="2">{{ cell.text }}</td>',
        "{# 4.27 is a comment #}<p>{{ text }}</p>",
        "{% if row.height > 4 %}<p>{{ text }}</p>{% endif %}",
        '<line y1="{{ field.top_axis_y + 6 }}" class="grid"/>',
        "<h2>Gap bridge</h2>",
    ],
)
def test_a_template_without_a_typed_figure_passes(template: str, tmp_path: Path) -> None:
    (tmp_path / "page.html.j2").write_text(template, encoding="utf-8")
    assert template_problems(tmp_path) == []


def test_the_real_templates_hold_no_typed_figure() -> None:
    assert template_problems(ROOT / "site" / "templates") == []


# Rule 2: figures that name their origin


def test_a_changed_valuation_figure_is_reported(
    copy_of_site: Path, valuation: dict[str, Any], inputs: Inputs, timeline: list[dict[str, str]]
) -> None:
    change_first(
        copy_of_site,
        "valuation.html",
        r'(data-key="dcf_value_per_share_aud_mid">)[^<]*',
        r"\g<1>3.84",
    )
    problems = problems_for(copy_of_site, valuation, inputs, timeline)
    assert any(
        "data-key=dcf_value_per_share_aud_mid shows '3.84'" in problem for problem in problems
    ), problems


def test_a_changed_forecast_figure_is_reported(
    copy_of_site: Path, valuation: dict[str, Any], inputs: Inputs, timeline: list[dict[str, str]]
) -> None:
    change_first(
        copy_of_site, "valuation.html", r'(data-forecast="free_cash_flow_aud_m">)[^<]*', r"\g<1>9.9"
    )
    problems = problems_for(copy_of_site, valuation, inputs, timeline)
    assert any("data-forecast=free_cash_flow_aud_m shows '9.9'" in p for p in problems), problems


def test_a_changed_input_is_reported(
    copy_of_site: Path, valuation: dict[str, Any], inputs: Inputs, timeline: list[dict[str, str]]
) -> None:
    change_first(
        copy_of_site, "valuation.html", r'(data-input="tax_rate_pct"><a [^>]*>)[^<]*', r"\g<1>25.0"
    )
    problems = problems_for(copy_of_site, valuation, inputs, timeline)
    assert any("data-input=tax_rate_pct shows '25.0'" in p for p in problems), problems


def test_a_changed_bridge_figure_is_reported(
    copy_of_site: Path, valuation: dict[str, Any], inputs: Inputs, timeline: list[dict[str, str]]
) -> None:
    change_first(
        copy_of_site, "gap.html", r'(data-bridge="weights:change_aud">)[^<]*', r"\g<1>+0.21"
    )
    problems = problems_for(copy_of_site, valuation, inputs, timeline)
    assert any("data-bridge=weights:change_aud shows '+0.21'" in p for p in problems), problems


def test_a_changed_chart_label_is_reported(
    copy_of_site: Path, valuation: dict[str, Any], inputs: Inputs, timeline: list[dict[str, str]]
) -> None:
    change_first(
        copy_of_site,
        "index.html",
        r'(data-key="offer_price_aud"[^>]*>)Offer A\$4\.43',
        r"\g<1>Offer A$4.34",
    )
    problems = problems_for(copy_of_site, valuation, inputs, timeline)
    assert any("data-key=offer_price_aud shows" in p for p in problems), problems


def test_a_flag_that_disagrees_with_the_input_is_reported(
    copy_of_site: Path, valuation: dict[str, Any], inputs: Inputs, timeline: list[dict[str, str]]
) -> None:
    change_first(
        copy_of_site,
        "valuation.html",
        r'(data-input="mid_year_discounting_flag"><a [^>]*>)Yes',
        r"\g<1>No",
    )
    problems = problems_for(copy_of_site, valuation, inputs, timeline)
    assert any("mid_year_discounting_flag shows 'No' for a flag of 1" in p for p in problems)


def test_a_changed_count_is_reported(
    copy_of_site: Path, valuation: dict[str, Any], inputs: Inputs, timeline: list[dict[str, str]]
) -> None:
    # 28 is a number that other sources hold, so only the count's own origin can catch it.
    change_first(copy_of_site, "timeline.html", r'(data-count="timeline_checked">)29', r"\g<1>28")
    problems = problems_for(copy_of_site, valuation, inputs, timeline)
    assert any("data-count=timeline_checked shows '28'" in p for p in problems), problems


def test_a_key_that_names_nothing_is_reported(
    copy_of_site: Path, valuation: dict[str, Any], inputs: Inputs, timeline: list[dict[str, str]]
) -> None:
    change_first(
        copy_of_site,
        "valuation.html",
        r'data-key="dcf_value_per_share_aud_mid"',
        'data-key="dcf_value_per_share_aud_median"',
    )
    problems = problems_for(copy_of_site, valuation, inputs, timeline)
    assert any("data-key=dcf_value_per_share_aud_median names nothing" in p for p in problems)


# Rule 3: every other number is in the evidence


def test_a_changed_number_with_no_attribute_is_reported(
    copy_of_site: Path, valuation: dict[str, Any], inputs: Inputs, timeline: list[dict[str, str]]
) -> None:
    change_first(
        copy_of_site,
        "valuation.html",
        r"<td class=\"num\">16\.3</td>",
        '<td class="num">16.37</td>',
    )
    problems = problems_for(copy_of_site, valuation, inputs, timeline)
    assert any("the number 16.37 is not in the sources" in p for p in problems), problems


def test_a_changed_date_in_the_timeline_is_reported(
    copy_of_site: Path, valuation: dict[str, Any], inputs: Inputs, timeline: list[dict[str, str]]
) -> None:
    change_first(
        copy_of_site,
        "timeline.html",
        r'(<p class="timeline-date">)27 August 2025',
        r"\g<1>27 August 2041",
    )
    problems = problems_for(copy_of_site, valuation, inputs, timeline)
    assert any("the number 2041 is not in the sources" in p for p in problems), problems


def test_a_number_in_the_text_alternative_of_the_chart_is_checked(
    copy_of_site: Path, valuation: dict[str, Any], inputs: Inputs, timeline: list[dict[str, str]]
) -> None:
    change_first(
        copy_of_site,
        "index.html",
        r"Discounted cash flow: A\$3\.47 to A\$4\.26",
        "Discounted cash flow: A$3.47 to A$4.62",
    )
    problems = problems_for(copy_of_site, valuation, inputs, timeline)
    assert any("the number 4.62 is not in the sources" in p for p in problems), problems


def test_the_known_limit_a_swap_for_another_number_in_the_sources_is_not_caught(
    copy_of_site: Path, valuation: dict[str, Any], inputs: Inputs, timeline: list[dict[str, str]]
) -> None:
    # 19.9 is the highest peer multiple elsewhere in the sources, so rule 3 accepts it in place of
    # 16.3. A figure that matters carries an attribute and is held to rule 2 instead.
    change_first(
        copy_of_site, "valuation.html", r"<td class=\"num\">16\.3</td>", '<td class="num">19.9</td>'
    )
    assert problems_for(copy_of_site, valuation, inputs, timeline) == []


def test_the_evidence_holds_the_sources_numbers_and_not_a_made_up_one(
    valuation: dict[str, Any], inputs: Inputs, timeline: list[dict[str, str]]
) -> None:
    evidence = evidence_tokens(valuation, inputs, BUILD, timeline)
    assert {"4.26", "4.43", "3.12", "2025", "16.3", "27"} <= evidence
    assert "7.77" not in evidence
    # The lowest, median and highest of the eight peers' forecast EBITDA multiples.
    assert "16.3" in evidence


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("3.83", (3.83, 2)),
        (f"{MINUS}0.21", (-0.21, 2)),
        ("+0.27", (0.27, 2)),
        ("A$4.43", (4.43, 2)),
        (f"{MINUS}A$0.05", (-0.05, 2)),
        ("2,401.1", (2401.1, 1)),
        ("Offer A$4.43 (deed signed 9 May 2025)", (4.43, 2)),
        ("10.0%", (10.0, 1)),
        ("Yes", None),
    ],
)
def test_a_displayed_figure_is_read_with_its_sign_and_decimal_places(
    text: str, expected: tuple[float, int] | None
) -> None:
    assert _parse_figure(text) == expected

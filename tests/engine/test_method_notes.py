"""The method page's completed-deals note and its list of what I could not verify print the
wording I approved on 17 October 2026, with every figure read from the data (task P5-13)."""

import html
import re
from pathlib import Path

import pytest

from valuation.inputs import Inputs, load_inputs
from valuation.method_page import build_method_page
from valuation.output import build_valuation
from valuation.precedent_sensitivity import base_range_deals
from valuation.site_build import build_site
from valuation.site_consistency import consistency_problems
from valuation.site_format import aud, number
from valuation.site_frame import BuildInfo
from valuation.timeline_page import load_timeline

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="17 October 2026", commit="0123456789abcdef0123456789abcdef01234567")
SENSITIVITY = "precedent_completed_deals_only"
RESEARCH = ROOT / "docs" / "RESEARCH.md"
RESEARCH_HEADING = "## Items I could not verify while transcribing the data and filling the inputs"
# Items of that list I chose to leave off the page on 17 October 2026, and why.
LEFT_OUT = {
    "The booklet's actual dispatch date": "no effect on any figure and no page recorded",
    "REA's 22.4x multiple for Rightmove and CoStar's 8-K statements": (
        "my notes disagree about how it was read, so I cannot state it accurately"
    ),
}
# Words that would point at my working method instead of the valuation.
INTERNAL_WORDS = re.compile(r"\b(task|tool|script|engine|test|fetch)\b|\bP\d-\d\d\b", re.IGNORECASE)


@pytest.fixture(scope="module")
def inputs() -> Inputs:
    return load_inputs(ROOT)


@pytest.fixture(scope="module")
def valuation(inputs: Inputs) -> dict[str, object]:
    return build_valuation(inputs)


@pytest.fixture(scope="module")
def site_dir() -> Path:
    out_dir = ROOT / "build" / "site_method_notes_test"
    build_site(ROOT, out_dir, BUILD)
    return out_dir


@pytest.fixture(scope="module")
def method_html(site_dir: Path) -> str:
    return (site_dir / "method.html").read_text(encoding="utf-8")


def plain_text(fragment: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", fragment)).split())


def sensitivity(valuation: dict[str, object]) -> dict[str, float]:
    block = valuation["sensitivities"]
    assert isinstance(block, dict)
    return dict(block[SENSITIVITY])


def test_the_note_prints_the_approved_sentence_with_every_figure_from_the_data(
    method_html: str, valuation: dict[str, object]
) -> None:
    data = sensitivity(valuation)
    expected = (
        "Two of the four deals behind my precedent range, Scout24 (2019) and Rightmove (2024), "
        "were proposals that did not complete. With completed deals only, the precedent range is "
        f"{number(data['multiple_low_x'], 1)}x to {number(data['multiple_high_x'], 1)}x instead of "
        f"{number(data['base_multiple_low_x'], 1)}x to {number(data['base_multiple_high_x'], 1)}x, "
        f"my preferred value is {aud(data['preferred_value_per_share_aud'])} instead of "
        f"{aud(data['base_preferred_value_per_share_aud'])}, and my range is "
        f"{aud(data['combined_value_per_share_aud_low'])} to "
        f"{aud(data['combined_value_per_share_aud_high'])} instead of "
        f"{aud(data['base_combined_value_per_share_aud_low'])} to "
        f"{aud(data['base_combined_value_per_share_aud_high'])}. "
        "My base case keeps the wider precedent range."
    )
    found = re.search(
        r'aria-labelledby="completed-deals-heading">.*?<p>(.*?)</p>', method_html, re.DOTALL
    )
    assert found is not None
    assert plain_text(found.group(1)) == expected


def test_the_note_gives_the_figures_i_approved(
    valuation: dict[str, object],
) -> None:
    data = sensitivity(valuation)
    assert aud(data["preferred_value_per_share_aud"]) == "A$4.07"
    assert aud(data["base_preferred_value_per_share_aud"]) == "A$4.21"
    assert aud(data["combined_value_per_share_aud_high"]) == "A$4.47"
    assert aud(data["base_combined_value_per_share_aud_high"]) == "A$4.75"
    assert number(data["multiple_high_x"], 1) == "17.7"
    assert number(data["base_multiple_high_x"], 1) == "22.3"


def test_the_table_has_a_base_row_and_a_completed_deals_row_from_the_data(
    method_html: str, valuation: dict[str, object]
) -> None:
    data = sensitivity(valuation)
    fields = (
        ("multiple_low_x", 1),
        ("multiple_high_x", 1),
        ("preferred_value_per_share_aud", 2),
        ("combined_value_per_share_aud_low", 2),
        ("combined_value_per_share_aud_high", 2),
    )
    section = method_html.split('id="completed-deals-heading"')[1].split("</section>")[0]
    rows = re.findall(r"<tr>\s*<th scope=\"row\">(.*?)</th>(.*?)</tr>", section, re.DOTALL)
    assert [label for label, _ in rows] == ["My base case", "Completed deals only"]
    for (_, cells), prefix in zip(rows, ("base_", ""), strict=True):
        found = re.findall(r'data-sensitivity="([^"]+)">([^<]*)<', cells)
        assert found == [
            (f"{SENSITIVITY}:{prefix}{field}", number(data[f"{prefix}{field}"], places))
            for field, places in fields
        ]


def test_the_two_unsuccessful_deals_are_two_of_the_four_in_my_base_range(
    inputs: Inputs,
) -> None:
    deals = base_range_deals(inputs)
    assert len(deals) == 4
    assert sorted((deal, year) for deal, year, failed in deals if failed) == [
        ("Rightmove", "2024"),
        ("Scout24", "2019"),
    ]
    multiples = sorted(
        float(row["multiple_x"])
        for row in inputs.tables["precedent_transactions"]
        if row["measure"] == "ebitda" and row["basis"] == "forecast"
    )
    assert multiples[1] == inputs.number("precedent_ebitda_multiple_fy26_low_x")
    assert multiples[-2] == inputs.number("precedent_ebitda_multiple_fy26_high_x")


def test_the_build_stops_if_the_data_no_longer_matches_the_words_two_of_the_four(
    inputs: Inputs, valuation: dict[str, object]
) -> None:
    rows = tuple({**row, "unsuccessful": "yes"} for row in inputs.tables["precedent_transactions"])
    changed = Inputs(
        assumptions=inputs.assumptions, tables={**inputs.tables, "precedent_transactions": rows}
    )
    with pytest.raises(ValueError, match="two of the four"):
        build_method_page(valuation, changed)


def test_the_page_lists_each_approved_limitation_unchanged_and_in_order(
    method_html: str, inputs: Inputs
) -> None:
    section = method_html.split('id="limitations-heading"')[1].split("</section>")[0]
    printed = [plain_text(item) for item in re.findall(r"<li>(.*?)</li>", section, re.DOTALL)]
    written = [" ".join(row["text"].split()) for row in inputs.tables["limitations"]]
    assert printed == written
    assert len(written) == 14


def test_every_item_in_my_list_is_published_or_left_out_for_a_stated_reason(
    inputs: Inputs,
) -> None:
    section = RESEARCH.read_text(encoding="utf-8").split(RESEARCH_HEADING)[1]
    items = [
        line.strip("|").split(" | ")[0].strip()
        for line in section.splitlines()
        if line.startswith("| ") and not line.startswith(("| Item", "|---"))
    ]
    assert len(items) == 16
    assert set(LEFT_OUT) <= set(items)
    assert len(inputs.tables["limitations"]) == len(items) - len(LEFT_OUT)


def test_each_limitation_has_a_page_or_a_source_and_names_no_working_method(
    inputs: Inputs,
) -> None:
    ids = [row["item"] for row in inputs.tables["limitations"]]
    assert len(ids) == len(set(ids))
    for row in inputs.tables["limitations"]:
        assert row["source"].strip(), row["item"]
        assert row["location"].strip(), row["item"]
        assert row["as_at"].strip(), row["item"]
        assert not INTERNAL_WORDS.search(row["text"]), row["item"]


def planted(site_dir: Path, tmp_path: Path, old: str, new: str) -> list[str]:
    edited, count = re.subn(
        old, new, (site_dir / "method.html").read_text(encoding="utf-8"), count=1
    )
    assert count == 1, old
    (tmp_path / "method.html").write_text(edited, encoding="utf-8")
    inputs = load_inputs(ROOT)
    return consistency_problems(
        ROOT, tmp_path, build_valuation(inputs), inputs, BUILD, load_timeline(ROOT)
    )


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        (
            r'(data-sensitivity="precedent_completed_deals_only:preferred_value_per_share_aud">)A\$4\.07',
            r"\g<1>A$4.17",
            "shows 'A$4.17'",
        ),
        (
            r'(data-sensitivity="precedent_completed_deals_only:base_multiple_high_x">)22\.3',
            r"\g<1>22.4",
            "shows '22.4'",
        ),
        (
            r'(<td class="num" data-sensitivity='
            r'"precedent_completed_deals_only:multiple_low_x">)15\.2',
            r"\g<1>15.3",
            "shows '15.3'",
        ),
        (
            r'data-sensitivity="precedent_completed_deals_only:multiple_high_x"',
            'data-sensitivity="precedent_completed_deals_only:nothing"',
            "names nothing in the data",
        ),
        (
            r'data-sensitivity="precedent_completed_deals_only:multiple_high_x"',
            'data-sensitivity="malformed"',
            "names nothing in the data",
        ),
    ],
)
def test_a_planted_change_to_a_sensitivity_figure_is_reported(
    site_dir: Path, tmp_path: Path, old: str, new: str, message: str
) -> None:
    assert any(message in problem for problem in planted(site_dir, tmp_path, old, new))

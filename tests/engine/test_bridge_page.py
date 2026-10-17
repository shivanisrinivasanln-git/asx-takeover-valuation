"""The gap bridge page: the steps add up, every label is the figure in valuation.json, each step
links to its explanation and the explanation is my wording, unchanged (task P5-11)."""

from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import pytest

from valuation.bridge_page import SHORT_LABELS, build_bridge_page
from valuation.inputs import Inputs, load_inputs
from valuation.output import build_valuation
from valuation.site_build import build_site
from valuation.site_format import MINUS, aud, aud_signed, number, signed
from valuation.site_frame import BuildInfo

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="17 October 2026", commit="0123456789abcdef0123456789abcdef01234567")


class _Page(HTMLParser):
    """The SVG elements, the labelled text and cells, links and the step articles."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[tuple[str, dict[str, str]]] = []
        self.labelled: list[tuple[str, str]] = []
        self.links: list[str] = []
        self.articles: dict[str, str] = {}
        self.row_labels: list[str] = []
        self.html = ""
        self._open: list[tuple[str, dict[str, str], list[str]]] = []
        self._article: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        self.elements.append((tag, values))
        self._open.append((tag, values, []))
        if tag == "a" and "href" in values:
            self.links.append(values["href"])
        if tag == "article" and values.get("id", "").startswith("step-"):
            self._article = values["id"]
            self.articles[self._article] = ""

    def handle_endtag(self, tag: str) -> None:
        while self._open:
            name, values, parts = self._open.pop()
            if name == tag:
                text = "".join(parts).strip()
                if "data-bridge" in values:
                    self.labelled.append((values["data-bridge"], text))
                if tag == "text" and "row-label" in values.get("class", ""):
                    self.row_labels.append(text)
                break
        if tag == "article":
            self._article = None

    def handle_data(self, data: str) -> None:
        for _, _, parts in self._open:
            parts.append(data)
        if self._article is not None:
            self.articles[self._article] += data


@pytest.fixture(scope="module")
def inputs() -> Inputs:
    return load_inputs(ROOT)


@pytest.fixture(scope="module")
def valuation(inputs: Inputs) -> dict[str, Any]:
    return build_valuation(inputs)


@pytest.fixture(scope="module")
def bridge(valuation: dict[str, Any]) -> dict[str, Any]:
    return dict(valuation["gap_bridge"])


@pytest.fixture(scope="module")
def page() -> _Page:
    out_dir = ROOT / "build" / "site_bridge_test"
    build_site(ROOT, out_dir, BUILD)
    parsed = _Page()
    parsed.html = (out_dir / "gap.html").read_text(encoding="utf-8")
    parsed.feed(parsed.html)
    parsed.close()
    return parsed


def expected_text(bridge: dict[str, Any], key: str) -> str:
    """What a label with this data-bridge key must read, from the engine's figures."""
    if key == "start_value_per_share_aud":
        return number(bridge[key])
    if key == "end_value_per_share_aud":
        return number(bridge[key])
    if key == "reconstruction_change_aud":
        return signed(bridge[key], 4)
    if key == "total_gap_aud":
        return signed(bridge[key])
    if key == "rounded_steps_sum_aud":
        return signed(round(sum(round(step["change_aud"], 2) for step in bridge["steps"]), 2))
    step_id, field = key.split(":")
    steps = bridge["steps"]
    step = next(item for item in steps if item["id"] == step_id)
    if field == "change_aud":
        return signed(step[field])
    return number(step[field])


def test_the_steps_add_up_to_the_gap(bridge: dict[str, Any]) -> None:
    steps = bridge["steps"]
    start = bridge["start_value_per_share_aud"]
    end = bridge["end_value_per_share_aud"]
    reconstruction = bridge["reconstruction_change_aud"]
    total = start + reconstruction + sum(step["change_aud"] for step in steps)
    assert total == pytest.approx(end, abs=1e-9)
    assert end - start == pytest.approx(bridge["total_gap_aud"], abs=1e-9)
    running = start + reconstruction
    for step in steps:
        running += step["change_aud"]
        assert running == pytest.approx(step["cumulative_value_per_share_aud"], abs=1e-9)


def test_every_label_and_cell_is_the_figure_in_valuation_json(
    page: _Page, bridge: dict[str, Any]
) -> None:
    steps = bridge["steps"]
    keys = [key for key, _ in page.labelled]
    # Ten chart labels (start, eight steps, end) and the same figures in the table, plus the
    # reconstruction row, the total and the cumulative value after each step and at the end.
    chart = 1 + len(steps) + 1
    table_changes = len(steps) + 2
    table_values = 1 + len(steps) + 1
    # The rounding note repeats the total and adds the sum of the rounded steps.
    assert len(keys) == chart + table_changes + table_values + 2
    for key, text in page.labelled:
        assert text == expected_text(bridge, key), key
    assert {key for key, _ in page.labelled} >= {f"{step['id']}:change_aud" for step in steps}


def test_a_nonzero_step_carries_a_sign_and_a_zero_step_does_not(
    page: _Page, bridge: dict[str, Any]
) -> None:
    steps = bridge["steps"]
    by_key = dict(page.labelled)
    for step in steps:
        text = by_key[f"{step['id']}:change_aud"]
        if round(step["change_aud"], 2) == 0:
            assert text == "0.00", step["id"]
        else:
            assert text[0] == ("+" if step["change_aud"] > 0 else MINUS), step["id"]
    assert not any("-" in text for _, text in page.labelled)


def test_the_chart_uses_percentage_coordinates_and_no_viewbox(page: _Page) -> None:
    svg = next(attrs for tag, attrs in page.elements if tag == "svg")
    assert "viewbox" not in {name.lower() for name in svg}
    assert svg["width"] == "100%"
    horizontal = [
        attrs[name]
        for tag, attrs in page.elements
        if tag in ("rect", "line", "text")
        for name in ("x", "x1", "x2")
        if name in attrs
    ]
    assert horizontal
    # Row labels sit at the left edge, x="0"; everything else is a percentage of the width.
    assert all(value.endswith("%") or value == "0" for value in horizontal)


def _percent(text: str) -> float:
    return float(text.removesuffix("%"))


def test_bars_sit_on_the_price_axis_and_start_where_the_last_step_ended(
    valuation: dict[str, Any], inputs: Inputs
) -> None:
    built = build_bridge_page(valuation, inputs)
    low: float = built["axis_min_aud"]
    high: float = built["axis_max_aud"]
    rows = built["rows"]
    steps = valuation["gap_bridge"]["steps"]

    def position(value: float) -> float:
        return float((value - low) / (high - low) * 100)

    previous_level: float | None = None
    for row, step in zip(rows[1:-1], steps, strict=True):
        before = step["cumulative_value_per_share_aud"] - step["change_aud"]
        if previous_level is not None:
            assert before == pytest.approx(previous_level, abs=1e-9)
        previous_level = step["cumulative_value_per_share_aud"]
        if row["direction"] == "none":
            continue
        assert _percent(row["x_low"]) == pytest.approx(
            position(min(before, previous_level)), abs=1e-3
        )
        assert _percent(row["x_width"]) == pytest.approx(
            abs(step["change_aud"]) / (high - low) * 100, abs=1e-3
        )
    assert previous_level is not None
    levels = [valuation["gap_bridge"]["start_value_per_share_aud"], previous_level]
    assert low <= min(levels)
    assert max(levels) <= high


def test_a_raising_step_is_teal_a_lowering_step_orange_and_a_zero_step_has_no_bar(
    page: _Page, bridge: dict[str, Any]
) -> None:
    steps = bridge["steps"]
    bars = [attrs["class"] for tag, attrs in page.elements if tag == "rect"]
    expected = [
        "bar bar-up" if step["change_aud"] > 0 else "bar bar-down"
        for step in steps
        if round(step["change_aud"], 2) != 0
    ]
    assert bars == expected
    assert sum("step-none" in attrs.get("class", "") for _, attrs in page.elements) == sum(
        round(step["change_aud"], 2) == 0 for step in steps
    )


def test_each_step_in_the_table_links_to_its_explanation(
    page: _Page, bridge: dict[str, Any]
) -> None:
    steps = bridge["steps"]
    for step in steps:
        anchor = f"#step-{step['id']}"
        assert page.links.count(anchor) == 1, step["id"]
        assert anchor.removeprefix("#") in page.articles
    assert set(page.row_labels) >= {SHORT_LABELS[step["id"]] for step in steps}
    assert SHORT_LABELS.keys() == {step["id"] for step in steps}


def test_each_explanation_is_my_wording_unchanged_with_its_amount(
    page: _Page, bridge: dict[str, Any], inputs: Inputs
) -> None:
    steps = bridge["steps"]
    for step in steps:
        row = inputs.table_row("gap_step_explanations", step_id=step["id"])
        article = " ".join(page.articles[f"step-{step['id']}"].split())
        assert " ".join(row["text"].split()) in article, step["id"]
        assert aud(abs(step["change_aud"])) in article, step["id"]
        assert aud_signed(step["change_aud"]) in article, step["id"]
        assert str(step["sources"]) in article, step["id"]


def test_the_page_says_the_start_is_a_midpoint_and_not_a_published_figure(page: _Page) -> None:
    assert "not a figure the expert published" in page.html


def test_the_rounding_note_gives_the_sum_of_the_rounded_steps(
    valuation: dict[str, Any], inputs: Inputs
) -> None:
    built = build_bridge_page(valuation, inputs)
    steps = valuation["gap_bridge"]["steps"]
    rounded = round(sum(round(step["change_aud"], 2) for step in steps), 2)
    assert built["rounding"]["steps_sum"] == signed(rounded)
    assert built["rounding"]["total"] == signed(valuation["gap_bridge"]["total_gap_aud"])
    # The rounded steps and the rounded total can differ by a cent, and the note says so.
    assert built["rounding"]["steps_sum"] != built["rounding"]["total"]


def test_the_input_tables_show_the_expert_and_my_values(
    valuation: dict[str, Any], inputs: Inputs
) -> None:
    built = build_bridge_page(valuation, inputs)
    steps = valuation["gap_bridge"]["steps"]
    for shown, step in zip(built["steps"], steps, strict=True):
        assert [row["key"] for row in shown["inputs"]] == step["inputs"]
        for row in shown["inputs"]:
            assert row["expert"] == number(step["expert_values"][row["key"]], 1)
            assert row["mine"] == number(step["my_values"][row["key"]], 1)

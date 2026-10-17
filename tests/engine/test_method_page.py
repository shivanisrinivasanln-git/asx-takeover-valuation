"""The method and sources page: every register row is an entry of assumptions.yaml, unchanged
(task P5-13)."""

import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import pytest

from valuation.inputs import Inputs, load_inputs
from valuation.output import build_valuation
from valuation.site_build import DISCLAIMER, build_site
from valuation.site_consistency import consistency_problems
from valuation.site_format import MINUS, plain
from valuation.site_frame import BuildInfo
from valuation.timeline_page import load_timeline

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="17 October 2026", commit="0123456789abcdef0123456789abcdef01234567")
UNIT_LABELS = {"pct": "%", "times": "x", "aud_m": "A$m", "aud": "A$", "million shares": "m shares"}


class _Register(HTMLParser):
    """The rows of the register table, each as its cells' text and attributes."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[dict[str, Any]] = []
        self.counts: dict[str, str] = {}
        self.text = ""
        self._row: dict[str, Any] | None = None
        self._cell: list[str] | None = None
        self._cell_attrs: dict[str, str] = {}
        self._count_key: str | None = None
        self._in_body = False
        self._in_register = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        if values.get("id") == "register-heading":
            self._in_register = True
        if tag == "tbody" and self._in_register:
            self._in_body = True
        if tag == "tr" and self._in_body:
            self._row = {"id": values.get("id", ""), "cells": [], "attrs": []}
        if tag in ("th", "td") and self._row is not None:
            self._cell, self._cell_attrs = [], values
        if "data-count" in values:
            self._count_key = values["data-count"]
            self.counts[self._count_key] = ""

    def handle_data(self, data: str) -> None:
        self.text += data
        if self._cell is not None:
            self._cell.append(data)
        if self._count_key is not None:
            self.counts[self._count_key] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "span":
            self._count_key = None
        if tag in ("th", "td") and self._row is not None and self._cell is not None:
            self._row["cells"].append("".join(self._cell).strip())
            self._row["attrs"].append(self._cell_attrs)
            self._cell = None
        if tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None
        if tag == "tbody":
            self._in_body = False


@pytest.fixture(scope="module")
def inputs() -> Inputs:
    return load_inputs(ROOT)


@pytest.fixture(scope="module")
def site_dir() -> Path:
    out_dir = ROOT / "build" / "site_method_test"
    build_site(ROOT, out_dir, BUILD)
    return out_dir


@pytest.fixture(scope="module")
def register(site_dir: Path) -> _Register:
    parsed = _Register()
    parsed.feed((site_dir / "method.html").read_text(encoding="utf-8"))
    parsed.close()
    return parsed


def expected_value(key: str, value: float | tuple[float, ...]) -> str:
    if isinstance(value, tuple):
        return ", ".join(str(int(part)) for part in value)
    if key == "mid_year_discounting_flag":
        return "Yes" if value == 1 else "No"
    return plain(value)


def test_every_register_row_is_an_input_in_the_order_of_the_file(
    register: _Register, inputs: Inputs
) -> None:
    assert [row["cells"][0] for row in register.rows] == list(inputs.assumptions)
    assert [row["id"] for row in register.rows] == [f"input-{key}" for key in inputs.assumptions]


def test_every_register_row_carries_its_value_unit_source_page_date_and_note(
    register: _Register, inputs: Inputs
) -> None:
    for row, (key, entry) in zip(register.rows, inputs.assumptions.items(), strict=True):
        name, value, unit, source, location, as_at, mine, note = row["cells"]
        assert name == key
        assert value == expected_value(key, entry.value), key
        assert unit == (
            "" if key == "mid_year_discounting_flag" else UNIT_LABELS.get(entry.unit, entry.unit)
        )
        assert source == entry.source, key
        assert location == entry.location, key
        assert as_at == entry.as_at, key
        assert mine == ("My judgement" if entry.judgement else ""), key
        assert note == entry.note, key


def test_a_single_value_names_its_input_and_a_date_does_not(
    register: _Register, inputs: Inputs
) -> None:
    for row, (key, entry) in zip(register.rows, inputs.assumptions.items(), strict=True):
        value_attrs = row["attrs"][1]
        if isinstance(entry.value, tuple):
            assert "data-input" not in value_attrs, key
        else:
            assert value_attrs["data-input"] == key, key


def test_the_counts_on_the_page_are_the_counts_in_the_file(
    register: _Register, inputs: Inputs
) -> None:
    assert register.counts["inputs"] == str(len(inputs.assumptions)) == "80"
    judgement = sum(entry.judgement for entry in inputs.assumptions.values())
    assert register.counts["judgement_inputs"] == str(judgement) == "26"


def test_the_page_carries_the_disclaimer(register: _Register) -> None:
    assert DISCLAIMER in " ".join(register.text.split())


def test_a_changed_register_value_is_reported(
    site_dir: Path, inputs: Inputs, tmp_path: Path
) -> None:
    changed = tmp_path / "site"
    changed.mkdir()
    html = (site_dir / "method.html").read_text(encoding="utf-8")
    edited, count = re.subn(r'(data-input="stub_period_years">)0\.5', r"\g<1>0.6", html)
    assert count == 1
    (changed / "method.html").write_text(edited, encoding="utf-8")
    valuation = build_valuation(inputs)
    problems = consistency_problems(ROOT, changed, valuation, inputs, BUILD, load_timeline(ROOT))
    assert any("data-input=stub_period_years shows '0.6'" in problem for problem in problems)


@pytest.mark.parametrize(
    ("value", "text"),
    [
        (4.249, "4.249"),
        (9.0, "9"),
        (420.0, "420"),
        (2401.07, "2,401.07"),
        (-0.5, f"{MINUS}0.5"),
        (0.00004, "0"),
        (0.5, "0.5"),
    ],
)
def test_a_value_is_written_with_up_to_four_places_and_no_trailing_zeros(
    value: float, text: str
) -> None:
    assert plain(value) == text

"""The football field: every label matches valuation.json, bars sit on the price scale, and the
chart has a text alternative and a data table."""

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

from valuation.football_field import build_football_field
from valuation.inputs import Inputs, load_inputs
from valuation.output import build_valuation
from valuation.site_build import build_site
from valuation.site_format import MINUS, aud, aud_signed, number, percent, signed
from valuation.site_frame import BuildInfo

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="17 October 2026", commit="0123456789abcdef0123456789abcdef01234567")
CSS = ROOT / "site" / "static" / "site.css"
TOKENS = ROOT / "site" / "static" / "tokens.css"
MINIMUM_GRAPHIC_CONTRAST = 3.0


class _Chart(HTMLParser):
    """Collects the SVG elements and the data table of the built page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[tuple[str, dict[str, str]]] = []
        self.texts: list[tuple[dict[str, str], str]] = []
        self.cells: list[tuple[dict[str, str], str]] = []
        self._open: list[tuple[str, dict[str, str], list[str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        self.elements.append((tag, values))
        self._open.append((tag, values, []))

    def handle_endtag(self, tag: str) -> None:
        while self._open:
            name, values, parts = self._open.pop()
            if name == tag:
                text = "".join(parts).strip()
                if tag == "text":
                    self.texts.append((values, text))
                if tag == "td":
                    self.cells.append((values, text))
                return

    def handle_data(self, data: str) -> None:
        for _, _, parts in self._open:
            parts.append(data)


@pytest.fixture(scope="module")
def inputs() -> Inputs:
    return load_inputs(ROOT)


@pytest.fixture(scope="module")
def valuation(inputs: Inputs) -> dict[str, object]:
    return build_valuation(inputs)


@pytest.fixture(scope="module")
def page() -> _Chart:
    out_dir = ROOT / "build" / "site_test"
    build_site(ROOT, out_dir, BUILD)
    chart = _Chart()
    chart.feed((out_dir / "index.html").read_text(encoding="utf-8"))
    return chart


def value_of(valuation: dict[str, object], key: str) -> float:
    values = valuation["values"]
    assert isinstance(values, dict)
    return float(values[key]["value"])


def test_every_label_and_table_cell_is_the_value_in_valuation_json(
    page: _Chart, valuation: dict[str, object]
) -> None:
    checked = 0
    for attrs, text in [*page.texts, *page.cells]:
        key = attrs.get("data-key")
        if key is None:
            continue
        value = value_of(valuation, key)
        if key in ("offer_price_aud", "undisturbed_share_price_aud"):
            assert aud(value) in text, (key, text)
        else:
            assert text == number(value), (key, text)
        checked += 1
    # Five rows with a low and a high on the chart and in the table, four preferred values in the
    # table, and the two reference lines.
    assert checked == 5 * 2 * 2 + 4 + 2


def test_reference_lines_show_the_price_and_the_date_of_the_input(
    page: _Chart, valuation: dict[str, object], inputs: Inputs
) -> None:
    texts = {attrs["data-key"]: text for attrs, text in page.texts if "data-key" in attrs}
    offer = inputs.assumptions["offer_price_aud"]
    undisturbed = inputs.assumptions["undisturbed_share_price_aud"]
    assert texts["offer_price_aud"] == (
        f"Offer {aud(value_of(valuation, 'offer_price_aud'))} (deed signed {offer.as_at})"
    )
    assert texts["undisturbed_share_price_aud"] == (
        f"Undisturbed price {aud(value_of(valuation, 'undisturbed_share_price_aud'))} "
        f"({undisturbed.as_at})"
    )


def test_the_chart_uses_percentage_coordinates_and_no_viewbox(page: _Chart) -> None:
    svg = next(attrs for tag, attrs in page.elements if tag == "svg")
    assert "viewbox" not in {name.lower() for name in svg}
    assert svg["width"] == "100%"
    bars = [
        attrs for tag, attrs in page.elements if tag == "rect" and "bar" in attrs.get("class", "")
    ]
    assert len(bars) == 5
    for bar in bars:
        assert bar["x"].endswith("%")
        assert bar["width"].endswith("%")


def test_bar_positions_follow_the_price_scale(inputs: Inputs, valuation: dict[str, object]) -> None:
    field = build_football_field(valuation, inputs)
    span = field.axis_max_aud - field.axis_min_aud
    for row in field.rows:
        assert float(row.x_low.rstrip("%")) == pytest.approx(
            (row.low_aud - field.axis_min_aud) / span * 100, abs=0.001
        )
        assert float(row.x_high.rstrip("%")) == pytest.approx(
            (row.high_aud - field.axis_min_aud) / span * 100, abs=0.001
        )
        assert float(row.width.rstrip("%")) == pytest.approx(
            float(row.x_high.rstrip("%")) - float(row.x_low.rstrip("%")), abs=0.002
        )
    values = [r.low_aud for r in field.rows] + [r.high_aud for r in field.rows]
    values += [field.offer.value_aud, field.undisturbed.value_aud]
    assert field.axis_min_aud < min(values)
    assert field.axis_max_aud > max(values)


def test_my_rows_have_a_hatch_and_a_preferred_tick_and_the_expert_row_has_neither(
    page: _Chart,
) -> None:
    groups = [
        (attrs["data-row"], index)
        for index, (tag, attrs) in enumerate(page.elements)
        if tag == "g" and "data-row" in attrs
    ]
    assert [name for name, _ in groups] == ["dcf", "trading", "precedent", "combined", "expert"]
    ticks = [
        attrs
        for tag, attrs in page.elements
        if tag == "line" and "preferred-tick" in attrs.get("class", "")
    ]
    assert len(ticks) == 4
    hatched = [
        attrs
        for tag, attrs in page.elements
        if tag == "rect" and attrs.get("fill") == "url(#hatch)"
    ]
    assert len(hatched) == 4
    expert = [
        attrs
        for tag, attrs in page.elements
        if tag == "rect" and "bar-expert" in attrs.get("class", "")
    ]
    assert len(expert) == 1
    assert "fill" not in expert[0]


def test_the_chart_has_a_text_alternative_and_a_table_of_every_low_and_high(
    page: _Chart, valuation: dict[str, object]
) -> None:
    titles = [
        attrs for tag, attrs in page.elements if tag == "title" and attrs.get("id") == "ff-title"
    ]
    descriptions = [attrs for tag, attrs in page.elements if tag == "desc"]
    assert len(titles) == 1
    assert len(descriptions) == 1
    rows = valuation["football_field"]
    assert isinstance(rows, list)
    keys_in_table = {attrs["data-key"] for attrs, _ in page.cells if "data-key" in attrs}
    for row in rows:
        assert row["low_key"] in keys_in_table
        assert row["high_key"] in keys_in_table


def test_the_expert_has_no_preferred_value_and_the_table_says_so(page: _Chart) -> None:
    assert any(text == "Not published" for _, text in page.cells)


def _hex(name: str) -> str:
    match = re.search(
        rf"--{re.escape(name)}:\s*(#[0-9a-fA-F]{{6}})", TOKENS.read_text(encoding="utf-8")
    )
    assert match, name
    return match.group(1)


def _luminance(colour: str) -> float:
    def channel(index: int) -> float:
        value = int(colour[1 + 2 * index : 3 + 2 * index], 16) / 255
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(0) + 0.7152 * channel(1) + 0.0722 * channel(2)


def _contrast(foreground: str, background: str) -> float:
    lighter, darker = sorted((_luminance(foreground), _luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


@pytest.mark.parametrize(
    ("selector", "token_name"),
    [
        (".chart .bar-mine", "owner-hatch"),
        (".chart .bar-expert", "expert-outline"),
        (".chart .preferred-tick", "owner-hatch"),
        (".chart .rule-offer", "offer-rule"),
        (".chart .rule-undisturbed", "undisturbed-rule"),
    ],
)
def test_the_edge_of_each_bar_and_line_is_at_least_3_to_1_against_the_page(
    selector: str, token_name: str
) -> None:
    css = CSS.read_text(encoding="utf-8")
    block = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css)
    assert block, selector
    assert f"var(--{token_name})" in block.group(1)
    # The notation tokens alias the colour tokens; follow one level to the hex value.
    alias = re.search(rf"--{token_name}:\s*var\(--([\w-]+)\)", TOKENS.read_text(encoding="utf-8"))
    assert alias, token_name
    assert _contrast(_hex(alias.group(1)), _hex("surface")) >= MINIMUM_GRAPHIC_CONTRAST


def test_formatting_uses_a_true_minus_and_two_decimals() -> None:
    assert number(-0.2136) == f"{MINUS}0.21"
    assert number(2401.0728) == "2,401.07"
    assert number(-0.0004) == "0.00"
    assert signed(0.27) == "+0.27"
    assert signed(-0.21) == f"{MINUS}0.21"
    assert signed(0.0) == "0.00"
    assert aud(4.2124) == "A$4.21"
    assert aud(-0.21) == f"{MINUS}A$0.21"
    assert aud_signed(0.27) == "+A$0.27"
    assert aud_signed(-0.21) == f"{MINUS}A$0.21"
    assert percent(10.0) == "10.0%"
    assert percent(-1.25, 2) == f"{MINUS}1.25%"

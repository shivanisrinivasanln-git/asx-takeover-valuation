"""Reference codes: one code for each input and each group of transcribed values, the same on
every page, and each page's markers agree with its list of sources (task P5-06)."""

import re
from dataclasses import replace
from pathlib import Path

import pytest

from valuation.inputs import Inputs, load_inputs
from valuation.output import build_valuation
from valuation.provenance import PageSources, ReferenceBook
from valuation.site_build import build_site
from valuation.site_consistency import consistency_problems
from valuation.site_frame import BuildInfo
from valuation.timeline_page import load_timeline
from valuation.valuation_page import build_valuation_page

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="17 October 2026", commit="0123456789abcdef0123456789abcdef01234567")
FIRST_INPUT = "revenue_growth_fy26_to_fy35_pct"


@pytest.fixture(scope="module")
def inputs() -> Inputs:
    return load_inputs(ROOT)


@pytest.fixture(scope="module")
def book(inputs: Inputs) -> ReferenceBook:
    return ReferenceBook(inputs)


@pytest.fixture(scope="module")
def site_dir() -> Path:
    out_dir = ROOT / "build" / "site_provenance_test"
    build_site(ROOT, out_dir, BUILD)
    return out_dir


def page_html(site_dir: Path, name: str) -> str:
    return (site_dir / name).read_text(encoding="utf-8")


def problems_after(
    inputs: Inputs, site_dir: Path, tmp_path: Path, name: str, old: str, new: str
) -> list[str]:
    edited, count = re.subn(old, new, page_html(site_dir, name), count=1)
    assert count == 1, old
    (tmp_path / name).write_text(edited, encoding="utf-8")
    return consistency_problems(
        ROOT, tmp_path, build_valuation(inputs), inputs, BUILD, load_timeline(ROOT)
    )


def test_an_input_is_a_plus_its_position_in_the_register(
    inputs: Inputs, book: ReferenceBook
) -> None:
    for position, key in enumerate(inputs.assumptions, start=1):
        assert book.for_input(key).code == f"A{position}"
    assert book.for_input(FIRST_INPUT).source == inputs.assumptions[FIRST_INPUT].source
    assert book.for_input(FIRST_INPUT).link == f"method.html#input-{FIRST_INPUT}"


def test_a_group_of_transcribed_values_shares_one_code(inputs: Inputs, book: ReferenceBook) -> None:
    rows = inputs.tables["comparable_multiples"]
    ebitda = [
        book.for_table_row("comparable_multiples", r) for r in rows if r["measure"] == "ebitda"
    ]
    ebita = [book.for_table_row("comparable_multiples", r) for r in rows if r["measure"] == "ebita"]
    assert len(set(ebitda)) == 1
    assert len(set(ebita)) == 1
    assert ebitda[0].code == "T1"
    assert ebita[0].code == "T2"
    assert ebitda[0].location == "p. 150, EBITDA multiples chart"
    assert ebitda[0].link is None


def test_every_code_is_unique(book: ReferenceBook) -> None:
    codes = [reference.code for reference in book.all_references()]
    assert len(codes) == len(set(codes))


def test_a_pages_sources_list_inputs_first_in_code_order(
    inputs: Inputs, book: ReferenceBook
) -> None:
    sources = PageSources(book)
    for key in ("tax_rate_pct", FIRST_INPUT, "offer_price_aud"):
        sources.use(book.for_input(key))
    sources.use(
        book.for_table_row("comparable_multiples", inputs.tables["comparable_multiples"][0])
    )
    codes = [reference.code for reference in sources.entries()]
    assert codes == [*sorted(codes[:-1], key=lambda code: int(code[1:])), "T1"]


def test_every_dcf_assumption_carries_the_code_of_its_input(
    site_dir: Path, book: ReferenceBook
) -> None:
    html = page_html(site_dir, "valuation.html")
    cells = re.findall(
        r'<td class="num" data-input="(\w+)"><a class="source-mark" href="#ref-(\w+)"', html
    )
    assert len(cells) == 13
    for key, code in cells:
        assert book.for_input(key).code == code


def test_the_peer_and_deal_columns_are_marked_on_their_headers(site_dir: Path) -> None:
    html = page_html(site_dir, "valuation.html")
    headers = re.findall(
        r'<th scope="col" class="num"><a class="source-mark" href="#ref-(T\d)"', html
    )
    assert headers == ["T1", "T1", "T2", "T2", "T3", "T3", "T4", "T4"]


def test_the_experts_range_and_the_reference_prices_are_marked_on_the_landing_page(
    site_dir: Path, book: ReferenceBook
) -> None:
    html = page_html(site_dir, "index.html")
    for key in ("expert_value_per_share_aud_low", "expert_value_per_share_aud_high"):
        assert re.search(rf'data-key="{key}"><a class="source-mark"', html), key
    for key in ("offer_price_aud", "undisturbed_share_price_aud"):
        code = book.for_input(key).code
        assert f'data-key="{key}"><a class="source-mark" href="#ref-{code}"' in html, key


def test_the_gap_inputs_carry_the_codes_of_the_experts_input_and_mine(
    site_dir: Path, book: ReferenceBook
) -> None:
    html = page_html(site_dir, "gap.html")
    pairs = re.findall(
        r'<th scope="row">(\w+)</th><td>[^<]*</td><td class="num"><a class="source-mark" '
        r'href="#ref-(\w+)"[^>]*>[^<]*</a></td><td class="num"><a class="source-mark" '
        r'href="#ref-(\w+)"',
        html,
    )
    assert pairs
    for key, expert_code, my_code in pairs:
        assert book.for_input(f"expert_{key}").code == expert_code
        assert book.for_input(key).code == my_code


def test_a_calculated_figure_carries_no_marker(site_dir: Path) -> None:
    html = page_html(site_dir, "valuation.html")
    calculated = re.findall(r'data-(?:key|forecast)="[^"]+"[^>]*>(.{0,30})', html)
    assert calculated
    assert not any("source-mark" in cell for cell in calculated)


def test_the_pages_have_no_problems(inputs: Inputs, site_dir: Path) -> None:
    assert (
        consistency_problems(
            ROOT, site_dir, build_valuation(inputs), inputs, BUILD, load_timeline(ROOT)
        )
        == []
    )


@pytest.mark.parametrize(
    ("page", "old", "new", "message"),
    [
        (
            "valuation.html",
            r'(data-input="tax_rate_pct"><a class="source-mark" href="#ref-)A\d+'
            r'("[^>]*data-ref=")A\d+',
            r"\g<1>A1\g<2>A1",
            "the figure for tax_rate_pct carries A1",
        ),
        (
            "valuation.html",
            r'href="#ref-A\d+" data-ref="(A\d+)"',
            r'href="#elsewhere" data-ref="\1"',
            "links to '#elsewhere'",
        ),
        (
            "valuation.html",
            r'<li id="ref-T1">',
            '<li id="ref-T9">',
            "has no entry in the list of sources",
        ),
        (
            "valuation.html",
            r'(<li id="ref-T1">.*?<span class="ref-location">)[^<]*',
            r"\g<1>p. 999",
            "the entry for T1",
        ),
        (
            "valuation.html",
            r'(<li id="ref-T1">.*?<span class="ref-date">)[^<]*',
            r"\g<1>1 January 2000",
            "the entry for T1",
        ),
        (
            "valuation.html",
            r'(<li id="ref-A\d+">.*?class="ref-link" href=")[^"]*',
            r"\g<1>method.html#input-wrong",
            "the entry for A",
        ),
        (
            "gap.html",
            r"</ul>",
            '<li id="ref-A79"><span class="ref-code">A79</span></li></ul>',
            "A79",
        ),
    ],
)
def test_a_planted_change_to_a_marker_or_an_entry_is_reported(
    inputs: Inputs,
    site_dir: Path,
    tmp_path: Path,
    page: str,
    old: str,
    new: str,
    message: str,
) -> None:
    html = page_html(site_dir, page)
    edited, count = re.subn(old, new, html, count=1, flags=re.DOTALL)
    assert count == 1, old
    (tmp_path / page).write_text(edited, encoding="utf-8")
    problems = consistency_problems(
        ROOT, tmp_path, build_valuation(inputs), inputs, BUILD, load_timeline(ROOT)
    )
    assert any(message in problem for problem in problems), problems


def test_a_column_whose_values_cite_two_sources_stops_the_build(inputs: Inputs) -> None:
    rows = list(inputs.tables["comparable_multiples"])
    rows[0] = {**rows[0], "location": "p. 151, EBITDA multiples chart"}
    changed = replace(inputs, tables={**inputs.tables, "comparable_multiples": tuple(rows)})
    with pytest.raises(ValueError, match="cite 2 sources"):
        build_valuation_page(build_valuation(changed), changed)

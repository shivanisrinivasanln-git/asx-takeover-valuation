"""The figures in the PDF report match valuation.json as the site displays them (task P6-03).

The text reader is tested on strings that hold the characters a PDF can carry (the true minus
sign, non-breaking spaces and thousands separators). The checks on a built PDF are skipped on a
machine without Typst."""

import json
from pathlib import Path
from typing import Any

import pytest

from test_report_template import build_script, clean_copy, needs_typst, valuation
from valuation.report_build import TEMPLATE_NAME
from valuation.report_check import (
    expected_figures,
    figure_problems,
    figures_in,
    pdf_text,
)

__all__ = ["valuation"]

MINUS = chr(0x2212)
BUILD_DATE = "17 October 2026"


def test_a_figure_keeps_its_true_minus_sign_and_its_thousands_separators() -> None:
    text = f"Low {MINUS}0.21 and +0.27, then 2,401.1 and {MINUS}1,234.50 in A$m."
    assert figures_in(text) == [f"{MINUS}0.21", "+0.27", "2,401.1", f"{MINUS}1,234.50"]


def test_a_hyphen_is_not_read_as_the_minus_sign() -> None:
    assert figures_in("Low -0.21") == ["-0.21"]
    assert figures_in("Low -0.21") != figures_in(f"Low {MINUS}0.21")


def test_dates_page_numbers_and_years_are_not_figures() -> None:
    assert figures_in("Valuation date 31 December 2024. Built 17 October 2026. Page 2") == []


def test_a_figure_followed_by_a_full_stop_is_read_whole() -> None:
    assert figures_in("Offer price A$4.43. Undisturbed A$3.12.") == ["4.43", "3.12"]


def test_the_expected_figures_hold_the_displayed_form_of_the_offer_price(
    valuation: dict[str, Any],
) -> None:
    expected = expected_figures(valuation)
    assert "4.43" in expected
    assert any(figure.startswith(MINUS) for figure in expected)
    assert any(figure.startswith("+") for figure in expected)
    assert any("," in figure for figure in expected)


def test_matching_text_has_no_problems(valuation: dict[str, Any]) -> None:
    text = " and ".join(expected_figures(valuation))
    assert figure_problems(valuation, text) == []


def test_a_mistyped_figure_is_named_by_its_position(valuation: dict[str, Any]) -> None:
    figures = expected_figures(valuation)
    figures[3] = "9.99"
    problems = figure_problems(valuation, " ".join(figures))
    assert problems == [
        f"figure 4: the PDF has 9.99, valuation.json gives {expected_figures(valuation)[3]}"
    ]


def test_a_missing_figure_and_an_extra_figure_are_both_reported(valuation: dict[str, Any]) -> None:
    figures = expected_figures(valuation)
    assert figure_problems(valuation, " ".join(figures[:-1]))[-1].startswith("the PDF holds")
    assert figure_problems(valuation, " ".join([*figures, "1.00"]))[-1].startswith("the PDF holds")


@needs_typst
def test_the_built_pdf_holds_exactly_the_figures_in_valuation_json(tmp_path: Path) -> None:
    root = clean_copy(tmp_path)
    pdf = build_script().build_report(root, root / "build" / "report", BUILD_DATE)
    written = json.loads((root / "build" / "report" / "valuation.json").read_text("utf-8"))
    assert figure_problems(written, pdf_text(pdf)) == []


@needs_typst
@pytest.mark.parametrize(
    ("original", "mistyped"),
    [
        ('val("offer_price_aud")', 'val("undisturbed_share_price_aud")'),
        ("number(bridge.end_value_per_share_aud)", '"4.12"'),
        ('number(val("dcf_business_operations_value_aud_m_mid"), places: 1)', '"2,628.2"'),
        ("signed(step.change_aud)", "number(step.change_aud)"),
    ],
)
def test_a_figure_mistyped_in_the_template_fails_the_check(
    tmp_path: Path, original: str, mistyped: str
) -> None:
    root = clean_copy(tmp_path)
    template = root / "report" / TEMPLATE_NAME
    source = template.read_text(encoding="utf-8")
    assert original in source
    template.write_text(source.replace(original, mistyped), encoding="utf-8")
    pdf = build_script().build_report(root, root / "build" / "report", BUILD_DATE)
    written = json.loads((root / "build" / "report" / "valuation.json").read_text("utf-8"))
    assert figure_problems(written, pdf_text(pdf)) != []


def write_pdf_with_text(path: Path, line: str) -> None:
    """A one-page PDF whose font maps code 1 to the true minus sign and code 2 to a non-breaking
    space, as a PDF made by a typesetter can; the other codes are plain ASCII."""
    cmap = "\n".join(
        [
            "/CIDInit /ProcSet findresource begin 12 dict begin begincmap",
            "1 begincodespacerange <00> <FF> endcodespacerange",
            "1 beginbfrange <20> <7E> <0020> endbfrange",
            "2 beginbfchar <01> <2212> <02> <00A0> endbfchar",
            "endcmap end end",
        ]
    )
    stream = f"BT /F1 12 Tf 72 700 Td ({line}) Tj ET"
    bodies = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R"
        " /Resources << /Font << /F1 5 0 R >> >> >>",
        f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /ToUnicode 6 0 R >>",
        f"<< /Length {len(cmap)} >>\nstream\n{cmap}\nendstream",
    ]
    out = b"%PDF-1.4\n"
    offsets = []
    for number, body in enumerate(bodies, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n{body}\nendobj\n".encode("latin-1")
    xref_at = len(out)
    entries = "".join(f"{offset:010d} 00000 n \n" for offset in offsets)
    out += f"xref\n0 {len(bodies) + 1}\n0000000000 65535 f \n{entries}".encode()
    trailer = f"trailer\n<< /Size {len(bodies) + 1} /Root 1 0 R >>\nstartxref\n{xref_at}\n%%EOF\n"
    out += trailer.encode()
    path.write_bytes(out)


def test_the_text_reader_keeps_the_minus_sign_and_collapses_non_breaking_spaces(
    tmp_path: Path,
) -> None:
    pdf = tmp_path / "fixture.pdf"
    write_pdf_with_text(pdf, "Change \\001" + "0.21,\\002and 2,401.1 and +0.27")
    text = pdf_text(pdf)
    assert text == f"Change {MINUS}0.21, and 2,401.1 and +0.27"
    assert figures_in(text) == [f"{MINUS}0.21", "2,401.1", "+0.27"]

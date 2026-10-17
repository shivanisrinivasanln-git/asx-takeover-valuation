"""The site serves the Excel model and the PDF report, and no link between its files is broken."""

from pathlib import Path

import pytest

from valuation.report_build import PDF_NAME
from valuation.site_build import (
    MODEL_HREF,
    MODEL_SOURCE,
    REPORT_HREF,
    REPORT_SOURCE,
    broken_links,
    build_site,
    copy_downloads,
)
from valuation.site_frame import BuildInfo

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="18 October 2026", commit="0123456789abcdef0123456789abcdef01234567")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_the_report_source_is_the_file_the_report_script_writes() -> None:
    assert Path("build") / "report" / PDF_NAME == REPORT_SOURCE
    assert (ROOT / MODEL_SOURCE).is_file()


def test_both_files_are_copied_to_the_addresses_the_pages_use(tmp_path: Path) -> None:
    model, report = tmp_path / "model.xlsx", tmp_path / "report.pdf"
    model.write_bytes(b"model")
    report.write_bytes(b"report")
    copy_downloads(model, report, tmp_path / "site")
    assert (tmp_path / "site" / MODEL_HREF).read_bytes() == b"model"
    assert (tmp_path / "site" / REPORT_HREF).read_bytes() == b"report"


def test_a_report_that_was_not_built_stops_the_build(tmp_path: Path) -> None:
    model = tmp_path / "model.xlsx"
    model.write_bytes(b"model")
    with pytest.raises(FileNotFoundError, match=r"report\.pdf"):
        copy_downloads(model, tmp_path / "report.pdf", tmp_path / "site")


def test_the_built_pages_have_no_broken_link() -> None:
    out_dir = ROOT / "build" / "site_links_test"
    build_site(ROOT, out_dir, BUILD)
    for href in (MODEL_HREF, REPORT_HREF):
        write(out_dir / href, "stand-in")
    assert broken_links(out_dir) == []


def test_a_missing_file_and_a_missing_id_are_reported(tmp_path: Path) -> None:
    write(tmp_path / "method.html", '<p id="register">x</p>')
    write(
        tmp_path / "index.html",
        '<a href="gone.html">a</a> <a href="method.html#register">b</a> '
        '<a href="method.html#nowhere">c</a> <img src="static/missing.png">',
    )
    assert broken_links(tmp_path) == [
        "index.html: gone.html points at a file that is not in the site",
        "index.html: method.html#nowhere points at an id that method.html lacks",
        "index.html: static/missing.png points at a file that is not in the site",
    ]


def test_an_address_off_the_site_is_not_followed(tmp_path: Path) -> None:
    write(tmp_path / "index.html", '<a href="https://www.asx.com.au/x.pdf">a</a>')
    assert broken_links(tmp_path) == []


def test_a_link_within_a_page_must_name_an_id_on_that_page(tmp_path: Path) -> None:
    write(
        tmp_path / "index.html",
        '<a href="#main">skip</a> <main id="main"></main> <a href="#ref-A1">figure</a>',
    )
    assert broken_links(tmp_path) == [
        "index.html: #ref-A1 points at an id that index.html lacks",
    ]

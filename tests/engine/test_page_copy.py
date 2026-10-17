"""Each page opens with its heading and a short introduction in my words (task P5-19). The
figures in the introductions are checked by the site consistency rules, and the links in them by
the link check of the build."""

import re
from pathlib import Path

import pytest

from valuation.site_build import build_site
from valuation.site_frame import BuildInfo

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="18 October 2026", commit="0123456789abcdef0123456789abcdef01234567")
HEADINGS = {
    "valuation.html": "How I valued Domain",
    "gap.html": "Where I differ from the expert",
    "method.html": "Method and sources",
    "timeline.html": "Deal timeline",
}


@pytest.fixture(scope="module")
def site_dir() -> Path:
    out_dir = ROOT / "build" / "site_copy_test"
    build_site(ROOT, out_dir, BUILD)
    return out_dir


@pytest.mark.parametrize(("name", "heading"), HEADINGS.items())
def test_each_page_has_its_heading_and_title(site_dir: Path, name: str, heading: str) -> None:
    html = (site_dir / name).read_text(encoding="utf-8")
    assert f"<h1>{heading}</h1>" in html
    assert re.search(rf"<title>{re.escape(heading)}, ", html)


@pytest.mark.parametrize("name", ["valuation.html", "gap.html", "timeline.html"])
def test_each_page_opens_with_an_introduction(site_dir: Path, name: str) -> None:
    html = (site_dir / name).read_text(encoding="utf-8")
    body = html[html.index("<main") :]
    first_content = min(body.find(tag) for tag in ("<h2", "<ol", "<table") if tag in body)
    assert 0 < body.index('<p class="lead">') < first_content


def test_the_method_page_explains_how_the_methods_combine_with_the_tested_weights(
    site_dir: Path,
) -> None:
    html = (site_dir / "method.html").read_text(encoding="utf-8")
    section = re.search(r'aria-labelledby="combine-heading">(.*?)</section>', html, re.DOTALL)
    assert section
    assert 'data-key="method_weight_dcf_pct"' in section.group(1)
    assert 'data-key="method_weight_trading_pct"' in section.group(1)
    assert 'href="gap.html#step-weights"' in section.group(1)


def test_the_valuation_page_points_to_the_trading_step_for_its_pages(site_dir: Path) -> None:
    html = (site_dir / "valuation.html").read_text(encoding="utf-8")
    assert 'href="gap.html#step-trading_multiples"' in html

"""The link-preview image is a 1200 by 630 picture of the verdict and the football field, and
every page names it with an absolute address (task P5-22). Rendering drives the Chrome installed
on the machine."""

import html
import re
from pathlib import Path

import pytest

from valuation.football_field import build_football_field
from valuation.inputs import load_inputs
from valuation.landing import build_verdict, source_refs
from valuation.link_preview import (
    PREVIEW_HEIGHT_PX,
    PREVIEW_HREF,
    PREVIEW_WIDTH_PX,
    SITE_URL,
    png_size,
    render_preview,
)
from valuation.output import build_valuation
from valuation.site_build import PAGES, PREVIEW_CARD, build_site, preview_dir
from valuation.site_frame import BuildInfo

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="18 October 2026", commit="0123456789abcdef0123456789abcdef01234567")


@pytest.fixture(scope="module")
def site_dir() -> Path:
    out_dir = ROOT / "build" / "site_preview_test"
    build_site(ROOT, out_dir, BUILD)
    return out_dir


@pytest.fixture(scope="module")
def sentence() -> str:
    inputs = load_inputs(ROOT)
    valuation = build_valuation(inputs)
    field = build_football_field(valuation, inputs)
    return build_verdict(valuation, source_refs(field)).sentence()


def meta(page: str, attribute: str, name: str) -> str:
    match = re.search(rf'<meta {attribute}="{re.escape(name)}" content="([^"]*)">', page)
    assert match, name
    return html.unescape(match.group(1))


@pytest.mark.parametrize("name", PAGES)
def test_every_page_names_the_image_with_an_absolute_address(
    site_dir: Path, name: str, sentence: str
) -> None:
    page = (site_dir / name).read_text(encoding="utf-8")
    assert meta(page, "property", "og:image") == SITE_URL + PREVIEW_HREF
    assert meta(page, "property", "og:image:width") == str(PREVIEW_WIDTH_PX)
    assert meta(page, "property", "og:image:height") == str(PREVIEW_HEIGHT_PX)
    assert meta(page, "property", "og:url") == SITE_URL + name
    assert meta(page, "property", "og:description") == sentence
    assert meta(page, "name", "twitter:card") == "summary_large_image"


def test_the_card_holds_the_verdict_and_the_chart_in_the_light_theme(
    site_dir: Path, sentence: str
) -> None:
    card = (preview_dir(site_dir) / PREVIEW_CARD).read_text(encoding="utf-8")
    assert '<html lang="en-AU" data-theme="light">' in card
    assert html.unescape(sentence) in html.unescape(card)
    assert '<svg class="chart"' in card
    assert not (site_dir / PREVIEW_CARD).exists()


def test_the_image_is_rendered_at_the_preview_size(site_dir: Path) -> None:
    png = site_dir / PREVIEW_HREF
    render_preview(preview_dir(site_dir) / PREVIEW_CARD, png)
    assert png_size(png) == (PREVIEW_WIDTH_PX, PREVIEW_HEIGHT_PX)


def test_a_file_that_is_not_a_png_is_refused(tmp_path: Path) -> None:
    other = tmp_path / "preview.png"
    other.write_bytes(b"GIF89a")
    with pytest.raises(ValueError, match="not a PNG"):
        png_size(other)

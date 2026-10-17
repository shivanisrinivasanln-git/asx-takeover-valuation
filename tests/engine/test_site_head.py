"""The head of every page links the favicon and preloads the font (task P5-17). The favicon is
drawn from the accent colour in tokens.css, so that colour is written in one place."""

import re
from pathlib import Path

import pytest

from valuation.site_build import PAGES, build_site, favicon_svg
from valuation.site_frame import BuildInfo

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="17 October 2026", commit="0123456789abcdef0123456789abcdef01234567")
FAVICON_LINK = '<link rel="icon" href="static/favicon.svg" type="image/svg+xml">'
FONT_PRELOAD = (
    '<link rel="preload" href="static/fonts/AtkinsonHyperlegibleNext-subset.woff2" '
    'as="font" type="font/woff2" crossorigin>'
)


@pytest.fixture(scope="module")
def site_dir() -> Path:
    out_dir = ROOT / "build" / "site_head_test"
    build_site(ROOT, out_dir, BUILD)
    return out_dir


def accent_hex() -> str:
    tokens = (ROOT / "site" / "static" / "tokens.css").read_text(encoding="utf-8")
    match = re.search(r"--accent:\s*(#[0-9a-fA-F]{6})\s*;", tokens)
    assert match
    return match.group(1)


def test_the_favicon_is_a_square_in_the_accent_colour(site_dir: Path) -> None:
    svg = (site_dir / "static" / "favicon.svg").read_text(encoding="utf-8")
    assert re.fullmatch(
        r'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
        r'<rect width="16" height="16" fill="(#[0-9a-f]{6})"/></svg>\n',
        svg,
    )
    assert accent_hex().lower() in svg


@pytest.mark.parametrize("name", PAGES)
def test_every_page_links_the_favicon_and_preloads_the_font(site_dir: Path, name: str) -> None:
    html = (site_dir / name).read_text(encoding="utf-8")
    assert FAVICON_LINK in html
    assert FONT_PRELOAD in html
    assert (site_dir / "static" / "fonts" / "AtkinsonHyperlegibleNext-subset.woff2").is_file()


def test_no_stylesheet_or_template_holds_the_favicon_colour_outside_the_tokens() -> None:
    other_files = [
        path
        for path in (ROOT / "site").rglob("*")
        if path.is_file() and path.suffix in {".css", ".svg", ".j2"} and path.name != "tokens.css"
    ]
    assert not [path for path in other_files if accent_hex().lower() in path.read_text().lower()]


def test_a_tokens_file_with_no_accent_stops_the_build(tmp_path: Path) -> None:
    static = tmp_path / "site" / "static"
    static.mkdir(parents=True)
    (static / "tokens.css").write_text(":root { --ink: #1a2332; }\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no --accent colour"):
        favicon_svg(tmp_path)

"""Every built page passes axe at a phone width and a laptop width, also with the Show sources
switch on and a source popover open (task P5-16). The tests drive the Chrome that is installed on
the machine. Axe is injected as a script, which the pages' own policy blocks, so only this test's
browser context ignores the policy; the pages are unchanged."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Browser, Page, sync_playwright

from valuation.site_build import build_site
from valuation.site_frame import BuildInfo

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="17 October 2026", commit="0123456789abcdef0123456789abcdef01234567")
WIDTHS_PX = (390, 1280)
HEIGHT_PX = 900
PAGES = ("index.html", "valuation.html", "gap.html", "method.html", "timeline.html")
PAGES_WITH_SOURCES = ("index.html", "valuation.html", "gap.html")
SWITCH = ".sources-switch"
MARKER = "a.source-mark"
POPOVER = "#source-popover"


@pytest.fixture(scope="module")
def browser() -> Iterator[Browser]:
    with sync_playwright() as playwright:
        chrome = playwright.chromium.launch(channel="chrome")
        yield chrome
        chrome.close()


@pytest.fixture(scope="module")
def site_dir() -> Path:
    out_dir = ROOT / "build" / "site_axe_test"
    build_site(ROOT, out_dir, BUILD)
    return out_dir


@contextmanager
def open_page(browser: Browser, site_dir: Path, name: str, width_px: int) -> Iterator[Page]:
    context = browser.new_context(
        viewport={"width": width_px, "height": HEIGHT_PX}, bypass_csp=True
    )
    page = context.new_page()
    page.goto((site_dir / name).as_uri())
    try:
        yield page
    finally:
        context.close()


def violations_report(page: Page) -> str:
    results = Axe().run(page)
    return results.generate_report() if results.violations_count else ""


@pytest.mark.parametrize("width_px", WIDTHS_PX)
@pytest.mark.parametrize("name", PAGES)
def test_a_page_has_no_axe_violations(
    browser: Browser, site_dir: Path, name: str, width_px: int
) -> None:
    with open_page(browser, site_dir, name, width_px) as page:
        assert violations_report(page) == ""


@pytest.mark.parametrize("width_px", WIDTHS_PX)
@pytest.mark.parametrize("name", PAGES_WITH_SOURCES)
def test_a_page_with_the_show_sources_switch_on_has_no_axe_violations(
    browser: Browser, site_dir: Path, name: str, width_px: int
) -> None:
    with open_page(browser, site_dir, name, width_px) as page:
        page.locator(SWITCH).click()
        assert page.locator(SWITCH).get_attribute("aria-pressed") == "true"
        assert violations_report(page) == ""


@pytest.mark.parametrize("width_px", WIDTHS_PX)
@pytest.mark.parametrize("name", PAGES_WITH_SOURCES)
def test_a_page_with_a_source_popover_open_has_no_axe_violations(
    browser: Browser, site_dir: Path, name: str, width_px: int
) -> None:
    with open_page(browser, site_dir, name, width_px) as page:
        page.locator(MARKER).first.click()
        assert page.locator(POPOVER).is_visible()
        assert violations_report(page) == ""

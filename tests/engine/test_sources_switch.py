"""The Show sources switch is off by default, prints each figure's reference code beside it when
on, and the page works when the script does not run (task P5-07). The tests drive the Chrome that
is installed on the machine."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page, Route, sync_playwright

from valuation.site_build import build_site
from valuation.site_frame import BuildInfo

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="17 October 2026", commit="0123456789abcdef0123456789abcdef01234567")
PHONE_WIDTH_PX = 390
PHONE_HEIGHT_PX = 800
SWITCH = ".sources-switch"
PAGES_WITH_SWITCH = ("index.html", "valuation.html", "gap.html")
PAGES_WITHOUT_SWITCH = ("method.html", "timeline.html", "about.html")

# Compares what each marker prints after it with its own reference code.
MISMATCHES = """() => Array.from(document.querySelectorAll('a.source-mark'))
    .filter(mark => getComputedStyle(mark, '::after').content !== '"' + mark.dataset.ref + '"')
    .map(mark => mark.dataset.ref)"""
PRINTED = """() => Array.from(document.querySelectorAll('a.source-mark'))
    .map(mark => getComputedStyle(mark, '::after').content)"""


@pytest.fixture(scope="module")
def browser() -> Iterator[Browser]:
    with sync_playwright() as playwright:
        chrome = playwright.chromium.launch(channel="chrome")
        yield chrome
        chrome.close()


@pytest.fixture(scope="module")
def site_dir() -> Path:
    out_dir = ROOT / "build" / "site_switch_test"
    build_site(ROOT, out_dir, BUILD)
    return out_dir


@pytest.fixture
def page(browser: Browser, site_dir: Path) -> Iterator[Page]:
    opened = browser.new_page(viewport={"width": PHONE_WIDTH_PX, "height": PHONE_HEIGHT_PX})
    opened.goto((site_dir / "valuation.html").as_uri())
    yield opened
    opened.close()


def test_the_switch_is_off_by_default_and_no_code_is_printed(page: Page) -> None:
    assert page.locator(SWITCH).is_visible()
    assert page.locator(SWITCH).get_attribute("aria-pressed") == "false"
    assert page.locator(SWITCH).inner_text() == "Show sources"
    printed = set(page.evaluate(PRINTED))
    assert printed <= {"none", "normal"}


def test_turning_it_on_prints_each_figures_own_reference_code(page: Page) -> None:
    page.locator(SWITCH).click()
    assert page.locator(SWITCH).get_attribute("aria-pressed") == "true"
    assert page.evaluate(MISMATCHES) == []
    assert len(page.evaluate(PRINTED)) > 20


def test_turning_it_off_again_removes_the_codes(page: Page) -> None:
    page.locator(SWITCH).click()
    page.locator(SWITCH).click()
    assert page.locator(SWITCH).get_attribute("aria-pressed") == "false"
    assert set(page.evaluate(PRINTED)) <= {"none", "normal"}


def test_the_keyboard_turns_it_on_and_off(page: Page) -> None:
    page.locator(SWITCH).focus()
    page.keyboard.press("Space")
    assert page.locator(SWITCH).get_attribute("aria-pressed") == "true"
    page.keyboard.press("Enter")
    assert page.locator(SWITCH).get_attribute("aria-pressed") == "false"


def test_the_switch_shows_a_focus_ring(page: Page) -> None:
    page.locator(SWITCH).focus()
    assert page.evaluate("getComputedStyle(document.activeElement).outlineStyle") != "none"


def test_a_popover_closes_when_the_switch_changes_the_layout(page: Page) -> None:
    page.locator('[aria-label="DCF assumptions table"] a.source-mark').first.click()
    assert page.locator("#source-popover").is_visible()
    page.locator(SWITCH).click()
    assert page.locator("#source-popover").is_hidden()


@pytest.mark.parametrize("name", PAGES_WITH_SWITCH)
def test_the_codes_do_not_widen_the_page(browser: Browser, site_dir: Path, name: str) -> None:
    opened = browser.new_page(viewport={"width": PHONE_WIDTH_PX, "height": PHONE_HEIGHT_PX})
    opened.goto((site_dir / name).as_uri())
    opened.locator(SWITCH).click()
    assert opened.evaluate("document.documentElement.scrollWidth") <= PHONE_WIDTH_PX
    opened.close()


@pytest.mark.parametrize("name", PAGES_WITH_SWITCH)
def test_a_page_with_sourced_figures_has_the_switch_hidden_in_its_markup(
    site_dir: Path, name: str
) -> None:
    html = (site_dir / name).read_text(encoding="utf-8")
    assert 'class="sources-switch" aria-pressed="false" hidden>Show sources</button>' in html


@pytest.mark.parametrize("name", PAGES_WITHOUT_SWITCH)
def test_a_page_with_no_sourced_figures_has_no_switch(site_dir: Path, name: str) -> None:
    assert "sources-switch" not in (site_dir / name).read_text(encoding="utf-8")


def test_when_the_script_is_blocked_the_switch_stays_hidden_and_the_links_still_work(
    browser: Browser, site_dir: Path
) -> None:
    opened = browser.new_page(viewport={"width": PHONE_WIDTH_PX, "height": PHONE_HEIGHT_PX})

    def refuse(route: Route) -> None:
        route.abort()

    opened.route("**/sources.js", refuse)
    opened.goto((site_dir / "valuation.html").as_uri())
    assert opened.locator(SWITCH).is_hidden()
    assert opened.locator("#source-popover").is_hidden()
    mark = opened.locator('[aria-label="DCF assumptions table"] a.source-mark').first
    code = mark.get_attribute("data-ref")
    mark.click()
    assert opened.url.endswith(f"#ref-{code}")
    assert opened.locator(f"#ref-{code}").is_visible()
    opened.close()


def test_when_scripting_is_off_the_page_reads_with_no_switch(
    browser: Browser, site_dir: Path
) -> None:
    context = browser.new_context(java_script_enabled=False)
    opened = context.new_page()
    opened.goto((site_dir / "valuation.html").as_uri())
    assert opened.locator(SWITCH).is_hidden()
    assert opened.locator("h1").inner_text() == "How I valued Domain"
    assert opened.locator("#sources-heading").is_visible()
    context.close()

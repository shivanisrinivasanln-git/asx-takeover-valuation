"""At 390 px a wide table scrolls sideways from the keyboard and keeps its first column in place
(task P5-10). The test drives the Chrome that is installed on the machine."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Browser, FloatRect, Page, sync_playwright

from valuation.site_build import build_site
from valuation.site_frame import BuildInfo

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="17 October 2026", commit="0123456789abcdef0123456789abcdef01234567")
PHONE_WIDTH_PX = 390
PHONE_HEIGHT_PX = 800
MAX_TABS = 60
SCROLL_PRESSES = 5
EDGE_TOLERANCE_PX = 1.0
SCROLL_POLL_MS = 100
SCROLL_POLLS = 30
# The valuation page has ten tables, each in its own scroll region. A new table changes this.
SCROLL_REGIONS_ON_PAGE = 10
WIDE_TABLES = ("Peer multiples", "Precedent transaction multiples", "Free cash flow forecast")


@pytest.fixture(scope="module")
def browser() -> Iterator[Browser]:
    with sync_playwright() as playwright:
        chrome = playwright.chromium.launch(channel="chrome")
        yield chrome
        chrome.close()


@pytest.fixture(scope="module")
def valuation_url() -> str:
    out_dir = ROOT / "build" / "site_scroll_test"
    build_site(ROOT, out_dir, BUILD)
    return (out_dir / "valuation.html").as_uri()


@pytest.fixture
def page(browser: Browser, valuation_url: str) -> Iterator[Page]:
    opened = browser.new_page(viewport={"width": PHONE_WIDTH_PX, "height": PHONE_HEIGHT_PX})
    opened.goto(valuation_url)
    yield opened
    opened.close()


def tab_to(page: Page, label: str) -> None:
    """Press Tab until the region with this label has the focus."""
    for _ in range(MAX_TABS):
        page.keyboard.press("Tab")
        if page.evaluate("document.activeElement.getAttribute('aria-label')") == label:
            return
    raise AssertionError(f"Tab never reached the region {label!r}")


def scroll_position_at_rest(page: Page, region: str) -> float:
    """The container's scrollLeft once two reads in a row agree.

    A key press scrolls with an animation. The page's policy forbids evaluating strings, so
    this polls from the test and does not use `wait_for_function`.
    """
    previous = -1.0
    for _ in range(SCROLL_POLLS):
        current = float(page.evaluate(f"document.querySelector('{region}').scrollLeft"))
        if current == previous:
            return current
        previous = current
        page.wait_for_timeout(SCROLL_POLL_MS)
    raise AssertionError(f"{region} was still scrolling after {SCROLL_POLLS * SCROLL_POLL_MS} ms")


def box(page: Page, selector: str) -> FloatRect:
    found = page.locator(selector).first.bounding_box()
    assert found is not None, selector
    return found


@pytest.mark.parametrize("label", WIDE_TABLES)
def test_a_wide_table_scrolls_sideways_with_the_arrow_key(page: Page, label: str) -> None:
    tab_to(page, label)
    region = f'[aria-label="{label}"]'
    assert page.evaluate(f"document.querySelector('{region}').scrollLeft") == 0
    assert page.evaluate(
        f"document.querySelector('{region}').scrollWidth"
        f" > document.querySelector('{region}').clientWidth"
    )
    for _ in range(SCROLL_PRESSES):
        page.keyboard.press("ArrowRight")
    assert scroll_position_at_rest(page, region) > 0


@pytest.mark.parametrize("label", WIDE_TABLES)
def test_the_first_column_stays_at_the_left_edge_while_the_rest_scrolls(
    page: Page, label: str
) -> None:
    region = f'[aria-label="{label}"]'
    row_header = f"{region} tbody tr:first-child th"
    last_cell = f"{region} tbody tr:first-child td:last-child"
    left_before = box(page, last_cell)["x"]
    tab_to(page, label)
    for _ in range(SCROLL_PRESSES):
        page.keyboard.press("ArrowRight")
    assert scroll_position_at_rest(page, region) > 0
    edge = box(page, region)["x"]
    assert box(page, row_header)["x"] == pytest.approx(edge, abs=EDGE_TOLERANCE_PX)
    assert box(page, last_cell)["x"] < left_before


def test_every_scroll_container_can_be_reached_by_keyboard_and_shows_a_focus_ring(
    page: Page,
) -> None:
    labels = page.eval_on_selector_all(
        ".table-scroll", "elements => elements.map(element => element.getAttribute('aria-label'))"
    )
    assert len(labels) == SCROLL_REGIONS_ON_PAGE
    for label in labels:
        tab_to(page, label)
        outline = page.evaluate("getComputedStyle(document.activeElement).outlineStyle")
        assert outline != "none", label

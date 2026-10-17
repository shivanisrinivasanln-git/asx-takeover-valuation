"""A sourced figure opens its document, page and date in a popover by keyboard and by tap, and
the page still reads and links to the same entry without the script (task P5-06).

The tests drive the Chrome that is installed on the machine. The page's own policy forbids
evaluating strings, so nothing here waits with `wait_for_function`.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Browser, FloatRect, Page, sync_playwright

from valuation.inputs import Inputs, load_inputs
from valuation.provenance import Reference, ReferenceBook
from valuation.site_build import build_site
from valuation.site_frame import BuildInfo

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="17 October 2026", commit="0123456789abcdef0123456789abcdef01234567")
PHONE_WIDTH_PX = 390
PHONE_HEIGHT_PX = 800
MAX_TABS = 200
FIRST_INPUT = "revenue_growth_fy26_to_fy35_pct"
POPOVER = "#source-popover"
DCF_MARK = '[aria-label="DCF assumptions table"] a.source-mark'
EDGE_TOLERANCE_PX = 1.0
PAGES_WITH_SOURCES = ("index.html", "valuation.html", "gap.html")
PAGES_WITHOUT_SOURCES = ("method.html", "timeline.html")


@pytest.fixture(scope="module")
def browser() -> Iterator[Browser]:
    with sync_playwright() as playwright:
        chrome = playwright.chromium.launch(channel="chrome")
        yield chrome
        chrome.close()


@pytest.fixture(scope="module")
def site_dir() -> Path:
    out_dir = ROOT / "build" / "site_marker_test"
    build_site(ROOT, out_dir, BUILD)
    return out_dir


@pytest.fixture(scope="module")
def inputs() -> Inputs:
    return load_inputs(ROOT)


@pytest.fixture(scope="module")
def book(inputs: Inputs) -> ReferenceBook:
    return ReferenceBook(inputs)


@pytest.fixture
def page(browser: Browser, site_dir: Path) -> Iterator[Page]:
    opened = browser.new_page(viewport={"width": PHONE_WIDTH_PX, "height": PHONE_HEIGHT_PX})
    opened.goto((site_dir / "valuation.html").as_uri())
    yield opened
    opened.close()


def first_mark(region: str) -> str:
    return f'[aria-label="{region}"] a.source-mark'


def box_of(page: Page, selector: str) -> FloatRect:
    found = page.locator(selector).first.bounding_box()
    assert found is not None, selector
    return found


def tab_to_mark(page: Page, selector: str) -> None:
    """Press Tab until the first marker matching the selector has the focus."""
    target = page.locator(selector).first
    target_id = target.get_attribute("data-ref")
    for _ in range(MAX_TABS):
        page.keyboard.press("Tab")
        if page.evaluate("document.activeElement.getAttribute('data-ref')") == target_id:
            return
    raise AssertionError(f"Tab never reached {selector}")


def popover_facts(page: Page) -> dict[str, str]:
    return {
        "name": page.locator(".source-popover-name").inner_text(),
        "document": page.locator('[data-field="document"]').inner_text(),
        "page": page.locator('[data-field="page"]').inner_text(),
        "date": page.locator('[data-field="date"]').inner_text(),
    }


def expected_facts(reference: Reference) -> dict[str, str]:
    return {
        "name": reference.name,
        "document": reference.source,
        "page": reference.location,
        "date": reference.as_at,
    }


def test_enter_opens_the_source_and_escape_closes_it_and_returns_to_the_figure(
    page: Page, book: ReferenceBook
) -> None:
    selector = DCF_MARK
    tab_to_mark(page, selector)
    assert page.locator(POPOVER).is_hidden()
    page.keyboard.press("Enter")
    assert page.locator(POPOVER).is_visible()
    assert popover_facts(page) == expected_facts(book.for_input(FIRST_INPUT))
    assert page.evaluate("document.activeElement.id") == "source-popover"
    assert page.locator(selector).first.get_attribute("aria-expanded") == "true"
    page.keyboard.press("Escape")
    assert page.locator(POPOVER).is_hidden()
    assert page.evaluate("document.activeElement.getAttribute('data-ref')") == (
        book.for_input(FIRST_INPUT).code
    )
    assert page.locator(selector).first.get_attribute("aria-expanded") == "false"


def test_tab_walks_through_the_popover_and_back_to_the_figure(
    page: Page, book: ReferenceBook
) -> None:
    selector = DCF_MARK
    tab_to_mark(page, selector)
    page.keyboard.press("Enter")
    page.keyboard.press("Tab")
    assert page.evaluate("document.activeElement.className") == "source-popover-link"
    page.keyboard.press("Tab")
    assert page.evaluate("document.activeElement.className") == "source-popover-close"
    page.keyboard.press("Tab")
    assert page.locator(POPOVER).is_hidden()
    assert page.evaluate("document.activeElement.getAttribute('data-ref')") == (
        book.for_input(FIRST_INPUT).code
    )


def test_shift_tab_from_the_popover_returns_to_the_figure(page: Page) -> None:
    tab_to_mark(page, DCF_MARK)
    page.keyboard.press("Enter")
    page.keyboard.press("Shift+Tab")
    assert page.locator(POPOVER).is_hidden()
    assert page.evaluate("document.activeElement.classList.contains('source-mark')")


def test_the_close_button_dismisses_the_popover(page: Page) -> None:
    page.locator(DCF_MARK).first.click()
    assert page.locator(POPOVER).is_visible()
    page.locator(".source-popover-close").click()
    assert page.locator(POPOVER).is_hidden()


def test_the_link_in_the_popover_goes_to_the_register_row(page: Page) -> None:
    page.locator(DCF_MARK).first.click()
    link = page.locator(".source-popover-link")
    assert link.is_visible()
    assert link.get_attribute("href") == f"method.html#input-{FIRST_INPUT}"


def test_a_table_column_source_has_no_register_link(
    page: Page, book: ReferenceBook, inputs: Inputs
) -> None:
    row = inputs.table_row(
        "comparable_multiples", company="SEEK", measure="ebitda", basis="forecast"
    )
    reference = book.for_table_row("comparable_multiples", row)
    page.locator(first_mark("Peer multiples")).first.click()
    assert popover_facts(page) == expected_facts(reference)
    assert page.locator(".source-popover-link").is_hidden()


def test_a_second_figure_replaces_the_first(page: Page, book: ReferenceBook) -> None:
    marks = page.locator(DCF_MARK)
    marks.nth(0).click()
    first = popover_facts(page)
    marks.nth(1).click()
    assert popover_facts(page) != first
    assert marks.nth(0).get_attribute("aria-expanded") == "false"
    assert marks.nth(1).get_attribute("aria-expanded") == "true"


def test_a_click_on_the_open_figure_closes_it(page: Page) -> None:
    mark = page.locator(DCF_MARK).first
    mark.click()
    mark.click()
    assert page.locator(POPOVER).is_hidden()


def test_a_click_elsewhere_dismisses_it(page: Page) -> None:
    page.locator(DCF_MARK).first.click()
    page.locator("h1").click()
    assert page.locator(POPOVER).is_hidden()


def test_scrolling_the_page_keeps_it_beside_its_figure(page: Page) -> None:
    mark = page.locator(DCF_MARK).first
    mark.click()
    gap_before = box_of(page, POPOVER)["y"] - box_of(page, DCF_MARK)["y"]
    page.mouse.wheel(0, 100)
    page.wait_for_timeout(200)
    assert page.locator(POPOVER).is_visible()
    gap_after = box_of(page, POPOVER)["y"] - box_of(page, DCF_MARK)["y"]
    assert gap_after == pytest.approx(gap_before, abs=EDGE_TOLERANCE_PX)


def test_scrolling_the_table_sideways_dismisses_it(page: Page) -> None:
    page.locator(DCF_MARK).first.click()
    page.evaluate(
        "document.querySelector('[aria-label=\"DCF assumptions table\"]').scrollLeft = 40"
    )
    page.wait_for_timeout(200)
    assert page.locator(POPOVER).is_hidden()


def test_the_popover_sits_under_the_figure_and_inside_the_phone_screen(page: Page) -> None:
    mark = page.locator(DCF_MARK).first
    mark.click()
    box = page.locator(POPOVER).bounding_box()
    figure = mark.bounding_box()
    assert box is not None
    assert figure is not None
    assert box["x"] >= 0
    assert box["x"] + box["width"] <= PHONE_WIDTH_PX + EDGE_TOLERANCE_PX
    below = box["y"] >= figure["y"] + figure["height"] - EDGE_TOLERANCE_PX
    above = box["y"] + box["height"] <= figure["y"] + EDGE_TOLERANCE_PX
    assert below or above
    assert box["y"] >= 0
    assert box["y"] + box["height"] <= PHONE_HEIGHT_PX + EDGE_TOLERANCE_PX


def test_opening_a_source_breaks_none_of_the_pages_security_rules(
    browser: Browser, site_dir: Path
) -> None:
    opened = browser.new_page(viewport={"width": PHONE_WIDTH_PX, "height": PHONE_HEIGHT_PX})
    problems: list[str] = []
    opened.on(
        "console",
        lambda message: problems.append(message.text) if message.type == "error" else None,
    )
    opened.on("pageerror", lambda error: problems.append(str(error)))
    opened.goto((site_dir / "valuation.html").as_uri())
    opened.locator(DCF_MARK).first.click()
    assert opened.locator(POPOVER).is_visible()
    opened.close()
    assert problems == []


def test_a_tap_opens_the_source_and_a_tap_elsewhere_dismisses_it(
    browser: Browser, site_dir: Path, book: ReferenceBook
) -> None:
    context = browser.new_context(
        viewport={"width": PHONE_WIDTH_PX, "height": PHONE_HEIGHT_PX},
        has_touch=True,
        is_mobile=True,
    )
    opened = context.new_page()
    opened.goto((site_dir / "valuation.html").as_uri())
    opened.locator(DCF_MARK).first.tap()
    assert opened.locator(POPOVER).is_visible()
    assert popover_facts(opened) == expected_facts(book.for_input(FIRST_INPUT))
    opened.locator("h1").tap()
    assert opened.locator(POPOVER).is_hidden()
    opened.locator(DCF_MARK).first.tap()
    opened.locator(".source-popover-close").tap()
    assert opened.locator(POPOVER).is_hidden()
    context.close()


def test_without_the_script_a_figure_links_to_its_entry_in_the_list(
    browser: Browser, site_dir: Path, book: ReferenceBook
) -> None:
    context = browser.new_context(
        viewport={"width": PHONE_WIDTH_PX, "height": PHONE_HEIGHT_PX}, java_script_enabled=False
    )
    opened = context.new_page()
    opened.goto((site_dir / "valuation.html").as_uri())
    code = book.for_input(FIRST_INPUT).code
    opened.locator(DCF_MARK).first.click()
    assert opened.url.endswith(f"#ref-{code}")
    assert opened.locator(":target").get_attribute("id") == f"ref-{code}"
    assert opened.locator(POPOVER).is_hidden()
    entry = opened.locator(f"#ref-{code}").inner_text()
    reference = book.for_input(FIRST_INPUT)
    for part in (reference.source, reference.location, reference.as_at):
        assert part in entry
    context.close()


@pytest.mark.parametrize("name", PAGES_WITH_SOURCES)
def test_pages_with_sourced_figures_list_their_sources_and_load_the_script(
    site_dir: Path, name: str
) -> None:
    html = (site_dir / name).read_text(encoding="utf-8")
    assert 'class="source-mark"' in html
    assert 'id="sources-heading"' in html
    assert '<script src="static/sources.js" defer></script>' in html
    assert 'id="source-popover"' in html


@pytest.mark.parametrize("name", PAGES_WITHOUT_SOURCES)
def test_pages_with_no_sourced_figures_carry_no_script(site_dir: Path, name: str) -> None:
    html = (site_dir / name).read_text(encoding="utf-8")
    assert "<script" not in html
    assert 'id="source-popover"' not in html

"""Light and dark themes: both colour sets pass the contrast rules, the page follows the system
setting until a choice is made with the switch, and the choice is kept under the one storage key
the site allows (my decision of 18 October 2026)."""

import re
from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page, sync_playwright

from valuation.site_build import build_site
from valuation.site_check import script_problems
from valuation.site_frame import BuildInfo

ROOT = Path(__file__).resolve().parents[2]
TOKENS = (ROOT / "site" / "static" / "tokens.css").read_text(encoding="utf-8")
BUILD = BuildInfo(date="18 October 2026", commit="0123456789abcdef0123456789abcdef01234567")
SWITCH = ".theme-switch"
LIGHT_SURFACE = "rgb(250, 250, 248)"
DARK_SURFACE = "rgb(15, 17, 22)"
TEXT_ROLES = ("ink", "ink-muted", "accent", "positive-variance", "negative-variance")


def block(selector: str) -> str:
    match = re.search(re.escape(selector) + r"\s*\{(.*?)\n\s*\}", TOKENS, re.DOTALL)
    assert match, selector
    return match.group(1)


def colours(body: str) -> dict[str, str]:
    """The first hex value of each custom property in a block (the color-mix line follows it)."""
    found: dict[str, str] = {}
    for name, value in re.findall(r"--([a-z-]+):\s*(#[0-9a-f]{6})", body):
        found.setdefault(name, value)
    return found


LIGHT = colours(block(":root"))
DARK = colours(block(':root[data-theme="dark"]'))


def luminance(hex_colour: str) -> float:
    def linear(channel: int) -> float:
        value = channel / 255
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

    red, green, blue = (int(hex_colour[i : i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * linear(red) + 0.7152 * linear(green) + 0.0722 * linear(blue)


def contrast(first: str, second: str) -> float:
    lighter, darker = sorted((luminance(first), luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def srgb_mix(accent: str, surface: str, share: float) -> str:
    channels = (
        round(share * int(accent[i : i + 2], 16) + (1 - share) * int(surface[i : i + 2], 16))
        for i in (1, 3, 5)
    )
    return "#" + "".join(f"{channel:02x}" for channel in channels)


def test_the_system_dark_block_and_the_chosen_dark_block_are_the_same() -> None:
    def normalised(body: str) -> list[str]:
        return [line.strip() for line in body.strip().splitlines()]

    assert normalised(block(':root:not([data-theme="light"])')) == normalised(
        block(':root[data-theme="dark"]')
    )


def test_the_dark_theme_sets_every_colour_the_light_theme_sets() -> None:
    assert set(DARK) == set(LIGHT)


@pytest.mark.parametrize("theme", [LIGHT, DARK], ids=["light", "dark"])
@pytest.mark.parametrize("background", ["surface", "surface-band", "surface-raised"])
def test_text_colours_reach_4_5_to_1_on_every_background(
    theme: dict[str, str], background: str
) -> None:
    for role in TEXT_ROLES:
        assert contrast(theme[role], theme[background]) >= 4.5, role


@pytest.mark.parametrize("theme", [LIGHT, DARK], ids=["light", "dark"])
def test_control_borders_reach_3_to_1(theme: dict[str, str]) -> None:
    for background in ("surface", "surface-band"):
        assert contrast(theme["rule-strong"], theme[background]) >= 3.0


@pytest.mark.parametrize("theme", [LIGHT, DARK], ids=["light", "dark"])
def test_my_hatch_stays_distinct_from_the_expert_outline(theme: dict[str, str]) -> None:
    # The accent (my bars) and the ink (the expert's outline) also differ in pattern and hue. This
    # minimum is just under the dark theme's 1.95:1, so a later colour change cannot bring them
    # closer.
    assert contrast(theme["accent"], theme["ink"]) >= 1.9


@pytest.mark.parametrize("theme", [LIGHT, DARK], ids=["light", "dark"])
def test_tint_fallbacks_are_the_srgb_mix_of_accent_and_surface(theme: dict[str, str]) -> None:
    assert theme["accent-wash"] == srgb_mix(theme["accent"], theme["surface"], 0.06)
    assert theme["accent-tint"] == srgb_mix(theme["accent"], theme["surface"], 0.12)


@pytest.mark.parametrize(
    ("code", "allowed"),
    [
        ('var t = localStorage.getItem("theme");', True),
        ('localStorage.setItem("theme", next);', True),
        ('var t = localStorage.getItem("other");', False),
        ('localStorage.removeItem("theme");', False),
        ('localStorage.setItem("theme2", x);', False),
        ("var store = localStorage;", False),
        ('var t = sessionStorage.getItem("theme");', False),
    ],
)
def test_only_the_theme_key_may_be_stored(code: str, allowed: bool) -> None:
    assert (script_problems(code) == []) is allowed


@pytest.fixture(scope="module")
def site_dir() -> Path:
    out_dir = ROOT / "build" / "site_theme_test"
    build_site(ROOT, out_dir, BUILD)
    return out_dir


@pytest.fixture(scope="module")
def browser() -> Iterator[Browser]:
    with sync_playwright() as playwright:
        chrome = playwright.chromium.launch(channel="chrome")
        yield chrome
        chrome.close()


def background(page: Page) -> str:
    return str(page.evaluate("getComputedStyle(document.body).backgroundColor"))


def open_page(browser: Browser, site_dir: Path, scheme: str, name: str = "index.html") -> Page:
    context = browser.new_context(color_scheme=scheme)  # type: ignore[arg-type]
    page = context.new_page()
    page.goto((site_dir / name).as_uri())
    return page


@pytest.mark.parametrize(
    ("scheme", "expected", "pressed"),
    [("light", LIGHT_SURFACE, "false"), ("dark", DARK_SURFACE, "true")],
)
def test_with_no_choice_the_page_follows_the_system(
    browser: Browser, site_dir: Path, scheme: str, expected: str, pressed: str
) -> None:
    page = open_page(browser, site_dir, scheme)
    assert background(page) == expected
    assert page.locator(SWITCH).is_visible()
    assert page.locator(SWITCH).get_attribute("aria-pressed") == pressed
    page.context.close()


def test_the_switch_changes_the_theme_and_the_next_page_keeps_it(
    browser: Browser, site_dir: Path
) -> None:
    page = open_page(browser, site_dir, "light")
    page.locator(SWITCH).click()
    assert background(page) == DARK_SURFACE
    assert page.locator(SWITCH).get_attribute("aria-pressed") == "true"
    page.goto((site_dir / "method.html").as_uri())
    assert page.evaluate("document.documentElement.dataset.theme") == "dark"
    assert background(page) == DARK_SURFACE
    page.locator(SWITCH).click()
    assert background(page) == LIGHT_SURFACE
    page.context.close()


def test_a_light_choice_overrides_a_dark_system(browser: Browser, site_dir: Path) -> None:
    page = open_page(browser, site_dir, "dark")
    page.locator(SWITCH).click()
    assert page.evaluate("document.documentElement.dataset.theme") == "light"
    assert background(page) == LIGHT_SURFACE
    page.context.close()


def test_without_scripting_the_switch_stays_hidden_and_the_system_theme_applies(
    browser: Browser, site_dir: Path
) -> None:
    context = browser.new_context(color_scheme="dark", java_script_enabled=False)
    page = context.new_page()
    page.goto((site_dir / "index.html").as_uri())
    assert not page.locator(SWITCH).is_visible()
    assert background(page) == DARK_SURFACE
    context.close()

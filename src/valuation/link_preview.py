"""The link-preview image: the verdict and the football field as a 1200 by 630 picture, rendered
when the site is built (task P5-22).

A page shared in a message or a post shows this image. The card is written from a template with
the same verdict and chart as the landing page and photographed by the Chrome installed on the
machine, through Playwright, in the light theme. The pages name it with an absolute address,
because a link preview is fetched from outside the site.
"""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

# The default GitHub Pages address of the repository (my decision of 18 October 2026).
SITE_URL = "https://shivanisrinivasanln-git.github.io/asx-takeover-valuation/"
PREVIEW_HREF = "static/preview.png"
PREVIEW_WIDTH_PX = 1200
PREVIEW_HEIGHT_PX = 630
PREVIEW_ALT = (
    "Football field chart of my value per share by method against the offer and the expert's range"
)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def render_preview(card_html: Path, out_png: Path) -> None:
    """Photograph the card at exactly the preview size."""
    out_png.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome")
        context = browser.new_context(
            viewport={"width": PREVIEW_WIDTH_PX, "height": PREVIEW_HEIGHT_PX},
            color_scheme="light",
        )
        page = context.new_page()
        page.goto(card_html.resolve().as_uri())
        page.screenshot(path=str(out_png))
        context.close()
        browser.close()


def png_size(png: Path) -> tuple[int, int]:
    """Width and height from a PNG file's header."""
    data = png.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError(f"{png} is not a PNG file")
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")

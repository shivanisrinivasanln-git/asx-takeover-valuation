"""Screenshot a built page at the four widths I review, in the light or the dark theme.

Usage, from the repository root:
    python scripts/screenshot.py build/site/index.html index          (light theme)
    python scripts/screenshot.py build/site/index.html index dark     (dark theme)

Writes build/screenshots/<name>_<width>.png for the light theme and <name>_dark_<width>.png for
the dark theme, at 390, 768, 1280 and 1440 px. The page follows the colour scheme the browser
reports, so the scheme is set here and does not depend on the machine's own setting. Playwright
drives the Chrome installed on the machine.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "build" / "screenshots"
WIDTHS = (390, 768, 1280, 1440)
HEIGHT = 1000
SCHEMES = ("light", "dark")


def screenshot_name(name: str, scheme: str, width: int) -> str:
    return f"{name}_{width}.png" if scheme == "light" else f"{name}_{scheme}_{width}.png"


def main() -> int:
    if len(sys.argv) not in (3, 4) or (len(sys.argv) == 4 and sys.argv[3] not in SCHEMES):
        raise SystemExit("usage: python scripts/screenshot.py <built page> <name> [light|dark]")
    page_path, name = Path(sys.argv[1]), sys.argv[2]
    scheme = sys.argv[3] if len(sys.argv) == 4 else "light"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome")
        for width in WIDTHS:
            context = browser.new_context(
                viewport={"width": width, "height": HEIGHT},
                color_scheme="dark" if scheme == "dark" else "light",
            )
            page = context.new_page()
            page.goto(page_path.resolve().as_uri())
            target = OUT_DIR / screenshot_name(name, scheme, width)
            page.screenshot(path=str(target))
            context.close()
            sys.stdout.write(f"{target}\n")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

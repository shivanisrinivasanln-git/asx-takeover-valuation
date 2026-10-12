"""Screenshot a built page at the four widths I review, using a browser already on this machine.

Usage, from the repository root: python scripts/screenshot.py build/site/index.html index

Writes build/screenshots/<name>_<width>.png for 390, 768, 1280 and 1440 px. A headless browser
will not lay a page out narrower than 500 px, so each page is shown in an iframe of exactly the
target width, inside a wrapper page; the page inside lays out at the target width.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "build" / "screenshots"
WIDTHS = (390, 768, 1280, 1440)
HEIGHT = 1000
MINIMUM_WINDOW_PX = 500
BROWSERS = (
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
)


def find_browser() -> Path:
    for browser in BROWSERS:
        if browser.is_file():
            return browser
    raise SystemExit("screenshot: no Chrome or Edge found in the usual folders; none is installed")


def screenshot(browser: Path, page: Path, name: str, width: int) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    wrapper = OUT_DIR / f"{name}_{width}.html"
    wrapper.write_text(
        '<!doctype html><body style="margin:0;background:#888">'
        f'<iframe src="{page.resolve().as_uri()}" width="{width}" height="{HEIGHT}" '
        'style="border:0;display:block"></iframe></body>',
        encoding="utf-8",
    )
    target = OUT_DIR / f"{name}_{width}.png"
    window = f"--window-size={max(width, MINIMUM_WINDOW_PX)},{HEIGHT}"
    command = [str(browser), "--headless=new", "--disable-gpu", "--hide-scrollbars", window]
    subprocess.run(
        [*command, f"--screenshot={target}", wrapper.as_uri()], check=True, capture_output=True
    )
    wrapper.unlink()
    return target


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: python scripts/screenshot.py <built page> <name>")
    browser = find_browser()
    for width in WIDTHS:
        sys.stdout.write(f"{screenshot(browser, Path(sys.argv[1]), sys.argv[2], width)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

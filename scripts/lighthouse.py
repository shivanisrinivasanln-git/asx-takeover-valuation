"""Run Lighthouse on every built page, on mobile, and fail if a page misses the budgets.

Usage, from the repository root, after `npm ci --ignore-scripts` in scripts/lighthouse:
    PYTHONPATH=src python scripts/lighthouse.py
    PYTHONPATH=src python scripts/lighthouse.py https://address/of/a/live/copy/

Without an address the pages are served from build/site on a local port, because Lighthouse
measures a page loaded over HTTP; with one, the same page names are measured at that address.
Node must be on the path (or named in NODE), and Chrome is taken from CHROME_PATH or the usual
folder. LIGHTHOUSE_CHROME_FLAGS replaces the Chrome flags; CI sets it to add --no-sandbox, which
Chrome needs on the Linux runner. Reports are written to build/lighthouse.
"""

from __future__ import annotations

import functools
import json
import os
import shutil
import subprocess
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from valuation.lighthouse_budget import PageScores, budget_problems, read_report

ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "build" / "site"
REPORT_DIR = ROOT / "build" / "lighthouse"
CLI = ROOT / "scripts" / "lighthouse" / "node_modules" / "lighthouse" / "cli" / "index.js"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
CATEGORIES = "performance,accessibility,best-practices"
CHROME_FLAGS = "--headless=new"
LOCAL_ADDRESS = "127.0.0.1"
ATTEMPTS = 3
TIMEOUT_S = 120


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


class QuietServer(ThreadingHTTPServer):
    # Chrome closes sockets it has finished with, which would print a traceback for each one.
    def handle_error(self, request: object, client_address: object) -> None:
        return


def find_node() -> str:
    node = os.environ.get("NODE") or shutil.which("node")
    if node is None:
        raise SystemExit("lighthouse: node is not on the path and NODE is not set")
    return node


def run_lighthouse(node: str, url: str, report: Path) -> None:
    env = {**os.environ, "CHROME_PATH": os.environ.get("CHROME_PATH", str(CHROME))}
    command = [
        node,
        str(CLI),
        url,
        f"--only-categories={CATEGORIES}",
        f"--chrome-flags={os.environ.get('LIGHTHOUSE_CHROME_FLAGS', CHROME_FLAGS)}",
        "--output=json",
        f"--output-path={report}",
        "--quiet",
    ]
    # Lighthouse on Windows sometimes fails while closing Chrome or hangs. A run that produced no
    # report is tried again; a report with low scores is never tried again.
    last_error = ""
    for _attempt in range(ATTEMPTS):
        try:
            result = subprocess.run(
                command, check=False, env=env, capture_output=True, text=True, timeout=TIMEOUT_S
            )
        except subprocess.TimeoutExpired:
            last_error = f"no result after {TIMEOUT_S} s"
            continue
        if result.returncode == 0:
            return
        last_error = result.stderr[-1500:]
    raise SystemExit(f"lighthouse: failed {ATTEMPTS} times on {url}\n{last_error}")


def measure(node: str, base_url: str, pages: list[Path]) -> list[str]:
    """Run Lighthouse on each page at `base_url`, print its scores and return the budget misses."""
    problems: list[str] = []
    for page in pages:
        report_path = REPORT_DIR / f"{page.stem}.json"
        run_lighthouse(node, f"{base_url}{page.name}", report_path)
        scores: PageScores = read_report(page.name, json.loads(report_path.read_text("utf-8")))
        summary = ", ".join(f"{name} {value}" for name, value in scores.score_pct.items())
        sys.stdout.write(f"{page.name}: {summary}, LCP {scores.lcp_ms / 1000:.1f} s\n")
        problems += budget_problems(scores)
    return problems


def main() -> int:
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and not sys.argv[1].startswith("https://")):
        raise SystemExit("usage: python scripts/lighthouse.py [https://address/of/a/live/copy/]")
    if not CLI.is_file():
        raise SystemExit("lighthouse: run `npm ci --ignore-scripts` in scripts/lighthouse first")
    pages = sorted(SITE_DIR.glob("*.html"))
    if not pages:
        raise SystemExit("lighthouse: build/site has no pages; run the site build first")
    node = find_node()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    if len(sys.argv) == 2:
        problems = measure(node, sys.argv[1].rstrip("/") + "/", pages)
    else:
        handler = functools.partial(QuietHandler, directory=str(SITE_DIR))
        with QuietServer((LOCAL_ADDRESS, 0), handler) as server:
            threading.Thread(target=server.serve_forever, daemon=True).start()
            port = server.server_address[1]
            problems = measure(node, f"http://{LOCAL_ADDRESS}:{port}/", pages)
            server.shutdown()
    for problem in problems:
        sys.stdout.write(f"{problem}\n")
    sys.stdout.write("lighthouse: PASS\n" if not problems else "lighthouse: FAIL\n")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())

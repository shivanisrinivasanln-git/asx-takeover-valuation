"""Run every product check in order and print one summary line.

Usage: python scripts/check.py

Each step is a command run with the interpreter that runs this script, so the
check uses the project's virtual environment when started from it. The first
failing step stops the run; its output is printed above the summary.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PATHS = ["src", "scripts", "tests/engine"]

STEPS: list[tuple[str, list[str]]] = [
    ("format", [sys.executable, "-m", "ruff", "format", "--check", *PATHS]),
    ("lint", [sys.executable, "-m", "ruff", "check", *PATHS]),
    ("types", [sys.executable, "-m", "mypy"]),
    ("tests", [sys.executable, "-m", "pytest", "-q"]),
    # The site serves the PDF report, so the report is built first. It needs Typst 0.15.1.
    ("report", [sys.executable, "scripts/build_report.py"]),
    ("build", [sys.executable, "-m", "valuation.site_build"]),
]


def run_step(name: str, command: list[str]) -> bool:
    # The package is run from src, so the build step needs it on the path.
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False, env=env)
    if result.returncode != 0:
        print(f"--- {name} failed ({' '.join(command[2:])})")
        print(result.stdout, end="")
        print(result.stderr, end="")
    return result.returncode == 0


def main() -> int:
    for name, command in STEPS:
        if not run_step(name, command):
            print(f"check: FAIL at {name}")
            return 1
    print(f"check: PASS ({len(STEPS)} steps: {', '.join(name for name, _ in STEPS)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

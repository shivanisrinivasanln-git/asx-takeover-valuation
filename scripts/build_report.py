"""Build the PDF report into build/report with the pinned Typst version.

Usage, from the repository root: PYTHONPATH=src python scripts/build_report.py

Typst is found through the TYPST variable or the path. The folder and the compile command are
prepared by src/valuation/report_build.py.
"""

from __future__ import annotations

import subprocess
import sys
from datetime import date
from pathlib import Path

from valuation.report_build import (
    FONT_DIR,
    PDF_NAME,
    check_version,
    compile_command,
    find_typst,
    prepare_folder,
)

ROOT = Path(__file__).resolve().parent.parent


def build_report(root: Path, out_dir: Path, build_date: str) -> Path:
    """Compile the report in `out_dir`, replacing what was there, and return the PDF's path."""
    typst = find_typst()
    version = subprocess.run([typst, "--version"], capture_output=True, text=True, check=True)
    check_version(version.stdout)
    template = prepare_folder(root, out_dir)
    result = subprocess.run(
        compile_command(typst, template, build_date, root / FONT_DIR),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"typst failed:\n{result.stderr}")
    return out_dir / PDF_NAME


def main() -> int:
    today = date.today()
    pdf = build_report(ROOT, ROOT / "build" / "report", f"{today.day} {today:%B %Y}")
    sys.stdout.write(f"report: wrote {pdf.relative_to(ROOT)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

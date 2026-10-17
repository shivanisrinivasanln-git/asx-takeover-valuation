"""Prepare the folder the PDF report is compiled in (task P6-01).

The template, report/report.typ, reads valuation.json and limitations.json from its own folder,
so the report is compiled in a folder that holds a copy of the template and fresh copies of both.
The compile itself is run by scripts/build_report.py, which uses the pieces here. The report is
set in the site's typeface, from the font file tracked in report/fonts under its licence.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from valuation.inputs import load_inputs
from valuation.output import write_valuation_json
from valuation.site_build import DISCLAIMER

TYPST_VERSION = "0.15.1"
TEMPLATE_NAME = "report.typ"
PDF_NAME = "report.pdf"
LIMITATIONS_NAME = "limitations.json"
FONT_DIR = Path("report") / "fonts"


def find_typst() -> str:
    """The TYPST variable, then the path."""
    typst = os.environ.get("TYPST") or shutil.which("typst")
    if typst is None:
        raise RuntimeError("typst is not on the path and TYPST is not set")
    return typst


def check_version(version_output: str) -> None:
    """Typst is before 1.0 and minor versions can break a template, so only the pinned one runs."""
    if version_output.split()[:2] != ["typst", TYPST_VERSION]:
        raise RuntimeError(f"expected typst {TYPST_VERSION}, found {version_output.strip()!r}")


def prepare_folder(root: Path, out_dir: Path) -> Path:
    """Replace `out_dir` with the template, a fresh valuation.json and the list of what I could
    not verify, and return the template."""
    build_root = (root / "build").resolve()
    if build_root not in out_dir.resolve().parents:
        raise ValueError(f"{out_dir} is not inside {build_root}; refusing to replace it")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    template = out_dir / TEMPLATE_NAME
    shutil.copyfile(root / "report" / TEMPLATE_NAME, template)
    inputs = load_inputs(root)
    write_valuation_json(inputs, out_dir / "valuation.json")
    limitations = [row["text"] for row in inputs.tables["limitations"]]
    (out_dir / LIMITATIONS_NAME).write_text(
        json.dumps(limitations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return template


def compile_command(typst: str, template: Path, build_date: str, font_dir: Path) -> list[str]:
    """The fonts are the tracked file in `font_dir` and Typst's embedded ones, never the fonts
    installed on the machine, so the PDF does not depend on where it is built. The disclaimer is
    the site's sentence, passed in as an input."""
    return [
        typst,
        "compile",
        "--root",
        str(template.parent),
        "--ignore-system-fonts",
        "--font-path",
        str(font_dir),
        "--input",
        f"disclaimer={DISCLAIMER}",
        "--input",
        f"build_date={build_date}",
        str(template),
        str(template.with_name(PDF_NAME)),
    ]

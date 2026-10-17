"""Prepare the folder the PDF report is compiled in (task P6-01).

The template, report/report.typ, reads valuation.json from its own folder, so the report is
compiled in a folder that holds a copy of the template and a fresh valuation.json. The compile
itself is run by scripts/build_report.py, which uses the pieces here.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from valuation.inputs import load_inputs
from valuation.output import write_valuation_json
from valuation.site_build import DISCLAIMER

TYPST_VERSION = "0.15.1"
TEMPLATE_NAME = "report.typ"
PDF_NAME = "report.pdf"


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
    """Replace `out_dir` with the template and a fresh valuation.json, and return the template."""
    build_root = (root / "build").resolve()
    if build_root not in out_dir.resolve().parents:
        raise ValueError(f"{out_dir} is not inside {build_root}; refusing to replace it")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    template = out_dir / TEMPLATE_NAME
    shutil.copyfile(root / "report" / TEMPLATE_NAME, template)
    write_valuation_json(load_inputs(root), out_dir / "valuation.json")
    return template


def compile_command(typst: str, template: Path, build_date: str) -> list[str]:
    """Only Typst's embedded fonts are used, so the PDF does not depend on the fonts installed on
    the machine that builds it. The disclaimer is the site's sentence, passed in as an input."""
    return [
        typst,
        "compile",
        "--root",
        str(template.parent),
        "--ignore-system-fonts",
        "--input",
        f"disclaimer={DISCLAIMER}",
        "--input",
        f"build_date={build_date}",
        str(template),
        str(template.with_name(PDF_NAME)),
    ]

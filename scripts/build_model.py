"""Build the Excel model, recalculate it in desktop Excel and write the committed workbook.

Usage, from the repository root: PYTHONPATH=src python scripts/build_model.py

openpyxl writes formulas without values, so the workbook is opened in Excel, calculated and
saved by scripts/recalculate_with_excel.ps1. The saved file holds Excel's own values, which the
reconciliation test reads (tests/engine/test_reconciliation.py). LibreOffice is not installed
on this machine, so Excel does the recalculation; the model is at model/domain_valuation_model.xlsx.
The PowerShell script is run with the execution policy bypassed for this one process, because
this machine blocks unsigned scripts and the setting itself stays unchanged.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from openpyxl import load_workbook

from valuation.inputs import load_inputs
from valuation.output import build_valuation
from valuation.reconcile import value_problems
from valuation.workbook import build_workbook

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "build" / "model_unrecalculated.xlsx"
MODEL_PATH = ROOT / "model" / "domain_valuation_model.xlsx"
RECALCULATE_SCRIPT = ROOT / "scripts" / "recalculate_with_excel.ps1"


def main() -> int:
    powershell = shutil.which("powershell")
    if powershell is None:
        raise SystemExit("model: FAIL, powershell is needed to run Excel and was not found")
    inputs = load_inputs(ROOT)
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    build_workbook(inputs).save(RAW_PATH)
    subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(RECALCULATE_SCRIPT),
            str(RAW_PATH),
            str(MODEL_PATH),
        ],
        check=True,
    )
    expected = build_valuation(inputs)["values"]
    problems = value_problems(load_workbook(MODEL_PATH, data_only=True), expected)
    if problems:
        print(f"model: FAIL, {len(problems)} named cell(s) do not reconcile")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print(f"model: wrote {MODEL_PATH.relative_to(ROOT)}, {len(expected)} named cells reconcile")
    return 0


if __name__ == "__main__":
    sys.exit(main())

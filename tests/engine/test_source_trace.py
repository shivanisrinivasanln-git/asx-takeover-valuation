"""Source trace test: every real input and data row in the repository has a source."""

from pathlib import Path

from valuation.assumptions import load_assumptions
from valuation.extracted import check_extracted_dir

ROOT = Path(__file__).resolve().parents[2]


def test_assumptions_file_is_valid() -> None:
    # The loader rejects any entry without a source, location and date, so loading is the check.
    load_assumptions(ROOT / "assumptions.yaml")


def test_every_extracted_row_has_a_source() -> None:
    check_extracted_dir(ROOT / "data" / "extracted")

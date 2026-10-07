"""Write build/valuation.json from assumptions.yaml and data/extracted/.

Usage, from the repository root: PYTHONPATH=src python -m valuation
"""

from __future__ import annotations

import sys
from pathlib import Path

from valuation.inputs import load_inputs
from valuation.output import write_valuation_json

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "build" / "valuation.json"


def main() -> int:
    write_valuation_json(load_inputs(ROOT), OUTPUT)
    sys.stdout.write(f"wrote {OUTPUT.relative_to(ROOT)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

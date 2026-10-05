"""Every item in the list of things I could not verify has a reason and a next step."""

from pathlib import Path

RESEARCH = Path(__file__).resolve().parents[2] / "docs" / "RESEARCH.md"
HEADING = "## Items I could not verify while transcribing the data and filling the inputs"


def table_rows() -> list[list[str]]:
    section = RESEARCH.read_text(encoding="utf-8").split(HEADING)[1]
    rows = []
    for line in section.splitlines():
        if line.startswith("| ") and not line.startswith(("| Item", "|---")):
            rows.append([cell.strip() for cell in line.strip("|").split(" | ")])
    return rows


def test_the_list_has_items_and_each_has_a_reason_and_a_next_step() -> None:
    rows = table_rows()
    assert len(rows) >= 10
    for row in rows:
        assert len(row) == 3, row[0]
        assert all(cell for cell in row), row[0]

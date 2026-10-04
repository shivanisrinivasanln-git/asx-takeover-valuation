"""The deal timeline: every event has a dated source and a verification status with its evidence."""

from datetime import datetime
from pathlib import Path

from valuation.extracted import load_rows

ROOT = Path(__file__).resolve().parents[2]
TIMELINE_FILE = ROOT / "data" / "extracted" / "deal_timeline.csv"
STATUSES = {"verified", "unverified"}


def parse_date(text: str) -> datetime:
    return datetime.strptime(text, "%d %B %Y")


def test_every_row_has_a_status_and_evidence() -> None:
    for row in load_rows(TIMELINE_FILE):
        assert row["status"] in STATUSES, row["date"]
        assert row["evidence"].strip(), row["date"]
        assert row["url"].startswith("https://"), row["date"]


def test_an_unverified_row_says_why() -> None:
    for row in load_rows(TIMELINE_FILE):
        if row["status"] == "unverified":
            assert row["note"].strip(), row["date"]


def test_dates_are_real_dates_in_order() -> None:
    dates = [parse_date(row["date"]) for row in load_rows(TIMELINE_FILE)]
    assert dates == sorted(dates)
    for row in load_rows(TIMELINE_FILE):
        parse_date(row["as_at"])


def test_the_timeline_runs_from_the_first_step_to_the_ruling() -> None:
    rows = load_rows(TIMELINE_FILE)
    assert rows[0]["date"] == "10 February 2025"
    assert rows[-1]["date"] == "10 December 2025"
    implemented = [row for row in rows if "scheme is implemented" in row["event"]]
    assert [row["date"] for row in implemented] == ["27 August 2025"]

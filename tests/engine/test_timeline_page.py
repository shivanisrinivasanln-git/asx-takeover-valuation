"""The deal timeline page lists every event with its date and source link (task P5-12)."""

from html.parser import HTMLParser
from pathlib import Path

import pytest

from valuation.site_build import build_site
from valuation.site_frame import BuildInfo
from valuation.timeline_page import build_timeline_page, load_timeline

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="17 October 2026", commit="0123456789abcdef0123456789abcdef01234567")


class _Events(HTMLParser):
    """Each `li` of the timeline list: its text and the links in it."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.texts: list[str] = []
        self.links: list[list[str]] = []
        self._in_list = False
        self._in_item = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "ol" and values.get("class") == "timeline":
            self._in_list = True
        if tag == "li" and self._in_list:
            self._in_item = True
            self.texts.append("")
            self.links.append([])
        if tag == "a" and self._in_item:
            self.links[-1].append(values.get("href") or "")

    def handle_data(self, data: str) -> None:
        if self._in_item:
            self.texts[-1] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "li":
            self._in_item = False
        if tag == "ol":
            self._in_list = False


@pytest.fixture(scope="module")
def events() -> _Events:
    out_dir = ROOT / "build" / "site_timeline_test"
    build_site(ROOT, out_dir, BUILD)
    parser = _Events()
    parser.feed((out_dir / "timeline.html").read_text(encoding="utf-8"))
    parser.close()
    return parser


def test_every_event_is_listed_in_order_with_its_date_and_link(events: _Events) -> None:
    rows = load_timeline(ROOT)
    assert len(events.texts) == len(rows) == 30
    for text, links, row in zip(events.texts, events.links, rows, strict=True):
        flat = " ".join(text.split())
        assert flat.startswith(row["date"]), row["date"]
        assert row["event"] in flat, row["date"]
        assert links == [row["url"]], row["date"]


def test_every_link_is_an_https_address(events: _Events) -> None:
    assert all(link.startswith("https://") for links in events.links for link in links)


def test_an_unverified_event_says_it_was_not_checked_and_why(events: _Events) -> None:
    rows = load_timeline(ROOT)
    for text, row in zip(events.texts, rows, strict=True):
        flat = " ".join(text.split())
        if row["status"] == "verified":
            assert "Checked against the source." in flat, row["date"]
            assert "Not checked" not in flat, row["date"]
        else:
            assert f"Not checked: {row['note']}" in flat, row["date"]


def test_the_summary_line_counts_the_checked_events() -> None:
    rows = load_timeline(ROOT)
    page = build_timeline_page(rows)
    assert page["total_count"] == len(rows)
    assert page["verified_count"] == sum(row["status"] == "verified" for row in rows)
    assert page["verified_count"] == 29

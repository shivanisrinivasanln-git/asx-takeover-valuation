"""The deal docket and the colophon appear on every page and match valuation.json (task P5-21)."""

from html.parser import HTMLParser
from pathlib import Path

import pytest

from valuation.inputs import load_inputs
from valuation.output import build_valuation
from valuation.site_build import DISCLAIMER, build_site
from valuation.site_frame import REPOSITORY_URL, BuildInfo, build_frame, current_commit
from valuation.timeline_page import implementation_date, load_timeline

ROOT = Path(__file__).resolve().parents[2]
COMMIT = "0123456789abcdef0123456789abcdef01234567"
BUILD = BuildInfo(date="17 October 2026", commit=COMMIT)


class _Facts(HTMLParser):
    """The labelled facts of each `dl` that has a class, the links and the paragraphs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lists: dict[str, list[tuple[str, str]]] = {}
        self.links: list[str] = []
        self.paragraphs: list[str] = []
        self._list: str | None = None
        self._tag: str | None = None
        self._label = ""
        self._text = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "dl":
            self._list = values.get("class") or ""
            self.lists[self._list] = []
        if tag in ("dt", "dd", "p"):
            self._tag, self._text = tag, ""
        if tag == "a" and values.get("href"):
            self.links.append(values["href"] or "")

    def handle_data(self, data: str) -> None:
        if self._tag:
            self._text += data

    def handle_endtag(self, tag: str) -> None:
        if tag != self._tag:
            return
        if tag == "dt":
            self._label = self._text.strip()
        elif tag == "dd" and self._list is not None:
            self.lists[self._list].append((self._label, self._text.strip()))
        elif tag == "p":
            self.paragraphs.append(self._text.strip())
        self._tag = None


def _facts(path: Path) -> _Facts:
    parser = _Facts()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


@pytest.fixture(scope="module")
def site_dir() -> Path:
    out_dir = ROOT / "build" / "site_frame_test"
    build_site(ROOT, out_dir, BUILD)
    return out_dir


def test_every_page_has_the_docket_and_the_colophon(site_dir: Path) -> None:
    pages = sorted(site_dir.glob("*.html"))
    assert {page.name for page in pages} >= {"index.html", "valuation.html", "timeline.html"}
    for page in pages:
        facts = _facts(page)
        assert [label for label, _ in facts.lists["docket"]] == [
            "Target",
            "Acquirer",
            "Consideration",
            "Implemented",
        ], page.name
        assert [label for label, _ in facts.lists["colophon"]] == [
            "Valuation date",
            "Market data as at",
            "Built",
            "Commit",
        ], page.name


def test_the_docket_and_colophon_dates_come_from_the_data(site_dir: Path) -> None:
    valuation = build_valuation(load_inputs(ROOT))
    offer = valuation["values"]["offer_price_aud"]["value"]
    implemented = implementation_date(load_timeline(ROOT))
    for page in site_dir.glob("*.html"):
        facts = _facts(page)
        docket = dict(facts.lists["docket"])
        assert docket["Target"] == valuation["meta"]["target"]
        assert (
            docket["Consideration"] == f"A${offer:.2f} a share, paid as cash and a special dividend"
        )
        assert docket["Implemented"] == implemented == "27 August 2025"
        colophon = dict(facts.lists["colophon"])
        assert colophon["Valuation date"] == valuation["meta"]["valuation_date"]
        assert colophon["Market data as at"] == valuation["meta"]["data_date"]
        assert colophon["Built"] == BUILD.date


def test_the_commit_links_to_the_repository(site_dir: Path) -> None:
    facts = _facts(site_dir / "index.html")
    assert f"{REPOSITORY_URL}/commit/{COMMIT}" in facts.links
    assert dict(facts.lists["colophon"])["Commit"] == COMMIT[:7]


def test_the_footer_carries_the_unit_note_and_the_disclaimer(site_dir: Path) -> None:
    for page in site_dir.glob("*.html"):
        paragraphs = _facts(page).paragraphs
        assert paragraphs[-2].startswith("Money is in A$ millions"), page.name
        assert paragraphs[-1] == DISCLAIMER, page.name


def test_the_data_date_is_the_date_of_the_peer_multiples_and_the_bond_yield() -> None:
    inputs = load_inputs(ROOT)
    data_date = build_valuation(inputs)["meta"]["data_date"]
    assert data_date == inputs.tables["comparable_multiples"][0]["as_at"]
    assert data_date == inputs.tables["market_rates_30_may_2025"][0]["as_at"]


def test_a_short_commit_hash_is_refused() -> None:
    valuation = build_valuation(load_inputs(ROOT))
    short = BuildInfo(date="17 October 2026", commit="abc1234")
    with pytest.raises(ValueError, match="full commit hash"):
        build_frame(valuation, short, "27 August 2025")


def test_the_commit_is_read_from_a_branch_file(tmp_path: Path) -> None:
    (tmp_path / ".git" / "refs" / "heads").mkdir(parents=True)
    (tmp_path / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (tmp_path / ".git" / "refs" / "heads" / "main").write_text(COMMIT + "\n", encoding="utf-8")
    assert current_commit(tmp_path) == COMMIT


def test_the_commit_is_read_from_the_packed_refs(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    other = "f" * 40
    (tmp_path / ".git" / "packed-refs").write_text(
        f"# pack-refs\n{other} refs/heads/other\n{COMMIT} refs/heads/main\n", encoding="utf-8"
    )
    assert current_commit(tmp_path) == COMMIT


def test_the_commit_is_read_from_a_detached_head(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "HEAD").write_text(COMMIT + "\n", encoding="utf-8")
    assert current_commit(tmp_path) == COMMIT


def test_a_branch_that_is_not_in_the_packed_refs_is_an_error(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (tmp_path / ".git" / "packed-refs").write_text("# pack-refs\n", encoding="utf-8")
    with pytest.raises(ValueError, match="is not in"):
        current_commit(tmp_path)


def test_the_commit_of_this_repository_is_a_full_hash() -> None:
    assert len(current_commit(ROOT)) == 40


def test_the_implementation_date_is_the_one_row_that_says_so() -> None:
    assert implementation_date(load_timeline(ROOT)) == "27 August 2025"


def test_a_timeline_without_exactly_one_implementation_row_is_an_error() -> None:
    rows = load_timeline(ROOT)
    implemented = [row for row in rows if row["event"].startswith("The scheme is implemented")]
    without = [row for row in rows if row not in implemented]
    with pytest.raises(ValueError, match="found 0"):
        implementation_date(without)
    with pytest.raises(ValueError, match="found 2"):
        implementation_date([*rows, *implemented])

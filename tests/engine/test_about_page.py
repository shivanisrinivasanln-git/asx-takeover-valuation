"""The About page says who I am in the words I approved, links to the repository and holds no
contact details or photo (task P5-14, my decision of 18 October 2026)."""

import re
from pathlib import Path

import pytest

from valuation.site_build import build_site
from valuation.site_frame import REPOSITORY_URL, BuildInfo

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="18 October 2026", commit="0123456789abcdef0123456789abcdef01234567")
APPROVED_FACTS = (
    "third-year Commerce student at UNSW Sydney",
    "Finance and Business Analytics",
    "background in security engineering",
    "comfortable with Python, React and Next.js",
    "Professional valuation practice is newer to me",
)


@pytest.fixture(scope="module")
def about_html() -> str:
    out_dir = ROOT / "build" / "site_about_test"
    build_site(ROOT, out_dir, BUILD)
    return (out_dir / "about.html").read_text(encoding="utf-8")


def visible_text(html: str) -> str:
    main = re.search(r"<main[^>]*>(.*?)</main>", html, re.DOTALL)
    assert main
    return " ".join(re.sub(r"<[^>]+>", " ", main.group(1)).split())


def test_the_page_states_each_approved_fact(about_html: str) -> None:
    text = visible_text(about_html)
    for fact in APPROVED_FACTS:
        assert fact in text


def test_the_page_links_to_the_repository(about_html: str) -> None:
    assert f'href="{REPOSITORY_URL}"' in about_html


def test_the_page_holds_no_contact_details_or_photo(about_html: str) -> None:
    main = re.search(r"<main[^>]*>(.*?)</main>", about_html, re.DOTALL)
    assert main
    assert "@" not in main.group(1)
    assert "mailto:" not in about_html
    assert "tel:" not in about_html
    assert "<img" not in about_html


def test_every_page_links_to_the_about_page(about_html: str) -> None:
    for page in (ROOT / "build" / "site_about_test").glob("*.html"):
        assert 'href="about.html"' in page.read_text(encoding="utf-8"), page.name

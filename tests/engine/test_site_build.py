"""The built site carries the security tags and loads nothing from outside the site."""

import re
from pathlib import Path

import pytest

from valuation.site_build import CONTENT_SECURITY_POLICY, DISCLAIMER, build_site
from valuation.site_check import (
    REFERRER_POLICY,
    page_problems,
    policy_problems,
    site_problems,
    stylesheet_problems,
)
from valuation.site_frame import BuildInfo

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="17 October 2026", commit="0123456789abcdef0123456789abcdef01234567")

POLICY_TAG = f'<meta http-equiv="Content-Security-Policy" content="{CONTENT_SECURITY_POLICY}">'
REFERRER_TAG = f'<meta name="referrer" content="{REFERRER_POLICY}">'
SCRIPT_TAG = '<script src="static/site.js"></script>'
GOOD_PAGE = f"""<!doctype html>
<html lang="en-AU"><head>
<meta charset="utf-8">
{POLICY_TAG}
{REFERRER_TAG}
<link rel="stylesheet" href="static/tokens.css">
{SCRIPT_TAG}
</head><body>
<a href="https://www.asx.com.au/">ASX</a>
<a href="#main">Skip</a>
<p>{DISCLAIMER}</p>
</body></html>
"""


@pytest.fixture(scope="module")
def site_dir() -> Path:
    out_dir = ROOT / "build" / "site_test"
    build_site(ROOT, out_dir, BUILD)
    return out_dir


def test_the_site_builds_and_has_no_problems(site_dir: Path) -> None:
    assert site_problems(site_dir, DISCLAIMER) == []


def test_the_build_copies_the_tokens_and_the_font_and_leaves_out_the_font_source(
    site_dir: Path,
) -> None:
    assert (site_dir / "static" / "tokens.css").is_file()
    assert (site_dir / "static" / "fonts" / "AtkinsonHyperlegibleNext-subset.woff2").is_file()
    assert not (site_dir / "font-source").exists()


def test_the_disclaimer_is_the_sentence_in_the_readme() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert DISCLAIMER in " ".join(readme.split())


def test_every_page_links_the_tokens_file_and_holds_no_colour(site_dir: Path) -> None:
    html = (site_dir / "index.html").read_text(encoding="utf-8")
    assert 'href="static/tokens.css"' in html
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", html.replace('href="#main"', ""))


def test_the_policy_allows_this_site_only() -> None:
    assert policy_problems(CONTENT_SECURITY_POLICY) == []
    assert "script-src 'self'" in CONTENT_SECURITY_POLICY
    assert "'unsafe-inline'" not in CONTENT_SECURITY_POLICY


def test_a_page_with_the_tags_and_outbound_links_passes() -> None:
    assert page_problems(GOOD_PAGE, DISCLAIMER) == []


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        (SCRIPT_TAG, "<script>alert(1)</script>", "inline script"),
        (SCRIPT_TAG, "<SCRIPT>alert(1)</SCRIPT>", "inline script"),
        (SCRIPT_TAG, '<script src="https://cdn.example.com/x.js"></script>', "https:"),
        (SCRIPT_TAG, '<script src="//cdn.example.com/x.js"></script>', "protocol-relative"),
        (SCRIPT_TAG, '<script src="/static/site.js"></script>', "root-absolute"),
        ("<p>", '<a href="/valuation.html">x</a><p>', "root-absolute"),
        (SCRIPT_TAG, '<script src="\\\\cdn.example.com/x.js"></script>', "backslash"),
        (SCRIPT_TAG, '<script src="/\\cdn.example.com/x.js"></script>', "backslash"),
        (SCRIPT_TAG, '<script src="ht\ttps://cdn.example.com/x.js"></script>', "control"),
        (SCRIPT_TAG, '<script src="HTTPS://cdn.example.com/x.js"></script>', "https:"),
        (
            '<link rel="stylesheet" href="static/tokens.css">',
            '<link rel="stylesheet" href="https://fonts.example.com/a.css">',
            "<link href> uses the scheme https:",
        ),
        (
            '<link rel="stylesheet" href="static/tokens.css">',
            '<link rel="preload" as="image" href="a.png" '
            'imagesrcset="a.png, https://x.example/c.png 2x">',
            "imagesrcset",
        ),
        ("<p>", '<img src="a.png" srcset="b.png 1x, https://x.example/c.png 2x"><p>', "srcset"),
        ("<p>", '<img src="http://tracker.example.com/p.gif"><p>', "http:"),
        ("<p>", '<input type="image" src="https://x.example/b.png"><p>', "https:"),
        ("<p>", '<body background="https://x.example/b.png"><p>', "background"),
        ("<p>", '<a href="javascript:alert(1)">x</a><p>', "javascript:"),
        ("<p>", '<a href="JavaScript:alert(1)">x</a><p>', "javascript:"),
        ("<p>", '<a href="data:text/html,x">x</a><p>', "data:"),
        ("<p>", '<area href="javascript:alert(1)"><p>', "javascript:"),
        ("<p>", '<button formaction="javascript:alert(1)">x</button><p>', "formaction"),
        ("<p>", '<iframe src="https://example.com/"></iframe><p>', "<iframe> is not an element"),
        ("<p>", '<iframe srcdoc="<script>alert(1)</script>"></iframe><p>', "srcdoc"),
        ("<p>", '<base href="https://example.com/"><p>', "<base> is not an element"),
        ("<p>", '<object data="a.swf"></object><p>', "<object> is not an element"),
        ("<p>", "<style>p { margin: 0 }</style><p>", "<style> is not an element"),
        ("<p>", '<p style="margin: 0">', "style attribute"),
        ("<p>", '<P STYLE="margin: 0">', "style attribute"),
        ("<p>", '<p onclick="go()">', "event handler onclick"),
        ("<p>", '<meta http-equiv="refresh" content="0; url=https://example.com/"><p>', "refresh"),
        (f"{POLICY_TAG}\n", "", "expected one policy meta tag, found 0"),
        (f"{REFERRER_TAG}\n", "", "expected one referrer meta"),
        (REFERRER_TAG, '<meta name="referrer" content="unsafe-url">', "referrer policy is"),
        (DISCLAIMER, "A different sentence.", "disclaimer sentence is missing"),
    ],
)
def test_a_planted_problem_is_reported(old: str, new: str, message: str) -> None:
    assert old in GOOD_PAGE
    problems = page_problems(GOOD_PAGE.replace(old, new, 1), DISCLAIMER)
    assert any(message in problem for problem in problems), problems


@pytest.mark.parametrize(
    ("snippet", "message"),
    [
        ('<script src="https://x.example/x.js" src="a.js"></script>', "repeats the attribute src"),
        ('<img src="https://x.example/x.png" src="a.png">', "repeats the attribute src"),
        ("<p class=a class=b>", "repeats the attribute class"),
        ("<!--> <script>alert(1)</script> -->", "HTML comment"),
        ("<!---> <script>alert(1)</script> -->", "HTML comment"),
        ("<!-- x --!> <script>alert(1)</script> -->", "HTML comment"),
        ("<!-- a note -->", "HTML comment"),
        ("<![if IE]><p>x<![endif]>", "marked section"),
        ("<!ENTITY x 'y'>", "HTML comment"),
        ("<?php echo 1 ?>", "processing instruction"),
        ('<script src="a.js">alert(1)</script>', "script element has content"),
        ('<svg><a href="#"><animate attributeName="href" values="x"/></a></svg>', "<animate>"),
        ('<svg><set attributeName="href" to="x"/></svg>', "<set>"),
        ("<marquee>x</marquee>", "<marquee> is not an element"),
        ('<svg><rect fill="url(https://x.example/x.svg#p)"/></svg>', "uses the scheme https:"),
        ('<svg><rect filter="url(//x.example/x.svg#f)"/></svg>', "protocol-relative"),
        ('<svg><g clip-path="url( HTTPS://x.example/x.svg#c )"></g></svg>', "uses the scheme"),
        ('<svg><rect mask="url(\\x.example/m)"/></svg>', "backslash"),
        ('<a href="https://www.asx.com.au/" referrerpolicy="unsafe-url">x</a>', "referrerpolicy"),
        ("<p>x</p><a referrerpolicy=origin>x</a>", "referrerpolicy"),
        ("<form action='a'></form>", "<form> is not an element"),
    ],
)
def test_a_construct_a_parser_and_a_browser_could_read_differently_is_reported(
    snippet: str, message: str
) -> None:
    page = GOOD_PAGE.replace("<p>", f"{snippet}<p>", 1)
    problems = page_problems(page, DISCLAIMER)
    assert any(message in problem for problem in problems), problems


@pytest.mark.parametrize(
    "ending",
    [
        "<!--> <script>alert(1)</script>",
        "<!---> <img src=x onerror=alert(1)>",
        "<!-- x --!> <script>alert(1)</script>",
    ],
)
def test_an_unfinished_comment_at_the_end_of_a_page_is_still_read(ending: str) -> None:
    page = GOOD_PAGE.replace("</body></html>\n", ending, 1)
    assert ending in page
    problems = page_problems(page, DISCLAIMER)
    assert any(
        word in problem for problem in problems for word in ("inline script", "onerror", "content")
    ), problems


@pytest.mark.parametrize(
    "ending",
    [
        '<script src="static/a.js"></script foo><img src=x onerror=alert(1)>',
        '<script src="static/a.js"></script/><img src=x onerror=alert(1)>',
        "</SCRIPT x><img src=x onerror=alert(1)>",
    ],
)
def test_a_script_end_tag_with_extra_characters_is_reported(ending: str) -> None:
    page = GOOD_PAGE.replace("</body></html>\n", ending, 1)
    assert any("script end tag" in problem for problem in page_problems(page, DISCLAIMER))


def test_an_unclosed_title_that_swallows_the_policy_tag_is_reported() -> None:
    page = GOOD_PAGE.replace("<head>", "<head><title>x", 1)
    problems = page_problems(page, DISCLAIMER)
    assert any("inside <title>" in problem for problem in problems), problems
    assert any("ends inside <title>" in problem for problem in problems), problems


def test_a_closed_title_is_accepted() -> None:
    page = GOOD_PAGE.replace("<head>", "<head><title>Domain</title>", 1)
    assert page_problems(page, DISCLAIMER) == []


def test_a_fragment_url_in_an_svg_attribute_and_the_pages_own_policy_are_accepted() -> None:
    page = GOOD_PAGE.replace(
        "<p>",
        '<svg><rect fill="url(#hatch)" stroke="none"/></svg>'
        '<a referrerpolicy="no-referrer">x</a><p>',
        1,
    )
    assert page_problems(page, DISCLAIMER) == []


def test_a_second_content_attribute_on_the_policy_tag_is_reported() -> None:
    doubled = POLICY_TAG.replace('content="', 'content="script-src *" content="', 1)
    page = GOOD_PAGE.replace(POLICY_TAG, doubled, 1)
    assert any("repeats the attribute content" in p for p in page_problems(page, DISCLAIMER))


def test_a_policy_tag_in_the_body_is_reported() -> None:
    moved = GOOD_PAGE.replace(f"{POLICY_TAG}\n", "", 1).replace("<body>", f"<body>{POLICY_TAG}", 1)
    assert any("outside <head>" in problem for problem in page_problems(moved, DISCLAIMER))


def test_a_stylesheet_before_the_policy_tag_is_reported() -> None:
    reordered = GOOD_PAGE.replace(f"{POLICY_TAG}\n", "", 1).replace(
        "</head>", f"{POLICY_TAG}</head>", 1
    )
    problems = page_problems(reordered, DISCLAIMER)
    assert any("comes before the policy tag" in problem for problem in problems)


@pytest.mark.parametrize(
    "policy",
    [
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self'; img-src 'self'; "
        "font-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'",
        "default-src 'none'; script-src https://cdn.example.com; style-src 'self'; img-src 'self'; "
        "font-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'",
        "default-src 'none'; style-src 'self'; img-src 'self'; font-src 'self'; "
        "connect-src 'self'; base-uri 'none'; form-action 'none'",
        "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
        "font-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'",
        "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
        "font-src 'self'; connect-src 'self'; base-uri 'none'",
        "default-src 'none'; script-src https://evil.example; script-src 'self'; style-src 'self'; "
        "img-src 'self'; font-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'",
    ],
)
def test_a_weaker_policy_is_reported(policy: str) -> None:
    assert policy_problems(policy)


@pytest.mark.parametrize(
    "css",
    [
        '@import url("other.css");',
        "a { background: url(https://example.com/a.png); }",
        "a { background: url('//example.com/a.png'); }",
        "a { background: url( HTTPS://example.com/a.png ); }",
        'a { background: image-set("https://example.com/a.png" 1x); }',
        "a { background: url(\\68ttps://example.com/a.png); }",
        "a { background: url(data:image/png;base64,AAAA); }",
        "a { background: url(/static/a.png); }",
        "a { background: u\\72l(https://example.com/a.png); }",
        "a { background: \\75rl(https://example.com/a.png); }",
        '@\\69mport "https://example.com/a.css";',
        'a{content:"/*"} b{background:url(https://example.com/a.png)} c{content:"*/"}',
    ],
)
def test_a_stylesheet_that_reaches_outside_the_site_is_reported(css: str) -> None:
    assert stylesheet_problems(css)


def test_a_local_font_is_accepted() -> None:
    css = '@font-face { src: url("fonts/a.woff2"); } a { fill: url(#shade); }'
    assert stylesheet_problems(css) == []


def test_a_comment_that_mentions_an_outside_url_is_reported_as_a_harmless_false_positive() -> None:
    # Comments are scanned with the rest of the text, because stripping them first can be fooled.
    assert stylesheet_problems("/* url(https://example.com/) */")


def test_a_planted_problem_in_a_built_file_is_reported_with_its_file(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text(GOOD_PAGE.replace("<p>", "<p onclick='x()'>", 1))
    (tmp_path / "bad.css").write_text("@import 'x.css';")
    problems = site_problems(tmp_path, DISCLAIMER)
    assert any(problem.startswith("index.html:") for problem in problems)
    assert any(problem.startswith("bad.css:") for problem in problems)


def test_an_empty_site_is_reported(tmp_path: Path) -> None:
    assert any("no pages" in problem for problem in site_problems(tmp_path, DISCLAIMER))


def test_the_build_refuses_to_replace_a_folder_outside_build(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="refusing to replace"):
        build_site(ROOT, tmp_path / "site", BUILD)

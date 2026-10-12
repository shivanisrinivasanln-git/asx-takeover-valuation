"""Checks on a built site: security tags, and no inline code or third-party request (task P5-03).

GitHub Pages cannot send response headers, so the policy is a meta tag in every page. The checks
read the files that were built, not the templates, so they see what a visitor's browser sees.

The rule for anything a page loads is an allow-list: the address must be a plain relative path on
this site. A link a visitor follows (`<a href>`) may also be an absolute http or https address,
because following it loads nothing into the page, and may not use any other scheme (a
`javascript:` address runs code when it is clicked).
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

REFERRER_POLICY = "no-referrer"
ALLOWED_POLICY_VALUES = ("'self'", "'none'")
REQUIRED_DIRECTIVES = (
    "default-src",
    "script-src",
    "style-src",
    "img-src",
    "font-src",
    "connect-src",
    "base-uri",
    "form-action",
)
# Attributes that make the browser fetch an address, whatever the tag.
LOADING_ATTRIBUTES = (
    "src",
    "srcset",
    "imagesrcset",
    "data",
    "poster",
    "background",
    "action",
    "formaction",
    "xlink:href",
    "manifest",
    "codebase",
    "ping",
)
SRCSET_ATTRIBUTES = ("srcset", "imagesrcset")
# The elements my templates use. Anything else fails, so there is no list of bad elements to keep
# complete: frames, embeds, forms, `<base>` and SVG animation (which can set an address after
# the checks) are out because they are not here. A template that needs another element adds it.
ALLOWED_TAGS = frozenset(
    {
        # document and sections
        "html",
        "head",
        "meta",
        "title",
        "link",
        "script",
        "body",
        "header",
        "footer",
        "main",
        "nav",
        "section",
        "article",
        "aside",
        "div",
        "span",
        # text
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "p",
        "a",
        "strong",
        "em",
        "small",
        "sub",
        "sup",
        "abbr",
        "code",
        "time",
        "br",
        "ul",
        "ol",
        "li",
        "dl",
        "dt",
        "dd",
        "figure",
        "figcaption",
        "details",
        "summary",
        # tables
        "table",
        "caption",
        "colgroup",
        "col",
        "thead",
        "tbody",
        "tfoot",
        "tr",
        "th",
        "td",
        # controls (the Show sources switch and the DCF controls; no <form>)
        "button",
        "label",
        "input",
        # SVG charts, drawn statically
        "svg",
        "g",
        "defs",
        "pattern",
        "rect",
        "line",
        "path",
        "circle",
        "text",
        "tspan",
        "desc",
        "use",
    }
)
FORBIDDEN_ATTRIBUTES = ("srcdoc",)
NAVIGATION_TAGS = ("a", "area")

SCHEME = re.compile(r"[a-z][a-z0-9+.-]*:", re.IGNORECASE)
# What a browser strips or rewrites in an address before reading its scheme and host.
CONTROL_OR_BACKSLASH = re.compile(r"[\x00-\x20\x7f\\]")
# A script end tag with anything before the closing bracket ends the script in a browser, and
# a parser that wants the exact tag stays in script mode and never delivers what follows.
ODD_SCRIPT_END = re.compile(r"</script(?!>)", re.IGNORECASE)
CSS_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE | re.DOTALL)
CSS_OTHER_FETCHERS = re.compile(r"@import|image-set\(|image\(|cross-fade\(|element\(|src\(", re.I)


def _address_problem(address: str, *, may_leave_site: bool) -> str | None:
    """Why an address is not allowed, or None.

    A loaded address must be a relative path. A followed link may also be http or https.
    """
    value = address.strip()
    if CONTROL_OR_BACKSLASH.search(value) or CONTROL_OR_BACKSLASH.search(address):
        return "has a backslash, space or control character"
    if value.startswith("//"):
        return "is protocol-relative"
    if value.startswith("/"):
        return "is root-absolute, which would miss the project path on GitHub Pages"
    match = SCHEME.match(value)
    if match is None:
        return None
    scheme = match.group(0).lower()
    if may_leave_site and scheme in ("http:", "https:"):
        return None
    return f"uses the scheme {scheme}"


def _candidates(attribute: str, value: str) -> list[str]:
    """The addresses in an attribute value: a srcset holds several, separated by commas."""
    if attribute not in SRCSET_ATTRIBUTES:
        return [value]
    return [part.split()[0] for part in value.split(",") if part.split()]


def policy_problems(policy: str) -> list[str]:
    """Problems with a Content-Security-Policy value: every directive allows this site only."""
    directives: dict[str, list[str]] = {}
    problems: list[str] = []
    for part in policy.split(";"):
        words = part.split()
        if not words:
            continue
        if words[0] in directives:
            problems.append(f"policy repeats {words[0]}, and a browser uses only the first")
        else:
            directives[words[0]] = words[1:]
    problems += [
        f"policy has no {name} directive" for name in REQUIRED_DIRECTIVES if name not in directives
    ]
    for name, values in directives.items():
        problems += [
            f"policy {name} allows {value}, only 'self' and 'none' are allowed"
            for value in values
            if value not in ALLOWED_POLICY_VALUES
        ]
    if directives.get("script-src") not in (["'self'"], ["'none'"]):
        problems.append("policy script-src must be 'self' or 'none'")
    return problems


class _PageReader(HTMLParser):
    """Collects what a page loads and what could run code or bring content in from outside."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.problems: list[str] = []
        self.policies: list[str] = []
        self.referrers: list[str] = []
        self.text: list[str] = []
        self._in_head = False
        self._head_closed = False
        self._in_script = False
        self._in_title = False

    def _problem(self, message: str) -> None:
        self.problems.append(f"line {self.getpos()[0]}: {message}")

    def _check_address(self, tag: str, attribute: str, value: str, *, may_leave_site: bool) -> None:
        for address in _candidates(attribute, value):
            reason = _address_problem(address, may_leave_site=may_leave_site)
            if reason is not None:
                self._problem(f"<{tag} {attribute}> {reason}: {address.strip()[:60]}")

    def _check_functional_urls(self, tag: str, attribute: str, value: str) -> None:
        """An SVG attribute such as fill, filter or mask can hold url(...)."""
        if "url(" not in value.lower():
            return
        found = CSS_URL.findall(value)
        if value.lower().count("url(") != len(found):
            self._problem(f"<{tag} {attribute}> has a url( that could not be read")
        for _, address in found:
            reason = _address_problem(address, may_leave_site=False)
            if reason is not None:
                self._problem(f"<{tag} {attribute}> url() {reason}: {address.strip()[:60]}")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "head":
            self._in_head = False
            self._head_closed = True
        if tag.lower() == "script":
            self._in_script = False
        if tag.lower() == "title":
            self._in_title = False

    # A parser and a browser can disagree about where a comment or a declaration ends, so a
    # built page holds none. Jinja comments are not written to the output.
    def handle_comment(self, data: str) -> None:
        self._problem("HTML comment")

    def handle_decl(self, decl: str) -> None:
        if decl.strip().lower() != "doctype html":
            self._problem(f"declaration <!{decl.strip()[:40]}>")

    def handle_pi(self, data: str) -> None:
        self._problem("processing instruction")

    def unknown_decl(self, data: str) -> None:
        self._problem("marked section or conditional comment")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        names = [name.lower() for name, _ in attrs]
        for name in sorted({name for name in names if names.count(name) > 1}):
            # A browser uses the first of two equal attributes; a parser may keep the last.
            self._problem(f"<{tag}> repeats the attribute {name}")
        values = {name.lower(): value or "" for name, value in attrs}
        if self._in_title:
            # A browser reads everything up to </title> as text, so this element would not exist.
            self._problem(f"<{tag}> inside <title>, which a browser reads as text")
        if tag == "script":
            self._in_script = True
        if tag == "title":
            self._in_title = True
        if tag == "head":
            self._in_head = True
        if tag == "body":
            self._head_closed = True
        if tag not in ALLOWED_TAGS:
            self._problem(f"<{tag}> is not an element the site uses")
        if tag == "script" and "src" not in values:
            self._problem("inline script")
        if tag == "style":
            self._problem("<style> element")
        if "style" in values:
            self._problem(f"style attribute on <{tag}>")
        for name in values:
            if name.startswith("on"):
                self._problem(f"event handler {name} on <{tag}>")
            if name in FORBIDDEN_ATTRIBUTES:
                self._problem(f"{name} attribute on <{tag}>")
        for name in LOADING_ATTRIBUTES:
            if name in values:
                self._check_address(tag, name, values[name], may_leave_site=False)
        for name, value in values.items():
            self._check_functional_urls(tag, name, value)
        if values.get("referrerpolicy", REFERRER_POLICY).strip().lower() != REFERRER_POLICY:
            self._problem(f"<{tag}> sets its own referrerpolicy {values['referrerpolicy']}")
        if "href" in values:
            followed = tag in NAVIGATION_TAGS
            self._check_address(tag, "href", values["href"], may_leave_site=followed)
        if tag == "meta":
            self._read_meta(values)
        elif self.policies == [] and (tag in ("script", "link") or "src" in values):
            self._problem(f"<{tag}> comes before the policy tag")

    def _read_meta(self, values: dict[str, str]) -> None:
        kind = values.get("http-equiv", "").lower()
        inside_head = self._in_head and not self._head_closed
        if kind == "content-security-policy":
            if not inside_head:
                self._problem("policy tag is outside <head>, where a browser ignores it")
            self.policies.append(values.get("content", ""))
        if kind == "refresh":
            self._problem("meta refresh")
        if values.get("name", "").lower() == "referrer":
            if not inside_head:
                self._problem("referrer tag is outside <head>")
            self.referrers.append(values.get("content", ""))

    def handle_data(self, data: str) -> None:
        if self._in_script and data.strip():
            self._problem("script element has content")
        self.text.append(data)


def page_problems(html: str, disclaimer: str) -> list[str]:
    """Problems in one built page."""
    reader = _PageReader()
    reader.feed(html)
    # Close the parser so that an unfinished construct at the end is read, not dropped.
    reader.close()
    if reader.cdata_elem is not None or ODD_SCRIPT_END.search(html):
        reader.problems.append(
            "script end tag is not exactly </script>, or the page ends in a script"
        )
    if reader._in_title:
        reader.problems.append("page ends inside <title>")
    problems = list(reader.problems)
    if len(reader.policies) != 1:
        problems.append(f"expected one policy meta tag, found {len(reader.policies)}")
    else:
        problems += policy_problems(reader.policies[0])
    if len(reader.referrers) != 1:
        problems.append(f"expected one referrer meta tag, found {len(reader.referrers)}")
    elif reader.referrers[0].strip().lower() != REFERRER_POLICY:
        problems.append(f"referrer policy is {reader.referrers[0]}, expected {REFERRER_POLICY}")
    # The disclaimer is one sentence; page text can break it across lines in the source.
    if disclaimer not in " ".join("".join(reader.text).split()):
        problems.append("disclaimer sentence is missing")
    return problems


def stylesheet_problems(css: str) -> list[str]:
    """A stylesheet may fetch only relative paths on this site, with no escapes or data URIs.

    The raw text is scanned, comments included: a comment that mentions url( is a harmless false
    positive, and stripping comments first can be fooled by a string that holds a comment opener.
    """
    problems: list[str] = []
    if "\\" in css:
        problems.append("stylesheet has a backslash, which can spell url( or @import")
    problems += [f"stylesheet uses {match.group(0)}" for match in CSS_OTHER_FETCHERS.finditer(css)]
    for match in CSS_URL.finditer(css):
        reason = _address_problem(match.group(2), may_leave_site=False)
        if reason is not None:
            problems.append(f"stylesheet url() {reason}: {match.group(2).strip()[:60]}")
    # A url( that the pattern above could not read as a whole is not accepted either.
    if css.lower().count("url(") != len(CSS_URL.findall(css)):
        problems.append("stylesheet has a url( that could not be read")
    return problems


def site_problems(site_dir: Path, disclaimer: str) -> list[str]:
    """Every problem in the built site, prefixed with the file it is in."""
    problems: list[str] = []
    pages = sorted(site_dir.rglob("*.html"))
    if not pages:
        problems.append(f"{site_dir}: no pages were built")
    for page in pages:
        problems += [
            f"{page.relative_to(site_dir)}: {problem}"
            for problem in page_problems(page.read_text(encoding="utf-8"), disclaimer)
        ]
    for sheet in sorted(site_dir.rglob("*.css")):
        problems += [
            f"{sheet.relative_to(site_dir)}: {problem}"
            for problem in stylesheet_problems(sheet.read_text(encoding="utf-8"))
        ]
    return problems

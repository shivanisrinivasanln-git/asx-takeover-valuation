"""Build the static site into `build/site` from the templates and `valuation.json` (task P5-03).

Usage, from the repository root: PYTHONPATH=src python -m valuation.site_build

Every page is rendered here, so the numbers are in the HTML before any script runs. The pages
load only files from the site itself, which lets the policy in each page's meta tag allow
scripts and everything else from the site only.
"""

from __future__ import annotations

import re
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from valuation.bridge_page import build_bridge_page
from valuation.football_field import build_football_field
from valuation.inputs import Inputs, load_inputs
from valuation.landing import build_landing
from valuation.method_page import build_method_page
from valuation.output import build_valuation
from valuation.site_check import REFERRER_POLICY, site_problems
from valuation.site_consistency import consistency_problems
from valuation.site_frame import BuildInfo, build_frame, current_commit
from valuation.timeline_page import build_timeline_page, implementation_date, load_timeline
from valuation.valuation_page import build_valuation_page

# The sentence under every page and in the README (checked against the README by a test).
DISCLAIMER = (
    "This is an educational case study, not financial advice, "
    "and it is not affiliated with any party to the deal."
)

# GitHub Pages cannot send headers, so the policy travels in a meta tag. Everything is allowed
# from this site only and nothing inline: pages carry no inline script or style.
CONTENT_SECURITY_POLICY = "; ".join(
    [
        "default-src 'none'",
        "script-src 'self'",
        "style-src 'self'",
        "img-src 'self'",
        "font-src 'self'",
        "connect-src 'self'",
        "base-uri 'none'",
        "form-action 'none'",
    ]
)

# The title of the landing page.
SITE_NAME = "Shadow valuation of the Domain takeover"

PAGES = {
    "index.html": "index.html.j2",
    "valuation.html": "valuation.html.j2",
    "gap.html": "gap.html.j2",
    "method.html": "method.html.j2",
    "timeline.html": "timeline.html.j2",
}
NAVIGATION = (
    ("index.html", "Football field"),
    ("valuation.html", "Valuation tables"),
    ("gap.html", "Gap bridge"),
    ("method.html", "Method and sources"),
    ("timeline.html", "Deal timeline"),
)


# The Excel model and the PDF report are served beside the pages, under these names. The report
# is the file scripts/build_report.py writes (report_build.py imports this module, so the path is
# written out here and a test compares the two).
MODEL_SOURCE = Path("model") / "domain_valuation_model.xlsx"
REPORT_SOURCE = Path("build") / "report" / "report.pdf"
MODEL_HREF = "downloads/domain_valuation_model.xlsx"
REPORT_HREF = "downloads/domain_valuation_report.pdf"

ACCENT_TOKEN = re.compile(r"--accent:\s*(#[0-9a-fA-F]{6})\s*;")
LINK_ATTRIBUTE = re.compile(r'\s(?:href|src)="([^"]*)"')
ELEMENT_ID = re.compile(r'\sid="([^"]*)"')
FAVICON_SIZE_PX = 16


def favicon_svg(root: Path) -> str:
    """A plain square in the accent colour, written from the colour in tokens.css so that the
    hex value stays in that one file."""
    tokens = (root / "site" / "static" / "tokens.css").read_text(encoding="utf-8")
    match = ACCENT_TOKEN.search(tokens)
    if match is None:
        raise ValueError("tokens.css has no --accent colour to draw the favicon from")
    size = FAVICON_SIZE_PX
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">'
        f'<rect width="{size}" height="{size}" fill="{match.group(1)}"/></svg>\n'
    )


def render_pages(
    root: Path, valuation: dict[str, Any], inputs: Inputs, build: BuildInfo
) -> dict[str, str]:
    """The HTML of every page, by output file name."""
    environment = Environment(
        loader=FileSystemLoader(root / "site" / "templates"),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    timeline = load_timeline(root)
    field = build_football_field(valuation, inputs)
    context = {
        "pages": NAVIGATION,
        "site_name": SITE_NAME,
        "landing": build_landing(valuation, field, MODEL_HREF, REPORT_HREF),
        "frame": build_frame(valuation, build, implementation_date(timeline)),
        "timeline": build_timeline_page(timeline),
        "meta": valuation["meta"],
        "field": field,
        "bridge": build_bridge_page(valuation, inputs),
        "method": build_method_page(valuation, inputs),
        "page": build_valuation_page(valuation, inputs),
        "disclaimer": DISCLAIMER,
        "content_security_policy": CONTENT_SECURITY_POLICY,
        # Outbound links to ASX documents do not say which page sent the visitor.
        "referrer_policy": REFERRER_POLICY,
    }
    # Pages that print sourced figures list their sources and load the script that opens them.
    page_sources = {
        "index.html": context["field"].sources,
        "valuation.html": context["page"]["sources"],
        "gap.html": context["bridge"]["sources"],
    }
    return {
        name: environment.get_template(template).render(
            current=name, sources=page_sources.get(name, ()), **context
        )
        for name, template in PAGES.items()
    }


def build_site(root: Path, out_dir: Path, build: BuildInfo) -> list[Path]:
    """Write the site to `out_dir`, replacing what was there, and return the files written."""
    build_root = (root / "build").resolve()
    if build_root not in out_dir.resolve().parents:
        raise ValueError(f"{out_dir} is not inside {build_root}; refusing to replace it")
    inputs = load_inputs(root)
    pages = render_pages(root, build_valuation(inputs), inputs, build)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    shutil.copytree(root / "site" / "static", out_dir / "static")
    favicon = out_dir / "static" / "favicon.svg"
    favicon.write_text(favicon_svg(root), encoding="utf-8", newline="\n")
    for name, html in pages.items():
        (out_dir / name).write_text(html, encoding="utf-8", newline="\n")
    return sorted(path for path in out_dir.rglob("*") if path.is_file())


def copy_downloads(model: Path, report: Path, out_dir: Path) -> None:
    """Put the Excel model and the PDF report where the pages link to them.

    The report is a build output (scripts/build_report.py), so it must be built first; a missing
    file raises here rather than leaving a link that goes nowhere.
    """
    for source, href in ((model, MODEL_HREF), (report, REPORT_HREF)):
        if not source.is_file():
            raise FileNotFoundError(f"{source} does not exist; build it before the site")
        target = out_dir / href
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def broken_links(out_dir: Path) -> list[str]:
    """Links that point at a file the site lacks or at an element id the target page lacks.

    Only addresses inside the site are followed; an address with a scheme leaves the site. A link
    that starts with # names a place on its own page.
    """
    pages = {path.relative_to(out_dir).as_posix(): path for path in out_dir.rglob("*.html")}
    ids = {
        name: set(ELEMENT_ID.findall(path.read_text(encoding="utf-8")))
        for name, path in pages.items()
    }
    problems: list[str] = []
    for name, path in sorted(pages.items()):
        for address in LINK_ATTRIBUTE.findall(path.read_text(encoding="utf-8")):
            if ":" in address:
                continue
            target, _, fragment = address.partition("#")
            resolved = (path.parent / target).resolve() if target else path.resolve()
            if not resolved.is_file():
                problems.append(f"{name}: {address} points at a file that is not in the site")
                continue
            target_name = resolved.relative_to(out_dir.resolve()).as_posix()
            if fragment and fragment not in ids.get(target_name, set()):
                problems.append(f"{name}: {address} points at an id that {target_name} lacks")
    return problems


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    out_dir = root / "build" / "site"
    build = BuildInfo(date=f"{date.today().day} {date.today():%B %Y}", commit=current_commit(root))
    build_site(root, out_dir, build)
    copy_downloads(root / MODEL_SOURCE, root / REPORT_SOURCE, out_dir)
    files = sorted(path for path in out_dir.rglob("*") if path.is_file())
    inputs = load_inputs(root)
    problems = (
        site_problems(out_dir, DISCLAIMER)
        + consistency_problems(
            root, out_dir, build_valuation(inputs), inputs, build, load_timeline(root)
        )
        + broken_links(out_dir)
    )
    if problems:
        sys.stdout.write("site: FAIL\n" + "\n".join(problems) + "\n")
        return 1
    sys.stdout.write(f"site: wrote {len(files)} files to {out_dir.relative_to(root)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

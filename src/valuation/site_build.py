"""Build the static site into `build/site` from the templates and `valuation.json` (task P5-03).

Usage, from the repository root: PYTHONPATH=src python -m valuation.site_build

Every page is rendered here, so the numbers are in the HTML before any script runs. The pages
load only files from the site itself, which lets the policy in each page's meta tag allow
scripts and everything else from the site only.
"""

from __future__ import annotations

import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from valuation.bridge_page import build_bridge_page
from valuation.football_field import build_football_field
from valuation.inputs import Inputs, load_inputs
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
    context = {
        "pages": NAVIGATION,
        "frame": build_frame(valuation, build, implementation_date(timeline)),
        "timeline": build_timeline_page(timeline),
        "meta": valuation["meta"],
        "field": build_football_field(valuation, inputs),
        "bridge": build_bridge_page(valuation, inputs),
        "method": build_method_page(inputs),
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
    for name, html in pages.items():
        (out_dir / name).write_text(html, encoding="utf-8", newline="\n")
    return sorted(path for path in out_dir.rglob("*") if path.is_file())


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    out_dir = root / "build" / "site"
    build = BuildInfo(date=f"{date.today().day} {date.today():%B %Y}", commit=current_commit(root))
    files = build_site(root, out_dir, build)
    inputs = load_inputs(root)
    problems = site_problems(out_dir, DISCLAIMER) + consistency_problems(
        root, out_dir, build_valuation(inputs), inputs, build, load_timeline(root)
    )
    if problems:
        sys.stdout.write("site: FAIL\n" + "\n".join(problems) + "\n")
        return 1
    sys.stdout.write(f"site: wrote {len(files)} files to {out_dir.relative_to(root)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

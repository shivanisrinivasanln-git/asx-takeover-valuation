"""What every page shares: the deal docket under the title and the colophon in the footer.

All dates and amounts come from `valuation.json`, the inputs or the timeline, so a page cannot
disagree with them (task P5-21).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from valuation.site_format import aud

REPOSITORY_URL = "https://github.com/shivanisrinivasanln-git/asx-takeover-valuation"
# The bidder named in the scheme booklet and in the deal timeline (rows of 27 March 2025).
ACQUIRER = "CoStar Group"
UNIT_NOTE = "Money is in A$ millions unless a header says per share. Per-share values are in A$."
COMMIT_LENGTH = 40


@dataclass(frozen=True)
class BuildInfo:
    """When the site was built and from which commit, for the footer."""

    date: str
    commit: str


def current_commit(root: Path) -> str:
    """The commit that HEAD points at, read from the git folder.

    Reading the files avoids running a program, and works for a checked-out branch and for the
    detached head that a CI checkout leaves.
    """
    git_dir = root / ".git"
    head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
    if not head.startswith("ref: "):
        return head
    ref = head.removeprefix("ref: ")
    loose = git_dir / ref
    if loose.is_file():
        return loose.read_text(encoding="utf-8").strip()
    for line in (git_dir / "packed-refs").read_text(encoding="utf-8").splitlines():
        if line.endswith(f" {ref}"):
            return line.split()[0]
    raise ValueError(f"{ref} is not in {git_dir}")


def build_frame(valuation: dict[str, Any], build: BuildInfo, implemented_on: str) -> dict[str, Any]:
    """The docket and the colophon, as labelled items."""
    if len(build.commit) != COMMIT_LENGTH:
        raise ValueError(f"commit {build.commit!r} is not a full commit hash")
    meta = valuation["meta"]
    offer = valuation["values"]["offer_price_aud"]["value"]
    return {
        "docket": [
            ("Target", meta["target"]),
            ("Acquirer", ACQUIRER),
            ("Consideration", f"{aud(offer)} a share, paid as cash and a special dividend"),
            ("Implemented", implemented_on),
        ],
        "colophon": [
            ("Valuation date", meta["valuation_date"]),
            ("Market data as at", meta["data_date"]),
            ("Built", build.date),
        ],
        "commit_short": build.commit[:7],
        "commit_url": f"{REPOSITORY_URL}/commit/{build.commit}",
        "unit_note": UNIT_NOTE,
    }

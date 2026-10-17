"""Read a Lighthouse report and say which of the site's budgets it misses.

The budgets are DESIGN.md section 10: on mobile, performance 90 or more, accessibility 95 or more,
best practices 95 or more, and largest contentful paint under 2.5 s.
"""

from dataclasses import dataclass
from typing import Any

MINIMUM_SCORE_PCT = {"performance": 90, "accessibility": 95, "best-practices": 95}
MAXIMUM_LCP_MS = 2500


@dataclass(frozen=True)
class PageScores:
    page: str
    score_pct: dict[str, int]
    lcp_ms: float


def read_report(page: str, report: dict[str, Any]) -> PageScores:
    """Scores are 0 to 1 in the report; they are rounded to the whole percent Lighthouse shows."""
    if report["configSettings"]["formFactor"] != "mobile":
        raise ValueError(f"{page}: the report is not a mobile run")
    score_pct = {
        name: round(report["categories"][name]["score"] * 100) for name in MINIMUM_SCORE_PCT
    }
    lcp_ms = float(report["audits"]["largest-contentful-paint"]["numericValue"])
    return PageScores(page=page, score_pct=score_pct, lcp_ms=lcp_ms)


def budget_problems(scores: PageScores) -> list[str]:
    problems = [
        f"{scores.page}: {name} {scores.score_pct[name]} is under {minimum}"
        for name, minimum in MINIMUM_SCORE_PCT.items()
        if scores.score_pct[name] < minimum
    ]
    if scores.lcp_ms >= MAXIMUM_LCP_MS:
        problems.append(
            f"{scores.page}: largest contentful paint {scores.lcp_ms / 1000:.1f} s is not under "
            f"{MAXIMUM_LCP_MS / 1000:.1f} s"
        )
    return problems

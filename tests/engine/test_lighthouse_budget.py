"""The budget check reads a Lighthouse report and names each budget a page misses (task P5-17)."""

from typing import Any

import pytest

from valuation.lighthouse_budget import PageScores, budget_problems, read_report


def report(
    performance: float = 0.97,
    accessibility: float = 1.0,
    best_practices: float = 0.96,
    lcp_ms: float = 1400.0,
    form_factor: str = "mobile",
) -> dict[str, Any]:
    return {
        "configSettings": {"formFactor": form_factor},
        "categories": {
            "performance": {"score": performance},
            "accessibility": {"score": accessibility},
            "best-practices": {"score": best_practices},
        },
        "audits": {"largest-contentful-paint": {"numericValue": lcp_ms}},
    }


def test_a_report_inside_every_budget_has_no_problem() -> None:
    scores = read_report("index.html", report())
    assert scores.score_pct == {"performance": 97, "accessibility": 100, "best-practices": 96}
    assert scores.lcp_ms == 1400.0
    assert budget_problems(scores) == []


def test_scores_exactly_on_the_minimum_pass() -> None:
    scores = read_report("index.html", report(0.90, 0.95, 0.95, 2499.0))
    assert budget_problems(scores) == []


@pytest.mark.parametrize(
    ("category", "score", "message"),
    [
        ("performance", 0.89, "performance 89 is under 90"),
        ("accessibility", 0.94, "accessibility 94 is under 95"),
        ("best-practices", 0.92, "best-practices 92 is under 95"),
    ],
)
def test_a_score_under_its_minimum_is_reported_by_name(
    category: str, score: float, message: str
) -> None:
    data = report()
    data["categories"][category]["score"] = score
    assert budget_problems(read_report("gap.html", data)) == [f"gap.html: {message}"]


def test_a_largest_contentful_paint_of_2_5_seconds_fails() -> None:
    problems = budget_problems(read_report("gap.html", report(lcp_ms=2500.0)))
    assert problems == ["gap.html: largest contentful paint 2.5 s is not under 2.5 s"]


def test_several_misses_are_all_reported() -> None:
    scores = PageScores(
        "method.html", {"performance": 50, "accessibility": 100, "best-practices": 80}, 4000.0
    )
    assert len(budget_problems(scores)) == 3


def test_a_desktop_report_is_refused() -> None:
    with pytest.raises(ValueError, match="not a mobile run"):
        read_report("index.html", report(form_factor="desktop"))

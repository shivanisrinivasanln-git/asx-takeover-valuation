"""The landing page states the verdict in the chart's notation and offers three routes onward
(tasks P5-05 and P5-18). The sentence's claims are checked against the figures it prints."""

import copy
import re
from pathlib import Path
from typing import Any

import pytest

from valuation.football_field import FootballField, build_football_field
from valuation.inputs import load_inputs
from valuation.landing import build_landing, build_verdict, source_refs
from valuation.output import build_valuation
from valuation.site_build import MODEL_HREF, REPORT_HREF, build_site
from valuation.site_format import number
from valuation.site_frame import BuildInfo

ROOT = Path(__file__).resolve().parents[2]
BUILD = BuildInfo(date="18 October 2026", commit="0123456789abcdef0123456789abcdef01234567")
VERDICT_KEYS = {
    "my_low": "combined_value_per_share_aud_low",
    "my_high": "combined_value_per_share_aud_high",
    "my_preferred": "preferred_value_per_share_aud",
    "offer": "offer_price_aud",
    "expert_low": "expert_value_per_share_aud_low",
    "expert_high": "expert_value_per_share_aud_high",
}


@pytest.fixture(scope="module")
def valuation() -> dict[str, Any]:
    return build_valuation(load_inputs(ROOT))


@pytest.fixture(scope="module")
def field(valuation: dict[str, Any]) -> FootballField:
    return build_football_field(valuation, load_inputs(ROOT))


@pytest.fixture(scope="module")
def index_html() -> str:
    out_dir = ROOT / "build" / "site_landing_test"
    build_site(ROOT, out_dir, BUILD)
    return (out_dir / "index.html").read_text(encoding="utf-8")


def with_value(valuation: dict[str, Any], key: str, value: float) -> dict[str, Any]:
    changed = copy.deepcopy(valuation)
    changed["values"][key]["value"] = value
    return changed


def test_each_figure_of_the_verdict_is_its_value_in_valuation_json(
    valuation: dict[str, Any], field: FootballField
) -> None:
    verdict = build_verdict(valuation, source_refs(field))
    for name, key in VERDICT_KEYS.items():
        figure = getattr(verdict, name)
        assert figure.key == key
        assert figure.text == number(valuation["values"][key]["value"])


def test_the_page_prints_the_sentence_with_each_mark_of_the_chart_notation(
    index_html: str, valuation: dict[str, Any]
) -> None:
    sentence = re.search(r'<p class="verdict">(.*?)</p>', index_html, re.DOTALL)
    assert sentence
    text = re.sub(r"<[^>]+>", "", sentence.group(1))
    values = {key: number(valuation["values"][key]["value"]) for key in VERDICT_KEYS.values()}
    assert text == (
        f"My valuation range of A${values['combined_value_per_share_aud_low']}\u2013"
        f"{values['combined_value_per_share_aud_high']} a share includes CoStar's "
        f"A${values['offer_price_aud']} offer, which is above my preferred value of "
        f"A${values['preferred_value_per_share_aud']}. Grant Samuel's range was "
        f"A${values['expert_value_per_share_aud_low']}\u2013"
        f"{values['expert_value_per_share_aud_high']}."
    )
    for mark, keys in {
        "mark-mine": ("combined_value_per_share_aud_low", "combined_value_per_share_aud_high"),
        "mark-offer": ("offer_price_aud",),
        "mark-preferred": ("preferred_value_per_share_aud",),
        "mark-expert": ("expert_value_per_share_aud_low", "expert_value_per_share_aud_high"),
    }.items():
        span = re.search(rf'<span class="{mark}">(.*?)</span>(?=[ .])', sentence.group(1))
        assert span, mark
        assert re.findall(r'data-key="([^"]+)"', span.group(1)) == list(keys)


def test_an_offer_outside_my_range_stops_the_build(valuation: dict[str, Any]) -> None:
    with pytest.raises(ValueError, match="my range includes the offer"):
        build_verdict(with_value(valuation, "offer_price_aud", 4.80), {})


def test_an_offer_at_or_below_my_preferred_value_stops_the_build(
    valuation: dict[str, Any],
) -> None:
    preferred = valuation["values"]["preferred_value_per_share_aud"]["value"]
    with pytest.raises(ValueError, match="above my preferred value"):
        build_verdict(with_value(valuation, "offer_price_aud", round(preferred, 2)), {})


def test_the_comparison_uses_the_figures_as_printed(valuation: dict[str, Any]) -> None:
    # An offer of 4.214 prints as A$4.21, the same as my preferred value, so it is not above it.
    with pytest.raises(ValueError, match="above my preferred value"):
        build_verdict(with_value(valuation, "offer_price_aud", 4.214), {})


def test_unequal_weights_for_the_two_multiples_methods_stop_the_build(
    valuation: dict[str, Any], field: FootballField
) -> None:
    changed = with_value(valuation, "method_weight_trading_pct", 30.0)
    with pytest.raises(ValueError, match="one weight for both multiples methods"):
        build_landing(changed, field, MODEL_HREF, REPORT_HREF)


def test_the_offer_and_the_experts_range_carry_the_codes_of_the_chart_table(
    index_html: str, field: FootballField
) -> None:
    sentence = re.search(r'<p class="verdict">(.*?)</p>', index_html, re.DOTALL)
    assert sentence
    marked = dict(
        re.findall(
            r'data-key="([^"]+)"><a class="source-mark" href="#ref-[^"]+" data-ref="([^"]+)">',
            sentence.group(1),
        )
    )
    expert = next(row for row in field.rows if row.id == "expert")
    offer = next(price for price in field.reference_prices if price.key == "offer_price_aud")
    assert marked == {
        "offer_price_aud": offer.ref,
        expert.low_key: expert.low_ref,
        expert.high_key: expert.high_ref,
    }


def test_three_routes_lead_to_the_method_the_gap_and_the_downloads(index_html: str) -> None:
    routes = re.search(r'<nav class="routes"[^>]*>(.*?)</nav>', index_html, re.DOTALL)
    assert routes
    assert routes.group(1).count("<li>") == 3
    links = re.findall(r'href="([^"]+)"', routes.group(1))
    assert links == ["valuation.html", "gap.html", MODEL_HREF, REPORT_HREF]


def test_the_verdict_comes_before_the_chart(index_html: str) -> None:
    assert index_html.index('class="verdict"') < index_html.index('class="football-field"')

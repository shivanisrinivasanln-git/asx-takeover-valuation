"""The verdict sentence and the routes onward on the landing page (tasks P5-05 and P5-18).

The sentence says that my range includes the offer and that the offer is above my preferred
value. Both relations are checked here on the figures as the page prints them, so a change in the
inputs that made either untrue stops the build instead of publishing a false sentence. The
figures taken from a document carry the same source code as in the chart's table.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from valuation.football_field import FootballField
from valuation.site_format import number

PLACES = 2
EN_DASH = chr(0x2013)


@dataclass(frozen=True)
class Figure:
    """A value per share as the page prints it, with the key it comes from and, for a figure
    taken from a document, the code of its source."""

    key: str
    value: float
    text: str
    ref: str | None


@dataclass(frozen=True)
class Verdict:
    my_low: Figure
    my_high: Figure
    my_preferred: Figure
    offer: Figure
    expert_low: Figure
    expert_high: Figure

    def sentence(self) -> str:
        """The sentence as plain text, for the link preview, with the same words as the page."""
        return (
            f"My valuation range of A${self.my_low.text}{EN_DASH}{self.my_high.text} a share "
            f"includes CoStar's A${self.offer.text} offer, which is above my preferred value of "
            f"A${self.my_preferred.text}. Grant Samuel's range was "
            f"A${self.expert_low.text}{EN_DASH}{self.expert_high.text}."
        )


def source_refs(field: FootballField) -> dict[str, str]:
    """The source code of each sourced figure in the chart's tables, by its valuation.json key."""
    refs = {price.key: price.ref for price in field.reference_prices}
    for row in field.rows:
        if row.low_ref is not None:
            refs[row.low_key] = row.low_ref
        if row.high_ref is not None:
            refs[row.high_key] = row.high_ref
    return refs


def build_verdict(valuation: dict[str, Any], refs: dict[str, str]) -> Verdict:
    """The figures of the verdict sentence, after checking that the sentence is still true."""
    values = valuation["values"]

    def figure(key: str) -> Figure:
        value = float(values[key]["value"])
        return Figure(key, round(value, PLACES), number(value, PLACES), refs.get(key))

    verdict = Verdict(
        my_low=figure("combined_value_per_share_aud_low"),
        my_high=figure("combined_value_per_share_aud_high"),
        my_preferred=figure("preferred_value_per_share_aud"),
        offer=figure("offer_price_aud"),
        expert_low=figure("expert_value_per_share_aud_low"),
        expert_high=figure("expert_value_per_share_aud_high"),
    )
    if not verdict.my_low.value <= verdict.offer.value <= verdict.my_high.value:
        raise ValueError(
            f"the sentence says my range includes the offer, but A${verdict.offer.text} is outside "
            f"A${verdict.my_low.text} to A${verdict.my_high.text}"
        )
    if not verdict.offer.value > verdict.my_preferred.value:
        raise ValueError(
            f"the sentence says the offer is above my preferred value, but A${verdict.offer.text} "
            f"is not above A${verdict.my_preferred.text}"
        )
    return verdict


@dataclass(frozen=True)
class Landing:
    """What the landing page prints around the football field."""

    verdict: Verdict
    weight_dcf: str
    weight_multiples: str
    model_href: str
    report_href: str


def build_landing(
    valuation: dict[str, Any], field: FootballField, model_href: str, report_href: str
) -> Landing:
    """The verdict, the method weights the lead sentence states and the download addresses.

    The lead sentence gives one weight for both multiples methods, so the two must be equal.
    """
    values = valuation["values"]
    trading = values["method_weight_trading_pct"]["value"]
    precedent = values["method_weight_precedent_pct"]["value"]
    if trading != precedent:
        raise ValueError(
            f"the page gives one weight for both multiples methods, but trading is {trading}% "
            f"and precedents {precedent}%"
        )
    return Landing(
        verdict=build_verdict(valuation, source_refs(field)),
        weight_dcf=number(values["method_weight_dcf_pct"]["value"], 0),
        weight_multiples=number(trading, 0),
        model_href=model_href,
        report_href=report_href,
    )

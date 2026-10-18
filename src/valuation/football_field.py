"""Geometry and labels for the football field chart (tasks P5-04 and P5-04b).

The chart is an inline SVG with percentage x coordinates and no `viewBox`, so bars stretch with
the page while text and line widths keep their size. Python decides every position
and label; the template only writes them out. Rows come from `valuation.json` `football_field`
(each row names its low, high and preferred keys), and nothing here recalculates a value.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from valuation.inputs import Inputs
from valuation.provenance import PageSources, Reference, ReferenceBook
from valuation.site_format import aud, number

AXIS_STEP_AUD = 0.5
AXIS_MARGIN_AUD = 0.25
MAJOR_TICK_EVERY_AUD = 1.0

# Vertical layout in pixels. Text is set in CSS, so these only place it.
TOP_LABEL_BASELINE = 14
TOP_AXIS_BASELINE = 36
FIRST_ROW_TOP = 46
ROW_PITCH = 64
LABEL_BASELINE_IN_ROW = 16
BAR_TOP_IN_ROW = 26
BAR_HEIGHT = 16
TICK_OVERHANG = 4
BOTTOM_AXIS_GAP = 20
BOTTOM_LABEL_GAP = 42

# The labels the chart uses for each row. The long labels in valuation.json name the multiple
# used, which belongs in the data table and not on a phone-width row.
SHORT_LABELS = {
    "dcf": "Discounted cash flow",
    "trading": "Trading comparables",
    "precedent": "Precedent transactions",
    "combined": "My combined range",
    "expert": "Independent expert",
}


@dataclass(frozen=True)
class FieldRow:
    id: str
    label: str
    table_label: str
    owner: bool
    low_key: str
    high_key: str
    preferred_key: str | None
    low_aud: float
    high_aud: float
    preferred_aud: float | None
    x_low: str
    x_high: str
    x_preferred: str | None
    width: str
    top: int
    label_y: int
    bar_y: int
    bar_height: int
    tick_y1: int
    tick_y2: int
    mid_y: int
    low_text: str
    high_text: str
    preferred_text: str | None
    low_label_x: str
    high_label_x: str
    # Reference codes of the figures taken from the booklet: the expert's range only.
    low_ref: str | None = None
    high_ref: str | None = None


@dataclass(frozen=True)
class ReferencePrice:
    key: str
    label: str
    text: str
    ref: str


@dataclass(frozen=True)
class AxisTick:
    value_aud: float
    x: str
    label: str
    major: bool
    anchor: str


@dataclass(frozen=True)
class ReferenceLine:
    key: str
    x: str
    value_aud: float
    text: str
    date: str
    anchor: str


@dataclass(frozen=True)
class FootballField:
    axis_min_aud: float
    axis_max_aud: float
    height: int
    plot_top: int
    plot_bottom: int
    top_label_y: int
    top_axis_y: int
    bottom_axis_y: int
    bottom_label_y: int
    ticks: tuple[AxisTick, ...]
    rows: tuple[FieldRow, ...]
    offer: ReferenceLine
    undisturbed: ReferenceLine
    title: str
    description: str
    reference_prices: tuple[ReferencePrice, ...]
    sources: tuple[Reference, ...]


def _x(value: float, low: float, high: float) -> float:
    return (value - low) / (high - low) * 100


def _pct(value: float) -> str:
    return f"{value:.3f}%"


def _axis_bounds(values: list[float]) -> tuple[float, float]:
    low = math.floor((min(values) - AXIS_MARGIN_AUD) / AXIS_STEP_AUD) * AXIS_STEP_AUD
    high = math.ceil((max(values) + AXIS_MARGIN_AUD) / AXIS_STEP_AUD) * AXIS_STEP_AUD
    return low, high


def _ticks(low: float, high: float) -> tuple[AxisTick, ...]:
    count = round((high - low) / AXIS_STEP_AUD)
    ticks: list[AxisTick] = []
    for index in range(count + 1):
        value = low + index * AXIS_STEP_AUD
        anchor = "start" if index == 0 else "end" if index == count else "middle"
        major = math.isclose(value % MAJOR_TICK_EVERY_AUD, 0, abs_tol=1e-9) or math.isclose(
            value % MAJOR_TICK_EVERY_AUD, MAJOR_TICK_EVERY_AUD, abs_tol=1e-9
        )
        ticks.append(AxisTick(value, _pct(_x(value, low, high)), f"{value:.2f}", major, anchor))
    return tuple(ticks)


def build_football_field(valuation: dict[str, Any], inputs: Inputs) -> FootballField:
    """The chart's rows, axis and reference lines from `valuation.json`."""
    values = {key: item["value"] for key, item in valuation["values"].items()}
    sources = PageSources(ReferenceBook(inputs))
    rows_spec = valuation["football_field"]
    offer = values["offer_price_aud"]
    undisturbed = values["undisturbed_share_price_aud"]
    every_value = [offer, undisturbed]
    for spec in rows_spec:
        every_value += [values[spec["low_key"]], values[spec["high_key"]]]
        if spec["preferred_key"] is not None:
            every_value.append(values[spec["preferred_key"]])
    axis_low, axis_high = _axis_bounds(every_value)

    rows: list[FieldRow] = []
    for index, spec in enumerate(rows_spec):
        top = FIRST_ROW_TOP + index * ROW_PITCH
        low, high = values[spec["low_key"]], values[spec["high_key"]]
        preferred_key = spec["preferred_key"]
        preferred = values[preferred_key] if preferred_key is not None else None
        x_low, x_high = _x(low, axis_low, axis_high), _x(high, axis_low, axis_high)
        rows.append(
            FieldRow(
                id=spec["id"],
                label=SHORT_LABELS[spec["id"]],
                table_label=spec["label"],
                owner=spec["id"] != "expert",
                low_key=spec["low_key"],
                high_key=spec["high_key"],
                preferred_key=preferred_key,
                low_aud=low,
                high_aud=high,
                preferred_aud=preferred,
                x_low=_pct(x_low),
                x_high=_pct(x_high),
                x_preferred=None if preferred is None else _pct(_x(preferred, axis_low, axis_high)),
                width=_pct(x_high - x_low),
                top=top,
                label_y=top + LABEL_BASELINE_IN_ROW,
                bar_y=top + BAR_TOP_IN_ROW,
                bar_height=BAR_HEIGHT,
                tick_y1=top + BAR_TOP_IN_ROW - TICK_OVERHANG,
                tick_y2=top + BAR_TOP_IN_ROW + BAR_HEIGHT + TICK_OVERHANG,
                mid_y=top + BAR_TOP_IN_ROW + BAR_HEIGHT // 2,
                low_text=number(low),
                high_text=number(high),
                preferred_text=None if preferred is None else number(preferred),
                low_label_x=_pct(x_low),
                high_label_x=_pct(x_high),
                low_ref=_expert_ref(inputs, sources, "low") if spec["id"] == "expert" else None,
                high_ref=_expert_ref(inputs, sources, "high") if spec["id"] == "expert" else None,
            )
        )

    plot_top = FIRST_ROW_TOP - 8
    plot_bottom = FIRST_ROW_TOP + len(rows_spec) * ROW_PITCH - 8
    # The offer input is dated 9 May 2025, when Domain signed the scheme implementation deed at
    # A$4.43 (data/extracted/deal_timeline.csv). A$4.43 was first offered on 27 March 2025, so the
    # label says what the date is.
    offer_date = inputs.assumptions["offer_price_aud"].as_at
    undisturbed_date = inputs.assumptions["undisturbed_share_price_aud"].as_at
    offer_x = _x(offer, axis_low, axis_high)
    undisturbed_x = _x(undisturbed, axis_low, axis_high)
    return FootballField(
        axis_min_aud=axis_low,
        axis_max_aud=axis_high,
        height=plot_bottom + BOTTOM_LABEL_GAP + 8,
        plot_top=plot_top,
        plot_bottom=plot_bottom,
        top_label_y=TOP_LABEL_BASELINE,
        top_axis_y=TOP_AXIS_BASELINE,
        bottom_axis_y=plot_bottom + BOTTOM_AXIS_GAP,
        bottom_label_y=plot_bottom + BOTTOM_LABEL_GAP,
        ticks=_ticks(axis_low, axis_high),
        rows=tuple(rows),
        offer=ReferenceLine(
            "offer_price_aud",
            _pct(offer_x),
            offer,
            f"Offer {aud(offer)} (deed signed {offer_date})",
            offer_date,
            "middle",
        ),
        undisturbed=ReferenceLine(
            "undisturbed_share_price_aud",
            _pct(undisturbed_x),
            undisturbed,
            f"Undisturbed price {aud(undisturbed)} ({undisturbed_date})",
            undisturbed_date,
            "start",
        ),
        title="Value per share by method, A$",
        description=_description(rows, offer, undisturbed),
        reference_prices=(
            ReferencePrice(
                "offer_price_aud",
                f"Offer (deed signed {offer_date})",
                number(offer),
                sources.use(sources.book.for_input("offer_price_aud")),
            ),
            ReferencePrice(
                "undisturbed_share_price_aud",
                f"Undisturbed price ({undisturbed_date})",
                number(undisturbed),
                sources.use(sources.book.for_input("undisturbed_share_price_aud")),
            ),
        ),
        sources=tuple(sources.entries()),
    )


def _expert_ref(inputs: Inputs, sources: PageSources, case: str) -> str:
    """The code of the booklet table that holds the expert's value per share."""
    row = inputs.table_row("valuation_summary", item="value_per_share", case=case)
    return sources.use(sources.book.for_table_row("valuation_summary", row))


def _description(rows: list[FieldRow], offer: float, undisturbed: float) -> str:
    parts = [f"{row.label}: {aud(row.low_aud)} to {aud(row.high_aud)}." for row in rows]
    return (
        "Horizontal bars show the low and high value per share for each method. "
        + " ".join(parts)
        + f" The offer was {aud(offer)} and the undisturbed price was {aud(undisturbed)}."
    )

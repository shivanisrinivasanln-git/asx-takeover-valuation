"""Geometry, labels and tables for the gap bridge page (task P5-11).

The bridge runs from the midpoint of the expert's range to my preferred value, one group of
inputs at a time. Every figure comes from `valuation.json` `gap_bridge`, and the explanation of
each step is my wording from `data/written/gap_step_explanations.csv`, passed through unchanged.
Like the football field, the chart is an inline SVG with percentage x coordinates and no
`viewBox`, and Python decides each position and label.
"""

from __future__ import annotations

import math
from typing import Any

from valuation.gap_bridge import expert_input_name
from valuation.inputs import Inputs
from valuation.provenance import PageSources, ReferenceBook
from valuation.site_format import aud, aud_signed, number, signed

AXIS_STEP_AUD = 0.1
AXIS_MARGIN_AUD = 0.05

# Vertical layout in pixels. Text is set in CSS, so these only place it.
TOP_AXIS_BASELINE = 16
FIRST_ROW_TOP = 36
ROW_PITCH = 46
LABEL_BASELINE_IN_ROW = 14
BAR_TOP_IN_ROW = 22
BAR_HEIGHT = 14
MARKER_OVERHANG = 4
BOTTOM_AXIS_GAP = 18
# A label that would run past this share of the width goes on the left of its bar instead.
LABEL_FLIP_PERCENT = 85.0

UNIT_SYMBOLS = {"pct": "%", "times": "x"}

# The chart's row labels. The long labels in valuation.json go in the table and the step
# headings, because a row label that does not fit a phone-width row is cut off.
SHORT_LABELS = {
    "weights": "Method weights",
    "discount_rate": "Discount rate",
    "forecast": "Forecast",
    "terminal_growth": "Terminal growth",
    "trading_multiples": "Trading multiples",
    "precedent_multiples": "Precedent multiples",
    "control_premium": "Control premium",
    "net_debt_and_shares": "Net debt and shares",
}


def _pct(value: float) -> str:
    return f"{value:.3f}%"


def _x(value: float, low: float, high: float) -> float:
    return (value - low) / (high - low) * 100


def _axis(values: list[float]) -> tuple[float, float]:
    low = math.floor(round((min(values) - AXIS_MARGIN_AUD) / AXIS_STEP_AUD, 9)) * AXIS_STEP_AUD
    high = math.ceil(round((max(values) + AXIS_MARGIN_AUD) / AXIS_STEP_AUD, 9)) * AXIS_STEP_AUD
    return round(low, 10), round(high, 10)


def _ticks(low: float, high: float) -> list[dict[str, str]]:
    count = round((high - low) / AXIS_STEP_AUD)
    ticks = []
    for index in range(count + 1):
        value = low + index * AXIS_STEP_AUD
        anchor = "start" if index == 0 else "end" if index == count else "middle"
        ticks.append({"x": _pct(_x(value, low, high)), "label": f"{value:.2f}", "anchor": anchor})
    return ticks


def _direction(change_aud: float) -> str:
    # A step that rounds to zero at the cent is drawn as a mark and not as a bar.
    if round(change_aud, 2) == 0:
        return "none"
    return "up" if change_aud > 0 else "down"


def _label_position(x_low: float, x_high: float) -> tuple[str, str, int]:
    """The x of a step's label, its anchor and its offset from the bar end in pixels."""
    if x_high > LABEL_FLIP_PERCENT:
        return _pct(x_low), "end", -6
    return _pct(x_high), "start", 6


def _input_changes(
    step: dict[str, Any], inputs: Inputs, sources: PageSources
) -> list[dict[str, str]]:
    rows = []
    for key in step["inputs"]:
        unit = inputs.assumptions[key].unit
        symbol = UNIT_SYMBOLS.get(unit, unit)
        rows.append(
            {
                "key": key,
                "unit": symbol,
                "expert": number(step["expert_values"][key], 1),
                "expert_ref": sources.use(sources.book.for_input(expert_input_name(key))),
                "mine": number(step["my_values"][key], 1),
                "mine_ref": sources.use(sources.book.for_input(key)),
            }
        )
    return rows


def _chart_rows(bridge: dict[str, Any], low: float, high: float) -> list[dict[str, Any]]:
    steps = bridge["steps"]
    kinds: list[dict[str, Any]] = [
        {
            "id": "start",
            "kind": "start",
            "label": "Expert's midpoint",
            "from": bridge["start_value_per_share_aud"],
            "to": bridge["start_value_per_share_aud"],
            "change": None,
            "key": "start_value_per_share_aud",
            "text": number(bridge["start_value_per_share_aud"]),
        }
    ]
    for step in steps:
        cumulative = step["cumulative_value_per_share_aud"]
        kinds.append(
            {
                "id": step["id"],
                "kind": "step",
                "label": SHORT_LABELS[step["id"]],
                "from": cumulative - step["change_aud"],
                "to": cumulative,
                "change": step["change_aud"],
                "key": f"{step['id']}:change_aud",
                "text": signed(step["change_aud"]),
            }
        )
    kinds.append(
        {
            "id": "end",
            "kind": "end",
            "label": "My preferred value",
            "from": bridge["end_value_per_share_aud"],
            "to": bridge["end_value_per_share_aud"],
            "change": None,
            "key": "end_value_per_share_aud",
            "text": number(bridge["end_value_per_share_aud"]),
        }
    )
    rows = []
    for index, spec in enumerate(kinds):
        top = FIRST_ROW_TOP + index * ROW_PITCH
        x_from, x_to = _x(spec["from"], low, high), _x(spec["to"], low, high)
        x_low, x_high = min(x_from, x_to), max(x_from, x_to)
        label_x, anchor, label_dx = _label_position(x_low, x_high)
        row = {
            **spec,
            "direction": "none" if spec["change"] is None else _direction(spec["change"]),
            "x_low": _pct(x_low),
            "x_width": _pct(x_high - x_low),
            "x_level": _pct(x_to),
            "label_x": label_x,
            "label_anchor": anchor,
            "label_dx": label_dx,
            "label_y": top + LABEL_BASELINE_IN_ROW,
            "bar_y": top + BAR_TOP_IN_ROW,
            "bar_height": BAR_HEIGHT,
            "mid_y": top + BAR_TOP_IN_ROW + BAR_HEIGHT // 2,
            "marker_y1": top + BAR_TOP_IN_ROW - MARKER_OVERHANG,
            "marker_y2": top + BAR_TOP_IN_ROW + BAR_HEIGHT + MARKER_OVERHANG,
            "connector_y1": top + BAR_TOP_IN_ROW + BAR_HEIGHT,
            "connector_y2": top + ROW_PITCH + BAR_TOP_IN_ROW,
            "has_connector": index < len(kinds) - 1,
        }
        rows.append(row)
    return rows


def _table_rows(bridge: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [
        {
            "label": bridge["start_label"],
            "href": None,
            "change": "",
            "change_key": None,
            "value": number(bridge["start_value_per_share_aud"]),
            "value_key": "start_value_per_share_aud",
            "pages": "",
        },
        {
            "label": "Rounding in the expert's printed multiples (not a step)",
            "href": None,
            "change": signed(bridge["reconstruction_change_aud"], 4),
            "change_key": "reconstruction_change_aud",
            "value": "",
            "value_key": None,
            "pages": "",
        },
    ]
    for step in bridge["steps"]:
        rows.append(
            {
                "label": step["label"],
                "href": f"#step-{step['id']}",
                "change": signed(step["change_aud"]),
                "change_key": f"{step['id']}:change_aud",
                "value": number(step["cumulative_value_per_share_aud"]),
                "value_key": f"{step['id']}:cumulative_value_per_share_aud",
                "pages": step["sources"],
            }
        )
    rows.append(
        {
            "label": "My preferred value",
            "href": None,
            "change": signed(bridge["total_gap_aud"]),
            "change_key": "total_gap_aud",
            "value": number(bridge["end_value_per_share_aud"]),
            "value_key": "end_value_per_share_aud",
            "pages": "",
        }
    )
    return rows


def _rounding(bridge: dict[str, Any]) -> dict[str, str]:
    """The sum of the steps rounded one by one, beside the total rounded once."""
    rounded_steps = round(sum(round(step["change_aud"], 2) for step in bridge["steps"]), 2)
    return {"steps_sum": signed(rounded_steps), "total": signed(bridge["total_gap_aud"])}


def _description(rows: list[dict[str, Any]], bridge: dict[str, Any]) -> str:
    steps = "; ".join(
        f"{row['label']} {aud_signed(row['change'])}" for row in rows if row["kind"] == "step"
    )
    return (
        "Horizontal bars show how each group of inputs moves the value per share from "
        f"{aud(bridge['start_value_per_share_aud'])}, the midpoint of the expert's range, to "
        f"{aud(bridge['end_value_per_share_aud'])}, my preferred value. {steps}."
    )


def build_bridge_page(valuation: dict[str, Any], inputs: Inputs) -> dict[str, Any]:
    """Everything the gap bridge templates need."""
    bridge = valuation["gap_bridge"]
    levels = [bridge["start_value_per_share_aud"], bridge["end_value_per_share_aud"]]
    for step in bridge["steps"]:
        levels += [
            step["cumulative_value_per_share_aud"],
            step["cumulative_value_per_share_aud"] - step["change_aud"],
        ]
    low, high = _axis(levels)
    rows = _chart_rows(bridge, low, high)
    plot_bottom = FIRST_ROW_TOP + len(rows) * ROW_PITCH - 10
    sources = PageSources(ReferenceBook(inputs))
    page: dict[str, Any] = {
        "axis_min_aud": low,
        "axis_max_aud": high,
        "ticks": _ticks(low, high),
        "rows": rows,
        "plot_top": FIRST_ROW_TOP - 8,
        "plot_bottom": plot_bottom,
        "top_axis_y": TOP_AXIS_BASELINE,
        "bottom_axis_y": plot_bottom + BOTTOM_AXIS_GAP,
        "height": plot_bottom + BOTTOM_AXIS_GAP + 8,
        "start_text": aud(bridge["start_value_per_share_aud"]),
        "title": "Gap bridge from the expert's midpoint to my preferred value, A$ per share",
        "description": _description(rows, bridge),
        "table": _table_rows(bridge),
        "rounding": _rounding(bridge),
        "order_note": bridge["order_note"],
        # The expert's value of business operations, which the explanations quote in A$m.
        "expert_operations_low": number(
            valuation["values"]["expert_business_operations_value_aud_m_low"]["value"], 0
        ),
        "expert_operations_high": number(
            valuation["values"]["expert_business_operations_value_aud_m_high"]["value"], 0
        ),
        "steps": [
            {
                "id": step["id"],
                "label": step["label"],
                "change": aud_signed(step["change_aud"]),
                "after": aud(step["cumulative_value_per_share_aud"]),
                "sources": step["sources"],
                "explanation": step["explanation"],
                "inputs": _input_changes(step, inputs, sources),
            }
            for step in bridge["steps"]
        ],
    }
    page["sources"] = sources.entries()
    return page

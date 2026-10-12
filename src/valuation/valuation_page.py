"""The data behind the valuation page: DCF tables, sensitivity grid, comparables and precedents.

Everything shown comes from `valuation.json` (the engine's figures) or from the transcribed
tables and `assumptions.yaml` (inputs, each with its source and page). Rounding happens here,
for display only, through `site_format`.
"""

from __future__ import annotations

import statistics
from typing import Any

from valuation.inputs import Inputs
from valuation.site_format import number, percent

CASES = ("low", "mid", "high")
CASE_LABELS = {"low": "Low", "mid": "Mid", "high": "High"}

# Inputs the DCF page shows, in reading order, with the label I give each.
DCF_ASSUMPTIONS = (
    ("revenue_growth_fy26_to_fy35_pct", "Revenue growth, FY26 to FY35"),
    ("ebitda_margin_fy30_pct", "EBITDA margin, FY30"),
    ("ebitda_margin_fy35_pct", "EBITDA margin, FY35"),
    ("capex_pct_of_revenue_fy26_to_fy30_pct", "Capital expenditure, FY26 to FY30"),
    ("capex_pct_of_revenue_long_term_pct", "Capital expenditure, long term"),
    ("depreciation_pct_of_revenue_long_term_pct", "Depreciation, long term"),
    ("working_capital_pct_of_revenue_pct", "Working capital, share of the change in revenue"),
    ("tax_rate_pct", "Tax rate"),
    ("corporate_cost_saving_aud_m", "Corporate cost saving each year"),
    ("terminal_growth_pct", "Terminal growth"),
    ("discount_rate_low_pct", "Discount rate, bottom of my range"),
    ("discount_rate_high_pct", "Discount rate, top of my range"),
    ("mid_year_discounting_flag", "Mid-year discounting"),
)
UNIT_LABELS = {
    "pct": "%",
    "aud_m": "A$m",
    "aud": "A$",
    "times": "x",
    "million shares": "m shares",
}

FORECAST_COLUMNS = (
    ("revenue_aud_m", "Revenue (A$m)", 1),
    ("ebitda_aud_m", "EBITDA (A$m)", 1),
    ("ebitda_margin_pct", "EBITDA margin (%)", 1),
    ("corporate_cost_saving_aud_m", "Corporate saving (A$m)", 1),
    ("depreciation_aud_m", "Depreciation (A$m)", 1),
    ("tax_aud_m", "Tax (A$m)", 1),
    ("capex_aud_m", "Capital expenditure (A$m)", 1),
    ("working_capital_increase_aud_m", "Working capital increase (A$m)", 1),
    ("agent_dividends_aud_m", "Agents' dividends (A$m)", 1),
    ("free_cash_flow_aud_m", "Free cash flow (A$m)", 1),
    ("discount_time_years", "Discount time (years)", 2),
    ("discount_factor_at_base_rate", "Discount factor", 3),
    ("present_value_at_base_rate_aud_m", "Present value (A$m)", 1),
)

# (label, key stem, decimal places). The case is appended to the stem.
DCF_VALUE_ROWS = (
    ("Discount rate (%)", "dcf_discount_rate_pct", 1),
    ("Present value of cash flows (A$m)", "dcf_present_value_of_cash_flows_aud_m", 1),
    ("Terminal value at the end of FY35 (A$m)", "dcf_terminal_value_aud_m", 1),
    ("Present value of terminal value (A$m)", "dcf_present_value_of_terminal_value_aud_m", 1),
    ("Value of business operations (A$m)", "dcf_business_operations_value_aud_m", 1),
    ("Enterprise value (A$m)", "dcf_enterprise_value_aud_m", 1),
    ("Equity value (A$m)", "dcf_equity_value_aud_m", 1),
    ("Diluted shares (m)", "dcf_diluted_shares_m", 1),
    ("Value per share (A$)", "dcf_value_per_share_aud", 2),
    ("Terminal value share of operations (%)", "dcf_terminal_value_share_of_operations_pct", 1),
)


def _values(valuation: dict[str, Any]) -> dict[str, float]:
    return {key: item["value"] for key, item in valuation["values"].items()}


def _assumption_rows(inputs: Inputs) -> list[dict[str, str]]:
    rows = []
    for key, label in DCF_ASSUMPTIONS:
        entry = inputs.assumptions[key]
        value = inputs.number(key)
        if key == "mid_year_discounting_flag":
            text, unit = ("Yes" if value == 1 else "No"), ""
        else:
            text, unit = number(value, 1), UNIT_LABELS.get(entry.unit, entry.unit)
        rows.append(
            {
                "key": key,
                "label": label,
                "value": text,
                "unit": unit,
                "source": entry.source,
                "location": entry.location,
                "as_at": entry.as_at,
                "judgement": "My judgement" if entry.judgement else "",
            }
        )
    return rows


def _forecast(valuation: dict[str, Any]) -> dict[str, Any]:
    forecast = valuation["forecast"]
    rows = [
        {
            "period": row["period"],
            "cells": [
                {"field": field, "text": number(row[field], places)}
                for field, _, places in FORECAST_COLUMNS
            ],
        }
        for row in forecast["rows"]
    ]
    return {
        "base_rate": percent(forecast["base_discount_rate_pct"]),
        "headers": [label for _, label, _ in FORECAST_COLUMNS],
        "rows": rows,
    }


def _dcf_values(values: dict[str, float]) -> dict[str, Any]:
    rows = []
    for label, stem, places in DCF_VALUE_ROWS:
        rows.append(
            {
                "label": label,
                "cells": [
                    {"key": f"{stem}_{case}", "text": number(values[f"{stem}_{case}"], places)}
                    for case in CASES
                ],
            }
        )
    return {
        "headers": [CASE_LABELS[case] for case in CASES],
        "rows": rows,
        "net_debt": {
            "key": "adjusted_net_debt_aud_m",
            "text": number(values["adjusted_net_debt_aud_m"], 1),
        },
        "other_assets": {
            "key": "other_assets_and_liabilities_aud_m",
            "text": number(values["other_assets_and_liabilities_aud_m"], 1),
        },
    }


def _sensitivity(valuation: dict[str, Any]) -> dict[str, Any]:
    grid = valuation["sensitivity"]
    rows = []
    for row_index, rate in enumerate(grid["discount_rates_pct"]):
        rows.append(
            {
                "rate": number(rate, 1),
                "cells": [
                    {
                        "text": number(value, 2),
                        "base": row_index == grid["base_row"] and column == grid["base_column"],
                    }
                    for column, value in enumerate(grid["value_per_share_aud"][row_index])
                ],
            }
        )
    return {
        "growths": [number(growth, 1) for growth in grid["terminal_growth_rates_pct"]],
        "rows": rows,
        "base_key": "dcf_value_per_share_aud_mid",
    }


def _summary_rows(multiples: list[float]) -> dict[str, str]:
    return {
        "lowest": number(min(multiples), 1),
        "median": number(statistics.median(multiples), 1),
        "highest": number(max(multiples), 1),
    }


def _comparables(inputs: Inputs) -> dict[str, Any]:
    columns = (
        ("ebitda", "forecast"),
        ("ebitda", "historical"),
        ("ebita", "forecast"),
        ("ebita", "historical"),
    )
    treatment = {row["company"]: row["treatment"] for row in inputs.tables["comparable_peer_set"]}
    companies = list(dict.fromkeys(row["company"] for row in inputs.tables["comparable_multiples"]))
    lookup = {
        (row["company"], row["measure"], row["basis"]): float(row["multiple_x"])
        for row in inputs.tables["comparable_multiples"]
    }
    rows = [
        {
            "company": company,
            "treatment": treatment.get(company, ""),
            "cells": [number(lookup[(company, measure, basis)], 1) for measure, basis in columns],
        }
        for company in companies
    ]
    summary = {
        name: [
            _summary_rows([v for (c, m, b), v in lookup.items() if (m, b) == column])[name]
            for column in columns
        ]
        for name in ("lowest", "median", "highest")
    }
    return {
        "as_at": inputs.tables["comparable_multiples"][0]["as_at"],
        "headers": [f"{basis.capitalize()} {measure.upper()} (x)" for measure, basis in columns],
        "rows": rows,
        "summary": summary,
    }


def _precedents(inputs: Inputs) -> dict[str, Any]:
    columns = (
        ("ebitda", "forecast"),
        ("ebitda", "historical"),
        ("ebita", "forecast"),
        ("ebita", "historical"),
    )
    deals: dict[tuple[str, str], dict[str, Any]] = {}
    for row in inputs.tables["precedent_transactions"]:
        key = (row["deal"], row["announced"])
        deal = deals.setdefault(
            key,
            {
                "deal": row["deal"],
                "announced": row["announced"],
                "acquirer": row["acquirer"],
                "status": "Unsuccessful proposal" if row["unsuccessful"] == "yes" else "Completed",
                "multiples": {},
            },
        )
        deal["multiples"][(row["measure"], row["basis"])] = float(row["multiple_x"])
    rows = [
        {
            **{k: deal[k] for k in ("deal", "announced", "acquirer", "status")},
            "cells": [
                number(deal["multiples"][column], 1) if column in deal["multiples"] else "n/a"
                for column in columns
            ],
        }
        for deal in deals.values()
    ]
    summary = {
        name: [
            _summary_rows([d["multiples"][c] for d in deals.values() if c in d["multiples"]])[name]
            for c in columns
        ]
        for name in ("lowest", "median", "highest")
    }
    return {
        "headers": [f"{basis.capitalize()} {measure.upper()} (x)" for measure, basis in columns],
        "rows": rows,
        "summary": summary,
    }


def _selected_range(values: dict[str, float], method: str, measure: str) -> dict[str, Any]:
    stem = f"{method}_{measure}"
    return {
        "measure": measure.upper(),
        "earnings": number(values[f"{stem}_earnings_aud_m"], 1),
        "premium": number(values[f"{stem}_control_premium_pct"], 1),
        "rows": [
            (
                "Multiple (x)",
                [
                    {
                        "key": f"{stem}_multiple_x_{case}",
                        "text": number(values[f"{stem}_multiple_x_{case}"], 2),
                    }
                    for case in CASES
                ],
            ),
            (
                "Value of business operations (A$m)",
                [
                    {
                        "key": f"{stem}_business_operations_value_aud_m_{case}",
                        "text": number(values[f"{stem}_business_operations_value_aud_m_{case}"], 1),
                    }
                    for case in CASES
                ],
            ),
            (
                "Value per share (A$)",
                [
                    {
                        "key": f"{stem}_value_per_share_aud_{case}",
                        "text": number(values[f"{stem}_value_per_share_aud_{case}"], 2),
                    }
                    for case in CASES
                ],
            ),
        ],
    }


def build_valuation_page(valuation: dict[str, Any], inputs: Inputs) -> dict[str, Any]:
    """Everything the valuation page templates need."""
    values = _values(valuation)
    return {
        "assumptions": _assumption_rows(inputs),
        "forecast": _forecast(valuation),
        "dcf_values": _dcf_values(values),
        "sensitivity": _sensitivity(valuation),
        "case_headers": [CASE_LABELS[case] for case in CASES],
        "comparables": _comparables(inputs),
        "precedents": _precedents(inputs),
        "trading_ranges": [_selected_range(values, "trading", m) for m in ("ebitda", "ebita")],
        "precedent_ranges": [_selected_range(values, "precedent", m) for m in ("ebitda", "ebita")],
        "base_value_text": number(values["dcf_value_per_share_aud_mid"], 2),
    }

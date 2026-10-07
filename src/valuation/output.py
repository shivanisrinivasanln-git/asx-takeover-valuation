"""Build `valuation.json`: every number the site, the Excel model and the report display.

Each scalar sits under a stable key with its unit, at full precision. A key's name carries its
unit (`_aud_m`, `_aud`, `_pct`, `_x`, `_shares_m`, `_years`), and the Excel defined names are
these keys. A trailing `_low`, `_mid` or `_high` is the value case, not a rate: the low case
discounts at the top of the adopted discount rate range, and the high case at the bottom.
"""

from __future__ import annotations

import calendar
import json
from pathlib import Path
from typing import Any

from valuation import finance
from valuation.bridge import Case, adjusted_net_debt_aud_m, equity_bridge
from valuation.dcf import (
    dcf_value,
    discount_factor,
    time_of_cash_flow_years,
    wacc_range_pct,
)
from valuation.forecast import YearCashFlow, forecast_from_inputs
from valuation.inputs import Inputs
from valuation.multiples import Measure, Method, multiples_value
from valuation.sensitivity import (
    base_discount_rate_pct,
    sensitivity_grid,
    use_mid_year,
)

SCHEMA_VERSION = 1
UNIT_SUFFIXES = {
    "_aud_m": "aud_m",
    "_aud": "aud",
    "_pct": "pct",
    "_x": "x",
    "_shares_m": "shares_m",
    "_years": "years",
}
CASES: tuple[Case, ...] = ("low", "mid", "high")
EDGE_CASES: tuple[Case, ...] = ("low", "high")
METHODS: tuple[Method, ...] = ("trading", "precedent")
MEASURES: tuple[Measure, ...] = ("ebitda", "ebita")


def unit_for_key(key: str) -> str:
    """The unit a key's name promises, ignoring a trailing value case."""
    stem = key.rsplit("_", 1)[0] if key.rsplit("_", 1)[-1] in CASES else key
    for suffix, unit in UNIT_SUFFIXES.items():
        if stem.endswith(suffix):
            return unit
    raise ValueError(f"{key} does not end in a unit suffix")


class _Values:
    """Scalars in the order they are added, rejecting a repeated key."""

    def __init__(self) -> None:
        self.items: dict[str, dict[str, Any]] = {}

    def add(self, key: str, value: float) -> None:
        if key in self.items:
            raise ValueError(f"repeated key {key}")
        self.items[key] = {"value": value, "unit": unit_for_key(key)}


def _discount_rate_pct(inputs: Inputs, case: Case) -> float:
    if case == "low":
        return inputs.number("discount_rate_high_pct")
    if case == "high":
        return inputs.number("discount_rate_low_pct")
    return base_discount_rate_pct(inputs)


def _add_dcf(values: _Values, inputs: Inputs, cash_flows: list[YearCashFlow]) -> None:
    growth = inputs.number("terminal_growth_pct")
    values.add("dcf_terminal_growth_pct", growth)
    for case in CASES:
        rate = _discount_rate_pct(inputs, case)
        dcf = dcf_value(inputs, cash_flows, rate, growth, use_mid_year(inputs))
        bridge = equity_bridge(inputs, dcf.enterprise_value_aud_m, case)
        values.add(f"dcf_discount_rate_pct_{case}", rate)
        values.add(
            f"dcf_present_value_of_cash_flows_aud_m_{case}", dcf.present_value_of_cash_flows_aud_m
        )
        values.add(f"dcf_terminal_value_aud_m_{case}", dcf.terminal_value_aud_m)
        values.add(
            f"dcf_present_value_of_terminal_value_aud_m_{case}",
            dcf.present_value_of_terminal_value_aud_m,
        )
        values.add(
            f"dcf_terminal_value_share_of_operations_pct_{case}",
            dcf.present_value_of_terminal_value_aud_m / dcf.enterprise_value_aud_m * 100,
        )
        values.add(f"dcf_business_operations_value_aud_m_{case}", bridge.business_operations_aud_m)
        values.add(f"dcf_enterprise_value_aud_m_{case}", bridge.enterprise_value_aud_m)
        values.add(f"dcf_equity_value_aud_m_{case}", bridge.equity_value_aud_m)
        values.add(f"dcf_diluted_shares_m_{case}", bridge.diluted_shares_m)
        values.add(f"dcf_value_per_share_aud_{case}", bridge.value_per_share_aud)


def _add_multiples(values: _Values, inputs: Inputs) -> None:
    for method in METHODS:
        for measure in MEASURES:
            result = multiples_value(inputs, method, measure)
            prefix = f"{method}_{measure}"
            values.add(f"{prefix}_earnings_aud_m", result.earnings_aud_m)
            values.add(f"{prefix}_control_premium_pct", result.control_premium_pct)
            multiples = {"low": result.low_multiple_x, "high": result.high_multiple_x}
            operations = {"low": result.value_low_aud_m, "high": result.value_high_aud_m}
            for case in EDGE_CASES:
                bridge = equity_bridge(inputs, operations[case], case)
                values.add(f"{prefix}_multiple_x_{case}", multiples[case])
                values.add(f"{prefix}_business_operations_value_aud_m_{case}", operations[case])
                values.add(f"{prefix}_enterprise_value_aud_m_{case}", bridge.enterprise_value_aud_m)
                values.add(f"{prefix}_equity_value_aud_m_{case}", bridge.equity_value_aud_m)
                values.add(f"{prefix}_diluted_shares_m_{case}", bridge.diluted_shares_m)
                values.add(f"{prefix}_value_per_share_aud_{case}", bridge.value_per_share_aud)


def _add_discount_rate(values: _Values, inputs: Inputs) -> None:
    for stem, key in (
        ("wacc", "risk_free_rate_pct"),
        ("wacc_at_expert_risk_free", "expert_risk_free_rate_pct"),
    ):
        low, high = wacc_range_pct(inputs, key)
        values.add(f"{stem}_pct_low", low)
        values.add(f"{stem}_pct_high", high)


def _add_reference(values: _Values, inputs: Inputs) -> None:
    printed = {
        case: inputs.table_number("valuation_summary", "value", item="value_per_share", case=case)
        for case in EDGE_CASES
    }
    operations = {
        case: inputs.table_number(
            "valuation_summary", "value", item="business_operations", case=case
        )
        for case in EDGE_CASES
    }
    for case in EDGE_CASES:
        values.add(f"expert_business_operations_value_aud_m_{case}", operations[case])
        values.add(f"expert_value_per_share_aud_{case}", printed[case])
    # The expert gave a range only; the midpoint is mine and is labelled as such wherever shown.
    values.add("expert_value_per_share_aud_mid", (printed["low"] + printed["high"]) / 2)
    values.add("offer_price_aud", inputs.number("offer_price_aud"))
    values.add("undisturbed_share_price_aud", inputs.number("undisturbed_share_price_aud"))
    values.add(
        "offer_premium_to_undisturbed_pct",
        finance.offer_premium_pct(
            inputs.number("offer_price_aud"), inputs.number("undisturbed_share_price_aud")
        ),
    )
    values.add("adjusted_net_debt_aud_m", adjusted_net_debt_aud_m(inputs))
    values.add(
        "other_assets_and_liabilities_aud_m", inputs.number("other_assets_and_liabilities_aud_m")
    )


def _forecast_table(inputs: Inputs, cash_flows: list[YearCashFlow]) -> dict[str, Any]:
    stub_years = inputs.number("stub_period_years")
    mid_year = use_mid_year(inputs)
    rate = base_discount_rate_pct(inputs)
    first_fiscal_year = int(inputs.series("valuation_date_ymd")[0]) + 1
    rows = []
    for row in cash_flows:
        years = time_of_cash_flow_years(row.year, stub_years, mid_year)
        factor = discount_factor(rate, years)
        rows.append(
            {
                "year": row.year,
                "period": f"FY{first_fiscal_year + row.year} second half"
                if row.year == 0
                else f"FY{first_fiscal_year + row.year}",
                "revenue_aud_m": row.revenue_aud_m,
                "ebitda_aud_m": row.ebitda_aud_m,
                "ebitda_margin_pct": row.ebitda_aud_m / row.revenue_aud_m * 100,
                "corporate_cost_saving_aud_m": row.corporate_cost_saving_aud_m,
                "depreciation_aud_m": row.depreciation_aud_m,
                "tax_aud_m": row.tax_aud_m,
                "capex_aud_m": row.capex_aud_m,
                "working_capital_increase_aud_m": row.working_capital_increase_aud_m,
                "agent_dividends_aud_m": row.agent_dividends_aud_m,
                "free_cash_flow_aud_m": row.free_cash_flow_aud_m,
                "discount_time_years": years,
                "discount_factor_at_base_rate": factor,
                "present_value_at_base_rate_aud_m": row.free_cash_flow_aud_m * factor,
            }
        )
    return {
        "base_discount_rate_pct": rate,
        "units": "A$ millions unless the field name says otherwise",
        "rows": rows,
    }


def _sensitivity_table(inputs: Inputs) -> dict[str, Any]:
    grid = sensitivity_grid(inputs)
    return {
        "discount_rates_pct": list(grid.discount_rates_pct),
        "terminal_growth_rates_pct": list(grid.terminal_growth_rates_pct),
        "value_per_share_aud": [list(row) for row in grid.value_per_share_aud],
        "base_row": grid.base_row,
        "base_column": grid.base_column,
        "share_count": "average of the low and high diluted share counts",
    }


FOOTBALL_FIELD_ROWS = (
    ("dcf", "Discounted cash flow", "dcf_value_per_share_aud_low", "dcf_value_per_share_aud_high"),
    (
        "trading",
        "Trading comparables (EBITDA multiple)",
        "trading_ebitda_value_per_share_aud_low",
        "trading_ebitda_value_per_share_aud_high",
    ),
    (
        "precedent",
        "Precedent transactions (EBITDA multiple)",
        "precedent_ebitda_value_per_share_aud_low",
        "precedent_ebitda_value_per_share_aud_high",
    ),
    (
        "expert",
        "Independent expert",
        "expert_value_per_share_aud_low",
        "expert_value_per_share_aud_high",
    ),
)


def valuation_date_label(inputs: Inputs) -> str:
    year, month, day = (int(part) for part in inputs.series("valuation_date_ymd"))
    return f"{day} {calendar.month_name[month]} {year}"


def build_valuation(inputs: Inputs) -> dict[str, Any]:
    """Every displayed number from the engine on the current inputs, at full precision."""
    cash_flows = forecast_from_inputs(inputs)
    values = _Values()
    _add_dcf(values, inputs, cash_flows)
    _add_multiples(values, inputs)
    _add_discount_rate(values, inputs)
    _add_reference(values, inputs)
    return {
        "schema_version": SCHEMA_VERSION,
        "meta": {
            "target": "Domain Holdings Australia (ASX: DHG)",
            "valuation_date": valuation_date_label(inputs),
            "discounting": "mid-year" if use_mid_year(inputs) else "year end",
            "status": "Seeded with the expert's disclosed inputs; my own base case is not set yet.",
            "case_note": "A trailing low, mid or high is the value case: the low case "
            "discounts at the top of the discount rate range.",
        },
        "values": values.items,
        "football_field": [
            {"id": row_id, "label": label, "low_key": low_key, "high_key": high_key}
            for row_id, label, low_key, high_key in FOOTBALL_FIELD_ROWS
        ],
        "forecast": _forecast_table(inputs, cash_flows),
        "sensitivity": _sensitivity_table(inputs),
    }


def write_valuation_json(inputs: Inputs, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_valuation(inputs), indent=2) + "\n", encoding="utf-8")

"""Load every input the engine uses and raise one error naming anything missing.

The inputs are `assumptions.yaml` (my inputs, each with a source) and the hand-transcribed tables
in `data/extracted/` (the evidence behind them). The engine never reads a file itself, so a
missing input stops the run before any calculation starts.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path

from valuation.assumptions import Assumption, load_assumptions
from valuation.extracted import load_rows

REQUIRED_ASSUMPTIONS = (
    "valuation_date_ymd",
    "projection_end_date_ymd",
    "stub_period_years",
    "fy25_revenue_aud_m",
    "fy25_ebitda_aud_m",
    "revenue_growth_fy26_to_fy35_pct",
    "ebitda_margin_fy30_pct",
    "ebitda_margin_fy35_pct",
    "capex_pct_of_revenue_fy26_to_fy30_pct",
    "capex_pct_of_revenue_long_term_pct",
    "fy25_depreciation_and_other_amortisation_aud_m",
    "depreciation_pct_of_revenue_long_term_pct",
    "working_capital_pct_of_revenue_pct",
    "tax_rate_pct",
    "terminal_growth_pct",
    "agent_dividend_pct_of_prior_year_revenue_pct",
    "residential_and_mdc_share_of_revenue_pct",
    "corporate_cost_saving_aud_m",
    "risk_free_rate_pct",
    "expert_risk_free_rate_pct",
    "market_risk_premium_pct",
    "equity_beta_low",
    "equity_beta_high",
    "cost_of_debt_margin_over_risk_free_pct",
    "equity_weight_low_pct",
    "equity_weight_high_pct",
    "discount_rate_low_pct",
    "discount_rate_high_pct",
    "fy26_adjusted_ebitda_aud_m",
    "fy26_adjusted_ebita_aud_m",
    "trading_ebitda_multiple_fy26_low_x",
    "trading_ebitda_multiple_fy26_high_x",
    "trading_ebita_multiple_fy26_low_x",
    "trading_ebita_multiple_fy26_high_x",
    "precedent_ebitda_multiple_fy26_low_x",
    "precedent_ebitda_multiple_fy26_high_x",
    "precedent_ebita_multiple_fy26_low_x",
    "precedent_ebita_multiple_fy26_high_x",
    "reported_net_debt_including_leases_aud_m",
    "net_debt_adjustment_capitalised_borrowing_costs_aud_m",
    "net_debt_adjustment_interim_dividend_aud_m",
    "other_assets_and_liabilities_aud_m",
    "ordinary_shares_on_issue_m",
    "treasury_shares_m",
    "share_rights_vesting_low_m",
    "share_rights_vesting_high_m",
    "share_rights_cash_settled_m",
    "offer_price_aud",
    "special_dividend_aud",
    "undisturbed_share_price_aud",
    "control_premium_typical_low_pct",
    "control_premium_typical_high_pct",
    "listed_share_discount_to_underlying_low_pct",
    "listed_share_discount_to_underlying_high_pct",
    "control_premium_applied_pct",
    "method_weight_dcf_pct",
    "method_weight_trading_pct",
    "method_weight_precedent_pct",
    "expert_method_weight_dcf_pct",
    "expert_method_weight_trading_pct",
    "expert_method_weight_precedent_pct",
    "expert_discount_rate_low_pct",
    "expert_discount_rate_high_pct",
    "expert_revenue_growth_fy26_to_fy35_pct",
    "expert_ebitda_margin_fy30_pct",
    "expert_ebitda_margin_fy35_pct",
    "expert_capex_pct_of_revenue_fy26_to_fy30_pct",
    "expert_capex_pct_of_revenue_long_term_pct",
    "expert_depreciation_pct_of_revenue_long_term_pct",
    "expert_working_capital_pct_of_revenue_pct",
    "expert_terminal_growth_pct",
    "expert_trading_ebitda_multiple_fy26_low_x",
    "expert_trading_ebitda_multiple_fy26_high_x",
    "expert_precedent_ebitda_multiple_fy26_low_x",
    "expert_precedent_ebitda_multiple_fy26_high_x",
    "expert_control_premium_applied_pct",
    "mid_year_discounting_flag",
    "sensitivity_rate_step_pct",
    "sensitivity_growth_step_pct",
    "sensitivity_steps_each_side",
)

REQUIRED_TABLES = (
    "balance_sheet",
    "broker_forecast_summary",
    "cash_flow",
    "comparable_multiples",
    "dcf_npv_chart_reads",
    "dcf_scenarios",
    "discount_rate_evidence",
    "domain_implied_multiples",
    "historical_pnl",
    "market_rates_30_may_2025",
    "net_debt_bridge",
    "precedent_transactions",
    "share_build",
    "valuation_summary",
)


# Tables I wrote myself (each row still carries its source, location and date).
REQUIRED_WRITTEN_TABLES = ("gap_step_explanations",)


class MissingInputError(ValueError):
    """One or more required inputs or data files are missing; the message lists each."""


@dataclass(frozen=True)
class Inputs:
    assumptions: Mapping[str, Assumption]
    tables: Mapping[str, tuple[Mapping[str, str], ...]]

    def number(self, key: str) -> float:
        """A single-number input, such as `tax_rate_pct`."""
        value = self.assumptions[key].value
        if not isinstance(value, float):
            raise ValueError(f"{key} is a series, not a single number")
        return value

    def series(self, key: str) -> tuple[float, ...]:
        """A series input, such as `valuation_date_ymd`."""
        value = self.assumptions[key].value
        if not isinstance(value, tuple):
            raise ValueError(f"{key} is a single number, not a series")
        return value

    def table_row(self, table: str, **match: str) -> Mapping[str, str]:
        """The one row of `table` whose fields equal `match`."""
        rows = [
            row
            for row in self.tables[table]
            if all(row.get(field) == wanted for field, wanted in match.items())
        ]
        if len(rows) != 1:
            raise ValueError(f"{table} has {len(rows)} rows matching {match}, expected 1")
        return rows[0]

    def with_assumption_values(self, values: Mapping[str, float]) -> Inputs:
        """The same inputs with some single-number assumptions set to other values."""
        assumptions = dict(self.assumptions)
        for name, value in values.items():
            assumptions[name] = replace(assumptions[name], value=value)
        return Inputs(assumptions=assumptions, tables=self.tables)

    def table_number(self, table: str, column: str, **match: str) -> float:
        """The value in `column` of the one row of `table` whose fields equal `match`."""
        return float(self.table_row(table, **match)[column])


def load_inputs(root: Path) -> Inputs:
    """Load the assumptions file and the data tables under `root`, or raise `MissingInputError`."""
    problems: list[str] = []
    assumptions_path = root / "assumptions.yaml"
    assumptions: dict[str, Assumption] = {}
    if assumptions_path.exists():
        assumptions = load_assumptions(assumptions_path)
        problems += [
            f"assumptions.yaml: missing input '{key}'"
            for key in REQUIRED_ASSUMPTIONS
            if key not in assumptions
        ]
    else:
        problems.append("assumptions.yaml: file not found")

    tables: dict[str, tuple[Mapping[str, str], ...]] = {}
    for name in REQUIRED_TABLES:
        path = root / "data" / "extracted" / f"{name}.csv"
        if path.exists():
            tables[name] = tuple(load_rows(path))
        else:
            problems.append(f"data/extracted/{name}.csv: file not found")

    for name in REQUIRED_WRITTEN_TABLES:
        path = root / "data" / "written" / f"{name}.csv"
        if path.exists():
            tables[name] = tuple(load_rows(path))
        else:
            problems.append(f"data/written/{name}.csv: file not found")

    if problems:
        raise MissingInputError("\n".join(problems))
    return Inputs(assumptions=assumptions, tables=tables)

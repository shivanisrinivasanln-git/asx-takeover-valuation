"""The balance sheet, cash flow and net debt build from the booklet add up as printed."""

from itertools import pairwise
from pathlib import Path

import pytest

from valuation.extracted import load_rows

DATA = Path(__file__).resolve().parents[2] / "data" / "extracted"
PERIODS = ["FY21", "FY22", "FY23", "FY24", "1HY25"]
BALANCE_DATES = ["30 June 2024", "31 December 2024"]
ROUNDING_AUD_M = 0.05
# A subtotal of several lines, each printed to one decimal, can differ by 0.05 per line.
SUM_OF_TEN_ROUNDING_AUD_M = 0.15
THREE_LINES_ROUNDING_AUD_M = 0.15
ADJUSTED_NET_DEBT_AUD_M = -187.0


def balance(date: str, item: str) -> float:
    rows = load_rows(DATA / "balance_sheet.csv")
    return float(
        next(r["value"] for r in rows if r["balance_date"] == date and r["line_item"] == item)
    )


def cash_flow(period: str, item: str) -> float:
    rows = load_rows(DATA / "cash_flow.csv")
    return float(next(r["value"] for r in rows if r["period"] == period and r["line_item"] == item))


def net_debt(item: str) -> float:
    rows = load_rows(DATA / "net_debt_bridge.csv")
    return float(next(r["value_aud_m"] for r in rows if r["item"] == item))


@pytest.mark.parametrize("date", BALANCE_DATES)
def test_balance_sheet_subtotals_add_up(date: str) -> None:
    working_capital = sum(
        balance(date, item)
        for item in (
            "trade_and_other_receivables",
            "trade_and_other_payables",
            "payables_related_parties",
        )
    )
    assert balance(date, "net_working_capital") == pytest.approx(
        working_capital, abs=ROUNDING_AUD_M
    )
    funds_employed = sum(
        balance(date, item)
        for item in (
            "net_working_capital",
            "goodwill",
            "other_intangible_assets",
            "property_plant_and_equipment_net",
            "right_of_use_assets",
            "convertible_notes_and_equity_accounted_investments",
            "current_tax_liabilities",
            "deferred_tax_liabilities_net",
            "provisions",
            "contingent_consideration",
        )
    )
    assert balance(date, "total_funds_employed") == pytest.approx(
        funds_employed, abs=SUM_OF_TEN_ROUNDING_AUD_M
    )


@pytest.mark.parametrize("date", BALANCE_DATES)
def test_balance_sheet_net_debt_and_equity_follow_from_the_lines(date: str) -> None:
    excluding = balance(date, "cash_and_cash_equivalents") + balance(
        date, "interest_bearing_liabilities"
    )
    assert balance(date, "net_debt_excluding_leases") == pytest.approx(
        excluding, abs=ROUNDING_AUD_M
    )
    including = balance(date, "net_debt_excluding_leases") + balance(date, "lease_liabilities")
    assert balance(date, "net_debt_including_leases") == pytest.approx(
        including, abs=ROUNDING_AUD_M
    )
    net_assets = balance(date, "total_funds_employed") + balance(date, "net_debt_including_leases")
    assert balance(date, "net_assets") == pytest.approx(net_assets, abs=ROUNDING_AUD_M)
    equity = balance(date, "net_assets") + balance(date, "non_controlling_interest")
    assert balance(date, "equity_attributable_to_domain_shareholders") == pytest.approx(
        equity, abs=THREE_LINES_ROUNDING_AUD_M
    )


@pytest.mark.parametrize("period", PERIODS)
def test_operating_cash_flow_and_net_cash_add_up(period: str) -> None:
    operating = sum(
        cash_flow(period, item)
        for item in (
            "ebitda",
            "changes_in_working_capital_and_other",
            "net_lease_payments",
            "income_tax_payments",
            "finance_costs_paid_net_of_interest_received",
        )
    )
    assert cash_flow(period, "operating_cash_flow") == pytest.approx(operating, abs=ROUNDING_AUD_M)
    net_cash = sum(
        cash_flow(period, item)
        for item in (
            "operating_cash_flow",
            "capital_expenditure_net",
            "net_investment_in_businesses_and_ventures",
            "dividends_paid_to_domain_shareholders",
            "dividends_paid_to_non_controlling_interest",
            "net_share_purchases_and_issues",
            "other",
        )
    )
    assert cash_flow(period, "net_cash_generated_or_used") == pytest.approx(
        net_cash, abs=ROUNDING_AUD_M
    )


@pytest.mark.parametrize("period", PERIODS)
def test_closing_net_debt_follows_from_opening_net_debt(period: str) -> None:
    closing = (
        cash_flow(period, "net_debt_excluding_leases_opening")
        + cash_flow(period, "net_cash_generated_or_used")
        + cash_flow(period, "non_cash_movements_in_interest_bearing_liabilities")
    )
    assert cash_flow(period, "net_debt_excluding_leases_closing") == pytest.approx(
        closing, abs=ROUNDING_AUD_M
    )


def test_each_period_opens_where_the_last_one_closed() -> None:
    for prior, period in pairwise(PERIODS):
        assert cash_flow(period, "net_debt_excluding_leases_opening") == cash_flow(
            prior, "net_debt_excluding_leases_closing"
        )


def test_cash_flow_net_debt_agrees_with_the_balance_sheet() -> None:
    assert cash_flow("FY24", "net_debt_excluding_leases_closing") == balance(
        "30 June 2024", "net_debt_excluding_leases"
    )
    assert cash_flow("1HY25", "net_debt_excluding_leases_closing") == balance(
        "31 December 2024", "net_debt_excluding_leases"
    )


def test_facilities_table_gives_the_net_debt_excluding_leases() -> None:
    limits = sum(
        net_debt(item)
        for item in (
            "facility_limit_revolving_credit_a",
            "facility_limit_revolving_loan_b",
            "facility_limit_revolving_loan_c",
        )
    )
    assert net_debt("facility_limit_total") == pytest.approx(limits, abs=ROUNDING_AUD_M)
    liabilities = (
        net_debt("drawn_revolving_credit_a")
        + net_debt("drawn_revolving_loan_b")
        + net_debt("drawn_revolving_loan_c")
        + net_debt("capitalised_borrowing_costs")
    )
    assert net_debt("total_interest_bearing_liabilities") == pytest.approx(
        liabilities, abs=ROUNDING_AUD_M
    )
    excluding_leases = net_debt("total_interest_bearing_liabilities") + net_debt(
        "cash_and_cash_equivalents"
    )
    assert net_debt("net_debt_excluding_leases") == pytest.approx(
        excluding_leases, abs=ROUNDING_AUD_M
    )


def test_reported_net_debt_including_leases_starts_the_bridge() -> None:
    reported = net_debt("net_debt_excluding_leases") + net_debt("lease_liabilities")
    assert net_debt("reported_net_debt_including_leases") == pytest.approx(
        reported, abs=ROUNDING_AUD_M
    )
    assert net_debt("reported_net_debt_including_leases") == balance(
        "31 December 2024", "net_debt_including_leases"
    )


def test_net_debt_bridge_reaches_the_adjusted_figure_in_the_valuation() -> None:
    bridge = (
        net_debt("reported_net_debt_including_leases")
        + net_debt("adjustment_capitalised_borrowing_costs")
        + net_debt("adjustment_interim_dividend_paid_11_march_2025")
    )
    assert bridge == pytest.approx(ADJUSTED_NET_DEBT_AUD_M, abs=ROUNDING_AUD_M)
    assert net_debt("adjusted_net_debt") == pytest.approx(ADJUSTED_NET_DEBT_AUD_M)
    summary = {
        r["case"]: float(r["value"])
        for r in load_rows(DATA / "valuation_summary.csv")
        if r["item"] == "adjusted_net_debt"
    }
    assert summary == {"low": ADJUSTED_NET_DEBT_AUD_M, "high": ADJUSTED_NET_DEBT_AUD_M}

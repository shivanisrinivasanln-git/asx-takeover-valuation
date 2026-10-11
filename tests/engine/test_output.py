"""valuation.json: every key is listed, units match key names, and values tie to the engine."""

import json
import math
from dataclasses import replace
from pathlib import Path

import pytest

from valuation.inputs import load_inputs
from valuation.output import (
    build_valuation,
    unit_for_key,
    valuation_date_label,
    write_valuation_json,
)
from valuation.sensitivity import base_value_per_share_aud

ROOT = Path(__file__).resolve().parents[2]

CASES = ("low", "mid", "high")
DCF_STEMS = (
    "dcf_discount_rate_pct",
    "dcf_present_value_of_cash_flows_aud_m",
    "dcf_terminal_value_aud_m",
    "dcf_present_value_of_terminal_value_aud_m",
    "dcf_terminal_value_share_of_operations_pct",
    "dcf_business_operations_value_aud_m",
    "dcf_enterprise_value_aud_m",
    "dcf_equity_value_aud_m",
    "dcf_diluted_shares_m",
    "dcf_value_per_share_aud",
)
MULTIPLE_STEMS = (
    "multiple_x",
    "business_operations_value_aud_m",
    "enterprise_value_aud_m",
    "equity_value_aud_m",
    "diluted_shares_m",
    "value_per_share_aud",
)

EXPECTED_KEYS = (
    {"dcf_terminal_growth_pct"}
    | {f"{stem}_{case}" for stem in DCF_STEMS for case in CASES}
    | {
        f"{method}_{measure}_{stem}"
        for method in ("trading", "precedent")
        for measure in ("ebitda", "ebita")
        for stem in ("earnings_aud_m", "control_premium_pct")
    }
    | {
        f"{method}_{measure}_{stem}_{case}"
        for method in ("trading", "precedent")
        for measure in ("ebitda", "ebita")
        for stem in MULTIPLE_STEMS
        for case in CASES
    }
    | {
        "method_weight_dcf_pct",
        "method_weight_trading_pct",
        "method_weight_precedent_pct",
        "preferred_dcf_value_per_share_aud",
        "preferred_trading_value_per_share_aud",
        "preferred_precedent_value_per_share_aud",
        "combined_value_per_share_aud_low",
        "preferred_value_per_share_aud",
        "combined_value_per_share_aud_high",
    }
    | {
        "wacc_pct_low",
        "wacc_pct_high",
        "wacc_at_expert_risk_free_pct_low",
        "wacc_at_expert_risk_free_pct_high",
        "expert_business_operations_value_aud_m_low",
        "expert_business_operations_value_aud_m_high",
        "expert_value_per_share_aud_low",
        "expert_value_per_share_aud_high",
        "expert_value_per_share_aud_mid",
        "offer_price_aud",
        "undisturbed_share_price_aud",
        "offer_premium_to_undisturbed_pct",
        "adjusted_net_debt_aud_m",
        "other_assets_and_liabilities_aud_m",
    }
)

FORECAST_FIELDS = {
    "year",
    "period",
    "revenue_aud_m",
    "ebitda_aud_m",
    "ebitda_margin_pct",
    "corporate_cost_saving_aud_m",
    "depreciation_aud_m",
    "tax_aud_m",
    "capex_aud_m",
    "working_capital_increase_aud_m",
    "agent_dividends_aud_m",
    "free_cash_flow_aud_m",
    "discount_time_years",
    "discount_factor_at_base_rate",
    "present_value_at_base_rate_aud_m",
}


@pytest.fixture(scope="module")
def valuation() -> dict[str, object]:
    return build_valuation(load_inputs(ROOT))


def values_of(valuation: dict[str, object]) -> dict[str, dict[str, object]]:
    scalars = valuation["values"]
    assert isinstance(scalars, dict)
    return scalars


def number(valuation: dict[str, object], key: str) -> float:
    value = values_of(valuation)[key]["value"]
    assert isinstance(value, float)
    return value


def test_the_scalar_keys_are_exactly_the_expected_list(valuation: dict[str, object]) -> None:
    keys = set(values_of(valuation))
    assert sorted(keys - EXPECTED_KEYS) == [], "keys the schema does not list"
    assert sorted(EXPECTED_KEYS - keys) == [], "listed keys that are missing"


def test_every_value_is_a_finite_number_with_the_unit_its_name_promises(
    valuation: dict[str, object],
) -> None:
    for key, entry in values_of(valuation).items():
        assert set(entry) == {"value", "unit"}, key
        assert isinstance(entry["value"], float), key
        assert math.isfinite(entry["value"]), key
        assert entry["unit"] == unit_for_key(key), key


def test_a_key_without_a_unit_suffix_is_rejected() -> None:
    with pytest.raises(ValueError, match="unit suffix"):
        unit_for_key("dcf_value")
    assert unit_for_key("dcf_value_per_share_aud_low") == "aud"
    assert unit_for_key("dcf_business_operations_value_aud_m_high") == "aud_m"
    assert unit_for_key("dcf_diluted_shares_m_mid") == "shares_m"


def test_the_mid_case_value_per_share_equals_the_sensitivity_base_value(
    valuation: dict[str, object],
) -> None:
    inputs = load_inputs(ROOT)
    assert number(valuation, "dcf_value_per_share_aud_mid") == pytest.approx(
        base_value_per_share_aud(inputs), rel=1e-12
    )


def test_the_low_case_is_below_the_high_case_for_every_method(valuation: dict[str, object]) -> None:
    for stem in ("dcf", "trading_ebitda", "trading_ebita", "precedent_ebitda", "precedent_ebita"):
        low = number(valuation, f"{stem}_value_per_share_aud_low")
        mid = number(valuation, f"{stem}_value_per_share_aud_mid")
        high = number(valuation, f"{stem}_value_per_share_aud_high")
        assert low < mid < high, stem


def test_the_multiples_mid_case_is_the_midpoint_multiple_on_the_average_share_count(
    valuation: dict[str, object],
) -> None:
    for method in ("trading", "precedent"):
        for measure in ("ebitda", "ebita"):
            stem = f"{method}_{measure}"
            low = number(valuation, f"{stem}_multiple_x_low")
            mid = number(valuation, f"{stem}_multiple_x_mid")
            high = number(valuation, f"{stem}_multiple_x_high")
            assert mid == pytest.approx((low + high) / 2, rel=1e-12)
            shares = number(valuation, f"{stem}_diluted_shares_m_mid")
            assert shares == pytest.approx(number(valuation, "dcf_diluted_shares_m_mid"), rel=1e-12)
            equity = number(valuation, f"{stem}_equity_value_aud_m_mid")
            assert number(valuation, f"{stem}_value_per_share_aud_mid") == pytest.approx(
                equity / shares, rel=1e-12
            )


def test_the_combined_range_is_the_weighted_sum_of_the_method_values(
    valuation: dict[str, object],
) -> None:
    weights = {
        method: number(valuation, f"method_weight_{method}_pct")
        for method in ("dcf", "trading", "precedent")
    }
    assert sum(weights.values()) == pytest.approx(100.0, rel=1e-12)
    stems = {"dcf": "dcf", "trading": "trading_ebitda", "precedent": "precedent_ebitda"}
    for case, key in (
        ("low", "combined_value_per_share_aud_low"),
        ("mid", "preferred_value_per_share_aud"),
        ("high", "combined_value_per_share_aud_high"),
    ):
        expected = sum(
            weights[method] * number(valuation, f"{stems[method]}_value_per_share_aud_{case}")
            for method in weights
        )
        assert number(valuation, key) == pytest.approx(expected / 100, rel=1e-12), case
    for method, stem in stems.items():
        assert number(valuation, f"preferred_{method}_value_per_share_aud") == number(
            valuation, f"{stem}_value_per_share_aud_mid"
        )


def test_my_preferred_value_and_range_on_my_inputs(valuation: dict[str, object]) -> None:
    # Weights of 50, 25 and 25 on the base case give A$4.21 and A$3.71 to A$4.75 a share.
    assert round(number(valuation, "preferred_value_per_share_aud"), 2) == 4.21
    assert round(number(valuation, "combined_value_per_share_aud_low"), 2) == 3.71
    assert round(number(valuation, "combined_value_per_share_aud_high"), 2) == 4.75


def test_the_equity_bridge_adds_up_in_every_dcf_case(valuation: dict[str, object]) -> None:
    for case in CASES:
        enterprise = number(valuation, f"dcf_enterprise_value_aud_m_{case}")
        equity = number(valuation, f"dcf_equity_value_aud_m_{case}")
        shares = number(valuation, f"dcf_diluted_shares_m_{case}")
        per_share = number(valuation, f"dcf_value_per_share_aud_{case}")
        net_debt = number(valuation, "adjusted_net_debt_aud_m")
        assert equity == pytest.approx(enterprise - net_debt, rel=1e-12)
        assert per_share == pytest.approx(equity / shares, rel=1e-12)
        operations = number(valuation, f"dcf_business_operations_value_aud_m_{case}")
        assert enterprise == pytest.approx(
            operations + number(valuation, "other_assets_and_liabilities_aud_m"), rel=1e-12
        )
        flows = number(valuation, f"dcf_present_value_of_cash_flows_aud_m_{case}")
        terminal = number(valuation, f"dcf_present_value_of_terminal_value_aud_m_{case}")
        assert operations == pytest.approx(flows + terminal, rel=1e-12)


def test_the_expert_reference_values_are_the_printed_range_and_its_midpoint(
    valuation: dict[str, object],
) -> None:
    assert number(valuation, "expert_value_per_share_aud_low") == 4.06
    assert number(valuation, "expert_value_per_share_aud_high") == 4.46
    assert number(valuation, "expert_value_per_share_aud_mid") == pytest.approx(4.26)
    assert number(valuation, "offer_price_aud") == 4.43
    assert number(valuation, "offer_premium_to_undisturbed_pct") == pytest.approx(
        (4.43 / 3.12 - 1) * 100
    )


def test_the_football_field_rows_point_at_keys_that_exist(valuation: dict[str, object]) -> None:
    rows = valuation["football_field"]
    assert isinstance(rows, list)
    assert [row["id"] for row in rows] == ["dcf", "trading", "precedent", "combined", "expert"]
    for row in rows:
        assert row["low_key"] in values_of(valuation), row
        assert row["high_key"] in values_of(valuation), row
        assert number(valuation, row["low_key"]) < number(valuation, row["high_key"]), row
        if row["id"] == "expert":
            assert row["preferred_key"] is None
        else:
            low = number(valuation, row["low_key"])
            high = number(valuation, row["high_key"])
            assert low < number(valuation, row["preferred_key"]) < high, row


def test_the_forecast_table_has_the_stub_then_ten_years_and_discounts_to_the_dcf(
    valuation: dict[str, object],
) -> None:
    forecast = valuation["forecast"]
    assert isinstance(forecast, dict)
    rows = forecast["rows"]
    assert [row["year"] for row in rows] == list(range(11))
    assert [rows[0]["period"], rows[1]["period"], rows[10]["period"]] == [
        "FY2025 second half",
        "FY2026",
        "FY2035",
    ]
    assert all(set(row) == FORECAST_FIELDS for row in rows)
    present_value = sum(row["present_value_at_base_rate_aud_m"] for row in rows)
    assert present_value == pytest.approx(
        number(valuation, "dcf_present_value_of_cash_flows_aud_m_mid"), rel=1e-12
    )


def test_the_sensitivity_table_is_five_by_five_with_the_base_cell_marked(
    valuation: dict[str, object],
) -> None:
    grid = valuation["sensitivity"]
    assert isinstance(grid, dict)
    cells = grid["value_per_share_aud"]
    assert len(cells) == 5
    assert all(len(row) == 5 for row in cells)
    assert cells[grid["base_row"]][grid["base_column"]] == pytest.approx(
        number(valuation, "dcf_value_per_share_aud_mid"), rel=1e-12
    )


def test_the_writer_produces_json_that_reads_back_to_the_same_numbers(tmp_path: Path) -> None:
    inputs = load_inputs(ROOT)
    path = tmp_path / "out" / "valuation.json"
    write_valuation_json(inputs, path)
    assert json.loads(path.read_text(encoding="utf-8")) == build_valuation(inputs)


def test_the_valuation_date_label_comes_from_the_input(valuation: dict[str, object]) -> None:
    meta = valuation["meta"]
    assert isinstance(meta, dict)
    assert meta["valuation_date"] == "31 December 2024"
    inputs = load_inputs(ROOT)
    moved = replace(inputs.assumptions["valuation_date_ymd"], value=(2025.0, 6.0, 30.0))
    changed = replace(inputs, assumptions={**inputs.assumptions, "valuation_date_ymd": moved})
    assert valuation_date_label(changed) == "30 June 2025"

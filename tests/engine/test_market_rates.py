"""The RBA rates I use for the valuation date, 30 May 2025, as read from the RBA's own tables."""

from pathlib import Path

import pytest

from valuation.extracted import load_rows

ROOT = Path(__file__).resolve().parents[2]
RATES_FILE = ROOT / "data" / "extracted" / "market_rates_30_may_2025.csv"


def rates_by_item() -> dict[str, dict[str, str]]:
    return {row["item"]: row for row in load_rows(RATES_FILE)}


@pytest.mark.parametrize(
    ("item", "expected_value"),
    [
        ("risk_free_rate_10y_pct", 4.249),
        ("aud_to_eur", 0.5670),
        ("aud_to_gbp", 0.4775),
    ],
)
def test_rate_matches_the_rba_table(item: str, expected_value: float) -> None:
    assert float(rates_by_item()[item]["value"]) == pytest.approx(expected_value, abs=1e-9)


def test_every_rate_is_dated_at_the_valuation_date() -> None:
    assert {row["as_at"] for row in rates_by_item().values()} == {"30 May 2025"}


def test_every_rate_carries_the_rba_credit() -> None:
    # CC BY 4.0 requires attribution, and the RBA asks for "Source: RBA [year]".
    for row in rates_by_item().values():
        assert "Source: RBA 2026" in row["source"]
        assert "CC BY 4.0" in row["source"]

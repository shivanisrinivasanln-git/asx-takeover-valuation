"""The equity bridge reproduces the expert's bridge from its own enterprise value (booklet p. 131).

Low: 2,775.0 - 7.6 = 2,767.4; less 187.0 = 2,580.4; over 635.507752 million shares = A$4.0604.
High: 3,025.0 - 7.6 = 3,017.4; less 187.0 = 2,830.4; over 634.449894 million shares = A$4.4612
(A$4.4615 on the printed 634.4 million).
"""

from pathlib import Path
from typing import Literal

import pytest

from valuation.bridge import adjusted_net_debt_aud_m, diluted_shares_m, equity_bridge
from valuation.inputs import load_inputs

ROOT = Path(__file__).resolve().parents[2]
PRINTED_PER_SHARE_ROUNDING_AUD = 0.005


def test_adjusted_net_debt_is_the_expert_figure() -> None:
    assert adjusted_net_debt_aud_m(load_inputs(ROOT)) == pytest.approx(187.0, abs=1e-9)


def test_diluted_shares_match_the_build_from_the_booklet() -> None:
    inputs = load_inputs(ROOT)
    assert diluted_shares_m(inputs, "low") == pytest.approx(635.507752, abs=1e-9)
    assert diluted_shares_m(inputs, "high") == pytest.approx(634.449894, abs=1e-9)
    assert diluted_shares_m(inputs, "mid") == pytest.approx((635.507752 + 634.449894) / 2, abs=1e-9)


def test_low_end_bridge_reproduces_the_expert_figures() -> None:
    bridge = equity_bridge(load_inputs(ROOT), 2775.0, "low")
    assert bridge.enterprise_value_aud_m == pytest.approx(2767.4, abs=1e-9)
    assert bridge.equity_value_aud_m == pytest.approx(2580.4, abs=1e-9)
    assert bridge.value_per_share_aud == pytest.approx(2580.4 / 635.507752, rel=1e-12)
    assert round(bridge.value_per_share_aud, 2) == 4.06


def test_high_end_bridge_reproduces_the_expert_figures() -> None:
    bridge = equity_bridge(load_inputs(ROOT), 3025.0, "high")
    assert bridge.enterprise_value_aud_m == pytest.approx(3017.4, abs=1e-9)
    assert bridge.equity_value_aud_m == pytest.approx(2830.4, abs=1e-9)
    assert bridge.value_per_share_aud == pytest.approx(2830.4 / 634.449894, rel=1e-12)
    assert round(bridge.value_per_share_aud, 2) == 4.46


def test_the_bridge_agrees_with_the_transcribed_valuation_summary() -> None:
    rows = {
        (r["item"], r["case"]): float(r["value"])
        for r in load_inputs(ROOT).tables["valuation_summary"]
    }
    cases: list[tuple[Literal["low", "high"], float]] = [("low", 2775.0), ("high", 3025.0)]
    for case, operations in cases:
        bridge = equity_bridge(load_inputs(ROOT), operations, case)
        assert bridge.enterprise_value_aud_m == pytest.approx(
            rows[("enterprise_value", case)], abs=0.05
        )
        assert bridge.equity_value_aud_m == pytest.approx(rows[("equity_value", case)], abs=0.05)
        assert bridge.value_per_share_aud == pytest.approx(
            rows[("value_per_share", case)], abs=PRINTED_PER_SHARE_ROUNDING_AUD
        )

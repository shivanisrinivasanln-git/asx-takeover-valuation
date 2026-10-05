"""From the value of business operations to the equity value per share.

Business operations value, plus other assets and liabilities, is the enterprise value. Less
adjusted net debt, it is the equity value, and divided by diluted shares, the value per share.
Money is A$ millions, shares are millions and per-share values are A$. Nothing is rounded here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from valuation import finance
from valuation.inputs import Inputs

Case = Literal["low", "high", "mid"]


@dataclass(frozen=True)
class EquityBridge:
    business_operations_aud_m: float
    other_assets_and_liabilities_aud_m: float
    enterprise_value_aud_m: float
    adjusted_net_debt_aud_m: float
    equity_value_aud_m: float
    diluted_shares_m: float
    value_per_share_aud: float


def adjusted_net_debt_aud_m(inputs: Inputs) -> float:
    """Reported net debt including leases, plus the two adjustments the expert makes."""
    return (
        inputs.number("reported_net_debt_including_leases_aud_m")
        + inputs.number("net_debt_adjustment_capitalised_borrowing_costs_aud_m")
        + inputs.number("net_debt_adjustment_interim_dividend_aud_m")
    )


def diluted_shares_m(inputs: Inputs, case: Case) -> float:
    """Ordinary shares plus rights that vest or are cash settled, less treasury shares.

    Fewer rights vest at the high end, so the share count is lower there.
    "Mid" is the plain average of the two, my choice because the booklet gives no middle case.
    """
    fixed = (
        inputs.number("ordinary_shares_on_issue_m")
        + inputs.number("share_rights_cash_settled_m")
        - inputs.number("treasury_shares_m")
    )
    low = fixed + inputs.number("share_rights_vesting_low_m")
    high = fixed + inputs.number("share_rights_vesting_high_m")
    return {"low": low, "high": high, "mid": (low + high) / 2}[case]


def equity_bridge(inputs: Inputs, business_operations_aud_m: float, case: Case) -> EquityBridge:
    other = inputs.number("other_assets_and_liabilities_aud_m")
    net_debt = adjusted_net_debt_aud_m(inputs)
    shares = diluted_shares_m(inputs, case)
    enterprise_value = business_operations_aud_m + other
    return EquityBridge(
        business_operations_aud_m=business_operations_aud_m,
        other_assets_and_liabilities_aud_m=other,
        enterprise_value_aud_m=enterprise_value,
        adjusted_net_debt_aud_m=net_debt,
        equity_value_aud_m=enterprise_value - net_debt,
        diluted_shares_m=shares,
        value_per_share_aud=finance.equity_value_per_share_aud(enterprise_value, net_debt, shares),
    )

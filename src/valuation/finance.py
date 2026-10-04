"""Basic valuation arithmetic used by every method.

Rates are percentages (4.0 means 4.0%), money is A$ millions, and per-share
values are A$. Nothing is rounded here; rounding happens only when a number is
displayed.
"""

from __future__ import annotations


def capitalised_earnings_value_aud_m(maintainable_ebitda_aud_m: float, multiple_x: float) -> float:
    """Enterprise value from maintainable EBITDA and a control-basis multiple."""
    return maintainable_ebitda_aud_m * multiple_x


def equity_value_per_share_aud(
    enterprise_value_aud_m: float, net_debt_aud_m: float, diluted_shares_m: float
) -> float:
    """Enterprise value less net debt, divided by diluted shares (millions)."""
    if diluted_shares_m <= 0:
        raise ValueError("diluted_shares_m must be positive")
    return (enterprise_value_aud_m - net_debt_aud_m) / diluted_shares_m


def cost_of_equity_pct(
    risk_free_rate_pct: float, beta: float, market_risk_premium_pct: float
) -> float:
    """Capital asset pricing model: risk-free rate plus beta times the premium."""
    return risk_free_rate_pct + beta * market_risk_premium_pct


def after_tax_cost_of_debt_pct(pre_tax_cost_of_debt_pct: float, tax_rate_pct: float) -> float:
    """Pre-tax cost of debt reduced by the tax shield."""
    return pre_tax_cost_of_debt_pct * (1 - tax_rate_pct / 100)


def wacc_pct(
    equity_cost_pct: float, debt_cost_after_tax_pct: float, equity_weight_pct: float
) -> float:
    """Weighted average cost of capital from the equity weight; debt takes the rest."""
    if not 0 <= equity_weight_pct <= 100:
        raise ValueError("equity_weight_pct must be between 0 and 100")
    equity_weight = equity_weight_pct / 100
    return equity_weight * equity_cost_pct + (1 - equity_weight) * debt_cost_after_tax_pct


def growing_perpetuity_value_aud_m(
    next_year_cash_flow_aud_m: float, discount_rate_pct: float, growth_rate_pct: float
) -> float:
    """Value of a cash flow growing for ever at a constant rate (Gordon growth)."""
    if discount_rate_pct <= growth_rate_pct:
        raise ValueError("discount_rate_pct must exceed growth_rate_pct")
    return next_year_cash_flow_aud_m / ((discount_rate_pct - growth_rate_pct) / 100)


def offer_premium_pct(offer_price_aud: float, undisturbed_price_aud: float) -> float:
    """Premium of the offer to the undisturbed price, as a percentage."""
    if undisturbed_price_aud <= 0:
        raise ValueError("undisturbed_price_aud must be positive")
    return (offer_price_aud / undisturbed_price_aud - 1) * 100


def price_with_premium_aud(undisturbed_price_aud: float, premium_pct: float) -> float:
    """Undisturbed price grossed up by a control premium."""
    return undisturbed_price_aud * (1 + premium_pct / 100)

"""How the site writes numbers: A$ amounts, signed changes and percentages.

Rounding happens here and only here, from the engine's full-precision values. A negative number
uses the true minus sign (U+2212), chosen on 4 October 2026 (docs/DECISIONS.md).
"""

from __future__ import annotations

MINUS = chr(0x2212)


def number(value: float, places: int = 2) -> str:
    """A number with thousands separators and a true minus sign, such as 2,401.07."""
    text = f"{abs(round(value, places)):,.{places}f}"
    # A value that rounds to zero is written without a sign.
    negative = value < 0 and float(text.replace(",", "")) != 0
    return f"{MINUS}{text}" if negative else text


def signed(value: float, places: int = 2) -> str:
    """A change with an explicit sign, a plus or a true minus, or 0.00."""
    text = number(value, places)
    if text.startswith(MINUS) or float(text.replace(",", "")) == 0:
        return text
    return f"+{text}"


def aud(value: float, places: int = 2) -> str:
    """An amount in A$ per share, such as A$4.21."""
    text = number(value, places)
    return f"{MINUS}A${text[1:]}" if text.startswith(MINUS) else f"A${text}"


def aud_signed(value: float, places: int = 2) -> str:
    """A signed change in A$ per share, such as +A$0.27."""
    text = signed(value, places)
    if text[0] in ("+", MINUS):
        return f"{text[0]}A${text[1:]}"
    return f"A${text}"


def percent(value: float, places: int = 1) -> str:
    """A rate or share written with a percent sign, such as 10.0%."""
    return f"{number(value, places)}%"

"""Checks on the formulas of the Excel model: no typed-in numbers, and every name is defined.

A formula may contain 0, 1, 2 and 100 only: a unit conversion (percent to a fraction), a step of
one year, or an average of two. Any other number belongs on the Assumptions sheet.
"""

from __future__ import annotations

import re

from openpyxl.formula import Tokenizer
from openpyxl.formula.tokenizer import Token

ALLOWED_CONSTANTS = frozenset({"0", "1", "2", "100"})
CELL_REFERENCE = re.compile(r"^\$?[A-Z]{1,3}\$?\d+(:\$?[A-Z]{1,3}\$?\d+)?$")


def _operands(formula: str) -> list[Token]:
    return [token for token in Tokenizer(formula).items if token.type == Token.OPERAND]


def numeric_constants(formula: str) -> list[str]:
    """Numbers typed into a formula, other than the allowed ones."""
    return [
        token.value
        for token in _operands(formula)
        if token.subtype == Token.NUMBER and token.value not in ALLOWED_CONSTANTS
    ]


def names_used(formula: str) -> set[str]:
    """Defined names a formula reads: operands that are neither cell references nor sheet refs."""
    return {
        token.value
        for token in _operands(formula)
        if token.subtype == Token.RANGE and not CELL_REFERENCE.match(token.value)
    }


def sheet_references(formula: str) -> list[str]:
    """Operands that point at another sheet by address, such as Assumptions!C5."""
    return [token.value for token in _operands(formula) if "!" in token.value]

"""The Summary sheet: the football field table, the reference prices and the discount rate range.

Every cell is a formula that reads another sheet's output by its `valuation.json` key, so the
sheet shows what the football field chart on the site draws.
"""

from __future__ import annotations

from openpyxl import Workbook
from openpyxl.cell.cell import Cell
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from valuation.output import FOOTBALL_FIELD_ROWS

SUMMARY_SHEET = "Summary"
NOTE_COLUMN = "F"
BOLD = Font(bold=True)
HEADING_FILL = PatternFill("solid", start_color="D9E1F2")
PER_SHARE = "0.00"
PERCENT = "0.00"
FIRST_ROW = 5


def _cell(sheet: Worksheet, ref: str) -> Cell:
    found = sheet[ref]
    if not isinstance(found, Cell):
        raise TypeError(f"{ref} is not a plain cell")
    return found


def _put(sheet: Worksheet, ref: str, value: object, number_format: str | None = None) -> None:
    cell = _cell(sheet, ref)
    cell.value = value  # type: ignore[assignment]
    if number_format:
        cell.number_format = number_format


def _heading(sheet: Worksheet, row: int, text: str) -> None:
    sheet[f"A{row}"] = text
    for column in range(1, 5):
        cell = sheet.cell(row, column)
        cell.font = BOLD
        cell.fill = HEADING_FILL


def add_summary_sheet(book: Workbook) -> dict[str, str]:
    """Add the Summary sheet; returns the cells of the outputs it defines, by valuation.json key."""
    sheet: Worksheet = book.create_sheet(SUMMARY_SHEET)
    sheet["A1"] = "Summary"
    sheet["A1"].font = Font(bold=True, size=14)
    sheet["A2"] = (
        "Value per share by method on the current inputs, with the offer and the expert's range."
    )
    sheet.column_dimensions["A"].width = 46
    sheet.column_dimensions["B"].width = 9
    for column in "CD":
        sheet.column_dimensions[column].width = 18
    sheet.column_dimensions[NOTE_COLUMN].width = 90

    _heading(sheet, FIRST_ROW - 1, "Value per share (A$)")
    _put(sheet, f"C{FIRST_ROW - 1}", "Low")
    _put(sheet, f"D{FIRST_ROW - 1}", "High")
    for offset, (_, label, low_key, high_key) in enumerate(FOOTBALL_FIELD_ROWS):
        row = FIRST_ROW + offset
        sheet[f"A{row}"] = label
        sheet[f"B{row}"] = "A$"
        _put(sheet, f"C{row}", f"={low_key}", PER_SHARE)
        _put(sheet, f"D{row}", f"={high_key}", PER_SHARE)
        sheet[f"{NOTE_COLUMN}{row}"] = "From the method's own sheet; the same figures as the chart."

    reference = FIRST_ROW + len(FOOTBALL_FIELD_ROWS) + 1
    _heading(sheet, reference, "Reference prices")
    rows = {
        "offer": (
            reference + 1,
            "Offer price",
            "A$",
            "=offer_price_aud",
            PER_SHARE,
            "Cash per share.",
        ),
        "undisturbed": (
            reference + 2,
            "Undisturbed share price",
            "A$",
            "=undisturbed_share_price_aud",
            PER_SHARE,
            "Close on the last trading day before the original proposal.",
        ),
        "premium": (
            reference + 3,
            "Offer premium to the undisturbed price",
            "%",
            "=(offer_price_aud/undisturbed_share_price_aud-1)*100",
            PERCENT,
            "Offer over undisturbed price, less one.",
        ),
        "midpoint": (
            reference + 4,
            "Midpoint of the expert's range",
            "A$",
            "=(expert_value_per_share_aud_low+expert_value_per_share_aud_high)/2",
            PER_SHARE,
            "My midpoint of the printed range. The expert published a range only.",
        ),
    }
    for row, label, unit, formula, number_format, note in rows.values():
        sheet[f"A{row}"] = label
        sheet[f"B{row}"] = unit
        _put(sheet, f"C{row}", formula, number_format)
        sheet[f"{NOTE_COLUMN}{row}"] = note

    discount = reference + 6
    _heading(sheet, discount, "Discount rate range (%)")
    _put(sheet, f"C{discount}", "Low")
    _put(sheet, f"D{discount}", "High")
    rates = (
        (
            "Adopted range (my input)",
            "=discount_rate_low_pct",
            "=discount_rate_high_pct",
            "The range the DCF discounts at. It is an input, not the build below.",
        ),
        (
            "Build at my risk-free rate",
            "=wacc_pct_low",
            "=wacc_pct_high",
            "WACC from the beta and gearing ranges at my risk-free rate (DCF sheet).",
        ),
        (
            "Build at the expert's risk-free rate",
            "=wacc_at_expert_risk_free_pct_low",
            "=wacc_at_expert_risk_free_pct_high",
            "The same build at the expert's risk-free rate (DCF sheet).",
        ),
    )
    for offset, (label, low, high, note) in enumerate(rates):
        row = discount + 1 + offset
        sheet[f"A{row}"] = label
        sheet[f"B{row}"] = "%"
        _put(sheet, f"C{row}", low, PERCENT)
        _put(sheet, f"D{row}", high, PERCENT)
        sheet[f"{NOTE_COLUMN}{row}"] = note
    return {
        "offer_premium_to_undisturbed_pct": f"{SUMMARY_SHEET}!$C${rows['premium'][0]}",
        "expert_value_per_share_aud_mid": f"{SUMMARY_SHEET}!$C${rows['midpoint'][0]}",
    }

"""The Summary sheet: the football field table, how the methods combine, the reference prices
and the discount rate range.

Every cell is a formula that reads another sheet's output by its `valuation.json` key, so the
sheet shows what the football field chart on the site draws. The combination block is where my
weighted range and preferred value are calculated.
"""

from __future__ import annotations

from openpyxl import Workbook
from openpyxl.cell.cell import Cell
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from valuation.output import FOOTBALL_FIELD_ROWS, PREFERRED_KEY_BY_ROW

SUMMARY_SHEET = "Summary"
NOTE_COLUMN = "G"
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
    for column in range(1, 7):
        cell = sheet.cell(row, column)
        cell.font = BOLD
        cell.fill = HEADING_FILL


# (method, label, weight name, low name, high name, preferred (mid) name, preferred output key)
METHOD_ROWS = (
    (
        "dcf",
        "Discounted cash flow",
        "method_weight_dcf_pct",
        "dcf_value_per_share_aud",
        "preferred_dcf_value_per_share_aud",
    ),
    (
        "trading",
        "Trading comparables (EBITDA multiple, with the control premium)",
        "method_weight_trading_pct",
        "trading_ebitda_value_per_share_aud",
        "preferred_trading_value_per_share_aud",
    ),
    (
        "precedent",
        "Precedent transactions (EBITDA multiple)",
        "method_weight_precedent_pct",
        "precedent_ebitda_value_per_share_aud",
        "preferred_precedent_value_per_share_aud",
    ),
)


def _combination_block(sheet: Worksheet, first_row: int) -> dict[str, str]:
    """Weights by method and the weighted low, high and preferred value per share."""
    _heading(sheet, first_row, "How the methods combine (A$ per share)")
    for column, title in zip("CDEF", ("Weight (%)", "Low", "High", "Preferred"), strict=True):
        _put(sheet, f"{column}{first_row}", title)
    first = first_row + 1
    last = first + len(METHOD_ROWS) - 1
    outputs: dict[str, str] = {}
    for offset, (_, label, weight, stem, preferred_key) in enumerate(METHOD_ROWS):
        row = first + offset
        sheet[f"A{row}"] = label
        sheet[f"B{row}"] = "A$"
        _put(sheet, f"C{row}", f"={weight}", PERCENT)
        _put(sheet, f"D{row}", f"={stem}_low", PER_SHARE)
        _put(sheet, f"E{row}", f"={stem}_high", PER_SHARE)
        _put(sheet, f"F{row}", f"={stem}_mid", PER_SHARE)
        sheet[f"{NOTE_COLUMN}{row}"] = (
            "The weight is my input. The preferred value is the method's mid case."
        )
        outputs[preferred_key] = f"{SUMMARY_SHEET}!$F${row}"
    total = last + 1
    sheet[f"A{total}"] = "My combined range"
    sheet[f"B{total}"] = "A$"
    _put(sheet, f"C{total}", f"=SUM(C{first}:C{last})", PERCENT)
    for column in "DEF":
        terms = "+".join(f"$C{row}*{column}{row}" for row in range(first, last + 1))
        _put(sheet, f"{column}{total}", f"=({terms})/100", PER_SHARE)
    sheet[f"{NOTE_COLUMN}{total}"] = (
        "Each column is the weights times the method values, over 100. The weights must add to 100."
    )
    for column in "ABCDEF":
        sheet[f"{column}{total}"].font = BOLD
    outputs["combined_value_per_share_aud_low"] = f"{SUMMARY_SHEET}!$D${total}"
    outputs["combined_value_per_share_aud_high"] = f"{SUMMARY_SHEET}!$E${total}"
    outputs["preferred_value_per_share_aud"] = f"{SUMMARY_SHEET}!$F${total}"
    return outputs


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
    for column in "CDEF":
        sheet.column_dimensions[column].width = 18
    sheet.column_dimensions[NOTE_COLUMN].width = 90

    _heading(sheet, FIRST_ROW - 1, "Value per share (A$)")
    _put(sheet, f"C{FIRST_ROW - 1}", "Low")
    _put(sheet, f"D{FIRST_ROW - 1}", "High")
    _put(sheet, f"E{FIRST_ROW - 1}", "Preferred")
    for offset, (row_id, label, low_key, high_key) in enumerate(FOOTBALL_FIELD_ROWS):
        row = FIRST_ROW + offset
        sheet[f"A{row}"] = label
        sheet[f"B{row}"] = "A$"
        _put(sheet, f"C{row}", f"={low_key}", PER_SHARE)
        _put(sheet, f"D{row}", f"={high_key}", PER_SHARE)
        preferred_key = PREFERRED_KEY_BY_ROW[row_id]
        if preferred_key is not None:
            _put(sheet, f"E{row}", f"={preferred_key}", PER_SHARE)
        sheet[f"{NOTE_COLUMN}{row}"] = (
            "From the method's own sheet and the combination below; the same figures as the chart."
            if preferred_key is not None
            else "The printed range. The expert gave a range only, so there is no preferred value."
        )

    combination = FIRST_ROW + len(FOOTBALL_FIELD_ROWS) + 1
    outputs = _combination_block(sheet, combination)
    reference = combination + len(METHOD_ROWS) + 3
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
    outputs.update(
        {
            "offer_premium_to_undisturbed_pct": f"{SUMMARY_SHEET}!$C${rows['premium'][0]}",
            "expert_value_per_share_aud_mid": f"{SUMMARY_SHEET}!$C${rows['midpoint'][0]}",
        }
    )
    return outputs

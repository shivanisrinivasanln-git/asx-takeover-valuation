import copy
from collections.abc import Mapping
from pathlib import Path

import pytest
import yaml

from valuation.assumptions import AssumptionsError, load_assumptions, parse_assumptions

VALID_ENTRY = {
    "value": 4.3,
    "unit": "pct",
    "source": "Domain scheme booklet, Grant Samuel report",
    "location": "booklet p. 139",
    "as_at": "30 May 2025",
    "note": "Expert's spot 10-year Commonwealth bond yield",
}


def dump(entries: Mapping[str, object]) -> str:
    return yaml.safe_dump(entries, sort_keys=False)


def test_valid_file_loads_with_full_precision_and_defaults() -> None:
    assumptions = parse_assumptions(dump({"risk_free_rate_pct": VALID_ENTRY}))
    entry = assumptions["risk_free_rate_pct"]
    assert entry.value == 4.3
    assert entry.unit == "pct"
    assert entry.location == "booklet p. 139"
    assert entry.judgement is False


def test_series_values_and_judgement_flag_are_accepted() -> None:
    entry = {**VALID_ENTRY, "value": [1, 2.5, 3], "judgement": True}
    loaded = parse_assumptions(dump({"revenue_growth_pct": entry}))["revenue_growth_pct"]
    assert loaded.value == (1.0, 2.5, 3.0)
    assert loaded.judgement is True


def test_empty_file_has_no_assumptions() -> None:
    assert parse_assumptions("") == {}
    assert parse_assumptions("# only a comment\n") == {}


@pytest.mark.parametrize("field", ["value", "unit", "source", "location", "as_at", "note"])
def test_each_missing_field_is_rejected(field: str) -> None:
    entry = copy.deepcopy(VALID_ENTRY)
    del entry[field]
    with pytest.raises(AssumptionsError, match=f"risk_free_rate_pct: missing '{field}'"):
        parse_assumptions(dump({"risk_free_rate_pct": entry}))


@pytest.mark.parametrize(
    ("field", "bad_value", "message"),
    [
        ("source", "  ", "'source' must be a non-empty string"),
        ("unit", 5, "'unit' must be a non-empty string"),
        ("value", True, "'value' must be a number"),
        ("value", "4.3", "'value' must be a number"),
        ("value", [], "'value' must be a number"),
        ("value", [1, "x"], "'value' must be a number"),
        ("as_at", "2025-05-30", "'as_at' must be a date"),
        ("as_at", "31 February 2025", "'as_at' must be a date"),
        ("judgement", "yes", "'judgement' must be true or false"),
    ],
)
def test_bad_field_values_are_rejected(field: str, bad_value: object, message: str) -> None:
    entry = {**VALID_ENTRY, field: bad_value}
    with pytest.raises(AssumptionsError, match=message):
        parse_assumptions(dump({"risk_free_rate_pct": entry}))


def test_unknown_field_is_rejected() -> None:
    entry = {**VALID_ENTRY, "comment": "extra"}
    with pytest.raises(AssumptionsError, match="unknown field 'comment'"):
        parse_assumptions(dump({"risk_free_rate_pct": entry}))


def test_bad_names_and_non_mapping_entries_are_rejected() -> None:
    with pytest.raises(AssumptionsError, match="lower-case words joined by _"):
        parse_assumptions(dump({"Risk Free Rate": VALID_ENTRY}))
    with pytest.raises(AssumptionsError, match="must be a mapping"):
        parse_assumptions("risk_free_rate_pct: 4.3\n")
    with pytest.raises(AssumptionsError, match="mapping of input names"):
        parse_assumptions("- a\n- b\n")


def test_duplicate_key_is_rejected() -> None:
    entry = "{value: 1, unit: pct, source: s, location: l, as_at: 1 May 2025, note: n}"
    text = f"risk_free_rate_pct: {entry}\nrisk_free_rate_pct: {entry}\n"
    with pytest.raises(AssumptionsError, match=r"duplicate key 'risk_free_rate_pct' \(line 2\)"):
        parse_assumptions(text)


def test_invalid_yaml_is_reported() -> None:
    with pytest.raises(AssumptionsError, match="not valid YAML"):
        parse_assumptions("key: [unclosed\n")


def test_every_problem_is_reported_at_once() -> None:
    entries = {
        "first_pct": {**VALID_ENTRY, "unit": ""},
        "second_pct": {k: v for k, v in VALID_ENTRY.items() if k != "note"},
    }
    with pytest.raises(AssumptionsError) as caught:
        parse_assumptions(dump(entries))
    message = str(caught.value)
    assert "first_pct: 'unit' must be a non-empty string" in message
    assert "second_pct: missing 'note'" in message


def test_load_assumptions_reads_a_file(tmp_path: Path) -> None:
    path = tmp_path / "assumptions.yaml"
    path.write_text(dump({"risk_free_rate_pct": VALID_ENTRY}), encoding="utf-8")
    assert load_assumptions(path)["risk_free_rate_pct"].value == 4.3

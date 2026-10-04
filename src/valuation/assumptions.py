"""Load and check `assumptions.yaml`, the single source of truth for valuation inputs.

Every entry must say where its value came from, so the site can show the source
next to the figure. The loader collects every problem in the file and raises one
error listing them, so I can fix a file in one pass.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

REQUIRED_FIELDS = ("value", "unit", "source", "location", "as_at", "note")
OPTIONAL_FIELDS = ("judgement",)
KEY_RE = re.compile(r"^[a-z][a-z0-9_]*$")
DATE_FORMAT = "%d %B %Y"


class AssumptionsError(ValueError):
    """The file has one or more problems; the message lists each."""


@dataclass(frozen=True)
class Assumption:
    key: str
    value: float | tuple[float, ...]
    unit: str
    source: str
    location: str
    as_at: str
    note: str
    judgement: bool


class _UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader that rejects a repeated key, which plain YAML silently overwrites."""

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
        seen: set[Any] = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=True)
            if key in seen:
                raise AssumptionsError(
                    f"duplicate key '{key}' (line {key_node.start_mark.line + 1})"
                )
            seen.add(key)
        return super().construct_mapping(node, deep)


def _is_number(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _entry_problems(key: str, entry: object) -> list[str]:
    if not isinstance(entry, dict):
        return [f"{key}: must be a mapping with {', '.join(REQUIRED_FIELDS)}"]
    problems = [f"{key}: missing '{field}'" for field in REQUIRED_FIELDS if field not in entry]
    problems += [
        f"{key}: unknown field '{field}'"
        for field in entry
        if field not in REQUIRED_FIELDS + OPTIONAL_FIELDS
    ]
    for field in ("unit", "source", "location", "note"):
        if field in entry and not (isinstance(entry[field], str) and entry[field].strip()):
            problems.append(f"{key}: '{field}' must be a non-empty string")
    if "value" in entry:
        value = entry["value"]
        is_series = isinstance(value, list) and bool(value) and all(_is_number(v) for v in value)
        if not (_is_number(value) or is_series):
            problems.append(f"{key}: 'value' must be a number or a non-empty list of numbers")
    if "as_at" in entry:
        try:
            datetime.strptime(str(entry["as_at"]), DATE_FORMAT)
        except ValueError:
            problems.append(f"{key}: 'as_at' must be a date such as '30 May 2025'")
    if "judgement" in entry and not isinstance(entry["judgement"], bool):
        problems.append(f"{key}: 'judgement' must be true or false")
    return problems


def parse_assumptions(text: str) -> dict[str, Assumption]:
    loader = _UniqueKeyLoader(text)
    try:
        raw = loader.get_single_data()
    except yaml.YAMLError as error:
        raise AssumptionsError(f"not valid YAML: {error}") from error
    finally:
        loader.dispose()
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise AssumptionsError("the file must be a mapping of input names to entries")

    problems: list[str] = []
    for key, entry in raw.items():
        if not (isinstance(key, str) and KEY_RE.match(key)):
            problems.append(f"{key!r}: input names are lower-case words joined by _")
        problems += _entry_problems(str(key), entry)
    if problems:
        raise AssumptionsError("\n".join(problems))

    assumptions: dict[str, Assumption] = {}
    for key, entry in raw.items():
        value = entry["value"]
        assumptions[key] = Assumption(
            key=key,
            value=tuple(float(v) for v in value) if isinstance(value, list) else float(value),
            unit=entry["unit"],
            source=entry["source"],
            location=entry["location"],
            as_at=str(entry["as_at"]),
            note=entry["note"],
            judgement=entry.get("judgement", False),
        )
    return assumptions


def load_assumptions(path: Path) -> dict[str, Assumption]:
    return parse_assumptions(path.read_text(encoding="utf-8"))

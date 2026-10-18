"""Trace every figure in `valuation.json` to its inputs and to a covering test (task P4-10).

`data/written/figure_trace.csv` is my list. Each row names a group of figures by a path, says how
they are calculated, which inputs in `assumptions.yaml` and which transcribed tables they depend
on, and which tests cover them. The source and page of each figure are not typed again: they are
read from the entries of the inputs the row names, so a figure and its source cannot disagree.

A row's `inputs` cell holds input names, `table:` names for transcribed tables, `doc:path#heading`
for a figure that comes from a rule in one of my documents, and `@path` references that mean
"everything the figure at that path depends on". `{method}` and `{measure}`
in a row's figure, inputs and tests stand for each of their values, so one row covers the four
multiples blocks.

The checks on the list are in `tests/engine/test_figure_trace.py`: every figure has
exactly one row, every row has a figure, every named input and test exists, and a figure does not
depend on an input that its row leaves out. `changed_figures` finds that last fact by moving each
input in turn and reporting which figures move.
"""

from __future__ import annotations

import ast
import csv
import itertools
import re
import sys
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from valuation.assumptions import Assumption
from valuation.extracted import TRACE_COLUMNS
from valuation.inputs import Inputs, load_inputs
from valuation.output import build_valuation

TRACE_FILE_COLUMNS = ("figure", "kind", "how", "inputs", "tests")
KINDS = ("input", "transcribed", "calculated", "written")
LIST_SEPARATOR = ";"
TABLE_PREFIX = "table:"
DOC_PREFIX = "doc:"
REFERENCE_PREFIX = "@"
PLACEHOLDERS = {"method": ("trading", "precedent"), "measure": ("ebitda", "ebita")}

# Text that a page prints and that carries a figure of its own.
TEXT_FIGURES = ("meta.valuation_date", "gap_bridge.steps[].explanation")

# The version number of the file layout is not a figure on any page.
SKIPPED_TOP_LEVEL = ("schema_version",)

# A date changes labels and the number of forecast years, not a figure that I can move by a step.
DATE_INPUTS = ("valuation_date_ymd", "projection_end_date_ymd")

# Weights must add to 100, so a weight is moved against each of the others in turn. A figure
# depends on the weight itself only if it moves in both runs.
BALANCED_GROUPS = (
    ("method_weight_dcf_pct", "method_weight_trading_pct", "method_weight_precedent_pct"),
    (
        "expert_method_weight_dcf_pct",
        "expert_method_weight_trading_pct",
        "expert_method_weight_precedent_pct",
    ),
)

# How far each input and each numeric table column is moved to see which figures follow, as a
# fraction of its value. An input that is zero is moved by ZERO_STEP in its own unit.
MOVE_FRACTION = 0.05
ZERO_STEP = 5.0

# Inputs that switch a convention or set a count, so a percentage step does not make sense.
SWITCH_INPUTS = {"mid_year_discounting_flag": 0.0, "sensitivity_steps_each_side": 3.0}

INDEX_RE = re.compile(r"\[\d+\]")
BRIDGE_VALUES_RE = re.compile(r"^(gap_bridge\.steps\[\]\.(?:expert_values|my_values))\..+$")
PLACEHOLDER_RE = re.compile(r"\{(method|measure)\}")


class TraceError(ValueError):
    """The trace file or the figures have one or more problems; the message lists each."""


@dataclass(frozen=True)
class TraceRow:
    figure: str
    kind: str
    how: str
    inputs: tuple[str, ...]
    tests: tuple[str, ...]
    line: int


def _split(cell: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in cell.split(LIST_SEPARATOR) if part.strip())


def _expand(row: TraceRow) -> list[TraceRow]:
    """The concrete rows for a row that uses `{method}` or `{measure}` in its figure."""
    names = sorted(set(PLACEHOLDER_RE.findall(row.figure)))
    if not names:
        return [row]
    expanded: list[TraceRow] = []
    for combination in itertools.product(*(PLACEHOLDERS[name] for name in names)):
        chosen = dict(zip(names, combination, strict=True))

        def fill(text: str, chosen: dict[str, str] = chosen) -> str:
            return PLACEHOLDER_RE.sub(
                lambda match: chosen.get(match.group(1), match.group(0)), text
            )

        expanded.append(
            replace(
                row,
                figure=fill(row.figure),
                how=fill(row.how),
                inputs=tuple(fill(item) for item in row.inputs),
                tests=tuple(fill(item) for item in row.tests),
            )
        )
    return expanded


def load_trace(path: Path) -> list[TraceRow]:
    """The rows of the trace file, with placeholders expanded, after checking each row."""
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        header = tuple(reader.fieldnames or ())
        if header != TRACE_FILE_COLUMNS:
            raise TraceError(f"{path.name}: columns are {header}, expected {TRACE_FILE_COLUMNS}")
        rows: list[TraceRow] = []
        problems: list[str] = []
        for number, record in enumerate(reader, start=2):
            row = TraceRow(
                figure=record["figure"].strip(),
                kind=record["kind"].strip(),
                how=record["how"].strip(),
                inputs=_split(record["inputs"]),
                tests=_split(record["tests"]),
                line=number,
            )
            if not row.figure:
                problems.append(f"line {number}: 'figure' is empty")
            if row.kind not in KINDS:
                problems.append(f"line {number}: kind '{row.kind}' is not one of {KINDS}")
            if not row.how:
                problems.append(f"line {number}: 'how' is empty")
            if not row.inputs and not row.tests:
                problems.append(f"line {number}: {row.figure} names no input and no test")
            if row.kind != "input" and not row.tests:
                problems.append(f"line {number}: {row.figure} names no test")
            if row.kind in ("input", "transcribed") and not row.inputs:
                problems.append(f"line {number}: {row.figure} names no input or table")
            rows.extend(_expand(row))
    if problems:
        raise TraceError("\n".join(problems))
    return rows


def flatten(valuation: Mapping[str, Any]) -> dict[str, float | str]:
    """Every numeric leaf of `valuation.json`, and the text figures, under a path with indices."""
    leaves: dict[str, float | str] = {}

    def walk(node: object, path: str) -> None:
        if isinstance(node, bool):
            return
        if isinstance(node, int | float):
            leaves[path] = float(node)
        elif isinstance(node, str):
            if normalise(path) in TEXT_FIGURES:
                leaves[path] = node
        elif isinstance(node, Mapping):
            for name, child in node.items():
                if not path and name in SKIPPED_TOP_LEVEL:
                    continue
                walk(child, f"{path}.{name}" if path else str(name))
        elif isinstance(node, list | tuple):
            for index, child in enumerate(node):
                walk(child, f"{path}[{index}]")

    walk(valuation, "")
    return leaves


def normalise(path: str) -> str:
    """A figure path without list positions, and without the input name inside a bridge step."""
    plain = INDEX_RE.sub("[]", path)
    if plain.startswith("values.") and plain.endswith(".value"):
        plain = plain.removesuffix(".value")
    match = BRIDGE_VALUES_RE.match(plain)
    return f"{match.group(1)}.*" if match else plain


def figure_groups(valuation: Mapping[str, Any]) -> list[str]:
    """The distinct normalised paths of the figures in `valuation.json`, in file order."""
    seen: dict[str, None] = {}
    for path in flatten(valuation):
        seen.setdefault(normalise(path))
    return list(seen)


def _pattern(figure: str) -> re.Pattern[str]:
    """A figure path with `*` as the only wildcard. Square brackets are part of the path."""
    return re.compile(".*".join(re.escape(part) for part in figure.split("*")))


def match_rows(groups: list[str], rows: list[TraceRow]) -> dict[str, TraceRow]:
    """The row for each figure group. Raises if a figure has no row or two, or a row is unused."""
    problems: list[str] = []
    matched: dict[str, TraceRow] = {}
    used: set[tuple[int, str]] = set()
    for group in groups:
        hits = [row for row in rows if _pattern(row.figure).fullmatch(group)]
        if not hits:
            problems.append(f"no row for figure {group}")
        elif len(hits) > 1:
            lines = ", ".join(str(row.line) for row in hits)
            problems.append(f"{group} matches rows on lines {lines}")
        else:
            matched[group] = hits[0]
            used.add((hits[0].line, hits[0].figure))
    problems += [
        f"line {row.line}: {row.figure} matches no figure"
        for row in rows
        if (row.line, row.figure) not in used
    ]
    if problems:
        raise TraceError("\n".join(problems))
    return matched


def resolved_inputs(
    row: TraceRow, by_group: Mapping[str, TraceRow], _seen: tuple[str, ...] = ()
) -> frozenset[str]:
    """The input and `table:` names a row depends on, following its `@` references."""
    if row.figure in _seen:
        raise TraceError(f"line {row.line}: {row.figure} refers to itself through {_seen}")
    names: set[str] = set()
    for item in row.inputs:
        if not item.startswith(REFERENCE_PREFIX):
            names.add(item)
            continue
        target = item.removeprefix(REFERENCE_PREFIX)
        if target not in by_group:
            raise TraceError(f"line {row.line}: {item} does not match a figure")
        names |= resolved_inputs(by_group[target], by_group, (*_seen, row.figure))
    return frozenset(names)


def explicit_inputs(row: TraceRow) -> frozenset[str]:
    return frozenset(item for item in row.inputs if not item.startswith(REFERENCE_PREFIX))


def _document_heading_exists(root: Path, reference: str) -> bool:
    """A `path#heading` reference to a Markdown heading that starts with the given text."""
    file_name, _, heading = reference.partition("#")
    path = root / file_name
    if not heading or not path.is_file():
        return False
    return any(
        line.startswith("#") and line.lstrip("#").strip().startswith(heading)
        for line in path.read_text(encoding="utf-8").splitlines()
    )


def unknown_names(rows: list[TraceRow], inputs: Inputs, root: Path) -> list[str]:
    """Inputs, tables and documents that a row names and the repository does not hold."""
    problems: list[str] = []
    for row in rows:
        for item in explicit_inputs(row):
            if item.startswith(TABLE_PREFIX):
                if item.removeprefix(TABLE_PREFIX) not in inputs.tables:
                    problems.append(f"line {row.line}: table {item} is not loaded")
            elif item.startswith(DOC_PREFIX):
                if not _document_heading_exists(root, item.removeprefix(DOC_PREFIX)):
                    problems.append(f"line {row.line}: {item} is not a heading in a document")
            elif item not in inputs.assumptions:
                problems.append(f"line {row.line}: input {item} is not in assumptions.yaml")
    return problems


def missing_tests(rows: list[TraceRow], root: Path) -> list[str]:
    """Test references of the form `tests/engine/test_x.py::test_name` that do not exist."""
    problems: list[str] = []
    functions: dict[str, set[str]] = {}
    for row in rows:
        for reference in row.tests:
            file_name, separator, test_name = reference.partition("::")
            path = root / file_name
            if not separator or not test_name or not path.is_file():
                problems.append(f"line {row.line}: '{reference}' is not file::name of a test")
                continue
            if file_name not in functions:
                tree = ast.parse(path.read_text(encoding="utf-8"))
                functions[file_name] = {
                    node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
                }
            if test_name not in functions[file_name]:
                problems.append(f"line {row.line}: {file_name} has no test {test_name}")
    return problems


def _moved_inputs(inputs: Inputs, name: str, partner: str | None = None) -> Inputs:
    if name in SWITCH_INPUTS:
        return inputs.with_assumption_values({name: SWITCH_INPUTS[name]})
    value = inputs.number(name)
    step = ZERO_STEP if value == 0 else value * MOVE_FRACTION
    if partner is None:
        return inputs.with_assumption_values({name: value + step})
    # Move towards the partner that has room, so no weight goes below zero.
    direction = 1.0 if inputs.number(partner) >= step else -1.0
    return inputs.with_assumption_values(
        {name: value + direction * step, partner: inputs.number(partner) - direction * step}
    )


def _partners(name: str) -> tuple[str, ...]:
    for group in BALANCED_GROUPS:
        if name in group:
            return tuple(member for member in group if member != name)
    return ()


def _moved_table(inputs: Inputs, table: str, column: str) -> Inputs:
    rows = tuple(
        {**row, column: repr(float(row[column]) * (1 + MOVE_FRACTION))}
        for row in inputs.tables[table]
    )
    return replace(inputs, tables={**inputs.tables, table: rows})


def _numeric_columns(inputs: Inputs, table: str) -> Iterator[str]:
    for column in inputs.tables[table][0]:
        if column in TRACE_COLUMNS:
            continue
        try:
            for row in inputs.tables[table]:
                float(row[column])
        except ValueError:
            continue
        yield column


def _moved_groups(base: Mapping[str, float | str], other: Mapping[str, float | str]) -> set[str]:
    changed = {path for path in base if other.get(path) != base[path]}
    return {normalise(path) for path in changed | (set(other) - set(base))}


def changed_figures(
    inputs: Inputs, build: Callable[[Inputs], Mapping[str, Any]]
) -> dict[str, set[str]]:
    """For each input and `table:` name, the figure groups that move when it moves.

    A table is moved one numeric column at a time. If a column is a selector in a lookup, the
    engine stops with an error and the test fails, so a selector column cannot be missed silently.
    """
    base = flatten(build(inputs))
    result: dict[str, set[str]] = {}
    for name in inputs.assumptions:
        if name in DATE_INPUTS:
            continue
        runs = [
            _moved_groups(base, flatten(build(_moved_inputs(inputs, name, partner))))
            for partner in _partners(name) or (None,)
        ]
        result[name] = set.intersection(*runs)
    for table in inputs.tables:
        moved: set[str] = set()
        for column in _numeric_columns(inputs, table):
            moved |= _moved_groups(base, flatten(build(_moved_table(inputs, table, column))))
        result[f"{TABLE_PREFIX}{table}"] = moved
    return result


def dependency_problems(
    by_group: Mapping[str, TraceRow], moved: Mapping[str, set[str]]
) -> list[str]:
    """Figures that depend on an input their row omits, and named inputs that move nothing.

    The first kind is the dangerous one: a figure with a source the list does not show. The
    second is checked only for inputs written out in the row, since a `@` reference brings in
    the inputs of a whole stem, which can be more than one case of it uses.
    """
    problems: list[str] = []
    actual_by_group: dict[str, set[str]] = {group: set() for group in by_group}
    for name, groups in moved.items():
        for group in groups:
            actual_by_group.setdefault(group, set()).add(name)
    for group, row in by_group.items():
        declared = resolved_inputs(row, by_group)
        omitted = sorted(actual_by_group[group] - declared)
        if omitted:
            problems.append(f"line {row.line}: {group} also depends on {', '.join(omitted)}")
    rows = {(row.line, row.figure): row for row in by_group.values()}.values()
    for row in rows:
        members = [group for group, other in by_group.items() if other is row]
        used: set[str] = set()
        for group in members:
            used |= actual_by_group[group]
        # My own wording is text, so no move of a number changes it.
        idle = sorted(
            item
            for item in explicit_inputs(row)
            if item not in used
            and item.removeprefix(TABLE_PREFIX) not in DATE_INPUTS
            and not item.startswith(DOC_PREFIX)
            and row.kind != "written"
        )
        if idle:
            problems.append(f"line {row.line}: {row.figure} names {', '.join(idle)} but none moves")
    return problems


def source_of(entry: Assumption) -> str:
    return f"{entry.source}, {entry.location} ({entry.as_at})"


def table_sources(inputs: Inputs, table: str) -> list[str]:
    """The distinct source and location pairs among the rows of one transcribed table."""
    seen: dict[str, None] = {}
    for row in inputs.tables[table]:
        seen.setdefault(f"{row['source']}, {row['location']} ({row['as_at']})")
    return list(seen)


def trace_lines(
    valuation: Mapping[str, Any], rows: list[TraceRow], inputs: Inputs
) -> list[dict[str, str]]:
    """One line per `values` key and one per other figure group, with each source resolved."""
    by_group = match_rows(figure_groups(valuation), rows)
    lines: list[dict[str, str]] = []
    for group, row in by_group.items():
        names = sorted(resolved_inputs(row, by_group))
        sources: list[str] = []
        for name in names:
            if name.startswith(TABLE_PREFIX):
                sources += table_sources(inputs, name.removeprefix(TABLE_PREFIX))
            elif name.startswith(DOC_PREFIX):
                file_name, _, heading = name.removeprefix(DOC_PREFIX).partition("#")
                sources.append(f'{file_name}, section "{heading}"')
            else:
                sources.append(source_of(inputs.assumptions[name]))
        lines.append(
            {
                "figure": group.removeprefix("values."),
                "kind": row.kind,
                "how": row.how,
                "inputs": LIST_SEPARATOR.join(names),
                "sources": " | ".join(dict.fromkeys(sources)),
                "tests": LIST_SEPARATOR.join(row.tests),
            }
        )
    return lines


def write_trace_listing(root: Path, path: Path) -> int:
    """Write one line per figure with its sources resolved, for reading. Returns the line count."""
    inputs = load_inputs(root)
    rows = load_trace(root / "data" / "written" / "figure_trace.csv")
    lines = trace_lines(build_valuation(inputs), rows, inputs)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(lines[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(lines)
    return len(lines)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    path = root / "build" / "figure_trace.csv"
    count = write_trace_listing(root, path)
    sys.stdout.write(f"wrote {path.relative_to(root)} with {count} figures\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

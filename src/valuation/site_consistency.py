"""Checks that every figure on the built pages comes from the engine, the inputs or a source table
(task P5-15).

Three rules, each reported with the page and the text it found:

1. A template holds no typed figure. Digits in a template's own text or in a `{{ }}` expression
   that writes text are errors, so a number can only arrive through a variable. The fiscal year
   labels (FY25, FY26) are the one allowed form: they name a year and are not a figure.
2. A figure that names its origin with a `data-key`, `data-input`, `data-forecast`,
   `data-bridge` or `data-count` attribute equals that value in `valuation.json`, the inputs or
   the tables, at the precision the page shows.
3. Every other number in the visible text must appear in the evidence: the numbers in
   `valuation.json` (rounded to up to four places), the text of the inputs, the transcribed and
   written tables, and the lowest, median and highest multiples of the peer and deal tables.
   This is a net and not a proof: a changed figure that happens to equal some other number in the
   evidence passes it, which is why the figures that matter carry an attribute (rule 2).

4. A reference marker (`data-ref`) links to its entry in the list of sources at the end of the
   page, every entry is cited by a marker, each entry equals the reference built from the inputs
   (document, page, date and register link), and a figure that names an input carries that
   input's code.

Scale marks on a chart axis, reference codes and the commit hash in the footer are not figures
and are skipped.
"""

from __future__ import annotations

import re
import statistics
from collections.abc import Iterator
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from valuation.inputs import Inputs
from valuation.provenance import Reference, ReferenceBook
from valuation.site_format import MINUS, number, plain
from valuation.site_frame import BuildInfo

ORIGIN_ATTRIBUTES = ("data-key", "data-input", "data-forecast", "data-bridge", "data-count")
NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")
# A fiscal year label names a year. It is the only number a template may write itself.
TEMPLATE_ALLOWED = re.compile(r"\bFY\d{2}\b")
VOID_TAGS = frozenset({"meta", "link", "br", "col", "input", "img", "hr"})
MAX_PLACES = 4


def _tokens(text: str) -> list[str]:
    return [token.replace(",", "") for token in NUMBER.findall(text)]


def _places(token: str) -> int:
    return len(token.split(".")[1]) if "." in token else 0


# Rule 1: templates


def template_problems(templates_dir: Path) -> list[str]:
    """Typed figures in the templates: digits in their text or in an expression that writes text."""
    problems: list[str] = []
    for template in sorted(templates_dir.glob("*.j2")):
        text = template.read_text(encoding="utf-8")
        text = re.sub(r"\{#.*?#\}", "", text, flags=re.DOTALL)
        text = re.sub(r"\{%.*?%\}", "", text, flags=re.DOTALL)
        expressions: list[str] = []

        def keep(match: re.Match[str], found: list[str] = expressions) -> str:
            found.append(match.group(1))
            return f"\x01{len(found) - 1}\x01"

        text = re.sub(r"\{\{(.*?)\}\}", keep, text, flags=re.DOTALL)
        # What is left in a tag is an attribute, which places a mark and does not write a figure.
        text = re.sub(r"<[^>]*>", "\x02", text)
        for line in text.splitlines():
            visible = TEMPLATE_ALLOWED.sub("", re.sub(r"\x01\d+\x01", "", line))
            if re.search(r"\d", visible):
                problems.append(f"{template.name}: typed figure in the text: {line.strip()[:80]}")
            for index in re.findall(r"\x01(\d+)\x01", line):
                expression = expressions[int(index)]
                if re.search(r"\d", expression):
                    problems.append(
                        f"{template.name}: typed figure in an expression: {expression.strip()[:80]}"
                    )
    return problems


# Pages


class _Page(HTMLParser):
    """The visible text of a page, with the figures that name their origin picked out."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tagged: list[tuple[dict[str, str], str, str]] = []
        self.loose: list[str] = []
        # Reference markers as (code, href, the origin attribute of the figure around it), and the
        # entries of the sources list as {code: {part: text}}.
        self.markers: list[tuple[str, str, dict[str, str]]] = []
        self.entries: dict[str, dict[str, str]] = {}
        self._stack: list[tuple[str, dict[str, str], list[str]]] = []
        self._row_header = ""
        self._entry = ""

    def _inside(self, test: str) -> bool:
        return any(test in attrs.get("class", "") for _, attrs, _ in self._stack)

    def _is_tagged(self) -> bool:
        return any(name in attrs for _, attrs, _ in self._stack for name in ORIGIN_ATTRIBUTES)

    def _skipped(self) -> bool:
        return any(
            "axis-label" in attrs.get("class", "")
            or "ref-code" in attrs.get("class", "")
            or "/commit/" in attrs.get("href", "")
            for _, attrs, _ in self._stack
        )

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        if tag in VOID_TAGS:
            return
        self._stack.append((tag, values, []))
        if "aria-label" in values and not self._is_tagged() and not self._skipped():
            self.loose.append(values["aria-label"])
        if tag == "a" and "data-ref" in values:
            origin = {
                name: attrs[name]
                for _, attrs, _ in self._stack
                for name in ORIGIN_ATTRIBUTES
                if name in attrs
            }
            self.markers.append((values["data-ref"], values.get("href", ""), origin))
        if tag == "li" and values.get("id", "").startswith("ref-"):
            self._entry = values["id"][len("ref-") :]
            self.entries[self._entry] = {}
        if self._entry and tag == "a" and "ref-link" in values.get("class", ""):
            self.entries[self._entry]["href"] = values.get("href", "")

    def handle_data(self, data: str) -> None:
        for _, _, parts in self._stack:
            parts.append(data)
        if self._stack and not self._is_tagged() and not self._skipped():
            self.loose.append(data)

    def handle_endtag(self, tag: str) -> None:
        while self._stack:
            name, values, parts = self._stack.pop()
            if name != tag:
                continue
            text = "".join(parts).strip()
            part = next(
                (word[len("ref-") :] for word in values.get("class", "").split() if "ref-" in word),
                "",
            )
            if self._entry and part:
                self.entries[self._entry][part] = text
            if tag == "li":
                self._entry = ""
            if tag == "th" and not self._row_header:
                self._row_header = text
            if tag == "tr":
                self._row_header = ""
            if any(attribute in values for attribute in ORIGIN_ATTRIBUTES):
                self.tagged.append((values, text, self._row_header))
            return


def _parse(path: Path) -> _Page:
    page = _Page()
    page.feed(path.read_text(encoding="utf-8"))
    page.close()
    return page


# Rule 2: figures that name their origin


def _parse_figure(text: str) -> tuple[float, int] | None:
    """The first figure in a text as a signed value with its decimal places, or None."""
    match = re.search(rf"([+{MINUS}-]?)\s*(?:A\$)?(\d[\d,]*(?:\.\d+)?)", text)
    if match is None:
        return None
    token = match.group(2).replace(",", "")
    value = float(token)
    if match.group(1) in (MINUS, "-"):
        value = -value
    return value, _places(token)


def _forecast_row(valuation: dict[str, Any], period: str) -> dict[str, Any]:
    return next(row for row in valuation["forecast"]["rows"] if row["period"] == period)


def _bridge_value(bridge: dict[str, Any], key: str) -> float:
    if key in ("start_value_per_share_aud", "end_value_per_share_aud"):
        return float(bridge[key])
    if key in ("reconstruction_change_aud", "total_gap_aud"):
        return float(bridge[key])
    if key == "rounded_steps_sum_aud":
        return sum(round(float(step["change_aud"]), 2) for step in bridge["steps"])
    step_id, field = key.split(":")
    step = next(item for item in bridge["steps"] if item["id"] == step_id)
    return float(step[field])


def _count(name: str, inputs: Inputs, timeline: list[dict[str, str]]) -> int:
    """A count the pages quote: inputs in the register, my judgement inputs, timeline events."""
    counts = {
        "inputs": len(inputs.assumptions),
        "judgement_inputs": sum(entry.judgement for entry in inputs.assumptions.values()),
        "timeline_events": len(timeline),
        "timeline_checked": sum(row["status"] == "verified" for row in timeline),
    }
    return counts[name]


def _source_value(
    attrs: dict[str, str],
    row_header: str,
    valuation: dict[str, Any],
    inputs: Inputs,
    timeline: list[dict[str, str]],
) -> float | str:
    if "data-key" in attrs:
        return float(valuation["values"][attrs["data-key"]]["value"])
    if "data-input" in attrs:
        return inputs.number(attrs["data-input"])
    if "data-forecast" in attrs:
        return float(_forecast_row(valuation, row_header)[attrs["data-forecast"]])
    if "data-count" in attrs:
        return _count(attrs["data-count"], inputs, timeline)
    return _bridge_value(valuation["gap_bridge"], attrs["data-bridge"])


def _figure_problems(
    page: _Page,
    name: str,
    valuation: dict[str, Any],
    inputs: Inputs,
    timeline: list[dict[str, str]],
) -> list[str]:
    problems = []
    for attrs, text, row_header in page.tagged:
        origin = next(f"{a}={attrs[a]}" for a in ORIGIN_ATTRIBUTES if a in attrs)
        try:
            source = _source_value(attrs, row_header, valuation, inputs, timeline)
        except (KeyError, StopIteration):
            problems.append(f"{name}: {origin} names nothing in the data (text {text!r})")
            continue
        if attrs.get("data-input") == "mid_year_discounting_flag":
            if text != ("Yes" if source == 1 else "No"):
                problems.append(f"{name}: {origin} shows {text!r} for a flag of {source}")
            continue
        shown = _parse_figure(text)
        if shown is None:
            problems.append(f"{name}: {origin} shows no figure (text {text!r})")
            continue
        value, places = shown
        if abs(round(float(source), places) - value) > 10 ** -(places + 6):
            problems.append(
                f"{name}: {origin} shows {text!r} but the data says {round(float(source), places)}"
            )
    return problems


# Rule 3: every other number is in the evidence


def _leaves(node: Any) -> Iterator[float | str]:
    if isinstance(node, dict):
        for item in node.values():
            yield from _leaves(item)
    elif isinstance(node, list | tuple):
        for item in node:
            yield from _leaves(item)
    elif isinstance(node, bool):
        return
    elif isinstance(node, int | float | str):
        yield node


def _multiple_statistics(rows: tuple[Any, ...] | list[Any]) -> list[str]:
    columns: dict[tuple[str, str], list[float]] = {}
    for row in rows:
        columns.setdefault((row["measure"], row["basis"]), []).append(float(row["multiple_x"]))
    found = []
    for multiples in columns.values():
        found += [
            number(min(multiples), 1),
            number(statistics.median(multiples), 1),
            number(max(multiples), 1),
        ]
    return found


def evidence_tokens(
    valuation: dict[str, Any], inputs: Inputs, build: BuildInfo, timeline: list[dict[str, str]]
) -> set[str]:
    """Every number the sources hold, as plain tokens such as 4.26 or 2025."""
    found: set[str] = set(_tokens(build.date))
    for leaf in _leaves(valuation):
        if isinstance(leaf, str):
            found.update(_tokens(leaf))
        else:
            found.update(
                number(abs(leaf), places).replace(",", "") for places in range(MAX_PLACES + 1)
            )
    for entry in inputs.assumptions.values():
        for text in (entry.source, entry.location, entry.as_at, entry.note):
            found.update(_tokens(str(text)))
        values = entry.value if isinstance(entry.value, tuple) else (entry.value,)
        found.update(token for part in values for token in _tokens(plain(abs(part))))
    for rows in (*inputs.tables.values(), timeline):
        for row in rows:
            for text in row.values():
                found.update(_tokens(text))
    for table in ("comparable_multiples", "precedent_transactions"):
        for text in _multiple_statistics(inputs.tables[table]):
            found.update(_tokens(text))
    return found


def _page_problems(page: _Page, name: str, evidence: set[str]) -> list[str]:
    problems = []
    for chunk in page.loose:
        for token in _tokens(chunk):
            if token not in evidence:
                shown = chunk.strip()[:60]
                problems.append(f"{name}: the number {token} is not in the sources (in {shown!r})")
    return problems


# Rule 4: reference codes


def _expected_entry(reference: Reference) -> dict[str, str]:
    expected = {
        "code": reference.code,
        "name": reference.name,
        "source": reference.source,
        "location": reference.location,
        "date": reference.as_at,
    }
    if reference.link is not None and reference.link_label is not None:
        expected["href"] = reference.link
        expected["link"] = reference.link_label
    return expected


def _marker_problems(page: _Page, name: str, book: ReferenceBook, inputs: Inputs) -> list[str]:
    problems = []
    for code, href, origin in page.markers:
        if href != f"#ref-{code}":
            problems.append(f"{name}: the marker {code} links to {href!r}, not to its source")
        if code not in page.entries:
            problems.append(f"{name}: the marker {code} has no entry in the list of sources")
        key = origin.get("data-input") or origin.get("data-key", "")
        if key in inputs.assumptions and book.for_input(key).code != code:
            problems.append(
                f"{name}: the figure for {key} carries {code}, not {book.for_input(key).code}"
            )
    return problems


def reference_problems(page: _Page, name: str, inputs: Inputs) -> list[str]:
    """Reference markers and the list of sources agree with each other and with the data."""
    book = ReferenceBook(inputs)
    known = {reference.code: reference for reference in book.all_references()}
    problems = _marker_problems(page, name, book, inputs)
    marked = {code for code, _, _ in page.markers}
    for code, parts in page.entries.items():
        if code not in known:
            problems.append(f"{name}: the list of sources has {code}, which is not a reference")
            continue
        if code not in marked:
            problems.append(f"{name}: {code} is listed but no figure on the page carries it")
        expected = _expected_entry(known[code])
        if parts != expected:
            problems.append(f"{name}: the entry for {code} is {parts}, the data says {expected}")
    return problems


def consistency_problems(
    root: Path,
    out_dir: Path,
    valuation: dict[str, Any],
    inputs: Inputs,
    build: BuildInfo,
    timeline: list[dict[str, str]],
) -> list[str]:
    """Every problem found in the templates and in the built pages."""
    problems = template_problems(root / "site" / "templates")
    evidence = evidence_tokens(valuation, inputs, build, timeline)
    for path in sorted(out_dir.glob("*.html")):
        page = _parse(path)
        problems += _figure_problems(page, path.name, valuation, inputs, timeline)
        problems += _page_problems(page, path.name, evidence)
        problems += reference_problems(page, path.name, inputs)
    return problems

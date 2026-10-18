"""The quieter header, table heads and motion rules (task P5-26, 19 October 2026)."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSS = (ROOT / "site" / "static" / "site.css").read_text(encoding="utf-8")


def rule(selector: str) -> str:
    match = re.search(r"(?:^|\n)\s*" + re.escape(selector) + r"\s*\{([^}]*)\}", CSS)
    assert match, selector
    return match.group(1)


def test_the_switches_are_set_as_text_with_no_box() -> None:
    bodies = re.findall(r"\n  \.sources-switch,\n  \.theme-switch \{([^}]*)\}", CSS)
    assert any("background: none;" in body and "border: none;" in body for body in bodies)


def test_the_header_and_the_table_heads_carry_no_band_fill() -> None:
    assert "background" not in rule(".site-header")
    assert "background" not in rule(".figures thead th")
    assert "border-block-end-color: var(--ink);" in rule(".figures thead th")


def test_every_transition_uses_the_motion_token_and_reduced_motion_turns_it_off() -> None:
    durations = re.findall(r"transition:\s*([^;]*);", CSS)
    assert durations
    for value in durations:
        assert value.strip() == "none" or "var(--motion-fast)" in value
    reduced = re.search(r"@media \(prefers-reduced-motion: reduce\)\s*\{(.*?)\n  \}", CSS, re.S)
    assert reduced
    assert "transition: none;" in reduced.group(1)

"""The PDF report template reads every figure from valuation.json and builds from the tracked
inputs alone (task P6-01). The tests that run Typst are skipped on a machine that has none; the
build refuses any Typst version other than the pinned one, so a wrong version fails and is not
skipped."""

import importlib.util
import json
import os
import re
import shutil
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from valuation.inputs import load_inputs
from valuation.output import build_valuation
from valuation.report_build import (
    PDF_NAME,
    TEMPLATE_NAME,
    TYPST_VERSION,
    check_version,
    compile_command,
    find_typst,
    prepare_folder,
)
from valuation.site_build import DISCLAIMER

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = (ROOT / "report" / TEMPLATE_NAME).read_text(encoding="utf-8")
# What a build needs from a clean clone: the template, the inputs and the transcribed data.
TRACKED_INPUTS = ("report", "assumptions.yaml", "data")
HAS_TYPST = bool(shutil.which("typst") or os.environ.get("TYPST"))
needs_typst = pytest.mark.skipif(not HAS_TYPST, reason="typst is not installed on this machine")


@pytest.fixture(scope="module")
def valuation() -> dict[str, Any]:
    written: dict[str, Any] = json.loads(json.dumps(build_valuation(load_inputs(ROOT))))
    return written


def build_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "build_report", ROOT / "scripts" / "build_report.py"
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clean_copy(destination: Path) -> Path:
    """A folder holding only what is tracked and needed, as in a fresh clone."""
    for name in TRACKED_INPUTS:
        source = ROOT / name
        target = destination / name
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copyfile(source, target)
    (destination / "build").mkdir()
    return destination


def test_every_key_the_template_reads_is_in_valuation_json(valuation: dict[str, Any]) -> None:
    keys = re.findall(r'val\("([a-z0-9_]+)"\)', TEMPLATE)
    assert len(keys) >= 5
    assert [key for key in keys if key not in valuation["values"]] == []


def test_every_field_the_template_reads_from_a_block_exists(valuation: dict[str, Any]) -> None:
    blocks = {
        "meta": valuation["meta"],
        "bridge": valuation["gap_bridge"],
        "step": valuation["gap_bridge"]["steps"][0],
        "row": valuation["football_field"][0],
    }
    used = re.findall(r"\b(meta|bridge|step|row)\.([a-z_]+)", TEMPLATE)
    assert len(used) >= 10
    assert [(block, field) for block, field in used if field not in blocks[block]] == []


def test_every_row_key_a_football_field_row_names_is_in_valuation_json(
    valuation: dict[str, Any],
) -> None:
    for row in valuation["football_field"]:
        for name in ("low_key", "high_key", "preferred_key"):
            if row[name] is not None:
                assert row[name] in valuation["values"], row[name]


def test_the_placeholders_hold_no_figure_and_no_text_of_mine() -> None:
    placeholders = re.findall(r"#placeholder\[(.*?)\]", TEMPLATE)
    assert len(placeholders) == 3
    assert not [text for text in placeholders if re.search(r"\d", text)]


def test_each_placeholder_uses_the_words_of_its_task_in_the_task_list() -> None:
    task_list = (ROOT / "TODO.md").read_text(encoding="utf-8").lower()
    placeholders = re.findall(r"#placeholder\[(.*?)\]", TEMPLATE)
    assert [text for text in placeholders if text.rstrip(".").lower() not in task_list] == []


def test_the_template_loads_valuation_json_from_its_own_folder() -> None:
    assert 'json("valuation.json")' in TEMPLATE


def test_the_pinned_version_is_accepted_and_any_other_is_not() -> None:
    check_version(f"typst {TYPST_VERSION} (9dfd3a08)\n")
    for other in ("typst 0.15.2 (abcdef12)", "typst 0.14.0 (abcdef12)", "typst", ""):
        with pytest.raises(RuntimeError, match="expected typst"):
            check_version(other)


def test_typst_is_taken_from_the_variable_then_the_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TYPST", "C:/tools/typst.exe")
    assert find_typst() == "C:/tools/typst.exe"
    monkeypatch.delenv("TYPST")
    monkeypatch.setattr(shutil, "which", lambda name: None)
    with pytest.raises(RuntimeError, match="typst is not on the path"):
        find_typst()


def test_the_folder_holds_the_template_and_a_fresh_valuation_json(
    valuation: dict[str, Any],
) -> None:
    out_dir = ROOT / "build" / "report_folder_test"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "stale.txt").write_text("old", encoding="utf-8")
    template = prepare_folder(ROOT, out_dir)
    assert template == out_dir / TEMPLATE_NAME
    assert template.read_text(encoding="utf-8") == TEMPLATE
    assert json.loads((out_dir / "valuation.json").read_text(encoding="utf-8")) == valuation
    assert not (out_dir / "stale.txt").exists()


def test_a_folder_outside_the_build_folder_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="refusing to replace"):
        prepare_folder(ROOT, tmp_path / "report")


def test_the_compile_command_uses_only_embedded_fonts_and_the_sites_disclaimer() -> None:
    folder = ROOT / "build" / "report"
    command = compile_command("typst", folder / TEMPLATE_NAME, "17 October 2026")
    assert "--ignore-system-fonts" in command
    assert f"disclaimer={DISCLAIMER}" in command
    assert "build_date=17 October 2026" in command
    assert command[command.index("--root") + 1] == str(folder)
    assert command[-1] == str(folder / PDF_NAME)


@needs_typst
def test_the_pdf_builds_from_a_copy_that_holds_only_the_tracked_inputs(tmp_path: Path) -> None:
    root = clean_copy(tmp_path)
    pdf = build_script().build_report(root, root / "build" / "report", "17 October 2026")
    assert pdf.read_bytes().startswith(b"%PDF-")
    assert pdf.stat().st_size > 5_000


@needs_typst
def test_a_key_that_valuation_json_does_not_hold_stops_the_build(tmp_path: Path) -> None:
    root = clean_copy(tmp_path)
    template = root / "report" / TEMPLATE_NAME
    template.write_text(
        template.read_text(encoding="utf-8").replace(
            'val("offer_price_aud")', 'val("no_such_key")'
        ),
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="typst failed"):
        build_script().build_report(root, root / "build" / "report", "17 October 2026")

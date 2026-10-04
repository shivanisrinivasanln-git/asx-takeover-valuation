from pathlib import Path

import pytest

from valuation.extracted import ExtractedDataError, check_extracted_dir, load_rows, trace_problems

HEADER = "item,value_aud_m,source,location,as_at\n"
GOOD_ROW = "revenue_fy24,415.7,Domain Annual Report 2024,report p. 12,30 June 2024\n"


def write(directory: Path, name: str, text: str) -> Path:
    path = directory / name
    path.write_text(text, encoding="utf-8")
    return path


def test_complete_file_has_no_problems_and_loads(tmp_path: Path) -> None:
    path = write(tmp_path, "revenue.csv", HEADER + GOOD_ROW)
    assert trace_problems(path) == []
    assert load_rows(path) == [
        {
            "item": "revenue_fy24",
            "value_aud_m": "415.7",
            "source": "Domain Annual Report 2024",
            "location": "report p. 12",
            "as_at": "30 June 2024",
        }
    ]


def test_missing_trace_columns_are_named(tmp_path: Path) -> None:
    path = write(tmp_path, "revenue.csv", "item,value_aud_m,source\nrevenue_fy24,415.7,Report\n")
    assert trace_problems(path) == ["revenue.csv: missing column(s) location, as_at"]


def test_empty_cells_are_reported_with_line_numbers(tmp_path: Path) -> None:
    text = HEADER + GOOD_ROW + "revenue_fy23,,Domain Annual Report 2023, ,30 June 2023\n"
    problems = trace_problems(write(tmp_path, "revenue.csv", text))
    assert problems == ["revenue.csv line 3: 'location' is empty"]


def test_file_with_no_rows_is_a_problem(tmp_path: Path) -> None:
    assert trace_problems(write(tmp_path, "empty.csv", HEADER)) == ["empty.csv: no data rows"]


def test_file_without_a_header_is_a_problem(tmp_path: Path) -> None:
    path = write(tmp_path, "blank.csv", "")
    assert trace_problems(path) == ["blank.csv: missing column(s) source, location, as_at"]


def test_check_dir_collects_problems_from_every_file(tmp_path: Path) -> None:
    write(tmp_path, "a.csv", HEADER + GOOD_ROW)
    write(tmp_path, "b.csv", HEADER)
    write(tmp_path, "c.csv", "item,source\nx,y\n")
    with pytest.raises(ExtractedDataError) as caught:
        check_extracted_dir(tmp_path)
    message = str(caught.value)
    assert "b.csv: no data rows" in message
    assert "c.csv: missing column(s) location, as_at" in message
    assert "a.csv" not in message


def test_load_rows_refuses_a_file_with_problems(tmp_path: Path) -> None:
    path = write(tmp_path, "bad.csv", HEADER)
    with pytest.raises(ExtractedDataError, match="no data rows"):
        load_rows(path)


def test_directory_with_no_csv_files_passes(tmp_path: Path) -> None:
    check_extracted_dir(tmp_path)

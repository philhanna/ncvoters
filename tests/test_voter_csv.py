# tests.test_voter_csv
"""Tests for the CsvVoterWriter driven adapter."""

import pandas as pd

from ncvoters.adapters.voter_csv import CsvVoterWriter


def test_writes_header_once_and_sorts_rows(tmp_path):
    path = tmp_path / "out.csv"
    writer = CsvVoterWriter(str(path))

    writer.write(pd.DataFrame({"a": [3, 1], "b": [30, 10]}))
    writer.write(pd.DataFrame({"a": [2], "b": [20]}))
    writer.close()

    result = pd.read_csv(path)
    assert list(result.columns) == ["a", "b"]
    # Rows are sorted (header preserved as the first line).
    assert result.to_dict("records") == [
        {"a": 1, "b": 10},
        {"a": 2, "b": 20},
        {"a": 3, "b": 30},
    ]


def test_sorts_across_multiple_runs(tmp_path):
    # batch_size=2 forces several sorted runs that must be merged.
    path = tmp_path / "out.csv"
    writer = CsvVoterWriter(str(path), batch_size=2)

    writer.write(pd.DataFrame({"a": [5, 1, 4, 2, 3], "b": [50, 10, 40, 20, 30]}))
    writer.close()

    result = pd.read_csv(path)
    assert list(result["a"]) == [1, 2, 3, 4, 5]


def test_output_not_created_until_close(tmp_path):
    path = tmp_path / "out.csv"
    writer = CsvVoterWriter(str(path))
    writer.write(pd.DataFrame({"a": [1], "b": [2]}))

    assert not path.exists()  # staged in a temp file, not the output yet
    writer.close()
    assert path.exists()


def test_removes_pre_existing_file(tmp_path):
    path = tmp_path / "out.csv"
    path.write_text("stale,data\n9,9\n")

    writer = CsvVoterWriter(str(path))
    writer.write(pd.DataFrame({"a": [1], "b": [2]}))
    writer.close()

    result = pd.read_csv(path)
    assert "stale" not in result.columns
    assert len(result) == 1


def test_close_without_writes_produces_no_output(tmp_path):
    path = tmp_path / "out.csv"
    writer = CsvVoterWriter(str(path))

    writer.close()

    assert not path.exists()

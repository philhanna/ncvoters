# tests.test_voter_csv
"""Tests for the CsvVoterWriter driven adapter."""

import pandas as pd

from ncvoters.adapters.voter_csv import CsvVoterWriter


def test_writes_header_once_and_appends(tmp_path):
    path = tmp_path / "out.csv"
    writer = CsvVoterWriter(str(path))

    writer.write(pd.DataFrame({"a": [1], "b": [2]}))
    writer.write(pd.DataFrame({"a": [3], "b": [4]}))

    result = pd.read_csv(path)
    assert list(result.columns) == ["a", "b"]
    assert result.to_dict("records") == [
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
    ]


def test_removes_pre_existing_file(tmp_path):
    path = tmp_path / "out.csv"
    path.write_text("stale,data\n9,9\n")

    writer = CsvVoterWriter(str(path))
    writer.write(pd.DataFrame({"a": [1], "b": [2]}))

    result = pd.read_csv(path)
    assert "stale" not in result.columns
    assert len(result) == 1

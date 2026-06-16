# tests.test_application
"""Tests for the create_voter_csv use case, using in-memory fake adapters."""

import pandas as pd

from ncvoters.application import create_voter_csv


class FakeLayoutProvider:
    def __init__(self, lines):
        self._lines = lines

    def get_lines(self):
        return self._lines


class FakeVoterReader:
    def __init__(self, chunks):
        self._chunks = chunks

    def read_chunks(self):
        return iter(self._chunks)


class FakeVoterWriter:
    def __init__(self):
        self.chunks = []
        self.closed = False

    def write(self, df):
        self.chunks.append(df)

    def close(self):
        self.closed = True


def _chunk(last_names, statuses):
    n = len(last_names)
    return pd.DataFrame({
        "status_cd": statuses,
        "last_name": last_names,
        "first_name": ["F"] * n,
        "middle_name": ["M"] * n,
        "res_street_address": ["1 ST"] * n,
        "res_city_desc": ["CITY"] * n,
        "county_id": ["01"] * n,
        "state_cd": ["NC"] * n,
        "zip_code": ["00000"] * n,
        "full_phone_number": [""] * n,
        "race_code": ["W"] * n,
        "party_cd": ["UNA"] * n,
        "gender_code": ["U"] * n,
        "birth_year": [2000] * n,
        "age_at_year_end": [26] * n,
        "birth_state": ["NC"] * n,
    })


def test_create_voter_csv_returns_total_active_rows():
    layout = FakeLayoutProvider(["ALAMANCE 1", "YANCEY 100"])
    reader = FakeVoterReader([
        _chunk(["A1", "R1", "A2"], ["A", "R", "A"]),
        _chunk(["A3"], ["A"]),
    ])
    writer = FakeVoterWriter()

    total = create_voter_csv(layout, reader, writer, log=lambda *a: None)

    assert total == 3
    assert writer.closed


def test_create_voter_csv_writes_one_transformed_chunk_per_input_chunk():
    layout = FakeLayoutProvider(["ALAMANCE 1", "YANCEY 100"])
    reader = FakeVoterReader([
        _chunk(["A1", "A2"], ["A", "A"]),
        _chunk(["A3"], ["A"]),
    ])
    writer = FakeVoterWriter()

    create_voter_csv(layout, reader, writer, log=lambda *a: None)

    assert len(writer.chunks) == 2
    assert list(writer.chunks[0]["county"]) == ["ALAMANCE", "ALAMANCE"]

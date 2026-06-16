# tests.test_domain
"""Tests for the pure domain services."""

import pandas as pd
import pytest

from ncvoters.domain import OUTPUT_COLUMNS, parse_county_map, sanitize, transform_chunk


@pytest.mark.parametrize("raw, expected", [
    ("  hello  world  ", "hello world"),
    ("\tfoo\n\nbar ", "foo bar"),
    ("clean", "clean"),
    ("", ""),
    (None, ""),
    (float("nan"), ""),
])
def test_sanitize(raw, expected):
    assert sanitize(raw) == expected


def test_parse_county_map_runs_from_alamance_to_yancey():
    lines = [
        "Some preamble that should be ignored",
        "ALAMANCE 1",
        "WAKE 92",
        "YANCEY 100",
        "TRAILER 999 ignored after yancey",
    ]
    county_map = parse_county_map(lines)
    assert county_map == {"01": "ALAMANCE", "92": "WAKE", "100": "YANCEY"}


def test_parse_county_map_empty_when_no_alamance():
    assert parse_county_map(["FOO 1", "BAR 2"]) == {}


def _raw_chunk():
    return pd.DataFrame({
        "status_cd": ["A", "R", "A"],
        "last_name": ["  SMITH  ", "X", " DOE "],
        "first_name": ["JANE", "Y", "JOHN"],
        "middle_name": ["", "", "Q"],
        "res_street_address": ["1  MAIN  ST", "z", "2 OAK"],
        "res_city_desc": ["RALEIGH", "c", "CARY"],
        "county_id": ["92", "01", "92"],
        "state_cd": ["NC", "NC", "NC"],
        "zip_code": ["27601", "0", "27606"],
        "full_phone_number": ["", "", ""],
        "race_code": ["W", "W", "B"],
        "party_cd": ["DEM", "REP", "UNA"],
        "gender_code": ["F", "M", "M"],
        "birth_year": [1980, 1, 1990],
        "age_at_year_end": [46, 1, 36],
        "birth_state": ["NC", "NC", "VA"],
    })


def test_transform_chunk_keeps_only_active_voters():
    out = transform_chunk(_raw_chunk(), {"92": "WAKE", "01": "ALAMANCE"})
    assert len(out) == 2
    assert list(out["last_name"]) == ["SMITH", "DOE"]


def test_transform_chunk_collapses_whitespace():
    out = transform_chunk(_raw_chunk(), {"92": "WAKE"})
    assert list(out["last_name"]) == ["SMITH", "DOE"]
    assert list(out["address"]) == ["1 MAIN ST", "2 OAK"]


def test_transform_chunk_maps_county_names():
    out = transform_chunk(_raw_chunk(), {"92": "WAKE"})
    assert list(out["county"]) == ["WAKE", "WAKE"]


def test_transform_chunk_unknown_county_is_nan():
    out = transform_chunk(_raw_chunk(), {})
    assert out["county"].isna().all()


def test_transform_chunk_renames_and_selects_output_columns():
    out = transform_chunk(_raw_chunk(), {"92": "WAKE"})
    assert list(out.columns) == OUTPUT_COLUMNS
    assert "res_street_address" not in out.columns


def test_transform_chunk_does_not_mutate_input():
    raw = _raw_chunk()
    before = raw.copy()
    transform_chunk(raw, {"92": "WAKE"})
    pd.testing.assert_frame_equal(raw, before)

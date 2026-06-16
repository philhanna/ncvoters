# -*- coding: utf-8 -*-
"""Domain layer: pure models and transformation services.

This module knows nothing about where data comes from or where it goes.
It operates only on pandas DataFrames and plain Python values, so it can
be exercised in tests without touching the network or the filesystem.
"""

import re

import pandas as pd

# We only want a subset of the columns.  Certain columns have additional
# whitespace that needs to be collapsed to just one space.
SANITIZED_COLUMNS = [
    'last_name',
    'first_name',
    'middle_name',
    'res_street_address',
    'res_city_desc',
]

# Source-to-output column renames applied to each chunk.
COLUMN_RENAMES = {
    "res_street_address": "address",
    "res_city_desc": "city",
    "state_cd": "state",
    "zip_code": "zip",
    "full_phone_number": "phone",
    "race_code": "race",
    "party_cd": "party",
    "gender_code": "gender",
    "birth_year": "birth_year",
    "age_at_year_end": "age",
}

# The subset of (renamed) columns kept in the output, in order.
OUTPUT_COLUMNS = [
    'last_name', 'first_name', 'middle_name', 'address', 'city',
    'county', 'state', 'zip', 'phone', 'race', 'party', 'gender',
    'birth_year', 'age', 'birth_state',
]


def transform_chunk(chunk, county_map):
    """Filter, clean, and reshape one chunk of raw voter rows.

    Keeps only active voters, collapses whitespace in name/address fields,
    adds the county name from ``county_map``, renames columns, and selects
    the output subset.  Returns a new DataFrame.
    """
    # Only active voters
    chunk = chunk[chunk['status_cd'] == 'A'].copy()

    # Clean unnecessary whitespace
    for col in SANITIZED_COLUMNS:
        if col in chunk.columns:
            chunk[col] = chunk[col].apply(sanitize)

    # Add county names.  Format county_id as a zero-padded 2-digit string so
    # the keys match county_map's keys (e.g. 1 -> "01"); missing keys map to
    # NaN.
    chunk['county_id'] = chunk['county_id'].astype(int).map(lambda n: f"{n:02d}")
    chunk['county'] = chunk['county_id'].map(county_map)

    # Rename columns and extract the output subset.
    chunk = chunk.rename(columns=COLUMN_RENAMES)
    chunk = chunk[OUTPUT_COLUMNS]
    return chunk


def sanitize(text):
    """Collapse runs of whitespace to a single space and strip the ends."""
    if pd.isna(text):  # Check for NaN or None
        return ''
    text = str(text)  # Ensure it's a string
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def parse_county_map(lines):
    """Build a map of county numbers to county names from layout lines.

    Runs a small finite state machine over the layout file's lines.  The
    county list runs from ALAMANCE (first) to YANCEY (last).
    """
    county_map = {}

    state = 0
    for line in lines:
        match state:
            case 0:
                if line.startswith("ALAMANCE"):
                    state = 1
                    name, number = line.split()
                    number = int(number)
                    number = f"{number:02d}"
                    county_map[number] = name
            case 1:
                name, number = line.split()
                number = int(number)
                number = f"{number:02d}"
                county_map[number] = name
                if line.startswith("YANCEY"):
                    state = 2
            case 2:
                break

    return county_map

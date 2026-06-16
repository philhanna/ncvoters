# -*- coding: utf-8 -*-
"""Driving adapter: the argparse command-line entry point.

This is the composition root.  It parses arguments, wires the concrete
adapters to the use case, runs it, and reports the result.
"""

import argparse
from pathlib import Path

from ncvoters.adapters.layout_http import HttpLayoutProvider
from ncvoters.adapters.sqlite_voter_db import create_sqlite_from_csv
from ncvoters.adapters.voter_csv import CsvVoterWriter
from ncvoters.adapters.voter_pandas import PandasZipVoterReader
from ncvoters.application import create_voter_csv

# Public S3 URL published by the NC State Board of Elections.
URL = "https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvoter_Statewide.zip"

# Output csv file that will contain our slimmed-down version of the database.
OUTPUT_CSV = "nc_voters.csv"

# Number of records to process per chunk.
DEFAULT_CHUNKSIZE = 100000


def main(argv=None):
    args = parse_args(argv)
    database_path = args.database or default_database_path(args.output)

    layout_provider = HttpLayoutProvider()
    voter_reader = PandasZipVoterReader(URL, args.chunksize)
    voter_writer = CsvVoterWriter(args.output)

    total_rows = create_voter_csv(layout_provider, voter_reader, voter_writer)
    create_sqlite_from_csv(args.output, database_path)
    print(
        f"Done. {total_rows} rows imported into {args.output} "
        f"and {database_path}."
    )


def default_database_path(csv_path):
    return str(Path(csv_path).with_suffix(".sqlite3"))


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="ncvoters",
        description="Create a slimmed-down CSV from NC voter registration data.")
    parser.add_argument(
        "-o", "--output",
        default=OUTPUT_CSV,
        help="Path of the output CSV file (default: %(default)s)")
    parser.add_argument(
        "-c", "--chunksize",
        type=int,
        default=DEFAULT_CHUNKSIZE,
        help="Number of records to process per chunk (default: %(default)s)")
    parser.add_argument(
        "-d", "--database",
        help="Path of the output SQLite database "
             "(default: OUTPUT with .sqlite3 suffix)")
    return parser.parse_args(argv)

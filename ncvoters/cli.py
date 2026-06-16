# -*- coding: utf-8 -*-
"""Driving adapter: the argparse command-line entry point.

This is the composition root.  It parses arguments, wires the concrete
adapters to the use case, runs it, and reports the result.
"""

import argparse
import logging
import os
import tempfile
from pathlib import Path

from ncvoters.adapters.layout_http import HttpLayoutProvider
from ncvoters.adapters.sqlite_voter_db import create_sqlite_from_csv
from ncvoters.adapters.voter_csv import CsvVoterWriter
from ncvoters.adapters.voter_pandas import PandasZipVoterReader
from ncvoters.application import create_voter_csv
from ncvoters.logging_config import configure_logging

# Public S3 URL published by the NC State Board of Elections.
URL = "https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvoter_Statewide.zip"

# Number of records to process per chunk.
DEFAULT_CHUNKSIZE = 100000
logger = logging.getLogger(__name__)


def default_output_db():
    """Return the default database path on the current user's Desktop."""
    if os.name == "nt":
        desktop = Path(os.environ.get("USERPROFILE", Path.home())) / "Desktop"
    else:
        desktop = Path.home() / "Desktop"
    return str(desktop / "nc_voters.db")


OUTPUT_DB = default_output_db()


def main(argv=None):
    configure_logging()
    args = parse_args(argv)
    database_path = args.output
    intermediate_csv = temporary_csv_path()

    layout_provider = HttpLayoutProvider()
    voter_reader = PandasZipVoterReader(URL, args.chunksize)
    voter_writer = CsvVoterWriter(intermediate_csv)

    try:
        total_rows = create_voter_csv(layout_provider, voter_reader, voter_writer)
        create_sqlite_from_csv(intermediate_csv, database_path)
    finally:
        if os.path.exists(intermediate_csv):
            os.remove(intermediate_csv)
    logger.info("Done. %s rows imported into %s.", total_rows, database_path)


def temporary_csv_path():
    db_stem = "nc_voters"
    with tempfile.NamedTemporaryFile(
        prefix=f"{db_stem}.",
        suffix=".csv",
        dir=tempfile.gettempdir(),
        delete=False,
    ) as temp_file:
        return temp_file.name


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="ncvoters",
        description="Create a SQLite database from NC voter registration data.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=OUTPUT_DB,
        help="Path of the output SQLite database (default: %(default)s)",
    )
    parser.add_argument(
        "-c",
        "--chunksize",
        type=int,
        default=DEFAULT_CHUNKSIZE,
        help="Number of records to process per chunk (default: %(default)s)",
    )
    return parser.parse_args(argv)

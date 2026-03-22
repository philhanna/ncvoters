"""CLI entry point — wires up adapters and runs use cases."""

import argparse
import logging
import sys
import tempfile
from pathlib import Path

from ncvoters.adapters.config_loader import YamlConfigLoader
from ncvoters.adapters.downloader import HttpFileDownloader
from ncvoters.adapters.layout_fetcher import NcboeLayoutFetcher
from ncvoters.adapters.sqlite_repo import SqliteVoterRepository
from ncvoters.application.use_cases import AddMetadata, CreateVoterDatabase

_DEFAULT_ZIP = str(Path(tempfile.gettempdir()) / "voter_data.zip")
_DEFAULT_DB = str(Path(tempfile.gettempdir()) / "voter_data.db")

_USAGE = """\
usage: get-voter-data [OPTIONS] [DBNAME]

Creates a database of North Carolina voter registrations

positional arguments:
  dbname          Name of the SQLite database file to create
                  (default: /tmp/voter_data.db)

options:
  -h, --help      Show this help text and exit
  -f, --force     Force the zip file to be re-downloaded even if it exists
  -l N, --limit N Maximum number of voter records to import (0 = no limit)
  -m, --metadata  Add metadata lookup tables (columns, race/ethnic/county codes, etc.)
  -q, --quiet     Suppress all progress output
"""


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False, usage=argparse.SUPPRESS)
    parser.add_argument("-h", "--help", action="store_true", default=False)
    parser.add_argument("-f", "--force", action="store_true", default=False)
    parser.add_argument("-l", "--limit", type=int, default=0, metavar="N")
    parser.add_argument("-m", "--metadata", action="store_true", default=False)
    parser.add_argument("-q", "--quiet", action="store_true", default=False)
    parser.add_argument("dbname", nargs="?", default=_DEFAULT_DB)
    return parser


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(filename)s:%(lineno)d %(message)s",
        stream=sys.stderr,
    )

    args = _build_parser().parse_args()

    if args.help:
        print(_USAGE)
        sys.exit(0)

    if args.quiet:
        logging.disable(logging.CRITICAL)

    # ---------------------------------------------------------------
    # Load configuration (primary adapter drives everything else)
    # ---------------------------------------------------------------
    config_loader = YamlConfigLoader()
    try:
        config = config_loader.load()
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    # ---------------------------------------------------------------
    # Wire up secondary (outbound) adapters
    # ---------------------------------------------------------------
    downloader = HttpFileDownloader(quiet=args.quiet)
    repo = SqliteVoterRepository(args.dbname, config)

    # ---------------------------------------------------------------
    # Execute use cases
    # ---------------------------------------------------------------
    CreateVoterDatabase(config, downloader, repo, quiet=args.quiet).execute(
        zip_path=_DEFAULT_ZIP,
        db_path=args.dbname,
        force=args.force,
        max_entries=args.limit,
    )

    if args.metadata:
        AddMetadata(NcboeLayoutFetcher(), repo, quiet=args.quiet).execute()

    if not args.quiet:
        logging.getLogger(__name__).info("Process completed successfully!")

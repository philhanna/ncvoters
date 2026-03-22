# ncvoters.cli.apply_views
"""CLI entry point for applying views to an existing database."""

import argparse
import logging
import sys
import tempfile
from pathlib import Path

from ncvoters.adapters.config_loader import YamlConfigLoader
from ncvoters.adapters.sqlite_repo import SqliteVoterRepository
from ncvoters.application.use_cases import ApplyViews

_DEFAULT_DB = str(Path(tempfile.gettempdir()) / "voter_data.db")
_DEFAULT_VIEWS_DIR = Path.home() / ".config" / "ncvoters" / "views"

_USAGE = """\
usage: apply-views [OPTIONS] [DBNAME]

Applies view definitions from ~/.config/ncvoters/views/ to an existing
database.  New views are created; changed views are dropped and recreated;
unchanged views are skipped.  Each view is attempted independently.

positional arguments:
  dbname          Path to the SQLite database file
                  (default: /tmp/voter_data.db)

options:
  -h, --help      Show this help text and exit
  -q, --quiet     Suppress all progress output
"""


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False, usage=argparse.SUPPRESS)
    parser.add_argument("-h", "--help", action="store_true", default=False)
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

    if not Path(args.dbname).exists():
        print(f"Error: database not found: {args.dbname}", file=sys.stderr)
        sys.exit(1)

    config_loader = YamlConfigLoader()
    try:
        config = config_loader.load()
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    repo = SqliteVoterRepository(args.dbname, config)
    ApplyViews(repo, _DEFAULT_VIEWS_DIR, quiet=args.quiet).execute(incremental=True)

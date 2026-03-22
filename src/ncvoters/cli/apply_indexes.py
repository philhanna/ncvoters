# ncvoters.cli.apply_indexes
"""CLI entry point for applying indexes to an existing database."""

import argparse
import logging
import sys
from pathlib import Path

from ncvoters.adapters.config_loader import YamlConfigLoader
from ncvoters.adapters.sqlite_repo import SqliteVoterRepository
from ncvoters.application.use_cases import ApplyIndexes
from ncvoters.cli.main import resolve_db_path

_DEFAULT_INDEXES_DIR = Path.home() / ".config" / "ncvoters" / "indexes"

_USAGE = """\
usage: apply-indexes [OPTIONS] [DBNAME]

Applies index definitions from ~/.config/ncvoters/indexes/ to an existing
database.  New indexes are created; changed indexes are dropped and recreated;
unchanged indexes are skipped.  Each index is attempted independently.

positional arguments:
  dbname          Path to the SQLite database file.
                  Overrides db_dir from config.yaml.
                  Default: db_dir/voter_data.db from config, or /tmp/voter_data.db.

options:
  -h, --help      Show this help text and exit
  -q, --quiet     Suppress all progress output
"""


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False, usage=argparse.SUPPRESS)
    parser.add_argument("-h", "--help", action="store_true", default=False)
    parser.add_argument("-q", "--quiet", action="store_true", default=False)
    parser.add_argument("dbname", nargs="?", default=None)
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

    config_loader = YamlConfigLoader()
    try:
        config = config_loader.load()
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    db_path = resolve_db_path(args.dbname, config.db_dir)

    if not Path(db_path).exists():
        print(f"Error: database not found: {db_path}", file=sys.stderr)
        sys.exit(1)

    repo = SqliteVoterRepository(db_path, config)
    ApplyIndexes(repo, _DEFAULT_INDEXES_DIR, quiet=args.quiet).execute(incremental=True)

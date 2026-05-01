#!/usr/bin/env python3
"""Apply SQL view files from ~/.config/ncvoters/views/ to the voter database."""

import re
import sqlite3
import sys
import tempfile
from pathlib import Path

import yaml

# Standard locations for config and user-defined view SQL files.

CONFIG_PATH = Path.home() / ".config" / "ncvoters" / "config.yaml"
VIEWS_DIR = Path.home() / ".config" / "ncvoters" / "views"

# Extracts the view name so we can DROP it before recreating, making each run idempotent.

_VIEW_NAME = re.compile(r"CREATE\s+VIEW\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)", re.IGNORECASE)


def resolve_db_path(cli_arg: str | None) -> str:
    """Return the path to voter_data.db, in priority order.

    Priority:
        1. cli_arg, if provided.
        2. <db_dir>/voter_data.db from CONFIG_PATH, if db_dir is set.
        3. <tempdir>/voter_data.db as a final fallback.

    Args:
        cli_arg: Path passed on the command line, or None.

    Returns:
        Absolute path string for the SQLite database file.
    """
    if cli_arg:
        return cli_arg
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        db_dir = config.get("db_dir")

        # db_dir may contain "~", so expanduser is required.

        if db_dir:
            return str(Path(db_dir).expanduser() / "voter_data.db")
    except FileNotFoundError:
        pass
    return str(Path(tempfile.gettempdir()) / "voter_data.db")


def apply_views(db_path: str) -> None:
    """Apply all SQL view files from VIEWS_DIR to the database.

    Each .sql file is applied in alphabetical order. The existing view is
    dropped before each CREATE VIEW so the operation is idempotent. Progress
    is reported to stderr.

    Args:
        db_path: Path to the SQLite database file.
    """
    # Sort files so views are applied in a predictable, alphabetical order.

    sql_files = sorted(VIEWS_DIR.glob("*.sql"))
    if not sql_files:
        print(f"No view files found in {VIEWS_DIR}", file=sys.stderr)
        return

    print(f"Applying views to {db_path}", file=sys.stderr)
    conn = sqlite3.connect(db_path)
    try:
        for path in sql_files:
            sql = path.read_text(encoding="utf-8").strip()

            # Fall back to the filename stem if the regex can't parse the view name.

            m = _VIEW_NAME.search(sql)
            name = m.group(1) if m else path.stem
            conn.execute(f"DROP VIEW IF EXISTS {name}")
            conn.execute(sql)
            conn.commit()
            print(f"  {name} — applied", file=sys.stderr)
    finally:
        conn.close()
    print("Done.", file=sys.stderr)


if __name__ == "__main__":
    db_path = resolve_db_path(sys.argv[1] if len(sys.argv) > 1 else None)
    apply_views(db_path)

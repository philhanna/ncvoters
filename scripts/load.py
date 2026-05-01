#!/usr/bin/env python3
"""Load selected columns from the voter txt file into SQLite."""

import csv
import re
import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import yaml

CONFIG_PATH = Path.home() / ".config" / "ncvoters" / "config.yaml"
DEFAULT_TXT = "/tmp/ncvoter_Statewide.txt"

# Number of rows accumulated before flushing to disk. Large enough to amortize
# SQLite commit overhead without consuming excessive memory.

BATCH_SIZE = 10_000

# Collapses runs of whitespace in sanitized columns to a single space.

_WS = re.compile(r"\s+")


def load_config() -> dict:
    """Load and return the YAML config from CONFIG_PATH.

    Returns:
        Parsed config dict. Expected keys include selected_columns and
        optionally db_dir and sanitize_columns.

    Raises:
        FileNotFoundError: If CONFIG_PATH does not exist.
    """
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_db_path(config: dict, cli_arg: str | None) -> str:
    """Return the path to voter_data.db, in priority order.

    Priority:
        1. cli_arg, if provided.
        2. <db_dir>/voter_data.db from config, if db_dir is set.
        3. <tempdir>/voter_data.db as a final fallback.

    Args:
        config: Parsed config dict, typically from load_config().
        cli_arg: Path passed on the command line, or None.

    Returns:
        Absolute path string for the SQLite database file.
    """
    if cli_arg:
        return cli_arg
    db_dir = config.get("db_dir")

    # db_dir may contain "~", so expanduser is required.

    if db_dir:
        return str(Path(db_dir).expanduser() / "voter_data.db")
    return str(Path(tempfile.gettempdir()) / "voter_data.db")


def rename_existing(db_path: str) -> None:
    """Rename an existing database file to a timestamped backup.

    If no file exists at db_path this is a no-op. The backup name follows the
    pattern <stem>_YYYYMMDD_HHMMSS<suffix>, e.g. voter_data_20240315_143022.db.

    Args:
        db_path: Path to the database file to back up.
    """
    p = Path(db_path)
    if not p.exists():
        return

    # Preserve the old database with a timestamp suffix instead of deleting it,
    # so a failed reload doesn't destroy the last good copy.

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = p.with_name(f"{p.stem}_{ts}{p.suffix}")
    p.rename(backup)
    print(f"Renamed existing database to {backup}", file=sys.stderr)


def load(txt_path: str, db_path: str, config: dict) -> None:
    """Load voter records from a tab-separated txt file into a new SQLite database.

    Creates a fresh voters table containing only the columns listed in
    config['selected_columns']. Columns in config['sanitize_columns'] have
    interior whitespace collapsed to a single space. Rows are inserted in
    batches of BATCH_SIZE. An existing database at db_path is renamed to a
    timestamped backup before the new one is created.

    Args:
        txt_path: Path to the Latin-1 encoded, tab-delimited voter data file.
        db_path: Destination path for the SQLite database.
        config: Parsed config dict with at least a selected_columns key.
    """
    selected = config["selected_columns"]

    # Columns listed under sanitize_columns have interior whitespace normalized
    # (e.g. double spaces in address fields from the raw export).

    sanitize = set(config.get("sanitize_columns", []))

    print(f"Loading {txt_path}", file=sys.stderr)
    print(f"     -> {db_path}", file=sys.stderr)

    rename_existing(db_path)

    conn = sqlite3.connect(db_path)
    try:
        # Create the table with only the columns the config requests, all TEXT
        # since the source file has no numeric fields we compute on.

        cols_def = ", ".join(f'"{c}" TEXT' for c in selected)
        conn.execute(f"CREATE TABLE voters ({cols_def})")

        placeholders = ", ".join("?" * len(selected))
        insert_sql = f"INSERT INTO voters VALUES ({placeholders})"

        # The NC SBE file uses Latin-1 encoding and tab-separated values.

        with open(txt_path, encoding="latin-1", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            batch = []
            count = 0
            for row in reader:
                values = [
                    _WS.sub(" ", row.get(col, "")).strip() if col in sanitize
                    else row.get(col, "")
                    for col in selected
                ]
                batch.append(values)
                count += 1
                if len(batch) >= BATCH_SIZE:
                    conn.executemany(insert_sql, batch)
                    conn.commit()
                    batch = []
                    print(f"\r  {count:,} rows", end="", file=sys.stderr, flush=True)

            # Flush any remaining rows that didn't fill a complete batch.

            if batch:
                conn.executemany(insert_sql, batch)
                conn.commit()

        print(f"\r  {count:,} rows loaded.", file=sys.stderr)
    finally:
        conn.close()


if __name__ == "__main__":
    config = load_config()
    txt_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TXT
    db_path = resolve_db_path(config, sys.argv[2] if len(sys.argv) > 2 else None)
    load(txt_path, db_path, config)

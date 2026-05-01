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
BATCH_SIZE = 10_000
_WS = re.compile(r"\s+")


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_db_path(config: dict, cli_arg: str | None) -> str:
    if cli_arg:
        return cli_arg
    db_dir = config.get("db_dir")
    if db_dir:
        return str(Path(db_dir).expanduser() / "voter_data.db")
    return str(Path(tempfile.gettempdir()) / "voter_data.db")


def rename_existing(db_path: str) -> None:
    p = Path(db_path)
    if not p.exists():
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = p.with_name(f"{p.stem}_{ts}{p.suffix}")
    p.rename(backup)
    print(f"Renamed existing database to {backup}", file=sys.stderr)


def load(txt_path: str, db_path: str, config: dict) -> None:
    selected = config["selected_columns"]
    sanitize = set(config.get("sanitize_columns", []))

    print(f"Loading {txt_path}", file=sys.stderr)
    print(f"     -> {db_path}", file=sys.stderr)

    rename_existing(db_path)

    conn = sqlite3.connect(db_path)
    try:
        cols_def = ", ".join(f'"{c}" TEXT' for c in selected)
        conn.execute(f"CREATE TABLE voters ({cols_def})")

        placeholders = ", ".join("?" * len(selected))
        insert_sql = f"INSERT INTO voters VALUES ({placeholders})"

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

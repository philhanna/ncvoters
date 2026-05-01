#!/usr/bin/env python3
"""Apply SQL view files from ~/.config/ncvoters/views/ to the voter database."""

import re
import sqlite3
import sys
import tempfile
from pathlib import Path

import yaml

CONFIG_PATH = Path.home() / ".config" / "ncvoters" / "config.yaml"
VIEWS_DIR = Path.home() / ".config" / "ncvoters" / "views"

_VIEW_NAME = re.compile(r"CREATE\s+VIEW\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)", re.IGNORECASE)


def resolve_db_path(cli_arg: str | None) -> str:
    if cli_arg:
        return cli_arg
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        db_dir = config.get("db_dir")
        if db_dir:
            return str(Path(db_dir).expanduser() / "voter_data.db")
    except FileNotFoundError:
        pass
    return str(Path(tempfile.gettempdir()) / "voter_data.db")


def apply_views(db_path: str) -> None:
    sql_files = sorted(VIEWS_DIR.glob("*.sql"))
    if not sql_files:
        print(f"No view files found in {VIEWS_DIR}", file=sys.stderr)
        return

    print(f"Applying views to {db_path}", file=sys.stderr)
    conn = sqlite3.connect(db_path)
    try:
        for path in sql_files:
            sql = path.read_text(encoding="utf-8").strip()
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

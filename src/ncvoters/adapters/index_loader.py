# ncvoters.adapters.index_loader
"""Discovers and parses SQL index files from the indexes directory."""

import re
from pathlib import Path

from ncvoters.adapters.view_loader import normalise_sql

_INDEX_NAME_RE = re.compile(r"CREATE\s+(?:UNIQUE\s+)?INDEX\s+(\w+)", re.IGNORECASE)


def load_index_files(indexes_dir: Path) -> list[tuple[str, str]]:
    """Return (filename, sql) pairs for every .sql file, sorted by filename."""
    if not indexes_dir.exists():
        return []
    return [
        (p.name, p.read_text(encoding="utf-8").strip())
        for p in sorted(indexes_dir.glob("*.sql"))
    ]


def extract_index_name(sql: str) -> str:
    """Parse the index name from a CREATE INDEX statement."""
    m = _INDEX_NAME_RE.search(sql)
    if not m:
        raise ValueError(f"Cannot extract index name from SQL: {sql[:80]!r}")
    return m.group(1)


__all__ = ["load_index_files", "extract_index_name", "normalise_sql"]

# ncvoters.adapters.view_loader
"""Discovers and parses SQL view files from the views directory."""

import re
from pathlib import Path

_VIEW_NAME_RE = re.compile(r"CREATE\s+VIEW\s+(\w+)", re.IGNORECASE)
_WS_RE = re.compile(r"\s+")


def load_view_files(views_dir: Path) -> list[tuple[str, str]]:
    """Return (filename, sql) pairs for every .sql file, sorted by filename."""
    if not views_dir.exists():
        return []
    return [
        (p.name, p.read_text(encoding="utf-8").strip())
        for p in sorted(views_dir.glob("*.sql"))
    ]


def extract_view_name(sql: str) -> str:
    """Parse the view name from a CREATE VIEW statement."""
    m = _VIEW_NAME_RE.search(sql)
    if not m:
        raise ValueError(f"Cannot extract view name from SQL: {sql[:80]!r}")
    return m.group(1)


def normalise_sql(sql: str) -> str:
    """Collapse whitespace for comparison purposes."""
    return _WS_RE.sub(" ", sql).strip()

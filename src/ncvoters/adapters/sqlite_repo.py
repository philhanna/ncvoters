import sqlite3
from typing import Iterator

from ncvoters.domain.models import Configuration, Layout
from ncvoters.ports.outbound import VoterRepositoryPort


class SqliteVoterRepository(VoterRepositoryPort):
    """Persists voter data to a SQLite database file."""

    def __init__(self, db_path: str, config: Configuration) -> None:
        self._db_path = db_path
        self._config = config

    # ------------------------------------------------------------------
    # VoterRepositoryPort
    # ------------------------------------------------------------------

    def create_voters_table(self, columns: list[str]) -> None:
        col_defs = ",\n".join(f"  {col:<20} TEXT" for col in columns)
        ddl = f"CREATE TABLE IF NOT EXISTS voters (\n{col_defs}\n)"
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(ddl)

    def insert_voters(self, rows: Iterator[list[str]]) -> None:
        cols = self._config.selected_columns
        placeholders = ",".join("?" * len(cols))
        sql = f"INSERT INTO voters ({','.join(cols)}) VALUES ({placeholders})"
        with sqlite3.connect(self._db_path) as conn:
            conn.executemany(sql, rows)

    def create_indexes(self) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("CREATE INDEX names ON voters (last_name, first_name, middle_name)")
            conn.execute("CREATE INDEX addresses ON voters (res_street_address)")

    def apply_view(self, sql: str) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(sql)

    def existing_view_sql(self, name: str) -> str | None:
        with sqlite3.connect(self._db_path) as conn:
            row = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='view' AND name=?", (name,)
            ).fetchone()
        return row[0] if row else None

    def add_metadata(self, layout: Layout) -> None:
        script = _build_metadata_script(layout)
        with sqlite3.connect(self._db_path) as conn:
            conn.executescript(script)


# ---------------------------------------------------------------------------
# DDL builder (pure function)
# ---------------------------------------------------------------------------

def _esc(s: str) -> str:
    """Escape single quotes for SQLite string literals."""
    return s.replace("'", "''")


def _build_metadata_script(layout: Layout) -> str:
    parts: list[str] = []

    # columns table
    parts.append("CREATE TABLE columns (name TEXT, dataType TEXT, description TEXT);")
    for col in layout.all_columns:
        parts.append(
            f"INSERT INTO columns VALUES('{_esc(col.name)}','{_esc(col.data_type)}','{_esc(col.description)}');"
        )

    # status_codes table
    parts.append("CREATE TABLE status_codes (status TEXT, description TEXT);")
    for code in sorted(layout.status_codes):
        parts.append(
            f"INSERT INTO status_codes VALUES('{_esc(code)}','{_esc(layout.status_codes[code])}');"
        )

    # race_codes table
    parts.append("CREATE TABLE race_codes (race TEXT, description TEXT);")
    for code in sorted(layout.race_codes):
        parts.append(
            f"INSERT INTO race_codes VALUES('{_esc(code)}','{_esc(layout.race_codes[code])}');"
        )

    # ethnic_codes table
    parts.append("CREATE TABLE ethnic_codes (ethnic TEXT, description TEXT);")
    for code in sorted(layout.ethnic_codes):
        parts.append(
            f"INSERT INTO ethnic_codes VALUES('{_esc(code)}','{_esc(layout.ethnic_codes[code])}');"
        )

    # county_codes table
    parts.append("CREATE TABLE county_codes (county_id INTEGER, county TEXT);")
    for code_id in sorted(layout.county_codes):
        parts.append(
            f"INSERT INTO county_codes VALUES({code_id},'{_esc(layout.county_codes[code_id])}');"
        )

    # reason_codes table
    parts.append("CREATE TABLE reason_codes (reason TEXT, description TEXT);")
    for code in sorted(layout.reason_codes):
        parts.append(
            f"INSERT INTO reason_codes VALUES('{_esc(code)}','{_esc(layout.reason_codes[code])}');"
        )

    return "\n".join(parts) + "\n"

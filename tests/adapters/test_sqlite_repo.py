import sqlite3

from ncvoters.adapters.sqlite_repo import SqliteVoterRepository
from ncvoters.domain.models import Configuration


def _make_repo(tmp_path):
    db = str(tmp_path / "test.db")
    config = Configuration(
        selected_columns=["last_name", "first_name"],
        sanitize_columns=["last_name"],
    )
    repo = SqliteVoterRepository(db, config)
    repo.create_voters_table(config.selected_columns)
    return db, repo


def test_create_and_insert(tmp_path) -> None:
    db, repo = _make_repo(tmp_path)
    repo.insert_voters(iter([["Smith", "John"], ["Doe", "Jane"]]))

    with sqlite3.connect(db) as conn:
        rows = conn.execute("SELECT last_name, first_name FROM voters ORDER BY last_name").fetchall()
    assert rows == [("Doe", "Jane"), ("Smith", "John")]


def test_apply_view_creates_view(tmp_path) -> None:
    db, repo = _make_repo(tmp_path)
    repo.insert_voters(iter([["Smith", "John"]]))
    repo.apply_view("CREATE VIEW smiths AS SELECT * FROM voters WHERE last_name = 'SMITH'")

    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='view' AND name='smiths'"
        ).fetchone()
    assert row is not None


def test_existing_view_sql_returns_none_when_absent(tmp_path) -> None:
    _, repo = _make_repo(tmp_path)
    assert repo.existing_view_sql("no_such_view") is None


def test_existing_view_sql_returns_sql_after_creation(tmp_path) -> None:
    db, repo = _make_repo(tmp_path)
    sql = "CREATE VIEW smiths AS SELECT * FROM voters WHERE last_name = 'SMITH'"
    repo.apply_view(sql)
    stored = repo.existing_view_sql("smiths")
    assert stored is not None
    assert "smiths" in stored

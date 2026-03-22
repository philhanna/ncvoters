from ncvoters.adapters.sqlite_repo import SqliteVoterRepository
from ncvoters.domain.models import Configuration


def test_create_and_insert(tmp_path) -> None:
    db = str(tmp_path / "test.db")
    config = Configuration(
        selected_columns=["last_name", "first_name"],
        sanitize_columns=["last_name"],
    )
    repo = SqliteVoterRepository(db, config)
    repo.create_voters_table(config.selected_columns)
    repo.insert_voters(iter([["Smith", "John"], ["Doe", "Jane"]]))

    import sqlite3
    with sqlite3.connect(db) as conn:
        rows = conn.execute("SELECT last_name, first_name FROM voters ORDER BY last_name").fetchall()
    assert rows == [("Doe", "Jane"), ("Smith", "John")]

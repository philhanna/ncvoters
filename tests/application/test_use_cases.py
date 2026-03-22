"""Tests for the ApplyIndexes, ApplyViews, and rename-on-rebuild use cases."""

import sqlite3

import pytest

from ncvoters.adapters.sqlite_repo import SqliteVoterRepository
from ncvoters.application.use_cases import ApplyIndexes, ApplyViews, _rename_existing_db
from ncvoters.domain.models import Configuration


def _make_repo(db_path: str) -> SqliteVoterRepository:
    config = Configuration(
        selected_columns=["last_name", "first_name"],
        sanitize_columns=[],
    )
    repo = SqliteVoterRepository(db_path, config)
    repo.create_voters_table(config.selected_columns)
    return repo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_view(views_dir, filename: str, sql: str) -> None:
    (views_dir / filename).write_text(sql, encoding="utf-8")


# ---------------------------------------------------------------------------
# ApplyViews — full-build mode (incremental=False)
# ---------------------------------------------------------------------------

def test_apply_views_creates_new_view(tmp_path) -> None:
    db = str(tmp_path / "v.db")
    repo = _make_repo(db)
    views_dir = tmp_path / "views"
    views_dir.mkdir()
    _write_view(views_dir, "everyone.sql", "CREATE VIEW everyone AS SELECT * FROM voters")

    result = ApplyViews(repo, views_dir, quiet=True).execute(incremental=False)

    assert "everyone" in result.applied
    assert result.skipped == []
    assert result.failed == []


def test_apply_views_empty_dir_returns_empty_result(tmp_path) -> None:
    db = str(tmp_path / "v.db")
    repo = _make_repo(db)
    views_dir = tmp_path / "views"
    views_dir.mkdir()

    result = ApplyViews(repo, views_dir, quiet=True).execute(incremental=False)

    assert result.applied == []
    assert result.skipped == []
    assert result.failed == []


def test_apply_views_missing_dir_returns_empty_result(tmp_path) -> None:
    db = str(tmp_path / "v.db")
    repo = _make_repo(db)

    result = ApplyViews(repo, tmp_path / "no_views", quiet=True).execute(incremental=False)

    assert result.applied == []


def test_apply_views_bad_sql_goes_to_failed(tmp_path) -> None:
    db = str(tmp_path / "v.db")
    repo = _make_repo(db)
    views_dir = tmp_path / "views"
    views_dir.mkdir()
    # Genuine syntax error — misspelled keyword
    _write_view(views_dir, "bad.sql", "CREATE VIEW bad AS SLECT * FROM voters")

    result = ApplyViews(repo, views_dir, quiet=True).execute(incremental=False)

    assert len(result.failed) == 1
    assert result.failed[0][0] == "bad"
    assert result.applied == []


def test_apply_views_invalid_sql_filename_goes_to_failed(tmp_path) -> None:
    db = str(tmp_path / "v.db")
    repo = _make_repo(db)
    views_dir = tmp_path / "views"
    views_dir.mkdir()
    _write_view(views_dir, "notaview.sql", "SELECT 1")  # no CREATE VIEW

    result = ApplyViews(repo, views_dir, quiet=True).execute(incremental=False)

    assert len(result.failed) == 1
    assert result.applied == []


# ---------------------------------------------------------------------------
# ApplyViews — incremental mode (incremental=True)
# ---------------------------------------------------------------------------

def test_incremental_skips_unchanged_view(tmp_path) -> None:
    db = str(tmp_path / "v.db")
    repo = _make_repo(db)
    views_dir = tmp_path / "views"
    views_dir.mkdir()
    sql = "CREATE VIEW everyone AS SELECT * FROM voters"
    _write_view(views_dir, "everyone.sql", sql)

    # First apply
    ApplyViews(repo, views_dir, quiet=True).execute(incremental=False)

    # Second apply — should skip
    result = ApplyViews(repo, views_dir, quiet=True).execute(incremental=True)

    assert "everyone" in result.skipped
    assert result.applied == []


def test_incremental_recreates_changed_view(tmp_path) -> None:
    db = str(tmp_path / "v.db")
    repo = _make_repo(db)
    views_dir = tmp_path / "views"
    views_dir.mkdir()
    _write_view(views_dir, "everyone.sql", "CREATE VIEW everyone AS SELECT * FROM voters")

    ApplyViews(repo, views_dir, quiet=True).execute(incremental=False)

    # Change the SQL
    _write_view(views_dir, "everyone.sql", "CREATE VIEW everyone AS SELECT last_name FROM voters")
    result = ApplyViews(repo, views_dir, quiet=True).execute(incremental=True)

    assert "everyone" in result.applied
    assert result.skipped == []

    # Verify the new definition is in sqlite_master
    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='view' AND name='everyone'"
        ).fetchone()
    assert "last_name" in (row[0] if row else "")


def test_incremental_creates_new_view_not_yet_in_db(tmp_path) -> None:
    db = str(tmp_path / "v.db")
    repo = _make_repo(db)
    views_dir = tmp_path / "views"
    views_dir.mkdir()

    # Start with one view applied
    _write_view(views_dir, "view_a.sql", "CREATE VIEW view_a AS SELECT * FROM voters")
    ApplyViews(repo, views_dir, quiet=True).execute(incremental=False)

    # Add a second view file
    _write_view(views_dir, "view_b.sql", "CREATE VIEW view_b AS SELECT last_name FROM voters")
    result = ApplyViews(repo, views_dir, quiet=True).execute(incremental=True)

    assert "view_b" in result.applied
    assert "view_a" in result.skipped


def test_incremental_failure_does_not_abort_remaining_views(tmp_path) -> None:
    db = str(tmp_path / "v.db")
    repo = _make_repo(db)
    views_dir = tmp_path / "views"
    views_dir.mkdir()
    # Genuine syntax error so SQLite rejects it at CREATE time
    _write_view(views_dir, "bad.sql", "CREATE VIEW bad AS SLECT * FROM voters")
    _write_view(views_dir, "good.sql", "CREATE VIEW good AS SELECT * FROM voters")

    result = ApplyViews(repo, views_dir, quiet=True).execute(incremental=False)

    assert "good" in result.applied
    assert len(result.failed) == 1


# ===========================================================================
# ApplyIndexes tests
# ===========================================================================

def _write_index(indexes_dir, filename: str, sql: str) -> None:
    (indexes_dir / filename).write_text(sql, encoding="utf-8")


# ---------------------------------------------------------------------------
# ApplyIndexes — full-build mode (incremental=False)
# ---------------------------------------------------------------------------

def test_apply_indexes_creates_new_index(tmp_path) -> None:
    db = str(tmp_path / "i.db")
    repo = _make_repo(db)
    indexes_dir = tmp_path / "indexes"
    indexes_dir.mkdir()
    _write_index(indexes_dir, "names.sql", "CREATE INDEX names ON voters (last_name, first_name)")

    result = ApplyIndexes(repo, indexes_dir, quiet=True).execute(incremental=False)

    assert "names" in result.applied
    assert result.skipped == []
    assert result.failed == []


def test_apply_indexes_empty_dir_returns_empty_result(tmp_path) -> None:
    db = str(tmp_path / "i.db")
    repo = _make_repo(db)
    indexes_dir = tmp_path / "indexes"
    indexes_dir.mkdir()

    result = ApplyIndexes(repo, indexes_dir, quiet=True).execute(incremental=False)

    assert result.applied == []
    assert result.skipped == []
    assert result.failed == []


def test_apply_indexes_missing_dir_returns_empty_result(tmp_path) -> None:
    db = str(tmp_path / "i.db")
    repo = _make_repo(db)

    result = ApplyIndexes(repo, tmp_path / "no_indexes", quiet=True).execute(incremental=False)

    assert result.applied == []


def test_apply_indexes_bad_sql_goes_to_failed(tmp_path) -> None:
    db = str(tmp_path / "i.db")
    repo = _make_repo(db)
    indexes_dir = tmp_path / "indexes"
    indexes_dir.mkdir()
    _write_index(indexes_dir, "bad.sql", "CREATE INDEX bad ON voters (no_such_col FOOBAR)")

    result = ApplyIndexes(repo, indexes_dir, quiet=True).execute(incremental=False)

    assert len(result.failed) == 1
    assert result.failed[0][0] == "bad"
    assert result.applied == []


def test_apply_indexes_invalid_sql_goes_to_failed(tmp_path) -> None:
    db = str(tmp_path / "i.db")
    repo = _make_repo(db)
    indexes_dir = tmp_path / "indexes"
    indexes_dir.mkdir()
    _write_index(indexes_dir, "notanindex.sql", "SELECT 1")  # no CREATE INDEX

    result = ApplyIndexes(repo, indexes_dir, quiet=True).execute(incremental=False)

    assert len(result.failed) == 1
    assert result.applied == []


# ---------------------------------------------------------------------------
# ApplyIndexes — incremental mode (incremental=True)
# ---------------------------------------------------------------------------

def test_apply_indexes_incremental_skips_unchanged(tmp_path) -> None:
    db = str(tmp_path / "i.db")
    repo = _make_repo(db)
    indexes_dir = tmp_path / "indexes"
    indexes_dir.mkdir()
    sql = "CREATE INDEX names ON voters (last_name, first_name)"
    _write_index(indexes_dir, "names.sql", sql)

    ApplyIndexes(repo, indexes_dir, quiet=True).execute(incremental=False)
    result = ApplyIndexes(repo, indexes_dir, quiet=True).execute(incremental=True)

    assert "names" in result.skipped
    assert result.applied == []


def test_apply_indexes_incremental_recreates_changed(tmp_path) -> None:
    db = str(tmp_path / "i.db")
    repo = _make_repo(db)
    indexes_dir = tmp_path / "indexes"
    indexes_dir.mkdir()
    _write_index(indexes_dir, "names.sql", "CREATE INDEX names ON voters (last_name)")

    ApplyIndexes(repo, indexes_dir, quiet=True).execute(incremental=False)

    _write_index(indexes_dir, "names.sql", "CREATE INDEX names ON voters (last_name, first_name)")
    result = ApplyIndexes(repo, indexes_dir, quiet=True).execute(incremental=True)

    assert "names" in result.applied
    assert result.skipped == []

    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='index' AND name='names'"
        ).fetchone()
    assert "first_name" in (row[0] if row else "")


def test_apply_indexes_incremental_failure_does_not_abort(tmp_path) -> None:
    db = str(tmp_path / "i.db")
    repo = _make_repo(db)
    indexes_dir = tmp_path / "indexes"
    indexes_dir.mkdir()
    _write_index(indexes_dir, "bad.sql", "CREATE INDEX bad ON voters (no_col OOPS)")
    _write_index(indexes_dir, "good.sql", "CREATE INDEX good ON voters (last_name)")

    result = ApplyIndexes(repo, indexes_dir, quiet=True).execute(incremental=False)

    assert "good" in result.applied
    assert len(result.failed) == 1


# ===========================================================================
# _rename_existing_db tests
# ===========================================================================

def test_rename_existing_db_renames_file(tmp_path) -> None:
    db = tmp_path / "voter_data.db"
    db.write_bytes(b"dummy")

    _rename_existing_db(str(db))

    assert not db.exists()
    backups = list(tmp_path.glob("voter_data_*.db"))
    assert len(backups) == 1


def test_rename_existing_db_backup_name_contains_timestamp(tmp_path) -> None:
    db = tmp_path / "voter_data.db"
    db.write_bytes(b"dummy")

    _rename_existing_db(str(db))

    backup = list(tmp_path.glob("voter_data_*.db"))[0]
    # Name should be voter_data_YYYYMMDD_HHMMSS.db — 15 extra chars after stem
    assert len(backup.stem) == len("voter_data_") + len("YYYYMMDD_HHMMSS")


def test_rename_existing_db_noop_when_absent(tmp_path) -> None:
    db = tmp_path / "voter_data.db"
    # File does not exist — should not raise
    _rename_existing_db(str(db))
    assert list(tmp_path.glob("voter_data_*.db")) == []

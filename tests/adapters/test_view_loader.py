import pytest

from ncvoters.adapters.view_loader import extract_view_name, load_view_files, normalise_sql


# ---------------------------------------------------------------------------
# load_view_files
# ---------------------------------------------------------------------------

def test_load_view_files_returns_sorted_pairs(tmp_path) -> None:
    (tmp_path / "beta.sql").write_text("CREATE VIEW beta AS SELECT 1", encoding="utf-8")
    (tmp_path / "alpha.sql").write_text("CREATE VIEW alpha AS SELECT 2", encoding="utf-8")
    result = load_view_files(tmp_path)
    assert [name for name, _ in result] == ["alpha.sql", "beta.sql"]


def test_load_view_files_returns_stripped_sql(tmp_path) -> None:
    (tmp_path / "v.sql").write_text("  CREATE VIEW v AS SELECT 1  \n", encoding="utf-8")
    _, sql = load_view_files(tmp_path)[0]
    assert sql == "CREATE VIEW v AS SELECT 1"


def test_load_view_files_ignores_non_sql_files(tmp_path) -> None:
    (tmp_path / "notes.txt").write_text("not sql", encoding="utf-8")
    (tmp_path / "view.sql").write_text("CREATE VIEW v AS SELECT 1", encoding="utf-8")
    result = load_view_files(tmp_path)
    assert len(result) == 1
    assert result[0][0] == "view.sql"


def test_load_view_files_missing_directory_returns_empty(tmp_path) -> None:
    result = load_view_files(tmp_path / "nonexistent")
    assert result == []


# ---------------------------------------------------------------------------
# extract_view_name
# ---------------------------------------------------------------------------

def test_extract_view_name_simple() -> None:
    assert extract_view_name("CREATE VIEW my_view AS SELECT 1") == "my_view"


def test_extract_view_name_case_insensitive() -> None:
    assert extract_view_name("create view Friends AS SELECT 1") == "Friends"


def test_extract_view_name_multiline() -> None:
    sql = "CREATE VIEW\n  chess\nAS SELECT 1"
    assert extract_view_name(sql) == "chess"


def test_extract_view_name_raises_on_invalid_sql() -> None:
    with pytest.raises(ValueError, match="Cannot extract view name"):
        extract_view_name("SELECT 1 FROM voters")


# ---------------------------------------------------------------------------
# normalise_sql
# ---------------------------------------------------------------------------

def test_normalise_sql_collapses_whitespace() -> None:
    assert normalise_sql("CREATE  VIEW   v  AS  SELECT  1") == "CREATE VIEW v AS SELECT 1"


def test_normalise_sql_strips_leading_trailing() -> None:
    assert normalise_sql("  SELECT 1  ") == "SELECT 1"


def test_normalise_sql_newlines_become_spaces() -> None:
    assert normalise_sql("CREATE VIEW v\nAS\nSELECT 1") == "CREATE VIEW v AS SELECT 1"


def test_normalise_sql_idempotent() -> None:
    sql = "CREATE VIEW v AS SELECT 1"
    assert normalise_sql(normalise_sql(sql)) == normalise_sql(sql)

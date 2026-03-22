import pytest

from ncvoters.adapters.index_loader import extract_index_name, load_index_files


# ---------------------------------------------------------------------------
# load_index_files
# ---------------------------------------------------------------------------

def test_load_index_files_returns_sorted_pairs(tmp_path) -> None:
    (tmp_path / "beta.sql").write_text("CREATE INDEX beta ON voters (first_name)", encoding="utf-8")
    (tmp_path / "alpha.sql").write_text("CREATE INDEX alpha ON voters (last_name)", encoding="utf-8")
    result = load_index_files(tmp_path)
    assert [name for name, _ in result] == ["alpha.sql", "beta.sql"]


def test_load_index_files_returns_stripped_sql(tmp_path) -> None:
    (tmp_path / "idx.sql").write_text("  CREATE INDEX idx ON voters (last_name)  \n", encoding="utf-8")
    _, sql = load_index_files(tmp_path)[0]
    assert sql == "CREATE INDEX idx ON voters (last_name)"


def test_load_index_files_ignores_non_sql_files(tmp_path) -> None:
    (tmp_path / "notes.txt").write_text("not sql", encoding="utf-8")
    (tmp_path / "idx.sql").write_text("CREATE INDEX idx ON voters (last_name)", encoding="utf-8")
    result = load_index_files(tmp_path)
    assert len(result) == 1
    assert result[0][0] == "idx.sql"


def test_load_index_files_missing_directory_returns_empty(tmp_path) -> None:
    result = load_index_files(tmp_path / "nonexistent")
    assert result == []


# ---------------------------------------------------------------------------
# extract_index_name
# ---------------------------------------------------------------------------

def test_extract_index_name_simple() -> None:
    assert extract_index_name("CREATE INDEX names ON voters (last_name)") == "names"


def test_extract_index_name_unique() -> None:
    assert extract_index_name("CREATE UNIQUE INDEX reg_num ON voters (voter_reg_num)") == "reg_num"


def test_extract_index_name_case_insensitive() -> None:
    assert extract_index_name("create index Addresses ON voters (res_street_address)") == "Addresses"


def test_extract_index_name_multicolumn() -> None:
    sql = "CREATE INDEX names ON voters (last_name, first_name, middle_name)"
    assert extract_index_name(sql) == "names"


def test_extract_index_name_raises_on_invalid_sql() -> None:
    with pytest.raises(ValueError, match="Cannot extract index name"):
        extract_index_name("SELECT 1 FROM voters")

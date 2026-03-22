# Plan: User-Defined Indexes

---

## Goal

Replace the two hard-coded `CREATE INDEX` statements in `sqlite_repo.py`
with the same file-driven approach used for views: each index lives as a
`.sql` file in `~/.config/ncvoters/indexes/`, and the program discovers and
applies them at runtime.

---

## Current state (to be replaced)

`VoterRepositoryPort` has a `create_indexes()` method.
`SqliteVoterRepository.create_indexes()` hard-codes two statements:

```python
conn.execute("CREATE INDEX names ON voters (last_name, first_name, middle_name)")
conn.execute("CREATE INDEX addresses ON voters (res_street_address)")
```

`CreateVoterDatabase.execute()` calls `self._repo.create_indexes()` after
inserting rows.

---

## Storage: one file per index

```
~/.config/ncvoters/
├── config.yaml
├── indexes/
│   ├── names.sql
│   └── addresses.sql
└── views/
    └── ...
```

Each file contains a single `CREATE INDEX <name> ON <table> (...)` statement.
The index name is parsed from the SQL itself (not the filename), though by
convention they should match.

---

## Two operating modes

### Mode 1 — Full build (`get-voter-data`)

On every full build the voters table is recreated from scratch, so all
indexes must be rebuilt regardless.  `ApplyIndexes` runs unconditionally
(no diff against `sqlite_master`) after rows are inserted.

### Mode 2 — Incremental apply (`apply-indexes`)

A second CLI entry point for applying index files to an **existing**
database without a full rebuild.  Useful when:

- A new `.sql` file has been added to the indexes directory, or
- An existing index's column list has changed and needs to be refreshed.

**Algorithm** (per `.sql` file, in alphabetical filename order):

1. Read the file and extract the index name from the SQL.
2. Query `sqlite_master` to check whether the index already exists
   (`type = 'index'`).
3. If it **does not exist** → create it.
4. If it **exists and the SQL is unchanged** (normalised) → skip.
5. If it **exists and the SQL has changed** → `DROP INDEX <name>` then
   recreate.
6. Wrap each file in its own `try/except`.  On failure, log and continue.
7. Print a summary:
   ```
   Indexes applied:  1  (names)
   Indexes skipped:  1  (addresses — already up to date)
   Indexes failed:   0
   ```

---

## New CLI entry point

```toml
[project.scripts]
get-voter-data  = "ncvoters.cli.main:main"
apply-views     = "ncvoters.cli.apply_views:main"
apply-indexes   = "ncvoters.cli.apply_indexes:main"
```

Usage:

```
apply-indexes [DBNAME]

Applies index definitions from ~/.config/ncvoters/indexes/ to an existing
database.  New indexes are created; changed indexes are dropped and
recreated; unchanged indexes are skipped.  Each index is attempted
independently.

positional arguments:
  dbname    Path to the SQLite database (default: /tmp/voter_data.db)

options:
  -q, --quiet    Suppress progress output
```

---

## What changes and what is removed

| Item | Change |
|---|---|
| `VoterRepositoryPort.create_indexes()` | **Removed** — replaced by `apply_index` / `existing_index_sql` |
| `SqliteVoterRepository.create_indexes()` | **Removed** |
| `CreateVoterDatabase.execute()` call to `create_indexes()` | **Replaced** by `ApplyIndexes(...).execute(incremental=False)` |
| `adapters/index_loader.py` | **New** — mirrors `view_loader.py` |
| `application/use_cases.py` | **New** `ApplyIndexesResult` dataclass and `ApplyIndexes` use case |
| `cli/apply_indexes.py` | **New** — mirrors `cli/apply_views.py` |
| `pyproject.toml` | Add `apply-indexes` entry point |
| `~/.config/ncvoters/indexes/names.sql` | **New** file |
| `~/.config/ncvoters/indexes/addresses.sql` | **New** file |
| `sample_config.yaml` | Add comment pointing to indexes directory |
| `dirstruct.md` | Document new files and runtime path |

---

## Implementation checklist

### `ports/outbound.py`
- [x] Remove `create_indexes(self) -> None` from `VoterRepositoryPort`
- [x] Add `apply_index(self, sql: str) -> None`
- [x] Add `existing_index_sql(self, name: str) -> str | None`

### `adapters/sqlite_repo.py`
- [x] Remove `create_indexes` implementation
- [x] Implement `apply_index`
- [x] Implement `existing_index_sql` (query `sqlite_master WHERE type='index'`)

### `adapters/index_loader.py` *(new file)*
- [x] `load_index_files(indexes_dir: Path) -> list[tuple[str, str]]`
- [x] `extract_index_name(sql: str) -> str` (regex handles optional `UNIQUE`)
- [x] `normalise_sql(sql: str) -> str` (can import from `view_loader` — same function)

### `application/use_cases.py`
- [x] Add `ApplyIndexesResult` dataclass (`.applied`, `.skipped`, `.failed`)
- [x] Add `ApplyIndexes(repo, indexes_dir, quiet)` use case
- [x] Replace `self._repo.create_indexes()` call in `CreateVoterDatabase.execute()` with `ApplyIndexes(...).execute(incremental=False)`

### `cli/apply_indexes.py` *(new file)*
- [x] `main()` entry point with `dbname` positional arg and `-q/--quiet` flag
- [x] Guards against missing database file
- [x] Incremental mode only

### `pyproject.toml`
- [x] Add `apply-indexes = "ncvoters.cli.apply_indexes:main"` to `[project.scripts]`

### Config / docs
- [x] Add `~/.config/ncvoters/indexes/names.sql`
- [x] Add `~/.config/ncvoters/indexes/addresses.sql`
- [x] Add comment to `sample_config.yaml` pointing to the indexes directory
- [x] Update `dirstruct.md` to document `index_loader.py`, `cli/apply_indexes.py`,
      and the `~/.config/ncvoters/indexes/` runtime path

### Tests
- [x] `tests/adapters/test_index_loader.py` — `load_index_files`, `extract_index_name`
- [x] `tests/adapters/test_sqlite_repo.py` — `apply_index`, `existing_index_sql`
- [x] `tests/application/test_use_cases.py` — `ApplyIndexes` (new, skip, update, failure)

---

## Notes

- `normalise_sql` in `index_loader.py` can simply re-use the one already
  defined in `view_loader.py` — no need to duplicate it.
- SQLite stores user-created index SQL in `sqlite_master` exactly as written,
  so the same whitespace-normalisation trick used for views works here too.
- Auto-generated SQLite internal indexes (`sqlite_autoindex_*`) always have
  `type='index'` but will never appear as `.sql` files, so there is no
  collision risk.
- `UNIQUE` indexes should be handled by the name-extraction regex:
  `CREATE\s+(?:UNIQUE\s+)?INDEX\s+(\w+)`.

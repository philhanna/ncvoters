# Plan: Configurable Database Directory

---

## Goal

Add a `db_dir` key to `config.yaml` so the user can specify where
`voter_data.db` is created, instead of always defaulting to `/tmp`.
When a database already exists at the target path, rename it with a
timestamp suffix rather than silently deleting it.

---

## Current behaviour

- The database path defaults to `/tmp/voter_data.db`.
- A positional `dbname` argument on the CLI can override it.
- `CreateVoterDatabase.execute()` calls `db_file.unlink()` on any existing
  database before starting, destroying it without a backup.

---

## Proposed behaviour

### Priority order for the database path

```
1. CLI positional argument (explicit override — highest priority)
2. config.yaml  db_dir  +  "voter_data.db"  (new config key)
3. /tmp/voter_data.db  (existing fallback — lowest priority)
```

Only the filename `voter_data.db` is fixed; `db_dir` specifies the
containing directory.  `~` expansion is supported (e.g. `~/Desktop`).

### Renaming the existing database

When the program is about to write to a path where a database already
exists, it renames the old file to `voter_data_YYYYMMDD_HHMMSS.db` in
the same directory before proceeding, and logs the rename.  This replaces
the current silent `unlink()` call in `CreateVoterDatabase.execute()`.

### `apply-views` and `apply-indexes` defaults

These two CLIs also hard-code `/tmp/voter_data.db` as their default.
They should derive the same default from `config.db_dir` when no
positional argument is given, for consistency.

---

## New config key

```yaml
# Directory where voter_data.db is created.
# Supports ~ expansion.  The filename voter_data.db is always used.
# If omitted, defaults to /tmp.
db_dir: ~/Desktop
```

---

## What changes

| Item | Change |
|---|---|
| `domain/models.py` | Add `db_dir: str \| None = None` field to `Configuration` |
| `adapters/config_loader.py` | Read `db_dir` from YAML (default `None`) |
| `application/use_cases.py` | Replace `db_file.unlink()` with a rename-with-timestamp helper |
| `cli/main.py` | Resolve db path from CLI arg → config → `/tmp`; update `_USAGE` |
| `cli/apply_views.py` | Derive default dbname from `config.db_dir`; update `_USAGE` |
| `cli/apply_indexes.py` | Same as `apply_views.py` |
| `sample_config.yaml` | Document `db_dir` key (commented out by default) |
| `dirstruct.md` | Note `db_dir` in the config section |

---

## Helper: resolving the database path

A small pure function, usable from all three CLI modules:

```python
def resolve_db_path(cli_arg: str | None, config: Configuration) -> str:
    if cli_arg is not None:
        return cli_arg
    if config.db_dir:
        return str(Path(config.db_dir).expanduser() / "voter_data.db")
    return str(Path(tempfile.gettempdir()) / "voter_data.db")
```

This lives in `cli/main.py` and is imported by the two `apply-*` CLIs.

---

## Rename scheme

```
voter_data.db  →  voter_data_20260322_143022.db
```

The timestamp is taken at the moment of the rename.  Both the old and new
names sit in the same directory.  The rename is logged at INFO level so the
user can see it.  If the rename fails for any reason (e.g. permissions),
the error is re-raised — the build does not silently continue with a
potentially corrupt or stale database.

---

## Implementation checklist

### `domain/models.py`
- [x] Add `db_dir: str | None = None` to `Configuration`

### `adapters/config_loader.py`
- [x] Read `db_dir` from YAML and pass to `Configuration`

### `application/use_cases.py`
- [x] Add `_rename_existing_db(db_path: str) -> None` helper
      (renames to `voter_data_YYYYMMDD_HHMMSS.db` in same directory)
- [x] Replace `db_file.unlink()` call with `_rename_existing_db(db_path)`

### `cli/main.py`
- [x] Add `resolve_db_path(cli_arg, config) -> str` helper
- [x] Change `dbname` argument default to `None`
- [x] Resolve db path after loading config; pass result through
- [x] Update `_USAGE` string to reflect new default behaviour

### `cli/apply_views.py`
- [x] Import and use `resolve_db_path`; change `dbname` default to `None`

### `cli/apply_indexes.py`
- [x] Import and use `resolve_db_path`; change `dbname` default to `None`

### `sample_config.yaml`
- [x] Add `db_dir` key (commented out) with explanation

### `dirstruct.md`
- [x] Note `db_dir` in the configuration section

### Tests
- [x] `tests/domain/test_models.py` — `db_dir` defaults to `None`
- [x] `tests/adapters/test_config_loader.py` — `db_dir` loaded from YAML;
      absent key yields `None`
- [x] `tests/application/test_use_cases.py` — existing db is renamed,
      not deleted; renamed file exists; original path is gone

---

## What does NOT change

- The zip file always stays in `/tmp` — it is a cache, not a deliverable.
- The database filename is always `voter_data.db`; only the directory is
  configurable.
- Passing an explicit `dbname` on the CLI continues to work exactly as
  before, writing to exactly the path given (no rename of anything at that
  path either — the user asked for it explicitly).

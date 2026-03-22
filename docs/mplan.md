# Plan: User-Defined Views

---

## Revised design (supersedes original)

Based on the following requirements:

- Views are stored as individual SQL files, one per view, in a directory.
- On a full database build, **all** view files are applied automatically.
- On an existing database, the user can apply **new or changed** view files
  without rebuilding the whole database.
- View files are applied **independently** — a syntax error in one does not
  prevent the others from being created.
- The user is shown a clear summary of what succeeded and what failed.

---

## Storage: one file per view

Views live in `~/.config/ncvoters/views/`, one `.sql` file per view:

```
~/.config/ncvoters/
├── config.yaml
└── views/
    ├── family.sql
    ├── friends.sql
    ├── doctors.sql
    ├── neighbors.sql
    └── chess.sql
```

Each file contains a single `CREATE VIEW <name> AS ...` statement (no
terminating semicolon required — the loader will strip/add as needed).
The view name is taken from the SQL itself, not the filename, though
by convention they should match.

---

## Two operating modes

### Mode 1 — Full build (`get-voter-data`)

Runs automatically at the end of every full database creation:

1. Download / reuse zip file
2. Create `voters` table
3. Stream and insert rows
4. Build indexes
5. **Apply all `.sql` files in `~/.config/ncvoters/views/`** ← new step
6. *(optional)* Add metadata tables (`--metadata`)

Since the database is created fresh every time, there is nothing to
track or diff — every view file is always applied.

### Mode 2 — Incremental apply (`apply-views`)

A second CLI entry point for applying views to an **existing** database
without a full rebuild.  Useful when:

- A new `.sql` file has been added to the views directory, or
- An existing view's SQL has been edited and needs to be refreshed.

**Algorithm** (per `.sql` file, in alphabetical filename order):

1. Read the file and extract the view name from the SQL.
2. Query `sqlite_master` to check whether the view already exists.
3. If it **does not exist** → create it.
4. If it **exists and the SQL is unchanged** → skip (log "already up to date").
5. If it **exists and the SQL has changed** → `DROP VIEW <name>` then recreate.
6. Wrap each file's operation in its own `try/except`.  On failure, log
   the error and continue to the next file.
7. Print a summary at the end:
   ```
   Views applied:  3  (family, doctors, chess)
   Views skipped:  1  (friends — already up to date)
   Views failed:   1  (neighbors — no such column: address)
   ```

SQL comparison is done by normalising whitespace on both sides before
comparing, so cosmetic edits to a file do not trigger an unnecessary
DROP/recreate.

---

## New CLI entry point

Add a second console script to `pyproject.toml`:

```toml
[project.scripts]
get-voter-data = "ncvoters.cli.main:main"
apply-views    = "ncvoters.cli.apply_views:main"
```

Usage:

```
apply-views [DBNAME]

Applies view definitions from ~/.config/ncvoters/views/ to an existing
database.  New views are created; changed views are dropped and recreated;
unchanged views are skipped.  Each view is attempted independently.

positional arguments:
  dbname    Path to the SQLite database (default: /tmp/voter_data.db)

options:
  -q, --quiet    Suppress progress output
```

---

## Implementation checklist

### `ports/outbound.py`
- [x] Add `apply_view(self, sql: str) -> None` to `VoterRepositoryPort`
- [x] Add `existing_view_sql(self, name: str) -> str | None` to `VoterRepositoryPort`

### `adapters/sqlite_repo.py`
- [x] Implement `apply_view`
- [x] Implement `existing_view_sql`

### `adapters/view_loader.py` *(new file)*
- [x] `load_view_files(views_dir: Path) -> list[tuple[str, str]]`
- [x] `extract_view_name(sql: str) -> str`
- [x] `normalise_sql(sql: str) -> str`

### `application/use_cases.py`
- [x] Add `ApplyViewsResult` dataclass (`.applied`, `.skipped`, `.failed` lists)
- [x] Add `ApplyViews(repo, views_dir, quiet)` use case
- [x] Call `ApplyViews` from `CreateVoterDatabase.execute()` after index creation

### `cli/main.py`
- [x] Instantiate and call `ApplyViews` after `create_indexes`
- [x] Log the summary unless `--quiet`

### `cli/apply_views.py` *(new file)*
- [x] `main()` entry point with `dbname` positional arg and `-q/--quiet` flag
- [x] Incremental mode: skip unchanged views, drop+recreate changed ones

### `pyproject.toml`
- [x] Add `apply-views = "ncvoters.cli.apply_views:main"` to `[project.scripts]`

### Config / docs
- [x] Add five view `.sql` files to `~/.config/ncvoters/views/`
- [x] Add comment to `sample_config.yaml` pointing to the views directory
- [x] Update `dirstruct.md` to document `view_loader.py`, `cli/apply_views.py`,
      and the `~/.config/ncvoters/views/` runtime path

### Tests
- [x] `tests/adapters/test_view_loader.py` — `load_view_files`, `extract_view_name`, `normalise_sql`
- [x] `tests/adapters/test_sqlite_repo.py` — `apply_view`, `existing_view_sql`
- [x] `tests/application/test_use_cases.py` — `ApplyViews` (new, skip, update, failure)

---

## Error handling policy

- **Full build**: log each failure as a warning; do not abort the build.
  The database is still usable without the broken view.
- **Incremental apply**: same — log and continue.
- In both cases the summary line makes it clear which views need fixing.

---

## Open questions (resolved)

| Question | Decision |
|---|---|
| Views in `config.yaml` or separate files? | **Separate `.sql` files** in `~/.config/ncvoters/views/` |
| Apply all or track state? | **Always all** on full build; **diff against `sqlite_master`** on incremental apply |
| Abort on failure? | **No** — apply each file independently, report failures in summary |
| `CREATE VIEW IF NOT EXISTS`? | **No** — the program manages existence checks itself so it can also handle updates |
| Config key name? | **Not needed** — views directory is discovered automatically |

# Project Directory Structure

This document describes the layout of the `ncvoters` Python project and the
purpose of every file and directory.

---

## Top-level

```
ncvoters/
├── pyproject.toml
├── sample_config.yaml
├── dirstruct.md
├── LICENSE
├── README.md
├── src/
├── tests/
└── go/
```

| Entry | Purpose |
|---|---|
| [pyproject.toml](pyproject.toml) | Single source of truth for package metadata, dependencies, build backend (Hatchling), and pytest configuration. Declares the `get-voter-data` console script entry point. |
| [sample_config.yaml](sample_config.yaml) | Template the user copies to `~/.config/ncvoters/config.yaml`. Documents the `selected_columns` and `sanitize_columns` keys. |
| [dirstruct.md](dirstruct.md) | This file. |
| [LICENSE](LICENSE) | Project licence. |
| [README.md](README.md) | Project overview and usage instructions. |
| [src/](src/) | Source root (PEP 517 `src` layout — keeps the package off `sys.path` during development unless explicitly installed). |
| [tests/](tests/) | Pytest test suite, mirroring the `src/ncvoters/` sub-package tree. |
| [go/](go/) | Original Go implementation, retained for reference. |

---

## `src/ncvoters/` — the Python package

The package is structured according to **Hexagonal Architecture** (also called
Ports and Adapters).  The dependency rule flows strictly inward:

```
cli  ──▶  application  ──▶  ports  ◀──  adapters
                    ╲               ╱
                     ──▶  domain ◀──
```

- **domain** has no dependencies on anything else in the project.
- **ports** depends only on domain.
- **application** depends on domain and ports.
- **adapters** depends on domain and ports (implements the port interfaces).
- **cli** depends on application and adapters (wires everything together).

```
src/ncvoters/
├── __init__.py
├── domain/
│   ├── __init__.py
│   └── models.py
├── ports/
│   ├── __init__.py
│   └── outbound.py
├── adapters/
│   ├── __init__.py
│   ├── config_loader.py
│   ├── downloader.py
│   ├── layout_fetcher.py
│   ├── progress.py
│   ├── index_loader.py
│   ├── sqlite_repo.py
│   └── view_loader.py
├── application/
│   ├── __init__.py
│   └── use_cases.py
└── cli/
    ├── __init__.py
    ├── apply_indexes.py
    ├── apply_views.py
    └── main.py
```

### `domain/`

The core of the application.  Contains pure Python dataclasses with **no
external dependencies** — no I/O, no third-party libraries.

| File | Contents |
|---|---|
| [domain/models.py](src/ncvoters/domain/models.py) | Three dataclasses: `Configuration` (the user's column selections), `Column` (a single field from the NC BOE layout file), and `Layout` (the full parsed layout: all columns plus look-up code dictionaries for status, race, ethnicity, county, and reason). |

### `ports/`

Abstract base classes (Python `abc.ABC`) that define the *contracts* between
the application core and the outside world.  Ports are **interfaces only** —
no implementation lives here.

| File | Contents |
|---|---|
| [ports/outbound.py](src/ncvoters/ports/outbound.py) | Four outbound (driven) ports: `ConfigurationPort` — loads a `Configuration`; `FileDownloaderPort` — downloads a URL to a local path; `LayoutFetcherPort` — fetches and parses the NC BOE layout file into a `Layout`; `VoterRepositoryPort` — creates the voters table, bulk-inserts rows, and adds metadata tables to the database. |

### `adapters/`

Concrete implementations of the port interfaces.  Each adapter is a
self-contained infrastructure concern.  Swapping an adapter (e.g. replacing
SQLite with PostgreSQL) requires changing only the relevant file here and the
wiring in [cli/main.py](src/ncvoters/cli/main.py).

| File | Implements | Purpose |
|---|---|---|
| [adapters/progress.py](src/ncvoters/adapters/progress.py) | *(standalone)* | `Progress` class — renders a single-line, carriage-return-updated progress bar to `stderr`. Tracks total, so-far, and elapsed time. |
| [adapters/config_loader.py](src/ncvoters/adapters/config_loader.py) | `ConfigurationPort` | `YamlConfigLoader` — reads `~/.config/ncvoters/config.yaml` using PyYAML and returns a `Configuration`. Raises `FileNotFoundError` with a helpful message if the file is absent. |
| [adapters/downloader.py](src/ncvoters/adapters/downloader.py) | `FileDownloaderPort` | `HttpFileDownloader` — issues an HTTP HEAD request to obtain the content length, then streams the file to disk in 1 MB chunks while rendering a progress bar. |
| [adapters/layout_fetcher.py](src/ncvoters/adapters/layout_fetcher.py) | `LayoutFetcherPort` | `NcboeLayoutFetcher` — downloads the NC BOE layout text file, appends the undocumented reason codes, writes the result to `/tmp/voter_layout.txt`, and parses it with a finite-state machine into a `Layout` object. The FSM states are: `INIT → LOOKING_FOR_COLUMNS_START → READING_COLUMNS → LOOKING_FOR_CODE_BLOCK → LOOKING_FOR_CODE_BLOCK_NAME → LOOKING_FOR_CODE_BLOCK_START → READING_CODE_BLOCK`. |
| [adapters/sqlite_repo.py](src/ncvoters/adapters/sqlite_repo.py) | `VoterRepositoryPort` | `SqliteVoterRepository` — creates the `voters` table (columns derived from `Configuration.selected_columns`), bulk-inserts rows with `executemany`, creates indexes on `(last_name, first_name, middle_name)` and `res_street_address`, implements `apply_view` / `existing_view_sql` for view management, and populates six metadata tables (`columns`, `status_codes`, `race_codes`, `ethnic_codes`, `county_codes`, `reason_codes`) using generated DDL. Single quotes inside values are escaped to prevent SQL errors. |
| [adapters/index_loader.py](src/ncvoters/adapters/index_loader.py) | *(standalone)* | Two pure functions: `load_index_files(indexes_dir)` — reads all `.sql` files from the indexes directory in alphabetical order, returning `(filename, sql)` pairs; `extract_index_name(sql)` — parses the index name from a `CREATE [UNIQUE] INDEX <name> ON …` statement using a regex.  Imports `normalise_sql` from `view_loader` rather than duplicating it. |
| [adapters/view_loader.py](src/ncvoters/adapters/view_loader.py) | *(standalone)* | Three pure functions: `load_view_files(views_dir)` — reads all `.sql` files from a directory in alphabetical order, returning `(name, sql)` pairs; `extract_view_name(sql)` — parses the view name from a `CREATE VIEW <name> AS …` statement using a regex; `normalise_sql(sql)` — collapses all whitespace runs to a single space so cosmetic edits don't trigger unnecessary DROP/recreate. |

### `application/`

Use cases — the application's behaviour expressed as plain Python classes.
Each class takes its dependencies as constructor arguments (ports), making
them independently testable without real infrastructure.

| File | Contents |
|---|---|
| [application/use_cases.py](src/ncvoters/application/use_cases.py) | **`CreateVoterDatabase`** — decides whether to reuse or re-download the zip file, deletes any existing database, creates the voters table, streams rows from the embedded tab-delimited CSV (read via `csv.DictReader` over a `zipfile.ZipFile` entry, decoded as `latin-1`) through the repository in a single `executemany` call, then applies all indexes and views.  Applies whitespace sanitization to columns listed in `Configuration.sanitize_columns`.  **`AddMetadata`** — delegates to `LayoutFetcherPort` to obtain a `Layout`, then calls `VoterRepositoryPort.add_metadata` to create and populate the six lookup tables.  **`ApplyIndexes`** — reads `.sql` files from the indexes directory, compares each against `sqlite_master`, and creates, skips, or drops-and-recreates each index accordingly.  Returns an `ApplyIndexesResult`.  **`ApplyViews`** — same pattern for the views directory. |

### `cli/`

The primary (driving) adapter.  Responsible solely for wiring: parsing
command-line arguments, constructing concrete adapter instances, and invoking
use cases in the correct order.

| File | Contents |
|---|---|
| [cli/main.py](src/ncvoters/cli/main.py) | `main()` — the `get-voter-data` entry point declared in [pyproject.toml](pyproject.toml). Parses flags (`-f/--force`, `-l/--limit`, `-m/--metadata`, `-q/--quiet`) and an optional positional `dbname` argument.  Instantiates `YamlConfigLoader`, `HttpFileDownloader`, `SqliteVoterRepository`, and `NcboeLayoutFetcher`, then calls `CreateVoterDatabase` (which automatically applies all views) and (optionally) `AddMetadata`. |
| [cli/apply_indexes.py](src/ncvoters/cli/apply_indexes.py) | `main()` — the `apply-indexes` entry point declared in [pyproject.toml](pyproject.toml). Parses an optional positional `dbname` argument and a `-q/--quiet` flag.  Guards against a missing database file.  Invokes `ApplyIndexes` in incremental mode: skips unchanged indexes, drops and recreates changed ones, and prints a summary. |
| [cli/apply_views.py](src/ncvoters/cli/apply_views.py) | `main()` — the `apply-views` entry point declared in [pyproject.toml](pyproject.toml). Parses an optional positional `dbname` argument and a `-q/--quiet` flag.  Guards against a missing database file.  Invokes `ApplyViews` in incremental mode: skips unchanged views, drops and recreates changed ones, and prints a summary of applied / skipped / failed views. |

---

## `tests/`

The test tree mirrors the source tree.  Each sub-package tests one layer of
the architecture.

```
tests/
├── __init__.py
├── domain/
│   ├── __init__.py
│   └── test_models.py
├── adapters/
│   ├── __init__.py
│   ├── test_config_loader.py
│   ├── test_index_loader.py
│   ├── test_layout_fetcher.py
│   ├── test_sqlite_repo.py
│   └── test_view_loader.py
└── application/
    ├── __init__.py
    └── test_use_cases.py
```

| File | What it tests |
|---|---|
| [tests/domain/test_models.py](tests/domain/test_models.py) | `Configuration`, `Column`, and `Layout` dataclass construction and defaults. |
| [tests/adapters/test_config_loader.py](tests/adapters/test_config_loader.py) | `YamlConfigLoader` — happy path with a temp file, and `FileNotFoundError` on a missing path. |
| [tests/adapters/test_layout_fetcher.py](tests/adapters/test_layout_fetcher.py) | `_parse_layout_file` — uses the `layout_ncvoter.txt` fixture from [go/testdata/](go/testdata/) to verify that column names are parsed correctly. |
| [tests/adapters/test_sqlite_repo.py](tests/adapters/test_sqlite_repo.py) | `SqliteVoterRepository` — creates a table, inserts rows, asserts rows round-trip correctly, and tests `apply_view` / `existing_view_sql`. |
| [tests/adapters/test_index_loader.py](tests/adapters/test_index_loader.py) | `load_index_files`, `extract_index_name` — sorting, stripping, name extraction (including `UNIQUE INDEX`), and error cases. |
| [tests/adapters/test_view_loader.py](tests/adapters/test_view_loader.py) | `load_view_files`, `extract_view_name`, `normalise_sql` — sorting, stripping, name extraction, whitespace collapsing, and error cases. |
| [tests/application/test_use_cases.py](tests/application/test_use_cases.py) | `ApplyViews` — full-build and incremental modes: new view creation, unchanged-view skipping, changed-view recreation, syntax-error failure isolation, and multi-view partial failure. |

---

## `go/`

The original Go implementation, kept for reference.  It is not built or
tested as part of the Python project.

```
go/
├── go.mod / go.sum          # Go module definition and checksums
├── config.go                # YAML config loading
├── mapreduce.go             # Generic Map/Reduce over channels
├── doc.go                   # Package-level godoc
├── cmd/create/
│   └── get_voter_data.go    # Go CLI entry point
├── create/                  # Database creation logic
├── download/                # HTTP download logic
├── util/                    # File existence, zip validation, progress
├── webdata/                 # Layout parsing and metadata DDL generation
├── testdata/                # Fixtures: zip files, layout text, CSV
└── sample_config.yaml       # Go-specific sample config
```

---

## Runtime paths

| Path | Purpose |
|---|---|
| `~/.config/ncvoters/config.yaml` | User configuration (columns to import). |
| `~/.config/ncvoters/indexes/` | Directory of `.sql` index definitions, one file per index.  Applied automatically on every full build; also applied incrementally by `apply-indexes`. |
| `~/.config/ncvoters/views/` | Directory of `.sql` view definitions, one file per view.  Applied automatically on every full build; also applied incrementally by `apply-views`. |
| `/tmp/voter_data.zip` | Downloaded NC voter zip file (reused across runs unless `--force` is given). |
| `/tmp/voter_layout.txt` | Downloaded and augmented NC BOE layout file (used only when `--metadata` is given). |
| `<dbname>` | Output SQLite database (defaults to `/tmp/voter_data.db`). |

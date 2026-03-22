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
| `pyproject.toml` | Single source of truth for package metadata, dependencies, build backend (Hatchling), and pytest configuration. Declares the `get-voter-data` console script entry point. |
| `sample_config.yaml` | Template the user copies to `~/.config/ncvoters/config.yaml`. Documents the `selected_columns` and `sanitize_columns` keys. |
| `dirstruct.md` | This file. |
| `LICENSE` | Project licence. |
| `README.md` | Project overview and usage instructions. |
| `src/` | Source root (PEP 517 `src` layout — keeps the package off `sys.path` during development unless explicitly installed). |
| `tests/` | Pytest test suite, mirroring the `src/ncvoters/` sub-package tree. |
| `go/` | Original Go implementation, retained for reference. |

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
│   └── sqlite_repo.py
├── application/
│   ├── __init__.py
│   └── use_cases.py
└── cli/
    ├── __init__.py
    └── main.py
```

### `domain/`

The core of the application.  Contains pure Python dataclasses with **no
external dependencies** — no I/O, no third-party libraries.

| File | Contents |
|---|---|
| `models.py` | Three dataclasses: `Configuration` (the user's column selections), `Column` (a single field from the NC BOE layout file), and `Layout` (the full parsed layout: all columns plus look-up code dictionaries for status, race, ethnicity, county, and reason). |

### `ports/`

Abstract base classes (Python `abc.ABC`) that define the *contracts* between
the application core and the outside world.  Ports are **interfaces only** —
no implementation lives here.

| File | Contents |
|---|---|
| `outbound.py` | Four outbound (driven) ports: `ConfigurationPort` — loads a `Configuration`; `FileDownloaderPort` — downloads a URL to a local path; `LayoutFetcherPort` — fetches and parses the NC BOE layout file into a `Layout`; `VoterRepositoryPort` — creates the voters table, bulk-inserts rows, and adds metadata tables to the database. |

### `adapters/`

Concrete implementations of the port interfaces.  Each adapter is a
self-contained infrastructure concern.  Swapping an adapter (e.g. replacing
SQLite with PostgreSQL) requires changing only the relevant file here and the
wiring in `cli/main.py`.

| File | Implements | Purpose |
|---|---|---|
| `progress.py` | *(standalone)* | `Progress` class — renders a single-line, carriage-return-updated progress bar to `stderr`. Tracks total, so-far, and elapsed time. |
| `config_loader.py` | `ConfigurationPort` | `YamlConfigLoader` — reads `~/.config/ncvoters/config.yaml` using PyYAML and returns a `Configuration`. Raises `FileNotFoundError` with a helpful message if the file is absent. |
| `downloader.py` | `FileDownloaderPort` | `HttpFileDownloader` — issues an HTTP HEAD request to obtain the content length, then streams the file to disk in 1 MB chunks while rendering a progress bar. |
| `layout_fetcher.py` | `LayoutFetcherPort` | `NcboeLayoutFetcher` — downloads the NC BOE layout text file, appends the undocumented reason codes, writes the result to `/tmp/voter_layout.txt`, and parses it with a finite-state machine into a `Layout` object. The FSM states are: `INIT → LOOKING_FOR_COLUMNS_START → READING_COLUMNS → LOOKING_FOR_CODE_BLOCK → LOOKING_FOR_CODE_BLOCK_NAME → LOOKING_FOR_CODE_BLOCK_START → READING_CODE_BLOCK`. |
| `sqlite_repo.py` | `VoterRepositoryPort` | `SqliteVoterRepository` — creates the `voters` table (columns derived from `Configuration.selected_columns`), bulk-inserts rows with `executemany`, and populates six metadata tables (`columns`, `status_codes`, `race_codes`, `ethnic_codes`, `county_codes`, `reason_codes`) using generated DDL. Single quotes inside values are escaped to prevent SQL errors. |

### `application/`

Use cases — the application's behaviour expressed as plain Python classes.
Each class takes its dependencies as constructor arguments (ports), making
them independently testable without real infrastructure.

| File | Contents |
|---|---|
| `use_cases.py` | **`CreateVoterDatabase`** — decides whether to reuse or re-download the zip file, deletes any existing database, creates the voters table, and streams rows from the embedded tab-delimited CSV (read via `csv.DictReader` over a `zipfile.ZipFile` entry, decoded as `latin-1`) through the repository in a single `executemany` call.  Applies whitespace sanitization to columns listed in `Configuration.sanitize_columns`.  Displays a progress bar using the uncompressed file size as an estimate of row count.  **`AddMetadata`** — delegates to `LayoutFetcherPort` to obtain a `Layout`, then calls `VoterRepositoryPort.add_metadata` to create and populate the six lookup tables. |

### `cli/`

The primary (driving) adapter.  Responsible solely for wiring: parsing
command-line arguments, constructing concrete adapter instances, and invoking
use cases in the correct order.

| File | Contents |
|---|---|
| `main.py` | `main()` — the `get-voter-data` entry point declared in `pyproject.toml`. Parses flags (`-f/--force`, `-l/--limit`, `-m/--metadata`, `-q/--quiet`) and an optional positional `dbname` argument.  Instantiates `YamlConfigLoader`, `HttpFileDownloader`, `SqliteVoterRepository`, and `NcboeLayoutFetcher`, then calls `CreateVoterDatabase` and (optionally) `AddMetadata`. |

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
│   ├── test_layout_fetcher.py
│   └── test_sqlite_repo.py
└── application/
    └── __init__.py
```

| File | What it tests |
|---|---|
| `domain/test_models.py` | `Configuration`, `Column`, and `Layout` dataclass construction and defaults. |
| `adapters/test_config_loader.py` | `YamlConfigLoader` — happy path with a temp file, and `FileNotFoundError` on a missing path. |
| `adapters/test_layout_fetcher.py` | `_parse_layout_file` — uses the `layout_ncvoter.txt` fixture from `go/testdata/` to verify that column names are parsed correctly. |
| `adapters/test_sqlite_repo.py` | `SqliteVoterRepository` — creates a table, inserts two rows via the iterator interface, and asserts the rows are present via a direct `sqlite3` connection. |
| `application/` | Placeholder package for future use-case integration tests. |

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
| `/tmp/voter_data.zip` | Downloaded NC voter zip file (reused across runs unless `--force` is given). |
| `/tmp/voter_layout.txt` | Downloaded and augmented NC BOE layout file (used only when `--metadata` is given). |
| `<dbname>` | Output SQLite database (defaults to `/tmp/voter_data.db`). |

# Project Directory Structure

This document describes the layout of the `ncvoters` project and the
purpose of every file and directory.

---

## Top-level

```
ncvoters/
├── CHANGELOG.md
├── dirstruct.md
├── get-voter-data
├── LICENSE
├── Makefile
├── pyproject.toml
├── README.md
├── sample_config.yaml
└── scripts/
```

| Entry | Purpose |
|---|---|
| [CHANGELOG.md](CHANGELOG.md) | Release history following the Keep a Changelog format. |
| [dirstruct.md](dirstruct.md) | This file. |
| [get-voter-data](get-voter-data) | Shell wrapper that runs `make` from the project directory, allowing the pipeline to be invoked from anywhere. |
| [LICENSE](LICENSE) | Project licence. |
| [Makefile](Makefile) | Defines the build pipeline: `download → unzip → load → indexes → views`. Uses stamp files to skip stages that are already up to date. |
| [pyproject.toml](pyproject.toml) | Package metadata and the single runtime dependency (`pyyaml`). |
| [README.md](README.md) | Project overview, installation steps, and usage instructions. |
| [sample_config.yaml](sample_config.yaml) | Template the user copies to `~/.config/ncvoters/config.yaml`. Documents the `db_dir`, `selected_columns`, and `sanitize_columns` keys. |
| [scripts/](scripts/) | Individual Python scripts, one per pipeline stage. |

---

## `scripts/` — the pipeline scripts

Each script is a standalone, directly-runnable Python file that handles one
stage of the build.  The `Makefile` calls them in order; they can also be
invoked individually for development or debugging.

```
scripts/
├── db_path.py
├── download.py
├── unzip.py
├── load.py
├── indexes.py
└── views.py
```

| File | Makefile target | Purpose |
|---|---|---|
| [scripts/db_path.py](scripts/db_path.py) | *(helper)* | Prints the resolved path to `voter_data.db` by reading `db_dir` from `config.yaml`, falling back to `/tmp`. Used by the Makefile to set the `DB` variable. |
| [scripts/download.py](scripts/download.py) | `download` | Downloads `ncvoter_Statewide.zip` from the NC Board of Elections S3 bucket to `/tmp`, with a live percentage indicator. Skipped by `make` if the zip already exists. |
| [scripts/unzip.py](scripts/unzip.py) | `unzip` | Streams the voter txt file out of the zip in 1 MB chunks, printing percentage progress. The uncompressed file is over 1 GB. |
| [scripts/load.py](scripts/load.py) | `load` | Reads `config.yaml`, renames any existing database to a timestamped backup, creates a fresh `voters` table with the configured columns, and bulk-inserts rows in batches of 10,000. |
| [scripts/indexes.py](scripts/indexes.py) | `indexes` | Applies every `.sql` file in `~/.config/ncvoters/indexes/` to the database. Drops and recreates each index so the operation is idempotent. |
| [scripts/views.py](scripts/views.py) | `views` | Applies every `.sql` file in `~/.config/ncvoters/views/` to the database. Drops and recreates each view so the operation is idempotent. |

---

## Makefile pipeline

```
download  →  unzip  →  load  →  indexes  →  views
```

Stamp files (`.load.stamp`, `.indexes.stamp`, `.views.stamp`) track which
stages have completed.  `make clean` removes the downloaded files and all
stamps, forcing a full rebuild on the next run.

---

## Runtime paths

| Path | Purpose |
|---|---|
| `~/.config/ncvoters/config.yaml` | User configuration: `db_dir`, `selected_columns`, `sanitize_columns`. |
| `~/.config/ncvoters/indexes/` | `.sql` files defining indexes, one per file. Applied by `make indexes`. |
| `~/.config/ncvoters/views/` | `.sql` files defining views, one per file. Applied by `make views`. |
| `/tmp/voter_data.zip` | Downloaded NC voter zip (reused by `make` until `make clean` is run). |
| `/tmp/ncvoter_Statewide.txt` | Extracted voter data file (reused by `make` until `make clean` is run). |
| `<db_dir>/voter_data.db` | Output SQLite database. Directory is `db_dir` from config, or `/tmp` if unset. |

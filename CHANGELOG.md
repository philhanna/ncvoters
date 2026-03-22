# Change Log
All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning],
and the format is based on [Keep a Changelog].

## [Unreleased]

## [0.1.0] - 2026-03-22

Initial Python release, converted from the original Go implementation.

### Added

- Hexagonal architecture (Ports and Adapters) with `domain`, `ports`,
  `adapters`, `application`, and `cli` layers
- `get-voter-data` CLI entry point — downloads NC voter zip file and
  creates an SQLite database
- `apply-views` CLI entry point — applies changed view definitions to an
  existing database without a full rebuild
- `apply-indexes` CLI entry point — applies changed index definitions to an
  existing database without a full rebuild
- `db_dir` config key to specify where `voter_data.db` is created;
  supports `~` expansion; defaults to `/tmp`
- Any existing database at the target path is renamed to
  `voter_data_YYYYMMDD_HHMMSS.db` before a new build starts
- File-driven views: one `.sql` file per view in
  `~/.config/ncvoters/views/`; applied automatically on full builds
- File-driven indexes: one `.sql` file per index in
  `~/.config/ncvoters/indexes/`; applied automatically on full builds
- Both views and indexes support incremental apply — unchanged definitions
  are skipped, changed ones are dropped and recreated, failures are
  isolated and reported in a summary
- Indexes on `voters(last_name, first_name, middle_name)` and
  `voters(res_street_address)`
- `--metadata` flag to add lookup tables for status, race, ethnicity,
  county, and reason codes
- Custom `\r`-based progress bar to stderr during download and import
- YAML configuration at `~/.config/ncvoters/config.yaml` with
  `selected_columns` and `sanitize_columns` keys
- `src` layout (PEP 517), Hatchling build backend, `pyproject.toml`
- Full pytest test suite (56 tests)
- `dirstruct.md` design document describing the directory structure and
  hexagonal dependency diagram
- `sample_config.yaml` template
- Plan documents in `docs/` (`mplan.md`, `iplan.md`, `dplan.md`)

[Semantic Versioning]: https://semver.org/
[Keep a Changelog]: https://keepachangelog.com/
[Unreleased]: https://github.com/philhanna/ncvoters/compare/0.1.0..HEAD
[0.1.0]: https://github.com/philhanna/ncvoters/commits/0.1.0

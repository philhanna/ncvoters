# Changelog

## [1.1.0] - 2026-10-16

### Added
- Output columns `nc_senate`, `nc_house`, `county_id`, and `voter_id`.
- More detailed logging while processing data.

### Changed
- `nc_senate` and `nc_house` are written as integers; blank values stay blank.
- `voter_id` is read and written as text so leading zeros are preserved.
- `pytest` is now a regular dependency, so `pip install -e .` is enough.

### Fixed
- `voter_id` is taken from the real `voter_reg_num` source column.

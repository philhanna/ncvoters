# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

Added `setup.py` and `requirements.txt`

## [1.2.0] - 2022-10-29

### Added
Added auxiliary tables and views:
  - active voters view
  - counties
  - reason codes
  - status code
- Added start of `origin` notebook, which finds commonest places of origin by last name 

### Changed
- Renamed `download.py` to `download-voters.py`

### Deleted
- Removed old development modules. This is a script and notebook only project now.

## [1.1.0] - 2022-10-28

Starting in this version, there are Jupyter notebooks in preference to scripts

### Added
- Added `download.py` to download the database with a self-contained script.
Does not require the rest of this project, only the `requests` package.
- Added `top10` notebook to find most popular names in North Carolina by decade

### Changed
- Added reference links to README.md
- Refactored classes to use `pathlib.Path` instead of `os.path`

### Deleted
- Deleted old `download_voters.py` script

## [1.0.1] - 2022-10-23

### Added

- SQL to create a view with only active voters

### Changed
 
- Updated README.md

### Bug fixes

- Issue #12: `create_small_db` unit test fails
- Issue #11: Unit test fails if no zipfile is already in `/tmp`
- Issue #10: Improved test coverage
- Issue #9: Added logging during all lengthy operations

## [1.0.0] - 2022-05-07

First workable version

[Unreleased]: https://github.com/philhanna/voters/compare/1.2.0..HEAD
[1.2.0]: https://github.com/philhanna/voters/compare/1.1.0..1.2.0
[1.1.0]: https://github.com/philhanna/voters/compare/1.0.1..1.1.0
[1.0.1]: https://github.com/philhanna/voters/compare/1.0.0..1.0.1
[1.0.0]: https://github.com/philhanna/voters/compare/840698..1.0.0

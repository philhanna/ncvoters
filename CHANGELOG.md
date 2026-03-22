# Change log for go-ncvoters
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning].
The format is based on [Keep a Changelog].
	
## [Unreleased]
- Added --metadata option
- Converted main read/write loop to channels in a pipeline
- Test coverage at 100%

## [v1.3.0] - 2024-01-02
- Added configurable additional tables
- Added active table view

## [v1.2.0] - 2023-12-31
- Performance improvement using buffered reads from CSV

## [v1.1.0] - 2023-06-12
- Added command line options
- Added installation and configuration instructions to `README.md`

## [v1.0.0] - 2023-06-12
- First public release

### Added
- Issue #4 - Progress bar added
- Issue #3 - Performance improvements
  
### Bug fixes
- Issue #8 - duplicate records being created
  
## [v1.0.0-rc2] - 2023-06-09
Release candidate 2

## [v1.0.0-rc1] - 2023-05-23
Release candidate 1

[Semantic Versioning]: http://semver.org
[Keep a Changelog]: http://keepachangelog.com
[Unreleased]: https://github.com/philhanna/go-ncvoters/compare/v1.3.0..HEAD
[v1.3.0]: https://github.com/philhanna/go-ncvoters/compare/v1.2.0..v1.3.0
[v1.2.0]: https://github.com/philhanna/go-ncvoters/compare/v1.1.0..v1.2.0
[v1.1.0]: https://github.com/philhanna/go-ncvoters/compare/v1.0.0..v1.1.0
[v1.0.0]: https://github.com/philhanna/go-ncvoters/compare/v1.0.0-rc2..v1.0.0
[v1.0.0-rc2]: https://github.com/philhanna/go-ncvoters/compare/v1.0.0-rc1..v1.0.0-rc2
[v1.0.0-rc1]: https://github.com/philhanna/go-ncvoters/compare/a0324a5..v1.0.0-rc1

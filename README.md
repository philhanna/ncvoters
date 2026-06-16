# ncvoters

Create a slimmed-down CSV from publicly available North Carolina voter
registration data, published weekly by the NC State Board of Elections.

## Usage

```
python -m ncvoters [-u URL] [-o OUTPUT] [-c CHUNKSIZE]
```

After installation the `ncvoters` console script is also available.

## Architecture

The package follows a ports-and-adapters (hexagonal) layout:

- `ncvoters.domain` — pure transformation services (`sanitize`,
  `parse_county_map`, `transform_chunk`); no I/O.
- `ncvoters.ports` — the Protocol interfaces the use case depends on.
- `ncvoters.application` — the `create_voter_csv` use case.
- `ncvoters.adapters` — concrete driven adapters: HTTP layout fetch,
  pandas zip reader, CSV writer.
- `ncvoters.cli` — the driving adapter and composition root.

## Development

```
pip install -e ".[dev]"
pytest
```

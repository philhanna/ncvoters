# -*- coding: utf-8 -*-
"""Application layer: the ``create_voter_csv`` use case.

This orchestrates the domain services and the ports.  It depends only on
the port Protocols (``ncvoters.ports``) and the pure domain functions
(``ncvoters.domain``) -- never on the concrete adapters.
"""

import logging

from ncvoters.domain import parse_county_map, transform_chunk
from ncvoters.ports import LayoutProvider, VoterChunkReader, VoterWriter

logger = logging.getLogger(__name__)


def create_voter_csv(
    layout_provider: LayoutProvider,
    voter_reader: VoterChunkReader,
    voter_writer: VoterWriter,
    log=None,
) -> int:
    """Read voter data in chunks, transform each, and write it out.

    Returns the total number of (active) rows written.
    """
    if log is None:
        log = logger.info

    # Create the map of county numbers to county names.
    county_map = parse_county_map(layout_provider.get_lines())
    
    # Read and process the data in chunks (so as not to exhaust memory).
    # There are about 90-95 chunks in the file at the default chunk size.
    total_rows = 0
    for i, chunk in enumerate(voter_reader.read_chunks()):
        log(f"Processing chunk {i + 1}")
        transformed = transform_chunk(chunk, county_map)
        total_rows += len(transformed)
        voter_writer.write(transformed)

    # Finalize (e.g. sort the staged rows into the output file).
    voter_writer.close()

    return total_rows

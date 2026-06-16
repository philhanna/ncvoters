# -*- coding: utf-8 -*-
"""Ports: the Protocol interfaces the use case depends on.

These describe *what* the application needs (a source of layout lines, a
source of voter chunks, a sink for transformed rows) without committing to
*how* it is provided.  Concrete implementations live in ``ncvoters.adapters``.
"""

from collections.abc import Iterator
from typing import Protocol

import pandas as pd


class LayoutProvider(Protocol):
    """Supplies the raw lines of the NC voter layout file."""

    def get_lines(self) -> list[str]:
        ...


class VoterChunkReader(Protocol):
    """Yields the raw voter registration data one chunk at a time."""

    def read_chunks(self) -> Iterator[pd.DataFrame]:
        ...


class VoterWriter(Protocol):
    """Persists transformed voter chunks to the output destination."""

    def write(self, df: pd.DataFrame) -> None:
        ...

    def close(self) -> None:
        """Finalize the output once all chunks have been written."""
        ...

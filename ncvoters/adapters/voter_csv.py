# -*- coding: utf-8 -*-
"""Driven adapter: write transformed voter chunks to a CSV file.

Implements the ``VoterWriter`` port.  Any pre-existing file is removed up
front so the output always starts fresh; the column header is written only
with the first chunk and subsequent chunks are appended.
"""

import os


class CsvVoterWriter:
    """Appends chunks to a CSV, writing the header only once."""

    def __init__(self, path):
        self.path = path
        self._header_written = False

        # Delete the output CSV if it already exists.
        if os.path.exists(path):
            os.remove(path)
            print(f"Deleted existing file: {path}")

    def write(self, df):
        df.to_csv(
            self.path,
            mode='a',
            header=not self._header_written,
            index=False,
        )
        self._header_written = True

# -*- coding: utf-8 -*-
"""Driven adapter: read the voter registration zip with pandas.

Implements the ``VoterChunkReader`` port.  The source is the publicly
published statewide zip file (a tab-separated, latin1-encoded CSV).
"""

import pandas as pd


class PandasZipVoterReader:
    """Reads the zipped statewide CSV in memory-friendly chunks."""

    def __init__(self, url, chunksize=100000):
        self.url = url
        self.chunksize = chunksize

    def read_chunks(self):
        return pd.read_csv(
            self.url,
            compression='zip',
            sep='\t',
            encoding='latin1',
            chunksize=self.chunksize,
            low_memory=False,
            # Keep zip codes as strings so leading zeros survive and they
            # are never coerced to a float (e.g. 27601.0).
            dtype={'zip_code': str},
        )

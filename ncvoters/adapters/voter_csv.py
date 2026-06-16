# -*- coding: utf-8 -*-
"""Driven adapter: write transformed voter chunks to a CSV file.

Implements the ``VoterWriter`` port.  Chunks are appended to a temporary
file in the system temp directory (e.g. ``/tmp`` on Linux); the column
header is written only with the first chunk.  ``close()`` then sorts the
data rows -- preserving the header -- into the final output path using an
external merge sort, so memory stays bounded regardless of file size.
"""

import heapq
import itertools
import os
import tempfile

# Maximum number of data rows held in memory while sorting a single run.
DEFAULT_BATCH_SIZE = 1_000_000


class CsvVoterWriter:
    """Stages chunks in a temp file, then sorts them into the output CSV."""

    def __init__(self, path, batch_size=DEFAULT_BATCH_SIZE):
        self.path = path
        self.batch_size = batch_size
        self._header_written = False

        # Stage chunks in a temp file (in /tmp or the OS equivalent);
        # close() sorts it into `path`.
        fd, self._temp_path = tempfile.mkstemp(
            prefix=os.path.basename(path) + ".", suffix=".unsorted")
        os.close(fd)

        # Delete the output CSV if it already exists.
        if os.path.exists(path):
            os.remove(path)
            print(f"Deleted existing file: {path}")

    def write(self, df):
        df.to_csv(
            self._temp_path,
            mode='a',
            header=not self._header_written,
            index=False,
        )
        self._header_written = True

    def close(self):
        """Sort the staged rows (keeping the header first) into the output.

        Uses an external merge sort: the staged rows are split into sorted
        runs of at most ``batch_size`` lines, then the runs are merged in a
        single streaming pass.  Only one batch is ever held in memory.
        """
        if not self._header_written:
            # Nothing was written; just discard the empty temp file.
            os.remove(self._temp_path)
            return

        run_paths = []
        try:
            with open(self._temp_path, encoding='utf-8', newline='') as staged:
                header = staged.readline()
                run_paths = self._write_sorted_runs(staged)
            self._merge_runs(header, run_paths)
        finally:
            for run_path in run_paths:
                if os.path.exists(run_path):
                    os.remove(run_path)
            os.remove(self._temp_path)

    def _write_sorted_runs(self, staged):
        """Split staged rows into sorted run files; return their paths."""
        run_paths = []
        while True:
            batch = list(itertools.islice(staged, self.batch_size))
            if not batch:
                break
            batch.sort()
            fd, run_path = tempfile.mkstemp(
                prefix=os.path.basename(self.path) + ".", suffix=".run")
            with os.fdopen(fd, 'w', encoding='utf-8', newline='') as run:
                run.writelines(batch)
            run_paths.append(run_path)
        return run_paths

    def _merge_runs(self, header, run_paths):
        """Merge the sorted runs into the output, writing the header first."""
        runs = [open(p, encoding='utf-8', newline='') for p in run_paths]
        try:
            with open(self.path, 'w', encoding='utf-8', newline='') as out:
                out.write(header)
                out.writelines(heapq.merge(*runs))
        finally:
            for run in runs:
                run.close()

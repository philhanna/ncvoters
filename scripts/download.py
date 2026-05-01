#!/usr/bin/env python3
"""Download the NC voter registration zip file."""

import sys
import urllib.request
from pathlib import Path

URL = "https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvoter_Statewide.zip"
DEFAULT_DEST = "/tmp/voter_data.zip"


def download(url: str, dest: str) -> None:
    print(f"Downloading {url}", file=sys.stderr)
    print(f"         -> {dest}", file=sys.stderr)

    def progress(count, block_size, total_size):
        if total_size > 0:
            pct = min(count * block_size * 100 // total_size, 100)
            print(f"\r  {pct}%", end="", file=sys.stderr, flush=True)

    urllib.request.urlretrieve(url, dest, reporthook=progress)
    print(file=sys.stderr)
    size_mb = Path(dest).stat().st_size / (1024 * 1024)
    print(f"Done ({size_mb:.0f} MB).", file=sys.stderr)


if __name__ == "__main__":
    dest = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DEST
    download(URL, dest)

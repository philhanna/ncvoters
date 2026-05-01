#!/usr/bin/env python3
"""Download the NC voter registration zip file."""

import sys
import urllib.request
from pathlib import Path

# Public S3 URL published by the NC State Board of Elections.

URL = "https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvoter_Statewide.zip"
DEFAULT_DEST = "/tmp/voter_data.zip"


def download(url: str, dest: str) -> None:
    """Download a file from url and save it to dest.

    Streams the download in blocks via urllib, printing a percentage progress
    indicator to stderr. Reports the final file size in megabytes when done.

    Args:
        url: The URL to download.
        dest: Local filesystem path where the file will be written.
    """
    print(f"Downloading {url}", file=sys.stderr)
    print(f"         -> {dest}", file=sys.stderr)

    def progress(count, block_size, total_size):
        """Print an in-place percentage progress indicator to stderr.

        Args:
            count: Number of blocks transferred so far.
            block_size: Size of each block in bytes.
            total_size: Total file size in bytes, or -1 if the server did not
                send a Content-Length header.
        """
        # total_size is -1 when the server omits Content-Length.

        if total_size > 0:
            pct = min(count * block_size * 100 // total_size, 100)
            print(f"\r  {pct}%", end="", file=sys.stderr, flush=True)

    urllib.request.urlretrieve(url, dest, reporthook=progress)

    # Move past the in-place progress line before reporting the final file size.

    print(file=sys.stderr)
    size_mb = Path(dest).stat().st_size / (1024 * 1024)
    print(f"Done ({size_mb:.0f} MB).", file=sys.stderr)


if __name__ == "__main__":
    dest = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DEST
    download(URL, dest)

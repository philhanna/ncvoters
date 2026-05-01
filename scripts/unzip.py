#!/usr/bin/env python3
"""Extract the voter txt file from the NC voter zip."""

import sys
import zipfile
from pathlib import Path

ENTRY_NAME = "ncvoter_Statewide.txt"
DEFAULT_ZIP = "/tmp/voter_data.zip"
DEFAULT_DEST = "/tmp/ncvoter_Statewide.txt"
CHUNK = 1 << 20  # 1 MB


def unzip(zip_path: str, dest_path: str) -> None:
    print(f"Extracting {ENTRY_NAME}", file=sys.stderr)
    print(f"      from {zip_path}", file=sys.stderr)
    print(f"        to {dest_path}", file=sys.stderr)

    with zipfile.ZipFile(zip_path) as zf:
        info = zf.getinfo(ENTRY_NAME)
        total = info.file_size
        written = 0

        with zf.open(ENTRY_NAME) as src, open(dest_path, "wb") as dst:
            while chunk := src.read(CHUNK):
                dst.write(chunk)
                written += len(chunk)
                if total > 0:
                    pct = written * 100 // total
                    print(f"\r  {pct}%", end="", file=sys.stderr, flush=True)

    print(file=sys.stderr)
    size_gb = Path(dest_path).stat().st_size / (1024 ** 3)
    print(f"Done ({size_gb:.1f} GB).", file=sys.stderr)


if __name__ == "__main__":
    zip_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ZIP
    dest_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DEST
    unzip(zip_path, dest_path)

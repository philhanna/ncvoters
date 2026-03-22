import sys
import time

import requests

from ncvoters.ports.outbound import FileDownloaderPort

_BLOCK_SIZE = 1024 * 1024  # 1 MB
_BAR_WIDTH = 50


class HttpFileDownloader(FileDownloaderPort):
    """Downloads a file over HTTP with a live progress bar."""

    def __init__(self, quiet: bool = False) -> None:
        self._quiet = quiet

    def download(self, url: str, dest_path: str) -> None:
        head = requests.head(url, allow_redirects=True, timeout=30)
        head.raise_for_status()
        total = int(head.headers.get("content-length", 0))

        if not self._quiet:
            mb_total = total / _BLOCK_SIZE
            print(f"Downloading file ({mb_total:.2f} MB)...", file=sys.stderr)

        so_far = 0
        last_percent = -1
        start = time.monotonic()

        with requests.get(url, stream=True, timeout=60) as resp:
            resp.raise_for_status()
            with open(dest_path, "wb") as fh:
                for chunk in resp.iter_content(chunk_size=_BLOCK_SIZE):
                    fh.write(chunk)
                    so_far += len(chunk)
                    if total > 0 and not self._quiet:
                        percent = int(so_far / total * 100)
                        if percent > last_percent:
                            filled = "*" * (percent // 2)
                            bar = f"{filled:<{_BAR_WIDTH}}"
                            mb_so_far = so_far / _BLOCK_SIZE
                            elapsed = time.monotonic() - start
                            print(
                                f"\rPercent complete: {percent}%, [{bar}] {mb_so_far:.2f} MB in {elapsed:.1f}s",
                                end="",
                                flush=True,
                                file=sys.stderr,
                            )
                            last_percent = percent

        if not self._quiet:
            print(file=sys.stderr)
            print("File downloaded successfully!", file=sys.stderr)

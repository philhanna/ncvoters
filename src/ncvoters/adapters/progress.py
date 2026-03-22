import sys
import time


class Progress:
    """Renders a single-line progress bar to stderr using carriage returns."""

    BAR_WIDTH = 50

    def __init__(self, total: int, quiet: bool = False) -> None:
        self.total = total
        self.so_far = 0
        self.last_percent = -1
        self.quiet = quiet
        self._start = time.monotonic()

    def update(self, n: int = 1) -> None:
        self.so_far += n
        if self.quiet or self.total <= 0:
            return
        percent = int(self.so_far / self.total * 100)
        if percent > self.last_percent:
            filled = "*" * (percent // 2)
            bar = f"{filled:<{self.BAR_WIDTH}}"
            elapsed = time.monotonic() - self._start
            print(
                f"\rPercent complete: {percent}%, [{bar}] {self.so_far:,} records in {elapsed:.1f}s",
                end="",
                flush=True,
                file=sys.stderr,
            )
            self.last_percent = percent

    def finish(self) -> None:
        if not self.quiet:
            print(file=sys.stderr)

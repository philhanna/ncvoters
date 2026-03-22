# ncvoters.application.create_voter_database
"""Use case: CreateVoterDatabase."""

import csv
import io
import logging
import re
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Iterator

from ncvoters.adapters.progress import Progress
from ncvoters.domain.models import Configuration
from ncvoters.ports.outbound import FileDownloaderPort, VoterRepositoryPort

from ncvoters.application.apply_indexes import ApplyIndexes
from ncvoters.application.apply_views import ApplyViews

log = logging.getLogger(__name__)

ZIP_URL = "https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvoter_Statewide.zip"
ENTRY_NAME = "ncvoter_Statewide.txt"

# Heuristic ratio for estimating voter count from uncompressed file size
# (values from March 22, 2026 file — update periodically)
_NUMER = 9_099_826
_DENOM = 4_258_425_549

_WS = re.compile(r"\s+")


def _rename_existing_db(db_path: str) -> None:
    """Rename an existing database file to a timestamped backup in the same directory."""
    p = Path(db_path)
    if not p.exists():
        return
    stem = p.stem  # e.g. "voter_data"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = p.with_name(f"{stem}_{timestamp}{p.suffix}")
    p.rename(backup)
    log.info("Renamed existing database to %s", backup)


def _estimate_voters(uncompressed_size: int) -> int:
    return round(uncompressed_size * _NUMER / _DENOM)


def _sanitize(value: str) -> str:
    return _WS.sub(" ", value).strip()


def _is_good_zip(path: str) -> bool:
    try:
        with zipfile.ZipFile(path) as zf:
            return len(zf.namelist()) > 0
    except zipfile.BadZipFile:
        return False


def _default_indexes_dir() -> Path:
    return Path.home() / ".config" / "ncvoters" / "indexes"


def _default_views_dir() -> Path:
    return Path.home() / ".config" / "ncvoters" / "views"


class CreateVoterDatabase:
    """Downloads the NC voter zip file and populates the voters table."""

    def __init__(
        self,
        config: Configuration,
        downloader: FileDownloaderPort,
        repo: VoterRepositoryPort,
        quiet: bool = False,
    ) -> None:
        self._config = config
        self._downloader = downloader
        self._repo = repo
        self._quiet = quiet

    def execute(
        self,
        zip_path: str,
        db_path: str,
        force: bool = False,
        max_entries: int = 0,
    ) -> None:
        if not self._quiet:
            log.info("Starting voter database creation")

        # Download or reuse the zip file
        zip_file = Path(zip_path)
        reuse = zip_file.exists() and _is_good_zip(zip_path) and not force
        if reuse:
            if not self._quiet:
                log.info("Reusing existing zip file: %s", zip_path)
        else:
            self._downloader.download(ZIP_URL, zip_path)

        # Rename existing database so we start fresh
        _rename_existing_db(db_path)

        if not self._quiet:
            log.info("Creating database...")

        self._repo.create_voters_table(self._config.selected_columns)
        self._repo.insert_voters(self._stream_voters(zip_path, max_entries))

        if not self._quiet:
            log.info("Building indexes...")
        ApplyIndexes(self._repo, _default_indexes_dir(), quiet=self._quiet).execute(incremental=False)

        ApplyViews(self._repo, _default_views_dir(), quiet=self._quiet).execute(incremental=False)

        if not self._quiet:
            log.info("Database created successfully!")

    def _stream_voters(self, zip_path: str, max_entries: int) -> Iterator[list[str]]:
        selected = self._config.selected_columns
        sanitize_set = set(self._config.sanitize_columns)

        with zipfile.ZipFile(zip_path) as zf:
            info = zf.getinfo(ENTRY_NAME)
            estimated = _estimate_voters(info.file_size)
            progress = Progress(estimated, quiet=self._quiet)

            with zf.open(ENTRY_NAME) as raw:
                text = io.TextIOWrapper(raw, encoding="latin-1", newline="")
                reader = csv.DictReader(text, delimiter="\t")

                count = 0
                for row in reader:
                    values = [
                        _sanitize(row.get(col, "")) if col in sanitize_set else row.get(col, "")
                        for col in selected
                    ]
                    yield values
                    count += 1
                    progress.update()
                    if max_entries > 0 and count >= max_entries:
                        break

            progress.finish()

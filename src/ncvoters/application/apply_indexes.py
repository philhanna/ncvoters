# ncvoters.application.apply_indexes
"""Use case: ApplyIndexes."""

import logging
from dataclasses import dataclass, field
from pathlib import Path

from ncvoters.adapters.index_loader import extract_index_name, load_index_files
from ncvoters.adapters.view_loader import normalise_sql
from ncvoters.ports.outbound import VoterRepositoryPort

log = logging.getLogger(__name__)


@dataclass
class ApplyIndexesResult:
    applied: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: list[tuple[str, str]] = field(default_factory=list)  # (name, error)

    def log_summary(self) -> None:
        applied = ", ".join(self.applied) or "none"
        skipped = ", ".join(self.skipped) or "none"
        log.info("Indexes applied: %d  (%s)", len(self.applied), applied)
        log.info("Indexes skipped: %d  (%s)", len(self.skipped), skipped)
        if self.failed:
            for name, err in self.failed:
                log.warning("Index FAILED: %s — %s", name, err)
        log.info("Indexes failed:  %d", len(self.failed))


class ApplyIndexes:
    """Applies SQL index files from the indexes directory to the database.

    In full-build mode (incremental=False) every file is applied unconditionally.
    In incremental mode indexes that are already up to date are skipped, and
    changed indexes are dropped and recreated.
    """

    def __init__(
        self,
        repo: VoterRepositoryPort,
        indexes_dir: Path,
        quiet: bool = False,
    ) -> None:
        self._repo = repo
        self._indexes_dir = indexes_dir
        self._quiet = quiet

    def execute(self, incremental: bool = True) -> ApplyIndexesResult:
        result = ApplyIndexesResult()
        files = load_index_files(self._indexes_dir)

        if not files:
            if not self._quiet:
                log.info("No index files found in %s", self._indexes_dir)
            return result

        if not self._quiet:
            log.info("Applying indexes from %s...", self._indexes_dir)

        for filename, sql in files:
            try:
                name = extract_index_name(sql)
            except ValueError as exc:
                result.failed.append((filename, str(exc)))
                log.warning("Skipping %s: %s", filename, exc)
                continue

            try:
                if incremental:
                    existing = self._repo.existing_index_sql(name)
                    if existing is not None:
                        if normalise_sql(existing) == normalise_sql(sql):
                            result.skipped.append(name)
                            if not self._quiet:
                                log.info("  %s — already up to date", name)
                            continue
                        # SQL has changed — drop and recreate
                        self._repo.apply_index(f"DROP INDEX {name}")

                self._repo.apply_index(sql)
                result.applied.append(name)
                if not self._quiet:
                    log.info("  %s — applied", name)

            except Exception as exc:
                result.failed.append((name, str(exc)))
                log.warning("  %s — FAILED: %s", name, exc)

        if not self._quiet:
            result.log_summary()

        return result

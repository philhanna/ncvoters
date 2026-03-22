# ncvoters.application.apply_views
"""Use case: ApplyViews."""

import logging
from dataclasses import dataclass, field
from pathlib import Path

from ncvoters.adapters.view_loader import extract_view_name, load_view_files, normalise_sql
from ncvoters.ports.outbound import VoterRepositoryPort

log = logging.getLogger(__name__)


@dataclass
class ApplyViewsResult:
    applied: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: list[tuple[str, str]] = field(default_factory=list)  # (name, error)

    def log_summary(self) -> None:
        applied = ", ".join(self.applied) or "none"
        skipped = ", ".join(self.skipped) or "none"
        log.info("Views applied: %d  (%s)", len(self.applied), applied)
        log.info("Views skipped: %d  (%s)", len(self.skipped), skipped)
        if self.failed:
            for name, err in self.failed:
                log.warning("View FAILED: %s — %s", name, err)
        log.info("Views failed:  %d", len(self.failed))


class ApplyViews:
    """Applies SQL view files from the views directory to the database.

    In full-build mode (incremental=False) every file is applied unconditionally.
    In incremental mode views that are already up to date are skipped, and
    changed views are dropped and recreated.
    """

    def __init__(
        self,
        repo: VoterRepositoryPort,
        views_dir: Path,
        quiet: bool = False,
    ) -> None:
        self._repo = repo
        self._views_dir = views_dir
        self._quiet = quiet

    def execute(self, incremental: bool = True) -> ApplyViewsResult:
        result = ApplyViewsResult()
        files = load_view_files(self._views_dir)

        if not files:
            if not self._quiet:
                log.info("No view files found in %s", self._views_dir)
            return result

        if not self._quiet:
            log.info("Applying views from %s...", self._views_dir)

        for filename, sql in files:
            try:
                name = extract_view_name(sql)
            except ValueError as exc:
                result.failed.append((filename, str(exc)))
                log.warning("Skipping %s: %s", filename, exc)
                continue

            try:
                if incremental:
                    existing = self._repo.existing_view_sql(name)
                    if existing is not None:
                        if normalise_sql(existing) == normalise_sql(sql):
                            result.skipped.append(name)
                            if not self._quiet:
                                log.info("  %s — already up to date", name)
                            continue
                        # SQL has changed — drop and recreate
                        self._repo.apply_view(f"DROP VIEW {name}")

                self._repo.apply_view(sql)
                result.applied.append(name)
                if not self._quiet:
                    log.info("  %s — applied", name)

            except Exception as exc:
                result.failed.append((name, str(exc)))
                log.warning("  %s — FAILED: %s", name, exc)

        if not self._quiet:
            result.log_summary()

        return result

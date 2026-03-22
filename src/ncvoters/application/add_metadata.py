# ncvoters.application.add_metadata
"""Use case: AddMetadata."""

import logging

from ncvoters.ports.outbound import LayoutFetcherPort, VoterRepositoryPort

log = logging.getLogger(__name__)

LAYOUT_URL = "https://s3.amazonaws.com/dl.ncsbe.gov/data/layout_ncvoter.txt"


class AddMetadata:
    """Downloads the layout file and creates lookup tables in the database."""

    def __init__(
        self,
        layout_fetcher: LayoutFetcherPort,
        repo: VoterRepositoryPort,
        quiet: bool = False,
    ) -> None:
        self._layout_fetcher = layout_fetcher
        self._repo = repo
        self._quiet = quiet

    def execute(self) -> None:
        if not self._quiet:
            log.info("Adding metadata tables...")
        layout = self._layout_fetcher.fetch(LAYOUT_URL)
        self._repo.add_metadata(layout)
        if not self._quiet:
            log.info("Metadata tables added.")

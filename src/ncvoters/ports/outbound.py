"""Outbound (driven) port interfaces.

In hexagonal architecture these are the boundaries the application
core uses to talk to infrastructure: database, HTTP, filesystem, etc.
Concrete implementations live in ``ncvoters.adapters``.
"""

from abc import ABC, abstractmethod
from typing import Iterator

from ncvoters.domain.models import Configuration, Layout


class ConfigurationPort(ABC):
    """Loads application configuration from an external source."""

    @abstractmethod
    def load(self) -> Configuration: ...


class FileDownloaderPort(ABC):
    """Downloads a remote file to a local path."""

    @abstractmethod
    def download(self, url: str, dest_path: str) -> None: ...


class LayoutFetcherPort(ABC):
    """Fetches and parses the NC voter layout metadata."""

    @abstractmethod
    def fetch(self, url: str) -> Layout: ...


class VoterRepositoryPort(ABC):
    """Persists voter data and metadata to a database."""

    @abstractmethod
    def create_voters_table(self, columns: list[str]) -> None: ...

    @abstractmethod
    def insert_voters(self, rows: Iterator[list[str]]) -> None: ...

    @abstractmethod
    def create_indexes(self) -> None: ...

    @abstractmethod
    def apply_view(self, sql: str) -> None: ...

    @abstractmethod
    def existing_view_sql(self, name: str) -> str | None: ...

    @abstractmethod
    def add_metadata(self, layout: Layout) -> None: ...

from pathlib import Path

import yaml

from ncvoters.domain.models import Configuration
from ncvoters.ports.outbound import ConfigurationPort

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "ncvoters" / "config.yaml"


class YamlConfigLoader(ConfigurationPort):
    """Loads :class:`Configuration` from a YAML file."""

    def __init__(self, path: Path = DEFAULT_CONFIG_PATH) -> None:
        self._path = path

    def load(self) -> Configuration:
        if not self._path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self._path}\n"
                "Create it with the columns you want to import.  "
                "See sample_config.yaml for an example."
            )
        with open(self._path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return Configuration(
            selected_columns=data.get("selected_columns", []),
            sanitize_columns=data.get("sanitize_columns", []),
            db_dir=data.get("db_dir", None),
        )

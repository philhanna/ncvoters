import textwrap
from pathlib import Path

import pytest

from ncvoters.adapters.config_loader import YamlConfigLoader


def test_load_valid_config(tmp_path: Path) -> None:
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(
        textwrap.dedent("""\
            selected_columns:
              - last_name
              - first_name
            sanitize_columns:
              - last_name
        """)
    )
    loader = YamlConfigLoader(path=cfg_file)
    config = loader.load()
    assert config.selected_columns == ["last_name", "first_name"]
    assert config.sanitize_columns == ["last_name"]


def test_load_missing_file(tmp_path: Path) -> None:
    loader = YamlConfigLoader(path=tmp_path / "missing.yaml")
    with pytest.raises(FileNotFoundError):
        loader.load()

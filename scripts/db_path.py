#!/usr/bin/env python3
"""Print the resolved database path from config."""

import sys
import tempfile
from pathlib import Path

import yaml

CONFIG_PATH = Path.home() / ".config" / "ncvoters" / "config.yaml"


def main():
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        db_dir = config.get("db_dir")
        if db_dir:
            print(str(Path(db_dir).expanduser() / "voter_data.db"))
            return
    except FileNotFoundError:
        pass
    print(str(Path(tempfile.gettempdir()) / "voter_data.db"))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Print the resolved database path from config."""

import sys
import tempfile
from pathlib import Path

import yaml

# Default location for the user-level config file.

CONFIG_PATH = Path.home() / ".config" / "ncvoters" / "config.yaml"


def main():
    """Print the resolved path to voter_data.db to stdout.

    Reads db_dir from CONFIG_PATH if the file exists and the key is set,
    then prints <db_dir>/voter_data.db. Falls back to the system temp
    directory when the config file is absent or db_dir is not configured.
    """
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        db_dir = config.get("db_dir")

        # If db_dir is set in config, use it; expanduser handles "~" in the path.

        if db_dir:
            print(str(Path(db_dir).expanduser() / "voter_data.db"))
            return
    except FileNotFoundError:
        pass

    # Fall back to the system temp directory so the tool works without configuration.

    print(str(Path(tempfile.gettempdir()) / "voter_data.db"))


if __name__ == "__main__":
    main()

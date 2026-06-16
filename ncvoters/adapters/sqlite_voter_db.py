# -*- coding: utf-8 -*-
"""Driven adapter: create a SQLite database from the generated CSV."""

import csv
import logging
import os
import sqlite3
from pathlib import Path

DEFAULT_TABLE_NAME = "voters"
DEFAULT_BATCH_SIZE = 10_000
logger = logging.getLogger(__name__)


def default_views_dir():
    """Return the per-user views directory for the current platform."""
    if os.name == "nt":
        config_root = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
    elif os.environ.get("XDG_CONFIG_HOME"):
        config_root = Path(os.environ["XDG_CONFIG_HOME"])
    elif os.sys.platform == "darwin":
        config_root = Path.home() / "Library/Application Support"
    else:
        config_root = Path.home() / ".config"
    return config_root / "ncvoters" / "views"


DEFAULT_VIEWS_DIR = default_views_dir()


def create_sqlite_from_csv(
    csv_path,
    db_path,
    table_name=DEFAULT_TABLE_NAME,
    batch_size=DEFAULT_BATCH_SIZE,
):
    """Stream CSV rows into a SQLite table using the CSV header as columns."""
    if os.path.exists(db_path):
        os.remove(db_path)
        logger.info("Deleted existing file: %s", db_path)

    with sqlite3.connect(db_path) as connection:
        logger.info(f"Creating {db_path} database")
        with open(csv_path, encoding="utf-8", newline="") as csv_file:
            logger.info(f"Reading {csv_path} input file")
            reader = csv.reader(csv_file)
            columns = next(reader)

            quoted_columns = ", ".join(f'"{column}" TEXT' for column in columns)
            placeholders = ", ".join("?" for _ in columns)
            quoted_names = ", ".join(f'"{column}"' for column in columns)

            connection.execute(
                f'CREATE TABLE "{table_name}" ({quoted_columns})'
            )

            batch = []
            bnumber = 0
            for row in reader:
                batch.append(row)
                if len(batch) >= batch_size:
                    bnumber += 1
                    logger.info(f"Batch {bnumber}. Appending {len(batch)} rows to database")
                    connection.executemany(
                        f'INSERT INTO "{table_name}" ({quoted_names}) '
                        f"VALUES ({placeholders})",
                        batch,
                    )
                    batch.clear()

            if batch:
                connection.executemany(
                    f'INSERT INTO "{table_name}" ({quoted_names}) '
                    f"VALUES ({placeholders})",
                    batch,
                )

        create_indexes(connection, table_name)
        create_views(connection)
        connection.commit()


def create_indexes(connection, table_name):
    """Create the indexes used by common voter lookups."""
    logger.info(f"Creating addresses index")
    connection.execute(
        f'CREATE INDEX "addresses" ON "{table_name}" ("address")'
    )
    logger.info(f"Creating names index")
    connection.execute(
        f'CREATE INDEX "names" ON "{table_name}" '
        '("last_name", "first_name", "middle_name")'
    )


def create_views(connection, views_dir=DEFAULT_VIEWS_DIR):
    """Apply each SQL file from the configured views directory."""
    views_path = Path(views_dir).expanduser()
    if not views_path.is_dir():
        return

    for sql_path in sorted(views_path.glob("*.sql")):
        logger.info(f"Creating {sql_path} view")
        connection.executescript(sql_path.read_text(encoding="utf-8"))

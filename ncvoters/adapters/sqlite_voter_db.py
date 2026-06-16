# -*- coding: utf-8 -*-
"""Driven adapter: create a SQLite database from the generated CSV."""

import csv
import os
import sqlite3

DEFAULT_TABLE_NAME = "voters"
DEFAULT_BATCH_SIZE = 10_000


def create_sqlite_from_csv(
    csv_path,
    db_path,
    table_name=DEFAULT_TABLE_NAME,
    batch_size=DEFAULT_BATCH_SIZE,
):
    """Stream CSV rows into a SQLite table using the CSV header as columns."""
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Deleted existing file: {db_path}")

    with sqlite3.connect(db_path) as connection:
        with open(csv_path, encoding="utf-8", newline="") as csv_file:
            reader = csv.reader(csv_file)
            columns = next(reader)

            quoted_columns = ", ".join(f'"{column}" TEXT' for column in columns)
            placeholders = ", ".join("?" for _ in columns)
            quoted_names = ", ".join(f'"{column}"' for column in columns)

            connection.execute(
                f'CREATE TABLE "{table_name}" ({quoted_columns})'
            )

            batch = []
            for row in reader:
                batch.append(row)
                if len(batch) >= batch_size:
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

        connection.commit()

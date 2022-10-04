import os
import sqlite3
from unittest import TestCase

from tests import testdata
from voters import DBLoader, DBCreator, TMP


class TestDBLoader(TestCase):

    def test_create_insert_stmt(self):
        stmt = DBLoader.create_insert_stmt()

        # Should be only one line
        expected = 1
        actual = len(stmt.splitlines())
        self.assertEqual(expected, actual)

        # Line should start with "INSERT "
        expected = True
        actual = stmt.startswith("INSERT ")
        self.assertEqual(expected, actual)

    def test_create_small_db(self):
        # Make a database file name in /tmp

        filename = "ten_voters.txt"
        zipfile = os.path.join(testdata, "ten_voters.zip")
        db_file_name = os.path.join(TMP, "small.db")
        if os.path.exists(db_file_name):
            os.remove(db_file_name)

        # Create the small database with just the table definitions,
        # not any rows of data
        creator = DBCreator(filename=db_file_name)
        creator.run()

        # Now load a few records from the actual network source
        loader = DBLoader(filename=filename, zipfile=zipfile, db_file_name=db_file_name)
        loader.run(limit=6)

        # The database now should contain ten records in the "voters" table
        with sqlite3.connect(db_file_name) as con:
            c = con.cursor()
            c.execute("select count(*) from voters;")
            rows = c.fetchall()

            expected = 1
            actual = len(rows)
            self.assertEqual(expected, actual)

            expected = 6
            actual = int(rows[0][0])
            self.assertEqual(expected, actual)

        # Delete the database file if the tests were successful
        os.remove(db_file_name)

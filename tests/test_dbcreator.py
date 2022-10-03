import os
from unittest import TestCase, skip

from voters import DBCreator, DB_FILE_NAME


class TestDBCreator(TestCase):

    def test_max_width(self):
        expected = len("res_street_address")
        actual = DBCreator.max_width()
        self.assertEqual(expected, actual)

    def test_create_schema(self):
        stmt = DBCreator.create_schema()
        self.assertTrue(stmt.startswith("CREATE TABLE voters"))
        self.assertIn("birth_state", stmt)

    def test_run(self):
        creator = DBCreator()
        creator.run()
        self.assertTrue(os.path.exists(DB_FILE_NAME))

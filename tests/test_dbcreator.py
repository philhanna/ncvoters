import os
from unittest import TestCase, skip

from voters import DBCreator, DB_FILE_NAME


class TestDBCreator(TestCase):

    def test_max_width(self):
        expected = len("res_street_address")
        actual = DBCreator.max_width()
        self.assertEqual(expected, actual)

    @skip("For debugging only")
    def test_create_schema(self):
        sql = DBCreator.create_schema()
        print(sql)

    def test_run(self):
        creator = DBCreator()
        creator.run()
        self.assertTrue(os.path.exists(DB_FILE_NAME))

from unittest import TestCase

from voters.dbcreator import DBCreator


class TestDBCreator(TestCase):

    def test_max_width(self):
        expected = len("res_street_address")
        actual = DBCreator.max_width()
        self.assertEqual(expected, actual)

    def test_create_schema(self):
        sql = DBCreator.create_schema()
        print(sql)

from unittest import TestCase, skipIf, skip

from voters import DBLoader, DBCreator


class TestDBLoader(TestCase):

    @skipIf(True, "Only for debug")
    def test_create_insert_stmt(self):
        print(DBLoader.create_insert_stmt())

    @skip("Do not load first 100 rows")
    def test_load_100(self):
        """ Creates a sample database from the first 100 rows in the CSV file. """
        creator = DBCreator()
        creator.run()
        DBLoader.run(limit=100)

    @skip("Do not load the whole database")
    def test_load_all(self):
        creator = DBCreator()
        creator.run()
        DBLoader.run()

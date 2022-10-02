from unittest import TestCase, skipIf, skip

from voters import DBLoader, DBCreator


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

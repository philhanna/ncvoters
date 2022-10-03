import os
from unittest import TestCase

from tests import testdata
from voters import COLUMNS, CSVExtractor


class TestExtractor(TestCase):

    def setUp(self):
        self.zipfile = os.path.join(testdata, "ten_voters.zip")
        self.filename = "ten_voters.txt"

    def test_columns(self):
        self.assertEqual(20, len(COLUMNS))

    def test_select_columns(self):
        row = [
            "able", "baker", "charlie", "dog", "easy", "foxtrot", "gamma"
        ]
        column_list = [1, 2]
        outrow = [row[x] for x in column_list]
        self.assertListEqual(['baker', 'charlie'], outrow)

    def test_get_rows_with_limit(self):
        extractor = CSVExtractor(filename=self.filename,zipfile=self.zipfile)
        expected = 4
        actual = 0
        for row in extractor.get_rows(limit=expected):
            actual += 1
        self.assertEqual(expected, actual)

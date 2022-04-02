from unittest import TestCase

from voters import COLUMNS
from voters.extractor import Extractor


class TestExtractor(TestCase):

    def test_columns(self):
        self.assertEqual(20, len(COLUMNS))

    def test_select_columns(self):
        row = [
            "able", "baker", "charlie", "dog", "easy", "foxtrot", "gamma"
        ]
        column_list = [1, 2]
        outrow = Extractor.select_columns(row, column_list)
        self.assertListEqual(['baker', 'charlie'], outrow)

    def test_get_run(self):
        extractor = Extractor()
        expected = 10
        actual = 0
        for row in extractor.get_rows(limit=expected):
            actual += 1
        self.assertEqual(expected, actual)

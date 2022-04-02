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

    def test_run(self):
        extractor = Extractor()
        extractor.run(limit=5)

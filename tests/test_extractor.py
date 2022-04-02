from unittest import TestCase

from voters import COLUMNS


class TestExtractor(TestCase):

    def test_columns(self):
        for k in COLUMNS.keys():
            print(k)

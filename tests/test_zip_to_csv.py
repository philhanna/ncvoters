import io
from unittest import TestCase
import os.path
from zipfile import ZipFile

from tests import TMP


def create_zipfile():
    stooges = os.path.join(TMP, "stooges.txt")
    with open(stooges, "wt") as fp:
        print("name,rank,saying", file=fp)
        print("Curly,3,'Nyuk, nyuk, nyuk'", file=fp)
        print("Larry,2,'Owwww!'", file=fp)
        print("Moe,1,'Why, I oughtta ...'", file=fp)
    zipfile = os.path.join(TMP, "stooges.zip")
    with ZipFile(zipfile, mode="w") as archive:
        archive.write(stooges, "stooges.txt")
    return zipfile


class TestZipToCSV(TestCase):

    def test_create(self):
        zipfile = create_zipfile()
        with ZipFile(zipfile) as zf:
            with io.TextIOWrapper(zf.open("stooges.txt"), encoding="utf-8") as fp:
                line_count = 0
                for line in fp:
                    line_count += 1
        self.assertEqual(4, line_count)

    def test_get_filename(self):
        zipfile = create_zipfile()
        with ZipFile(zipfile) as zf:
            list_of_names = zf.namelist()
        self.assertEqual(1, len(list_of_names))
        filename = list_of_names[0]
        self.assertEqual("stooges.txt", filename)

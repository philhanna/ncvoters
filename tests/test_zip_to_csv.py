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


class TestZipToCSV(TestCase):

    def test_dummy(self):
        create_zipfile()

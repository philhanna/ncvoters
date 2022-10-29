import filecmp
from pathlib import Path
from unittest import TestCase
from zipfile import ZipFile

from tests import outputs, testdata
from voters import ZIP_FILE_NAME, ZipDownloader


class TestDownloader(TestCase):

    def test_run_file_size(self):
        zipfile = testdata.joinpath("ten_voters.zip")
        app = ZipDownloader(zipfile)
        app.zipfile_size = zipfile.stat().st_size
        app.run()
        expected = 1585
        actual = app.zipfile_size
        self.assertEqual(expected, actual)

    def test_run_with_ten_voters(self):

        class ZipLocal(ZipDownloader):
            """Subclass of ZipDownloader that lets me override
            the ``read_chunks`` method so that it reads/writes
            locally with a small file"""

            def __init__(self, source=None, zipfile=None):
                super().__init__(source, zipfile)

            def read_chunks(self):
                """Reads the small zipfile in testdata and returns it in chunks"""
                testzip = testdata.joinpath("ten_voters.zip")
                with open(testzip, "rb") as fp:
                    chunk_size = 512
                    while True:
                        chunk = fp.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk

        # The output will be a zip file in outputs
        zipfile_in_tmp = outputs.joinpath("ten_voters.zip")
        if zipfile_in_tmp.exists():
            zipfile_in_tmp.unlink()

        app = ZipLocal(zipfile=zipfile_in_tmp)
        app.run()

        # Unzip the generated .zip file
        with ZipFile(zipfile_in_tmp) as myzip:
            myzip.extract("ten_voters.txt", path=outputs)

        file1 = outputs.joinpath("ten_voters.txt")
        file2 = testdata.joinpath("ten_voters.txt")

        self.assertTrue(filecmp.cmp(file1, file2))
        zipfile_in_tmp.unlink()
        file1.unlink()

    def test_real_download_first_record(self):
        app = ZipDownloader()
        for chunk in app.read_chunks():
            actual = chunk[:4]
            expected = b'PK\x03\x04'
            self.assertEqual(expected, actual)
            break

    def test_real_download_first_record_bogus(self):
        with self.assertRaises(RuntimeError) as ex:
            app = ZipDownloader(source="https://www.cnn.com/bogus")
            for _ in app.read_chunks():
                break
        output = str(ex.exception)
        self.assertIn("HTTP status 404", output)

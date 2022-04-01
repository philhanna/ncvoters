import os.path
from unittest import TestCase

from voters import ZIP_FILE_NAME
from voters.downloader import Downloader


class TestDownloader(TestCase):

    def test_init(self):
        app = Downloader()
        name, ext = os.path.splitext(ZIP_FILE_NAME)
        self.assertTrue(name.startswith("/tmp"))
        self.assertEqual(ext, ".zip")

    def test_run(self):
        app = Downloader()
        app.run()
        self.assertGreater(app.zipfile_size, 468000000)

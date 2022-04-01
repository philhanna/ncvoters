import os.path
from unittest import TestCase

from voters.downloader import Downloader


class TestDownloader(TestCase):

    def test_init(self):
        app = Downloader()
        name = app.zipfile
        ext = os.path.splitext(name)[1]
        self.assertEqual(ext, ".zip")

    def test_run(self):
        app = Downloader()
        app.run()
        self.assertGreater(app.zipfile_size, 468000000)

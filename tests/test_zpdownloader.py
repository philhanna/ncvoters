import os.path
import unittest
from unittest import TestCase

from voters import ZIP_FILE_NAME, ZipDownloader


class TestDownloader(TestCase):

    def test_init(self):
        app = ZipDownloader()
        name, ext = os.path.splitext(ZIP_FILE_NAME)
        self.assertTrue(name.startswith("/tmp"))
        self.assertEqual(ext, ".zip")

    @unittest.skipIf(os.path.exists(ZIP_FILE_NAME), 'No need to redo the download')
    def test_run(self):
        app = ZipDownloader()
        app.run()
        self.assertGreater(app.zipfile_size, 468000000)

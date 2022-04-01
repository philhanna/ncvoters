import os
import tempfile
from http import HTTPStatus

import requests


class Downloader:
    """ Downloads the latest zip file from the NC state elections website """
    DATA_SOURCE_URL = "https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvoter_Statewide.zip"
    ZIP_FILE_NAME = "ncvoter_Statewide.zip"
    CHUNK_SIZE = 2 ** 24

    def __init__(self, source=DATA_SOURCE_URL):
        """ Creates a Downloader instance """
        self.source = source
        self.tmp = tempfile.gettempdir()
        self.zipfile = os.path.join(self.tmp, Downloader.ZIP_FILE_NAME)
        self.zipfile_size = None

    def run(self):
        """ Downloads the zip file """

        # Make an HTTP request for the source zip file
        resp = requests.get(self.source, stream=True)
        if resp.status_code != HTTPStatus.OK:  # Expecting a status code of 200
            errmsg = f"HTTP status {resp.status_code} returned for request to {self.source}"
            raise RuntimeError(errmsg)

        # Read the response and write the zip file a chunk at a time
        with open(self.zipfile, "wb") as fp:
            total_bytes = 0
            for chunk in resp.iter_content(chunk_size=Downloader.CHUNK_SIZE):
                total_bytes += len(chunk)
                fp.write(chunk)
        self.zipfile_size = total_bytes

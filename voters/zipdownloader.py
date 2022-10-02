import logging
import os
from http import HTTPStatus

import requests

from voters import ZIP_FILE_NAME, DATA_SOURCE_URL, ZIP_CHUNK_SIZE


class ZipDownloader:
    """Downloads the latest zip file from the NC state elections website"""

    def __init__(self, source=None, zipfile=None):
        """ Creates a ZipDownloader instance """
        if source is None:
            source = DATA_SOURCE_URL
        self.source = source

        if zipfile is None:
            zipfile = ZIP_FILE_NAME
        self.zipfile = zipfile

        self.zipfile_size = None

    def run(self):
        """Downloads the zip file if it doesn't already exist"""
        if os.path.exists(self.zipfile):
            logging.info(f"Using existing zip file {self.zipfile}")
            return
        logging.info(f"start, source={self.source}")

        # Read the response and write the zip file a chunk at a time
        with open(self.zipfile, "wb") as fp:
            total_bytes = 0
            for chunk in self.read_chunks():
                total_bytes += len(chunk)
                logging.info(f"{total_bytes=:,}")
                fp.write(chunk)

        # Set the resulting size
        self.zipfile_size = total_bytes

        logging.info(f"end, {total_bytes=:,}")

    def read_chunks(self):
        """A generator that reads chunks from the response content,
         a (zip file)"""

        # Make an HTTP request for the source zip file
        resp = requests.get(self.source, stream=True)
        if resp.status_code != HTTPStatus.OK:  # Expecting a status code of 200
            errmsg = f"HTTP status {resp.status_code} returned for request to {self.source}"
            raise RuntimeError(errmsg)

        # Read chunks from the response content
        for chunk in resp.iter_content(chunk_size=ZIP_CHUNK_SIZE):
            yield chunk

import tempfile
from http import HTTPStatus

import requests

from voters import ZIP_FILE_NAME, DATA_SOURCE_URL, ZIP_CHUNK_SIZE


class ZipDownloader:
    """ Downloads the latest zip file from the NC state elections website """

    def __init__(self, source=DATA_SOURCE_URL):
        """ Creates a ZipDownloader instance """
        self.source = source
        self.tmp = tempfile.gettempdir()
        self.zipfile = ZIP_FILE_NAME
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
            for chunk in resp.iter_content(chunk_size=ZIP_CHUNK_SIZE):
                total_bytes += len(chunk)
                fp.write(chunk)
        self.zipfile_size = total_bytes

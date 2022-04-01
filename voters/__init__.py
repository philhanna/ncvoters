import os.path
import tempfile

DATA_SOURCE_URL = "https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvoter_Statewide.zip"
ZIP_FILE_NAME = os.path.join(tempfile.gettempdir(), "ncvoter_Statewide.zip")
ZIP_CHUNK_SIZE = 2**24

import os.path
import tempfile

__all__ = {
    'Downloader',
    'Extractor',
    'DBCreator',
    'DBLoader',
    'DATA_SOURCE_URL',
    'ZIP_FILE_NAME',
    'TEXT_FILE_NAME',
    'ENCODING',
    'COLUMNS'
}

DATA_SOURCE_URL = "https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvoter_Statewide.zip"
TEXT_FILE_NAME = "ncvoter_Statewide.txt"
DB_FILE_NAME = os.path.join(tempfile.gettempdir(), "ncvoters.db")
ZIP_FILE_NAME = os.path.join(tempfile.gettempdir(), "ncvoter_Statewide.zip")
ZIP_CHUNK_SIZE = 2 ** 24
ENCODING = "iso8859"
COLUMNS = {
    0: "county_id",
    2: "voter_reg_num",
    4: "last_name",
    5: "first_name",
    6: "middle_name",
    7: "name_suffix_lbl",
    8: "status_cd",
    10: "reason_cd",
    12: "res_street_address",
    13: "res_city_desc",
    14: "state_cd",
    15: "zip_code",
    23: "full_phone_number",
    26: "race_code",
    27: "ethnic_code",
    28: "party_cd",
    29: "gender_code",
    30: "birth_year",
    31: "age_at_year_end",
    32: "birth_state",
}

from .downloader import Downloader
from .extractor import Extractor
from .dbcreator import DBCreator
from .dbloader import DBLoader

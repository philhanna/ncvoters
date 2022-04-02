import os.path
import tempfile

DATA_SOURCE_URL = "https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvoter_Statewide.zip"
TEXT_FILE_NAME = "ncvoter_Statewide.txt"
ZIP_FILE_NAME = os.path.join(tempfile.gettempdir(), "ncvoter_Statewide.zip")
ZIP_CHUNK_SIZE = 2**24
ENCODING = "iso8859"
COLUMNS = {
    0 : "county_id",
    2 : "voter_reg_num",
    9 : "last_name",
    10 : "first_name",
    11 : "middle_name",
    12 : "name_suffix_lbl",
    13 : "res_street_address",
    14 : "res_city_desc",
    15 : "state_cd",
    16 : "zip_code",
    24 : "full_phone_number",
    25 : "race_code",
    26 : "ethnic_code",
    27 : "party_cd",
    28 : "gender_code",
    29 : "birth_age",
    30 : "birth_state",
    67 : "birth_year",
}

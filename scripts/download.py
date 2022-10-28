"""
Python script to download selected rows and column from the
voter registration data at the NC Board of Elections website
and create an SQLite database file from it.  The data is
updated every Saturday.

The file at the website is a very large (about 478MB) zip file,
and the CSV file it contains is nearly 4GB, which can make it
hard to manage.  Not all the columns may be of interest, so this
script allows you to select a subset of columns.

The CSV file is tab-delimited.  The layout is described in
https://s3.amazonaws.com/dl.ncsbe.gov/data/layout_ncvoter.txt
which I have summarized below:

/***********************************************************************
* name:     layout_ncvoter.txt
* purpose:  Contains all legally available voter specific information.
*           Personal identifying information (PII) such as birth date
*           and drivers license number are not included. Voter registrations
*           with a voter_status_desc of 'Removed' are omitted whenever the
*           most recent last voted date is greater than 10 years.
*           This is a weekly point-in-time snapshot current per file date
*           and time.
* updated:  02/11/2022
* format:   tab delimited
* instructions:
*            1) extract using a file archiving and compression program
*               (e.g. WinZip)
*            2) can be linked to ncvhis file by ncid
************************************************************************/

------------------------------------------------------------------------
-- File layout (from 02/12/2022)
-- ---------------------------------------------------------------------
name                       data type          description
------------------------------------------------------------------------
0: county_id               int                County identification number
1: county_desc             varchar(15)        County name
2: voter_reg_num           char(12)           Voter registration number (unique to county)
3: ncid                    char(12)           North Carolina identification (NCID) number
4: last_name               varchar(25)        Voter last name
5: first_name              varchar(20)        Voter first name
6: middle_name             varchar(20)        Voter middle name
7: name_suffix_lbl         char(3)            Voter suffix name (JR, III, etc.)
8: status_cd               char(2)            Registration status code
9: voter_status_desc       varchar(25)        Registration status description
10: reason_cd               varchar(2)         Registration status reason code
11: voter_status_reason_desc varchar(60)       Registration status reason description
12: res_street_address      varvarchar(65)     Residential street address
13: res_city_desc           varchar(60)        Residential city name
14: state_cd                varchar(2)         Residential address state code
15: zip_code                char(9)            Residential address zip code
16: mail_addr1              varchar(40)        Mailing address line 1
17: mail_addr2              varchar(40)        Mailing address line 2
18: mail_addr3              varchar(40)        Mailing address line 3
19: mail_addr4              varchar(40)        Mailing address line 4
20: mail_city               varchar(3)0        Mailing address city name
21: mail_state              varchar(2)         Mailing address city code
22: mail_zipcode            char(9)            Mailing address zip code
23: full_phone_number       varchar(12)        Full phone number including area code
24: confidential_ind        char(1)            Confidential indicator (by General Statute
                                               certain data is confidential for this record)
25: registr_dt              char(10)           Registration date
26: race_code               char(3)            Race code
27: ethnic_code             char(3)            Ethnicity code
28: party_cd                char(3)            Registered party code
29: gender_code             char(1)            Gender/sex code
30: birth_year              char(4)            Year of birth
31: age_at_year_end         char(3)            Age at end of the year (was: birth_age - 02/09/2022)
32: birth_state             varchar(2)         Birth state
33: drivers_lic             char(1)            Drivers license (Y/N)
34: precinct_abbrv          varchar(6)         Precinct abbreviation
35: precinct_desc           varchar(60)        Precinct name
36: municipality_abbrv      varchar(6)         Municipality jurisdiction abbreviation
37: municipality_desc       varchar(60)        Municipality jurisdiction name
38: ward_abbrv              varchar(6)         Ward jurisdiction abbreviation
39: ward_desc               varchar(60)        Ward jurisdiction name
40: cong_dist_abbrv         varchar(6)         Congressional district abbreviation
41: super_court_abbrv       varchar(6)         Superior court jurisdiction abbreviation
42: judic_dist_abbrv        varchar(6)         Judicial district abbreviation
43: nc_senate_abbrv         varchar(6)         NC Senate jurisdiction abbreviation
44: nc_house_abbrv          varchar(6)         NC House jurisdiction abbreviation
45: county_commiss_abbrv    varchar(6)         County commisioner jurisdiction abbreviation
46: county_commiss_desc     varchar(60)        County commisioner jurisdiction name
47: township_abbrv          varchar(6)         Township jurisdiction abbreviation
48: township_desc           varchar(60)        Township jurisdiction name
49: school_dist_abbrv       varchar(6)         School district abbreviation
50: school_dist_desc        varchar(60)        School district name
51: fire_dist_abbrv         varchar(6)         Fire district abbreviation
52: fire_dist_desc          varchar(60)        Fir district name
53: water_dist_abbrv        varchar(6)         Water district abbreviation
54: water_dist_desc         varchar(60)        Water district name
55: sewer_dist_abbrv        varchar(6)         Sewer district abbreviation
56: sewer_dist_desc         varchar(60)        Sewer district name
57: sanit_dist_abbrv        varchar(6)         Sanitation district abbreviation
58: sanit_dist_desc         varchar(60)        Sanitation district name
59: rescue_dist_abbrv       varchar(6)         Rescue district abbreviation
60: rescue_dist_desc        varchar(60)        Rescue district name
61: munic_dist_abbrv        varchar(6)         Municpal district abbreviation
62: munic_dist_desc         varchar(60)        Municipal district name
63: dist_1_abbrv            varchar(6)         Presecutorial district abbreviation
64: dist_1_desc             varchar(60)        Presecutorial district name
65: vtd_abbrv               varchar(6)         Voter tabulation district abbreviation
66: vtd_desc                varchar(60)        Voter tabulation district name
------------------------------------------------------------------------------------

See the COLUMNS dictionary below for a list of what I selected as the
columns of interest.  You can change this by adding or deleting lines.
"""

import csv
import io
import logging
import re
import requests
import sqlite3
import sys
import tempfile
from http import HTTPStatus
from pathlib import Path
from zipfile import ZipFile

# Where to find the zip file, and the name for the text file inside it
DATA_SOURCE_URL = "https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvoter_Statewide.zip"
TEXT_FILE_NAME = "ncvoter_Statewide.txt"

# Where to put the zip file and database
TMP = tempfile.gettempdir()
DB_FILE_NAME = Path(TMP).joinpath("ncvoters.db")
ZIP_FILE_NAME = Path(TMP).joinpath("ncvoter_Statewide.zip")

# The text file has a funny encoding.  You have to use this:
ENCODING = "iso8859"

# How big a chunk will we read from the zip file at one time.
# I start at 16 MB; you can make it larger or smaller depending
# on how much memory you have vs. how long it will take to run.
ZIP_CHUNK_SIZE = 2 ** 24

# Start logging.  It takes a little over 2 minutes to run this on my computer,
# so I log progress information on the console.
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s"
                           " %(module)s:%(lineno)d"
                           " %(funcName)s()"
                           " %(message)s",
                    datefmt="%H:%M:%S")
ch = logging.StreamHandler(stream=sys.stdout)
ch.flush()

########################################################################
# Step 1: Download the latest zip file from the NC state elections website
# Skip the download if the file already exists locally
########################################################################

zipfile = ZIP_FILE_NAME
if zipfile.exists():
    logging.info(f"Using existing zip file {zipfile}")
else:
    source = DATA_SOURCE_URL
    logging.info(f"start, source={source}")

    # Make an HTTP request for the source zip file
    resp = requests.get(source, stream=True)
    if resp.status_code != HTTPStatus.OK:  # Expecting a status code of 200
        errmsg = f"HTTP status {resp.status_code} returned for request to {source}"
        raise RuntimeError(errmsg)

    # Read the response and write the zip file a chunk at a time
    with open(zipfile, "wb") as fp:
        total_bytes = 0
        for chunk in resp.iter_content(chunk_size=ZIP_CHUNK_SIZE):
            total_bytes += len(chunk)
            logging.info(f"{total_bytes=:,}")
            fp.write(chunk)

    # Remember the resulting size
    zipfile_size = total_bytes
    logging.info(f"end, {total_bytes=:,}")

########################################################################
# Step 2: Create an empty voter database with just the table definition.
########################################################################

outfile = DB_FILE_NAME

# Delete the output database file if it already exists.
# I always make a copy in my home directory so nothing
# tragic will happen if this step fails for any reason.
if outfile.exists():
    outfile.unlink()

# Build the sql CREATE TABLE statement for the .db file, using the
# column names in the COLUMNS dictionary below.
# COLUMNS is a map of column numbers to column names for the subset
# of columns we want.
#
# You can adjust this by adding or deleting lines.  The columns are
# numbered starting with 0 for county_id to 66 for vtd_desc
# Be sure to put the column name in quote and add a comma at the
# end of the line
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
ncols = len(COLUMNS)

# For the list of columns in COLUMNS, we'll build an SQL statement
# that looks like this:
#
# CREATE TABLE voters(
#     county_id           TEXT,
#     voter_reg_num       TEXT,
#     last_name           TEXT,
#     first_name          TEXT,
#     middle_name         TEXT,
#     name_suffix_lbl     TEXT,
#     status_cd           TEXT,
#     reason_cd           TEXT,
#     res_street_address  TEXT,
#     res_city_desc       TEXT,
#     state_cd            TEXT,
#     zip_code            TEXT,
#     full_phone_number   TEXT,
#     race_code           TEXT,
#     ethnic_code         TEXT,
#     party_cd            TEXT,
#     gender_code         TEXT,
#     birth_year          TEXT,
#     age_at_year_end     TEXT,
#     birth_state         TEXT
# );

# I want to make the SQL look nice by padding the column names
# so that they are all as long as the longest among them
max_name_width = max([len(x) for x in COLUMNS.values()])

name_list = [x for x in COLUMNS.values()]

sql = "CREATE TABLE voters(\n"
for i in range(len(COLUMNS)):
    name = name_list[i]
    padded_name = name.ljust(max_name_width, ' ')

    # Add a comma to all lines but the last
    comma = "," if i < len(COLUMNS)-1 else ""
    buffer = f"    {padded_name}  TEXT{comma}" + "\n"

    sql += buffer
sql += ");"

# Now run the SQL to create the "voters" table
with sqlite3.connect(outfile) as con:
    con.execute(sql)

########################################################################
# Step 3: Load rows into the new database
########################################################################

logging.info(f"start loading voters into the data")

# Create the SQL for the INSERT statement we'll use.  This can't be
# hard-coded because it has to have the right number of "?" symbols
# for the number of columns we're using.
qmarks = "?, " * (len(COLUMNS)-1) + "?"
insert_stmt = f"INSERT INTO voters VALUES({qmarks})"

# Create rows filtered by the list of columns.  The first row,
# which contains the column names, is automatically ignored.
with ZipFile(ZIP_FILE_NAME) as archive:
    with archive.open(TEXT_FILE_NAME, "r") as fp:
        with sqlite3.connect(DB_FILE_NAME) as con:

            # Open a CSV reader over the entry in the zip file
            reader = csv.reader(io.TextIOWrapper(fp, encoding=ENCODING), delimiter='\t')

            # Read and process every row in the CSV file
            for count, row in enumerate(reader):

                # Log a progress message every million records created
                if count % 1000000 == 0:
                    logging.info(f"voters so far = {count:,}")

                # Skip the column header row
                if count == 1:
                    continue

                # Select only certain columns
                outrow = [row[column] for column in COLUMNS.keys()]

                # We'll need to remove spaces inside field values
                regexp = re.compile(r'\s+')

                for i in range(len(outrow)):
                    field = outrow[i]
                    if regexp.search(field):
                        field = regexp.sub(" ", field).strip()
                        outrow[i] = field

                # Insert the new row
                con.execute(insert_stmt, outrow)

            # At end, commit the transaction
            con.commit()

            logging.info(f"end, total voters = {count:,}")
# ncvoters

Creates an SQLite database from publicly available voter registration data in North Carolina

## Contents:
  - [Overview](#overview)
    - [File layout](#file-layout)
    - [Choosing the columns](#choosing-the-columns)
  - [Installation](#installation)
  - [Configuration](#configuration)
    - [Additional tables](#additional-tables)
  - [Running the application](#running-the-application)
  - [Viewing the database](#viewing-the-database)
  - [References](#references)

## Overview
<a id="overview"></a>
Downloads selected columns from the NC voter registration data at the NC Board
of Elections website and create an SQLite database file from it. The data is
updated every Saturday.

The file at the website is a very large (about 478MB) zip file, and the CSV
file it contains is nearly 4GB, which can make it hard to manage.  Not all the
columns may be of interest, so this script allows you to select a subset of
columns.

### File layout
<a id="file-layout"></a>
The file format is described at
https://s3.amazonaws.com/dl.ncsbe.gov/data/layout_ncvoter.txt,
which I summarize below:
```
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
```
### Choosing the columns
<a id="choosing-the-columns"></a>

Here are all the available columns:
```
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
```
See `selected_columns` in the sample configuration YAML file for a list of what
I selected as the columns of interest.  You can change this by adding or
deleting lines.

## Installation
<a id="installation"></a>

### Prerequisites

- Python 3.11 or later
- `pip`

### Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/philhanna/ncvoters.git
   cd ncvoters
   ```

2. **Install the package**

   Installing in editable mode (`-e`) lets you pull future updates with
   `git pull` without reinstalling:

   ```bash
   pip install -e .
   ```

   This registers three commands on your `PATH`:

   | Command | Purpose |
   |---|---|
   | `get-voter-data` | Download the NC voter file and build the SQLite database |
   | `apply-views` | Apply new or changed view definitions to an existing database |
   | `apply-indexes` | Apply new or changed index definitions to an existing database |

3. **Create the configuration directory**

   ```bash
   mkdir -p ~/.config/ncvoters
   ```

4. **Copy the sample configuration file**

   ```bash
   cp sample_config.yaml ~/.config/ncvoters/config.yaml
   ```

   Then edit `~/.config/ncvoters/config.yaml` as described in the
   [Configuration](#configuration) section below.

---

## Configuration
<a id="configuration"></a>
Create a subdirectory named `ncvoters` in your user configuration directory, which is:
   - On Unix/Mac: `$HOME/.config/ncvoters`
   - On Windows: `%USERPROFILE%\AppData\Roaming\ncvoters`
  
Copy `sample_config.yaml` to that directory, renaming it `config.yaml`.  There are two sections:

```yaml
selected_columns:
  - county_id
  - voter_reg_num
  - last_name
    ...
  - age_at_year_end
  - birth_state
```
This is where you specify the subset of the available columns described above that you
want to be included in your local copy of the database.  Note that you need to indent
each line in the list by two spaces (or a tab character)

```yaml
sanitize_columns:
  - last_name
  - first_name
  - middle_name
  - res_street_address
  - res_city_desc
```
The `sanitize_columns` section is where you list the column names that need to be
cleaned up - they may have sets of multiple whitespace characters that need to be
replaced by a single space.

Edit these two sections as you like to specify how to build your database.
If you are not familiar with YAML, a good introductory page is
[YAML tutorial](https://www.cloudbees.com/blog/yaml-tutorial-everything-you-need-get-started).

### Views and indexes

You can define your own SQL views and indexes as individual `.sql` files
stored in subdirectories of your configuration directory:

```
~/.config/ncvoters/
├── config.yaml
├── indexes/
│   ├── names.sql
│   └── addresses.sql
└── views/
    ├── family.sql
    └── friends.sql
```

Each file contains a single SQL statement.

**Views** go in `~/.config/ncvoters/views/`.  Each file should contain a
`CREATE VIEW <name> AS ...` statement:

```sql
CREATE VIEW family AS
    SELECT last_name, first_name, middle_name,
           res_street_address AS address,
           res_city_desc      AS city
    FROM   voters
    WHERE  last_name = 'FINE'  AND first_name = 'LARRY'
    OR     last_name = 'HOWARD'
    ORDER BY 1, 2, 3
```

**Indexes** go in `~/.config/ncvoters/indexes/`.  Each file should contain a
`CREATE INDEX <name> ON <table> (...)` statement:

```sql
CREATE INDEX names ON voters (last_name, first_name, middle_name)
```

Both views and indexes are applied automatically at the end of every full
build.  To apply new or changed definitions to an existing database without
rebuilding, use the incremental commands:

```bash
apply-views
apply-indexes
```

Each command processes files independently — a syntax error in one file does
not prevent the others from being applied — and prints a summary of what was
applied, skipped, or failed.

## Running the application
<a id="running-the-application"></a>

### Building the database

```bash
get-voter-data
```

This will:

1. Download the NC voter zip file to `/tmp/voter_data.zip` (reused on
   subsequent runs unless `--force` is given)
2. Rename any existing database to `voter_data_YYYYMMDD_HHMMSS.db` in the
   same directory
3. Create a fresh `voter_data.db` with the columns listed in `config.yaml`
4. Build indexes from `~/.config/ncvoters/indexes/`
5. Apply views from `~/.config/ncvoters/views/`

The database is written to `~/Desktop/voter_data.db` if `db_dir` is set in
`config.yaml`, otherwise to `/tmp/voter_data.db`.

**Options:**

| Flag | Description |
|---|---|
| `get-voter-data [DBNAME]` | Write to a specific path instead of the configured default |
| `-f`, `--force` | Re-download the zip file even if it already exists |
| `-l N`, `--limit N` | Import only the first N voter records (useful for testing) |
| `-m`, `--metadata` | Also add lookup tables for status, race, ethnicity, county, and reason codes |
| `-q`, `--quiet` | Suppress all progress output |

### Applying views and indexes incrementally

If you add or edit a `.sql` file without wanting to rebuild the entire
database, use the incremental commands:

```bash
apply-views
apply-indexes
```

Both accept an optional `[DBNAME]` argument and a `-q`/`--quiet` flag.
Unchanged definitions are skipped; changed ones are dropped and recreated.
A summary is printed at the end.

## Viewing the database
<a id="viewing-the-database"></a>
I use [DB Browser for SQLite](https://sqlitebrowser.org/) to work with the database.
It provides a very good user interface into the data and the table metadata.
You can also run SQL queries from the UI to select subsets of the database in which
you are interested.

There is also a command-line tool named [sqlite3](https://sqlite.org/cli.html)
that allows you to run queries and export data into CSV, JSON, HTML, and
other formats.

SQLite3 is also supported natively in the standard Python library.

## References
<a id="references"></a>
- [Github repository](https://github.com/philhanna/ncvoters)
- [NC Board of Elections](https://www.ncsbe.gov/)
- [File layout](https://s3.amazonaws.com/dl.ncsbe.gov/data/layout_ncvoter.txt)
- [SQLite home page](https://sqlite.org/index.html)
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- [SQLite system tables](https://www.techonthenet.com/sqlite/sys_tables/index.php)

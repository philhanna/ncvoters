# go-ncvoters
[![Go Report Card](https://goreportcard.com/badge/github.com/philhanna/go-ncvoters)][idGoReportCard]
[![PkgGoDev](https://pkg.go.dev/badge/github.com/philhanna/go-ncvoters)][idPkgGoDev]

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
- Ensure that you have Go installed.  See [https://go.dev/doc/install](https://go.dev/doc/install)
for instructions.

- Go to the Github repository at
[https://github.com/philhanna/go-ncvoters](https://github.com/philhanna/go-ncvoters).
You will see a green button labeled "Code":
Click the down arrow and in the resulting dialog box, click "Download ZIP",
and unzip the resulting file in your home directory.
![Code](https://github.com/philhanna/go-ncvoters/assets/3708685/d12883b8-8335-4c11-9db1-5f85ab8e0462)

## Configuration
<a id="configuration"></a>
Create a subdirectory named `go-ncvoters` in your user configuration directory, which is:
   - On Unix/Mac: `$HOME/.config/go-ncvoters`
   - On Windows: `%USERPROFILE%\AppData\Roaming\go-ncvoters`
  
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

### Additional tables
<a id="additional_tables"></a>

You can also add a section to describe additional tables you want to
have added to the database after its construction.  Create a `tables`
section with a list of entries for each additional table. Specify the SQL
statements that will create your additional tables as follows:

```yaml
tables:
  - |
    CREATE TABLE family AS
        SELECT
            last_name, first_name, middle_name
            res_street_address
            (etc.)
        FROM        voters
        WHERE       first_name = 'LARRY' AND last_name = 'FINE'
        OR          first_name = 'CURLY  AND last_name = 'HOWARD'
        OR          first_name = 'MOE'   AND last_name = 'HOWARD'
        ORDER BY    1, 2, 3
        ;
        
  - |
    CREATE TABLE friends AS
        SELECT
            last_name, first_name, middle_name
            res_street_address
            (etc.)
        FROM        voters
        WHERE       first_name = 'TOM' AND last_name = 'THUMB'
        OR          first_name = 'SNOW  AND last_name = 'WHITE'
        ORDER BY    1, 2, 3
        ;
        
```

Note the pipe character "|" after the hyphen that begins the SQL for your table.
This allows you to continue the SQL onto multiple lines.

## Running the application
<a id="running-the-application"></a>

There is a mainline in `cmd/get_voter_data.go` that will run the download
application.

You can also compile a native executable by running the following command from
the root directory of the project:

```bash
$ go install cmd/create/get_voter_data.go
```

This will create an executable in your path named `get_voter_data`, which you can invoke from a command line like any other program:

```bash
$ get_voter_data -h
usage: get_voter_data [OPTIONS] [DBNAME]

Creates a database of North Carolina voter registrations

positional arguments:
  dbname         Name of database file to be created (default /tmp/voter_data.db)

options:
  -h, --help     Show this help text and exit
  -f, --force    Force the zip file to be downloaded, not reused

```
This takes a little over two minutes on my Linux machine.

I generally run this every Saturday night, since the database is updated on the
website that day. The database is built as `voter_data.db` in the `/tmp`
directory (`%TEMP%`, on Windows).  I typically create a soft link to it in my home
directory and the desktop for quick access.

You need to delete the .zip file from `/tmp` before the next Saturday update,
because the system will reuse the existing ZIP file if it exists.  You can do
these delete and download steps in your [cron](https://en.wikipedia.org/wiki/Cron) table
so that it is all done automatically every Saturday night.

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
- [Github repository](https://github.com/philhanna/go-ncvoters)
- [NC Board of Elections](https://www.ncsbe.gov/)
- [File layout](https://s3.amazonaws.com/dl.ncsbe.gov/data/layout_ncvoter.txt)
- [SQLite home page](https://sqlite.org/index.html)
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- [SQLite system tables](https://www.techonthenet.com/sqlite/sys_tables/index.php)

[idGoReportCard]: https://goreportcard.com/report/github.com/philhanna/go-ncvoters
[idPkgGoDev]: https://pkg.go.dev/github.com/philhanna/go-ncvoters

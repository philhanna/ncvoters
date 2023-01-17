/*
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

***********************************************************************
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
************************************************************************

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

See the columns map below for a list of what I selected as the
columns of interest. You can change this by adding or deleting lines.
*/
package main

import (
	"archive/zip"
	"fmt"
	"log"
	"os"
	"path/filepath"
)

const (
	// Where to find the zip file, and the name for the text file inside it
	dataSourceUrl = "https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvoter_Statewide.zip"
	textFileName  = "ncvoter_Statewide.txt"

	// The text file has a funny encoding.  You have to use this:
	encoding = "iso8859"

	// How big a chunk will we read from the zip file at one time.
	// I start at 16 MB; you can make it larger or smaller depending
	// on how much memory you have vs. how long it will take to run.
	zipChunkSize = 16 * 1024 * 1024
)

func main() {

	// columns is a map of column numbers to column names for the subset
	// of columns we want.
	//
	// You can adjust this by adding or deleting lines. The columns are
	// numbered starting with 0 for county_id to 66 for vtd_desc
	columns := make(map[int]string)

	columns[4] = "last_name"
	columns[5] = "first_name"
	columns[6] = "middle_name"

	// dbFileName := filepath.Join(tmp, "ncvoters.db")

	/*******************************************************************
	 * Step 1: Download the latest zip file from the NC state elections
	 * website. Skip the download if the file already exists locally.
	 *******************************************************************/

	zipFileName := filepath.Join(os.TempDir(), "ncvoter_Statewide.zip")
	if fileExists(zipFileName) {
		// Make sure the zipfile isn't a partial one.
		_, err := assertZipfileIsntPartial(zipFileName)
		if err != nil {
			log.Fatalf("Could not open zip file %v: %s", zipFileName, err)
		}
		fmt.Printf("Using existing zip file %s\n", zipFileName)
	}

}

func assertZipfileIsntPartial(filename string) (*zip.ReadCloser, error) {
	archive, err := zip.OpenReader(filename)
	if err != nil {
		return nil, err
	}
	defer archive.Close()
	return nil, nil

}

func fileExists(filename string) bool {
	info, err := os.Stat(filename)
	if os.IsNotExist(err) {
		return false
	}
	return !info.IsDir()
}

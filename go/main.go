package main

import (
	"log"
	"os"
	"path/filepath"

	commas "github.com/philhanna/commas"
)

type Column struct {
	number int    // column number
	name   string // column name
}

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

var (
	// Path to the database to be created
	dbFileName = filepath.Join(os.TempDir(), "ncvoters.db")

	// selectedColumns is a map of column numbers to column names for the subset
	// of selectedColumns we want.
	//
	// You can adjust this by adding or deleting lines. The selectedColumns are
	// numbered starting with 0 for county_id to 66 for vtd_desc.
	//
	// See ncvoters.md for the list of all selectedColumns available.
	selectedColumns = map[int]string{
		0:  "county_id",
		2:  "voter_reg_num",
		4:  "last_name",
		5:  "first_name",
		6:  "middle_name",
		7:  "name_suffix_lbl",
		8:  "status_cd",
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

	columns = getColumnsAsStruct()
)

func main() {

	var (
		err      error
		filesize int64
		count    int64
	)

	// Step 1: Download the latest zip file
	filesize, err = step1()
	if err != nil {
		log.Fatalf("Step 1 failed: %v", err)
	}
	log.Printf("zip file size is %s bytes", commas.Format(filesize))

	// Step 2: Create an empty voter database with just the table definition.
	err = step2()
	if err != nil {
		log.Fatalf("Step 2 failed: %v", err)
	}
	log.Printf("Created empty database \"%s\"", dbFileName)

	// Step 3: Load rows into the new database
	count, err = step3()
	if err != nil {
		log.Fatalf("Step 3 failed: %v", err)
	}
	log.Printf("end, total voters = %s", commas.Format(count))
}

package main

import (
	"archive/zip"
	"database/sql"
	"encoding/csv"
	"fmt"
	"io"
	"log"

	_ "github.com/mattn/go-sqlite3"
	commas "github.com/philhanna/commas"
)

// Step 3: Load rows into the new database
func step3() (int64, error) {
	log.Println("Started loading voters into the database")

	// Open a connection to the SQL database to be created
	var con *sql.DB
	con, err := sql.Open("sqlite3", "ncvoters.db")
	if err != nil {
		log.Fatal(err)
	}
	err = con.Ping()
	if err != nil {
		log.Fatal(err)
	}
	defer con.Close()

	// Create the SQL for the INSERT statement we'll use.  This can't
	// be hard-coded because it has to have the right number of "?"
	// symbols for the number of columns we're using.
	qmarks := getQMarks(len(columns))
	insertStmt := fmt.Sprintf("INSERT INTO voters VALUES(%s)", qmarks)
	log.Printf("DEBUG: %s", insertStmt)

	// Open the zip file for reading
	r, err := zip.OpenReader(zipFileName)
	if err != nil {
		log.Fatal(err)
	}
	defer r.Close()
	log.Printf("Opened \"%s\" for reading", zipFileName)

	// Open a reader over the zipped text file (there is only one)
	// textFileName  = "ncvoter_Statewide.txt"
	f := r.File[0]
	if f.Name != textFileName {
		log.Fatalf("Unknown file name in zip: %s", f.Name)
	}
	log.Printf("Opened compressed file \"%s\" for reading", textFileName)

	// Create rows filtered by the list of columns.  The first row,
	// which contains the column names, is automatically ignored.
	fp, err := f.Open()
	if err != nil {
		log.Fatal()
	}
	csv := csv.NewReader(fp)
	csv.Comma = '\t'

	var count int64

	for {
		row, err := csv.Read()
		if err == io.EOF {
			break
		}
		count++

		// Skip the column headers row
		if count == 1 {
			continue
		}

		// Log a progress message every million records created
		if count%1000000 == 0 {
			log.Printf("voters so far = %s", commas.Format(count))
		}

		// Select only certain columns
		outrow := []string{}
		for cnumber, _ := range columns {
			outrow = append(outrow, row[cnumber])
		}

	}

	// Done
	return count, nil
}

// getQMarks returns a string of comma-delimited question marks
// of the number requested. This will be used to create the INSERT
// statement
func getQMarks(n int) string {
	var qmarks string
	for i := 0; i < n-1; i++ {
		qmarks += "?, "
	}
	qmarks += "?"
	return qmarks
}

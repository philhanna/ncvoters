package create

import (
	"database/sql"
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"math"
	"os"
	"strings"
	"time"

	_ "github.com/mattn/go-sqlite3"
	"github.com/philhanna/commas"
	goncvoters "github.com/philhanna/go-ncvoters"
	"github.com/philhanna/go-ncvoters/util"
)

var (
	selectedIndices []int
	colNames        []string
	progress        *util.Progress
	stime           time.Time
	MAX_ENTRIES     int
)

// CreateDatabase is the mainline for creating a database from the zip file.
func CreateDatabase(zipFileName, entryName, dbFileName string, progressEvery int) error {
	if !quiet() {
		log.Println("Creating database...")
	}
	stime = time.Now()

	// Open the database
	db, err := sql.Open("sqlite3", ":memory:")
	if err != nil {
		log.Fatalf("error opening memory database: %v", err)
	}
	defer db.Close()
	
	// Begin a transaction
	tx, err := db.Begin()
	if err != nil {
		log.Fatalf("error beginning transaction: %v", err)
	}

	// Create a table with selected columns
	query := CreateDDL()
	tx.Exec(query)

	// Create a prepared statement for inserting records into the voters
	// table.
	stmt, _ := CreatePreparedStatement(tx)
	defer stmt.Close()

	// Get the zip file entry for the embedded CSV file
	zipEntry, err := GetZipEntry(zipFileName, entryName)
	if err != nil {
		return err
	}

	// Initialize the progress bar
	progress = util.NewProgress()
	progress.Total = estimatedNumberOfVoters(zipEntry.UncompressedSize64)
	progress.SoFar = 0
	progress.LastPercent = 0

	// Open the CSV file entry
	f, _ := zipEntry.Open()
	defer f.Close()

	// Create a CSV csvReader over the zip file entry
	csvReader := csv.NewReader(f)
	csvReader.Comma = '\t'
	csvReader.FieldsPerRecord = -1 // Allow varying number of fields

	// Get the column names
	colNames, _ = csvReader.Read()
	selectedNames := goncvoters.Configuration.GetColumnNames()
	selectedIndices = GetSelectedIndices(colNames, selectedNames)

	csvChannel := readFromCSV(csvReader)
	selChannel := goncvoters.Map(selectedColumns, csvChannel, 50)
	sanChannel := goncvoters.Map(sanitizeColumns, selChannel, 50)

	// Read from the CSV reader and insert records into the database
	entries := 0
	for input := range sanChannel {
		entries++
		if MAX_ENTRIES > 0 && entries > MAX_ENTRIES {
			break
		}
		values := input.([]any)
		stmt.Exec(values...)
		showProgress()
	}
	fmt.Println()

	// Commit the transaction
	tx.Commit()

	// Now copy to the real database on disk
	if util.FileExists(dbFileName) {
		if !quiet() {
			log.Printf("Deleting existing disk database %s\n", dbFileName)
		}
		os.Remove(dbFileName)
	}

	if !quiet() {
		log.Println("Attaching physical database...")
	}
	sql := fmt.Sprintf(`ATTACH DATABASE %q AS diskdb;`, dbFileName)
	db.Exec(sql)

	if !quiet() {
		log.Println("Copying voters table...")
	}
	sql = `CREATE TABLE diskdb.voters AS SELECT * FROM voters;`
	db.Exec(sql)

	if !quiet() {
		log.Println("Detaching physical database...")
	}
	sql = `DETACH DATABASE diskdb;`
	db.Exec(sql)

	if !quiet() {
		log.Printf("Database created successfully in %v\n", time.Since(stime))
	}

	// Return without error
	return nil
}

// estimatedNumberOfVoters returns the estimated number of voters based
// on a heuristic that employs a ratio of actual number of voters
// divided by compressed file size. This is only used for the progress bar.
// These constants should be updated from time to time.
func estimatedNumberOfVoters(size uint64) int64 {
	const (
		// Values from December 22, 2023 file
		NUMER = 8465201
		DENOM = 3911973311
	)
	ratio := float64(NUMER) / float64(DENOM)
	countf := float64(size) * ratio
	count := int64(math.Round(countf))
	return count
}

// readFromCSV reads one record at a time from the CSV file and sends it
// through an output channel
func readFromCSV(reader *csv.Reader) chan any {
	ch := make(chan any, 10)
	go func() {
		defer close(ch)
		for {
			record, err := reader.Read()
			if err == io.EOF {
				break
			}
			ch <- record
		}
	}()
	return ch
}

// sanitizeColumns removes embedded spaces
func sanitizeColumns(input any) any {
	record := input.([]any)
	output := make([]any, len(selectedIndices))
	for i, idx := range selectedIndices {
		colName := colNames[idx]
		if IsSanitizeCol(colName) {
			output[i] = Sanitize(record[i].(string))
		} else {
			output[i] = record[i]
		}
	}
	return output
}

// selectedColumns returns just the columns the user has selected
func selectedColumns(input any) any {
	record := input.([]string)
	values := make([]any, len(selectedIndices))
	for i, idx := range selectedIndices {
		values[i] = record[idx]
	}
	return values
}

// showProgress prints the progress bar
func showProgress() {
	progress.SoFar++
	percent := int(float64(progress.SoFar) / float64(progress.Total) * 100)
	if percent > progress.LastPercent {
		s := strings.Repeat("*", percent/2)
		for len(s) < 50 {
			s += "."
		}
		if percent > progress.LastPercent {
			countWithCommas := commas.Format(progress.SoFar)
			if !quiet() {
				fmt.Printf("Percent complete: %d%%, [%-s] %s records added in %v\r",
					percent, s, countWithCommas, time.Since(stime))
			}
		}
		progress.LastPercent = percent

	}
}

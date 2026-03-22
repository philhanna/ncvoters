// A Go program that addresses the requirements of optimizing
// performance, memory usage, and disk space while downloading the zip
// file, processing the CSV data, and creating an SQLite database.
// Includes the following optimizations:
//
// 1. **Memory optimization**: Instead of storing the entire CSV file in
// memory, the program reads the CSV file line by line using
// `csv.Reader`.  This approach reduces memory consumption, especially
// for large CSV files, as it only keeps a single record in memory at a
// time.
//
// 2. **Disk space optimization**: The program processes the CSV file
// directly from disk without extracting it from the zip file. This
// eliminates the need to extract and store the entire CSV file on disk,
// resulting in significant disk space savings.
//
// 3. **Performance optimization**: The program utilizes a single
// transaction to insert records into the SQLite database, which
// improves performance by reducing the overhead of committing each
// individual record. Additionally, it uses a prepared statement for the
// insertion, further optimizing the database operations.
package main

import (
	"database/sql"
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"

	_ "github.com/mattn/go-sqlite3"
	goncvoters "github.com/philhanna/go-ncvoters"
	"github.com/philhanna/go-ncvoters/create"
	"github.com/philhanna/go-ncvoters/download"
	"github.com/philhanna/go-ncvoters/util"
	"github.com/philhanna/go-ncvoters/webdata"
)

// ---------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------

const Usage = `usage: get_voter_data [OPTIONS] [DBNAME]

Creates a database of North Carolina voter registrations

positional arguments:
  dbname         Name of database file to be created (default /tmp/voter_data.db)

options:
  -h, --help     Show this help text and exit
  -f, --force    Force the zip file to be downloaded, not reused
  -m, --metadata Add metadata tables
  -q, --quiet    Do not log progress messages

  `

// ---------------------------------------------------------------------
// Variables
// ---------------------------------------------------------------------

var (
	optForce    bool
	optLimit    int
	optMeta     bool
	zipFileName = filepath.Join(os.TempDir(), "voter_data.zip")
	dbFileName  = filepath.Join(os.TempDir(), "voter_data.db")
)

// ---------------------------------------------------------------------
// Functions
// ---------------------------------------------------------------------

// Set the logging flags
func init() {
	log.SetFlags(log.Ldate | log.Ltime | log.Lshortfile)
}

// Parse command line and run the application
func main() {

	// Parse the command line
	flag.BoolVar(&optForce, "force", false, "Deletes the zipfile, if it exists")
	flag.BoolVar(&optForce, "f", false, "Deletes the zipfile, if it exists")
	flag.IntVar(&optLimit, "limit", 0, "Maximum number of entries")
	flag.IntVar(&optLimit, "l", 0, "Maximum number of entries")
	flag.BoolVar(&optMeta, "metadata", false, "Add metadata tables")
	flag.BoolVar(&optMeta, "m", false, "Add metadata tables")
	flag.BoolVar(&goncvoters.OptQuiet, "quiet", false, "Do not log messages")
	flag.BoolVar(&goncvoters.OptQuiet, "q", false, "Do not log messages")

	flag.Usage = func() {
		fmt.Fprint(os.Stderr, Usage)
	}
	flag.Parse()
	if flag.NArg() > 0 {
		dbFileName = flag.Arg(0)
	}

	// Run the database creation
	run()
}

func quiet() bool {
	return goncvoters.OptQuiet
}

// Runs the application
func run() {

	const (
		zipURL        = "https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvoter_Statewide.zip"
		entryName     = "ncvoter_Statewide.txt"
		progressEvery = 100_000 // Log progress every n records
	)

	var err error

	if !quiet() {
		log.Println("Starting voter database creation")
	}

	// Download or reuse the voter zip file
	reuse := false
	if util.FileExists(zipFileName) && util.IsGoodZipFile(zipFileName) {
		reuse = true
	}
	if optForce {
		reuse = false
	}
	if reuse {
		if !quiet() {
			log.Printf("Reusing existing zip file: %v\n", zipFileName)
		}
	} else {
		err = download.DownloadFile(zipURL, zipFileName)
		if err != nil {
			log.Fatal("Failed to download the zip file:", err)
		}
	}

	// Create the database
	create.MAX_ENTRIES = optLimit
	create.CreateDatabase(zipFileName, entryName, dbFileName, progressEvery)

	// Add the metadata tables
	if optMeta {
		addMetadata()
	}

	// Add the additional tables, if specified
	addAdditionalTables()

	if !quiet() {
		log.Println("Process completed successfully!")
	}
}

// addMetadata adds the metadata tables
func addMetadata() {

	// Add the metadata tables
	if !quiet() {
		log.Println("Adding metadata tables...")
	}
	db, err := sql.Open("sqlite3", dbFileName)
	handleError(err)
	defer db.Close()

	// Get the layout
	layoutFile, err := webdata.DownloadLayout(webdata.URL)
	handleError(err)

	layout, err := webdata.ParseLayoutFile(layoutFile)
	handleError(err)

	sqlStmt, err := layout.GetMetadataDDL()
	handleError(err)

	// Write the tables
	tx, err := db.Begin()
	handleError(err)
	_, err = db.Exec(sqlStmt)
	handleError(err)
	err = tx.Commit()
	handleError(err)
}

// addAdditionalTables create any additional tables specified
// in the configuration file
func addAdditionalTables() {
	if len(goncvoters.Configuration.GetTables()) <= 0 {
		return
	}
	if !quiet() {
		log.Println("Adding additional tables")
	}
	db, err := sql.Open("sqlite3", dbFileName)
	handleError(err)
	defer db.Close()
	for _, tableSQL := range goncvoters.Configuration.GetTables() {
		tx, err := db.Begin()
		handleError(err)
		_, err = db.Exec(tableSQL)
		handleError(err)
		err = tx.Commit()
		handleError(err)
	}
}

// handleError provides common error handling for the program
func handleError(err error, msg ...string) {
	if err != nil {
		for _, m := range msg {
			log.Println(m)
		}
		log.Fatal(err)
	}
}

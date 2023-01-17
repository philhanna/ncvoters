// See dv.md for documentation
package main

import (
	"archive/zip"
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

var (
	// columns is a map of column numbers to column names for the subset
	// of columns we want.
	//
	// You can adjust this by adding or deleting lines. The columns are
	// numbered starting with 0 for county_id to 66 for vtd_desc
	columns = make(map[int]string)
)

func main() {
	setColumns()

	// dbFileName := filepath.Join(os.TempDir(), "ncvoters.db")

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
		log.Printf("Using existing zip file %s\n", zipFileName)
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

func setColumns() {
	columns[4] = "last_name"
	columns[5] = "first_name"
	columns[6] = "middle_name"
}

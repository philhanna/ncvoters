// See ncvoters.md for documentation
package main

import (
	"archive/zip"
	"fmt"
	"io"
	"log"
	"net/http"
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
	// numbered starting with 0 for county_id to 66 for vtd_desc.
	//
	// The map is initialized with the setColumns method called from main.
	columns = make(map[int]string)
)

func main() {

	// Populate the column number map
	setColumns()

	// 1. Download the latest zip file
	filesize, err := step1()
	if err != nil {
		log.Fatalf("Step 1 failed: %v", err)
	}
	log.Printf("zip file size is %d bytes", filesize)

}

/* Mainline subroutines */

func step1() (int64, error) {

	/*******************************************************************
	 * Step 1: Download the latest zip file from the NC state elections
	 * website. Skip the download if the file already exists locally.
	 *******************************************************************/

	var nBytes int64

	// If zip file already exists in /tmp, skip the download,
	// just return the size

	zipFileName := filepath.Join(os.TempDir(), "ncvoter_Statewide.zip")
	if fileExists(zipFileName) {

		// Make sure the zipfile isn't a partial one.
		_, err := assertZipfileIsntPartial(zipFileName)
		if err != nil {
			errmsg := fmt.Errorf("Could not open zip file %v: %s", zipFileName, err)
			return 0, errmsg
		}

		// Tell the user that we are using an existing file
		log.Printf("Using existing zip file %s", zipFileName)

		// Get the file size
		file, err := os.Open(zipFileName)
		if err != nil {
			log.Fatal(err)
		}
		fi, err := file.Stat()
		if err != nil {
			log.Fatal(err)
		}
		nBytes = fi.Size()
		return nBytes, nil
	}

	// Otherwize, download the file
	source := dataSourceUrl
	log.Printf("start, source=%s", source)

	// Make an HTTP request for the source zip file
	resp, err := http.Get(source)
	defer resp.Body.Close()
	if err != nil {
		log.Fatalf("err=%s\n", err)
	}

	// Create the output zip file
	fp, err := os.Create(zipFileName)
	defer fp.Close()
	if err != nil {
		log.Fatalf("Could not open %s for output, err=%v\n", zipFileName, err)
	}

	// Read from the HTTP stream and write to the output zip file
	chunk := make([]byte, zipChunkSize)
	var soFar int64
	for i := 0; true; i += 1 {

		// Read zipChunkSize bytes from the HTTP stream.
		// If number of bytes is zero, we are done
		log.Printf("Reading chunk %d, %d bytes so far", i, soFar)
		n, err := io.ReadAtLeast(resp.Body, chunk, zipChunkSize)
		soFar += int64(n)
		if n == 0 {
			break
		}

		// Then write the chunk slice to the output zip file
		_, err = fp.Write(chunk[0:n])
		if err != nil {
			log.Printf("err=%v", err)
			break
		}
	}

	// Done

	return soFar, nil
}

/* Internal functions */

// assertZipfileIsntPartial checks whether the specified zip file
// can be opened correctly.
func assertZipfileIsntPartial(filename string) (*zip.ReadCloser, error) {
	archive, err := zip.OpenReader(filename)
	if err != nil {
		return nil, err
	}
	defer archive.Close()
	return nil, nil

}

// fileExists returns true if the specified file exist
func fileExists(filename string) bool {
	info, err := os.Stat(filename)
	if os.IsNotExist(err) {
		return false
	}
	return !info.IsDir()
}

// setColumns initializes the list of columns
func setColumns() {
	columns[4] = "last_name"
	columns[5] = "first_name"
	columns[6] = "middle_name"
}

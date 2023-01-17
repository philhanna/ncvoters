package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
)

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
	if err != nil {
		log.Fatalf("err=%s\n", err)
	}
	defer resp.Body.Close()

	// Create the output zip file
	fp, err := os.Create(zipFileName)
	if err != nil {
		log.Fatalf("Could not open %s for output, err=%v\n", zipFileName, err)
	}
	defer fp.Close()

	// Read from the HTTP stream and write to the output zip file
	chunk := make([]byte, zipChunkSize)
	nBytes = 0
	for i := 0; true; i += 1 {

		// Read zipChunkSize bytes from the HTTP stream.
		// If number of bytes is zero, we are done
		log.Printf("Reading chunk %d, %d bytes so far", i, nBytes)
		n, err := io.ReadAtLeast(resp.Body, chunk, zipChunkSize)
		nBytes += int64(n)
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

	return nBytes, nil
}

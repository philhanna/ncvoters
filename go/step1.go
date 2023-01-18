package main

import (
	"io"
	"io/fs"
	"log"
	"net/http"
	"os"
	"path/filepath"

	commas "github.com/philhanna/commas"
)

func step1() (int64, error) {

	/*******************************************************************
	 * Step 1: Download the latest zip file from the NC state elections
	 * website. Skip the download if the file already exists locally.
	 *******************************************************************/

	var (
		chunk       []byte
		err         error
		fi          fs.FileInfo
		file        *os.File
		fp          *os.File
		n           int64
		nBytes      int64
		resp        *http.Response
		source      string
		zipFileName string
	)

	// If zip file already exists in /tmp, skip the download,
	// just return the size
	zipFileName = filepath.Join(os.TempDir(), "ncvoter_Statewide.zip")
	if fileExists(zipFileName) {

		// Make sure the zipfile isn't a partial one.
		if _, err = assertZipfileIsntPartial(zipFileName); err != nil {
			log.Println("Existing zip file is corrupted.  Will recreate.")
			goto download
		}

		// Tell the user that we are using an existing file
		log.Printf("Using existing zip file %s", zipFileName)

		// Get the file size
		if file, err = os.Open(zipFileName); err != nil {
			log.Fatal(err)
		}
		if fi, err = file.Stat(); err != nil {
			log.Fatal(err)
		}
		nBytes = fi.Size()
		return nBytes, nil
	}

	// Otherwize, download the file

download:

	source = dataSourceUrl
	log.Printf("start, source=%s", source)

	// Make an HTTP request for the source zip file
	if resp, err = http.Get(source); err != nil {
		log.Fatalf("err=%s\n", err)
	}
	defer resp.Body.Close()

	// Create the output zip file
	if fp, err = os.Create(zipFileName); err != nil {
		log.Fatalf("Could not open %s for output, err=%v\n", zipFileName, err)
	}
	defer fp.Close()

	// Read from the HTTP stream and write to the output zip file
	chunk = make([]byte, zipChunkSize)
	nBytes = 0
	for i := 0; true; i += 1 {

		// Read zipChunkSize bytes from the HTTP stream.
		// If number of bytes is zero, we are done
		log.Printf("Reading chunk %d, %s bytes so far", i, commas.Format64(nBytes))
		shortN, err := io.ReadAtLeast(resp.Body, chunk, zipChunkSize)
		n = int64(shortN)
		nBytes += n
		if n == 0 {
			break
		}

		// Then write the chunk slice to the output zip file
		if _, err = fp.Write(chunk[0:n]); err != nil {
			log.Printf("err=%v", err)
			break
		}
	}
	// Done

	return nBytes, nil
}

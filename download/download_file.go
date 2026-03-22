package download

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/philhanna/go-ncvoters/util"
)

// ---------------------------------------------------------------------
// Functions
// ---------------------------------------------------------------------

// DownloadFile gets the data from the specified url and writes it to a
// file.
func DownloadFile(url, fileName string, blockSize ...int64) error {
	var (
		BLOCK_SIZE = int64(1024 * 1024) // One megabyte
	)
	if len(blockSize) > 0 {
		BLOCK_SIZE = blockSize[0]
	}

	var err error

	// Use an http HEAD request to get the content length
	length, err := GetContentLength(url)
	if err != nil {
		return err
	}
	progress := util.NewProgress()
	progress.Total = length
	progress.SoFar = 0
	progress.LastPercent = 0

	mb := float64(progress.Total) / float64(BLOCK_SIZE)
	if !quiet() {
		log.Printf("Downloading file (%.2fMB)...\n", mb)
	}

	resp, err := http.Get(url)
	_ = err // Would not get here if http HEAD failed above
	defer resp.Body.Close()

	file, err := os.Create(fileName)
	_ = err
	defer file.Close()

	// Create a byte buffer with a size of one megabyte
	buffer := make([]byte, BLOCK_SIZE)

	// Read from the response body and write to the file using the byte buffer
	stime := time.Now()
	for {

		// Read bytes from the response body into the buffer
		n, _ := resp.Body.Read(buffer)
		if n <= 0 {
			break
		}
		progress.SoFar += int64(n)
		percent := int(float64(progress.SoFar) / float64(progress.Total) * 100)
		if percent != progress.LastPercent {
			s := strings.Repeat("*", percent/2)
			for len(s) < 50 {
				s += "."
			}
			if percent > progress.LastPercent {
				mb := float64(progress.SoFar) / float64(BLOCK_SIZE)
				if !quiet() {
					fmt.Printf("Percent complete: %d%%, [%-s] %.2fMB in %v\r",
						percent, s, mb, time.Since(stime))
				}
			}
			progress.LastPercent = percent
		}

		// Write the bytes from the buffer to the file
		file.Write(buffer[:n])

	}

	if !quiet() {
		fmt.Println()
		log.Println("File downloaded successfully!")
	}
	return nil
}

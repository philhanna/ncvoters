package create

import (
	"archive/zip"
	"fmt"
	"log"
)

// GetZipEntry gets a pointer to the embedded CSV file.
func GetZipEntry(zipFileName string, entryName string) (*zip.File, error) {

	// Open the zip file
	zipFile, err := zip.OpenReader(zipFileName)
	if err != nil {
		log.Println(err)
		return nil, err
	}

	// Find the CSV file in the zip archive
	var zipEntry *zip.File
	for _, file := range zipFile.File {
		if file.Name == entryName {
			zipEntry = file
			break
		}
	}

	// If the CSV file is not found, exit with an error
	if zipEntry == nil {
		err = fmt.Errorf("file %q not found in zip archive", entryName)
		log.Println(err)
		return nil, err
	}

	return zipEntry, nil
}

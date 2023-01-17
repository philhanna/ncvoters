package main

import (
	"archive/zip"
	"os"
)

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

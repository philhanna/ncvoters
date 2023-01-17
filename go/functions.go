package main

import (
	"archive/zip"
	"fmt"
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

// buildSQL constructs the SQL needed to create the voters table
func buildSQL() (string, error) {
	var names []string
	for i := 0; i < len(columnNumbers); i++ {
		columnNumber := columnNumbers[i]
		names = append(names, columns[columnNumber])
	}
	fmt.Printf("DEBUG: names=%v\n", names)

	maxNameLength := getMaxNameLength(names)
	fmt.Printf("DEBUG: maxNameLength=%d\n", maxNameLength)
	sql := "CREATE TABLE voters(\n"
	return sql, nil
}

// deleteFile deletes the specified file, if it exists
func deleteFile(filename string) error {
	if fileExists(filename) {
		err := os.Remove(filename)
		return err
	}
	return nil
}

// fileExists returns true if the specified file exist
func fileExists(filename string) bool {
	info, err := os.Stat(filename)
	if os.IsNotExist(err) {
		return false
	}
	return !info.IsDir()
}

// getMaxNameLength returns the length of the longest name in the list
func getMaxNameLength(names []string) int {
	maxLength := 0
	for _, name := range names {
		nameLength := len(name)
		if nameLength > maxLength {
			maxLength = nameLength
		}
	}
	return maxLength
}

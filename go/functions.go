package main

import (
	"archive/zip"
	"os"
	"sort"
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

// getColumnNames returns the column names in column number order
func getColumnNames() []string {
	var names []string
	columnNumbers := getColumnNumbers()
	for i := 0; i < len(selectedColumns); i++ {
		columnNumber := columnNumbers[i]
		name := selectedColumns[columnNumber]
		names = append(names, name)
	}
	return names
}

// getColumnNumbers returns the column numbers in sorted order
func getColumnNumbers() []int {
	var columnNumbers = make([]int, 0, len(selectedColumns))
	for k := range selectedColumns {
		columnNumbers = append(columnNumbers, k)
	}
	sort.Ints(columnNumbers)
	return columnNumbers
}

// getColumnsAsStruct returns a list of Column structs in column number order
func getColumnsAsStruct() []Column {
	var cnStructs = make([]Column, 0, len(selectedColumns))
	cns := getColumnNumbers()
	cnn := getColumnNames()
	for i := 0; i < len(selectedColumns); i++ {
		var cnStruct Column
		cnStruct.number = cns[i]
		cnStruct.name = cnn[i]
		cnStructs = append(cnStructs, cnStruct)
	}
	return cnStructs
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

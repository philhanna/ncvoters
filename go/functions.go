package main

import (
	"os"
	"sort"
)

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

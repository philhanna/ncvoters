package main

import (
	"log"
	"os"

	_ "github.com/mattn/go-sqlite3"
)

// Step 2: Create an empty voter database with just the table definition.
func step2() error {

	// Delete the output database if it already exists
	deleteFile(dbFileName)

	// Create the sqlite3 connection
	con, err := connect(dbFileName)
	if err != nil {
		return err
	}

	// Get the SQL needed to create the voters table
	sqlForTableCreation, _ := buildSQL()

	// Run the SQL to create the voters table
	_, err = con.Exec(sqlForTableCreation)
	if err != nil {
		log.Printf("Could not create tables: %v\n", err)
		return err
	}

	// OK
	return nil
}

// deleteFile deletes the specified file, if it exists
func deleteFile(filename string) error {
	if fileExists(filename) {
		err := os.Remove(filename)
		return err
	}
	return nil
}

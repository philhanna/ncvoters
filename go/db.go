package main

import (
	"database/sql"
	"fmt"
)

// buildSQL constructs the SQL needed to create the voters table
func buildSQL() (string, error) {
	names := getColumnNames()
	maxNameLength := getMaxNameLength(names)

	sql := "CREATE TABLE voters (\n"
	for i, name := range names {
		// Pad each name to the max name length
		for len(name) < maxNameLength {
			name = name + " "
		}

		// Add a comma to all lines but the last
		var comma string
		comma = ","
		if i >= len(selectedColumns)-1 {
			comma = ""
		}

		buffer := fmt.Sprintf("    %s  TEXT%s\n", name, comma)
		sql += buffer
	}
	sql += ");"

	return sql, nil
}

// connect opens a connection to the database
func connect(fileName string) (*sql.DB, error) {

	var db *sql.DB

	// Open the database
	var err error
	db, err = sql.Open("sqlite3", fileName)
	if err != nil {
		return nil, err
	}

	// Open a connection
	pingErr := db.Ping()
	if pingErr != nil {
		return nil, err
	}

	return db, nil
}

package main

import (
	"database/sql"
)

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

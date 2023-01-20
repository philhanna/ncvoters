package main

import (
	"fmt"
	"log"

	_ "github.com/mattn/go-sqlite3"
)

// Step 3: Load rows into the new database
func step3() (int64, error) {
	log.Println("Start loading voters into the database")

	// Create the SQL for the INSERT statement we'll use.  This can't
	// be hard-coded because it has to have the right number of "?"
	// symbols for the number of columns we're using.
	qmarks := getQMarks(len(columns))
	insertStmt := fmt.Sprintf("INSERT INTO voters VALUES(%s)", qmarks)
	log.Printf("DEBUG: insert statement is %s", insertStmt)

	// Create rows filtered by the list of columns.  The first row,
	// which contains the column names, is automatically ignored.

	// Done
	return 0, nil
}

func getQMarks(n int) string {
	var qmarks string
	for i := 0; i < n-1; i++ {
		qmarks += "?, "
	}
	qmarks += "?"
	return qmarks
}

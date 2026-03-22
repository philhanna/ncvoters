package create

import (
	"fmt"
	"strings"
)

// CreateInsertSQL creates an SQL string that can be used for inserting
// records into the voters table.
func CreateInsertSQL(cols []string) string {

	// Create a string with a comma-separated list of column names.
	colNames := strings.Join(cols, ",")

	// Create a string with a comma-separated list of question marks for
	// the "VALUES" part of the SQL.
	qMarks := strings.Repeat("?,", len(cols)-1) + "?"

	// Create the SQL text of the INSERT statement using the two
	// substrings created above.
	sqlString := fmt.Sprintf("INSERT INTO voters (%s) VALUES (%s)", colNames, qMarks)

	return sqlString
}

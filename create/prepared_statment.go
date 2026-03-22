package create

import (
	"database/sql"

	goncvoters "github.com/philhanna/go-ncvoters"
)

// CreatePreparedStatement creates an SQL statement for inserting
// records into the voters table.
func CreatePreparedStatement(tx *sql.Tx) (*sql.Stmt, error) {
	sqlString := CreateInsertSQL(goncvoters.Configuration.GetColumnNames())
	stmt, _ := tx.Prepare(sqlString)
	return stmt, nil
}

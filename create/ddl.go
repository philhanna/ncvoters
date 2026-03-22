package create

import (
	"fmt"
	"strings"

	goncvoters "github.com/philhanna/go-ncvoters"
)

// This function creates a Data Definition Language (DDL) statement for
// creating a table called `voters`.
func CreateDDL() string {
	sb := strings.Builder{}
	sb.WriteString("CREATE TABLE IF NOT EXISTS voters (\n")
	colNames := goncvoters.Configuration.GetColumnNames()
	for i, colName := range colNames {
		comma := ","
		if i == len(colNames)-1 {
			comma = ""
		}
		part := fmt.Sprintf("  %-20s TEXT%s\n", colName, comma)
		sb.WriteString(part)
	}
	sb.WriteString(")\n")
	s := sb.String()

	return s
}

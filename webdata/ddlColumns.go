package webdata

import (
	"fmt"
	"strings"
)

// Creates DDL to create and load data into the columns table
func CreateColumnsDDL(columns []Column) string {
	parts := []string{}
	parts = append(parts, fmt.Sprintf("CREATE TABLE %s (", TABLE_COLUMNS))
	parts = append(parts, "  name           TEXT,")
	parts = append(parts, "  dataType       TEXT,")
	parts = append(parts, "  description    TEXT")
	parts = append(parts, `);`)
	for _, column := range columns {
		stmt := fmt.Sprintf(`INSERT INTO %s VALUES('%s','%s','%s');`,
			TABLE_COLUMNS,
			column.Name,
			column.DataType,
			column.Description,
		)
		parts = append(parts, stmt)
	}
	return strings.Join(parts, "\n") + "\n"
}

package webdata

import (
	"fmt"
	"sort"
	"strings"
)

// Creates DDL to create and load data into the reason_codes table
func CreateReasonCodesDDL(reasonCodes map[string]string) string {
	parts := []string{}
	parts = append(parts, fmt.Sprintf("CREATE TABLE %s (", TABLE_REASON_CODES))
	parts = append(parts, "  reason         TEXT,")
	parts = append(parts, "  description    TEXT")
	parts = append(parts, `);`)

	// Sort the codes in alphabetical order
	keys := []string{}
	for key := range reasonCodes {
		keys = append(keys, key)
	}
	sort.Strings(keys)

	// Write the insert statements
	for _, code := range keys {
		value := reasonCodes[code]
		stmt := fmt.Sprintf(`INSERT INTO %s VALUES('%s','%s');`,
			TABLE_REASON_CODES,
			code,
			value,
		)
		parts = append(parts, stmt)
	}

	// Create the whole string
	return strings.Join(parts, "\n") + "\n"
}

package webdata

import (
	"fmt"
	"sort"
	"strings"
)

// Creates DDL to create and load data into the ethnic_codes table
func CreateEthnicCodesDDL(ethnicCodes map[string]string) string {
	parts := []string{}
	parts = append(parts, fmt.Sprintf("CREATE TABLE %s (", TABLE_ETHNIC_CODES))
	parts = append(parts, "  ethnicity      TEXT,")
	parts = append(parts, "  description    TEXT")
	parts = append(parts, `);`)

	// Sort the codes in alphabetical order
	keys := []string{}
	for key := range ethnicCodes {
		keys = append(keys, key)
	}
	sort.Strings(keys)

	// Write the insert statements
	for _, code := range keys {
		value := ethnicCodes[code]
		stmt := fmt.Sprintf(`INSERT INTO %s VALUES('%s','%s');`,
			TABLE_ETHNIC_CODES,
			code,
			value,
		)
		parts = append(parts, stmt)
	}

	// Create the whole string
	return strings.Join(parts, "\n") + "\n"
}

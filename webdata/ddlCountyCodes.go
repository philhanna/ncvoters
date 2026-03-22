package webdata

import (
	"fmt"
	"sort"
	"strings"
)

// Creates DDL to create and load data into the county table
func CreateCountyCodesDDL(countyCodes map[int]string) string {
	parts := []string{}
	parts = append(parts, fmt.Sprintf("CREATE TABLE %s (", TABLE_COUNTY_CODES))
	parts = append(parts, "  county_id      TEXT,")
	parts = append(parts, "  county         TEXT")
	parts = append(parts, `);`)

	// Sort the codes in alphabetical order
	keys := []int{}
	for key := range countyCodes {
		keys = append(keys, key)
	}
	sort.Ints(keys)

	// Write the insert statements
	for _, code := range keys {
		value := countyCodes[code]
		stmt := fmt.Sprintf(`INSERT INTO %s VALUES(%d,'%s');`,
			TABLE_COUNTY_CODES,
			code,
			value,
		)
		parts = append(parts, stmt)
	}

	// Create the whole string and print it
	return strings.Join(parts, "\n") + "\n"
}

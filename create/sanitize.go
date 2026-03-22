package create

import (
	"regexp"
	"strings"

	goncvoters "github.com/philhanna/go-ncvoters"
)

var re = regexp.MustCompile(`\s+`)

// Sanitize takes a string parameter and returns a modified string by replacing
// multiple consecutive whitespace characters with a single space, and trimming
// leading and trailing whitespace.
func Sanitize(input string) string {
	// Replace multiple consecutive whitespace characters with a single space
	sanitized := re.ReplaceAllString(input, " ")

	// Trim leading and trailing whitespace
	sanitized = strings.TrimSpace(sanitized)

	return sanitized
}

// IsSanitizeCol returns true if the specified column name is found in
// the list of columns that need to be sanitized.
func IsSanitizeCol(colName string) bool {
	colNames := goncvoters.Configuration.GetSanitizeColumns()
	for _, san := range colNames {
		if colName == san {
			return true
		}
	}
	return false
}

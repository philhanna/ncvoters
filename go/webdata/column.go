package webdata

import (
	"regexp"
	"strings"
)

// ---------------------------------------------------------------------
// Type definitions
// ---------------------------------------------------------------------

// A column in the database
type Column struct {
	Name        string `json:"name"`
	DataType    string `json:"type"`
	Description string `json:"desc"`
}

// ---------------------------------------------------------------------
// Constructor
// ---------------------------------------------------------------------

// NewColumn creates a Column filled by splitting a string into three
// fields separated by any amount of whitespace characters.
func NewColumn(line string) Column {
	re := regexp.MustCompile(`\s+`)
	tokens := re.Split(line, 3)
	column := Column{
		Name:        strings.Trim(tokens[0], " "),
		DataType:    strings.Trim(tokens[1], " "),
		Description: strings.Trim(tokens[2], " "),
	}
	return column
}

// Package create has functions to create an SQLite3 database from a
// zipped CSV file.
package create

import goncvoters "github.com/philhanna/go-ncvoters"

func quiet() bool {
	return goncvoters.OptQuiet
}

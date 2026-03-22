// Package download has functions to download the latest voter
// registration file from the NC Board of Elections website
package download

import goncvoters "github.com/philhanna/go-ncvoters"

func quiet() bool {
	return goncvoters.OptQuiet
}

package create

import (
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestGetZipEntry(t *testing.T) {
	zipFileName := filepath.Join("..", "testdata", "stooges.zip")

	// Good entry
	entryName := "stooges.csv"
	fp, err := GetZipEntry(zipFileName, entryName)
	assert.Nil(t, err)
	assert.NotNil(t, fp)
	assert.Equal(t, entryName, fp.FileHeader.Name)

	// Bad entry
	entryName = "bogus"
	_, err = GetZipEntry(zipFileName, entryName)
	assert.NotNil(t, err)
}

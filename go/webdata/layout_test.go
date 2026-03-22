package webdata

import (
	"fmt"
	"path/filepath"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestDownloadLayout(t *testing.T) {
	tests := []struct {
		name    string
		url     string
		bufsiz  int
		want    string
		wantErr bool
	}{
		{"bad URL", "bad URL", 0, "", true},
		{"WFF but not found", "http://www.example.com/bogus", 0, "", true},
		{"good", URL, 1024, "voter_layout.txt", false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			have, err := DownloadLayout(tt.url, tt.bufsiz)
			if tt.wantErr {
				assert.NotNil(t, err)
			} else {
				assert.Nil(t, err)
				assert.True(t, strings.HasSuffix(have, tt.want))
			}
		})
	}
}

func TestNewLayout(t *testing.T) {
	const NCOLUMNS = 67
	path := filepath.Join("..", "testdata", "layout_ncvoter.txt")
	layout, err := ParseLayoutFile(path)
	assert.Nil(t, err)

	assert.Equal(t, NCOLUMNS, len(layout.AllColumns))

	if false {
		for i, column := range layout.AllColumns {
			fmt.Printf("%d: %v\n", i, column)
		}
	}
}

func TestLayout_GetMetadataDDL(t *testing.T) {
	path := filepath.Join("..", "testdata", "layout_ncvoter.txt")
	layout, err := ParseLayoutFile(path)
	assert.Nil(t, err)
	ddl, err := layout.GetMetadataDDL()
	assert.Nil(t, err)
	fmt.Print(ddl)
}

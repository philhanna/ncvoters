package webdata

import (
	"os"
	"path"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestParseColumns(t *testing.T) {
	tests := []struct {
		name     string
		filename string
		columns  []Column
		wantErr  bool
	}{
		{"bogus", "BOGUS", nil, true},
		{"good file", "../testdata/layout_ncvoter.txt", []Column{
			NewColumn("county_id int County identification number"),
			NewColumn("last_name varchar(25) Voter last name"),
			NewColumn("race_code char(3) Race code"),
			NewColumn("vtd_desc varchar(60) Voter tabulation district name"),
		}, false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			layout, err := ParseLayoutFile(tt.filename)
			if tt.wantErr {
				assert.NotNil(t, err)
			} else {
				assert.Nil(t, err)
				// Verify that the test columns were found
				for _, column := range tt.columns {
					assert.Contains(t, layout.AllColumns, column)
				}
			}
		})
	}
}

func TestParseLayoutFile(t *testing.T) {
	const filename = "../testdata/layout_ncvoter.txt"
	layout, err := ParseLayoutFile(filename)
	assert.Nil(t, err)
	actual, err := layout.GetMetadataDDL()
	assert.Nil(t, err)

	outfile := path.Join(os.TempDir(), "metadata.sql")
	os.WriteFile(outfile, []byte(actual), 0644)
}

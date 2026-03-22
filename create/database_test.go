package create

import (
	"math"
	"os"
	"path/filepath"
	"testing"

	_ "github.com/mattn/go-sqlite3"

	"github.com/stretchr/testify/assert"
)

func Test_estimatedNumberOfVoters(t *testing.T) {
	tests := []struct {
		name string
		size uint64
		want int64
	}{
		{"base", 3913556170, 8470544},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			want := tt.want
			have := estimatedNumberOfVoters(tt.size)
			diff := math.Abs(float64(want - have))
			delta := diff / float64(want)
			assert.True(t, delta < 3e-4)
		})
	}
}

func TestCreateDatabase(t *testing.T) {
	tests := []struct {
		name        string // test name
		zipFileName string
		entryName   string
		dbFileName  string
		maxEntries  int
		wantErr     bool
	}{
		{
			"Good test",
			filepath.Join("..", "testdata", "voters.zip"),
			`ncvoter_Statewide.txt`,
			filepath.Join(os.TempDir(), "testdatavoters.db"),
			0,
			false,
		},
		{
			"Good test with max entries = 25",
			filepath.Join("..", "testdata", "voters.zip"),
			`ncvoter_Statewide.txt`,
			filepath.Join(os.TempDir(), "testdatavoters.db"),
			25,
			false,
		},
		{
			"Bad test",
			filepath.Join("..", "testdata", "bogus.zip"),
			`bogus`,
			filepath.Join(os.TempDir(), "bogus.db"),
			0,
			true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			MAX_ENTRIES = tt.maxEntries
			err := CreateDatabase(tt.zipFileName, tt.entryName, tt.dbFileName, 100)
			if tt.wantErr {
				assert.NotNil(t, err)
			} else {
				assert.Nil(t, err)
			}
		})
	}
}

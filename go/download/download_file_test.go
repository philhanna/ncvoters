package download

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestDownloadFile(t *testing.T) {
	tests := []struct {
		name     string
		url      string
		fileName string
		wantErr  bool
	}{
		{
			"Bad URL",
			`bogus`,
			filepath.Join(os.TempDir(), "bogus"),
			true,
		},
		{
			"Good URL",
			`https://www.iana.org/numbers`,
			filepath.Join(os.TempDir(), "numbers.html"),
			false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {

			// Use a small block size so that the "." output will be
			// triggered for test coverage

			err := DownloadFile(tt.url, tt.fileName, 1024)
			if tt.wantErr {
				assert.NotNil(t, err)
				return
			}
		})
	}
}

package util

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestFileExists(t *testing.T) {
	tests := []struct {
		name     string
		filename string
		want     bool
	}{
		{"empty", "", false},
		{"current directory", ".", true},
		{"~/bin", "~/bin", true},
		{"/etc/passwd", "/etc/passwd", true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			want := tt.want
			have := FileExists(tt.filename)
			assert.Equal(t, want, have)
		})
	}
}

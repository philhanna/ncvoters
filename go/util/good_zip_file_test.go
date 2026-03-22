package util

import (
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestIsGoodZipFile(t *testing.T) {
	tests := []struct {
		name     string
		filename string
		want     bool
	}{
		{"partial zip", filepath.Join("..", "testdata", "partial.zip"), false},
		{"not zip", filepath.Join("..", "testdata", "stooges.csv"), false},
		{"voters", filepath.Join("..", "testdata", "voters.zip"), true},
		{"stooges", filepath.Join("..", "testdata", "stooges.zip"), true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			want := tt.want
			have := IsGoodZipFile(tt.filename)
			assert.Equal(t, want, have)
		})
	}
}

func TestFindCentralDirectory(t *testing.T) {
	tests := []struct {
		name     string
		filename string
		want     int64
	}{
		{"partial zip", filepath.Join("..", "testdata", "partial.zip"), -1},
		{"not zip", filepath.Join("..", "testdata", "stooges.csv"), -1},
		{"voters", filepath.Join("..", "testdata", "voters.zip"), 0xf3cb},
		{"stooges", filepath.Join("..", "testdata", "stooges.zip"), 0x0097},
		{"non-existent file", "bogus", -1},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			want := tt.want
			have := FindCentralDirectory(tt.filename)
			assert.Equal(t, want, have)
		})
	}
}

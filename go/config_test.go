package goncvoters

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

func Test_getConfigurationFileName(t *testing.T) {
	tests := []struct {
		name string
		want string
	}{
		{"default", "go-ncvoters/config.yaml"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.True(t, strings.HasSuffix(getConfigurationFileName(), tt.want))
		})
	}
}

func Test_newConfiguration(t *testing.T) {
	tests := []struct {
		name     string
		filename string
		wantErr  bool
	}{
		{"good", getConfigurationFileName(), false},
		{"YAML error", func() string {
			filename := filepath.Join(os.TempDir(), "garbled.yaml")
			fp, err := os.Create(filename)
			assert.Nil(t, err)
			defer fp.Close()
			fp.WriteString("delete me - this is purposefully garbled")
			return filename
		}(), true},
		{"file not found", "BOGUS", true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			config := newConfiguration(tt.filename)
			if tt.wantErr {
				assert.Nil(t, config)
			}
			_ = config
		})
	}
}

func Test_configuration_GetColumnNames(t *testing.T) {
	filename := "sample_config.yaml"
	config := newConfiguration(filename)
	names := config.GetColumnNames()
	assert.Greater(t, len(names), 0)
}

func Test_configuration_GetSanitizedColumns(t *testing.T) {
	filename := "sample_config.yaml"
	config := newConfiguration(filename)
	names := config.GetSanitizeColumns()
	assert.Greater(t, len(names), 0)
}

func Test_configuration_GetTables(t *testing.T) {
	filename := "sample_config.yaml"
	config := newConfiguration(filename)
	names := config.GetTables()
	assert.Equal(t, len(names), 0)
}

package util

import (
	"os"
	"path/filepath"
	"strings"
)

// FileExists returns true if the specified file exists
func FileExists(filename string) bool {
	if strings.HasPrefix(filename, "~/") {
		simpleName := strings.TrimPrefix(filename, "~/")
		dirname, _ := os.UserHomeDir()
		filename = filepath.Join(dirname, simpleName)
	}
	_, err := os.Stat(filename)
	return !os.IsNotExist(err)
}

package goncvoters

import (
	"log"
	"os"
	"path/filepath"

	yaml "gopkg.in/yaml.v2"
)

// ---------------------------------------------------------------------
// Type definitions
// ---------------------------------------------------------------------
type configuration struct {
	SelectedColumns []string `yaml:"selected_columns"`
	SanitizeColumns []string `yaml:"sanitize_columns"`
	Tables          []string `yaml:"tables"`
}

// ---------------------------------------------------------------------
// Constants and variables
// ---------------------------------------------------------------------

const PACKAGE_NAME = "go-ncvoters"

var Configuration *configuration
var OptQuiet bool

func init() {
	Configuration = newConfiguration(getConfigurationFileName())
}

// ---------------------------------------------------------------------
// Constructor
// ---------------------------------------------------------------------

// getConfigurationFileName returns the fully qualified path to the
// config.yaml file.
func getConfigurationFileName() string {
	// Get the configuration file directory
	configDir, _ := os.UserConfigDir()
	filename := filepath.Join(configDir, PACKAGE_NAME, "config.yaml")
	return filename
}

// newConfiguration creates a new selected columns object and loads it
// from a configuration file.  This is an internal methods that is
// called from init().
func newConfiguration(filename string) *configuration {
	p := new(configuration)

	// Read the configuration file
	configData, err := os.ReadFile(filename)
	if err != nil {
		log.Printf("%s file not found", filename)
		return nil
	}
	err = yaml.Unmarshal(configData, p)
	if err != nil {
		log.Println(err)
		return nil
	}
	return p
}

// ---------------------------------------------------------------------
// Methods
// ---------------------------------------------------------------------

// GetColumnNames returns the list of selected column names
func (config *configuration) GetColumnNames() []string {
	return config.SelectedColumns
}

// GetSanitizeColumns returns the list of columns that need to be
// sanitized (i.e., have multiple embedded whitespace characters
// replaced with a single space).
func (config *configuration) GetSanitizeColumns() []string {
	return config.SanitizeColumns
}

// GetTables returns the list of SQL for additional tables
func (config *configuration) GetTables() []string {
	return config.Tables
}

package main

import (
	"testing"
)

func TestColumnOrder(t *testing.T) {
	for i := 1; i < len(columns); i++ {
		column := columns[i]
		prevColumn := columns[i-1]
		if prevColumn.number >= column.number {
			t.Errorf("Columns not in ascending order at %d", i)
		}
	}
}

func TestConstants(t *testing.T) {
	if encoding != "iso8859" {
		t.Errorf("Should have found constant 'encoding'")
	}
}

func TestExistingFile(t *testing.T) {
	filename := "go.mod"
	if !fileExists(filename) {
		t.Errorf("%s file exists but was not detected", filename)
	}
}

func TestMaxNameLength(t *testing.T) {
	names := []string{"Larry", "Curly", "Moe"}
	expected := 5
	actual := getMaxNameLength(names)
	if actual != expected {
		t.Errorf("Expected longest name length=%d, got %d", expected, actual)
	}
}

func TestNonExistingFile(t *testing.T) {
	filename := "bogus"
	if fileExists(filename) {
		t.Errorf("%s file does not exist but was detected", filename)
	}
}

func TestPartialZip(t *testing.T) {
	zipFileName := "testdata/partial.zip"
	_, err := assertZipfileIsntPartial(zipFileName)
	if err == nil {
		t.Errorf("%s should have been detected as partial", zipFileName)
	}
}

func TestGetQMarks(t *testing.T) {
	expected := "?, ?, ?"
	actual := getQMarks(3)
	if actual != expected {
		t.Errorf("Expected %s, got %s", expected, actual)
	}
}

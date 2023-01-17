package main

import (
	"testing"
)

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

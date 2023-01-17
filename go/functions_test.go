package main

import (
	"testing"
)

func TestColumns(t *testing.T) {
	setColumns()
	actual := len(columns)
	expected := 3
	if actual != expected {
		t.Errorf("Number of columns was %d, not %d", actual, expected)
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

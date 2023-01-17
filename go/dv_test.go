package main

import (
	"testing"
)

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

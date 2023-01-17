package main

import "testing"

func TestExistingFile(t *testing.T) {
	filename := "go.mod"
	if !fileExists(filename) {
		t.Errorf("%s file exists but is not detected", filename)
	}
}

func TestNonExistingFile(t *testing.T) {
	filename := "bogus"
	if fileExists(filename) {
		t.Errorf("%s file does not exist but is detected", filename)
	}
}

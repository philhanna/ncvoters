package main

import (
	"testing"
)

func TestStep2GetQMarks(t *testing.T) {
	expected := "?, ?, ?"
	actual := getQMarks(3)
	if actual != expected {
		t.Errorf("Expected %s, got %s", expected, actual)
	}
}

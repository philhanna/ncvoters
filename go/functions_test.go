package main

import (
	"testing"
)

func TestMainColumnOrder(t *testing.T) {
	for i := 1; i < len(columns); i++ {
		column := columns[i]
		prevColumn := columns[i-1]
		if prevColumn.number >= column.number {
			t.Errorf("Columns not in ascending order at %d", i)
		}
	}
}

func TestMainConstants(t *testing.T) {
	if encoding != "iso8859" {
		t.Errorf("Should have found constant 'encoding'")
	}
}

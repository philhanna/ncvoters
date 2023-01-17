package main

import "testing"

func TestGoodConnect(t *testing.T) {
	dbFileName := "testdata/stooges.db"
	db, err := connect(dbFileName)
	defer db.Close()
	if err != nil {
		t.Errorf("Could not connect to %s", dbFileName)
	}
}

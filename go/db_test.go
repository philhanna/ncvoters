package main

import (
	"strings"
	"testing"
)

func TestBuildSQL(t *testing.T) {
	sql, err := buildSQL()
	if err != nil {
		t.Errorf("Could not create SQL, err=%s", err)
	}
	if !strings.HasPrefix(sql, "CREATE") {
		t.Errorf("SQL does not start with CREATE: %s", sql)
	}
}

func TestGoodConnect(t *testing.T) {
	dbFileName := "testdata/stooges.db"
	db, err := connect(dbFileName)
	defer db.Close()
	if err != nil {
		t.Errorf("Could not connect to %s", dbFileName)
	}
}

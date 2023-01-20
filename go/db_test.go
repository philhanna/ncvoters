package main

import (
	"strings"
	"testing"
)

func TestDBBuildSQL(t *testing.T) {
	sql, err := buildSQL()
	if err != nil {
		t.Errorf("Could not create SQL, err=%s", err)
	}
	if !strings.HasPrefix(sql, "CREATE") {
		t.Errorf("SQL does not start with CREATE: %s", sql)
	}
}

func TestDBGoodConnect(t *testing.T) {
	dbFileName := "testdata/stooges.db"
	db, err := connect(dbFileName)
	defer db.Close()
	if err != nil {
		t.Errorf("Could not connect to %s", dbFileName)
	}
}

func TestDBMaxNameLength(t *testing.T) {
	names := []string{"Larry", "Curly", "Moe"}
	expected := 5
	actual := getMaxNameLength(names)
	if actual != expected {
		t.Errorf("Expected longest name length=%d, got %d", expected, actual)
	}
}

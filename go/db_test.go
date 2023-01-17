package main

import (
	"fmt"
	"testing"
)

func TestBuildSQL(t *testing.T) {
	sql, err := buildSQL()
	if err != nil {
		t.Errorf("Could not create SQL, err=%s", err)
	}
	fmt.Println(sql)
}

func TestGoodConnect(t *testing.T) {
	dbFileName := "testdata/stooges.db"
	db, err := connect(dbFileName)
	defer db.Close()
	if err != nil {
		t.Errorf("Could not connect to %s", dbFileName)
	}
}

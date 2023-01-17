package main

import (
	"os"

	_ "github.com/mattn/go-sqlite3"
)

func remove(filename string) error {
	if fileExists(filename) {
		err := os.Remove(filename)
		return err
	}
	return nil
}

func buildSQL() (string, error) {
	sql := "CREATE TABLE voters(\n"

	return sql, nil
}

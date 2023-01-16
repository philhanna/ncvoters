package main

import (
	"fmt"
	"os"
)

const (
	dataSourceUrl = "https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvoter_Statewide.zip"
	textFileName  = "ncvoter_Statewide.txt"
)

func main() {
	tmp := os.TempDir()
	fmt.Println("Temp directory is", tmp)
}

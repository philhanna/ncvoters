package main

const (
	dataSourceUrl = "https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvoter_Statewide.zip"
	textFileName  = "ncvoter_Statewide.txt"
	encoding      = "iso8859"
	zipChunkSize  = 16 * 1024 * 1024
)

func main() {
	// tmp := os.TempDir()
	// dbFileName := filepath.Join(tmp, "ncvoters.db")
	// zipFileName := filepath.Join(tmp, "ncvoter_Statewide.zip")

	columns := make(map[int]string)

	columns[4] = "last_name"
	columns[5] = "first_name"
	columns[6] = "middle_name"

	ncols := len(columns)
	ncols = ncols

	// Step 1: Download the latest zip file

}

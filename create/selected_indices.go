package create

// GetSelectedIndices returns the indices of selected columns from a
// given list of columns.
//
// It takes two parameters:
//   - 'columns' a slice of strings representing all available columns, and
//   - 'selectedCols' - a slice of strings representing the columns that are selected.
//
// The function iterates over the 'columns' slice, checks if each column
// exists in the 'selectedCols' slice, and if found, appends the index
// of the column to the 'selectedIndices' slice.  Finally, it returns
// the 'selectedIndices' slice containing the indices of selected
// columns.
func GetSelectedIndices(columns, selectedCols []string) []int {

	// Create an empty slice to store the selected column indices.
	selectedIndices := make([]int, 0)

	// Iterate over each column in the 'columns' slice.
	for i, col := range columns {

		// Initialize a flag variable to track if the column is found in 'selectedCols'.
		found := false

		// Iterate over each element in 'selectedCols'.
		for _, element := range selectedCols {
			if element == col {
				found = true
				break
			}
		}
		if found {
			selectedIndices = append(selectedIndices, i)
		}
	}

	// Return the slice containing the indices of selected columns.
	return selectedIndices
}

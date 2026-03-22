package util

// ---------------------------------------------------------------------
// Type definitions
// ---------------------------------------------------------------------

// Progress is a custom writer that tracks the progress of a
// long-running operation.
type Progress struct {
	Total       int64
	SoFar       int64
	LastPercent int
}

func NewProgress() *Progress {
	p := new(Progress)
	return p
}

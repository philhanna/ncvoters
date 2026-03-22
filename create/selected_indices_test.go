package create

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestGetSelectedIndices(t *testing.T) {
	all := []string{
		"Larry",
		"Curly",
		"Moe",
	}
	tests := []struct {
		name   string
		subset []string
		want   []int
	}{
		{"Find all", all, []int{0, 1, 2}},
		{"Empty list", []string{}, []int{}},
		{"Just one", []string{"Larry"}, []int{0}},
		{"Just two", []string{"Curly", "Moe"}, []int{1, 2}},
		{"Bogus", []string{"Bogus"}, []int{}},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			want := tt.want
			have := GetSelectedIndices(all, tt.subset)
			assert.Equal(t, want, have)
		})
	}
}

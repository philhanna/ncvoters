package create

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestCreateInsertSQL(t *testing.T) {
	tests := []struct {
		name string
		cols []string
		want string
	}{
		{"Three columns", []string{"name", "rank", "serial_number"},
			"INSERT INTO voters (name,rank,serial_number) VALUES (?,?,?)"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			want := tt.want
			have := CreateInsertSQL(tt.cols)
			assert.Equal(t, want, have)
		})
	}
}

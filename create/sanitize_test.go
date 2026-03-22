package create

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestSanitize(t *testing.T) {
	tests := []struct {
		name  string
		input string
		want  string
	}{
		{"Empty string", "", ""},
		{"All spaces", "        ", ""},
		{"Like       this", "Like       this", "Like this"},
		{"   Like       this ", "Like       this", "Like this"},
		{"Embedded tabs", "Embedded\ttabs", "Embedded tabs"},
		{"Leading and trailing tabs", "\t\tEmbedded\ttabs\t", "Embedded tabs"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			want := tt.want
			have := Sanitize(tt.input)
			assert.Equal(t, want, have)
		})
	}
}

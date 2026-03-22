package goncvoters

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestMap(t *testing.T) {
	square := func(input any) any {
		n := input.(int)
		return n * n
	}

	tests := []struct {
		name     string
		bufsize  int
		limit    int
		expected []any
	}{
		{
			name:     "Unbuffered",
			bufsize:  0,
			limit:    3,
			expected: []any{1, 4, 9},
		},
		{
			name:     "Buffered",
			bufsize:  10,
			limit:    3,
			expected: []any{1, 4, 9},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			inch := make(chan any)
			var ouch chan any
			switch tt.bufsize {
			case 0:
				ouch = Map(square, inch)
			default:
				ouch = Map(square, inch, tt.bufsize)
			}

			go func() {
				for i := 1; i <= tt.limit; i++ {
					inch <- i
				}
				close(inch)
			}()

			for _, expected := range tt.expected {
				actual, ok := <-ouch
				assert.Truef(t, ok, "Not enough values found in channel")
				assert.Equal(t, expected, actual)
			}

			_, ok := <-ouch
			assert.Falsef(t, ok, "Too many values found in channel")

		})
	}
}

func TestReduce(t *testing.T) {
	add := func(x, y any) any {
		return x.(int) + y.(int)
	}

	longest := func(x, y any) any {
		xs := x.(string)
		ys := y.(string)
		switch {
		case len(ys) > len(xs):
			return ys
		default:
			return xs
		}
	}

	tests := []struct {
		name    string
		f       func(x, y any) any
		inputs  []any
		initial any
		want    any
	}{
		{
			name:    "strings",
			f:       longest,
			inputs:  []any{"Larry", "Curly", "Moe"},
			initial: "",
			want:    "Larry",
		},
		{
			name:    "Happy path",
			f:       add,
			inputs:  []any{1, 2, 3},
			initial: 0,
			want:    6,
		},
		{
			name:    "Just one value",
			f:       add,
			inputs:  []any{1},
			initial: 0,
			want:    1,
		},
		{
			name:    "Empty",
			inputs:  []any{},
			initial: 0,
			want:    0,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ch := make(chan any)
			go func() {
				defer close(ch)
				for _, input := range tt.inputs {
					ch <- input
				}
			}()
			have := Reduce(tt.f, ch, tt.initial)
			assert.Equal(t, tt.want, have)
		})
	}
}

package download

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestGetContentLength(t *testing.T) {
	tests := []struct {
		name    string
		url     string
		want    int64
		wantErr bool
	}{
		{"Good", `https://www.ssa.gov/themes/custom/ssa_core/assets/img/us_flag_small.png`, 176, false},
		{"Bogus", `bogus`, 0, true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			have, err := GetContentLength(tt.url)
			if tt.wantErr {
				assert.NotNil(t, err)
				return
			}
			assert.Nil(t, err)
			assert.Equal(t, tt.want, have)
		})
	}
}

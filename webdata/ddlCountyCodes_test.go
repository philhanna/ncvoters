package webdata

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestCreateCountyCodesDDL(t *testing.T) {
	tests := []struct {
		name        string
		countyCodes map[int]string
		want        string
	}{
		{
			"just3",
			map[int]string{
				2: "Blinken",
				1: "Winken",
				3: "Nod",
			}, `
CREATE TABLE county_codes (
	county_id TEXT,
	county TEXT
);
INSERT INTO county_codes VALUES(1,'Winken');
INSERT INTO county_codes VALUES(2,'Blinken');
INSERT INTO county_codes VALUES(3,'Nod');
`,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			want := NormalizeSQL(tt.want)
			have := NormalizeSQL(CreateCountyCodesDDL(tt.countyCodes))
			assert.Equal(t, want, have)
		})
	}
}

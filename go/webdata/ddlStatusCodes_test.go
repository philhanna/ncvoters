package webdata

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestCreateStatusCodesDDL(t *testing.T) {
	tests := []struct {
		name        string
		statusCodes map[string]string
		want        string
	}{
		{
			"just3",
			map[string]string{
				"A": "Active",
				"I": "Inactive",
				"D": "Denied",
			},
			`
CREATE TABLE status_codes (
  status         TEXT,
  description    TEXT
);
INSERT INTO status_codes VALUES('A','Active');
INSERT INTO status_codes VALUES('D','Denied');
INSERT INTO status_codes VALUES('I','Inactive');
`},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			want := NormalizeSQL(tt.want)
			have := NormalizeSQL(CreateStatusCodesDDL(tt.statusCodes))
			assert.Equal(t, want, have)
		})
	}
}

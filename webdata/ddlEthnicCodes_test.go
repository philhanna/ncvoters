package webdata

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestCreateEthnicCodesDDL(t *testing.T) {
	tests := []struct {
		name        string
		ethnicCodes map[string]string
		want        string
	}{
		{
			"all3",
			map[string]string{
				"HL": "HISPANIC or LATINO",
				"NL": "NOT HISPANIC or NOT LATINO",
				"UN": "UNDESIGNATED",
			},
			`
CREATE TABLE ethnic_codes (
  ethnicity      TEXT,
  description    TEXT
);
INSERT INTO ethnic_codes VALUES('HL','HISPANIC or LATINO');
INSERT INTO ethnic_codes VALUES('NL','NOT HISPANIC or NOT LATINO');
INSERT INTO ethnic_codes VALUES('UN','UNDESIGNATED'); 
`,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			want := NormalizeSQL(tt.want)
			have := NormalizeSQL(CreateEthnicCodesDDL(tt.ethnicCodes))
			assert.Equal(t, want, have)
		})
	}
}

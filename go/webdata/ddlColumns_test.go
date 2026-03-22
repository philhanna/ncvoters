package webdata

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestCreateColumnsDDL(t *testing.T) {
	tests := []struct {
		name    string
		columns []Column
		want    string
	}{
		{"just3", []Column{
			{"first_name", "varchar(20)", "Voter first name"},
			{"middle_name", "varchar(20)", "Voter middle name"},
			{"first_name", "varchar(25)", "Voter last name"},
		},
			`
CREATE TABLE columns (
	name           TEXT,
	dataType       TEXT,
	description    TEXT
);
INSERT INTO columns VALUES('first_name','varchar(20)','Voter first name');
INSERT INTO columns VALUES('middle_name','varchar(20)','Voter middle name');
INSERT INTO columns VALUES('first_name','varchar(25)','Voter last name');
`},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			want := NormalizeSQL(tt.want)
			have := NormalizeSQL(CreateColumnsDDL(tt.columns))
			assert.Equal(t, want, have)
		})
	}
}

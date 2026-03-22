package util

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewProgress(t *testing.T) {
	p := NewProgress()
	assert.NotNil(t, p)
}

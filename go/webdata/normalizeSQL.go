package webdata

import (
	"regexp"
	"strings"
)

// Removes leading and trailing whitespace and compress whitespace into single spaces
func NormalizeSQL(s string) string {
	re := regexp.MustCompile(`\s+`)
	out := make([]string, 0)
	lines := strings.Split(s, "\n")
	for _, line := range lines {
		line := strings.Trim(line, " \t")
		if line != "" {
			line = re.ReplaceAllString(line, " ")
			out = append(out, line)
		}
	}
	outs := strings.Join(out, "\n")
	return outs
}

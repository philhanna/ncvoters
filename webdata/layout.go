package webdata

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"path"
	"strings"
)

// ---------------------------------------------------------------------
// Type definitions
// ---------------------------------------------------------------------

type Layout struct {
	AllColumns  []Column
	StatusCodes map[string]string
	RaceCodes   map[string]string
	EthnicCodes map[string]string
	CountyCodes map[int]string
	ReasonCodes map[string]string
}

// ---------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------

const (
	URL                = "https://s3.amazonaws.com/dl.ncsbe.gov/data/layout_ncvoter.txt"
	TABLE_COLUMNS      = "columns"
	TABLE_COUNTY_CODES = "county_codes"
	TABLE_ETHNIC_CODES = "ethnic_codes"
	TABLE_RACE_CODES   = "race_codes"
	TABLE_REASON_CODES = "reason_codes"
	TABLE_STATUS_CODES = "status_codes"
)

var BUFSIZ = 65536

// ---------------------------------------------------------------------
// Constructor
// ---------------------------------------------------------------------

// NewLayout parses the file layouts from an io.Reader
func NewLayout() *Layout {
	layout := new(Layout)
	layout.AllColumns = make([]Column, 0)
	layout.StatusCodes = make(map[string]string)
	layout.RaceCodes = make(map[string]string)
	layout.EthnicCodes = make(map[string]string)
	layout.CountyCodes = make(map[int]string)
	layout.ReasonCodes = make(map[string]string)
	return layout
}

// ---------------------------------------------------------------------
// Functions
// ---------------------------------------------------------------------

// DownloadLayout gets the latest layout data from the voters website
// and writes it to a file in the system temporary directory
func DownloadLayout(url string, bufsiz ...int) (string, error) {

	if len(bufsiz) > 0 {
		BUFSIZ = bufsiz[0]
	}

	// Get the page with the layout data
	resp, err := http.Get(url)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	// Check the HTTP status code
	statusCode := resp.StatusCode
	if statusCode != 200 {
		err := fmt.Errorf("expected HTTP status code 200, got %d", statusCode)
		return "", err
	}

	// Write the page to /tmp/voter_layout.txt
	filename := path.Join(os.TempDir(), "voter_layout.txt")
	fp, _ := os.Create(filename)
	defer fp.Close()

	buffer := make([]byte, BUFSIZ)

readLoop:
	for {
		n, err := resp.Body.Read(buffer)
		switch {
		case err == io.EOF:
			if n > 0 {
				fp.Write(buffer[:n])
			}
			break readLoop
		default:
			fp.Write(buffer[:n])
		}
	}

	// Add [undocumented] reason codes
	fp.WriteString("/* ****************************************************************************\n")
	fp.WriteString("Reason codes\n")
	fp.WriteString("reason_cd  voter_status_reason_desc\n")
	fp.WriteString("*******************************************************************************\n")
	fp.WriteString("A1         UNVERIFIED\n")
	fp.WriteString("A2         CONFIRMATION PENDING\n")
	fp.WriteString("AA         ARMED FORCES\n")
	fp.WriteString("AL         LEGACY DATA\n")
	fp.WriteString("AN         UNVERIFIED NEW\n")
	fp.WriteString("AP         VERIFICATION PENDING\n")
	fp.WriteString("AV         VERIFIED\n")
	fp.WriteString("DI         UNAVAILABLE ESSENTIAL INFORMATION\n")
	fp.WriteString("DN         CONFIRMATION NOT RETURNED\n")
	fp.WriteString("DU         VERIFICATION RETURNED UNDELIVERABLE\n")
	fp.WriteString("IA         ADMINISTRATIVE\n")
	fp.WriteString("IL         LEGACY - CONVERSION\n")
	fp.WriteString("IN         CONFIRMATION NOT RETURNED\n")
	fp.WriteString("IU         CONFIRMATION RETURNED UNDELIVERABLE\n")
	fp.WriteString("R2         DUPLICATE\n")
	fp.WriteString("RA         ADMINISTRATIVE\n")
	fp.WriteString("RC         REMOVED DUE TO SUSTAINED CHALLENGE\n")
	fp.WriteString("RD         DECEASED\n")
	fp.WriteString("RF         FELONY CONVICTION\n")
	fp.WriteString("RH         MOVED WITHIN STATE\n")
	fp.WriteString("RL         MOVED FROM COUNTY\n")
	fp.WriteString("RM         REMOVED AFTER 2 FED GENERAL ELECTIONS IN INACTIVE STATUS\n")
	fp.WriteString("RP         REMOVED UNDER OLD PURGE LAW\n")
	fp.WriteString("RQ         REQUEST FROM VOTER\n")
	fp.WriteString("RR         FELONY SENTENCE COMPLETED\n")
	fp.WriteString("RS         MOVED FROM STATE\n")
	fp.WriteString("RT         TEMPORARY REGISTRANT\n")
	fp.WriteString("SM         MILITARY\n")
	fp.WriteString("SO         OVERSEAS CITIZEN\n")
	fp.WriteString("**************************************************************************** */\n")

	// Done
	return filename, nil

}

// ---------------------------------------------------------------------
// Methods
// ---------------------------------------------------------------------

// GetMetadataDDL returns the metadata DDL extracted from a layout
// object
func (layout *Layout) GetMetadataDDL() (string, error) {
	sb := strings.Builder{}
	sb.WriteString(CreateColumnsDDL(layout.AllColumns))
	sb.WriteString(CreateStatusCodesDDL(layout.StatusCodes))
	sb.WriteString(CreateRaceCodesDDL(layout.RaceCodes))
	sb.WriteString(CreateEthnicCodesDDL(layout.EthnicCodes))
	sb.WriteString(CreateCountyCodesDDL(layout.CountyCodes))
	sb.WriteString(CreateReasonCodesDDL(layout.ReasonCodes))
	ddl := sb.String()
	return ddl, nil
}

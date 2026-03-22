package util

import (
	"archive/zip"
	"encoding/binary"
	"io"
	"os"
)

// IsGoodZipFile returns true of the specified file is a valid zip file
func IsGoodZipFile(filename string) bool {

	// Try to open the Zip file. If it fails, the file is corrupt or
	// non-existent
	reader, err := zip.OpenReader(filename)
	if err != nil {
		return false
	}
	defer reader.Close()

	// See if it has a central directory (should be near the end of the
	// file)
	offset := FindCentralDirectory(filename)
	return offset != -1
}

// FindCentralDirectory returns the offset of the zip file's central directory. If not found, returns -1
func FindCentralDirectory(filename string) int64 {
	const (
		BCD   = 0x504b0102
		ECD   = 0x504b0506
		LIMIT = 100
	)
	var (
		err       error
		offset    int64
		newOffset int64
		dword     int32
	)

	// Open the file
	fp, err := os.Open(filename)
	if err != nil {
		return -1
	}
	defer fp.Close()

	// Look for the end of central directory marker in the last 100
	// bytes or so of the file, then give up.

	offset = -20
	for i := 0; i < LIMIT; i++ {

		// Read a double word at offset from end of file and see if
		// it is the end of central directory marker
		newOffset, err = fp.Seek(offset, io.SeekEnd)
		if err != nil {
			return -1
		}
		binary.Read(fp, binary.BigEndian, &dword)
		if dword == ECD {

			// Move forward 16 bytes and read an offset
			fp.Seek(newOffset+16, io.SeekStart)
			binary.Read(fp, binary.LittleEndian, &dword)

			// Read 4 bytes at this offset to see if it is the start of
			// the central directory
			newOffset, _ := fp.Seek(int64(dword), io.SeekStart)
			binary.Read(fp, binary.BigEndian, &dword)
			if dword == BCD {

				// Found it. Return the offset
				return newOffset
			}
		}

		// Back up one byte and try again
		offset--
	}

	// Give up
	return -1
}

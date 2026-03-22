package download

import "net/http"

// GetContentLength determines how many bytes will be downloaded.
func GetContentLength(url string) (int64, error) {
	response, err := http.Head(url)
	if err != nil {
		return 0, err
	}
	defer response.Body.Close()

	contentLength := response.ContentLength
	return contentLength, nil
}

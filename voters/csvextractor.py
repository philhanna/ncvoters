import csv
import io
import re
import zipfile

from voters import ZIP_FILE_NAME, TEXT_FILE_NAME, ENCODING, COLUMNS


class CSVExtractor:
    """ Extracts specific columns from the CSV file embedded in the zip file
    that was downloaded using the downloader class.  The column numbers
    are contained in the COLUMNS dictionary in __init__.py.  The CSV file
    is tab-delimited.  The layout is described in
    https://s3.amazonaws.com/dl.ncsbe.gov/data/layout_ncvoter.txt
    """

    def __init__(self, filename=TEXT_FILE_NAME, zipfile=ZIP_FILE_NAME):
        self.zip_file_name = zipfile
        self.internal_file_name = filename

    def get_rows(self, limit=None):
        """ A generator that returns rows filtered by the list
        of columns from __init__.py.  The first row, which contains
        the column names, is automatically ignored. """
        regexp = re.compile(r'\s\s+')
        with zipfile.ZipFile(self.zip_file_name) as archive:
            with archive.open(self.internal_file_name, "r") as fp:

                # Open a CSV reader over the entry in the zip file
                reader = csv.reader(io.TextIOWrapper(fp, encoding=ENCODING), delimiter='\t')
                count = 0
                for row in reader:
                    count += 1
                    if count == 1:      # Skip the column header row
                        if limit:
                            limit += 1
                        continue
                    if limit and count > limit:
                        break

                    # Select only certain columns
                    outrow = [row[column] for column in COLUMNS.keys()]
                    for i in range(len(outrow)):
                        if regexp.search(outrow[i]):
                            field = regexp.sub(' ', outrow[i]).rstrip()
                            outrow[i] = field
                    yield outrow


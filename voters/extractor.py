import csv
import io
import zipfile

from voters import ZIP_FILE_NAME, TEXT_FILE_NAME, ENCODING, COLUMNS


class Extractor:
    """ Extracts specific columns from CSV file """

    def __init__(self, filename=TEXT_FILE_NAME, zipfile=ZIP_FILE_NAME):
        self.zip_file_name = zipfile
        self.internal_file_name = filename

    def run(self, limit=0):
        with zipfile.ZipFile(self.zip_file_name) as archive:
            with archive.open(self.internal_file_name, "r") as fp:

                # Open a CSV reader over the entry in the zip file
                reader = csv.reader(io.TextIOWrapper(fp, encoding=ENCODING), delimiter='\t')
                count = 0
                for row in reader:
                    count += 1
                    if limit != 0 and count > limit:
                        break

                    # Select only certain columns
                    outrow = Extractor.select_columns(row)
                    print(outrow)

    @staticmethod
    def select_columns(row, column_list=COLUMNS.keys()):
        outrow = list()
        for colnum in column_list:
            outrow.append(row[colnum])
        return outrow

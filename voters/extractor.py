import csv
import io
import zipfile

from voters import ZIP_FILE_NAME, TEXT_FILE_NAME, ENCODING, COLUMNS


class Extractor:
    """ Extracts specific columns from CSV file """

    def __init__(self, zipfile=ZIP_FILE_NAME):
        self.zip_file_name = zipfile

    def run(self):
        with zipfile.ZipFile(self.zip_file_name) as archive:
            with archive.open(TEXT_FILE_NAME, "r") as fp:

                # Open a CSV reader over the entry in the zip file
                reader = csv.reader(io.TextIOWrapper(fp, encoding=ENCODING), delimiter='\t')
                count = 0
                for row in reader:
                    count += 1
                    if count > 32:
                        break

                    # Select only certain columns
                    outrow = Extractor.select_columns(row)

    @staticmethod
    def select_columns(row, column_list=COLUMNS.keys()):
        outrow = list()
        for colnum in column_list:
            outrow.append(row[colnum])
        return outrow

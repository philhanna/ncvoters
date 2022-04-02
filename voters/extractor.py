import zipfile

from voters import ZIP_FILE_NAME


class Extractor:
    """ Extracts specific columns from CSV file """

    def __init__(self, zipfile=ZIP_FILE_NAME):
        self.zip_file_name = zipfile

    def run(self):
        with zipfile.ZipFile(self.zip_file_name) as archive:
            pass

import os

from voters import DB_FILE_NAME


class DBCreator:
    def __init__(self, filename=DB_FILE_NAME):
        self.filename = filename

    def run(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

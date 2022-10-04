import logging
import sqlite3

from voters import DB_FILE_NAME, COLUMNS, CSVExtractor, TEXT_FILE_NAME, ZIP_FILE_NAME


class DBLoader:
    """Loads rows from ncvoter_Statewide into database"""

    def __init__(self, filename=TEXT_FILE_NAME, zipfile=ZIP_FILE_NAME, db_file_name=DB_FILE_NAME):
        self._filename: str = filename
        self._zipfile: str = zipfile
        self._db_file_name: str = db_file_name

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def zipfile(self) -> str:
        return self._zipfile

    @property
    def db_file_name(self) -> str:
        return self._db_file_name

    def run(self, limit=None):
        """ Loads rows into database """
        logging.info(f"start")

        # Get parameters for CVSExtractor
        filename = self.filename
        zipfile = self.zipfile
        db_file_name = self.db_file_name

        insert_stmt = DBLoader.create_insert_stmt()
        extractor = CSVExtractor(filename=filename, zipfile=zipfile)
        with sqlite3.connect(db_file_name) as con:
            cur = con.cursor()
            for row in extractor.get_rows(limit=limit):
                cur.execute(insert_stmt, row)
            con.commit()
        logging.info(f"end, count={extractor.count:,}")

    @staticmethod
    def create_insert_stmt():
        ncols = len(COLUMNS)
        # I needed to split the string because otherwise
        # PyCharm inspects it as SQL and reports an error
        sql = "INSERT" + " INTO voters VALUES("
        qmarks = "?," * (ncols - 1)
        qmarks += "?"
        sql += qmarks
        sql += ")"
        return sql

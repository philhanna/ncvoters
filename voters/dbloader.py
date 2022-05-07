import sqlite3

from voters import ZIP_FILE_NAME, DB_FILE_NAME, COLUMNS, CSVExtractor


class DBLoader:
    """ Loads rows from ncvoter_Statewide into database """

    @staticmethod
    def create_insert_stmt():
        ncols = len(COLUMNS)
        # I needed to split the string because otherwise
        # PyCharm inspects it as SQL and reports an error
        sql = "INSERT" + " INTO voters VALUES("
        qmarks = "?," * (ncols-1)
        qmarks += "?"
        sql += qmarks
        sql += ")"
        return sql

    @staticmethod
    def run(limit=None):
        """ Loads rows into database """
        insert_stmt = DBLoader.create_insert_stmt()
        extractor = CSVExtractor()
        with sqlite3.connect(DB_FILE_NAME) as con:
            cur = con.cursor()
            for row in extractor.get_rows(limit=limit):
                cur.execute(insert_stmt, row)
            con.commit()

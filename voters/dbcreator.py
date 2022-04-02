import os

from voters import DB_FILE_NAME, COLUMNS


class DBCreator:

    @staticmethod
    def create_schema():
        """ Creates the SQL for the .db file, using the column names
        in the voters.__init__ COLUMNS dict """

        ncols = len(COLUMNS)
        max_name_width = DBCreator.max_width()
        name_list = [x for x in COLUMNS.values()]

        sql = "CREATE TABLE ncvoters(\n"
        for i in range(ncols):
            name = name_list[i]
            padded_name = name.ljust(max_name_width, ' ')
            comma = "," if i < ncols-1 else ""
            buffer = f"    {padded_name}  TEXT{comma}" + "\n"
            sql += buffer
        sql += ");"
        return sql

    @staticmethod
    def max_width():
        """ Returns the length in bytes of the longest column name """
        return max([len(x) for x in COLUMNS.values()])

    def __init__(self, filename=DB_FILE_NAME):
        self.filename = filename

    def run(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

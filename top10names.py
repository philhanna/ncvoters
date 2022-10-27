import csv
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

sql = """
    SELECT      DISTINCT first_name, COUNT(first_name) AS number
    FROM        voters
    WHERE       gender_code = ?
    AND         race_code = ?
    AND         birth_year BETWEEN ? AND ?
    GROUP BY    first_name
    ORDER BY    2 DESC
    LIMIT       10
    ;
"""

dbfile = Path("~/ncvoters.db").expanduser()
uri = f"file:{dbfile}?mode=ro"

outfile = Path(tempfile.gettempdir()).joinpath("top10names.csv")
with open(outfile, "wt") as fp:
    out = csv.writer(fp, lineterminator="\n")
    hrow = ['Decade']
    for race_code in "WB":
        for gender_code in "MF":
            for i in range(10):
                suffix = str(i+1)
                #head = race_code + gender_code + suffix
                hrow.append(suffix)
    out.writerow(hrow)
    with sqlite3.connect(uri) as con:
        con.row_factory = sqlite3.Row
        c = con.cursor()
        this_year = datetime.now().year
        min_age = 17
        for year in range(1900, this_year-min_age, 10):
            print(f"DEBUG: {year=}")
            end_year = year + 9
            outrow = [year]
            for race_code in "WB":
                for gender_code in "MF":
                    c.execute(sql, (gender_code, race_code, year, end_year))
                    for i, row in enumerate(c.fetchall()):
                        popular_name = row['first_name']
                        outrow.append(popular_name)
            out.writerow(outrow)
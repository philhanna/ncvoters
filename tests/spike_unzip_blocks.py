import csv
import io
import unittest
import zipfile

from voters import ZIP_FILE_NAME, ENCODING


class MyTestCase(unittest.TestCase):
    def test_blocked(self):
        expected = 8538323
        with zipfile.ZipFile(ZIP_FILE_NAME) as zipf:
            with zipf.open("ncvoter_Statewide.txt", "r") as f:
                reader = csv.reader(io.TextIOWrapper(f, encoding=ENCODING), delimiter='\t')
                count = 0
                for row in reader:
                    count += 1
                    if count > 10:
                        break
                    print(f"DEBUG: row={row}")
        #self.assertEqual(expected, count)


if __name__ == '__main__':
    unittest.main()

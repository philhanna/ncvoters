# ncvoters
This project allows the user to download selected rows and columns from
North Carolina voter registration data at https://www.ncsbe.gov/results-data/voter-registration-data
See comments at the beginning of
[download-voters.py](https://github.com/philhanna/voters/blob/56e1addab56c6f6f0cc9bb1a081cef52642b3613/scripts/download-voters.py)
for details.

## Table of contents

- [Installation](#installation)
  - [Clone the repository](#clone-the-repository)
  - [Create a virtual environment and install the application](#create-a-virtual-environment-and-install-the-application)
  - [References](#references)

## Installation

### Clone the repository

To install, first clone the Github repository.

**On Windows:**
```bat
cd %USERPROFILE%
git clone git@github.com:philhanna/ncvoters.git
```

**On MacOS/Linux:**
```bash
cd $HOME
git clone git@github.com:philhanna/ncvoters.git
```

### Create a virtual environment and install the application

**On Windows:**
```bat
cd %USERPROFILE%\ncvoters
python -m venv venv
venv\Scripts\activate.bat
python -m pip install -r requirements.txt
REM 
python -m pip install .
```

**On MacOS/Linux:**
```bash
cd $HOME/ncvoters
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install .
```

The `pip install -r requirements.txt` step installs the `requests` package.

The `pip install .` command (**Note the dot!**) actually installs
the application in your Python system.

## References
- [Github repository](https://github.com/philhanna/voters)
- [NC Board of Elections file layout](https://s3.amazonaws.com/dl.ncsbe.gov/data/layout_ncvoter.txt)
- [Python 3 standard library](https://docs.python.org/3/library/index.html)
- [requests](https://requests.readthedocs.io/en/latest/)
- [Pandas API](https://pandas.pydata.org/docs/reference/index.html)
- [SQLite3 home page](https://www.sqlite.org/index.html)
- [SQLite3 Python API](https://docs.python.org/3/library/sqlite3.html)



# -*- coding: utf-8 -*-
"""
# North Carolina Voter Registration Database

This program creates an SQLite database from publicly available voter
registration data in North Carolina.  The information is maintained by
the NC State Board of Elections and is updated every Saturday.

The file format is described at https://s3.amazonaws.com/dl.ncsbe.gov/data/layout_ncvoter.txt
"""

import re
import os
import pandas as pd
import urllib.request

# Public S3 URL published by the NC State Board of Elections.
URL = "https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvoter_Statewide.zip"

# Output csv file that will contain our slimmed-down version of the database
OUTPUT_CSV = "nc_voters.csv"

# We only want a subset of the columns.  Certain columns have additional
# whitespace that needs to be converted to just one space.
sanitized_columns = [
  'last_name',
  'first_name',
  'middle_name',
  'res_street_address',
  'res_city_desc'
]


def main(args):
  # Delete the output CSV if it already exists
  if os.path.exists(args.output):
    os.remove(args.output)
    print(f"Deleted existing file: {args.output}")

  # Create the map of county numbers to county names.
  county_map = build_county_map()
  print(f"Found {len(county_map)} counties")
  print(county_map)

  # Read and process the zip file in chunks (so as not to exhaust memory).
  # There are about 90-95 chunks in the file at the default chunk size.
  chunks = pd.read_csv(args.url,
                       compression='zip',
                       sep='\t',
                       encoding='latin1',
                       chunksize=args.chunksize,
                       low_memory=False)

  total_rows = 0
  for i, chunk in enumerate(chunks):
    print(f"Processing chunk {i+1}")

    # Only active voters
    chunk = chunk[chunk['status_cd'] == 'A'].copy()

    # Clean unnecessary whitespace
    for col in sanitized_columns:
      if col in chunk.columns:
        chunk[col] = chunk[col].apply(sanitize)
    total_rows += len(chunk)

    # Add county names
    # Convert county_id to string to ensure keys match county_map's string keys
    chunk['county_id'] = chunk['county_id'].astype(str)
    # Use .map() to add county names, handling missing keys by assigning NaN
    chunk['county'] = chunk['county_id'].map(county_map)

    # Rename columns
    chunk = chunk.rename(
        columns = {
            "res_street_address": "address",
            "res_city_desc": "city",
            "state_cd": "state",
            "zip_code": "zip",
            "full_phone_number": "phone",
            "race_code": "race",
            "party_cd": "party",
            "gender_code": "gender",
            "birth_year": "birth_year",
            "age_at_year_end": "age",
        }
    )
    # Extract a subset
    chunk = chunk[['last_name', 'first_name', 'middle_name', 'address', 'city',
                   'county', 'state', 'zip', 'phone', 'race', 'party', 'gender',
                   'birth_year', 'age', 'birth_state']]

    # We only want headers on the first chunk (i == 0)
    chunk.to_csv(args.output, mode='a', header=(i == 0), index=False)

  print(f"Done. {total_rows} rows imported into {args.output}.")


def build_county_map():
    """Build a map of county numbers to county names from the layout file."""
    LAYOUT_URL = "https://s3.amazonaws.com/dl.ncsbe.gov/data/layout_ncvoter.txt"
    county_map = {}
    
    # Download the layout from the website
    txt = urllib.request.urlopen(LAYOUT_URL).read()
    
    # Read the layout into a list of lines
    lines = [line.decode('utf-8') for line in txt.splitlines()]
    
    # Finite state machine over the layout lines.
    # The county list runs from ALAMANCE (first) to YANCEY (last).
    
    state = 0
    for line in lines:
        match state:
            case 0:
                if line.startswith("ALAMANCE"):
                    state = 1
                    name, number = line.split()
                    number = int(number)
                    number = f"{number:02d}"
                    county_map[number] = name
            case 1:
                name, number = line.split()
                number = int(number)
                number = f"{number:02d}"
                county_map[number] = name
                if line.startswith("YANCEY"):
                    state = 2
            case 2:
                break

    return county_map


def sanitize(text):
  if pd.isna(text): # Check for NaN or None
    return ''
  text = str(text) # Ensure it's a string
  text = re.sub(r'\s+', ' ', text)
  text = text.strip()
  return text


if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser(
      description="Create a slimmed-down CSV from NC voter registration data.")
  parser.add_argument(
      "-u", "--url",
      default=URL,
      help="URL of the statewide voter registration zip file "
           "(default: %(default)s)")
  parser.add_argument(
      "-o", "--output",
      default=OUTPUT_CSV,
      help="Path of the output CSV file (default: %(default)s)")
  parser.add_argument(
      "-c", "--chunksize",
      type=int,
      default=100000,
      help="Number of records to process per chunk (default: %(default)s)")
  args = parser.parse_args()

  main(args)

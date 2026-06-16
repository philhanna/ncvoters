# ncvoters
"""
# North Carolina Voter Registration Database

This package creates a slimmed-down CSV from publicly available voter
registration data in North Carolina.  The information is maintained by
the NC State Board of Elections and is updated every Saturday.

The file format is described at
https://s3.amazonaws.com/dl.ncsbe.gov/data/layout_ncvoter.txt

The package follows a ports-and-adapters (hexagonal) architecture:

  * ``domain``      -- pure models and transformation services
  * ``ports``       -- Protocol definitions the use case depends on
  * ``application`` -- the ``create_voter_csv`` use case
  * ``adapters``    -- concrete driven adapters (HTTP, pandas, CSV)
  * ``cli``         -- the driving adapter (argparse entry point)
"""

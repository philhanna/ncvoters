""" Creates the latest version of the database """
import logging
import time

from voters import Downloader, DBCreator, DBLoader

# Start logging to the console
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


job_time_start = time.time()

# Download the .zip file
logging.info("Starting download")
stime = time.time()
downloader = Downloader()
downloader.run()
etime = time.time()
elapsed = etime - stime
logging.info(f"Finished download, elapsed time = {elapsed}")

# Create an empty voter database
logging.info("Creating empty database")
stime = time.time()
creator = DBCreator()
creator.run()
etime = time.time()
elapsed = etime - stime
logging.info(f"Database created, elapsed time = {elapsed}")

# Load rows into the new database
logging.info("Loading database from zip file")
stime = time.time()
loader = DBLoader()
loader.run()
etime = time.time()
elapsed = etime - stime
logging.info(f"Done loading database, elapsed time = {elapsed}")

job_time_end = time.time()
elapsed = job_time_end - job_time_start
logging.info(f"Total time elapsed = {elapsed}")

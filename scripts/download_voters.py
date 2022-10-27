#! /usr/bin/python

""" Creates the latest version of the database """
import logging
import sys

from voters import ZipDownloader, DBCreator, DBLoader


def timer(fn):
    """ Decorator to find execution time for a function """
    from time import perf_counter

    def inner(*args, **kwargs):
        start_time = perf_counter()
        result = fn(*args, **kwargs)
        end_time = perf_counter()
        elapsed_time = end_time - start_time
        print(f"{fn.__name__} took {elapsed_time:.8f} seconds to execute")
        return result

    return inner


# Configure logging
def configure_logging():
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(asctime)s %(module)s:%(lineno)d %(funcName)s() %(message)s",
                        datefmt="%H:%M:%S")
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.flush()


# Download the .zip file
def step_1():
    downloader = ZipDownloader()
    downloader.run()


# Create an empty voter database
def step_2():
    creator = DBCreator()
    creator.run()


# Load rows into the new database
def step_3():
    loader = DBLoader()
    loader.run()


@timer
def main():
    configure_logging()
    step_1()
    step_2()
    step_3()


#   ============================================================
#   Mainline
#   ============================================================
if __name__ == '__main__':
    main()

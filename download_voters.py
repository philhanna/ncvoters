""" Creates the latest version of the database """

from voters import ZipDownloader, DBCreator, DBLoader, timer


# Download the .zip file
@timer
def step_1():
    downloader = ZipDownloader()
    downloader.run()


# Create an empty voter database
@timer
def step_2():
    creator = DBCreator()
    creator.run()


# Load rows into the new database
@timer
def step_3():
    loader = DBLoader()
    loader.run()


@timer
def main():
    step_1()
    step_2()
    step_3()


#   ============================================================
#   Mainline
#   ============================================================
if __name__ == '__main__':
    main()

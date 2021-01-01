from os import path, mkdir
import sys
from datetime import datetime
from pathlib import Path

import constants


def createFileStore(fileLocation, dbFilePath):
    # Creating a new datastore
    if not path.isdir(dbFilePath):
        # if the path doesn't exist, either create directory
        # or abort based on user response
        nextStep = input(
            'Directory does not exists. Do you want to create the directory? (Y/n) ')
        if nextStep.lower() == 'n':
            sys.exit("Path does not exists")
        else:
            mkdir(dbFilePath)
    elif fileLocation.is_file():
        # if the file already exists, either open the existing file
        # or abort based on user response
        nextStep = input(
            'File already exists. Do you want to access it? (Y/n) ')
        if nextStep.lower() == 'n':
            sys.exit("File already exists")
        return open(fileLocation, 'a+')

    fileStore = open(fileLocation, 'a+')
    # Writing metadata to file
    fileStore.write(constants.ENCODING)
    fileStore.write(constants.LINE_FEED)
    fileStore.write(constants.FILE_START)
    fileStore.write(constants.LINE_FEED)
    fileStore.write(constants.CREATED.format(datetime.now()))
    fileStore.write(constants.LINE_FEED)
    fileStore.write(constants.FILE_END)
    fileStore.flush()
    return fileStore


def accessFileStore(fileLocation):
    if not fileLocation.is_file():
        sys.exit("Specified file/directory does not exists")
    else:
        return open(fileLocation, 'a+')

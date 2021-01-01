import argparse
from os import remove, rename, path
from linecache import getline
from datetime import datetime
from time import time
from pathlib import Path
from typing import IO

from fileAccess import createFileStore, accessFileStore
import constants


def create(fileStore: IO, fileLocation: Path):
    """Creates new Entry in filestore

    Parameters:
    fileStore (IO): File object of filestore
    fileLocation(Path): Path object of the filestore

    """

    if (fileLocation.stat().st_size > constants.MAX_FILE_SIZE_BYTES):
        print("File size exceeded the quota of {} GB".format(
            constants.MAX_FILE_SIZE_BYTES/(1024 * 1024 * 1024)))  # Converting Bytes to GigaBytes
        return

    # Give instructions to user
    print("\nMaximum key size is {} characters. Maximum Data size is {} KB and format is JSON".format(
        constants.MAX_KEY_SIZE_BYTES, constants.MAX_DATA_SIZE_BYTES/1024))  # Converting Bytes to KiloBytes

    # Getting key and data
    userInput = input(
        "\nType key and data in single line separated by space: ")
    if not userInput:
        print("Operation Cancelled")
        return fileStore
    key, data = userInput.split(maxsplit=1)

    existingData = search(fileStore, key)
    if existingData:
        print("""\nKey already exists with the following data\n{}\n\nIf you want to modify the data, delete key and re-enter it""".format(existingData))
        return fileStore

    writeFlag = True
    # Checking if key and data matches the constraints
    if (len(key) > constants.MAX_KEY_SIZE_BYTES):
        print("\nGiven Key size({}) is longer than {} characters".format(
            len(key), constants.MAX_KEY_SIZE_BYTES))
        writeFlag = False

    if (len(data) > constants.MAX_DATA_SIZE_BYTES):
        print("\nGiven Data size({}KB) is longer than {}KB".format(
            len(data)/1024, constants.MAX_KEY_SIZE_BYTES/1024))  # Converting Bytes to KiloBytes
        writeFlag = False

    if(writeFlag):
        # for i in range(100000):
        fileStore.write(constants.LINE_FEED)
        bytesWritten = fileStore.write("{} {}".format(key, data))
        print("Written {} Bytes successfully".format(bytesWritten))
        fileStore.flush()
    else:
        print("Data creation failed")
    return fileStore


def search(fileStore: IO, key: str):
    """Searched for Entry in filestore

    Parameters:
    fileStore (IO): File object of filestore
    key (str): Key to search

    Returns
    Value if key is found otherwise False
    """

    fileStore.seek(0)
    for line in fileStore:
        currentData = line.strip('\n').split(maxsplit=1)
        if currentData[0] == key:
            return currentData[1].strip()
    return False


def read(fileStore: IO, fileLocation: Path):
    """Prints data for the given key in filestore

    Parameters:
    fileStore (IO): File object of filestore
    fileLocation(Path): Path object of the filestore

    """
    key = input("\nEnter key name to search: ")
    if not key:
        print("Operation Cancelled")
        return fileStore
    data = search(fileStore, key)
    if not data:
        print("Key {} not found.".format(key))
    else:
        print(data)
    return fileStore


def delete(fileStore: IO, fileLocation: Path):
    """Deletes the given key from filestore

    Parameters:
    fileStore (IO): File object of filestore
    fileLocation(Path): Path object of the filestore

    """

    # Get the key to delete
    key = input("\nEnter key name to delete: ")
    if not key:
        print("Operation Cancelled")
        return fileStore
    # Create a temp file and copy the contents of the
    # source file except the key that is to be deleted
    tempFile = open(fileStore.name[0:-4] + "_temp.dts", "w")
    deleted = False
    start = time()
    fileStore.seek(0)

    for line in fileStore.readlines():
        currentKey = line.split(maxsplit=1)[0]
        # print(line)
        if currentKey == key:
            print("Deleted {} successfully".format(key))
            deleted = True
            continue
        tempFile.write(line)
    tempFile.flush()

    if deleted:
        # If the key is found and deleted, the source file
        # will be deleted and temp file will be renamed
        fileStore.close()
        tempFile.close()
        remove(fileStore.name)
        rename(tempFile.name, fileStore.name)
        print(time() - start)
        return open(fileStore.name, 'a+')
    else:
        # If the key is found and deleted, the spurce file
        # will be retained and temp file will be deleted
        print("Key {} not found".format(key))
        tempFile.close()
        remove(tempFile.name)
        print(time() - start)
        return fileStore


def exitProgram(fileStore: IO,  fileLocation: Path):
    """Flushes the data from buffer to file, then closes the file
    and program is exited

    Parameters:
    fileStore (IO): File object of filestore
    fileLocation(Path): Path object of the filestore

    """
    fileStore.flush()
    fileStore.close()
    exit(0)


options = {
    "1": {"name": "CREATE", "function": create, "help": "To create new key with data"},
    "2": {"name": "READ", "function": read, "help": "To find data for the given key"},
    "3": {"name": "DELETE", "function": delete, "help": "To delete given key"},
    "4": {"name": "EXIT", "function":  exitProgram, "help": "Also you can type \'q\' and press Enter"}
}

"""Initializing Argument Parser

optional arguments:
  -h, --help            show this help message and exit
  --new                 Flag to create new Datastore
  -d DBFILEPATH, --dbFilePath DBFILEPATH
                        Path to the existing datastore file
  -n DBFILENAME, --dbFileName DBFILENAME
                        Name of the datastore file

"""
argumentParser = argparse.ArgumentParser(
    description='Perform CRD operation on File-Based Key-Value datastore')
argumentParser.add_argument(
    "--new", action='store_true', help="Flag to create new Datastore")
argumentParser.add_argument("-d", "--dbFilePath", type=str,
                            help="Path to the existing datastore file. Default is current directory", default="./")
argumentParser.add_argument(
    "-n", "--dbFileName", type=str, help="Name of the datastore file", required=True)

# Parsing the arguments
arguments = argumentParser.parse_args()

fileLocation = Path(path.join(arguments.dbFilePath, arguments.dbFileName))
fileStore = None

if arguments.new:
    fileStore = createFileStore(fileLocation, arguments.dbFilePath)
else:
    fileStore = accessFileStore(fileLocation)


def listOptions():
    print("\n Operations Available: ")
    for key, option in options.items():
        print("\t{}. {} - {}".format(key, option["name"], option["help"]))


def getOperation(fileStore, fileLocation):
    while True:
        listOptions()
        option = input(
            "\nType command name (or) Select any option (1 - 4): ").strip().upper()
        optionKeys = options.keys()
        if option == "Q" or option == "4":
            exitProgram(fileStore, fileLocation)
        elif option not in optionKeys:
            for key in optionKeys:
                if options[key]["name"] == option:
                    option = key
                    break
            else:
                print("Option not valid")
                continue
        selectedOption = options[option]
        selectedFuntion = selectedOption["function"]
        fileStore = selectedFuntion(fileStore, fileLocation)

        if (input("\nType q and press Enter to exit or simply press Enter to continue... ").lower() == "q"):
            exitProgram(fileStore, fileLocation)


# driver code
getOperation(fileStore, fileLocation)

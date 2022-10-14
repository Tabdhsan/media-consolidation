from collections import defaultdict
import hashlib
import os
from pprint import pprint
import re
import shutil
from PIL import Image
from PIL.ExifTags import TAGS
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
import tkinter as tk
from tkinter.filedialog import askdirectory
from helpers import timer
from MediaTypes import allImageTypes, allVideoTypes, allMediaTypes


# TODOTAB: Look into splititng/indexing vs regexing
# TODOTAB Check PEP


def os_walk(src, getObj=False):
    res = []
    for root, dirs, files in os.walk(src):
        for name in files:
            # TODOTAB: Arrays are slow look into dict
            file = (
                os.path.join(root, name)
                if not getObj
                else [os.path.join(root, name), name]
            )
            res.append(file)
    return res


@timer
# TODOTAB: Might be faster on python 3.8, currently using 3.7.9
def create_directory_copy(src, dst):
    shutil.copytree(src, dst)


def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


# SRC can be a folder OR a file
def item_to_dst(src, dst):
    try:
        shutil.move(src, dst)
    except Exception as e:
        # Often error if file is duplicate/already exists in dst
        print(e)


# Walks through directory and subdirectory and moves all files to master folder
def move_all_files_to_one_master_folder(src, dst):
    # Creates Destination, Destination/CLEAN, Destination/DUP
    create_folder(dst)

    cleanFolder = f"{dst}/CLEAN"
    create_folder(cleanFolder)

    dupFolder = f"{dst}/DUPS"
    create_folder(dupFolder)

    files = os_walk(src)
    count = 0
    print(f"------About to move all files from {src} to {dst} ------")

    # Hashing is used to check for duplicates
    # TODOTAB: Might be able to speed this up by only checking start of hash?
    hashes = {}
    dupCount = 0

    for file in files:
        fileHash = getFileHash(file)
        hashes[fileHash] = hashes.get(fileHash, 0) + 1

        if hashes[fileHash] == 1:
            item_to_dst(file, cleanFolder)
            count += 1
            if not count % 300:
                print(f"{count} Files Moved")

        else:
            dupCount += 1
            curCount = hashes[fileHash]
            filePieces = file.split(".")
            fileType = filePieces[-1]
            fileName = filePieces[-2].split("\\")[-1]
            newName = f"{dupFolder}/{fileName}_{curCount}.{fileType}"
            item_to_dst(file, newName)

    print(f"{count} UNIQUE moved")
    print(f"{dupCount} DUPS moved")
    print("-------------------------")
    # Returns path to cleanFolder for next function
    return cleanFolder


def getFileHash(file):
    fileHash = hashlib.md5(open(file, "rb").read()).hexdigest()
    return fileHash


def remove_empty_folders(src):
    walk = list(os.walk(src))
    for path, _, _ in walk[::-1]:
        if len(os.listdir(path)) == 0:
            os.rmdir(path)


def get_image_metadata(image):
    image_name = image
    image = Image.open(image_name)
    exifdata = image.getexif()
    cur_image_info = {}
    for tag_id in exifdata:
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
        # Decode bytes
        if isinstance(data, bytes):
            data = data.decode()
        cur_image_info[tag] = data
    return cur_image_info


# Moves files from a source into new MEDIA and MISC folders
def separate_based_on_file_type(src):
    print("-----About to separate files based on type-----")
    media_folder = f"{src}/Media"
    misc_folder = f"{src}/Misc"
    create_folder(media_folder)
    create_folder(misc_folder)

    files = os_walk(src)
    count = 0
    for file in files:
        type = file.split(".")[-1]
        if type in allMediaTypes:
            item_to_dst(file, media_folder)
        else:
            item_to_dst(file, misc_folder)
        count += 1


def get_year_from_str(string, type):
    try:
        date, time = string.split(" ")
    except Exception as e:
        return string
    if type == "image":
        year, month, day = date.split(":")
    else:
        year, month, day = date.split("-")
    return year


def get_video_file_metadata(file):
    parser = createParser(file)
    with parser:
        metadata = extractMetadata(parser)
    allData = metadata.exportDictionary()["Metadata"]
    dateTime = (
        allData["Date-time original"]
        if "Date-time original" in allData
        else allData["Creation date"]
    )
    year = get_year_from_str(dateTime, "video")

    return year


def get_image_file_metadata(file):
    data = get_image_metadata(file)
    if "DateTime" in data and data["DateTime"] != None:
        dateTime = data["DateTime"]
    else:
        dateTime = "NO_DATE"
    return get_year_from_str(dateTime, "image")


def get_media_metadata(file):
    type = file.split(".")[-1]
    if type in allVideoTypes:
        return get_video_file_metadata(file)
    elif type in allImageTypes:
        return get_image_file_metadata(file)
    else:
        print(f"type : {type} not in any set")


def get_all_years(src):
    mediaFiles = os_walk(src)
    media_by_year = defaultdict(list)

    for file in mediaFiles:
        rawYear = get_media_metadata(file)
        year = rawYear if rawYear != "1904" else "NO_DATE"
        media_by_year[year].append(file)

    return media_by_year


def create_folder_for_year_and_move_files(src, yearDictionary):
    for year, imgList in yearDictionary.items():
        folder = f"{src}/{year}"
        create_folder(folder)
        for file in imgList:
            item_to_dst(file, folder)


def get_whatsapp_year(file):
    pieces = file.split("-")  # IMG-20211230-WA00000.jpg
    if pieces[-1].startswith("WA"):
        date = pieces[1]
        year = date[:4]
        month = date[4:6]
        day = date[6:]
        return year


def get_screenshot_year(file):
    # Screenshot_20211203-150147_Settings

    # TODOTAB: Check split vs regex speed
    year = file.split("_")[1][:4]
    return year


def get_basic_file_year(file):
    return file[:4]


def get_no_date_file_name_type(file):
    # WHATSAPP = [IMG/VID]-20211230-WA00000.jpg
    whatsapp_regex = re.compile(r"^\w+-\d+-WA\d+\.\w+$")

    # Screenshot_20211203-150147_Settings
    screenshot_regex = re.compile(r"^Screenshot_*")

    # Basic = 20210905_004903.jpg
    basic_regex = re.compile(r"^\d+_\d+\.\w+$")

    if bool(re.fullmatch(whatsapp_regex, file)):
        return "WHATSAPP"

    if bool(re.match(screenshot_regex, file)):
        return "SCREENSHOT"

    if bool(re.fullmatch(basic_regex, file)):
        return "BASIC"


def get_year_from_file_name(file, fileType):
    if fileType == "WHATSAPP":
        return get_whatsapp_year(file)

    if fileType == "SCREENSHOT":
        return get_screenshot_year(file)

    if fileType == "BASIC":
        return get_basic_file_year(file)


def all_types_cleanup(filePath, fileName, src):
    fileType = get_no_date_file_name_type(fileName)
    year = get_year_from_file_name(fileName, fileType)
    if fileType and year:
        folder = f"{src}/{year}"
        create_folder(folder)
        item_to_dst(filePath, folder)
    else:
        print(f"{fileName} had cleanup issues")


def no_date_folder_cleanup(no_date_folder, clean_folder):
    files = os_walk(no_date_folder, True)
    count = 0
    for filePath, fileName in files:
        count += 1
        all_types_cleanup(filePath, fileName, clean_folder)


def ask_for_directory(directoryType):
    root = tk.Tk()
    root.withdraw()

    master_directory = askdirectory(title=f"Select {directoryType} Folder")

    return master_directory


@timer
def MediaConsolidation(all_media_source, all_media_copy):

    ### Create a copy of the Master Folder ###

    # all_media_source = ask_for_directory("Source")
    # all_media_copy = ask_for_directory("Destination")

    create_directory_copy(all_media_source, all_media_copy)  ##This is only for testing

    ### Organizes files into Media and Misc ###
    flattened_files = "./FlattenedFiles"
    # all_media_copy = ask_for_directory("Destination")
    clean_folder = move_all_files_to_one_master_folder(all_media_copy, flattened_files)
    remove_empty_folders(all_media_copy)
    separate_based_on_file_type(clean_folder)

    ### Organize by year ###
    yearDictionary = get_all_years(clean_folder)
    create_folder_for_year_and_move_files(clean_folder, yearDictionary)
    no_date_folder = f"{clean_folder}/NO_DATE"

    no_date_folder_cleanup(no_date_folder, clean_folder)
    remove_empty_folders(clean_folder)


all_media_source = "./MASTER"
all_media_copy = "./ALL_MEDIA_COPY"
# MediaConsolidation(all_media_source, all_media_copy)

QUICK_TEST = "./QUICK_TEST"
MediaConsolidation(QUICK_TEST, all_media_copy)

print("Done")

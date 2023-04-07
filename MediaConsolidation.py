import os
import re
import shutil
import tkinter as tk
from collections import defaultdict
from datetime import datetime, timezone
from random import randint
from tkinter.filedialog import askdirectory
from xmlrpc.client import boolean

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image
from PIL.ExifTags import TAGS

from constants import all_audio_types, all_image_types, all_media_types, all_video_types

ERROR_FOLDER = "./FlattenedFiles/ERRORS"


############ Get Hash and File Info Functions ############


def get_video_file_metadata(file):
    parser = createParser(file)
    with parser:
        metadata = extractMetadata(parser)
    try:
        all_data = metadata.exportDictionary()["Metadata"]
        date_time = (
            all_data["Date-time original"]
            if "Date-time original" in all_data
            else all_data["Creation date"]
        )
        year = get_year_from_str(date_time, "video")
        # TODO: Potential for error if getModifiedMedia ever returns null
        if year == "1904":
            year = str(getMediaModifiedDate(file))
            year = year.replace("-", ":").split(":")[0]

        return year
    except Exception as error:
        # print("moving file to error folder", file)
        # item_to_dst(file, f"{ERROR_FOLDER}/file")
        return "NO_DATE"


def get_image_file_metadata(file):
    try:
        data = get_image_metadata(file)
        if "DateTime" in data and data["DateTime"] is not None:
            date_time = data["DateTime"]
        elif getMediaModifiedDate(file):
            date_time = str(getMediaModifiedDate(file))
            date_time = date_time.replace("-", ":")
        else:
            date_time = "NO_DATE"
        return get_year_from_str(date_time, "image")
    except:
        # print("moving file to error folder")
        # item_to_dst(file, f"{ERROR_FOLDER}/file")
        # print("WE IN EXCEPT")
        date_time = "NO_DATE"
        return get_year_from_str(date_time, "image")


def get_media_metadata(file):
    file_extension = file.split(".")[-1].lower()
    if file_extension in all_video_types:
        return get_video_file_metadata(file)
    elif file_extension in all_image_types:
        return get_image_file_metadata(file)
    else:
        print(f"file_extension : {file_extension} not in any set")


def get_all_years(src):
    print("------------Trying to get all years--------------")
    media_files = os_walk(src)
    media_by_year = defaultdict(list)

    for file in media_files:
        # print(file)
        raw_year = get_media_metadata(file)
        # Cleanup if it is 2013-09-28T00:42:42-17:00
        if raw_year and raw_year != "NO_DATE" and len(raw_year) > 4:
            raw_year = raw_year[0:4]

        media_by_year[raw_year].append(file)

    return media_by_year


def get_whatsapp_year(file_name):
    pieces = file_name.split("-")  # IMG-20211230-WA00000.jpg
    if pieces[-1].startswith("WA"):
        date = pieces[1]
        year = date[:4]
        month = date[4:6]
        day = date[6:]
        return year


def get_screenshot_year(file_name):
    # Screenshot_20211203-150147_Settings

    match = bool(re.fullmatch(r"Screenshot_*-*_*", file_name))

    year = file_name.split("_")[1][:4] if match else None
    return year


def get_basic_and_tiktok_file_year(file_name):
    return file_name[:4]


def get_no_date_file_name_type(file_name):
    # WHATSAPP = [IMG/VID]-20211230-WA00000.jpg
    whatsapp_regex = re.compile(r"^\w+-\d+-WA\d+\.\w+$")

    # Screenshot_20211203-150147_Settings
    screenshot_regex = re.compile(r"^Screenshot_*")

    # Basic = 20210905_004903.jpg
    basic_regex = re.compile(r"^\d+_\d+\.\w+$")

    # Tiktok = 2021-09-05-004903.jpg
    tiktok_regex = re.compile(r"^\d+-\d+-\d+-\d+\.\w+$")

    if bool(re.fullmatch(whatsapp_regex, file_name)):
        return "WHATSAPP"

    if bool(re.match(screenshot_regex, file_name)):
        return "SCREENSHOT"

    if bool(re.fullmatch(basic_regex, file_name)) or bool(
        re.fullmatch(tiktok_regex, file_name)
    ):
        return "BASIC"


def get_year_from_file_name(file_name, file_type):
    if file_type == "WHATSAPP":
        return get_whatsapp_year(file_name)

    if file_type == "SCREENSHOT":
        return get_screenshot_year(file_name)

    if file_type == "BASIC":
        return get_basic_and_tiktok_file_year(file_name)


def all_types_cleanup(file_path, file_name, src):
    file_type = get_no_date_file_name_type(file_name)
    year = get_year_from_file_name(file_name, file_type)
    if file_type and year:
        folder = f"{src}/{year}"
        create_folder(folder)
        item_to_dst(file_path, folder, "from all type clean")


def no_date_folder_cleanup(no_date_folder, clean_folder):
    files = os_walk(no_date_folder, True)
    count = 0
    for filepath, file_name in files:
        count += 1
        all_types_cleanup(filepath, file_name, clean_folder)


def ask_for_directory(directory_type):
    root = tk.Tk()
    root.withdraw()

    master_directory = askdirectory(title=f"Select {directory_type} Folder")

    return master_directory


@timer
def Media_Consolidation(all_media_source, all_media_copy, flattened_files):

    ### Create a copy of the Master Folder ###

    # all_media_source = ask_for_directory("Source")
    # all_media_copy = ask_for_directory("Destination")
    # TESTING
    try:
        shutil.rmtree(
            "./ALL_MEDIA_COPY", ignore_errors=False, onerror=handleRemoveReadonly
        )
    except Exception as error:
        print("SHUTIL rmTree error ALL_MEDIA_COPY", error)
    try:
        shutil.rmtree(
            "./FlattenedFiles", ignore_errors=False, onerror=handleRemoveReadonly
        )
    except Exception as error:
        print("SHUTIL rmTree error FlattenedFiles", error)

    # TESTING

    print("Creating copy of all files")
    # create_directory_copy(all_media_source, all_media_copy)  ##This is only for testing

    # ### Organizes files into Media and Misc ###

    # clean_folder = move_all_files_to_one_master_folder(all_media_copy, flattened_files)
    # remove_empty_folders(all_media_copy)

    # TODOTAB: Working without copies here, BE CAREFUL
    clean_folder = move_all_files_to_one_master_folder(
        all_media_source, flattened_files
    )
    # remove_empty_folders(all_media_source)

    # separate_based_on_file_type(clean_folder)

    # ### Organize by year ###
    # year_dict = get_all_years(f"{clean_folder}/Media")
    # create_folder_for_year_and_move_files(f"{clean_folder}/Media", year_dict)

    # no_date_folder = f"{clean_folder}/NO_DATE"
    # no_date_folder_cleanup(no_date_folder, clean_folder)
    # remove_empty_folders(clean_folder)

    # ### Cleanup of Misc Folder ###
    misc_folder = f"{clean_folder}/MISC"
    # separate_misc_based_on_file_type(misc_folder)


ALL_MEDIA_SRC = "D:\\ALL_PARENT_MEDIA\\FOLDERS"
ALL_MEDIA_COPY = "D:\\ALL_PARENT_MEDIA\\ALL_MEDIA_COPY"

# Used so flattened_files always has a new number
random = int(datetime.now(timezone.utc).timestamp())
FLATTENED_FILES = f"D:\\ALL_PARENT_MEDIA\\FLATTENED_FILES_{random}"


Media_Consolidation(ALL_MEDIA_SRC, ALL_MEDIA_COPY, FLATTENED_FILES)
create_folder(ALL_MEDIA_SRC)

# TODOTAB: Need function to turn clean/Misc folder -> multiple folders by extensions

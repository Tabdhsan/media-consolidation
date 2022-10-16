from collections import defaultdict
import hashlib
import os
import re
import shutil
import tkinter as tk
from tkinter.filedialog import askdirectory
from xmlrpc.client import boolean
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from PIL import Image
from PIL.ExifTags import TAGS
from helpers import timer, all_image_types, all_video_types, all_media_types

############ OS and SHUTIL Functions ############
# Goes through all files in a folder
def os_walk(src, get_list=False):
    res = []
    for root, dirs, files in os.walk(src):
        for name in files:
            # Either appends the filePath or [filePath, fileName]
            file = (
                os.path.join(root, name)
                if not get_list
                else [os.path.join(root, name), name]
            )
            res.append(file)
    return res


def remove_empty_folders(src):
    walk = list(os.walk(src))
    for path, _, _ in walk[::-1]:
        if len(os.listdir(path)) == 0:
            os.rmdir(path)


@timer
# Optimization: Can be run conditionally based on whether checked in GUI
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


def get_folder_size(folder):
    size = 0
    for path, dirs, files in os.walk(folder):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)

    return size


############ Main Functions ############

# Walks through directory and subdirectory and moves all files to master folder
def move_all_files_to_one_master_folder(src, dst):
    # Creates Destination, Destination/CLEAN, Destination/DUP
    create_folder(dst)

    clean_folder = f"{dst}/CLEAN"
    create_folder(clean_folder)

    dup_folder = f"{dst}/DUPS"
    create_folder(dup_folder)

    files = os_walk(src)
    count = 0
    print(f"------About to move all files from {src} to {dst} ------")

    # Hashing is used to check for duplicates
    hashes = {}
    dup_count = 0

    for file in files:
        file_hash = get_file_hash(file)
        hashes[file_hash] = hashes.get(file_hash, 0) + 1

        if hashes[file_hash] == 1:
            item_to_dst(file, clean_folder)
            count += 1
            if not count % 300:
                print(f"{count} Files Moved")

        else:
            dup_count += 1
            cur_count = hashes[file_hash]
            file_pieces = file.split(".")
            file_type = file_pieces[-1]
            file_name = file_pieces[-2].split("\\")[-1]
            new_name = f"{dup_folder}/{file_name}_{cur_count}.{file_type}"
            item_to_dst(file, new_name)

    print(f"{count} UNIQUE moved")
    print(f"{dup_count} DUPS moved")
    print("-------------------------")
    # Returns path to clean_folder for next function
    return clean_folder


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
        file_extension = file.split(".")[-1]
        if file_extension in all_media_types:
            item_to_dst(file, media_folder)
        else:
            item_to_dst(file, misc_folder)
        count += 1


def create_folder_for_year_and_move_files(src, year_dict):

    for year, img_list in year_dict.items():
        folder = f"{src}/{year}"
        create_folder(folder)
        for file in img_list:
            item_to_dst(file, folder)


############ Get Hash and File Info Functions ############


def get_file_hash(file):
    # file_size = os.path.getsize(file)
    # Optimization: Might be able to use less mem up by only checking parts of a hash?
    file_hash = hashlib.sha1(open(file, "rb").read()).hexdigest()
    return file_hash


def get_image_metadata(image):
    image_name = image
    image = Image.open(image_name)
    exif_data = image.getexif()
    cur_image_info = {}
    for tag_id in exif_data:
        tag = TAGS.get(tag_id, tag_id)
        data = exif_data.get(tag_id)
        # Decode bytes
        if isinstance(data, bytes):
            data = data.decode()
        cur_image_info[tag] = data
    return cur_image_info


def get_year_from_str(string, media_type):
    try:
        date, time = string.split(" ")
    except Exception as e:
        return string
    if media_type == "image":
        year, month, day = date.split(":")
    else:
        year, month, day = date.split("-")
    return year


def get_video_file_metadata(file):
    parser = createParser(file)
    with parser:
        metadata = extractMetadata(parser)
    all_data = metadata.exportDictionary()["Metadata"]
    date_time = (
        all_data["Date-time original"]
        if "Date-time original" in all_data
        else all_data["Creation date"]
    )
    year = get_year_from_str(date_time, "video")

    return year


def get_image_file_metadata(file):
    data = get_image_metadata(file)
    if "DateTime" in data and data["DateTime"] is not None:
        date_time = data["DateTime"]
    else:
        date_time = "NO_DATE"
    return get_year_from_str(date_time, "image")


def get_media_metadata(file):
    file_extension = file.split(".")[-1]
    if file_extension in all_video_types:
        return get_video_file_metadata(file)
    elif file_extension in all_image_types:
        return get_image_file_metadata(file)
    else:
        print(f"file_extension : {file_extension} not in any set")


def get_all_years(src):
    media_files = os_walk(src)
    media_by_year = defaultdict(list)

    for file in media_files:
        raw_year = get_media_metadata(file)
        year = raw_year if raw_year != "1904" else "NO_DATE"
        media_by_year[year].append(file)

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

    year = file_name.split("_")[1][:4]
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
        item_to_dst(file_path, folder)
    else:
        print(f"{file_name} had cleanup issues")


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
def Media_Consolidation(all_media_source, all_media_copy):

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
    year_dict = get_all_years(clean_folder)
    create_folder_for_year_and_move_files(clean_folder, year_dict)
    no_date_folder = f"{clean_folder}/NO_DATE"

    no_date_folder_cleanup(no_date_folder, clean_folder)
    remove_empty_folders(clean_folder)


ALL_MEDIA_SRC = "./MASTER"
ALL_MEDIA_COPY = "./ALL_MEDIA_COPY"
Media_Consolidation(ALL_MEDIA_SRC, ALL_MEDIA_COPY)

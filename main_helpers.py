# Walks through directory and subdirectory and moves all files to master folder
import os
import re
from os_helpers import create_folder, create_dst_path, item_to_dst, os_walk
import hashlib
from constants import all_media_types, types_to_ignore
from magic import Magic


magic_mime = Magic(mime=True)


def move_all_files_to_one_master_folder(src: str, dst: str) -> str:
    """
    Create a new master folder and 2 subfolders called UNIQUE and DUP
    Moves all files to the correct folder and keeps count of unique and dups

    Returns path to clean folder

    """
    # Creates Destination, Destination/UNIQUE, Destination/DUP

    unique_folder, dup_folder = f"{dst}/UNIQUE/", f"{dst}/DUPS/"
    create_folder(dst)
    create_folder(unique_folder)
    create_folder(dup_folder)

    files = os_walk(src)
    print(f"------About to move all files from {src} to {dst} ------")

    # Hashing is used to check for duplicates
    hashes = {}
    total_unique_count = 0
    total_dup_count = 0
    # res = {}
    for file in files:

        # Optimization: Might be able to use less mem up by only checking parts of a hash?
        file_hash = hashlib.sha1(open(file, "rb").read()).hexdigest()
        hashes[file_hash] = hashes.get(file_hash, 0) + 1

        # This means this is the first time we've seen the file
        if hashes[file_hash] == 1:
            dst = f"{unique_folder}/"
            item_to_dst(
                file,
                create_dst_path(file, unique_folder),
                "move_all_files_to_one_master_folder--if hashes[file_hash] == 1",
            )
            total_unique_count += 1
            # if not unique_count % 300:
            #     print(f"{unique_count} Files Moved")
            # res[unique_file_name] = res.get(unique_file_name, 0) + 1

        else:
            # We are in duplicate territory
            dup_count = hashes[file_hash]

            # dup_file_name = f"{dup_folder}/__{cur_count}__{base_file_name}"

            item_to_dst(
                file,
                create_dst_path(file, dup_folder, dup_count),
                "move_all_files_to_one_master_folder--else statement",
            )
            total_dup_count += 1
    #         res[dup_file_name] = res.get(dup_file_name, 0) + 1
    # for item, count in res.items():
    #     if count > 1:
    #         print(item, count)
    # print("RESLEN", len(res))

    print(f"{total_unique_count} UNIQUE moved")
    print(f"{total_dup_count} DUPS moved")
    print(f"{total_dup_count+total_unique_count} total moved")
    print("-------------------------")
    # Returns path to clean_folder for next function
    # return clean_folder


def separate_based_on_file_type(src: str):
    """
    Goes through the clean folder and organizes files into MEDIA and MISC
    We check the type of file 2 ways (MIME and file_extension)
    The reason for doing both is MIME picks up that might not have extension but are media
    File_extension picks up any media the MIME missed b/c it got a default result "application/octet-stream"

    """
    media_folder, misc_folder = f"{src}/Media/", f"{src}/Misc/"
    create_folder(media_folder)
    create_folder(misc_folder)

    files = os_walk(src)
    i = 0
    for file in files:
        file_type = magic_mime.from_file(file)
        file_extension = os.path.splitext(file)[1]

        if (
            file_extension
            and file_extension not in types_to_ignore
            and not re.match(r"^\.\d*$", file_extension)
            and (
                file_type.startswith("image")
                or file_type.startswith("video")
                or file_type.startswith("audio")
                or file_extension in all_media_types
            )
        ):
            item_to_dst(
                file,
                create_dst_path(file, media_folder),
                "separate_based_on_file_type--image or video or audio",
            )
        else:
            item_to_dst(
                file,
                create_dst_path(file, misc_folder),
                "separate_based_on_file_type--misc",
            )
        i += 1
        if not i % 300:
            print(f"{i} files done")


def create_folder_for_year_and_move_files(src: str, year_dict: dict):
    """
    Takes in the Media folder and creates a folder for each year
    """
    for year, media_list in year_dict.items():
        year_folder = f"{src}/{year}"
        create_folder(year_folder)
        for file in media_list:
            item_to_dst(file, year_folder, "create_folder_for_year_and_move_files")

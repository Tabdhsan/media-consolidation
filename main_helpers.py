# Walks through directory and subdirectory and moves all files to master folder
from os_helpers import create_folder, item_to_dst, os_walk
import hashlib
from constants import all_audio_types, all_image_types, all_media_types, all_video_types
from magic import Magic


magic_mime = Magic(mime=True)


def move_all_files_to_one_master_folder(src: str, dst: str) -> str:
    """
    Create a new master folder and 2 subfolders called UNIQUE and DUP
    Moves all files to the correct folder and keeps count of unique and dups

    Returns path to clean folder

    """
    # Creates Destination, Destination/UNIQUE, Destination/DUP
    create_folder(dst)

    clean_folder, dup_folder = f"{dst}/UNIQUE", f"{dst}/DUPS"
    create_folder(clean_folder)
    create_folder(dup_folder)

    files = os_walk(src)
    print(f"------About to move all files from {src} to {dst} ------")

    # Hashing is used to check for duplicates
    hashes = {}
    unique_count = 0
    dup_count = 0

    for file in files:
        # Optimization: Might be able to use less mem up by only checking parts of a hash?
        file_hash = hashlib.sha1(open(file, "rb").read()).hexdigest()
        hashes[file_hash] = hashes.get(file_hash, 0) + 1

        # This means this is the first time we've seen the file
        if hashes[file_hash] == 1:
            item_to_dst(
                file,
                clean_folder,
                "move_all_files_to_one_master_folder--if hashes[file_hash] == 1",
            )
            unique_count += 1
            if not unique_count % 300:
                print(f"{unique_count} Files Moved")

        else:
            # We are in duplicate territory
            dup_count += 1
            cur_count = hashes[file_hash]

            new_name = f"{dup_folder}/__{cur_count}__{file}"
            item_to_dst(
                file, new_name, "move_all_files_to_one_master_folder--else statement"
            )

    print(f"{unique_count} UNIQUE moved")
    print(f"{dup_count} DUPS moved")
    print("-------------------------")
    # Returns path to clean_folder for next function
    return clean_folder


# Optimization: Separate audio as well
def separate_based_on_file_type(src: str):
    """
    Goes through the clean folder and organizes files into MEDIA and MISC

    """
    print("-----About to separate files based on type-----")
    media_folder, misc_folder = f"{src}/Media", f"{src}/Misc"
    create_folder(media_folder)
    create_folder(misc_folder)

    files = os_walk(src)
    for file in files:
        file_type = magic_mime.from_file(file)
        if file_type.startswith("image") or file_type.startswith("video"):
            item_to_dst(
                file, media_folder, "separate_based_on_file_type--image or video"
            )
        else:
            item_to_dst(file, misc_folder, "separate_based_on_file_type--misc")


# TODOTAB: Is this used?
def create_folder_for_year_and_move_files(src: str, year_dict: dict):
    for year, media_list in year_dict.items():
        year_folder = f"{src}/{year}"
        create_folder(year_folder)
        for file in media_list:
            item_to_dst(file, year_folder, "create_folder_for_year_and_move_files")

import hashlib
import os
import re
import time

from magic import Magic

from constants import all_audio_types, all_media_types, types_to_ignore
from os_helpers import create_folder, item_to_dst, os_walk

magic_mime = Magic(mime=True)


def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        print(f"Elapsed time: {minutes} minutes and {seconds} seconds")
        return result

    return wrapper


def count_files(folder: str) -> int:
    count = 0
    for root, _, files in os.walk(folder):
        for f in files:
            if os.path.isfile(os.path.join(root, f)):
                count += 1
    return count


def move_all_files_to_one_master_folder(src: str, dst: str) -> None:
    """
    Moves all files from the source directory to the destination directory,
    categorizing unique and duplicate files.

    Args:
        src (str): Source directory path.
        dst (str): Destination directory path.

    Returns:
        None
    """
    unique_folder = os.path.join(dst, "UNIQUE")
    dup_folder = os.path.join(dst, "DUPS")
    create_folder(dst)
    create_folder(unique_folder)
    create_folder(dup_folder)

    files = os_walk(src)

    # Hashing is used to check for duplicates
    hashes = {}
    total_unique_count = 0
    total_dup_count = 0

    for i, file in enumerate(files):
        # Optimization: Might be able to use less mem up by only checking parts of a hash?

        file_hash = hashlib.sha1(open(file, "rb").read()).hexdigest()
        hashes[file_hash] = hashes.get(file_hash, 0) + 1

        # This means this is the first time we've seen the file
        if hashes[file_hash] == 1:
            destination = unique_folder
            total_unique_count += 1
        else:
            destination = dup_folder
            total_dup_count += 1

        item_to_dst(file, destination, "move_all_files_to_one_master_folder")

        if (i + 1) % 300 == 0:
            print(f"{i + 1} files processed")

    print(f"{total_unique_count} unique files moved")
    print(f"{total_dup_count} duplicate files moved")
    print(f"{total_dup_count + total_unique_count} total files moved")
    print("")


def separate_based_on_file_type(src: str) -> None:
    """
    Separates files into Media, Audio, and Misc folders based on file type.

    Args:
        src (str): Source directory path.

    Returns:
        None
    """
    media_folder = os.path.join(src, "Media")
    audio_folder = os.path.join(src, "Audio")
    misc_folder = os.path.join(src, "Misc")
    create_folder(media_folder)
    create_folder(audio_folder)
    create_folder(misc_folder)

    files = os_walk(src)

    for i, file in enumerate(files):
        try:
            file_type = magic_mime.from_file(file)
        except Exception as e:
            file_type = "error"
            print("-------")
            print(e, file)
            print("-------")

        file_extension = os.path.splitext(file)[1]
        is_audio = file_extension in all_audio_types or file_type.startswith("audio")

        if (
            file_extension
            and file_extension not in types_to_ignore
            and not re.match(r"^\.\d*$", file_extension)
            and (
                file_type.startswith("image")
                or file_type.startswith("video")
                or is_audio
                or file_extension in all_media_types
            )
        ):
            destination = media_folder if not is_audio else audio_folder
            item_to_dst(file, destination, "separate_based_on_file_type")
        else:
            item_to_dst(file, misc_folder, "separate_based_on_file_type")

        if (i + 1) % 300 == 0:
            print(f"{i + 1} files processed")


def create_folder_for_year_and_move_files(src: str, year_dict: dict) -> None:
    """
    Creates year-based folders and moves files to respective folders.

    Args:
        src (str): Source directory path.
        year_dict (dict): Dictionary containing years and associated media files.

    Returns:
        None
    """
    for year, media_list in year_dict.items():
        year_folder = os.path.join(src, str(year))
        create_folder(year_folder)
        for file in media_list:
            item_to_dst(file, year_folder, "create_folder_for_year_and_move_files")

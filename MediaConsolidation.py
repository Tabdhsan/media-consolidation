import os
import time
from main_helpers import (
    create_folder_for_year_and_move_files,
    move_all_files_to_one_master_folder,
    separate_based_on_file_type,
)
from metadata_helpers import get_all_years_dict

BASE_FOLDER = "E:/media-for-consolidation-script"
ERROR_FOLDER = f"{BASE_FOLDER}/FlattenedFiles/ERRORS"
START_FOLDER = f"{BASE_FOLDER}/MASTER"
FLAT_FOLDER = f"{BASE_FOLDER}/FlattenedFiles"


def file_count(folder):
    print(folder)
    count = 0
    for root, _, files in os.walk(folder):
        for f in files:
            if os.path.isfile(os.path.join(root, f)):
                count += 1
    return count


def Media_Consolidation(src, dst):
    # Move all files into a new flat folder separated by UNIQUE and DUPS
    src_count = file_count(src)
    move_all_files_to_one_master_folder(src, dst)
    dst_count = file_count(FLAT_FOLDER)
    print(src_count)
    print(dst_count)

    clean_folder = f"{dst}/UNIQUE"

    # # Separate into Media and Misc
    print("-------ABT TO SEPARATE INTO MEDIA AND MISC-------")
    separate_based_on_file_type(clean_folder)
    quit()
    # Organize files strings by year -> {year :[files]}
    all_years_and_media = get_all_years_dict(clean_folder)

    # Create year folders and move files
    print("-------MOVING TO YEARS-------")
    create_folder_for_year_and_move_files(clean_folder, all_years_and_media)

    dst_count = file_count(dst)
    print("src_count->", src_count)
    print("dst_count->", dst_count)

    print("files separated")


start_time = time.time()
Media_Consolidation(START_FOLDER, FLAT_FOLDER)
end_time = time.time()
elapsed_time = end_time - start_time
minutes = int(elapsed_time // 60)
seconds = int(elapsed_time % 60)
print(f"Elapsed time: {minutes} minutes and {seconds} seconds")

# TODOTAB: Need function to turn clean/Misc folder -> multiple folders by extensions

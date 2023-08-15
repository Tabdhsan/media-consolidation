import os
import time
from main_helpers import (
    create_folder_for_year_and_move_files,
    move_all_files_to_one_master_folder,
    separate_based_on_file_type,
)
from metadata_helpers import get_all_years_dict

from tkinter.filedialog import askdirectory


def file_count(folder):
    count = 0
    for root, _, files in os.walk(folder):
        for f in files:
            if os.path.isfile(os.path.join(root, f)):
                count += 1
    return count


def Media_Consolidation():
    SRC_DIRECTORY = (
        rf"{askdirectory(title='Select Folder to Consolidate', mustexist=True)}"
    )

    DST_DIRECTORY = rf"{askdirectory(title='Select Destination Folder', mustexist=True)}/Consolidated"

    UNIQUE_FOLDER = f"{DST_DIRECTORY}/UNIQUE"
    MEDIA_FOLDER = f"{UNIQUE_FOLDER}/Media"

    # Move all files into a new flat folder separated by UNIQUE and DUPS
    print("Starting process to move all files into new folder!")
    print("")
    time.sleep(1.5)
    print("Using hashing to sift out duplicate files...")
    print("")
    time.sleep(1.5)

    src_count = file_count(SRC_DIRECTORY)
    move_all_files_to_one_master_folder(SRC_DIRECTORY, DST_DIRECTORY)

    dst_count = file_count(DST_DIRECTORY)

    # # Separate into Media and Misc
    print("About to separate files into Audio, Media and Misc Folders...")
    print("")

    separate_based_on_file_type(UNIQUE_FOLDER)
    # Organize files strings by year -> {year :[files]}
    all_years_and_media = get_all_years_dict(MEDIA_FOLDER)

    # Create year folders and move files
    print("About to organize media by years...")
    print("")
    time.sleep(1.5)
    create_folder_for_year_and_move_files(MEDIA_FOLDER, all_years_and_media)

    dst_count = file_count(DST_DIRECTORY)
    print("Script has successfully completed! 🎉🎉🎉")


start_time = time.time()
Media_Consolidation()
end_time = time.time()
elapsed_time = end_time - start_time
minutes = int(elapsed_time // 60)
seconds = int(elapsed_time % 60)
print(f"Elapsed time: {minutes} minutes and {seconds} seconds")
print("")

# TODOTAB: Need function to turn clean/Misc folder -> multiple folders by extensions

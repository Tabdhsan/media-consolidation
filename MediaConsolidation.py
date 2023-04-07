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


def Media_Consolidation(src, dst):
    # Move all files into a new flat folder separated by UNIQUE and DUPS
    clean_folder = move_all_files_to_one_master_folder(src, dst)

    # # Separate into Media and Misc
    print("-------ABT TO SEPARATE INTO MEDIA AND MISC-------")
    separate_based_on_file_type(clean_folder)
    # Organize files strings by year -> {year :[files]}

    all_years_and_media = get_all_years_dict(clean_folder)

    # Create year folders and move files
    print("-------MOVING TO YEARS-------")
    create_folder_for_year_and_move_files(clean_folder, all_years_and_media)

    print("files separated")


Media_Consolidation(START_FOLDER, FLAT_FOLDER)

# TODOTAB: Need function to turn clean/Misc folder -> multiple folders by extensions

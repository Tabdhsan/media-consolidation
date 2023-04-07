from main_helpers import (
    create_folder_for_year_and_move_files,
    move_all_files_to_one_master_folder,
    separate_based_on_file_type,
)
from metadata_helpers import get_all_years_dict


ERROR_FOLDER = "./FlattenedFiles/ERRORS"

START_FOLDER = ""
MASTER_FOLDER = ""


def Media_Consolidation(src, dst):
    # Move all files into a new flat folder separated by UNIQUE and DUPS
    clean_folder = move_all_files_to_one_master_folder(START_FOLDER, MASTER_FOLDER)

    # Separate into Media and Misc
    separate_based_on_file_type(clean_folder)

    # Organize files strings by year -> {year :[files]}
    all_years_and_media = get_all_years_dict(f"{clean_folder}/Media")

    # Create year folders and move files
    create_folder_for_year_and_move_files(f"{clean_folder}/Media", all_years_and_media)

    print("done")


# TODOTAB: Need function to turn clean/Misc folder -> multiple folders by extensions

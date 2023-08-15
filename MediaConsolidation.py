from tkinter.filedialog import askdirectory

from main_helpers import (
    create_folder_for_year_and_move_files,
    count_files,
    move_all_files_to_one_master_folder,
    separate_based_on_file_type,
    timer_decorator,
)
from metadata_helpers import get_all_years_dict


@timer_decorator
def Media_Consolidation():
    SRC_DIRECTORY = (
        rf"{askdirectory(title='Select Folder to Consolidate', mustexist=True)}"
    )

    DST_DIRECTORY = rf"{askdirectory(title='Select Destination Folder', mustexist=True)}/Consolidated"

    UNIQUE_FOLDER = f"{DST_DIRECTORY}/UNIQUE"
    MEDIA_FOLDER = f"{UNIQUE_FOLDER}/Media"

    # Move all files into a new flat folder separated by UNIQUE and DUPS
    src_count = count_files(SRC_DIRECTORY)
    move_all_files_to_one_master_folder(SRC_DIRECTORY, DST_DIRECTORY)

    dst_count = count_files(DST_DIRECTORY)

    # Separate into Media and Misc
    print("About to separate files into Audio, Media and Misc Folders...\n")

    separate_based_on_file_type(UNIQUE_FOLDER)
    # Organize files strings by year -> {year :[files]}
    all_years_and_media = get_all_years_dict(MEDIA_FOLDER)

    # Create year folders and move files
    print("About to organize media by years...\n")
    create_folder_for_year_and_move_files(MEDIA_FOLDER, all_years_and_media)

    dst_count = count_files(DST_DIRECTORY)
    print(f"Started with {src_count} files and ended with {dst_count} files ")
    print("Script has successfully completed! 🎉🎉🎉")


if __name__ == "__main__":
    Media_Consolidation()

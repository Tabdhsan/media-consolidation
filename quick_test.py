from collections import defaultdict
import filecmp
import os
import hashlib
import time

# Set the paths to the two folders
BASE_FOLDER = "E:/"
folder1 = f"{BASE_FOLDER}/media-for-consolidation-script/FlattenedFiles"
folder2 = f"{BASE_FOLDER}/MASTER_DO_NOT_DELETE - Copy/DAD SD CARD"


def file_count(folder):
    print(folder)
    count = 0
    for root, _, files in os.walk(folder):
        for f in files:
            if os.path.isfile(os.path.join(root, f)):
                count += 1
    return count


# Keep track of files that have been processed
def quick_test():
    start_time = time.time()
    folder1_files = []
    folder2_files = []

    for dirpath, _, filenames in os.walk(folder1):
        for filename in filenames:
            folder1_files.append(os.path.join(dirpath, filename))

    for dirpath, _, filenames in os.walk(folder2):
        for filename in filenames:
            folder2_files.append(os.path.join(dirpath, filename))

    res = []
    # Compare each file in folder1 with each file in folder2
    for file1 in folder2_files:
        found_match = False
        for file2 in folder1_files:
            if filecmp.cmp(file1, file2):
                found_match = True
                break
        if not found_match:
            res.append(file1)
    print(len(res))

    # Print the list of unique files

    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    print(f"Elapsed time: {minutes} minutes and {seconds} seconds")

    # print(len(unique_hash_set))
    # print(f"len we should have-> {abs(file_count(folder1)-file_count(folder2))} ")


quick_test()

import errno, os, stat, shutil
import random
from datetime import datetime, timezone


def os_walk(src: str, get_list: bool = False) -> list:
    """
    Brief function description goes here.

    ARGS:
        src: string of starting folder
        get_list: boolean that chooses what format to return res

    :return: [filePath ...] or [[filePath, fileName]...]
    """
    res = []
    for root, _, files in os.walk(src):
        for name in files:
            # Either appends the filePath or [filePath, fileName]
            file = (
                os.path.join(root, name)
                if not get_list
                else [os.path.join(root, name), name]
            )
            res.append(file)
    return res


def handle_remove_read_only(func, path, exc):
    """
    Helper function given to shutil.rmtree for on error
    ex.  shutil.rmtree(filename, ignore_errors=False, onerror=handle_remove_read_only)

    Using this makes sure readonly files and files with data inside can be deleted

    """
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise


# TODOTAB: Might not even be used
def remove_empty_folders(src: str):
    """
    Removes all empty folders and accounts for errors as well via "handle_remove_read_only"
    """
    walk = list(os.walk(src))
    for path, _, _ in walk[::-1]:
        if len(os.listdir(path)) == 0:
            try:
                shutil.rmtree(
                    path, ignore_errors=False, onerror=handle_remove_read_only
                )
            except Exception as error:
                print(f"Could not delete {path}", error)


# Optimization: Can be run conditionally based on whether checked in GUI
def create_directory_copy(src: str, dst: str):
    shutil.copytree(src, dst)


def create_folder(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def create_dst_path(src, dst, dup_count=0):
    # Timestamp logic is to avoid overwriting files with the same name
    time_stamp = int(datetime.now(timezone.utc).timestamp())
    random_digit = random.randint(0, 99999999)

    # E:/folder/subfolder/20220604_220000.mp4" -> 20220604_220000.mp4
    base_file_name = os.path.basename(src)
    name, ext = os.path.splitext(base_file_name)

    dup_str = f"{dup_count}_" if dup_count else ""
    new_name = f"{dup_str}{name}_{time_stamp + random_digit}{ext}"
    new_path = os.path.join(dst, new_name)
    # print(new_path)

    print("new_path", new_path)
    return new_path

    # TODOTAB: Get better way to randomize and add logic when to randomize

    # directory, file_name = os.path.split(src)
    # name, ext = os.path.splitext(file_name)
    # new_name = (
    #     f"{dup_count if dup_count else ''}{name}_{time_stamp}_{random_digit}{ext}"
    # )
    # new_path = os.path.join(dst, new_name)

    # return new_path


def item_to_dst(src: str, dst: str, error_function_name: str = ""):
    """
        Moves a file or folder to a new location
        SRC can be a file or a folder
        DST is a file
        Adds a timestamp on the end to make sure the file is unique

    ARGS:
        src can be a folder or a file
        dst is a string for the dst location
        error_function_name is where the helper function was used (for debugging)

    """
    try:
        shutil.move(src, dst)
    except Exception as e:
        print()
        print("--ERROR--", "FUNCTION:", error_function_name)
        print(e)
        print()


# TODOTAB: Might not even be used
def get_folder_size(folder):
    size = 0
    for path, _, files in os.walk(folder):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)

    return size

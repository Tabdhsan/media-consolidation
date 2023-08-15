import errno
import os
import random
import shutil
import stat
from datetime import datetime, timezone


def os_walk(src: str, get_list: bool = False) -> list:
    """
    Recursively walk through directories and return file paths or [file path, file name] pairs.

    Args:
        src (str): Starting folder path
        get_list (bool, optional): Boolean to choose the format of return. Defaults to False.

    Returns:
        list: List of file paths or [file path, file name] pairs
    """
    res = []
    for root, _, files in os.walk(src):
        for name in files:
            # Either appends the file path or [file path, file name]
            file = (
                os.path.join(root, name)
                if not get_list
                else [os.path.join(root, name), name]
            )
            res.append(file)
    return res


def handle_remove_read_only(func, path, exc):
    """
    Helper function given to shutil.rmtree for handling errors when removing files.

    Args:
        func: Operation function (os.rmdir or os.remove)
        path: Path to the file or directory
        exc: Exception information
    """
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise


def remove_empty_folders(src: str):
    """
    Removes all empty folders and handles errors using "handle_remove_read_only".

    Args:
        src (str): Folder path
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


def create_directory_copy(src: str, dst: str):
    """
    Creates a copy of a directory.

    Args:
        src (str): Source directory path
        dst (str): Destination directory path
    """
    shutil.copytree(src, dst)


def create_folder(path: str):
    """
    Creates a folder if it doesn't exist.

    Args:
        path (str): Folder path to create
    """
    if not os.path.exists(path):
        os.makedirs(path)


def create_dst_path(src, dst, dup_count=0):
    pass


def item_to_dst(src_file: str, dst_folder: str, error_function_name: str = ""):
    """
    Moves a file or folder to a new location. Adds a timestamp to ensure uniqueness.

    Args:
        src_file (str): Source file or folder path
        dst_folder (str): Destination folder path
        error_function_name (str, optional): Name of the calling function (for debugging). Defaults to "".
    """
    try:
        file_name_with_ext = os.path.basename(src_file)
        dst_string = os.path.join(dst_folder, file_name_with_ext)
        if os.path.exists(dst_string):
            random_digit = int(datetime.now(timezone.utc).timestamp()) + random.randint(
                0, 99999999
            )
            dst_string = os.path.join(
                dst_folder, f"{random_digit}_{file_name_with_ext}"
            )

        shutil.move(src_file, dst_string)

    except Exception as e:
        print(
            "\n--ERROR--\n",
            "FUNCTION:",
            error_function_name,
            f"\nsrc:{src_file}",
            f"\ndst:{dst_folder}",
        )
        print(e)
        print()


def get_folder_size(folder):
    size = 0
    for path, _, files in os.walk(folder):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)

    return size

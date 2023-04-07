import errno, os, stat, shutil
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


def item_to_dst(src: str, dst: str, error_function_name: str = ""):
    """
        Moves a file or folder to a new location
        Adds a timestamp on the end to make sure the file is unique

    ARGS:
        src can be a folder or a file
        dst is a string for the dst location
        error_function_name is where the helper function was used (for debugging)

    """
    try:
        time_stamp = int(datetime.now(timezone.utc).timestamp())
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

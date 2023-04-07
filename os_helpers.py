import errno, os, stat, shutil


def os_walk(src: str, get_list: bool = False) -> list:
    """
    Brief function description goes here.

    ARGS:
        src: string of starting folder
        get_list: boolean that chooses what format to return res

    :return: [filePath ...] or [[filePath, fileName]...]
    """
    res = []
    for root, dirs, files in os.walk(src):
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


def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

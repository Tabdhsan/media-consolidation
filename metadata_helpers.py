from collections import defaultdict
import os
from datetime import datetime

from dateutil.parser import parse
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image
from magic import Magic

from os_helpers import os_walk


magic_mime = Magic(mime=True)


def get_year_from_string(date: str) -> str:
    date_object = parse(date)
    year = date_object.year
    return year


def get_earliest_date_time(file: str) -> str:
    """
    Returns earliest date time object related to file

    Returns 'YYYY:MM:DD'

    """
    created_time = datetime.fromtimestamp(os.path.getctime(file))
    modified_time = datetime.fromtimestamp(os.path.getmtime(file))
    earliest_time = min(created_time, modified_time)
    earliest_time = earliest_time.strftime("%Y:%m:%d")

    return earliest_time


# Optimization: Can we just get earliest time via os.path everywhere?
def get_image_year(image_file: str) -> object:
    """
    Takes in a file, creates a PIL Image and gets datetime
    Returns
            {datetime: year:month:day}
    """
    PIL_image_instance = Image.open(image_file)
    exif_data = PIL_image_instance.getexif()
    cur_image_info = {}

    DATETIME_TAG_ID = 306
    """
    These are from the exif data and more tags can be found via for loop comment below
    DATETIME_TAG_ID = 306 
    TODOTAB: This might be getting just modified date anyway.
    TODOTAB: Look for other options like dateTaken
    for tag_id in exif_data:
        tag = TAGS.get(tag_id, tag_id)
        print(tag, tag_id)
    """
    try:
        date_bytes = exif_data.get(DATETIME_TAG_ID)
        if date_bytes:
            # 2015:06:06 16:08:32
            date = date_bytes.split(" ")[0]
        else:
            date = get_earliest_date_time(image_file)

        cur_image_info["date"] = date

    except Exception as e:
        print()
        print("WE HIT EXCEPT in get image metadata")
        print(e)
        # TODO: Might be an edge case issue that needs to be handled here
        print()
    return cur_image_info


def get_video_year(file):
    parser = createParser(file)
    with parser:
        metadata = extractMetadata(parser)

    try:
        all_data = metadata.exportDictionary()["Metadata"]
        date_time = (
            all_data["Date-time original"]
            if "Date-time original" in all_data
            else all_data["Creation date"]
        )
        year = get_year_from_string(date_time)

        # TODOTAB: Handle this later
        # if year == "1904":
        #     year = str(getMediaModifiedDate(file))
        #     year = year.replace("-", ":").split(":")[0]

        return year
    except Exception as error:
        print(error)
        # TODOTAB: Get error folder logic
        # print("moving file to error folder", file)
        # item_to_dst(file, f"{ERROR_FOLDER}/file")
        return "NO_DATE"


def get_media_year(file):
    file_type = magic_mime.from_file(file)
    if file_type == "video":
        return get_media_year(file)
    elif file_type in "image":
        return get_image_year(file)
    else:
        print("file_type was weird", file_type)


def get_all_years_dict(src) -> dict:
    """
    Returns a dict { year:[files] }

    """
    print("------------Trying to get all years--------------")
    media_files = os_walk(src)
    media_by_year = defaultdict(list)

    for file in media_files:
        raw_year = get_media_year(file)
        media_by_year[raw_year].append(file)

    return media_by_year


# def get_whatsapp_year(file_name):
#     pieces = file_name.split("-")  # IMG-20211230-WA00000.jpg
#     if pieces[-1].startswith("WA"):
#         date = pieces[1]
#         year = date[:4]
#         month = date[4:6]
#         day = date[6:]
#         return year


# def get_screenshot_year(file_name):
#     # Screenshot_20211203-150147_Settings

#     match = bool(re.fullmatch(r"Screenshot_*-*_*", file_name))

#     year = file_name.split("_")[1][:4] if match else None
#     return year


# def get_basic_and_tiktok_file_year(file_name):
#     return file_name[:4]


# def get_no_date_file_name_type(file_name):
#     # WHATSAPP = [IMG/VID]-20211230-WA00000.jpg
#     whatsapp_regex = re.compile(r"^\w+-\d+-WA\d+\.\w+$")

#     # Screenshot_20211203-150147_Settings
#     screenshot_regex = re.compile(r"^Screenshot_*")

#     # Basic = 20210905_004903.jpg
#     basic_regex = re.compile(r"^\d+_\d+\.\w+$")

#     # Tiktok = 2021-09-05-004903.jpg
#     tiktok_regex = re.compile(r"^\d+-\d+-\d+-\d+\.\w+$")

#     if bool(re.fullmatch(whatsapp_regex, file_name)):
#         return "WHATSAPP"

#     if bool(re.match(screenshot_regex, file_name)):
#         return "SCREENSHOT"

#     if bool(re.fullmatch(basic_regex, file_name)) or bool(
#         re.fullmatch(tiktok_regex, file_name)
#     ):
#         return "BASIC"


# def get_year_from_file_name(file_name, file_type):
#     if file_type == "WHATSAPP":
#         return get_whatsapp_year(file_name)

#     if file_type == "SCREENSHOT":
#         return get_screenshot_year(file_name)

#     if file_type == "BASIC":
#         return get_basic_and_tiktok_file_year(file_name)


# def all_types_cleanup(file_path, file_name, src):
#     file_type = get_no_date_file_name_type(file_name)
#     year = get_year_from_file_name(file_name, file_type)
#     if file_type and year:
#         folder = f"{src}/{year}"
#         create_folder(folder)
#         item_to_dst(file_path, folder, "from all type clean")


# def no_date_folder_cleanup(no_date_folder, clean_folder):
#     files = os_walk(no_date_folder, True)
#     count = 0
#     for filepath, file_name in files:
#         count += 1
#         all_types_cleanup(filepath, file_name, clean_folder)

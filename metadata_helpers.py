from datetime import datetime
import os
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image
from PIL.ExifTags import TAGS


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
def get_image_metadata(image_file: str) -> object:
    """
    Takes in a file, creates a PIL Image and gets datetime
    Returns
            {datetime: year:month:day}
    """
    PIL_image_instance = Image.open(image_file)
    exif_data = PIL_image_instance.getexif()
    cur_image_info = {"date": None}

    DATETIME_TAG_ID = 306
    """
    These are from the exif data and more tags can be found via for loop comment below
    DATETIME_TAG_ID = 306
    for tag_id in exif_data:
        tag = TAGS.get(tag_id, tag_id)
        print(tag, tag_id)
        data = exif_data.get(tag_id)
    """
    try:
        date_bytes = exif_data.get(DATETIME_TAG_ID)
        if date_bytes:
            # date = date_bytes.decode()
            print("decoded", date_bytes)
            date = get_earliest_date_time(image_file)
            print(date)
        else:
            pass

        cur_image_info["date"] = date

    except Exception as e:
        print()
        print("WE HIT EXCEPT in get image metadata")
        print(e)
        # TODO: Might be an edge case issue that needs to be handled here
        print()
    return cur_image_info


get_image_metadata("./IMG_20150606_160831.jpg")
# def get_year_from_str(raw_date_string, media_type):

#     try:
#         date, time = raw_date_string.split(" ")
#     except Exception as e:
#         return raw_date_string
#     if media_type == "image":
#         year, month, day = date.split(":")
#     else:
#         year, month, day = date.split("-")
#     return year

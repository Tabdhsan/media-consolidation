import os
from collections import defaultdict
from datetime import datetime

from dateutil.parser import parse
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from magic import Magic
from PIL import Image

from constants import all_image_types, all_video_types
from os_helpers import os_walk

magic_mime = Magic(mime=True)


def get_year_from_string(date: str) -> str:
    date_object = parse(date)
    year = date_object.year
    return year


def get_earliest_date_time(file: str) -> str:
    created_time = datetime.fromtimestamp(os.path.getctime(file))
    modified_time = datetime.fromtimestamp(os.path.getmtime(file))
    earliest_time = min(created_time, modified_time)
    earliest_time = earliest_time.strftime("%Y:%m:%d")
    return earliest_time


def get_image_year(image_file: str) -> str:
    try:
        PIL_image_instance = Image.open(image_file)
        exif_data = PIL_image_instance.getexif()
        DATETIME_TAG_ID = 306
        date_bytes = exif_data.get(DATETIME_TAG_ID)
        if date_bytes:
            year = date_bytes[:4]
        else:
            year = get_earliest_date_time(image_file)[:4]
        return year
    except Exception as e:
        print("\nWE HIT EXCEPT in get image metadata")
        print(f"{e}\n")
        print(f"FILE: {image_file}")


def get_video_year(file: str) -> str:
    parser = createParser(file)
    try:
        with parser:
            metadata = extractMetadata(parser)
        all_data = metadata.exportDictionary()["Metadata"]
        date_time = all_data.get("Date-time original") or all_data.get("Creation date")
        year = (
            get_year_from_string(date_time)
            if date_time
            else get_earliest_date_time(file)[:4]
        )

        # NOTE: Media Parsers sometimes default to 1904
        if year == "1904":
            year = get_earliest_date_time(file)[:4]
        return year
    except Exception as error:
        print("in error", error)
        print("file that errored", file)
        return get_earliest_date_time(file)[:4]


def get_media_year(file: str) -> str:
    file_type = magic_mime.from_file(file)
    file_ext = os.path.splitext(file)[1]
    if file_type.startswith("video") or file_ext in all_video_types:
        return get_video_year(file)
    elif file_type.startswith("image") or file_ext in all_image_types:
        return get_image_year(file)
    else:
        return "WEIRD"


def get_all_years_dict(src: str) -> dict:
    media_files = os_walk(src)
    media_by_year = defaultdict(list)

    for file in media_files:
        raw_year = get_media_year(file)
        media_by_year[raw_year].append(file)

    return media_by_year

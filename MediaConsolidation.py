import os
import re
import shutil
import tkinter as tk
from collections import defaultdict
from datetime import datetime, timezone
from random import randint
from tkinter.filedialog import askdirectory
from xmlrpc.client import boolean

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image
from PIL.ExifTags import TAGS

from constants import all_audio_types, all_image_types, all_media_types, all_video_types

ERROR_FOLDER = "./FlattenedFiles/ERRORS"


def Media_Consolidation():
    pass


# TODOTAB: Need function to turn clean/Misc folder -> multiple folders by extensions

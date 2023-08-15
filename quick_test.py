import os

BASE_FOLDER = "E:/media-for-consolidation-script"
MEDIA_FOLDER = f"{BASE_FOLDER}/FlattenedFiles/UNIQUE/Media"
AUDIO_FOLDER = f"{BASE_FOLDER}/FlattenedFiles/UNIQUE/Audio"


audio_ext = []


def get_extensions(folder):
    res = []
    for _, _, files in os.walk(folder):
        for file_name in files:
            _, extension = os.path.splitext(file_name)
            res.append(extension)

    return list(set(res))


print("----MEDIA----")
for item in get_extensions(MEDIA_FOLDER):
    print(item)
print("----MEDIA----")
print("---------------------")
print("----Audio----")
for item in get_extensions(AUDIO_FOLDER):
    print(item)
print("----Audio----")

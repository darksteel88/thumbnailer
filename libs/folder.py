from .video import is_video
import os
import re

def get_all_video_files(source):
    """Returns an iterator of all the videos contained inside the source folder
    Results are returned as their fullpath name"""

    # note that we are intentionally not using an iterator here
    # because the expectation is we will be printing some sort of progress information
    # which is not possible with an iterator because we don't know the total size
    results = []
    for root, dirs, files in os.walk(source):
        if files:
            for f in files:
                if is_video(os.path.join(root, f)):
                    results.append(os.path.join(root, f))
    return results

def does_thumb_exist(f, file_format, file_suffix):
    """Returns True/False depending on whether the thumbnail file exists"""
    return os.path.exists("{}{}.{}".format(f.split('.')[0], file_suffix, file_format))

def get_folder_from_file(f):
    """Returns the folder of a given file"""
    return os.sep.join(f.split('\\')[0:-1])

def delete_temp_thumbs(thumb_files):
    """Remove all the temporary thumbnails generated"""

    for f in thumb_files:
        os.remove(f)

def _get_thumbnail_list(folder):
    """Get a list of all the files in the folder that are thumbnail files for us to join"""
    pattern = r'[a-zA-z]+\d{4}'
    results = []
    for root, dirs, files in os.walk(folder):
        for f in files:
            if re.match(pattern, f):
                results.append(os.path.join(root, f))
    return results

def get_thumbnail_filename(filename, suffix=None):
    res = filename.split('.')[0]
    if suffix:
        res += suffix
    return res

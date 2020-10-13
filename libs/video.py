from . import helpers

from decimal import Decimal

import datetime
import ffmpeg
import math
import mimetypes
import multiprocessing as mp
import os
import time

def is_video(path):
    """Returns True/False depending on whether the file denoted by the path is a video"""
    if not os.path.exists(path) or not os.path.isfile(path):
        return False
    if mimetypes.guess_type(path)[0].lower().startswith('video'):
        return True
    else:
        return False

def _format_bitrate(bitrate):
    """Given a bitrate in b/s format it to kb/s rounded up"""

    bitrate = f'{bitrate[0:4]}.{bitrate[4:]}'
    return helpers._round_whole(bitrate)

def _format_fps(avg_frame_rate, r_frame_rate):
    """Given the raw format of fps from ffprobe return it formatted to two decimal places"""
    
    try:
        splits = avg_frame_rate.split('/')
        return Decimal(int(splits[0]) / int(splits[1])).quantize(Decimal('0.01'))
    except Exception as e:
        splits = r_frame_rate.split('/')
        return Decimal(int(splits[0]) / int(splits[1])).quantize(Decimal('0.01'))

def _parse_video(data):
    """Given raw data from ffprobe about a video's video portion return a dict with the following keys:
    codec - the codec of the video file
    pixel_format - the colour encoding of the pixels
    height
    width
    fps - the frames per second of the video, may be slightly less than expected ie 30 is 29.97"""
    
    return {
        'codec': data['codec_name'],
        'pixel_format': data['pix_fmt'],
        'height': data['height'],
        'width': data['width'],
        'fps': _format_fps(data['avg_frame_rate'], data['r_frame_rate']),
    }

def _get_video_stream(data):
    """Given the input data streams return the one corresponding to video"""

    """Each one has data relevant to the type, video, audio, etc.
    And the order is random"""

    for stream in data:
        if stream['codec_type'] == 'video':
            return stream

    raise ValueError("Could not get video details") # TODO: do something about this


def get_header_info(filepath):
    """Returns the data to add to the header as a dictionary with the following keys:
    filename: name of the file
    size: {bytes, humansize}
    duration: datetime.timedelta
    average bitrate: humansize
    video details: {codec, pixel_format, height, width, fps}
    data is returned in a raw format that can be formatted for display"""

    data = ffmpeg.probe(filepath)
    filename = filepath.split(os.sep)[-1]

    results = {
        'filename': filename,
        'size': {
            'humansize': helpers.humansize(int(data['format']['size'])),
            'bytes': int(data['format']['size']),
        },
        'duration': datetime.timedelta(seconds=helpers._round_whole(data['format']['duration'])),
        'avg.bitrate': _format_bitrate(data['format']['bit_rate']),
        'video': _parse_video(_get_video_stream(data['streams'])),
    }

    return results

def generate_individual_thumbnails(filename, duration, num_thumbs, output_width, output_folder, file_format, multi_processing=False):
    """Given a video file generate all the individual thumbnails for it
    All thumbnails have the output format thumb1234.format
    These are only temporary so we use a generic suffix for it

    Returns the start position and vframes ratio"""

    start_pos, vframes_ratio = _determine_start_post_and_vframes_ratio(duration, num_thumbs)
    # ffmpeg for some reason needs an initial seed to offset the timestamp
    # and this is exactly half the start position
    start_pos -= math.floor(0.5*start_pos)

    # because of how slow ffmpeg is at seeking through the video for future frames
    # it's far faster to seek to the exact frame and generate the screen
    # so instead of running the command to let ffmpeg generate all the screen itself
    # we do them all individually
    # we also enable multiprocessing but only if we specify it explicitly because it'll consume a large amount of resources
    if multi_processing:
        processes = []
    for i in range(1, num_thumbs+1):
        ss = 2*(start_pos * i) - (i-1)
        output_name = 'thumb{}'.format(str(i).zfill(4))
        if multi_processing:
            proc = mp.Process(target=generate_ffmpeg_screen, args=(ss, filename, output_width, output_folder, output_name, file_format))
            processes.append(proc)
            proc.start()
        else:
            generate_ffmpeg_screen(ss, filename, output_width, output_folder, output_name, file_format)

    if multi_processing:
        for p in processes:
            p.join()

    # even though we modified start_pos above that's only to the ffmpeg command
    # our real start pos is still at vframes_ratio
    return vframes_ratio, vframes_ratio

def _determine_start_post_and_vframes_ratio(duration, num_thumbs):
    """Determine the starting position and vframes ratio
    In most cases these should be the same for you to get equidistant frames"""

    # we return start for both since that's what you do for equidistant frames
    # change this if it doesn't work for you
    start = int(duration / (num_thumbs + 1))
    return start, start

def generate_ffmpeg_screen(ss, filename, output_width, output_folder, output_name, file_format):
    """Generate a screenshot in ffmpeg"""

    ffmpeg.input(filename, ss=ss) \
          .filter('scale', output_width, -1) \
          .output("{}{}{}.{}".format(output_folder, os.sep, output_name, file_format),
                  vframes=1) \
          .run(capture_stdout=True, capture_stderr=True)
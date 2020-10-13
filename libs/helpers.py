from decimal import Decimal

SUFFIXES = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

def humansize(nbytes):
    i = 0
    while nbytes >= 1024 and i < len(SUFFIXES)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, SUFFIXES[i])

def _round_whole(n, as_int=True):
    """Round a decimal to a whole number
    as_int - returns as an int if specified otherwise as a Decimal"""

    ret = Decimal(n).quantize(Decimal('0'))
    if as_int:
        ret = int(ret)
    return ret

def human_readable_header_info(info):
    """Given header information format it in a more human readable way for display purposes"""

    return {
        'avg.bitrate': f'{info["avg.bitrate"]} kb/s',
        'filename': info['filename'],
        'size': f'{info["size"]["bytes"]} bytes ({info["size"]["humansize"]})',
        'duration': str(info['duration']),
        'video': _format_video_header(info['video']),
    }

def _format_video_header(info):
    """Given the video portion of the header format it in a human readable string"""
    return f'{info["codec"]}, {info["pixel_format"]}, {info["width"]}x{info["height"]}, {info["fps"]} fps'

def human_readable_header_info_to_str(info):
    """Convert the human readable header into a string for outputting to the image"""
    return "File: {}\nSize: {}, Duration: {}, Avg.bitrate: {}\nVideo: {}".format(info['filename'],
                                                                                 info['size'],
                                                                                 info['duration'],
                                                                                 info['avg.bitrate'],
                                                                                 info['video'])
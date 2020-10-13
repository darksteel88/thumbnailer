import datetime
import os
import sys

from pprint import pprint

from lib import innput # avoid name clash on reserved keyword
from lib import folder
from lib import video
from lib import logger
from lib import image
from lib import helpers

ARGS = innput.get_argparse_input()

def should_skip(video_file, file_counter):
    """Returns True/False based on whether we should skip the given video_file"""
    if ARGS.offset and file_counter < ARGS.offset:
        return True
    if ARGS.skip and folder.does_thumb_exist(video_file, ARGS.format, ARGS.suffix):
        return True
    return False

def generate_thumbnail(video_file):
    """Given a video file generate a thumbnail for it"""

    local_start = datetime.datetime.now()
    # we grab the header info regardless of whether we intend to place header info at the top or not
    # because it contains useful information like the duration that we're going to use regardless
    header_info = video.get_header_info(video_file)
    the_folder = folder.get_folder_from_file(video_file)
    start_pos, vframes_ratio = video.generate_individual_thumbnails(video_file,
                                                                    header_info['duration'].seconds,
                                                                    ARGS.rows * ARGS.columns,
                                                                    innput.get_output_width(ARGS.width, ARGS.columns, ARGS.gap),
                                                                    the_folder,
                                                                    ARGS.format,
                                                                    ARGS.multiprocessing)

    scale_ratio = ARGS.width / 1024 # TODO: I don't think this should be hardcoded
    if ARGS.timestamp:
        image.overlay_timestamps(start_pos, vframes_ratio, folder._get_thumbnail_list(the_folder), ARGS.overlay, scale_ratio)

    if ARGS.details:
        output_header_info = helpers.human_readable_header_info_to_str(helpers.human_readable_header_info(header_info))

    new_name = folder.get_thumbnail_filename(header_info['filename'], ARGS.suffix)

    image.save_thumbnail(the_folder,
                         new_name,
                         ARGS.format,
                         ARGS.columns,
                         ARGS.gap,
                         scale_ratio,
                         text=output_header_info)

    folder.delete_temp_thumbs(folder._get_thumbnail_list(the_folder))

    local_end = datetime.datetime.now()
    logger.log_individual_timer(ARGS.verbose, video_file, local_start, local_end)

def main():
    if ARGS.verbose: # we will have a global timer and an individual file timer in this case
        global_start = datetime.datetime.now()
    file_counter = 1
    video_files = folder.get_all_video_files(ARGS.input)

    for video_file in video_files:
        if should_skip(video_file, file_counter):
            logger.log_skipping(ARGS.verbose, video_file)
            continue
        logger.log_counter(ARGS.verbose, file_counter, len(video_files), video_file)
        generate_thumbnail(video_file)
        file_counter += 1

    if ARGS.verbose:
        global_end = datetime.datetime.now()
        logger.log_global_timer(ARGS.verbose, global_start, global_end)

if __name__ == '__main__':
    main()
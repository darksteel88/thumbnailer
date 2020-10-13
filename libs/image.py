import datetime
import os

from PIL import Image
from PIL import ImageDraw
from PIL import  ImageFont

from . import folder

def overlay_timestamps(initial, difference, files, position, scale_ratio):
    """Given an initial frame starting time, a difference between timestamps on screens
    and a list of the corresponding files on disk
    Overlay the timestamp on the files and save them"""

    start = datetime.timedelta(seconds=initial)
    draw_timestamp(str(start), files[0], position, scale_ratio)
    for i in range(len(files) - 1):
        cur = datetime.timedelta(seconds=((i+1) * difference) + initial)
        draw_timestamp(str(cur), files[i + 1], position, scale_ratio)

def draw_timestamp(time_str, f, position, scale_ratio):
    """Given a timestamp string and a file
    draw the string on the file and save it
    the string is drawn according to the position:
    tl - top left
    tr - top right
    bl - bottom left
    br - bottom right"""

    img = Image.open(f)
    draw = ImageDraw.Draw(img)
    font_size = int(20 * scale_ratio)
    font = ImageFont.truetype('arial.ttf', font_size)
    x, y = determine_overlay_position(position, font, time_str, img)
    draw.text((x, y), time_str, (255,255,255), font=font)
    img.save(f)

def determine_overlay_position(position, font, text, image):
    """Given an image, a font, the text for the font, and the position to overlay it to
    return the x,y coordinates to place the text on the image"""

    x = 0
    y = 0

    if position[0] == 't':
        y = 0
    if position[0] == 'b':
        y = _determine_bottom_overlay_position(font, text, image)

    if position[1] == 'l':
        x = 0
    if position[1] == 'r':
        x = _determine_right_overlay_position(font, text, image)

    return x, y

def _determine_bottom_overlay_position(font, text, image):
    return image.size[1] - font.getsize(text)[1]

def _determine_right_overlay_position(font, text, image):
    return image.size[0] - font.getsize(text)[0]

def save_thumbnail(the_folder, name, file_format, columns=4, gap=0, scale_ratio=1, text=None):
    thumbnail_files = folder._get_thumbnail_list(the_folder)
    images = [Image.open(x) for x in thumbnail_files]
    widths, heights = zip(*(i.size for i in images))

    x_offset = gap
    y_offset = gap
    row_counter = 0

    total_width = int((widths[0] * columns) + (gap * (columns+1)))

    # validate that the number of images we have will fit into our columns
    # rows can get determined based on columns and num images
    if len(images) % columns != 0:
        raise ValueError("Mismatch on column number for image set provided")
    rows = len(images) / columns
    total_height = int((rows * heights[0]) + (gap * (rows+1)))

    # if we decide to put text at the top, add space for it and offset our starting position
    if text:
        font_size = int(20 * scale_ratio)
        y_offset += _get_header_height(font_size)
        total_height += y_offset

    new_image = Image.new('RGB', (total_width, total_height))

    for img in images:
        new_image.paste(img, (x_offset, y_offset))
        x_offset += widths[0] + gap
        row_counter += 1
        if row_counter % columns == 0:
            y_offset += heights[0] + gap
            x_offset = gap

    if text:
        draw = ImageDraw.Draw(new_image)
        font = ImageFont.truetype("arial.ttf", font_size)
        draw.text((0, 0), text, (255, 255, 255), font=font)

    new_image.save(os.path.join(the_folder,'{}.{}'.format(name, file_format)))

def _get_header_height(font_size):
    """Get the height we have to append to the image that we label as the black area for the header text"""
    # the size we return is 3 times bigger padded up to 10
    res = font_size * 3
    res += (10 - (res % 10))
    return res
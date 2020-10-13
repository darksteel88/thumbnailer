import argparse

def get_argparse_input():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='The root folder to look for video files', required=True)
    parser.add_argument('-c', '--columns', help='The number of columns in the output, defaults to 4', default=4, type=int)
    parser.add_argument('-r', '--rows', help='The number of rows in the output, defaults to 8', default=8, type=int)
    parser.add_argument('-d', '--details', help='If specified will add video details at the top', action='store_true')
    parser.add_argument('-t', '--timestamp', help='If specified will include timestamps on the tiles', action='store_false', default=True)
    parser.add_argument('-g', '--gap', help='The gap between tiles, defaults to 1', default=1,  type=int)
    parser.add_argument('-f', '--format', help='The format to output the file to, defaults to jpg', default='jpg')
    parser.add_argument('-s', '--suffix', help='Output name is the original name with the suffix appended', default='_thumb')
    parser.add_argument('-w', '--width', help='The width of the final image, defaults to 1024', default=1024, type=int)
    parser.add_argument('-op', '--overlay', help='The position of the timestamp overlay, tl, tr, bl, br', default='br')
    parser.add_argument('-v', '--verbose', help='Add verbose logging to the console', action='store_true', default=False)
    parser.add_argument('-mp', '--multiprocessing', help='Use multiprocessing to speed up screen generation', action='store_true', default=False)
    parser.add_argument('-os', '--offset', help='Offset where you start in the folder, i.e. start at file 10', default=0, type=int)
    parser.add_argument('-sk', '--skip', help='Skip creating thumbnails if the thumbnail already exists', default=False, action='store_true')
    return parser.parse_args()

def get_output_width(width, columns, gap):
    return (width - (gap * columns)) // columns

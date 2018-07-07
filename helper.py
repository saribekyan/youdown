import sys
import os
import re

from consts import *

def video_id(link):
    vid = link[-11:]

    if vid != re.search('[a-zA-Z0-9_-]+', vid).group(0):
        print("Bad link: %s" % link)
        sys.exit(0)
    return vid

def normalise_path(path, audio_only):
    base_path = AUDIO_HOME if audio_only else VIDEO_HOME
    if path == None:
        path = base_path
    elif path[0] == '/':
        pass
    elif path[0] == '~':
        path = os.path.expanduser(path)
    else:
        path = os.path.join(base_path, path)

    if not os.path.isdir(path):
        print("Path does not exist or is not a directory: %s" % path)
        sys.exit(0)
    return path

def id_to_link(vid):
    return "https://www.youtube.com/watch?v=" + vid


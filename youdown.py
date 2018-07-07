import sys
import argparse
import os
import os.path
import re
import pytube
import urllib

import defaults as defs

def init():
    defs.audio_home = os.path.expanduser(defs.audio_home)
    if defs.audio_home[0] != '/':
        print('Provide absolute path for the audio home directory')

    defs.video_home = os.path.expanduser(defs.video_home)
    if defs.video_home[0] != '/':
        print('Provide absolute path for the video home directory')

    defs.future_links = os.path.expanduser(defs.future_links)
    if defs.future_links[0] != '/':
        defs.future_links = os.path.join(os.path.dirname(os.path.abspath(__file__)), defs.future_links)
        with open(defs.future_links, 'a') as f:
            # if the file didn't exist it got created
            pass

def video_id(link):
    vid = link[-11:]

    if vid != re.search('[a-zA-Z0-9_-]+', vid).group(0):
        print("Bad link: %s" % link)
        sys.exit(0)
    return vid

def normalise_path(path, audio_only):
    base_path = defs.audio_home if audio_only else defs.video_home
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

def to_yt_link(vid):
    return "https://www.youtube.com/watch?v=" + vid

def download_video(vid, audio_only, path):
    print(('Downloading %s to %s' % (vid, path)) + ('; audio only' if audio_only else ''))
    try:
        yt = pytube.YouTube(to_yt_link(vid))
    except urllib.error.URLError as e:
        print("URLError from pytube - no internet? See error log.")
        with open('error-log.txt', 'w') as errlog:
            errlog.write(repr(e))
        return

    title = yt.title

    if audio_only:
        stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
    else:
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()

    stream.download(path)

    with open(defs.past_links, 'a') as f:
        f.write(str((vid, audio_only, path, title)) + '\n')

def get_now(link, audio_only, path):
    vid = video_id(link)
    path = normalise_path(path, audio_only)

    download_video(vid, audio_only, path)

def add_link(link, audio_only, path):
    vid = video_id(link)
    path = normalise_path(path, audio_only)

    with open(defs.future_links, 'a') as links_f:
        links_f.write(str((vid, audio_only, path)) + '\n')

def get_all(down_audios):
    with open(defs.future_links, 'r') as links_f:
        to_download = links_f.readlines()

    is_down = [ ]
    for l in to_download:
        (vid, audio_only, path) = eval(l)
        if not down_audios or audio_only:
            download_video(vid, audio_only, path)
            is_down.append(True)
        else:
            print('Skipping %s as it is not oudio_only' % vid)
            is_down.append(False)

    with open(defs.future_links, 'w') as links_f:
        for i in len(xrange(is_down)):
            if not is_down[i]:
                links_f.write(to_download[i])

if __name__ == '__main__':
    init()

    parser = argparse.ArgumentParser(
            description='Download audio or video files from Youtube.',
            usage='python youdown.py <command> [<args>]')

    parser.add_argument(
            'command',
            help='The command to execute with its arguments (one of: get-all, add, get-now).')

    command = parser.parse_args(sys.argv[1:2]).command

    if command == 'get-all':
        parser = argparse.ArgumentParser(
                description='Download all videos in the future downloads list.',
                usage='get-all [--audios]')

        parser.add_argument(
                '-a',
                '--audios',
                action='store_true',
                default=False,
                help='Download only the links that have the audio-only flag set.')

        args = parser.parse_args(sys.argv[2:])

        get_all(args.audios)

    elif command == 'get-now' or command == 'add-link':
        parser = argparse.ArgumentParser(
                description='Get the link immediately.' if command == 'get-now' else 'Add the link to the list of future donwloads.',
                usage=('%s link [path] [-a/--audio-only]' % command))

        parser.add_argument(
                'link',
                help='A link to a YouTube video')

        parser.add_argument(
                'path',
                nargs='?',
                help='''The path to the download location.
If starts with \'/\' or ~, means non-relative to the default A/V directory.
Otherwise the path relative to the default directory''')

        parser.add_argument(
                '-a',
                '--audio-only',
                action='store_true',
                default=False,
                help='Download audio only.')

        args = parser.parse_args(sys.argv[2:])

        if command == 'get-now':
            get_now(args.link, args.audio_only, args.path)
        else:
            add_link(args.link, args.audio_only, args.path)

    else:
        print('Unrecognised command, see help.')


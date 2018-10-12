import sys
import argparse
import os
import os.path
import re
import pytube
import urllib
import shutil
import time

from consts import *
from helper import *


def download_video(vid, audio_only, path):
    try:
        yt = pytube.YouTube(id_to_link(vid))
    except urllib.error.URLError as e:
        print("URLError from pytube - no internet? See error log.")
        with open('error-log.txt', 'w') as errlog:
            errlog.write(repr(e))
        return

    title = yt.title
    print(('Downloading %s (vid: %s) to %s' % (title, vid, path)) + ('; audio only' if audio_only else ''))

    ##### HACKY PROGRESS BAR LOGIC
    stream_size = 0
    progress = 0
    perc = 1
    start_t = 0
    def show_progress_bar(stream, chunk, file_handle, bytes_remaining):
        nonlocal stream_size, progress, perc, start_t
        if stream_size == 0:
            stream_size = bytes_remaining
            start_t = time.time()

            print('Downloading %.1fmb' % (stream_size / (2.0**20)))
        progress += len(chunk)
        if progress > perc * stream_size / 100.0:
            elapsed = time.time() - start_t
            rate = progress * 1.0 / elapsed
            remain = bytes_remaining / rate

            sys.stdout.write('\r')
            sys.stdout.write('[%-50s] %d%% [elapsed: %.1fs remain: %.1fs rate: %dkb/s]' %
                    ('#'*(perc >> 1), perc, elapsed, remain,
                    progress / (2.0**10) / elapsed))
            sys.stdout.flush()

            perc += 1
        if bytes_remaining == 0:
            print()
    #######

    yt.register_on_progress_callback(show_progress_bar)

    if audio_only:
        stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
    else:
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()

    stream.download(path)

    # the stuff below should actually be in on_download_complete callback

    if audio_only:
        if shutil.which('ffmpeg') is not None:
            fpath = os.path.join(path, title + '.mp4')
            if os.path.exists(fpath):
                print('Converting %s from mp4 to mp3' % title)
                opath = os.path.join(path, title + '.mp3')
                os.system('ffmpeg -i "%s" "%s" -v 0' % (fpath, opath))
        else:
            print('ffmpeg is not installed; otherwise would convert %s from mp4 to mp3' % title)

    with open(PAST_LINKS, 'a') as f:
        f.write(str((vid, audio_only, path, title)) + '\n')

def get_now(link, audio_only, path):
    vid = video_id(link)
    path = normalise_path(path, audio_only)

    download_video(vid, audio_only, path)

def add_link(link, audio_only, path):
    vid = video_id(link)
    path = normalise_path(path, audio_only)

    with open(FUTURE_LINKS, 'a') as links_f:
        links_f.write(str((vid, audio_only, path)) + '\n')

    print('Link %s is added to the future downloads (audio=%s,path=%s)' % (vid, str(audio_only), path)) 

def get_all(down_audios):
    with open(FUTURE_LINKS, 'r') as links_f:
        links = links_f.readlines()

    is_down = [ ]
    for l in links:
        (vid, audio_only, path) = eval(l)

        if not down_audios or audio_only:
            is_down.append(True)
        else:
            is_down.append(False)

    n_down = sum(is_down)
    print('Downloading %d links out of %d.' % (n_down, len(links)))

    links_f = open(FUTURE_LINKS, 'w')

    c_down = 1
    for i in range(len(is_down)):
        (vid, audio_only, path) = eval(links[i])

        if is_down[i]:
            print('Downloading %d/%d.' % (c_down, n_down))
            download_video(vid, audio_only, path)
            c_down += 1
        else:
            print('Skipping %s as its audio_only flag is not set.' % vid)
            links_f.write(str((vid, audio_only, path)) + '\n')

    links_f.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Download audio or video files from Youtube.',
            usage='python youdown.py <command> [<args>]')

    parser.add_argument(
            'command',
            help='The command to execute with its arguments (one of: get-all, add-link, get-now).')

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


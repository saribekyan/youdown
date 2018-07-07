######################
# constants - modify when setting up

VIDEO_HOME = '~/Videos'
AUDIO_HOME = '~/Audio'

# unless other paths are given, these files will be next to the scripts
FUTURE_LINKS = 'future-downloads.txt'
PAST_LINKS   = 'past-downloads.txt'

######################
# USER: do not modify below
# cleaning up the paths, making them absolute

import os

AUDIO_HOME = os.path.expanduser(AUDIO_HOME)
if AUDIO_HOME[0] != '/':
    print('Provide absolute path for the audio home directory')
    sys.exit(0)

VIDEO_HOME = os.path.expanduser(VIDEO_HOME)
if VIDEO_HOME[0] != '/':
    print('Provide absolute path for the video home directory')
    sys.exit(0)

FUTURE_LINKS = os.path.expanduser(FUTURE_LINKS)
if FUTURE_LINKS[0] != '/':
    FUTURE_LINKS = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            FUTURE_LINKS)
    with open(FUTURE_LINKS, 'a') as f:
        pass

PAST_LINKS = os.path.expanduser(PAST_LINKS)
if PAST_LINKS[0] != '/':
    PAST_LINKS = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            PAST_LINKS)
    with open(PAST_LINKS, 'a') as f:
        pass


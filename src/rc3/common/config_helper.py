import os
import re

DEFAULT_CONFIG_FOLDER = '.rc'
RC_HOME = 'RC_HOME'


def get_config_folder():
    rc_home = os.getenv(RC_HOME)
    if rc_home is None:
        home = os.path.expanduser("~")
        rc_home = os.path.join(home, DEFAULT_CONFIG_FOLDER)
    if not os.path.exists(rc_home):
        os.mkdir(rc_home)
    return rc_home


def clean_filename(name):
    if name is None:
        return None
    name = name.lower()
    name = re.sub(' ', '_', name)
    name = re.sub('[^a-zA-Z0-9_-]', '', name)
    return name

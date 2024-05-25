import os
import re

from rc3.common import data_helper
from rc3.common.data_helper import SETTINGS_FILENAME, GLOBAL_ENV_FILENAME
from rc3.common.decorators import rc_print_durations

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


@rc_print_durations
def init_rc_home():
    # Note: this next cmd will always create RC_HOME / ~/.rc if it doesn't exist
    home = get_config_folder()

    dest = os.path.join(home, SETTINGS_FILENAME)
    if not os.path.exists(dest):
        # print("Creating " + dest)
        data_helper.copy('home/' + SETTINGS_FILENAME, dest)

    dest = os.path.join(home, GLOBAL_ENV_FILENAME)
    if not os.path.exists(dest):
        # print("Creating " + dest)
        data_helper.copy('home/' + GLOBAL_ENV_FILENAME, dest)

    dest = os.path.join(home, 'schemas')
    if not os.path.exists(dest):
        # print("Creating " + dest)
        data_helper.copy_tree('home/schemas', dest)

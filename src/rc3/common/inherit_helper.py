import json
import os
import re
import click

from rc3.common import json_helper, print_helper
from rc3.common.data_helper import FOLDER_FILENAME, COLLECTION_FILENAME


def find_auth(wrapper):
    r = wrapper.get('_original')
    if r.get('auth', {}).get('type','inherit') != 'inherit':
        return r.get('auth')
    auth = walk_up_folders(wrapper.get('_dir'))
    # print_helper.print_json(auth)
    return auth


def walk_up_folders(_dir):
    collection_filename = os.path.join(_dir, COLLECTION_FILENAME)
    if os.path.exists(collection_filename):
        # we;re at the root of the collection stop walking & return something!
        c, wrapper = json_helper.read_current_collection()
        if c.get('auth',{}).get('type','inherit') != 'inherit':
            return c.get('auth')
        else:
            return {
                "type": "none"
            }

    folder_filename = os.path.join(_dir, FOLDER_FILENAME)
    if os.path.exists(folder_filename):
        folder = json_helper.load_and_validate(FOLDER_FILENAME, _dir=_dir)
        if folder.get('auth',{}).get('type','inherit') == 'inherit':
            # RECURSIVE walk_up_folders!
            return walk_up_folders(os.path.join(_dir, os.pardir))
        else:
            return folder.get('auth')

    # RECURSIVE walk_up_folders!
    return walk_up_folders(os.path.join(_dir, os.pardir))

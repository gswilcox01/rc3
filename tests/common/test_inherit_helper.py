import os
import re

import pytest
from click import ClickException

from rc3 import cli
from rc3.common import json_helper, print_helper, env_helper, inherit_helper
from rc3.common.data_helper import FOLDER_FILENAME
from tests.commands import test_request


def auth_remove():
    return {}


def auth_none():
    return {
        "type": "none"
    }


def auth_inherit():
    return {
        "type": "inherit"
    }


def auth_basic():
    return {
        "type": "basic",
        "username": "gary",
        "password": "is-cool"
    }


def auth_bearer():
    return {
        "type": "bearer",
        "bearer_token": "ABCDEFGHIJKLMNOPQRSTUVWXY..."
    }


def set_collection(auth):
    c, wrapper = json_helper.read_current_collection()
    c['auth'] = auth
    json_helper.write_collection(wrapper)


def set_folder(auth, _dir=None):
    if _dir is None:
        r, wrapper = test_request.lookup_current()
        _dir = wrapper['_dir']
    full_filename = os.path.join(_dir, FOLDER_FILENAME)
    folder = {}
    if os.path.exists(full_filename):
        folder = json_helper.load_and_validate(FOLDER_FILENAME, _dir=_dir)

    folder['auth'] = auth
    json_helper.write_json(full_filename, folder)


def delete_folder(_dir=None):
    if _dir is None:
        r, wrapper = test_request.lookup_current()
        _dir = wrapper['_dir']
    full_filename = os.path.join(_dir, FOLDER_FILENAME)
    if os.path.exists(full_filename):
        os.remove(full_filename)


def set_request(auth):
    r, wrapper = test_request.lookup_current()
    r['auth'] = auth
    json_helper.write_request(r, wrapper)


def test_stops_at_request_none(example_collection, runner):
    set_request(auth_none())
    set_folder(auth_basic())
    set_collection(auth_basic())

    r, wrapper = test_request.lookup_current()
    auth = inherit_helper.find_auth(wrapper)

    assert auth.get('type') == "none"


def test_stops_at_folder_basic(example_collection, runner):
    set_request(auth_remove())
    set_folder(auth_basic())
    set_collection(auth_bearer())

    r, wrapper = test_request.lookup_current()
    auth = inherit_helper.find_auth(wrapper)

    assert auth.get('type') == "basic"


def test_follows_explicit_inherit(example_collection, runner):
    set_request(auth_inherit())
    set_folder(auth_inherit())
    set_collection(auth_bearer())

    r, wrapper = test_request.lookup_current()
    auth = inherit_helper.find_auth(wrapper)

    assert auth.get('type') == "bearer"


def test_follows_implicit_inherit(example_collection, runner):
    set_request(auth_remove())
    set_folder(auth_remove())
    set_collection(auth_bearer())

    r, wrapper = test_request.lookup_current()
    auth = inherit_helper.find_auth(wrapper)

    assert auth.get('type') == "bearer"


def test_follows_missing_folder(example_collection, runner):
    set_request(auth_inherit())
    delete_folder()
    set_collection(auth_bearer())

    r, wrapper = test_request.lookup_current()
    auth = inherit_helper.find_auth(wrapper)

    assert auth.get('type') == "bearer"


def test_stops_at_collection(example_collection, runner):
    set_request(auth_inherit())
    set_folder(auth_inherit())
    set_collection(auth_inherit())

    r, wrapper = test_request.lookup_current()
    auth = inherit_helper.find_auth(wrapper)

    assert auth.get('type') == "none"



import copy
import json
import os
import sys
from datetime import datetime
from json import JSONDecodeError

import click
from funcy import print_durations
from jsonschema import Draft7Validator
from referencing import Registry, Resource
from rc3.common import config_helper, data_helper, print_helper
from rc3.common.data_helper import SCHEMA_PREFIX, SCHEMA_VERSION, COLLECTION_FILENAME, SETTINGS_FILENAME, \
    FOLDER_FILENAME, GLOBAL_ENV_FILENAME, KEYRING_FILENAME
from rc3.common.decorators import rc_print_durations, rc_memoized


def guess_schema(filename):
    if filename == COLLECTION_FILENAME:
        return 'collection'
    if filename == SETTINGS_FILENAME:
        return 'settings'
    if filename == GLOBAL_ENV_FILENAME:
        return 'environment'
    if filename == FOLDER_FILENAME:
        return 'folder'
    if filename == KEYRING_FILENAME:
        return 'keyring'
    if filename.endswith('.request'):
        return 'request'
    # default, because it's the only one that can't be guessed based on filename
    return 'environment'


@rc_print_durations
@rc_memoized
def guess_dir(filename):
    home = config_helper.get_config_folder()
    # if filename in [SETTINGS_FILENAME, GLOBAL_ENV_FILENAME]:
    #     return home
    if filename in os.listdir(home):
        return home

    current_collection = find_current_collection()
    current_location = current_collection.get('location', None) or None
    if current_location is None:
        return None
    for dirpath, dirnames, files in os.walk(current_location):
        if filename in files:
            return dirpath

    if filename.endswith(".json"):
        return os.path.join(current_location, "environments")

    return None


@rc_print_durations
@rc_memoized
# @rc_memoized
def create_registry():
    # TODO: do i even need a registry any more, rc3-auth refs are no longer relative...
    # Registry is only needed for relative refs ($ref) in schemas (and we only have 1 to begin with)
    # All the full document schemas will be loaded individually when used
    registry = Registry()
    loaded = read_schema('auth')
    resource = Resource.from_contents(loaded)
    filename = data_helper.get_schema_filename('auth')
    registry = registry.with_resource(f"./{filename}", resource)
    return registry


def load_and_validate(filename, schema=None, _dir=None):
    # print("LOAD AND VALIDATE: " + filename)
    # if schema=None, guess based on filename
    if schema is None:
        schema = guess_schema(filename)
        # print(f'filename=[{filename}, schema=[{schema}]')

    # if _dir=None, look for filename in RC_HOME, or current_collection
    if _dir is None:
        _dir = guess_dir(filename)

    file = os.path.join(_dir, filename)
    if not os.path.exists(file):
        raise click.ClickException("Can't find: " + filename)

    _dict = read_json(file)
    schema_dict = read_json(data_helper.get_schema_file(schema))
    # print(schema_dict)

    # This PDF seemed better than the web docs for jsonschema:
    # https://readthedocs.org/projects/python-jsonschema/downloads/pdf/latest/
    validator = Draft7Validator(schema_dict, registry=create_registry())

    validator.check_schema(schema_dict)
    if validator.is_valid(_dict):
        return _dict

    print()
    print("Error: file doesn't pass JSON schema validation: " + file)
    # print(filename + " is invalid:")
    for error in validator.iter_errors(_dict):
        # print(vars(error)) # use to look at what other attributes are available...
        # print(vars(error))
        path = [s if isinstance(s, str) else f'[{s}]' for s in error.path]
        print(" * json path: /" + '.'.join(path))
        print(" * error: " + error.message)
    print("If needed, please use VSCode to see validation errors w/ squiggles & hovers")
    sys.exit()


def validate(_dict, schema=None):
    if schema is None:
        schema = 'request'

    schema_dict = read_json(data_helper.get_schema_file(schema))
    validator = Draft7Validator(schema_dict, registry=create_registry())

    validator.check_schema(schema_dict)
    if validator.is_valid(_dict):
        return _dict

    print("JSON is invalid: " + schema)
    for error in validator.iter_errors(_dict):
        # print(vars(error)) # use to look at what other attributes are available...
        print(" * json path: /" + '.'.join(error.path))
        print(" * error: " + error.message)
    print("If needed, please use VSCode to see validation errors w/ squiggles & hovers")
    sys.exit()


# @rc_print_durations
# def validate_schemas():
#     check_schema(data_helper.get_schema_file('auth'))
#     check_schema(data_helper.get_schema_file('collection'))
#     check_schema(data_helper.get_schema_file('environment'))
#     check_schema(data_helper.get_schema_file('folder'))
#     check_schema(data_helper.get_schema_file('request'))
#     check_schema(data_helper.get_schema_file('settings'))
#
#
# def check_schema(_file):
#     _dict = read_json(_file)
#     validator = Draft7Validator(_dict, registry=create_registry())
#     validator.check_schema(_dict)


@rc_memoized
def read_schema(partial_name):
    _file = data_helper.get_schema_file(partial_name)
    return read_json(_file)


def read_json(filename):
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except JSONDecodeError as e:
        print()
        print(type(e).__name__ + " " + str(e))
        raise click.ClickException("unable to load file as JSON: " + filename)


def read_json_or_none(filename):
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except JSONDecodeError as e:
        return None


def parse_json(json_string):
    try:
        _json = json.loads(json_string)
    except ValueError:  # includes simplejson.decoder.JSONDecodeError
        return None
    return _json


def write_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


@rc_print_durations
@rc_memoized
def read_settings():
    home = config_helper.get_config_folder()
    return load_and_validate(SETTINGS_FILENAME, _dir=home)


def write_settings(settings):
    home = config_helper.get_config_folder()
    write_json(os.path.join(home, SETTINGS_FILENAME), settings)


@rc_print_durations
@rc_memoized
def read_keyring():
    home = config_helper.get_config_folder()
    return load_and_validate(KEYRING_FILENAME, _dir=home)


def write_keyring(keyring_history):
    home = config_helper.get_config_folder()
    write_json(os.path.join(home, KEYRING_FILENAME), keyring_history)


@rc_print_durations
@rc_memoized
def find_current_collection():
    settings = load_and_validate(SETTINGS_FILENAME)
    current_name = settings.get('current_collection', None) or None
    collections = settings.get('collections', None) or None
    if current_name is None or collections is None:
        return None

    for c in collections:
        if c['name'] == current_name:
            return c
    return None


@rc_print_durations
@rc_memoized
def read_current_collection():
    current = find_current_collection()
    if current is None:
        return None, None
    c = load_and_validate(COLLECTION_FILENAME, _dir=current['location'])
    return c, {
        '_dir': current['location'],
        '_original': c
    }


def read_collection(_dir=None):
    if _dir is None:
        _dir = os.getcwd()
    c = load_and_validate(COLLECTION_FILENAME, _dir=_dir)
    return c, {
        '_dir': _dir,
        '_original': c
    }


def write_collection(wrapper):
    location = wrapper['_dir']
    write_json(os.path.join(location, COLLECTION_FILENAME), wrapper['_original'])


@rc_print_durations
@rc_memoized
def read_request_list():
    c, c_wrapper = read_current_collection()
    start = c_wrapper['_dir']
    current_request = c.get('current_request', "")
    _list = []
    number = 0
    for root, dirs, files in os.walk(start):
        dirs.sort()
        for file in sorted(files):
            if root.endswith('examples'):
                continue
            if file.endswith('.request'):
                number = number + 1
                display_num = str(number)

                short_file = file.split('.')[0]
                short_path = root.replace(start, "")
                short_path = short_path.replace("\\", "/")
                short_request = short_path + "/" + file
                current = False

                if short_request == current_request:
                    current = True
                    display_num += '*'

                # read each request to get the METHOD
                r = load_and_validate(file, _dir=root)
                method = r.get('method', '')

                # edit path further for display
                if len(short_path) > 49:
                    short_path = ".../" + short_path[-46]

                _list.append({
                    '_index': number - 1,
                    '_current': current,
                    '_dir': root,
                    '_filename': file,
                    '_original': r,
                    '_display_ref': str(number) + ":" + short_request,
                    '_short_request': short_request,
                    'number': number,
                    'display_num': display_num,
                    'folder': short_path,
                    'method': method,
                    'name': short_file
                })
    return _list


@rc_print_durations
@rc_memoized
def read_environment_list():
    c, c_wrapper = read_current_collection()
    env_folder = os.path.join(c_wrapper['_dir'], 'environments')
    _list = []
    idx = 0
    for root, dirs, files in os.walk(env_folder):
        dirs.sort()
        for file in sorted(files):
            if file.endswith('.json'):
                env = load_and_validate(file, _dir=root)
                name = file.split('.')[-2]
                idx = idx + 1
                number = str(idx)

                current = False
                if name == c['current_environment']:
                    current = True
                    number += '*'
                _list.append({
                    '_index': idx - 1,
                    '_current': current,
                    '_dir': root,
                    '_filename': file,
                    '_original': env,
                    'name': file.split('.')[-2],
                    'number': idx,
                    'display_num': number,
                    'baseUrl': env.get('baseUrl', 'None')
                })
    return _list


@rc_print_durations
@rc_memoized
def read_collection_list():
    settings = read_settings()
    current_c = find_current_collection()
    _list = []
    for idx, c in enumerate(settings.get('collections', [])):
        number = str(idx + 1)
        current = False
        if c['name'] == current_c['name']:
            current = True
            number += '*'

        _list.append({
            '_index': idx,
            '_current': current,
            'number': str(idx+1),
            'display_num': number,
            'name': c['name'],
            'location': c['location']
        })
    return _list


@rc_print_durations
@rc_memoized
def read_keyring_entry_list():
    keyring_history = read_keyring()
    entries = copy.deepcopy(keyring_history['entries'])
    _list = sorted(entries, key=lambda e: e['name'])

    idx = 0
    for entry in _list:
        idx = idx + 1
        number = str(idx)
        # if current:
        # current = True
        # number += '*'
        entry['_index'] = idx - 1
        entry['number'] = number
        entry['display_num'] = number
        entry['display_created'] = datetime.fromisoformat(entry['created']).strftime("%x %X") if "created" in entry else "-"
        entry['display_accessed'] = datetime.fromisoformat(entry['accessed']).strftime("%x %X") if "accessed" in entry else "-"
        entry['display_modified'] = datetime.fromisoformat(entry['modified']).strftime("%x %X") if "modified" in entry else "-"
    return _list


@rc_print_durations
@rc_memoized
def read_environment(name):
    c, c_wrapper = read_current_collection()
    env_folder = os.path.join(c_wrapper['_dir'], 'environments')
    if name == 'current':
        name = c['current_environment']
    if name == 'global':
        name = 'rc-global'
        env_folder = config_helper.get_config_folder()
    env_filename = name+'.json'
    env = load_and_validate(env_filename, _dir=env_folder)
    return env_filename, env


def write_environment(filename, data):
    if filename == SETTINGS_FILENAME:
        raise click.ClickException("WTF?  Contact Gary, code is trying to write rc-settings as an environment!")
    _dir = guess_dir(filename)
    write_json(os.path.join(_dir, filename),
               data)


def write_request(r, wrapper):
    path = os.path.join(wrapper.get('_dir'), wrapper.get('_filename'))
    write_json(path, r)



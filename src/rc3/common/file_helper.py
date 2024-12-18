import json
from json import JSONDecodeError

import click

state = {
    'has_file': False,
    'consumed': False,
    '_json': None,
    '_text': None
}


def reset_for_test():
    state['has_file'] = False
    state['consumed'] = False
    state['_json'] = None
    state['_text'] = None


def preprocess_file_option(file):
    if file is not None:
        state['has_file'] = True
        state['_json'] = read_as_json(file)
        if state['_json'] is None:
            state['_text'] = read_as_text(file)


def read_as_json(file):
    try:
        with click.open_file(file) as f:
            return json.load(f)
    except JSONDecodeError as e:
        return None


def read_as_text(file):
    with click.open_file(file) as f:
        return f.read()


def consume_as_string():
    state['consumed'] = True
    if state['_json'] is not None:
        return json.dumps(state['_json'])
    return state['_text']

import os
import re

import pytest
from click import ClickException

from rc3 import cli
from rc3.common import json_helper, print_helper, env_helper
from tests.commands import test_request


def add_to_current(var, value):
    env_filename, env = json_helper.read_environment('current')
    env[var] = value
    json_helper.write_environment(env_filename, env)


def add_to_global(var, value):
    env_filename, env = json_helper.read_environment('global')
    env[var] = value
    json_helper.write_environment(env_filename, env)


def add_to_shell(var, value):
    os.environ[var] = value


def test_subbing_all_spots(example_collection, runner):
    r, wrapper = test_request.lookup_current()
    r['form_data'] = {
        "something": "{{ bob }}"
    }
    r['headers']["another"] = "{{ bob }}"
    r['params']["more"] = "{{ bob }}"
    r['auth']["username"] = "{{ bob }}"
    r['url'] = "{{ bob }}"
    r['body'] = {
        'text': "{{ bob }}",
        'json': {
            "some": "{{ bob }}",
            "more": "{{ bob }}"
        }
    }
    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 8
    assert len(re.findall(r'current_bob', json_string)) == 0
    add_to_current("bob", "current_bob")

    env_helper.process_subs(wrapper)
    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 0
    assert len(re.findall(r'current_bob', json_string)) == 8


def test_sub_current(example_collection, runner):
    r, wrapper = test_request.lookup_current()
    r['auth']["username"] = "{{ bob }}"

    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 1
    assert len(re.findall(r'current_bob', json_string)) == 0
    add_to_current("bob", "current_bob")

    env_helper.process_subs(wrapper)

    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 0
    assert len(re.findall(r'current_bob', json_string)) == 1


def test_sub_global(example_collection, runner):
    r, wrapper = test_request.lookup_current()
    r['auth']["username"] = "{{ bob }}"

    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 1
    assert len(re.findall(r'global_bob', json_string)) == 0
    add_to_global("bob", "global_bob")

    env_helper.process_subs(wrapper)

    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 0
    assert len(re.findall(r'global_bob', json_string)) == 1


def test_sub_shell(example_collection, runner):
    r, wrapper = test_request.lookup_current()
    r['auth']["username"] = "{{ bob }}"

    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 1
    assert len(re.findall(r'galactic_bob', json_string)) == 0
    add_to_shell("bob", "galactic_bob")

    env_helper.process_subs(wrapper)

    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 0
    assert len(re.findall(r'galactic_bob', json_string)) == 1


def test_missing_var(example_collection, runner):
    r, wrapper = test_request.lookup_current()
    r['auth']["username"] = "{{ missing_bob }}"

    with pytest.raises(ClickException, match=r'cannot be found in the current, global, or OS environment'):
        env_helper.process_subs(wrapper)


def test_current_wins(example_collection, runner):
    r, wrapper = test_request.lookup_current()
    r['auth']["username"] = "{{ bob }}"
    add_to_current("bob", "current_bob")
    add_to_global("bob", "global_bob")
    add_to_shell("bob", "galactic_bob")

    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 1
    assert len(re.findall(r'current_bob', json_string)) == 0
    assert len(re.findall(r'global_bob', json_string)) == 0
    assert len(re.findall(r'galactic_bob', json_string)) == 0

    env_helper.process_subs(wrapper)

    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 0
    assert len(re.findall(r'current_bob', json_string)) == 1
    assert len(re.findall(r'global_bob', json_string)) == 0
    assert len(re.findall(r'galactic_bob', json_string)) == 0


def test_global_wins(example_collection, runner):
    r, wrapper = test_request.lookup_current()
    r['auth']["username"] = "{{ bob }}"
    # add_to_current("bob", "current_bob")
    add_to_global("bob", "global_bob")
    add_to_shell("bob", "galactic_bob")

    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 1
    assert len(re.findall(r'current_bob', json_string)) == 0
    assert len(re.findall(r'global_bob', json_string)) == 0
    assert len(re.findall(r'galactic_bob', json_string)) == 0

    env_helper.process_subs(wrapper)

    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 0
    assert len(re.findall(r'current_bob', json_string)) == 0
    assert len(re.findall(r'global_bob', json_string)) == 1
    assert len(re.findall(r'galactic_bob', json_string)) == 0

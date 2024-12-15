import os
import re

import click
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


def test_recursive_sub(example_collection, runner):
    r, wrapper = test_request.lookup_current()
    r['auth']["username"] = "{{ bob }}"
    add_to_current("bob", "{{linda}}")
    add_to_current("linda", "miller")

    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 1
    assert len(re.findall(r'linda', json_string)) == 0
    assert len(re.findall(r'miller', json_string)) == 0

    env_helper.process_subs(wrapper)

    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 0
    assert len(re.findall(r'linda', json_string)) == 0
    assert len(re.findall(r'miller', json_string)) == 1


def test_3x_recursive_sub(example_collection, runner):
    r, wrapper = test_request.lookup_current()
    r['auth']["username"] = "{{ bob }}"
    add_to_current("bob", "{{linda}}")
    add_to_current("linda", "{{stacy}}")
    add_to_current("stacy", "Wilcox")

    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 1
    assert len(re.findall(r'linda', json_string)) == 0
    assert len(re.findall(r'stacy', json_string)) == 0
    assert len(re.findall(r'Wilcox', json_string)) == 0

    env_helper.process_subs(wrapper)

    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 0
    assert len(re.findall(r'linda', json_string)) == 0
    assert len(re.findall(r'stacy', json_string)) == 0
    assert len(re.findall(r'Wilcox', json_string)) == 1


def test_double_sub(example_collection, runner):
    r, wrapper = test_request.lookup_current()
    r['auth']["username"] = "{{ bob }} {{ linda }}"
    add_to_current("bob", "Miller")
    add_to_current("linda", "Indermuehle")

    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 1
    assert len(re.findall(r'linda', json_string)) == 1
    assert len(re.findall(r'Miller', json_string)) == 0
    assert len(re.findall(r'Indermuehle', json_string)) == 0

    env_helper.process_subs(wrapper)

    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 0
    assert len(re.findall(r'linda', json_string)) == 0
    assert len(re.findall(r'Miller Indermuehle', json_string)) == 1


def test_infinite_loop_sub(example_collection, runner):
    r, wrapper = test_request.lookup_current()
    r['auth']["username"] = "{{ bob }}"
    add_to_current("bob", "{{linda}}")
    add_to_current("linda", "{{bob}}")

    json_string = print_helper.get_json_string(r)
    assert len(re.findall(r'{{ bob }}', json_string)) == 1
    assert len(re.findall(r'linda', json_string)) == 0
    assert len(re.findall(r'miller', json_string)) == 0

    with pytest.raises(click.exceptions.ClickException) as exception_info:
        env_helper.process_subs(wrapper)

    assert "has caused an infinite loop during lookup" in str(exception_info.value)


def test_3x_recursive_loop_caught(example_collection, runner):
    r, wrapper = test_request.lookup_current()
    r['auth']["username"] = "{{ bob }}"
    add_to_current("bob", "{{linda}}")
    add_to_current("linda", "{{stacy}}")
    add_to_current("stacy", "{{bob}}")

    with pytest.raises(click.exceptions.ClickException) as exception_info:
        env_helper.process_subs(wrapper)

    assert "has caused an infinite loop during lookup" in str(exception_info.value)


def test_lookup_one(example_collection, runner):
    add_to_current("my", "mom")
    add_to_global("my", "dad")
    add_to_shell("my", "grandma")

    r = env_helper.lookup_one_var("my")
    assert r == "mom"


def test_lookup_one_global(example_collection, runner):
    add_to_global("my", "dad")
    add_to_shell("my", "grandma")

    r = env_helper.lookup_one_var("my")
    assert r == "dad"


def test_lookup_one_environment(example_collection, runner):
    add_to_shell("my", "grandma")

    r = env_helper.lookup_one_var("my")
    assert r == "grandma"


def test_vars_no_pound(example_collection, runner):
    add_to_current("#uuid", "mom")

    r = env_helper.lookup_one_var("#uuid")
    # vars can never start with a #, instead a helper function must exist
    assert r != "mom"

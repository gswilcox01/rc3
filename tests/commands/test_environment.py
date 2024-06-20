import os
import re

import click
import pytest

from rc3 import cli
from rc3.commands import cmd_request, cmd_environment
from rc3.common import json_helper, print_helper


def test_new_qa(example_collection, runner):
    result = runner.invoke(cli.cli, ['e', '--new'], input="qa\n\n")
    assert result.exit_code == 0
    assert "ENVIRONMENT created" in result.output


def test_overwrite_qa(example_collection, runner):
    result = runner.invoke(cli.cli, ['e', '--new'], input="qa\n\n")
    assert result.exit_code == 0
    assert "ENVIRONMENT created" in result.output

    result = runner.invoke(cli.cli, ['e', '--new'], input="qa\ny\n\n")
    assert result.exit_code == 0
    assert "An ENVIRONMENT named 'qa' already exists" in result.output
    assert "ENVIRONMENT created" in result.output


def lookup_current():
    wrapper = cmd_environment.lookup_environment(None)
    e = wrapper.get('_original')
    return e, wrapper


def test_edit_nosave(example_collection, runner, monkeypatch):
    e, wrapper = lookup_current()
    monkeypatch.setattr(click, "edit", lambda x: None)

    # edit current
    result = runner.invoke(cli.cli, ['environment', "--edit"])
    assert result.exit_code == 0
    assert result.output == ''
    e2, wrapper2 = lookup_current()
    assert print_helper.get_json_string(e) == print_helper.get_json_string(e2)


def test_edit_withsave(runner, example_collection, monkeypatch):
    e, wrapper = lookup_current()
    e['baseUrl'] = "not even a url"
    monkeypatch.setattr(click, "edit", lambda x: print_helper.get_json_string(e))

    # edit with SAVE should save
    result = runner.invoke(cli.cli, ['environment', "--edit"])
    assert result.exit_code == 0
    assert "ENVIRONMENT saved" in result.output

    # new file should have the new value
    e2, wrapper2 = lookup_current()
    assert print_helper.get_json_string(e) == print_helper.get_json_string(e2)


def test_edit_errors(runner, example_collection, monkeypatch):
    e, wrapper = lookup_current()
    # invalid, schema calls for anyof(string, null) as values
    e['bob'] = 2112
    monkeypatch.setattr(click, "edit", lambda x: print_helper.get_json_string(e))

    # edit with SAVE should VALIDATE JSON against schema and reject errors
    result = runner.invoke(cli.cli, ['e', "--edit"])
    assert result.exit_code == 0
    assert "JSON is invalid" in result.output
    assert "2112 is not valid" in result.output

    # new file should NOT have the edits
    e2, wrapper2 = lookup_current()
    assert print_helper.get_json_string(e) != print_helper.get_json_string(e2)


def test_edit_unknown(runner, example_collection):
    result = runner.invoke(cli.cli, ['e', "--edit", "10"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_info(runner, example_collection):
    e, wrapper = lookup_current()

    result = runner.invoke(cli.cli, ['e', "--info"])
    assert result.exit_code == 0
    assert print_helper.get_json_string(e) in result.output


def test_no_options_list(runner, example_collection):
    result = runner.invoke(cli.cli, ['e'])
    assert result.exit_code == 0

    result2 = runner.invoke(cli.cli, ['e', '--list'])
    assert result2.exit_code == 0
    assert result.output == result2.output


def test_no_options_pick(runner, example_collection):
    e, wrapper = lookup_current()

    result = runner.invoke(cli.cli, ['e', '2'])
    assert result.exit_code == 0
    assert "ENVIRONMENT has been picked" in result.output

    e2, wrapper2 = lookup_current()
    assert print_helper.get_json_string(e) != print_helper.get_json_string(e2)

    result = runner.invoke(cli.cli, ['e', '--list'])
    assert result.exit_code == 0
    assert len(re.findall(r'1\*', result.output)) == 0
    assert len(re.findall(r'2\*', result.output)) == 1


def test_pick_prompt_bad_choice(runner, example_collection):
    result = runner.invoke(cli.cli, ['e', '--pick'], input="0\n")
    assert result.exit_code == 1
    assert "Invalid selection" in result.output


def test_pick_prompt(runner, example_collection):
    result = runner.invoke(cli.cli, ['e', '--pick'], input="2\n")
    assert result.exit_code == 0
    assert "ENVIRONMENT has been picked" in result.output

    result = runner.invoke(cli.cli, ['e', '--list'])
    assert result.exit_code == 0
    assert len(re.findall(r'1\*', result.output)) == 0
    assert len(re.findall(r'2\*', result.output)) == 1


def test_pick_number_works(runner, example_collection):
    result = runner.invoke(cli.cli, ['e', '--pick', '2'])
    assert result.exit_code == 0
    assert "ENVIRONMENT has been picked" in result.output

    result = runner.invoke(cli.cli, ['e', '--list'])
    assert result.exit_code == 0
    assert len(re.findall(r'1\*', result.output)) == 0
    assert len(re.findall(r'2\*', result.output)) == 1


def test_pick_name_works(runner, example_collection):
    result = runner.invoke(cli.cli, ['e', '--pick', 'localhost'])
    assert result.exit_code == 0
    assert "ENVIRONMENT has been picked" in result.output

    result = runner.invoke(cli.cli, ['e', '--list'])
    assert result.exit_code == 0
    assert len(re.findall(r'1\*', result.output)) == 0
    assert len(re.findall(r'2\*', result.output)) == 1


def test_pick_bad_values_error(runner, example_collection):
    result = runner.invoke(cli.cli, ['e', '--pick', '11'])
    assert result.exit_code == 1
    assert "not found" in result.output

    result = runner.invoke(cli.cli, ['e', '--pick', 'not-there'])
    assert result.exit_code == 1
    assert "not found" in result.output

    result = runner.invoke(cli.cli, ['e', '--list'])
    assert result.exit_code == 0
    assert len(re.findall(r'1\*', result.output)) == 1






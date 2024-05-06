import os
import re

import click
import pytest

from rc3 import cli
from rc3.commands import cmd_request
from rc3.common import json_helper, print_helper


def test_not_new(example_collection, runner):
    result = runner.invoke(cli.cli, ['request', '--new'])
    assert result.exit_code == 0
    assert "NOT IMPLEMENTED!" in result.output


def test_list_variations(example_collection, runner):
    result = runner.invoke(cli.cli, ['request', '--list'])
    assert result.exit_code == 0
    result2 = runner.invoke(cli.cli, ['request'])
    assert result2.exit_code == 0
    result3 = runner.invoke(cli.cli, ['r', '--list'])
    assert result3.exit_code == 0
    result4 = runner.invoke(cli.cli, ['r'])
    assert result4.exit_code == 0

    assert result.output == result2.output == result3.output == result4.output
    assert "Listing REQUESTS" in result.output
    assert len(re.findall(r'1\*', result.output)) == 1


def lookup_current():
    wrapper = cmd_request.lookup_request(None)
    r = wrapper.get('_original')
    return r, wrapper


def test_edit_nosave(example_collection, runner, monkeypatch):
    r, wrapper = lookup_current()
    monkeypatch.setattr(click, "edit", lambda x: None)

    # edit current REQUEST
    result = runner.invoke(cli.cli, ['r', "--edit"])
    assert result.exit_code == 0
    assert result.output == ''
    r2, wrapper2 = lookup_current()
    assert print_helper.get_json_string(r) == print_helper.get_json_string(r2)


def test_edit_withsave(runner, example_collection, monkeypatch):
    r, wrapper = lookup_current()
    r['method'] = "POST"
    monkeypatch.setattr(click, "edit", lambda x: print_helper.get_json_string(r))

    # edit with SAVE should save
    result = runner.invoke(cli.cli, ['r', "--edit"])
    assert result.exit_code == 0
    assert "REQUEST saved" in result.output

    # new file should have the new value
    r2, wrapper2 = lookup_current()
    assert print_helper.get_json_string(r) == print_helper.get_json_string(r2)


def test_edit_errors(runner, example_collection, monkeypatch):
    r, wrapper = lookup_current()
    r['method'] = "WHAT?"
    monkeypatch.setattr(click, "edit", lambda x: print_helper.get_json_string(r))

    # edit with SAVE should VALIDATE JSON against schema and reject errors
    result = runner.invoke(cli.cli, ['r', "--edit"])
    assert result.exit_code == 0
    assert "JSON is invalid" in result.output
    assert "'WHAT?' is not one of" in result.output

    # new file should NOT have the edits
    r2, wrapper2 = lookup_current()
    assert print_helper.get_json_string(r) != print_helper.get_json_string(r2)


def test_edit_unknown(runner, example_collection, monkeypatch):
    result = runner.invoke(cli.cli, ['r', "--edit", "10"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_info(runner, example_collection, monkeypatch):
    r, wrapper = lookup_current()

    result = runner.invoke(cli.cli, ['r', "--info"])
    assert result.exit_code == 0
    assert print_helper.get_json_string(r) in result.output


def test_no_options_list(runner, example_collection, monkeypatch):
    r, wrapper = lookup_current()

    result = runner.invoke(cli.cli, ['r'])
    assert result.exit_code == 0

    result2 = runner.invoke(cli.cli, ['r', '--list'])
    assert result2.exit_code == 0
    assert result.output == result2.output


def test_no_options_pick(runner, example_collection, monkeypatch):
    r, wrapper = lookup_current()

    result = runner.invoke(cli.cli, ['r', '3'])
    assert result.exit_code == 0
    assert "REQUEST has been picked" in result.output

    r2, wrapper2 = lookup_current()
    assert print_helper.get_json_string(r) != print_helper.get_json_string(r2)

    result = runner.invoke(cli.cli, ['r', '--list'])
    assert result.exit_code == 0
    assert len(re.findall(r'1\*', result.output)) == 0
    assert len(re.findall(r'3\*', result.output)) == 1


def test_pick_prompt_bad_choice(runner, example_collection, monkeypatch):
    _input = "0\n"
    result = runner.invoke(cli.cli, ['r', '--pick'], input=_input)
    assert result.exit_code == 1
    assert "Invalid selection" in result.output


def test_pick_prompt(runner, example_collection, monkeypatch):
    _input = "3\n"
    result = runner.invoke(cli.cli, ['r', '--pick'], input=_input)
    assert result.exit_code == 0
    assert "REQUEST has been picked" in result.output

    result = runner.invoke(cli.cli, ['r', '--list'])
    assert result.exit_code == 0
    assert len(re.findall(r'1\*', result.output)) == 0
    assert len(re.findall(r'3\*', result.output)) == 1


def test_pick_number_works(runner, example_collection, monkeypatch):
    result = runner.invoke(cli.cli, ['r', '--pick', '4'])
    assert result.exit_code == 0
    assert "REQUEST has been picked" in result.output

    result = runner.invoke(cli.cli, ['r', '--list'])
    assert result.exit_code == 0
    assert len(re.findall(r'1\*', result.output)) == 0
    assert len(re.findall(r'4\*', result.output)) == 1


def test_pick_name_works(runner, example_collection, monkeypatch):
    result = runner.invoke(cli.cli, ['r', '--pick', 'mint-admin-token'])
    assert result.exit_code == 0
    assert "REQUEST has been picked" in result.output

    result = runner.invoke(cli.cli, ['r', '--list'])
    assert result.exit_code == 0
    assert len(re.findall(r'1\*', result.output)) == 0
    assert len(re.findall(r'7\*', result.output)) == 1


def test_pick_bad_values_error(runner, example_collection, monkeypatch):
    result = runner.invoke(cli.cli, ['r', '--pick', '11'])
    assert result.exit_code == 1
    assert "not found" in result.output

    result = runner.invoke(cli.cli, ['r', '--pick', 'not-there'])
    assert result.exit_code == 1
    assert "not found" in result.output

    result = runner.invoke(cli.cli, ['r', '--list'])
    assert result.exit_code == 0
    assert len(re.findall(r'1\*', result.output)) == 1



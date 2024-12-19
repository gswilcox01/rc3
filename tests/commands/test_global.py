import os
import re

import click
import pytest

from rc3 import cli
from rc3.commands import cmd_request
from rc3.common import json_helper, print_helper


def test_edit_nosave(example_collection, runner, monkeypatch):
    monkeypatch.setattr(click, "edit", lambda x: None)

    # before
    fn, before = json_helper.read_environment("global")
    # edit
    result = runner.invoke(cli.cli, ['global', "--edit"])
    assert result.exit_code == 0
    assert result.output == ''
    fn, after = json_helper.read_environment("global")
    assert print_helper.get_json_string(before) == print_helper.get_json_string(after)


def test_edit_withsave(runner, example_collection, monkeypatch):
    fn, before = json_helper.read_environment("global")
    before['new'] = "NAME"
    monkeypatch.setattr(click, "edit", lambda x: print_helper.get_json_string(before))

    # edit with SAVE should save
    result = runner.invoke(cli.cli, ['global', "--edit"])
    assert result.exit_code == 0

    # new file should have the new value
    fn, after = json_helper.read_environment("global")
    assert print_helper.get_json_string(before) == print_helper.get_json_string(after)
    assert "NAME" in print_helper.get_json_string(after)


def test_edit_errors(runner, example_collection, monkeypatch):
    monkeypatch.setattr(click, "edit", lambda x: "WHAT? This ain't JSON")

    # edit with SAVE should FAIL TO PARSE JSON and raise exception
    result = runner.invoke(cli.cli, ['global', "--edit"])
    assert result.exit_code == 1
    assert "new ENVIRONMENT must be valid JSON" in result.output


def test_info(runner, example_collection):
    # default and --info, both return the same thing
    result = runner.invoke(cli.cli, ['global', "--info"])
    assert result.exit_code == 0
    out1 = result.output

    result = runner.invoke(cli.cli, ['global'])
    assert result.exit_code == 0
    out2 = result.output
    assert out1 == out2


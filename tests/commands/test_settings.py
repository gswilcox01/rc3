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
    before = json_helper.read_settings()
    # edit
    result = runner.invoke(cli.cli, ['settings', "--edit"])
    assert result.exit_code == 0
    assert result.output == ''
    after = json_helper.read_settings()
    assert print_helper.get_json_string(before) == print_helper.get_json_string(after)


def test_edit_withsave(runner, example_collection, monkeypatch):
    before = json_helper.read_settings()
    before['indent_type'] = "tab"
    monkeypatch.setattr(click, "edit", lambda x: print_helper.get_json_string(before))

    # edit with SAVE should save
    result = runner.invoke(cli.cli, ['settings', "--edit"])
    assert result.exit_code == 0

    # new file should have the new value
    after = json_helper.read_settings()
    assert print_helper.get_json_string(before) == print_helper.get_json_string(after)
    assert "indent_type" in print_helper.get_json_string(after)


def test_edit_errors(runner, example_collection, monkeypatch):
    before = json_helper.read_settings()
    before['indent_type'] = "newline"
    monkeypatch.setattr(click, "edit", lambda x: print_helper.get_json_string(before))

    # edit with SAVE should validate schema (newline is not a valid value)
    result = runner.invoke(cli.cli, ['settings', "--edit"])
    assert result.exit_code == 0
    assert "JSON is invalid" in result.output
    assert "'newline' is not one of" in result.output


def test_info(runner, example_collection):
    # default and --info, both return the same thing
    result = runner.invoke(cli.cli, ['settings', "--info"])
    assert result.exit_code == 0
    out1 = result.output

    result = runner.invoke(cli.cli, ['settings'])
    assert result.exit_code == 0
    out2 = result.output
    assert out1 == out2


import os
import re

import click
import pytest
from click import ClickException

from rc3 import cli
from rc3.commands import cmd_request
from rc3.common import json_helper, print_helper


def test_get_set_delete(example_collection, runner):
    result = runner.invoke(cli.cli, ['keyring', '--get', 'not-there-no-way'])
    assert result.exit_code == 0
    assert "None" in result.output

    result = runner.invoke(cli.cli, ['keyring', '--set', 'secret'], input="secret_password\n")
    assert result.exit_code == 0
    result = runner.invoke(cli.cli, ['keyring', '--get', 'secret'])
    assert result.exit_code == 0
    assert "secret_password" in result.output

    result = runner.invoke(cli.cli, ['keyring', '--del', 'secret'])
    assert result.exit_code == 0
    result = runner.invoke(cli.cli, ['keyring', '--get', 'secret'])
    assert result.exit_code == 0
    assert "None" in result.output


def test_get_is_default(example_collection, runner):
    result = runner.invoke(cli.cli, ['keyring', '--set', 'secret'], input="secret_password\n")
    assert result.exit_code == 0
    result = runner.invoke(cli.cli, ['keyring', 'secret'])
    assert result.exit_code == 0
    assert "secret_password" in result.output

    result = runner.invoke(cli.cli, ['keyring', '--del', 'secret'])
    assert result.exit_code == 0
    result = runner.invoke(cli.cli, ['keyring', 'secret'])
    assert result.exit_code == 0
    assert "None" in result.output


def test_name_or_number(example_collection, runner):
    # setup some data in keyring
    # NOTE: \n is not really part of the password, but indicates input on prompt, and the output later also includes \n
    password = "is cool!\n"
    result = runner.invoke(cli.cli, ['keyring', '--set', 'gary'], input=f"{password}")
    assert result.exit_code == 0

    # test listing shows gary before test
    result = runner.invoke(cli.cli, ['keyring', '--list'])
    assert result.exit_code == 0
    assert "Listing KEYRING history" in result.output
    assert "1      gary" in result.output
    assert "2      test" in result.output

    # test different options for getting a password all work / are equal
    result = runner.invoke(cli.cli, ['keyring', 'gary'])
    assert result.exit_code == 0
    out1 = result.output
    result = runner.invoke(cli.cli, ['keyring', '1'])
    assert result.exit_code == 0
    out2 = result.output
    result = runner.invoke(cli.cli, ['keyring', '--get', 'gary'])
    assert result.exit_code == 0
    out3 = result.output
    result = runner.invoke(cli.cli, ['keyring', '--get', '1'])
    assert result.exit_code == 0
    out4 = result.output
    assert out1 == out2 == out3 == out4 == password

    # cleanup
    result = runner.invoke(cli.cli, ['keyring', '--del', 'gary'])
    assert result.exit_code == 0


def test_list_basics(example_collection, runner):
    # list is default if no name
    result = runner.invoke(cli.cli, ['keyring'])
    assert result.exit_code == 0
    assert "Listing KEYRING history" in result.output
    assert "1      test" in result.output
    out1 = result.output

    # --list option does the same
    result = runner.invoke(cli.cli, ['keyring', '--list'])
    assert result.exit_code == 0
    assert result.output == out1


def test_no_entries_on_history(example_collection, runner):
    # delete the default "test" entry
    result = runner.invoke(cli.cli, ['keyring', '--del', 'test'])
    assert result.exit_code == 0

    # --list option should have a message, no listing, and no exception
    result = runner.invoke(cli.cli, ['keyring', '--list'])
    assert result.exit_code == 1
    assert "No KEYRING history found in settings" in result.output

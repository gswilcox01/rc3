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


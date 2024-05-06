import os
import re

import click
import pytest

from rc3 import cli
from rc3.commands import cmd_request
from rc3.common import json_helper, print_helper


def test_not_edit(example_collection, runner):
    result = runner.invoke(cli.cli, ['c', '--edit'])
    assert result.exit_code == 0
    assert "NOT IMPLEMENTED!" in result.output


def test_info(example_collection, runner):
    result = runner.invoke(cli.cli, ['c', '--info'])
    assert result.exit_code == 0
    assert "name" in result.output
    assert "current_request" in result.output
    assert "current_environment" in result.output

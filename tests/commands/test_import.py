import os
import re

import click
import pytest
from click import ClickException

from rc3 import cli
from rc3.commands import cmd_request
from rc3.common import json_helper, print_helper


def test_reimport_example(example_collection, tmp_path, runner):
    # starting place will example_collection
    result = runner.invoke(cli.cli, ['import'])
    assert result.exit_code == 0
    assert "has been successfully imported" in result.output


def test_import_empty_dir_fails(example_collection, tmp_path, runner):
    d = tmp_path / "empty2"
    d.mkdir()
    os.chdir(d)
    result = runner.invoke(cli.cli, ['import'])
    assert result.exit_code == 1
    assert "CWD must contain a valid rc-collection.json file" in result.output


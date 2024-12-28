import os
import re

import click
import pytest

from rc3 import cli
from rc3.commands import cmd_request
from rc3.common import json_helper, print_helper


def test_basic_command_runs(example_collection, runner):
    result = runner.invoke(cli.cli, ['upgrade'], input="n\nn\n")
    assert result.exit_code == 0
    assert "Checking RC_HOME schemas... UPGRADES NEEDED" in result.output
    assert "Checking current COLLECTION schemas... OK" in result.output
    assert "COLLECTION REQUEST extract JSON... NOT IMPLEMENTED YET" in result.output
    assert "COLLECTION validating JSON against current schemas... NOT IMPLEMENTED YET" in result.output


def test_upgrade_does_needful(example_collection, runner):
    result = runner.invoke(cli.cli, ['upgrade'], input="y\n")
    assert result.exit_code == 0
    assert "Checking RC_HOME schemas... UPGRADES NEEDED" in result.output
    assert "Checking current COLLECTION schemas... OK" in result.output
    assert "COLLECTION REQUEST extract JSON... NOT IMPLEMENTED YET" in result.output
    assert "COLLECTION validating JSON against current schemas... NOT IMPLEMENTED YET" in result.output

    result = runner.invoke(cli.cli, ['upgrade'])
    assert result.exit_code == 0
    assert "Checking RC_HOME schemas... OK" in result.output
    assert "Checking current COLLECTION examples... OK" in result.output
    assert "Checking current COLLECTION schemas... OK" in result.output

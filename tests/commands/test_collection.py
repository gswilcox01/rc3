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


def test_pick(example_collection, runner):
    result = runner.invoke(cli.cli, ['c', '--pick', 'missing'])
    assert result.exit_code == 1
    assert "COLLECTION_NAME not found" in result.output

    result = runner.invoke(cli.cli, ['c', '--pick', 'example-collection'])
    assert result.exit_code == 0
    assert "Found COLLECTION_NAME" in result.output
    assert "COLLECTION has been picked" in result.output

    result = runner.invoke(cli.cli, ['c', '--pick', '1'])
    assert result.exit_code == 0
    assert "Found COLLECTION_NAME: 1" in result.output

    # default is pick also
    result = runner.invoke(cli.cli, ['c', '1'])
    assert result.exit_code == 0
    assert "Found COLLECTION_NAME: 1" in result.output


def test_pick_prompter(example_collection, runner):
    result = runner.invoke(cli.cli, ['c', '--pick'], input='5\n')
    assert result.exit_code == 1
    assert "Invalid selection" in result.output

    result = runner.invoke(cli.cli, ['c', '--pick'], input='1\n')
    assert result.exit_code == 0
    assert "COLLECTION has been picked" in result.output

    # default choice should be 1 / work also
    result = runner.invoke(cli.cli, ['c', '--pick'], input='\n')
    assert result.exit_code == 0
    assert "COLLECTION has been picked" in result.output


def test_list(example_collection, runner):
    result = runner.invoke(cli.cli, ['c', '--list'])
    assert result.exit_code == 0
    assert "Listing COLLECTIONS" in result.output
    o1 = result.output

    result = runner.invoke(cli.cli, ['c'])
    assert result.exit_code == 0
    assert "Listing COLLECTIONS" in result.output
    assert o1 == result.output
